# SourceCoverOptimizer: consensus boundary

## Mechanism

A reusable, bounded weighted-set-cover primitive for documentation retrieval.
An immutable pack fixes 1–5 substantive reading requirements, 1–8 distinct RFC
document IDs, a deadline and maximum observation age. Any caller may observe a
listed source. Leader and validators independently acquire its complete body
from the RFC Editor, hash it and semantically determine which requirements it
explicitly covers. Only exact equality of the full source-bound report can
install a matrix row. Sources are external documents, not caller summaries.

Any caller can solve once every source has a terminal observation, or after the
deadline. An exhaustive bounded subset search minimizes total fetched UTF-8
byte cost while covering every requirement. Equal costs break by sorted RFC-ID
tuple. Selection is deterministic, but its input coverage matrix is materially
AI-derived: a different agreed coverage row changes the selected bundle or
whether any complete bundle exists. Missing, stale, unavailable or ambiguous
rows yield INCOMPLETE, not a false global optimum over a partial source set.

## Ownership and outputs

- Caller: immutable reading goals and candidate RFC IDs; no source body,
  coverage vector, cost, confidence or winner supplied.
- RFC Editor: original public source bytes. One document authority, not
  independent witnesses of real-world performance. RFC currency is not proven.
- GenLayer: source acquisition, semantic coverage, exact validator comparison,
  matrix admission, minimum-cover solution and immutable report/result roots.
- Offchain application: retrieval UI, caching and use of the selected sources.

The useful output is a minimal documentation bundle for the fixed candidates,
not a certificate of truth, a payment, a policy program, a graph head or an
authorization token. The creator cannot approve results, change the candidates,
exclude an observed row, reset a solution or veto deadline closure.

## State and liveness

OPEN -> source observations -> permissionless solve ->
COVERED / UNCOVERED / INCOMPLETE (all terminal).

A completed coverage row is immutable. Acquisition failures have at most three
attempts per source; an ambiguous semantic interpretation is terminal and cannot
be resampled. Failed acquisition reports remain readable. Deadline closure
ensures unavailable sources cannot lock a pack forever. No funds are held.

Reports bind deployment/pack, immutable definition root, RFC ID, constructed URL,
observer, transaction time, response status, byte count, raw SHA-256, full
coverage vector and derived state. The source adapter permits no arbitrary
host, redirect-selected URL, caller text or hash-only semantic decision.

## Distinction from existing mechanisms

Unlike consensus selection, there are no applicant scores or owner-finalized
rankings. Unlike source-tariff-vm, no program is compiled and no scenario quote
is interpreted. Unlike semantic-ledger-bridge, there is no bipartite record
matching. Unlike the prior graph variants, there are no edges, parent versions
or proposed graph transitions. The core structure is a fixed coverage matrix
plus a globally minimized subset with an explicit infeasibility outcome.

## Review audit question

Could this only verify caller information? No: goals are authoritative requests,
not achievements; source bodies and byte costs are independently acquired, and
coverage is independently inferred from full external document contents. It
does not establish that a document's factual assertions are true in the world.
Universal novelty, production safety and steward acceptance are not claimed.
