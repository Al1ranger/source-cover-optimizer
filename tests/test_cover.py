import ast
import hashlib
import itertools
import json
from pathlib import Path
from datetime import datetime, timezone
import pytest

START = int(datetime(2026, 10, 8, 12, tzinfo=timezone.utc).timestamp())
GOALS = "Explains the alpha requirement completely;Explains the beta requirement completely"


def addr(value):
    return "0x" + value.hex() if isinstance(value, bytes) else str(value)


def warp(vm, text):
    vm.warp(text)
    from genlayer import gl
    gl.message_raw["datetime"] = text


def mock(vm, rfc, coverage=("YES", "NO"), raw=None, status=200, output=None):
    vm.clear_mocks()
    body = raw if raw is not None else ("Request for Comments: " + str(rfc) + "\nA full synthetic explanation.\n").encode()
    vm.mock_web(r".*rfc" + str(rfc) + r"\.txt", {"status": status, "body": body})
    vm.mock_llm(r"(?s).*Build the document coverage row.*", json.dumps({"coverage": list(coverage)} if output is None else output))
    return hashlib.sha256(body).hexdigest(), len(body)


@pytest.fixture
def contract(direct_vm, direct_deploy, direct_alice):
    direct_vm.sender = direct_alice
    direct_vm.warp("2026-10-08T12:00:00Z")
    return direct_deploy("contracts/SourceCoverOptimizer.py")


def pack(contract, creator, rfcs="2119,2606", name="demo", max_age=7200):
    contract.open_pack(name, GOALS, rfcs, START + 3600, max_age)
    return contract.pack_key(addr(creator), name)


@pytest.fixture
def helpers():
    tree = ast.parse(Path("contracts/SourceCoverOptimizer.py").read_text())
    functions = [item for item in tree.body if isinstance(item, ast.FunctionDef) and item.name in
                 ("canonical", "digest", "parse_coverage", "equivalent", "minimum_cover")]
    namespace = {"hashlib": hashlib, "json": json}
    exec(compile(ast.Module(body=functions, type_ignores=[]), "actual_contract_helpers", "exec"), namespace)
    return namespace


def test_acquired_semantics_determine_minimum_bundle(contract, direct_vm, direct_alice, helpers):
    key = pack(contract, direct_alice)
    expected_hash, size = mock(direct_vm, 2119)
    contract.observe(key, 2119)
    row = contract.get_row(key, 2119)
    assert row["coverage"] == ["YES", "NO"] and row["hash"] == expected_hash and row["bytes"] == size
    mock(direct_vm, 2606, ("YES", "YES"))
    contract.observe(key, 2606)
    contract.solve(key)
    result = contract.get_pack(key)["result"]
    assert result["state"] == "COVERED" and result["selected"] == [2606]
    assert result["root"] == helpers["digest"]({k: v for k, v in result.items() if k != "root"})


def test_semantic_change_forces_two_source_bundle(contract, direct_vm, direct_alice):
    key = pack(contract, direct_alice)
    for rfc, row in ((2119, ("YES", "NO")), (2606, ("NO", "YES"))):
        mock(direct_vm, rfc, row)
        contract.observe(key, rfc)
    contract.solve(key)
    assert contract.get_pack(key)["result"]["selected"] == [2119, 2606]


def test_fully_observed_but_uncovered_has_no_bundle(contract, direct_vm, direct_alice):
    key = pack(contract, direct_alice, "2119")
    mock(direct_vm, 2119, ("YES", "NO"))
    contract.observe(key, 2119)
    contract.solve(key)
    result = contract.get_pack(key)["result"]
    assert result["state"] == "UNCOVERED" and result["selected"] == [] and result["total_bytes"] == 0


