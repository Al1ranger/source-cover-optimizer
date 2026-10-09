# Security and scope

Experimental documentation-selection infrastructure. Not audited. Do not use
as legal/compliance advice, financial authorization or a real-world truth oracle.

## Trust boundaries

- Immutable creator-selected goals and candidates can be biased. The optimum
  does not extend to documents outside that fixed list.
- RFC Editor HTTPS is a single publishing authority, not multiple independent
  witnesses. TLS/host compromise, changed responses and future API outages remain.
- AI agreement can still misinterpret or miss a prompt injection. Exact agreement
  is not a proof of truth or perfect comprehension.
- Source bytes are fully fetched, UTF-8/header/size checked and hashed. Hashes
  commit to acquired content; format checks alone do not yield coverage.
- Observation freshness does not mean a historical RFC remains applicable today.
- Documents/reports/goals and observer identities are public. No privacy.

## Controls

Deployment/creator/pack/RFC namespaces; fixed candidate list; exact independently
recomputed decision report; no supplied costs/labels/summaries; immutable terminal
rows and results; three source-acquisition attempts; permissionless deadline
closure; all unresolved/ambiguous/stale rows block a false complete optimum;
bounded exhaustive solver; append-only hash-linked history; native value rejected;
no transfers, approvals, external contract dispatch or secret storage.

An adversary can consume acquisition attempts during a real source outage;
deadline closure then records INCOMPLETE. The contract deliberately does not
silently drop unavailable candidates or let an owner retry an ambiguous row until
the model gives a preferred answer. Open pack creation permits Sybil-created
packs; per-creator bounds do not provide global anti-spam or personhood.

## Verification scope

Direct tests exercise actual state with mocked HTTP/AI, plus pure equivalence and
optimizer tests. They do not simulate distributed consensus. Only entries marked
live in LIVE_PROOFS.md have inspected onchain receipts and state readbacks.
No Slither/Foundry claim: this is a GenVM Python contract, not EVM Solidity.

Report security issues privately through the repository owner's GitHub contact;
never publish credentials or personal documents in an issue.
