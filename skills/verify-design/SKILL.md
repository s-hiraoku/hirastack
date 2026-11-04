---
name: verify-design
description: Resolve an existing design verification contract and project verify skill, execute the reviewed checks and user-path recipes, and report source-bound evidence, failures, ambiguity and unverified scope.
---

# Verify design

This coordinator runs existing verification. It does not silently author a new contract, settle design disputes, change product code, install services or refresh source pins.

## Resolve and prepare

Read AGENTS.md, the exact project's contract, principles, review notes, generated verify skill and feature map. Resolve target origin, checkout, commit and dirty state. Several plausible contracts require a concrete selection; none means use create-design-verification. Locate the hirastack checkout and run its CLI there.

Inspect every command/helper and prerequisites before `--execute`. External credentials, production data, paid models, permanent services and remote writes need the user's already granted scope. Synthetic local fixtures may run within the task's verification scope. Do not use a user's existing live process as an isolated fixture.

```sh
python3 -m hirastack audit --target "$TARGET" --spec "$BUNDLE/contract.json"
python3 -m hirastack run --target "$TARGET" --spec "$BUNDLE/contract.json" --out "$NEW_RUN" --execute
```

Audit failure means maintain-design-verification must review the drift. Do not execute stale commands. Audit current only proves index/citation currency. The run must use a new evidence directory outside the target. Existing evidence is never overwritten. `--execute` is required to start commands; omitting it produces an incomplete plan.

## Drive and observe

Follow the project skill's Launch, Doctor, Drive, Evidence and Cleanup sections. The coordinator owns driving. Capture the action and independent result/side effects, not just the final response. For a full claim cover every mapped public feature; a single proved path establishes only that path. CLI checks supplement a feature map; they do not automatically replace every mapped feature.

Check logs and assertion totals, not only exit status. No tests, skipped cases, timeout, failed cleanup, inaccessible feature or environment error cannot become a pass. Distinguish synthetic authority, loopback protocols, in-process reopen, process restart, kill-9 and physical restore. Read check `proves`, `limitations` and requirement `scope` together before reporting a result.

For manual requirements, perform the recipe only if authorized and accessible; retain evidence and describe it separately. This CLI conservatively leaves manual requirements unverified even when an agent reports a manual observation; do not edit a report to turn that into an automated pass. Open design conflicts remain open despite green independent checks.

## Cleanup and report

Always run owned teardown, including after failure. Verify proof artifacts still exist and inspect cleanup records. A local timeout/abort does not prove remote work stopped. An unexpected product action is a finding, not permission to retry with different identity, scope or input.

Read `report.json`, `report.md` and each log. Report target commit/tree identity, spec hash, requirement/check results, unresolved questions, substitutions, coverage gaps and artifact paths. Exit `0` means all required recorded scopes passed; `1` means a checked behavior failed; `2` means incomplete/stale/invalid. Do not call the product globally compliant when any relevant scope is manual, proposed, inaccessible, conflicted or outside the contract. Never commit, publish evidence, create PRs, merge, deploy or message others solely because verification ran.