def test_ambiguity_blocks_optimum_even_if_another_source_covers_all(contract, direct_vm, direct_alice):
    key = pack(contract, direct_alice)
    for rfc, row in ((2119, ("YES", "YES")), (2606, ("UNKNOWN", "NO"))):
        mock(direct_vm, rfc, row)
        contract.observe(key, rfc)
    contract.solve(key)
    result = contract.get_pack(key)["result"]
    assert result["state"] == "INCOMPLETE" and result["selected"] == []
    assert result["rejected"] == [{"rfc": 2606, "reason": "AMBIGUOUS"}]


def test_observation_and_solve_are_permissionless(contract, direct_vm, direct_alice, direct_bob):
    key = pack(contract, direct_alice, "2119")
    direct_vm.sender = direct_bob
    mock(direct_vm, 2119, ("YES", "YES"))
    contract.observe(key, 2119)
    contract.solve(key)
    assert contract.get_pack(key)["state"] == "COVERED"
    assert contract.get_row(key, 2119)["spec"]["observer"].lower() == addr(direct_bob).lower()


def test_replayed_row_and_result_rejected(contract, direct_vm, direct_alice):
    key = pack(contract, direct_alice, "2119")
    mock(direct_vm, 2119, ("YES", "YES"))
    contract.observe(key, 2119)
    with direct_vm.expect_revert("source already terminal"):
        contract.observe(key, 2119)
    contract.solve(key)
    saved = contract.get_pack(key)
    with direct_vm.expect_revert("terminal pack"):
        contract.solve(key)
    assert contract.get_pack(key) == saved


def test_cross_pack_observation_cannot_move_row(contract, direct_vm, direct_alice):
    one = pack(contract, direct_alice, "2119", "one")
    two = pack(contract, direct_alice, "2606", "two")
    mock(direct_vm, 2119, ("YES", "YES"))
    contract.observe(one, 2119)
    with direct_vm.expect_revert("source not bound"):
        contract.observe(two, 2119)
    with direct_vm.expect_revert("waiting for sources"):
        contract.solve(two)
    assert contract.get_row(one, 2119)["spec"]["pack"] == one


def test_missing_source_cannot_lock_after_deadline(contract, direct_vm, direct_alice, direct_bob):
    key = pack(contract, direct_alice)
    with direct_vm.expect_revert("waiting for sources"):
        contract.solve(key)
    warp(direct_vm, "2026-10-08T13:00:01Z")
    direct_vm.sender = direct_bob
    contract.solve(key)
    result = contract.get_pack(key)["result"]
    assert result["state"] == "INCOMPLETE" and len(result["rejected"]) == 2


def test_expired_source_fails_closed(contract, direct_vm, direct_alice):
    key = pack(contract, direct_alice, "2119", max_age=30)
    mock(direct_vm, 2119, ("YES", "YES"))
    contract.observe(key, 2119)
    warp(direct_vm, "2026-10-08T12:00:31Z")
    contract.solve(key)
    assert contract.get_pack(key)["result"]["rejected"] == [{"rfc": 2119, "reason": "STALE"}]


def test_three_unavailable_attempts_terminal_and_auditable(contract, direct_vm, direct_alice):
    key = pack(contract, direct_alice, "2119")
    mock(direct_vm, 2119, status=503)
    for attempt in range(1, 4):
        contract.observe(key, 2119)
        assert contract.get_attempt(key, 2119, attempt)["state"] == "UNAVAILABLE"
    with direct_vm.expect_revert("source already terminal"):
        contract.observe(key, 2119)
    contract.solve(key)
    assert contract.get_pack(key)["state"] == "INCOMPLETE"


@pytest.mark.parametrize("body,reason", [(b"Fake RFC text", "RFC_IDENTITY"),
    (b"Request for Comments: 2606\nWrong source", "RFC_IDENTITY"),
    (b"Request for Comments: 2119\x00", "RFC_IDENTITY"), (b"\xff", "INVALID_UTF8"),
    (b"x" * 16385, "SOURCE_SIZE"), (b"", "SOURCE_SIZE")])
