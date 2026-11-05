import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from hirastack.cli import Invalid, audit, digest, document_paths, execute_check, run, validate


class HarnessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.root = self.base / "app"
        self.root.mkdir()
        self.git("init", "-q")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("config", "user.name", "Fixture")
        self.git("remote", "add", "origin", "https://github.com/example/app.git")
        (self.root / "DESIGN.md").write_text("# Purpose\nPersist before ACK.\n")
        self.git("add", ".")
        self.git("commit", "-qm", "fixture")
        self.check = {"id": "save", "kind": "command", "tier": "integration", "argv": [sys.executable, "-c", "print('assertions ran')"], "cwd": ".", "timeout_seconds": 5, "protocol": "exit", "proves": "Fixture check execution.", "limitations": "Synthetic fixture only."}
        self.spec = {"version": 1, "project": {"name": "Fixture", "repository": "https://github.com/example/app", "baseline": self.git("rev-parse", "HEAD").strip()}, "documents": [{"path": "DESIGN.md", "sha256": digest((self.root / "DESIGN.md").read_bytes()), "role": "normative", "review": "reviewed", "summary": "ACK follows commit."}], "requirements": [{"id": "R1", "title": "Durable receive", "statement": "Persist before ACK.", "rationale": "Avoid loss.", "scope": "Fixture only", "decision": "accepted", "citations": [{"path": "DESIGN.md", "start": 2, "end": 2, "excerpt_sha256": digest(b"Persist before ACK.\n")}], "checks": ["save"]}], "checks": [self.check], "conflicts": []}

    def git(self, *argv):
        return subprocess.check_output(["git", "-C", str(self.root), *argv], stderr=subprocess.DEVNULL).decode()

    def verify(self, execute=True):
        return run(self.spec, self.root, self.base / "evidence", execute, "spec-hash")

    def test_success_records_evidence_and_target_identity(self):
        report = self.verify()
        self.assertEqual(report["overall"], "pass")
        self.assertEqual(report["before"], report["after"])
        self.assertIn("assertions ran", (self.base / "evidence/save.log").read_text())
        self.assertEqual(json.loads((self.base / "evidence/report.json").read_text())["overall"], "pass")

    def test_manual_requirement_cannot_inherit_command_pass(self):
        self.spec["checks"].append({"id": "owner", "kind": "manual", "tier": "manual", "proves": "Real owner path.", "limitations": "Not automated.", "instructions": "Exercise owner denial."})
        self.spec["requirements"][0]["checks"].append("owner")
        self.assertEqual(self.verify()["overall"], "incomplete")

    def test_plan_never_executes(self):
        self.check["argv"] = [sys.executable, "-c", "open('unexpected', 'w').write('x')"]
        self.assertEqual(self.verify(False)["overall"], "incomplete")
        self.assertFalse((self.root / "unexpected").exists())

    def test_changed_document_blocks_before_command(self):
        (self.root / "DESIGN.md").write_text("Changed principle\n")
        self.check["argv"] = ["must-not-launch"]
        report = self.verify()
        self.assertEqual(report["overall"], "incomplete")
        self.assertFalse((self.base / "evidence/save.log").exists())
        self.assertTrue(any("citation" in f for f in report["drift"]))

    def test_untracked_new_document_is_not_silently_omitted(self):
        (self.root / "new.md").write_text("new design")
        self.assertTrue(any("unreviewed new document" in f for f in audit(self.spec, self.root)))

    def test_non_markdown_doc_asset_is_inventoried(self):
        (self.root / "docs").mkdir()
        (self.root / "docs/decisions.tsv").write_text("decision\taccepted\n")
        self.assertIn("docs/decisions.tsv", document_paths(self.root))

    def test_wrong_repository_cannot_pass(self):
        self.spec["project"]["repository"] = "https://github.com/elsewhere/app"
        self.assertEqual(self.verify()["overall"], "incomplete")

    def test_ssh_origin_is_equivalent_to_https(self):
        self.git("remote", "set-url", "origin", "git@github.com:example/app.git")
        self.assertEqual(audit(self.spec, self.root), [])

    def test_open_semantic_conflict_blocks_success(self):
        self.spec["conflicts"].append({"id": "C1", "status": "open", "question": "Which processing stage?", "requirements": ["R1"]})
        report = self.verify()
        self.assertEqual(report["checks"][0]["status"], "pass")
        self.assertEqual(report["requirements"][0]["status"], "blocked")
        self.assertEqual(report["overall"], "incomplete")

    def test_failed_assertion_is_failure(self):
        self.check["argv"] = [sys.executable, "-c", "raise AssertionError('ACK preceded commit')"]
        self.assertEqual(self.verify()["overall"], "fail")

    def test_missing_runtime_is_blocked(self):
        self.check["argv"] = ["hirastack-no-such-runtime"]
        self.assertEqual(self.verify()["checks"][0]["status"], "blocked")

    def test_tap_skip_is_not_a_pass(self):
        self.check.update(protocol="node-tap", argv=[sys.executable, "-c", "print('# tests 3\\n# pass 2\\n# fail 0\\n# skipped 1\\n# cancelled 0\\n# todo 0')"])
        self.assertEqual(self.verify()["checks"][0]["status"], "unverified")

    def test_empty_suite_is_not_a_pass(self):
        self.check.update(protocol="node-tap", argv=[sys.executable, "-c", "print('# tests 0\\n# pass 0\\n# fail 0\\n# skipped 0\\n# cancelled 0\\n# todo 0')"])
        self.assertEqual(self.verify()["checks"][0]["status"], "blocked")

    def test_valid_tap_records_count(self):
        self.check.update(protocol="node-tap", argv=[sys.executable, "-c", "print('# tests 3\\n# pass 3\\n# fail 0\\n# skipped 0\\n# cancelled 0\\n# todo 0')"])
        self.assertEqual(self.verify()["checks"][0]["passed_tests"], 3)

    def test_node_tap_exit_zero_without_totals_is_not_proof(self):
        self.check["protocol"] = "node-tap"
        self.assertEqual(self.verify()["overall"], "incomplete")

    def test_evidence_is_never_overwritten(self):
        self.verify()
        with self.assertRaises(Invalid):
            self.verify()
        self.assertTrue((self.base / "evidence/report.json").exists())

    def test_target_mutation_during_verification_invalidates_pass(self):
        self.check["argv"] = [sys.executable, "-c", "open('implementation.py','w').write('changed')"]
        self.assertEqual(self.verify()["overall"], "incomplete")

    def test_path_escape_and_symlink_escape_are_refused(self):
        self.spec["documents"][0]["path"] = "../outside.md"
        with self.assertRaises(Invalid):
            validate(self.spec, self.root)
        (self.base / "outside.md").write_text("outside")
        (self.root / "link.md").symlink_to(self.base / "outside.md")
        self.spec["documents"][0]["path"] = "link.md"
        with self.assertRaises(Invalid):
            validate(self.spec, self.root)

    def test_malformed_contracts_are_refused(self):
        variants = []
        for key, value in (("checks", ["unknown"]), ("citations", []), ("decision", "approved-by-code")):
            other = copy.deepcopy(self.spec)
            other["requirements"][0][key] = value
            variants.append(other)
        other = copy.deepcopy(self.spec)
        other["requirements"] = []
        variants.append(other)
        other = copy.deepcopy(self.spec)
        other["checks"].append(copy.deepcopy(other["checks"][0]))
        variants.append(other)
        for variant in variants:
            with self.subTest(variant=variant), self.assertRaises(Invalid):
                validate(variant, self.root)

    def test_timeout_terminates_owned_child_and_preserves_log(self):
        self.check.update(timeout_seconds=1, argv=[sys.executable, "-c", "import time; print('started', flush=True); time.sleep(30)"])
        report = self.verify()
        self.assertEqual(report["checks"][0]["status"], "blocked")
        self.assertIn("started", (self.base / "evidence/save.log").read_text())

    def test_unresolved_requirement_is_never_passed_by_green_checks(self):
        self.spec["requirements"][0]["decision"] = "unresolved"
        self.assertEqual(self.verify()["overall"], "incomplete")

    def test_todo_cannot_pass_even_when_other_tests_pass(self):
        self.check.update(protocol="node-tap", argv=[sys.executable, "-c", "print('# tests 3\\n# pass 2\\n# fail 0\\n# skipped 0\\n# cancelled 0\\n# todo 1')"])
        self.assertEqual(self.verify()["checks"][0]["status"], "unverified")

    def test_inconsistent_tap_totals_cannot_pass(self):
        self.check.update(protocol="node-tap", argv=[sys.executable, "-c", "print('# tests 4\\n# pass 3\\n# fail 0\\n# skipped 0\\n# cancelled 0\\n# todo 0')"])
        self.assertEqual(self.verify()["checks"][0]["status"], "blocked")

    def test_scratch_is_canonical_private_and_cleaned_but_logs_survive(self):
        self.check["argv"] = [sys.executable, "-c", "import os; from pathlib import Path; p=Path(os.environ['TMPDIR']); assert str(p)==str(p.resolve()); assert p.stat().st_mode & 0o077 == 0; print(p)"]
        report = self.verify()
        scratch = Path(report["checks"][0]["environment_overrides"]["TMPDIR"])
        self.assertFalse(scratch.exists())
        self.assertIn(str(scratch), (self.base / "evidence/save.log").read_text())

    def test_declared_environment_override_is_executed_and_recorded(self):
        self.check["env"] = {"HIRASTACK_FIXTURE": "explicit"}
        self.check["argv"] = [sys.executable, "-c", "import os; assert os.environ['HIRASTACK_FIXTURE']=='explicit'"]
        report = self.verify()
        self.assertEqual(report["overall"], "pass")
        self.assertEqual(report["checks"][0]["environment_overrides"]["HIRASTACK_FIXTURE"], "explicit")

    def test_cleanup_uncertainty_blocks_and_preserves_scratch(self):
        with patch("hirastack.cli.stop_group", side_effect=PermissionError("denied")):
            report = self.verify()
        check = report["checks"][0]
        self.assertEqual(check["status"], "blocked")
        self.assertEqual(check["cleanup"], "unconfirmed")
        self.assertTrue(Path(check["scratch_retained"]).is_dir())

    def test_helper_change_invalidates_execution_provenance(self):
        bundle = self.base / "bundle"
        bundle.mkdir()
        helper = bundle / "helper.py"
        helper.write_text("from pathlib import Path\nPath(__file__).write_text('# changed during run\\n')\n")
        self.check["argv"] = [sys.executable, "{bundle}/helper.py"]
        report = run(self.spec, self.root, self.base / "evidence", True, "spec-hash", bundle)
        self.assertEqual(report["overall"], "incomplete")
        self.assertNotEqual(report["verification_inputs_before"], report["verification_inputs_after"])

    def test_outputs_in_evidence_under_bundle_are_not_helpers(self):
        # Evidence placed under the contract directory: build outputs written there must not
        # look like a changed helper, while real helpers beside it are still pinned.
        bundle = self.base
        (bundle / "helper.py").write_text("import pathlib, sys; pathlib.Path(sys.argv[1]).mkdir(parents=True)\n")
        self.check["argv"] = [sys.executable, "{bundle}/helper.py", "{evidence}/build"]
        report = run(self.spec, self.root, self.base / "evidence", True, "spec-hash", bundle)
        self.assertEqual(report["checks"][0]["status"], "pass")
        self.assertEqual(list(report["checks"][0]["bundle_inputs_before"]), [str(bundle / "helper.py")])

    def test_citation_hash_uses_original_crlf_bytes(self):
        data = b"# Purpose\r\nPersist before ACK.\r\n"
        (self.root / "DESIGN.md").write_bytes(data)
        self.spec["documents"][0]["sha256"] = digest(data)
        self.spec["requirements"][0]["citations"][0]["excerpt_sha256"] = digest(b"Persist before ACK.\r\n")
        self.assertEqual(audit(self.spec, self.root), [])

    def test_exited_parent_does_not_leave_running_child(self):
        self.check["argv"] = [sys.executable, "-c", "import subprocess,sys; c=subprocess.Popen([sys.executable,'-c','import time; time.sleep(30)']); print(c.pid,flush=True)"]
        report = self.verify()
        self.assertEqual(report["checks"][0]["cleanup"], "confirmed")
        pid = (self.base / "evidence/save.log").read_text().strip()
        state = subprocess.run(["ps", "-p", pid, "-o", "stat="], capture_output=True, text=True).stdout.strip()
        self.assertTrue(not state or state.startswith("Z"), state)

    def test_generic_cli_create_audit_plan_execute_and_detect_drift(self):
        tool_root = Path(__file__).resolve().parents[1]
        spec_path = self.base / "contract.json"
        def cli(*args):
            return subprocess.run([sys.executable, "-m", "hirastack", *args], cwd=tool_root, capture_output=True, text=True)
        created = cli("init", "--target", str(self.root), "--name", "IndependentFixture", "--repository", "https://github.com/example/app", "--spec", str(spec_path))
        self.assertEqual(created.returncode, 0, created.stderr)
        self.assertEqual(cli("audit", "--target", str(self.root), "--spec", str(spec_path)).returncode, 2)
        # The author reads the design and supplies a reviewed contract; init does not infer it.
        spec_path.write_text(json.dumps(self.spec))
        self.assertEqual(cli("audit", "--target", str(self.root), "--spec", str(spec_path)).returncode, 0)
        plan = cli("run", "--target", str(self.root), "--spec", str(spec_path), "--out", str(self.base / "plan"))
        self.assertEqual(plan.returncode, 2)
        executed = cli("run", "--target", str(self.root), "--spec", str(spec_path), "--out", str(self.base / "executed"), "--execute")
        self.assertEqual(executed.returncode, 0, executed.stderr)
        self.assertEqual(json.loads((self.base / "executed/report.json").read_text())["overall"], "pass")
        (self.root / "DESIGN.md").write_text("Design changed\n")
        self.assertEqual(cli("audit", "--target", str(self.root), "--spec", str(spec_path)).returncode, 2)

    def test_python_unittest_nonempty_summary_is_recorded(self):
        self.check.update(protocol="python-unittest", argv=[sys.executable, "-c", "print('Ran 2 tests in 0.01s\\n\\nOK')"])
        self.assertEqual(self.verify()["checks"][0]["passed_tests"], 2)

    def test_python_unittest_empty_or_skipped_is_not_passed(self):
        for total, summary in ((0, "OK"), (2, "OK (skipped=1)"), (2, "OK (expected failures=1)")):
            self.check.update(protocol="python-unittest", argv=[sys.executable, "-c", f"print('Ran {total} tests in 0.01s\\n\\n{summary}')"])
            out = self.base / ("python-" + summary.replace(" ", "-").replace("=", "-") + str(total))
            report = run(self.spec, self.root, out, True, "spec-hash")
            self.assertNotEqual(report["checks"][0]["status"], "pass")


