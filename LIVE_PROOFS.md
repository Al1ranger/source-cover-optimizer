# Proof matrix

StudioNet deployment and source equality verified on October 8, 2026.

Contract: [0x77d21ce3cbeb50CcaA8C50D6584fbD7EE891AEcE](https://explorer-studio.genlayer.com/address/0x77d21ce3cbeb50CcaA8C50D6584fbD7EE891AEcE).
Published contract commit: `2164289969f03af951f16a2296df72879a003e2b`.
Normalized deployed source SHA-256: `dded47903a525946af13c81f65d1708a526d547ec858916dcde159820b0ee750`.
Only CRLF and final newline are normalized for source equality, never source evidence.

Dedicated encrypted test wallet: `0x7a413BB4AB62E31d62d4cD9efC8C8a8Dae37FB42`.
Starting next nonce was `0x73` (115). Gasless test transactions, no asset transfers.

## Finalized live receipts

Successful entries require FINALIZED, leader SUCCESS and MAJORITY_AGREE. This
does not claim unanimity, production assurance or a distributed disagreement test.

| Stage | Transaction | Verified outcome |
| --- | --- | --- |
| Deployment | [0x6d47…2558](https://explorer-studio.genlayer.com/tx/0x6d478a8a2d8f7a4306c87b3cc2c371332a0548f6e6472d02f62ccc749d562558) | SUCCESS; deployed source equals GitHub |
| Open documentation-live | [0x0234…46ca](https://explorer-studio.genlayer.com/tx/0x02345d3efd22b8e78a51fe3ec2dbf9c8e5d4ebf70df9f380c6ba50c9fe7b46ca) | OPEN; definition root checked; key `69ba03ce0fc5ea3cededa654b1b9f48d30fb156fae49ad9cebdc92d9fc7cc211` |
| Observe RFC 2119 | [0xfad3…02a7](https://explorer-studio.genlayer.com/tx/0xfad37880d01f0b08491d32eec93922f826bf889a43d9bf6df5defa83598602a7) | OBSERVED; [NO, NO]; 4723 raw bytes; independently checked source hash, pack binding and report root |
| Observe RFC 2606 | [0xf816…24f4](https://explorer-studio.genlayer.com/tx/0xf816cf0f6a6c5c554f0cb846e379230b1fd32fe142dec0e1873676f72b3124f4) | OBSERVED; [YES, NO]; 8008 raw bytes; source hash, report root and binding checked |
| Observe RFC 5737 | [0x7d11…8e1f](https://explorer-studio.genlayer.com/tx/0x7d113669d46cbdaa46f8066b8d07ab7efd023b9c3bbd5349483e989a59cd8e1f) | OBSERVED; [NO, YES]; 7036 raw bytes; source hash, report root and binding checked |
| Solve documentation-live | [0x14e3…a1dc](https://explorer-studio.genlayer.com/tx/0x14e37f79ff46d84bde68e6b9e7b0a35342fda047495ed9d849f25458ba9da1dc) | COVERED; minimum subset [2606, 5737], 15044 bytes; independently reconstructed all subsets, matrix, report/result roots and bindings |
| Open uncovered-live | [0x1a1b…e152](https://explorer-studio.genlayer.com/tx/0x1a1be9a2e6c3026355371730fdbd5045533e1fb8250ff0f403c7fcc76f5ee152) | OPEN; definition root checked; one bound candidate, RFC 2119 |
| Observe negative RFC 2119 | [0x3446…4545](https://explorer-studio.genlayer.com/tx/0x34463185bdb2373ed7e992f39025adbfe8fcd5cb35e1f2484554175999124545) | OBSERVED; [NO, NO]; actual raw hash and 4723-byte cost match the independent fetch; binding/root checked |
| Solve uncovered-live | [0x49d5…6f26](https://explorer-studio.genlayer.com/tx/0x49d57be36b000ad582931e24142398c6906216f2e4d9b5b484655c457f5d6f26) | UNCOVERED; no selected sources, zero selected bytes; full matrix, infeasibility, roots and bindings independently reconstructed |

Local lint and SDK validation passed: eight methods, five views, three writes,
zero constructor parameters. Informational newer-runner notice only.

29 direct tests pass (mocked HTTP/AI, leader-only), including 64 small coverage
instances checked against an independently enumerated optimum. Two mocked Node
tests pass (transport and CLI-string compatibility); neither signs nor broadcasts. Initial five failures
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
| Irrelevant row excluded; complete source set gives exact optimum | PASS helper | PASS: RFC 2119 excluded, [2606, 5737], 15044 bytes |
| No complete coverage -> UNCOVERED | PASS | PASS: valid RFC 2119 row [NO, NO], no bundle issued |
| Ambiguous/invalid/stale/missing row -> INCOMPLETE, no bundle | PASS | Not run |
| Cross-pack source ID cannot transplant a row | PASS | Not run |
| Replay and terminal reset rejected | PASS | Not run |
| Any caller closes after deadline; no creator veto | PASS | Not run |
| Exact report mismatch rejects equivalence | Helper test only | Distributed disagreement experiment not run |
| Exhaustive solver matches independent subset reference | PASS: 64 instances | PASS: all seven nonempty subsets reconstructed |

Use check.mjs for FINALIZED + leader execution + majority agreement and source
equality. Use verify_pack.mjs to independently reconstruct the matrix/optimum.
Do not treat mocked test cases or planned transactions as real proofs.

A permission-review timeout occurred before starting one RFC 2606 observation
command. The permitted retry started once and produced the verified receipt
above. No transaction or proof is attributed to the pre-process timeout.

The initial one-RFC negative pack command, transaction
`0x9236ea712a5001b09899a0785481068a428d0f37dbf7f1f8cfd1d3d84fc6873e`,
finalized with leader ERROR and the expected invalid-requirements/RFCs error.
The explicit-string prefix lacked its CLI loader hook. No pack was created;
this is excluded from successful lifecycle proofs. The installed CLI and
deployed contract were not modified to work around the argument encoding.