def test_invalid_acquisition_never_installs_coverage(contract, direct_vm, direct_alice, body, reason):
    key = pack(contract, direct_alice, "2119")
    mock(direct_vm, 2119, ("YES", "YES"), raw=body)
    contract.observe(key, 2119)
    row = contract.get_row(key, 2119)
    assert row["state"] == "INVALID" and row["reason"] == reason and row["coverage"] == []
    contract.solve(key)
    assert contract.get_pack(key)["state"] == "INCOMPLETE"


@pytest.mark.parametrize("output", [{"coverage": [True, False]}, {"coverage": ["YES"]},
    {"coverage": ["YES", "YES"], "winner": 2119}, {"coverage": ["YES", "MAYBE"]}])
def test_bad_ai_schema_aborts_not_false_coverage(contract, direct_vm, direct_alice, output):
    key = pack(contract, direct_alice, "2119")
    mock(direct_vm, 2119, output=output)
    with direct_vm.expect_revert("malformed coverage"):
        contract.observe(key, 2119)
    assert contract.get_pack(key)["state"] == "OPEN"
    with direct_vm.expect_revert("unknown attempt"):
        contract.get_attempt(key, 2119, 1)


def test_native_value_rejected(contract, direct_vm, direct_alice):
    direct_vm.value = 1
    with direct_vm.expect_revert("native value"):
        pack(contract, direct_alice)


@pytest.mark.parametrize("goals,rfcs", [("short", "2119"), (GOALS, "2119,2119"),
    (GOALS, "0"), (GOALS, "https://evil.example/a"), (GOALS, "02119")])
def test_invalid_pack_inputs(contract, direct_vm, goals, rfcs):
    expected = "duplicate RFC" if rfcs == "2119,2119" else "invalid requirements"
    with direct_vm.expect_revert(expected):
        contract.open_pack("bad", goals, rfcs, START + 3600, 7200)


def test_exact_equivalence_rejects_every_consequential_difference(helpers):
    report = {"spec": {"pack": "one", "rfc": 2119}, "hash": "a" * 64, "bytes": 20,
              "coverage": ["YES", "NO"], "state": "OBSERVED"}
    assert helpers["equivalent"](report, dict(report))
    for field, value in (("hash", "b" * 64), ("bytes", 21), ("coverage", ["NO", "YES"]),
                         ("state", "AMBIGUOUS"), ("spec", {"pack": "two", "rfc": 2119})):
        assert not helpers["equivalent"](report, {**report, field: value})


def test_exact_solver_beats_greedy_and_has_canonical_tie_break(helpers):
    rows = [{"rfc": 1, "bytes": 7, "coverage": ["YES", "YES", "NO"]},
            {"rfc": 2, "bytes": 7, "coverage": ["NO", "NO", "YES"]},
            {"rfc": 3, "bytes": 11, "coverage": ["YES", "YES", "YES"]},
            {"rfc": 4, "bytes": 11, "coverage": ["YES", "YES", "YES"]}]
    assert helpers["minimum_cover"](rows, 3) == {"selected": [3], "total_bytes": 11}


def test_solver_matches_independent_small_set_reference(helpers):
    for vectors in itertools.product(range(4), repeat=3):
        rows = [{"rfc": i + 1, "bytes": i + 2, "coverage": ["YES" if vector & (1 << j) else "NO" for j in range(2)]}
                for i, vector in enumerate(vectors)]
        candidates = []
        for count in range(1, 4):
            for subset in itertools.combinations(rows, count):
                if all(any(row["coverage"][j] == "YES" for row in subset) for j in range(2)):
                    candidates.append((sum(row["bytes"] for row in subset), tuple(row["rfc"] for row in subset)))
        expected = min(candidates) if candidates else (0, ())
        assert helpers["minimum_cover"](rows, 2) == {"selected": list(expected[1]), "total_bytes": expected[0]}