WRITE = "import pathlib, sys; p = pathlib.Path(sys.argv[1]); p.parent.mkdir(parents=True, exist_ok=True); p.write_text(sys.argv[2])"


def junit(*cases, suite_error=False):
    body = "".join(f'<testcase name="c{i}">{inner}</testcase>' for i, inner in enumerate(cases))
    error = '<error message="collection failed"/>' if suite_error else ""
    return f'<?xml version="1.0"?><testsuites><testsuite name="s" tests="{len(cases)}">{error}{body}</testsuite></testsuites>'


def jest(statuses, total=None, suite_status=None, success=None):
    failed = statuses.count("failed")
    data = {
        "numTotalTests": len(statuses) if total is None else total,
        "numFailedTests": failed,
        "success": (failed == 0) if success is None else success,
        "testResults": [{"status": suite_status or ("failed" if failed else "passed"), "assertionResults": [{"status": s} for s in statuses]}],
    }
    return json.dumps(data)


def go_events(*events):
    return "\n".join(json.dumps(e) for e in events)


class ProtocolTests(unittest.TestCase):
    setUp = HarnessTests.setUp
    git = HarnessTests.git
    verify = HarnessTests.verify

    def report(self, protocol, path, payload):
        self.spec["checks"][0].update(protocol=protocol, report="{evidence}/" + path, argv=[sys.executable, "-c", WRITE, "{evidence}/" + path, payload])
        return self.verify()["checks"][0]

    def stdout(self, protocol, text):
        self.spec["checks"][0].update(protocol=protocol, argv=[sys.executable, "-c", "import sys; print(sys.argv[1])", text])
        return self.verify()["checks"][0]

    # JUnit XML: Maven/Gradle, pytest --junitxml, PHPUnit --log-junit, Vitest/Jest junit reporters.
    def test_junit_counts_testcases(self):
        result = self.report("junit-xml", "junit.xml", junit("", ""))
        self.assertEqual((result["status"], result["passed_tests"]), ("pass", 2))

    def test_junit_failure_with_exit_zero_fails(self):
        self.assertEqual(self.report("junit-xml", "junit.xml", junit("", '<failure message="x"/>'))["status"], "fail")

    def test_junit_error_case_fails(self):
        self.assertEqual(self.report("junit-xml", "junit.xml", junit("", '<error message="x"/>'))["status"], "fail")

    def test_junit_suite_level_error_fails(self):
        self.assertEqual(self.report("junit-xml", "junit.xml", junit("", suite_error=True))["status"], "fail")

    def test_junit_skip_is_unverified(self):
        self.assertEqual(self.report("junit-xml", "junit.xml", junit("", "<skipped/>"))["status"], "unverified")

    def test_junit_without_testcases_is_blocked(self):
        self.assertEqual(self.report("junit-xml", "junit.xml", junit())["status"], "blocked")

    def test_junit_report_directory_is_summed(self):
        write_two = "import pathlib, sys; d = pathlib.Path(sys.argv[1]); d.mkdir(parents=True); [(d / f'TEST-{i}.xml').write_text(sys.argv[2]) for i in range(2)]"
        self.spec["checks"][0].update(protocol="junit-xml", report="{evidence}/reports", argv=[sys.executable, "-c", write_two, "{evidence}/reports", junit("", "")])
        self.assertEqual(self.verify()["checks"][0]["passed_tests"], 4)

    def test_missing_report_is_blocked(self):
        self.spec["checks"][0].update(protocol="junit-xml", report="{evidence}/junit.xml")
        self.assertEqual(self.verify()["checks"][0]["status"], "blocked")

    def test_malformed_report_is_blocked(self):
        self.assertEqual(self.report("junit-xml", "junit.xml", "<testsuite>")["status"], "blocked")

    def test_report_must_live_in_fresh_evidence(self):
        self.spec["checks"][0].update(protocol="junit-xml", report="reports/junit.xml")
        with self.assertRaises(Invalid):
            validate(self.spec, self.root)
        self.spec["checks"][0]["report"] = "{evidence}/../junit.xml"
        with self.assertRaises(Invalid):
            validate(self.spec, self.root)

    def test_report_requires_a_report_protocol(self):
        self.spec["checks"][0].update(protocol="exit", report="{evidence}/junit.xml")
        with self.assertRaises(Invalid):
            validate(self.spec, self.root)
        self.spec["checks"][0].update(protocol="junit-xml")
        del self.spec["checks"][0]["report"]
        with self.assertRaises(Invalid):
            validate(self.spec, self.root)

    # Jest --json --outputFile / Vitest --reporter=json --outputFile.
    def test_jest_counts_assertions(self):
        result = self.report("jest-json", "jest.json", jest(["passed", "passed", "passed"]))
        self.assertEqual((result["status"], result["passed_tests"]), ("pass", 3))

    def test_jest_failed_with_exit_zero_fails(self):
        self.assertEqual(self.report("jest-json", "jest.json", jest(["passed", "failed"]))["status"], "fail")

    def test_jest_pending_and_todo_are_unverified(self):
        self.assertEqual(self.report("jest-json", "jest.json", jest(["passed", "pending", "todo"]))["status"], "unverified")

    def test_jest_suite_that_failed_to_run_fails(self):
        self.assertEqual(self.report("jest-json", "jest.json", jest(["passed"], suite_status="failed", success=False))["status"], "fail")

    def test_jest_inconsistent_totals_are_blocked(self):
        self.assertEqual(self.report("jest-json", "jest.json", jest(["passed"], total=5))["status"], "blocked")

    def test_jest_empty_run_is_blocked(self):
        self.assertEqual(self.report("jest-json", "jest.json", jest([]))["status"], "blocked")

    # go test -json on stdout.
    def test_go_counts_test_events(self):
        result = self.stdout("go-test-json", go_events({"Action": "run", "Test": "TestA"}, {"Action": "pass", "Test": "TestA"}, {"Action": "pass", "Test": "TestB"}, {"Action": "pass", "Package": "p"}))
        self.assertEqual((result["status"], result["passed_tests"]), ("pass", 2))

    def test_go_failed_test_fails(self):
        self.assertEqual(self.stdout("go-test-json", go_events({"Action": "pass", "Test": "TestA"}, {"Action": "fail", "Test": "TestB"}))["status"], "fail")

    def test_go_package_failure_fails(self):
        self.assertEqual(self.stdout("go-test-json", go_events({"Action": "pass", "Test": "TestA"}, {"Action": "fail", "Package": "p"}))["status"], "fail")

    def test_go_skipped_test_is_unverified(self):
        self.assertEqual(self.stdout("go-test-json", go_events({"Action": "pass", "Test": "TestA"}, {"Action": "skip", "Test": "TestB"}))["status"], "unverified")

    def test_go_package_without_tests_is_unverified(self):
        self.assertEqual(self.stdout("go-test-json", go_events({"Action": "pass", "Test": "TestA"}, {"Action": "skip", "Package": "empty"}))["status"], "unverified")

    def test_go_without_json_events_is_blocked(self):
        self.assertEqual(self.stdout("go-test-json", "ok  \tp\t0.01s")["status"], "blocked")

    # cargo test (libtest summary per test binary and doctests).
    def test_cargo_sums_binaries(self):
        text = "test result: ok. 3 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.01s\ntest result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 2 filtered out; finished in 0.00s"
        result = self.stdout("cargo-test", text)
        self.assertEqual((result["status"], result["passed_tests"]), ("pass", 4))

    def test_cargo_ignored_is_unverified(self):
        self.assertEqual(self.stdout("cargo-test", "test result: ok. 2 passed; 0 failed; 1 ignored; 0 measured; 0 filtered out")["status"], "unverified")

    def test_cargo_failed_is_failure(self):
        self.assertEqual(self.stdout("cargo-test", "test result: FAILED. 2 passed; 1 failed; 0 ignored; 0 measured; 0 filtered out")["status"], "fail")

    def test_cargo_without_summary_is_blocked(self):
        self.assertEqual(self.stdout("cargo-test", "running 0 tests")["status"], "blocked")

    def test_cargo_zero_tests_is_blocked(self):
        self.assertEqual(self.stdout("cargo-test", "test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out")["status"], "blocked")


class RepositoryLayoutTests(unittest.TestCase):
    def test_projects_holds_only_the_self_contract(self):
        projects = Path(__file__).resolve().parent.parent / "projects"
        found = sorted(entry.name for entry in projects.iterdir())
        self.assertEqual(
            found,
            ["hirastack"],
            "target-specific contracts and documents belong in the target repository "
            "(or a user-selected verification repo), not in hirastack/projects/",
        )


if __name__ == "__main__":
    unittest.main()
