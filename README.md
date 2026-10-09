# SourceCoverOptimizer

An experimental, reusable GenLayer **minimum documentation cover** primitive.
Independent source interpretation supplies a coverage matrix; an exact weighted
set-cover solver selects the cheapest complete source bundle by raw-body bytes.
Not an audited production system.

## Problem and why GenLayer

A retrieval application needs a compact reading bundle that actually explains
every requested subject. Keyword counts and a single model's recommendation
can silently omit requirements. An ordinary chain can solve a small set-cover
instance but cannot fetch and interpret RFC prose independently.

Here consequential semantic judgments determine the input matrix. Every validator
independently fetches and hashes the complete source and recomputes each coverage
decision. A different accepted coverage row can change the minimum bundle or
turn a feasible instance into UNCOVERED. The model cannot nominate winners,
invent costs or silently fill gaps with other documents.

```text
immutable goals + fixed candidate RFC IDs + time bounds
                         |
permissionless source observation
                         |
independent RFC Editor full-body acquisition + raw SHA-256
                         |
independent semantic requirement coverage: YES / NO / UNKNOWN
                         |
exact full-report equality -> immutable coverage matrix row
                         |
permissionless exact subset minimization, at most 255 subsets
                         |
COVERED (minimum bundle) / UNCOVERED / INCOMPLETE
```

## Distinct architecture

No graph nodes, edges, parent versions, proposer-controlled transitions, scores,
certificates, compiled programs, consumed capabilities, escrow or settlement.
Storage is a fixed set-cover instance, source-scoped rows, bounded acquisition
attempts and a terminal optimum/infeasibility result. The creator cannot edit
the instance, veto observation, remove a candidate or choose the final subset.
See [architecture and reviewer comparison](docs/architecture.md).

## Consensus and evidence lifecycle

The contract constructs `https://www.rfc-editor.org/rfc/rfc<ID>.txt` from a bound
integer ID. Callers submit neither text, hash, cost, confidence nor coverage.
Each validator fetches the full response, checks HTTP 200, 1–16 KiB, strict UTF-8,
no NUL and matching RFC identity header, then interprets all requested subjects
from that complete body. YES requires every substantive element to be explicitly
explained; bare mentions and citations do not suffice. Absence is NO; ambiguous
coverage or attempted classifier instructions yield UNKNOWN.

Exact comparison includes pack/definition/RFC/observer/attempt/time bindings,
status, full-response SHA-256, byte count, coverage vector and derived state.
There is no tolerance crossing a decision threshold. Malformed AI output aborts
with LLM_ERROR; validator disagreement cannot install a row. Disagreement is
not falsely advertised as a stored CONFLICTED outcome.

Each report is hash-bound and immutable. These commitments bind actual acquired
bytes; they do not replace semantic evaluation or prove real-world facts.

## State, security and liveness

```text
OPEN -> OBSERVED / AMBIGUOUS / INVALID source row
     -> UNAVAILABLE attempt (up to three; final failure becomes terminal)
OPEN -> solve after all sources terminal OR deadline ->
        COVERED / UNCOVERED / INCOMPLETE (immutable)
```

Every source is keyed by its deployment/creator/pack and RFC ID. Completed
observations and results cannot be resampled or replayed into another pack.
Observation stops at the deadline. Anyone can close at the deadline even if the
creator disappears. Any missing, stale, invalid, unavailable or ambiguous row
produces INCOMPLETE and no selected bundle: the contract never asserts a global
optimum over an incomplete candidate set. Age checks observation age, not RFC
currency. All writes and deployment reject nonzero native value; no assets held.

Bounds: 1–5 ASCII reading requirements, 1–8 distinct RFCs, at most three attempts
per source, eight packs per creator, 30 seconds–24 hours for deadline/age bounds.
The exact optimizer enumerates every nonempty subset, minimizing total source
bytes; equal costs break by ascending RFC-ID tuple. NO rows remain eligible but
cannot help coverage. History is append-only and hash-linked.

## Real-source demonstration

