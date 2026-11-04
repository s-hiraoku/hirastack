# Bounded delivery, replies and attachments

## Sub-features

Permanent reply/source budgets; finite retry/record/byte capacity; digest-verified attachments; selection fairness; single diagram source.

## How to get to it (user POV)

Use synthetic fixed messages and attachment bytes, exceed permitted bounds, and confirm the original accepted message and quota remain intact.

## Driving it with hirastack

bounded-replies, attachment-integrity and capacity-fairness run storage/protocol failure suites. diagram-source validates Markdown/image manifest hashes without opening a browser. Read TAP totals and logs for each group.

## Gotchas

Selection opportunity is not latency SLO. A bounded local budget does not prove every production adapter is wired. Logical deletion is not secure erase or deletion from backups. Actual external cost/model usage is not exercised.
