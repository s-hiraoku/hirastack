---
name: setup-hirastack
description: "Prepare this repo for the hirastack skills: check the CLI and prerequisites, find existing verification and formal verification skills, and record where the verification bundle lives. Run once per repo before the other hirastack skills."
disable-model-invocation: true
---

# Set up hirastack

Record, once per target repository, what the other hirastack skills would otherwise rediscover or ask: how to run the CLI, where the verification bundle lives, and which verification and formal verification skills the project already has. This is a prompt-driven setup, not a script. Explore, present what you found, confirm with the user, then write. It installs nothing and changes no global configuration.

## 1. Explore

Resolve the target from the current directory, `git remote -v` and `git status`. Read whatever exists; do not assume:

- `CLAUDE.md` and `AGENTS.md` at the target root, and whether either already has a `## hirastack` section.
- An existing design verification bundle: any `contract.json` whose top level has `version`, `project`, `documents`, `requirements` and `checks`.
- Project-local skills in `.agents/skills/`, `.claude/skills/` and `.cursor/skills/`: a verify skill (launch/drive/evidence), and formal verification skills that run a model checker, prover or code-level verifier. Identify them by what they do, not by name.
- Design material at a glance (`docs/`, ADRs, specs, README), only to estimate the size of the first create run. Reading it all is create-design-verification's job.

Resolve the CLI:

- When this skill sits inside a hirastack checkout or plugin, the root is two levels above this skill and holds `hirastack/cli.py`. Run `python3 -m hirastack` from that root.
- Otherwise, when this skill was installed alone (for example with `npx skills add` or `gemini skills install`), use `uvx --from git+https://github.com/s-hiraoku/hirastack@<commit> hirastack`. Resolve the current commit of `main` with `git ls-remote https://github.com/s-hiraoku/hirastack main`, and pin it. Use `pipx run --spec git+https://github.com/s-hiraoku/hirastack@<commit> hirastack` when `uv` is missing.

Run `<cli> doctor --target <target>` and keep its JSON. A missing required tool (Python 3.11 or later, Git, a readable POSIX `ps`) blocks every CLI step. Missing optional items matter only for open-verified-pr on a project that has formal verification.

## 2. Present findings and ask

Summarise what is present and what is missing, then take these one at a time, leading with the recommended answer so the user can accept it in a word. Skip a question that exploration already settled.

**A. Bundle location.** Recommend `docs/design-verification/` in the target repository. Offer a separate verification repository only when the user does not want verification files in the product repository. An existing bundle is the answer; do not create a second one.

**B. CLI pin.** For a standalone install, confirm the pinned commit. For a plugin, record only that the CLI comes from the plugin: its root is a version-named cache folder that changes on every update, so the other skills resolve it two levels above themselves at run time. For a checkout, record its path and run `python3 -m hirastack` there.

**C. Prerequisites the user must install.** List only what doctor reported missing and the project needs. For pstack's statechart and formal verification skills, give the install the user's agent supports, such as `claude plugin marketplace add cursor/plugins` then `claude plugin install pstack@cursor-plugins` in Claude Code, or the Cursor plugin. Do not run installs yourself.

## 3. Confirm and write

Pick the file to edit: `CLAUDE.md` if it exists, else `AGENTS.md`. If neither exists, ask the user which to create. Never create one when the other exists. If a `## hirastack` section already exists, update it in place and keep the user's other sections untouched.

Show the user this draft and let them edit it before writing:

```markdown
## hirastack

- Verification bundle: `docs/design-verification/` (contract: `docs/design-verification/contract.json`, not yet created)
- CLI: `uvx --from git+https://github.com/s-hiraoku/hirastack@<commit> hirastack` (or: from the hirastack plugin, resolved at run time)
- Project verify skill: none yet (create-design-verification makes one)
- Formal verification skills: none found
- Prerequisites missing: <from doctor, or "none">
```

Write only this section. Do not create the bundle, the contract or any skill here; `init` and the contract belong to create-design-verification.

## 4. Done

Tell the user setup is complete and what to run next: create-design-verification when no contract exists, otherwise verify-design. Mention that create-design-verification, maintain-design-verification, verify-design and open-verified-pr read this section, and that they can edit it by hand or re-run this skill after moving the bundle or changing the CLI pin.
