# Proof matrix

Not yet deployed. No live address or transaction proof is claimed.

Local lint and SDK validation passed: eight methods, five views, three writes,
zero constructor parameters. Informational newer-runner notice only.

29 direct tests pass (mocked HTTP/AI, leader-only), including 64 small coverage
instances checked against an independently enumerated optimum. One mocked Node
transport test passes; it neither signs nor broadcasts. Initial five failures
were literal error-message assertions, corrected without changing the contract.

Independently fetched public source bodies, HTTP 200:

| RFC | Raw bytes | SHA-256 |
| --- | ---: | --- |
| 2119 | 4723 | 3c2ceb7bfc84cd34720f4a5271338ab9d8280d34bdd1eb250c64306202f2ed8b |
| 2606 | 8008 | b6869c8984701701bc2e6973b6ffc750d497f845cc1a65a106e9301590a13ab0 |
| 5737 | 7036 | 9d16217614a74a9b064eff900e5cd07a525793cf8227dca1267100e880f0c410 |

These hashes are observations, not caller-provided semantic decisions or costs.

| Scenario | Direct status | Live status |
| --- | --- | --- |
| Semantic coverage changes selected minimum bundle | PASS | Not run |
| Irrelevant row excluded; complete source set gives exact optimum | PASS helper | Not run |
| No complete coverage -> UNCOVERED | PASS | Not run |
| Ambiguous/invalid/stale/missing row -> INCOMPLETE, no bundle | PASS | Not run |
| Cross-pack source ID cannot transplant a row | PASS | Not run |
| Replay and terminal reset rejected | PASS | Not run |
| Any caller closes after deadline; no creator veto | PASS | Not run |
| Exact report mismatch rejects equivalence | Helper test only | Distributed disagreement experiment not run |
| Exhaustive solver matches independent subset reference | PASS: 64 instances | Not run |

Use check.mjs for FINALIZED + leader execution + majority agreement and source
equality. Use verify_pack.mjs to independently reconstruct the matrix/optimum.
Do not treat mocked test cases or planned transactions as real proofs.
