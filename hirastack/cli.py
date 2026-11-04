"""Dependency-free CLI. A successful command is evidence, not a design decision."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import shutil
import subprocess
import sys
import tempfile
import time

DOCUMENT_SUFFIXES = {".md", ".mdx", ".rst", ".adoc", ".txt"}
ID = re.compile(r"[A-Za-z][A-Za-z0-9_-]{0,79}\Z")


class Invalid(ValueError):
    pass


def digest(data):
    return hashlib.sha256(data).hexdigest()


def git(root, *args):
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True)
    if result.returncode:
        raise Invalid("target must be a Git checkout: " + result.stderr.decode(errors="replace"))
    return result.stdout


def inside(root, relative):
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        raise Invalid(f"expected relative path: {relative!r}")
    path = (root / relative).resolve()
    if not path.is_relative_to(root):
        raise Invalid(f"path escapes root: {relative}")
    return path


def tracked(root):
    return sorted(p.decode("utf-8") for p in git(root, "ls-files", "-z").split(b"\0") if p)


def visible(root):
    return sorted(set(p.decode("utf-8") for p in git(root, "ls-files", "--cached", "--others", "--exclude-standard", "-z").split(b"\0") if p))


def document_paths(root):
    return [p for p in visible(root) if Path(p).suffix.lower() in DOCUMENT_SUFFIXES or (p.startswith("docs/") and Path(p).suffix.lower() not in {".png", ".svg", ".jpg", ".jpeg", ".gif", ".webp", ".pdf"})]


def snapshot(root):
    files = []
    for name in visible(root):
        path = inside(root, name)
        files.append((name, digest(path.read_bytes()) if path.is_file() else "missing"))
    return {
        "commit": git(root, "rev-parse", "HEAD").decode().strip(),
        "visible_tree_sha256": digest(json.dumps(files, ensure_ascii=False).encode()),
        "status": git(root, "status", "--porcelain=v1", "--untracked-files=all").decode(),
    }


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def require(condition, message):
    if not condition:
        raise Invalid(message)


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def unique_ids(items, label):
    require(isinstance(items, list), f"{label} must be an array")
    found = set()
    for item in items:
        require(isinstance(item, dict), f"{label} entry must be an object")
        key = item.get("id")
        require(isinstance(key, str) and ID.fullmatch(key), f"invalid {label} id: {key!r}")
        require(key not in found, f"duplicate {label} id: {key}")
        found.add(key)
    return found


def validate(spec, root):
    require(isinstance(spec, dict) and spec.get("version") == 1, "spec version must be 1")
    require(isinstance(spec.get("project"), dict), "project must be an object")
    for key in ("name", "repository", "baseline"):
        require(nonempty(spec["project"].get(key)), f"project.{key} is required")
    docs = spec.get("documents")
    require(isinstance(docs, list) and docs, "documents must be a nonempty array")
    paths = set()
    for doc in docs:
        require(isinstance(doc, dict), "document must be an object")
        name = doc.get("path")
        inside(root, name)
        require(name not in paths, f"duplicate document: {name}")
        paths.add(name)
        require(doc.get("role") in {"normative", "context", "evidence", "excluded"}, f"invalid document role: {name}")
        require(isinstance(doc.get("sha256"), str) and re.fullmatch(r"[a-f0-9]{64}", doc["sha256"]), f"invalid document hash: {name}")
        require(doc.get("review") in {"pending", "reviewed"}, f"invalid review status: {name}")
        require(nonempty(doc.get("summary")), f"document summary/review reason required: {name}")
        if doc["role"] == "excluded":
            require(nonempty(doc.get("exclusion_reason")), f"explicit exclusion reason required: {name}")
    reqs = spec.get("requirements")
    req_ids = unique_ids(reqs, "requirement")
    check_ids = unique_ids(spec.get("checks"), "check")
    require(req_ids, "empty requirement set cannot verify a design")
    for req in reqs:
        for key in ("title", "statement", "rationale", "scope"):
            require(nonempty(req.get(key)), f"{req['id']}.{key} is required")
        require(req.get("decision") in {"accepted", "proposed", "unresolved", "historical"}, f"invalid decision: {req['id']}")
        require(isinstance(req.get("checks"), list) and req["checks"], f"{req['id']} needs a check (manual is allowed)")
        require(set(req["checks"]) <= check_ids, f"unknown check in {req['id']}")
        require(isinstance(req.get("citations"), list) and req["citations"], f"{req['id']} needs citations")
        for cite in req["citations"]:
            require(isinstance(cite, dict) and cite.get("path") in paths, f"unknown citation in {req['id']}")
            start, end = cite.get("start"), cite.get("end")
            require(type(start) is int and type(end) is int and 1 <= start <= end, f"invalid citation range: {req['id']}")
            require(isinstance(cite.get("excerpt_sha256"), str) and re.fullmatch(r"[a-f0-9]{64}", cite["excerpt_sha256"]), f"citation hash required: {req['id']}")
    for check in spec["checks"]:
        require(check.get("kind") in {"command", "manual"}, f"invalid check kind: {check['id']}")
        require(check.get("tier") in {"static", "integration", "live", "manual"}, f"invalid tier: {check['id']}")
        for key in ("proves", "limitations"):
            require(nonempty(check.get(key)), f"{check['id']}.{key} is required")
        if check["kind"] == "manual":
            require(nonempty(check.get("instructions")), f"manual instructions required: {check['id']}")
        else:
            argv = check.get("argv")
            require(isinstance(argv, list) and argv and all(nonempty(a) for a in argv), f"argv required: {check['id']}")
            inside(root, check.get("cwd", "."))
            timeout = check.get("timeout_seconds")
            require(type(timeout) is int and 1 <= timeout <= 3600, f"timeout must be 1..3600: {check['id']}")
            require(check.get("protocol") in {"exit", "node-tap", "python-unittest"}, f"explicit assertion protocol required: {check['id']}")
            env = check.get("env", {})
            require(isinstance(env, dict) and all(isinstance(k, str) and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", k) and isinstance(v, str) and "\0" not in v for k, v in env.items()), f"invalid environment overrides: {check['id']}")
    conflicts = spec.get("conflicts", [])
    unique_ids(conflicts, "conflict")
    for conflict in conflicts:
        require(conflict.get("status") in {"open", "resolved"}, f"invalid conflict status: {conflict['id']}")
        require(nonempty(conflict.get("question")), f"conflict question required: {conflict['id']}")
        require(isinstance(conflict.get("requirements"), list) and conflict["requirements"] and set(conflict["requirements"]) <= req_ids, f"unknown conflict requirement: {conflict['id']}")
        if conflict["status"] == "resolved":
            require(nonempty(conflict.get("resolution")), f"record decision/evidence for resolution: {conflict['id']}")


def audit(spec, root):
    validate(spec, root)
    findings = []
    remote = git(root, "remote", "get-url", "origin").decode().strip()
    def canonical(url):
        return url.removesuffix(".git").removesuffix("/").replace("git@github.com:", "https://github.com/")
    if canonical(remote) != canonical(spec["project"]["repository"]):
        findings.append("target origin differs from recorded project.repository")
    recorded = {doc["path"] for doc in spec["documents"]}
    actual = set(document_paths(root))
    for name in sorted(actual - recorded):
        findings.append(f"unreviewed new document: {name}")
    for name in sorted(recorded - actual):
        findings.append(f"document deleted or no longer tracked: {name}")
    for doc in spec["documents"]:
        path = inside(root, doc["path"])
        if not path.is_file() or digest(path.read_bytes()) != doc["sha256"]:
            findings.append(f"document content changed: {doc['path']}")
        if doc["review"] != "reviewed":
            findings.append(f"document review pending: {doc['path']}")
    for req in spec["requirements"]:
        for cite in req["citations"]:
            path = inside(root, cite["path"])
            lines = path.read_bytes().decode("utf-8").splitlines(keepends=True) if path.is_file() else []
            excerpt = "".join(lines[cite["start"] - 1:cite["end"]]).encode()
            if cite["end"] > len(lines) or digest(excerpt) != cite["excerpt_sha256"]:
                findings.append(f"citation moved/changed: {req['id']} {cite['path']}:{cite['start']}")
    return findings


def stop_group(process):
    # A check must be finite. An exited parent may have left live children behind.
    def active():
        process.poll()
        listing = subprocess.run(["ps", "-axo", "pgid=,stat="], capture_output=True, text=True, check=True, timeout=2)
        for line in listing.stdout.splitlines():
            fields = line.split()
            if len(fields) >= 2 and fields[0] == str(process.pid) and not fields[1].startswith("Z"):
                return True
        return False

    for sig in (signal.SIGTERM, signal.SIGKILL):
        try:
            os.killpg(process.pid, sig)
        except ProcessLookupError:
            break
        deadline = time.monotonic() + 2
        while active() and time.monotonic() < deadline:
            time.sleep(0.02)
        if not active():
            break
    require(not active(), "owned process group still active after termination; scratch retained")
    process.wait(timeout=2)


def command_argv(check, root, out, bundle):
    argv = check["argv"]
    for key, value in {"{target}": str(root), "{evidence}": str(out), "{bundle}": str(bundle or root)}.items():
        argv = [arg.replace(key, value) for arg in argv]
    return argv


def bundle_inputs(argv, bundle):
    return {arg: digest(Path(arg).read_bytes()) if Path(arg).is_file() else "missing" for arg in argv if bundle is not None and Path(arg).is_absolute() and Path(arg).is_relative_to(bundle) and not Path(arg).is_dir()}


def execute_check(check, root, out, bundle=None):
    result = {"id": check["id"], "tier": check["tier"], "proves": check["proves"], "limitations": check["limitations"]}
    if check["kind"] == "manual":
        return {**result, "status": "unverified", "reason": check["instructions"]}
    log = out / (check["id"] + ".log")
    argv = command_argv(check, root, out, bundle)
    inputs_before = bundle_inputs(argv, bundle)
    started = time.monotonic()
    process = None
    # Some storage contracts correctly reject symlinked macOS /var or /tmp paths.
    temporary = tempfile.mkdtemp(prefix=check["id"] + "-scratch-", dir=out)
    cleanup_ok = True
    with log.open("wb") as stream:
        overrides = {"TMPDIR": str(Path(temporary).resolve()), **check.get("env", {})}
        result["environment_overrides"] = overrides
        try:
            process = subprocess.Popen(argv, cwd=inside(root, check.get("cwd", ".")), env={**os.environ, **overrides}, stdout=stream, stderr=subprocess.STDOUT, start_new_session=True)
            try:
                code = process.wait(timeout=check["timeout_seconds"])
                result.update(status="pass" if code == 0 else "fail", exit_code=code)
            except subprocess.TimeoutExpired:
                result.update(status="blocked", reason="timeout; owned process group terminated")
            finally:
                try:
                    stop_group(process)
                except (OSError, Invalid, subprocess.SubprocessError) as error:
                    cleanup_ok = False
                    result.update(status="fail" if result.get("status") == "fail" else "blocked", reason=f"cannot confirm owned-group cleanup: {error}")
        except OSError as error:
            result.update(status="blocked", reason=f"cannot launch command: {error}")
    if cleanup_ok:
        shutil.rmtree(temporary)
    result.update(argv=argv, duration_seconds=round(time.monotonic() - started, 3), log=log.name, log_sha256=digest(log.read_bytes()), cleanup="confirmed" if cleanup_ok else "unconfirmed", scratch_retained=None if cleanup_ok else temporary)
    result["bundle_inputs_before"] = inputs_before
    result["bundle_inputs_after"] = bundle_inputs(argv, bundle)
    if result["bundle_inputs_before"] != result["bundle_inputs_after"]:
        result.update(status="blocked", reason="verification helper changed during check")
    if result["status"] == "pass" and check["protocol"] == "node-tap":
        content = log.read_text(errors="replace")
        totals = {key: re.findall(r"^# " + key + r" (\d+)\s*$", content, re.M) for key in ("tests", "pass", "fail", "skipped", "cancelled", "todo")}
        if not all(len(values) == 1 for values in totals.values()) or int(totals["pass"][0]) == 0 or int(totals["fail"][0]) != 0 or int(totals["tests"][0]) != sum(int(totals[k][0]) for k in ("pass", "fail", "skipped", "cancelled", "todo")):
            result.update(status="blocked", reason="missing/empty/inconsistent Node TAP totals; no proof")
        elif int(totals["skipped"][0]) or int(totals["cancelled"][0]) or int(totals["todo"][0]):
            result.update(status="unverified", reason="suite contains skipped/cancelled/TODO cases")
        else:
            result["passed_tests"] = int(totals["pass"][0])
    if result["status"] == "pass" and check["protocol"] == "python-unittest":
        content = log.read_text(errors="replace")
        totals = re.findall(r"^Ran (\d+) tests? in .+$", content, re.M)
        summaries = re.findall(r"^OK(?: \([^\n]+\))?$", content, re.M)
        if len(totals) != 1 or int(totals[0]) == 0 or len(summaries) != 1:
            result.update(status="blocked", reason="missing/empty unittest summary; no proof")
        elif summaries[0] != "OK":
            result.update(status="unverified", reason="unittest contains skipped/expected-failure cases")
        else:
            result["passed_tests"] = int(totals[0])
    return result


def run(spec, root, out, execute, spec_hash, bundle=None):
    issues = audit(spec, root)
    require(not out.exists(), "evidence directory must be new; previous evidence is never overwritten")
    require(not out.is_relative_to(root), "evidence must be outside target checkout so verification cannot mutate the target inventory")
    out.mkdir(parents=True, mode=0o700)
    before = snapshot(root)
    def verification_inputs():
        return {"runner": digest(Path(__file__).read_bytes()), "helpers": {c["id"]: bundle_inputs(command_argv(c, root, out, bundle), bundle) for c in spec["checks"] if c["kind"] == "command"}}
    verification_before = verification_inputs()
    used = {key for req in spec["requirements"] if req["decision"] in {"accepted", "unresolved"} for key in req["checks"]}
    checks = []
    for check in spec["checks"]:
        if check["id"] not in used:
            continue
        if issues or not execute:
            checks.append({"id": check["id"], "status": "blocked", "reason": "stale source/spec" if issues else "plan only; --execute was not supplied"})
        else:
            checks.append(execute_check(check, root, out, bundle))
    after = snapshot(root)
    if before != after:
        issues.append("target changed during verification; review snapshot/diff before re-running")
    verification_after = verification_inputs()
    if verification_before != verification_after:
        issues.append("verification runner/helper changed during run; results invalidated")
    statuses = {c["id"]: c["status"] for c in checks}
    requirements = []
    for req in spec["requirements"]:
        conflicts = [c["id"] for c in spec.get("conflicts", []) if c["status"] == "open" and req["id"] in c["requirements"]]
        values = [statuses.get(key, "unverified") for key in req["checks"]]
        if req["decision"] in {"proposed", "historical"}:
            status = "not-enforced"
        elif "fail" in values:
            status = "fail"
        elif issues or conflicts or req["decision"] == "unresolved":
            status = "blocked"
        elif values and all(value == "pass" for value in values):
            status = "pass"
        else:
            status = "unverified"
        requirements.append({"id": req["id"], "title": req["title"], "scope": req["scope"], "status": status, "checks": req["checks"], "open_conflicts": conflicts})
    active = [r for r in requirements if r["status"] != "not-enforced"]
    overall = "fail" if any(r["status"] == "fail" for r in active) else "pass" if active and all(r["status"] == "pass" for r in active) and not issues else "incomplete"
    report = {"version": 1, "overall": overall, "project": spec["project"], "spec_sha256": spec_hash, "runner_sha256": verification_before["runner"], "verification_inputs_before": verification_before, "verification_inputs_after": verification_after, "executed": execute and any("argv" in c for c in checks), "before": before, "after": after, "drift": issues, "checks": checks, "requirements": requirements, "conflicts": spec.get("conflicts", [])}
    write_json(out / "report.json", report)
    lines = [f"# {spec['project']['name']}: {overall}", "", f"Target commit: `{before['commit']}`", f"Spec SHA256: `{spec_hash}`", "", "A pass applies only to each recorded scope. Synthetic checks do not establish production behavior.", "", "| Requirement | Status | Checks |", "| --- | --- | --- |"]
    lines += [f"| {r['id']} | {r['status']} | {', '.join(r['checks'])} |" for r in requirements]
    lines += ["", "## Drift", ""] + ([f"- {issue}" for issue in issues] or ["None detected."])
    lines += ["", "## Check evidence and limits", ""]
    for check in checks:
        lines += [f"- {check['id']}: {check['status']}; {check.get('log', 'no log')}; {check.get('reason', check.get('proves', ''))}", f"  Limits: {check.get('limitations', 'See contract.')}"]
    (out / "report.md").write_text("\n".join(lines) + "\n")
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    for name in ("init", "inventory", "audit", "run"):
        command = sub.add_parser(name)
        command.add_argument("--target", required=True, type=Path)
        if name != "inventory":
            command.add_argument("--spec", required=True, type=Path)
        if name == "init":
            command.add_argument("--name", required=True)
            command.add_argument("--repository", required=True)
        if name == "run":
            command.add_argument("--out", required=True, type=Path)
            command.add_argument("--execute", action="store_true", help="run the reviewed contract's argv in the target; commands may have side effects")
    args = parser.parse_args(argv)
    try:
        root = args.target.resolve()
        require(root.is_dir(), "target directory does not exist")
        if args.action == "inventory":
            print(json.dumps([{"path": p, "sha256": digest(inside(root, p).read_bytes())} for p in document_paths(root)], indent=2, ensure_ascii=False))
            return 0
        if args.action == "init":
            require(not args.spec.exists(), "refusing to overwrite existing spec")
            docs = [{"path": p, "sha256": digest(inside(root, p).read_bytes()), "role": "context", "review": "pending", "summary": "Review required; no design meaning inferred by inventory."} for p in document_paths(root)]
            write_json(args.spec, {"version": 1, "project": {"name": args.name, "repository": args.repository, "baseline": snapshot(root)["commit"]}, "documents": docs, "requirements": [], "checks": [], "conflicts": []})
            print("Draft created. Read and classify every document; empty requirements deliberately fail audit.")
            return 0
        data = args.spec.read_bytes()
        spec = json.loads(data)
        if args.action == "audit":
            issues = audit(spec, root)
            print(json.dumps({"status": "stale" if issues else "current", "findings": issues}, indent=2, ensure_ascii=False))
            return 2 if issues else 0
        report = run(spec, root, args.out.resolve(), args.execute, digest(data), args.spec.resolve().parent)
        print(json.dumps({"overall": report["overall"], "report": str(args.out.resolve() / "report.json")}, indent=2))
        return {"pass": 0, "fail": 1, "incomplete": 2}[report["overall"]]
    except (Invalid, OSError, ValueError, TypeError, KeyError) as error:
        print(f"hirastack: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
