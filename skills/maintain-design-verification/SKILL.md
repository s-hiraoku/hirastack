---
name: maintain-design-verification
description: Maintain an existing source-cited design verification contract when design, implementation, dependencies, public surfaces or verification evidence change, without weakening requirements to fit regressions.
---

# Maintain design verification

Resolve the target, existing contract, generated verify skill and feature map. Read their instructions plus [contract format](../../docs/contract-format.md). If none exists, use create-design-verification. Edit verification-owned files only; product changes belong in a separate authorized task.

## Audit and source review

Run `python3 -m hirastack audit --target "$TARGET" --spec "$BUNDLE/contract.json"` and inspect `git diff` since `project.baseline`, dependency changes and new entry points. Re-enumerate design material and external references. New/deleted/renamed documents, cited text changes and changed test semantics all need review. Do not refresh hashes just to make audit pass.

Check the feature index against actual sibling files and public routes/commands. Use one read-only source reader per affected feature/subsystem; each returns behavior, source citations, likely design/doc/harness drift and one bounded live recipe. Source readers do not edit or drive the app. The coordinator checks every returned citation and reconciles overlapping recipes.

Re-read changed design documents and every affected requirement; revisit untouched foundational principles when a new architecture changes their context. Maintain a row for every document and explicit exclusion reasons. Preserve stable requirement IDs and source provenance. Deletions need a disposition (superseded, moved, intentionally removed, unresolved), not disappearance from the ledger.

Classify findings:

| Finding | Action |
| --- | --- |
| Explicitly changed, authorized design | Update requirement, rationale, decision source and regression checks |
| Historical/subsystem scope difference | Record the scope and evidence without declaring a global conflict |
| Conflicting authority/meaning | Keep both sources; leave open and affected requirement blocked |
| Stale verification recipe or missing drive capability | Fix only verification assets; re-drive the changed path |
| Product regression | Report source + live evidence; preserve intended requirement |
| Missing auth/platform/product capability | Record attempted route and exact prerequisite; remain unverified |

Do not accept broader execution rights because current implementation already has them. Do not convert a crash requirement to clean reopen, a durable-save requirement to raw ACK, a real-owner requirement to a synthetic token, or an unknown outcome to success.

## Live maintenance pass

The coordinator drives the existing skill's launch model. Exercise every mapped feature at least once for a full maintenance claim; a focused partial pass reports covered and remaining features. Doctor before the first drive, on each fresh instance, and after any surprising failure; reset or relaunch when healthy-process checks cannot detect a stuck state. Preserve evidence across every cleanup. Kill only processes owned by the run. Re-drive every harness correction before finishing.

Run current contract checks with a new evidence directory. Compare negative controls and false-positive controls as well as positive cases. Update baseline/hash/citations only after the corresponding source review, then rerun. Keep historical failed evidence; do not rewrite it to use the new commit.

Outcomes are clean, changed, or blocked, with explicit coverage. Clean requires source and live coverage of all promised scope. Changed means verification corrections were proved locally; it does not mean a PR or commit exists. Blocked includes partial live coverage or unresolved design authority. Report product issues separately with exact evidence. Commit/push/PR/merge/deploy require the user's existing authorization and are never a side effect of maintenance itself.
