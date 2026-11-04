# Authority and state

## Sub-features

Verified current identity and group scope; denied impersonation; separate Task acceptance; recipient-owned judgment; honest delivery/working/stop states.

## How to get to it (user POV)

Use synthetic groups and try authorized and foreign mailbox actions. Actual recipient owner approval is a separate product path.

## Driving it with hirastack

current-authorization tests shared-group opt-in, foreign denial, revocation and durable roundtrip. explicit-task-boundary verifies ACK creates no Task. real-recipient-policy and state-semantics are manual checks with concrete instructions in contract.json and remain unverified.

## Gotchas

Group-shared credentials do not identify which Bot executed a call. WORKING's current coordinator meaning and proposed recipient-processing meaning are unresolved. A synthetic policy assertion cannot establish real tool approval or absence of file/shell/plugin/subagent/network effects.
