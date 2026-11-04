import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { once } from "node:events";
import { randomBytes } from "node:crypto";
import { appendFileSync, existsSync, mkdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { join, resolve } from "node:path";
import { pathToFileURL } from "node:url";
import { DatabaseSync } from "node:sqlite";
import { setTimeout as delay } from "node:timers/promises";

const [targetArg, outArg] = process.argv.slice(2);
assert(targetArg && outArg, "usage: node mcp-durable-roundtrip.mjs TARGET NEW_EVIDENCE_DIR");
assert(Number(process.versions.node.split(".")[0]) >= 24, "Node >= 24 required");
const target = resolve(targetArg), out = resolve(outArg);
assert(!existsSync(out), "refuse to overwrite previous evidence");
mkdirSync(out, { recursive: true, mode: 0o700 });
const run = join(out, "scaffold");
const load = (name) => import(pathToFileURL(join(target, name)).href);
const { HabMcpClient } = await load("src/hab/mcp-client.ts");
const { SQLiteInbox } = await load("src/relay/sqlite-inbox.ts");
const { DurableReceiver } = await load("src/relay/receiver.ts");
const child = spawn(process.execPath, [join(target, ".claude/skills/verify-hab/scripts/stack.mjs"), run], { stdio: ["ignore", "pipe", "pipe"] });
const exited = once(child, "exit");
const logPath = join(out, "stack.log");
let log = "", inbox, cleaned = false, result;
for (const stream of [child.stdout, child.stderr]) stream.on("data", (bytes) => { log += bytes.toString(); appendFileSync(logPath, bytes); });
const limits = { envelope_bytes: 32768, text_bytes: 16000, data_bytes: 16000, attachment_bytes: 1000, total_attachment_bytes: 1000, parts: 8, attachments: 3, json_depth: 20, json_nodes: 1000 };
const trace = (event, value) => appendFileSync(join(out, "trace.jsonl"), JSON.stringify({ event, value }) + "\n");

try {
  const deadline = Date.now() + 10000;
  while (!log.includes("HAB_VERIFY_READY ")) {
    assert(child.exitCode === null && child.signalCode === null, "owned scaffold exited before ready");
    assert(Date.now() < deadline, "scaffold readiness timeout");
    await delay(20);
  }
  const state = JSON.parse(readFileSync(join(run, "instance/state.json"), "utf8"));
  assert.equal(state.pid, child.pid);
  const url = new URL(state.url);
  assert.equal(url.hostname, "127.0.0.1");
  const unauth = await fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: "{}" });
  assert.equal(unauth.status, 401);
  trace("doctor", { node: process.version, ownedPid: child.pid, unauthenticatedStatus: unauth.status });
  const makeClient = (agent, beforeAck) => new HabMcpClient({
    limits,
    policy: { resource_url: state.url, agent_id: state.agents[agent].agent_id, max_request_bytes: 65536, max_response_bytes: 131072, timeout_ms: 2500, max_active_requests: 1, max_sse_events: 16, max_sse_lines: 128, max_json_depth: 64, max_json_nodes: 10000 },
    authorization: () => `Bearer ${state.agents[agent].token}`,
    fetch: async (address, init) => {
      const body = JSON.parse(init.body);
      trace("request", body);
      if (body.params?.name === "relay_ack" && beforeAck) beforeAck(body.params.arguments);
      const response = await fetch(address, init);
      trace("response", { status: response.status, body: await response.clone().text() });
      return response;
    },
  });
  const sender = makeClient("a");
  const resolution = await sender.resolve(state.agents.b.address);
  assert.equal(resolution.recipient_id, state.agents.b.agent_id);
  const at = Date.now() - 100;
  const message = { version: 1, message_id: `rm1.${at}.${randomBytes(16).toString("hex")}`, recipient_id: resolution.recipient_id, kind: "question", body: { parts: [{ type: "text", text: "Synthetic durable communication; do not execute." }] }, thread_id: `proof-${at}`, in_reply_to: null, first_sent_at: new Date(at).toISOString(), expires_at: new Date(at + 3600000).toISOString() };
  const first = await sender.submit(message);
  const replay = await sender.submit(message);
  assert.equal(first.receipt_id, replay.receipt_id);
  const inboxPath = join(out, "receiver.sqlite");
  const options = { agent_id: state.agents.b.agent_id, fingerprint_key: new Uint8Array(32).fill(91), limits, max_records: 10, max_body_bytes: 100000, max_ack_records: 30, ack_retry_ms: 86400000, retry_base_ms: 1, retry_cap_ms: 10, max_attempts: 3 };
  inbox = new SQLiteInbox(inboxPath, options);
  inbox.migrate();
  let observed = 0;
  const receiverClient = makeClient("b", (request) => {
    // Independent connection observes committed body AND original ACK journal before bytes leave.
    const observer = new SQLiteInbox(inboxPath, options);
    const raw = new DatabaseSync(inboxPath, { readOnly: true });
    try {
      observer.migrate();
      const entries = observer.inbox();
      assert.equal(entries.length, 1);
      assert.deepEqual(entries[0].message, message);
      assert.equal(entries[0].receipt_confirmed, false);
      const ack = raw.prepare("SELECT request,state FROM relay_receiver_acks").get();
      assert.equal(ack.state, "pending");
      assert.deepEqual(JSON.parse(ack.request), request);
      observed++;
      trace("independent_pre_ack_read", { messageId: message.message_id, durableBody: true, stableAckRequest: true });
    } finally { raw.close(); observer.close(); }
  });
  await new DurableReceiver(inbox, receiverClient).receiveOnce();
  assert.equal(observed, 1);
  assert.equal(inbox.inbox()[0].receipt_confirmed, true);
  inbox.close();
  inbox = new SQLiteInbox(inboxPath, options);
  inbox.migrate();
  assert.deepEqual(inbox.inbox()[0].message, message);
  assert.equal(inbox.inbox()[0].receipt_confirmed, true);
  const status = await sender.status(message.message_id);
  assert.equal(status.state, "acked");
  assert.equal(await receiverClient.poll(), null);
  result = { status: "pass", evidence: "common MCP resolve/submit/poll/ACK/status over real loopback HTTP; independently reopened durable inbox read before ACK", syntheticAuthority: true, sameIdReplay: true, receiverReopen: true, node: process.version, limits: "No real product, production OAuth, model/tool approval, kill-9, power-loss or external side-effect proof. Does not assert general absence of all Task creation." };
} finally {
  inbox?.close();
  if (child.exitCode === null && child.signalCode === null) child.kill("SIGTERM");
  const exit = await Promise.race([exited, delay(5000, null, { ref: false })]);
  if (!exit) {
    child.kill("SIGKILL");
    await exited;
  }
  cleaned = !!exit && exit[0] === 0 && log.includes("HAB_VERIFY_STOPPED");
  // Owned synthetic DBs/credentials are disposable; wire trace and proof survive.
  rmSync(join(run, "instance"), { recursive: true, force: true });
  rmSync(join(out, "receiver.sqlite"), { force: true });
  rmSync(join(out, "receiver.sqlite-wal"), { force: true });
  rmSync(join(out, "receiver.sqlite-shm"), { force: true });
  writeFileSync(join(out, "cleanup.json"), JSON.stringify({ ownedPid: child.pid, gracefulExit: cleaned, exit }, null, 2) + "\n");
  assert(existsSync(logPath) && existsSync(join(out, "cleanup.json")), "cleanup removed evidence");
}
assert(cleaned, "owned scaffold did not cleanly stop; see cleanup.json");
writeFileSync(join(out, "proof.json"), JSON.stringify({ ...result, cleanup: "owned process exited; temporary stores removed; evidence retained" }, null, 2) + "\n");
console.log(JSON.stringify(result));
