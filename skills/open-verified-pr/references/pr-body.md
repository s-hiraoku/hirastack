# PR body layout

Use the project's PR template headings first, and put these sections under or after them. Write in the reader's words; keep model variable and action names out of prose and labels. Leave no placeholder in the final body.

````markdown
## Summary

One or two sentences: what changes for the user and why.

## Formal verification

| Check | Property (plain sentence) | Outcome | Bounds and assumptions | Sync commit |
| --- | --- | --- | --- | --- |
| name | the promise the code keeps | in sync / updated / bug / blocked | constants, constraints, what is assumed | sha |

Changed files covered: each file with the check that covers it.
Changed files not covered: each file, and how it was reviewed instead.
Untouched checks: list, or "none".

### State-transition chart: check name

```mermaid
chart text exactly as the statechart workflow produced it
```

- Changed since the merge base: states and arrows added, removed or relabeled.
- Hidden steps: the steps the chart hides, or "none".
- Rules not checked: list, or "none".

### Chart review

- What the review checked: marked states, unintended reachable states, missing arrows, dead ends, model-to-code atomicity, bounds.
- Each bug: the rule, the reader's sentence for it, the path as numbered steps in the code's words, the harm, and the replay evidence.
- Model corrections made during the review, and why.

## Reviewer guide

Either "Within the scope above, reading the chart is sufficient: every condition in the PR skill holds." or the files and questions that need human code review.

Outside every model: what the verification does not cover.

## Reproduce

The command that regenerates each chart into a new output folder, the checker and its exact version (for example tla-ts and its npm version), and the project's fast checks with their totals.
````
