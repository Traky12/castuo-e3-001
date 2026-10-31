"""Tests of the S-001A candidate replay harness. No signatures are synthesized."""
from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "run_s001a_foreign_replay.py"
spec = importlib.util.spec_from_file_location("s001a_candidate", SCRIPT)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class CandidateReplayTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.fixture = root / "fixture.json"
        self.fixture.write_text('{"scenario_id":"S-001A","synthetic":true}\n')
        self.runner = root / "dummy_runner.py"
        self.runner.write_text("# synthetic candidate runner\n")
        self.runner_hash = hashlib.sha256(self.runner.read_bytes()).hexdigest()
        self.output = root / "out"
        self.sha = "a" * 40

    def args(self):
        return dict(
            fixture=self.fixture, runner_script=self.runner,
            runner_script_sha256=self.runner_hash, source_commit=self.sha,
            runner_id="EXTERNAL-OPERATOR-UNVERIFIED", output=self.output,
            stress_repetitions=2,
        )

    def test_rejects_wrong_sha_without_executing(self):
        kw = self.args()
        kw["runner_script_sha256"] = "f" * 64
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            module.run_candidate(**kw)

    def test_rejects_local_fake_identity(self):
        kw = self.args()
        kw["runner_id"] = "LOCAL-demo"
        with self.assertRaisesRegex(ValueError, "non-demo"):
            module.run_candidate(**kw)

    def test_rejects_invalid_source_commit(self):
        kw = self.args()
        kw["source_commit"] = "HEAD"
        with self.assertRaisesRegex(ValueError, "format invalid"):
            module.run_candidate(**kw)

    def test_rejects_missing_replay_source(self):
        kw = self.args()
        kw["runner_script"] = self.output / "missing.py"
        with self.assertRaises(FileNotFoundError):
            module.run_candidate(**kw)

    def test_rejects_bad_repetitions(self):
        kw = self.args()
        kw["stress_repetitions"] = 1
        with self.assertRaisesRegex(ValueError, "2..10"):
            module.run_candidate(**kw)

    def test_no_attestation_even_if_replay_equivalent(self):
        from subprocess import CompletedProcess
        def mocked_subprocess(cmd, **options):
            if cmd[0] == "git":
                if "rev-parse" in cmd:
                    return CompletedProcess(cmd, 0, stdout=self.sha + "\n")
                return CompletedProcess(cmd, 0, stdout="")
            target = Path(cmd[cmd.index("--output") + 1])
            target.mkdir(parents=True)
            fixture_digest = module.sha(self.fixture.read_bytes())
            obj = {
                "scenario_id":"S-001A",
                "output_hash_scope":"S001A_DETERMINISTIC_FUNCTIONAL_V1",
                "fixture_hash":fixture_digest,
                "promotion":"BLOCKED",
                "assurance":{"oneV":False, "oneA":False},
                "metrics":{"latency_ms":{"x":1}, "throughput":{"x":2}},
                "events":[{"event_id":"synthetic-1"}],
            }
            base = dict(obj)
            base["metrics"] = {}
            obj["output_hash"] = module.sha(module.canonical(base))
            (target / "result.json").write_text(__import__("json").dumps(obj))
            return CompletedProcess(cmd, 0, stdout="")
        with patch.object(module.subprocess, "run", side_effect=mocked_subprocess):
            result = module.run_candidate(**self.args())
        self.assertEqual(result["status"], "CANDIDATE_REPLAY_ONLY")
        self.assertEqual(result["network_isolation"], "NOT_VERIFIED_BY_THIS_HARNESS")
        self.assertFalse(result["signed_attestation"])
        self.assertEqual(result["reviewer_signatures"], 0)
        self.assertFalse(result["oneR"])
        self.assertEqual(result["promotion"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
