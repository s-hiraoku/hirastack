# Durable receive

## Sub-features

Commit body/dedup/original ACK before network ACK; same-ID receipt; ACK response loss recovery; receiver reopen; failed save sends zero ACK.

## How to get to it (user POV)

Send one synthetic text message to a registered recipient over MCP, then receive and later inspect sender delivery state.

## Driving it with hirastack

mcp-durable-live reads receiver SQLite from an independent connection immediately before sending ACK; then sender status must be acked and reopened inbox must preserve the same message. durable-receive and immutable-delivery exercise response loss, conflict, old lease and finite retries.

## Gotchas

Raw relay_poll followed by direct relay_ack only proves the wire protocol. Do not substitute it for durable receiver proof. The live helper asserts receiver reopen, not process crash. C-ACK-PROOF remains open until original HAB verification assets are maintained.
