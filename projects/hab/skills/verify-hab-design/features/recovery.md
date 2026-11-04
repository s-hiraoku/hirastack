# Recovery and evidence

## Sub-features

Original IDs/receipts and unknown outcomes survive logical recovery; snapshot scope is explicit; public success does not imply production acceptance.

## How to get to it (user POV)

Observe the same received message after inbox reopen and run the explicit snapshot helper tests on disposable stores.

## Driving it with hirastack

mcp-durable-live proves committed inbox reopen and owned child teardown. logical-snapshot covers declared profile restore. crash-and-production-recovery and deployment-and-cost remain manual/unverified; inspect their missing prerequisites and C-CRASH-CLAIM.

## Gotchas

Clean reopen is not kill-9. Same-volume logical restore is not power-loss or separate failure-domain proof. Snapshot excludes Registry/Task/authority that need current reconciliation. Missing cleanup/proof files cannot be treated as success.
