---
name: open-verified-pr
description: Open a pull request whose description carries the state-transition chart of every formal verification check the change touches, reviewed for bugs, with the verified scope, bounds and remaining review stated plainly. Use when the user asks to open or prepare a PR for a change in a project that has formal verification skills.
disable-model-invocation: true
---

# Open a verified pull request

The goal is a PR whose reviewer can decide mostly from one state-transition chart: the chart shows every order of steps inside the model's scope, the agent has already looked for bugs in it, and the description says exactly what the chart does not cover. A chart is only as trustworthy as the model behind it, so the PR must also show that the model still describes the code at this commit.

The user's request to open the PR is the authorization for this skill's remote writes: pushing the current work branch and opening one PR. If this skill was reached without such a request, stop after drafting the description. It never authorizes merging, deploying, force-pushing, pushing to the default branch or messaging anyone. Do not change product code to make a check pass.

Resolve [the PR body layout](references/pr-body.md) relative to this skill's installed source.

## Prepare the change

Read the target's AGENTS.md, contribution notes and PR template (`.github/pull_request_template.md` or `.github/PULL_REQUEST_TEMPLATE/`). The template's headings come first; this skill's sections go under or after them. Resolve the base branch, the merge base, the head commit and the dirty state. Uncommitted work is not part of the PR: commit it only if the user asked for that, otherwise stop and say what is uncommitted. Run the fast checks (tests, type check, lint) that the project requires before a PR, and record their totals.

## Find the formal checks this change touches

Find the project's formal verification skills by what they do, not by name: project-local skills (`.agents/skills/`, `.claude/skills/`, `.cursor/skills/`) that run a model checker, prover or code-level verifier against named code. For each check read its property, covered files and functions, bounds, assumptions, run command and recorded sync commit.

Compare the PR diff (merge base to head) with each coverage record. Also count as touched: a covered function that was renamed, split or moved, and new code that writes the state a check guards. Classify every changed file as covered by a named check or covered by none.

- No check exists: say so in the PR, review the diff yourself, and name the formal verification creation workflow as a follow-up when the diff contains concurrency, retries, a state machine, a parser or unsafe code. Do not invent a model inside this skill.
- A touched check whose covered code changed after its sync commit: run the formal verification maintenance workflow first. Its outcome (in sync, updated, bug, blocked) goes into the PR. Put verification updates in their own commit, separate from product changes. Drift that this PR did not cause belongs in a separate PR; mention it rather than mixing it in.
- An untouched check: leave it out of the chart section and list it as untouched.

## Run each touched check and draw its chart

Run each touched check with its own command, at the head commit, into a scratch output folder outside the repository. When the check is a state-machine model, read the result with the statechart workflow and keep its chart, report and rerun command. Keep the modeling language the project's verify skill already uses; do not switch languages inside a PR. Follow that workflow's current instructions for running, labeling and hiding steps; do not copy its commands or paths into this skill or the target.

For a TLA+ model, check it with [tla-ts](https://github.com/aidenybai/tla-ts), a TLC-compatible model checker that runs on Node without a JVM. Use the version the project pins, or pin one exact npm version and record it in the PR. When the installed statechart workflow drives its own checker instead of tla-ts, run it as it is, also check the same spec and config with tla-ts, and compare the verdict, each broken rule and the distinct-state count. A difference makes the check blocked, not passed; report both outputs. When tla-ts rejects a construct as unsupported, say so and keep the other checker's result as the evidence.

Label states and arrows in the words of the PR's reader. Keep the chart near 20 arrows. Keep every state of a bug path and every mark.

When the PR changes the model or the covered behavior, also draw the chart at the merge base with the same view, and list the states and arrows that were added, removed or relabeled. That difference is what the reviewer is approving.

## Look for bugs in the chart before anyone else does

A passing check proves only the rules that were written. Review the chart against the code and the PR's stated intent, preferably with a fresh reader that is given the code and the chart but not your conclusion:

- Every `breaks` or `mayBreak` state, and every rule listed as not checked.
- A reachable state that the PR's intent says must not happen, even when no rule marks it. Propose the missing rule as an invariant in the reader's words and run it; never weaken an existing rule.
- An expected step that has no arrow, a state with no way out that is not a correct end state, a state that cannot be reached, and steps the view hides.
- An atomic step in the model that is several steps in the code, a code path in the diff that the model has no action for, and bounds too small to reach the changed behavior.

Replay each bug path against the real code, one step per action, as a test or a live reproduction. If a step cannot happen in the code, the model is wrong: fix the verification and say what was wrong. If every step happens, it is a bug in the code: report it in the PR with the path in the code's words and the harm in one sentence. Do not hide it to keep the PR green.

## Decide what the reviewer still has to read

The PR may say that reading the chart is enough only when all of these hold:

- every changed file that carries behavior is covered by a touched check, or the PR names the tests that exercise it;
- each touched check is in sync or updated at the head commit, ran at that commit and passed every rule, with no rule unchecked and no state-budget truncation;
- the chart review found nothing unresolved, and every bug path was replayed;
- each property has been shown to fail on a deliberately broken variant (recorded by the verify skill or rerun now);
- the project's required fast checks passed.

Otherwise list the files and questions that need human code review. The chart never covers what is outside its model: say so in the description, and never describe a pass as proof of the whole system.

## Open the PR

Write the description with [the PR body layout](references/pr-body.md). Embed each chart as a fenced `mermaid` block, which GitHub renders in the description. A description is limited to 65,536 characters: when the charts exceed it, keep the bug paths and the merge-base difference inline and attach the full chart files where the project's process allows.

Push the work branch and open the PR against the base branch. Open it as a draft when any check is a bug or blocked, when the chart review left a question, or when required fast checks failed. Follow the user's or project's rules for assignees, reviewers and labels. Do not merge, approve or enable auto-merge.

## Hand off

Tell the user the PR link, which checks ran and their outcomes, each bug in one line, whether the description says the chart is sufficient, and what still needs human review. Suggest keeping the verification fresh by running the maintenance workflow per PR or on a schedule; set up a schedule or CI job only after the user agrees.
