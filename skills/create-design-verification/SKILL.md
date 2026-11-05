---
name: create-design-verification
description: Create a source-cited design verification contract and project-local verification skill from all project design documents; prove the generated harness with real behavior and negative controls.
---

# Create design verification

Use the hirastack CLI from its repository root. This is an agent workflow: source discovery is mechanical, interpreting design intent is your responsibility. Read [contract format](../../docs/contract-format.md) and [architecture](../../docs/architecture.md). Resolve these relative to this skill's installed source; if only this directory was installed, locate the hirastack checkout before continuing.

## Discover the project

Read AGENTS.md, existing `.agents/skills`, `.claude/skills`, `.cursor/skills`, README, build/test scripts, actual entry points and repository identity. Reuse a project verify skill when present; do not create a competing feature map. Resolve the target from user context and Git remotes. If several targets remain equally plausible, ask for the missing identity while continuing read-only discovery.

Use `rg --files --hidden` and `git ls-files`, including ignored/private locations only when authorized and appropriate, to locate design material. Cover architecture, ADRs, product specs, protocols, schemas/migrations/config contracts, profiles, security, operations, test plans and historical result documents. Follow referenced local documents. Index vendored method docs separately; explicit exclusion needs a reason. External design references need a recorded revision and access outcome; an unread link is pending. Note binary/PDF/wiki/issue material and the CLI's discovery limits. Do not equate an inventory with review.

Run:

```sh
python3 -m hirastack init --target "$TARGET" --name "$PROJECT" --repository "$ORIGIN" --spec "$BUNDLE/contract.json"
python3 -m hirastack inventory --target "$TARGET"
```

`init` writes a draft and refuses overwrite. Read every included document in full. Keep a row per document with purpose, extracted invariants, role and review status. For large projects use read-only source readers per coherent subsystem; the coordinator reconciles their citations and owns all live driving. Never delegate simultaneous driving of a shared app.

## Extract the design

Document the problem and intended user outcome, component responsibilities, trust/authority boundaries, non-goals, state meanings, failure/recovery rules, finite resource/cost limits and invariants that must survive refactoring. Retain the reason each exists. Separate an adopted requirement, a future proposal, a historical observation and an implementation claim. An old fixed pilot must not constrain every later capability without evidence.

Each requirement needs a stable ID, scope, statement, rationale, decision state and exact path/line range with excerpt SHA256. Link to the recorded commit for human reading. Give each document a review summary even if it yields no new principle. Derive requirements from authoritative design and user instructions, not from current behavior just because it passes.

Record contradictory meanings, explicit supersession, subsystem/version differences and unresolved priorities. Later timestamps or longer files alone do not decide authority. Keep both sources and a concrete question for unresolved cases. Do useful independent verification without inventing a decision. User instructions govern implementation intent; preserve evidence of their scope without publishing private conversation content.

## Generate useful verification

Write a contract in `projects/<name>/` here or in a user-selected verification repo. Keep generic mechanisms free of target/product names. Generate or maintain the runtime-native project skill (`.agents/skills/verify-<name>` on Codex) with frontmatter and exact Launch, Doctor, Drive, Evidence, Cleanup and Helpers sections. A skill stored here as an example is not automatically installed in the target.

Map every active requirement to checks; use an honest manual recipe for unautomatable behavior. A manual requirement stays unverified in this CLI. Tests must observe a user/protocol path and relevant side effects. Static import checks establish dependency boundaries only. ACK, HTTP 200, mock responses, open processes or a rendered final screen alone cannot prove broader execution semantics. Build a feature map for each public entry point; inherited maps may need a source review before reuse.

Choose existing tests before new harness machinery. Test storage, real protocols and failure boundaries; mock only isolated external authority/services and name the substitution. Include controls that should fail (e.g. ACK before commit, missing evidence, forbidden dependency, zero tests or skipped case) and harmless cases that should not fail (comments, optional execution adapters outside communication). State residual false positives/negatives.

Launch must start from isolated empty state; readiness must include usability. Doctor verifies owned instance and identity without changing state. Never commandeer a user process/port. Helpers must be directly invokable, bounded, and document their argv and prerequisites. Cleanup stops only owned processes, removes disposable state, preserves evidence and records uncertain outcomes.

## Prove and hand over

Read the generated commands and their side effects. `--execute` runs trusted arbitrary argv and grants no additional access to a live system.

```sh
python3 -m hirastack audit --target "$TARGET" --spec "$BUNDLE/contract.json"
python3 -m hirastack run --target "$TARGET" --spec "$BUNDLE/contract.json" --out "$NEW_RUN" --execute
```

Run the generated instructions end to end for at least one mapped real path: launch, doctor, action, independent resulting-state observation, evidence, cleanup, evidence-exists check. Run cleanup after failed attempts too and retain their logs. If the target cannot start or cannot be exercised, report the exact blocker and leave the generated skill draft. A stand-in result must list setup, substitutions and unverified real-target behavior.

Report requirement/check coverage, real failures, unresolved decisions, skipped/manual/inaccessible scope and artifact paths. Distinguish a working harness from complete product compliance. Point to maintain-design-verification and verify-design. Do not commit, push, open a PR, merge, deploy or message third parties merely because the skill ran.
