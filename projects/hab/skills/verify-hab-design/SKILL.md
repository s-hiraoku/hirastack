---
name: verify-hab-design
description: Verify HAB communication design invariants through a source-cited contract, AST dependency checks, real MCP/HTTP with durable SQLite readback, and bounded failure suites; report manual and unresolved scope honestly.
---

# Verify HAB design

This reference skill lives in hirastack; it is not installed into or editing HAB. Run commands from hirastack root with `HAB` pointing to an isolated HAB checkout. Consult [feature index](features/README.md), [principles](../../design-principles.md) and [conflicts](../../conflicts.md).

## Launch

Node >=24, Python >=3.11, Git; HAB dependencies prepared with `npm ci --no-audit --no-fund` in that isolated checkout. No real credential, user DB, broker or model is needed. Read `projects/hab/contract.json` argv first.

`mcp-durable-roundtrip.mjs` launches HAB's existing verify-hab scaffold on an ephemeral loopback port, with synthetic verified agents and fresh private SQLite state. It waits at most10s for HAB_VERIFY_READY and an owned PID. Other suites create their own fresh fixtures. No shared live instance is driven.

```sh
python3 -m hirastack audit --target "$HAB" --spec projects/hab/contract.json
python3 -m hirastack run --target "$HAB" --spec projects/hab/contract.json --out "$NEW_RUN" --execute
```

## Doctor

Audit must be current. The live helper checks Node major, child still alive, state PID equals the child, loopback URL and unauthenticated HTTP401 before driving. Every fresh helper invocation repeats this doctor. An unexpected exit/readiness/auth result fails the helper and triggers its finally cleanup; it does not drive a foreign process.

## Drive

The live helper invokes common HabMcpClient against actual MCP/HTTP: resolve recipient → submit → exact retry → DurableReceiver poll → independent SQLite connection reads committed body and original pending ACK → actual network ACK → sender status → inbox close/reopen. It never edits DB rows to make the path pass.

Run the fourteen automatic checks and inspect all check results. Full current contract remains incomplete because manual requirements and open conflicts exist. Existing HAB verify-hab has seven other public-feature recipes; this skill's five additional design features do not claim all seven were live driven.

## Evidence

`$NEW_RUN/report.json` and `report.md` bind the target commit/visible-tree hash, Git status, spec hash and runner hash to each result. Logs are named by check ID. The live path records `$NEW_RUN/mcp-live/trace.jsonl`, stack.log, proof.json and cleanup.json. Trace contains synthetic payloads only; do not adapt it to private real content without controlling disclosure.

Both pre-ACK committed body/journal and post-ACK independent sender state are asserted. Evidence of normal inbox reopen is not kill-9, power-loss, production identity or actual recipient model/owner-approval proof. Negative failure suites supplement the happy live path.

## Cleanup

The live helper's finally closes the receiver store, SIGTERMs only its spawned child, waits up to5s, and uses SIGKILL only for that child if needed. Non-graceful cleanup fails. It removes owned synthetic DBs/instance, keeps trace/log/proof/cleanup and asserts evidence survives. The runner also terminates its owned command process group on exit/timeout. Missing proof or cleanup records mean incomplete coverage. Never kill by executable name.

## Helpers

```sh
node projects/hab/checks/communication-boundary.mjs "$HAB"
node projects/hab/checks/communication-boundary.mjs "$HAB" --self-test
node projects/hab/checks/mcp-durable-roundtrip.mjs "$HAB" "$NEW_LIVE_DIR"
```

AST check loads the target's TypeScript parser, traverses literal imports/exports/require/import types from all `src/relay/*.ts`, and restricts project dependencies to Relay plus explicit protocol/security shared modules. It does not inspect dependency package internals or prove runtime capability isolation. The self-test uses only disposable scratch source. The live helper uses target source and existing synthetic scaffold; all helpers start from the named target revision and write only new evidence/scratch state.
