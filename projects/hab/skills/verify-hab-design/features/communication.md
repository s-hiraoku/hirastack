# Common communication

## Sub-features

Standard MCP resolve/submit/poll/ACK/status without model startup; optional execution stays outside Relay. A2A/MCP application state is shared.

## How to get to it (user POV)

An authenticated synthetic agent resolves a recipient address and sends text through its common MCP client. Receiving is independent of executing a Task.

## Driving it with hirastack

Run contract checks dependency-boundary, boundary-controls, mcp-durable-live, model-free-supervisor, explicit-task-boundary and shared-application. The live helper captures request/response and sender status; supervisor/bridge tests assert Task count and explicit acceptance boundaries.

## Gotchas

Synthetic auth is a substituted boundary. Optional old fixed Hermes driver outside Relay is allowed; product-name strings in comments are not violations. GUI parity is manual/unverified. Static edges cannot prove injected runtime callbacks are safe.