The demo combines [RFC 2606](https://www.rfc-editor.org/rfc/rfc2606.txt), describing
reserved example domain names, with [RFC 5737](https://www.rfc-editor.org/rfc/rfc5737.txt),
describing IPv4 documentation blocks. [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119.txt)
defines requirement terminology and should be irrelevant to both goals.
The expected minimum bundle is RFCs 2606 and 5737, excluding 2119.
[Demo assertions](examples/demo.json) are never passed as authoritative outcomes.

The sources are actual RFC Editor documents, not project-authored fixtures, but
share one publisher. The primitive establishes document coverage, not independent
real-world truth, current operational correctness or service delivery. Optimality
holds only for the fixed candidate set and consensus-agreed semantic matrix.

## Install, test, deploy

```powershell
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/genvm-lint check contracts/SourceCoverOptimizer.py --json
.venv/Scripts/python -m pytest tests -q
npm ci
node --test tests/transport.test.cjs
npm install -g genlayer@0.39.2
genlayer network set studionet
genlayer account use YOUR_ENCRYPTED_TEST_KEYSTORE
genlayer account unlock
genlayer deploy --contract contracts/SourceCoverOptimizer.py
```

Concrete GenVM runner is pinned. Direct tests mock source/AI calls and execute
the leader only; equivalence helper checks are not distributed disagreement
proofs. Windows test cleanup defers only gltest's open temporary message-file
unlink. Deadline tests refresh the runner's cached message datetime after warp;
production supplies a fresh transaction message.

## API and interaction

`open_pack`, `pack_key`, `observe`, `solve`, `get_pack`, `get_row`, `get_attempt`,
`history`. Requirements are semicolon-separated; RFC IDs are comma-separated.
Use SDK views to pass addresses explicitly as strings: CLI 0.39.2 may coerce a
hex address into an address-typed argument when `pack_key` expects a string.

```powershell
$deadline=[DateTimeOffset]::UtcNow.ToUnixTimeSeconds()+7200
genlayer write ADDRESS open_pack --args demo 'Explains reservation of example.com example.net and example.org for documentation examples;Defines all three IPv4 TEST-NET address blocks reserved for documentation' '2119,2606,5737' $deadline 7200
node scripts/verify_pack.mjs ADDRESS CREATOR_ADDRESS demo OPEN
genlayer write ADDRESS observe --args PACK_KEY 2119
genlayer write ADDRESS observe --args PACK_KEY 2606
genlayer write ADDRESS observe --args PACK_KEY 5737
genlayer write ADDRESS solve --args PACK_KEY
node scripts/verify_pack.mjs ADDRESS CREATOR_ADDRESS demo COVERED 2606,5737
```

Use a dedicated encrypted StudioNet wallet; never export its private key. StudioNet
is gasless. Inspect FINALIZED **and leader execution SUCCESS and majority agreement**,
not the CLI banner. `node scripts/check.mjs --success HASH` verifies metadata;
`--source ADDRESS` compares deployed source with this repository. The pack verifier
recomputes roots, bindings, freshness and every subset to verify optimality.
See [LIVE_PROOFS.md](LIVE_PROOFS.md) for actual evidence status.

## Optional Windows HTTPS fallback

Prepend `--require ./scripts/windows_read_transport.cjs` to Node view/verifier
commands if Node HTTPS times out. This forwards public reads through native
PowerShell only. For an already-signed CLI write, the separately enabled
`windows_broadcast_once.cjs` uses `STUDIO_NATIVE_BROADCAST=1`; signing remains in
the encrypted CLI keystore. It sends each signed payload once and caches success
and failure. Inspect account history after an unknown broadcast outcome; never
blindly resend. The transport unit test uses mocks and sends no transaction.

```powershell
$cli=Join-Path (npm root -g) 'genlayer/dist/index.js'
$env:STUDIO_NATIVE_BROADCAST='1'
node --require ./scripts/windows_read_transport.cjs --require ./scripts/windows_broadcast_once.cjs $cli deploy --contract contracts/SourceCoverOptimizer.py
Remove-Item Env:STUDIO_NATIVE_BROADCAST
```

Risks and limits: [SECURITY.md](SECURITY.md). No production audit, universal
novelty, steward approval or points are claimed.
