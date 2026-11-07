import json
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from check_unsigned_rejection import check_unsigned_report


def good_report():
    return {
        "status": "BLOCKED",
        "mode": "EXTERNAL_EVIDENCE",
        "claim_boundary": "NO_CLAIM",
        "g2_eligible": False,
        "foreign_replay_verified": False,
        "human_review_verified": False,
        "oneR": False,
        "oneV": False,
        "oneA": False,
        "promotion": "BLOCKED",
        "findings": [
            "missing manifest: manifest.json",
            "missing result: foreign-replay-result.json",
            "missing envelope: evidence-envelope.json",
            "missing attestation: runner-attestation.json",
            "missing reviewers: reviewers.json",
        ],
    }


class UnsignedPolicyEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "policy-report.json"

    def save(self, value):
        self.path.write_text(json.dumps(value), encoding="utf-8")

    def test_expected_policy_rejection(self):
        self.save(good_report())
        self.assertTrue(check_unsigned_report(1, self.path))

    def test_missing_report_blocks(self):
        self.assertFalse(check_unsigned_report(1, self.path))

    def test_validator_import_crash_blocks(self):
        self.path.write_text("ModuleNotFoundError: cryptography")
        self.assertFalse(check_unsigned_report(1, self.path))

    def test_wrong_exit_codes_block(self):
        self.save(good_report())
        for code in (0, 2, 127):
            with self.subTest(code=code):
                self.assertFalse(check_unsigned_report(code, self.path))

    def test_promoted_status_blocks(self):
        self.save(dict(good_report(), promotion="APPROVED"))
        self.assertFalse(check_unsigned_report(1, self.path))

    def test_string_false_blocks(self):
        self.save(dict(good_report(), oneR="false"))
        self.assertFalse(check_unsigned_report(1, self.path))

    def test_missing_semantic_reason_blocks(self):
        bad = good_report()
        bad["findings"] = ["unexpected runtime error"]
        self.save(bad)
        self.assertFalse(check_unsigned_report(1, self.path))

    def test_duplicate_json_key_blocks(self):
        self.path.write_text('{"status":"BLOCKED","status":"BLOCKED"}')
        self.assertFalse(check_unsigned_report(1, self.path))

    def test_corrupt_json_blocks(self):
        self.path.write_text("{bad")
        self.assertFalse(check_unsigned_report(1, self.path))

    def test_wrong_mode_blocks(self):
        self.save(dict(good_report(), mode="DEMO_ONLY"))
        self.assertFalse(check_unsigned_report(1, self.path))


if __name__ == "__main__":
    unittest.main()
