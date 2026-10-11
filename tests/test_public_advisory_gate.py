import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from check_public_advisory import validate_advisory  # noqa: E402


class PublicAdvisoryGateTests(unittest.TestCase):
    def setUp(self):
        self.advisory = {
            "ghsa_id": "GHSA-55pc-7v4h-jf7c",
            "published_at": "2026-10-11T00:00:00Z",
            "withdrawn_at": None,
            "vulnerabilities": [
                {
                    "package": {"ecosystem": "pip", "name": "e3bundle"},
                    "vulnerable_version_range": "< 0.1.3",
                    "first_patched_version": {"identifier": "0.1.3"},
                }
            ],
        }

    def test_passes_only_when_public_metadata_marks_013_as_fixed(self):
        passed, reason = validate_advisory(self.advisory)
        self.assertTrue(passed, reason)
        self.assertIn("0.1.3", reason)

    def test_fails_when_advisory_is_not_public(self):
        document = dict(self.advisory, published_at=None)
        passed, reason = validate_advisory(document)
        self.assertFalse(passed)
        self.assertIn("not publicly published", reason)

    def test_fails_when_advisory_is_withdrawn(self):
        document = dict(self.advisory, withdrawn_at="2026-10-11T01:00:00Z")
        passed, reason = validate_advisory(document)
        self.assertFalse(passed)
        self.assertIn("withdrawn", reason)

    def test_fails_for_wrong_advisory_identifier(self):
        document = dict(self.advisory, ghsa_id="GHSA-0000-0000-0000")
        passed, reason = validate_advisory(document)
        self.assertFalse(passed)
        self.assertIn("unexpected advisory ID", reason)

    def test_fails_when_fixed_version_is_missing_or_different(self):
        document = dict(self.advisory)
        document["vulnerabilities"] = [
            {
                "package": {"ecosystem": "pip", "name": "e3bundle"},
                "vulnerable_version_range": "< 0.1.3",
                "first_patched_version": {"identifier": "0.1.2"},
            }
        ]
        passed, reason = validate_advisory(document)
        self.assertFalse(passed)
        self.assertIn("does not list e3bundle 0.1.3", reason)

    def test_fails_when_package_or_ecosystem_does_not_match(self):
        document = dict(self.advisory)
        document["vulnerabilities"] = [
            {
                "package": {"ecosystem": "npm", "name": "e3bundle"},
                "first_patched_version": {"identifier": "0.1.3"},
            }
        ]
        passed, reason = validate_advisory(document)
        self.assertFalse(passed)
        self.assertIn("does not list e3bundle 0.1.3", reason)

    def test_supports_string_fixed_version_field(self):
        document = dict(self.advisory)
        document["vulnerabilities"] = [
            {
                "package": {"ecosystem": "pip", "name": "e3bundle"},
                "first_patched_version": "0.1.3",
            }
        ]
        passed, reason = validate_advisory(document)
        self.assertTrue(passed, reason)

    def test_malformed_document_fails_closed(self):
        for document in (None, [], {"ghsa_id": "GHSA-55pc-7v4h-jf7c", "published_at": "today"}):
            with self.subTest(document=document):
                passed, _ = validate_advisory(document)
                self.assertFalse(passed)

    def test_non_string_package_fields_fail_closed_without_raising(self):
        document = dict(self.advisory)
        document["vulnerabilities"] = [
            {
                "package": {"ecosystem": None, "name": ["e3bundle"]},
                "first_patched_version": {"identifier": "0.1.3"},
            }
        ]
        passed, reason = validate_advisory(document)
        self.assertFalse(passed)
        self.assertIn("does not list e3bundle 0.1.3", reason)

    def test_pages_publication_gate_uses_advisory_helper(self):
        workflow = (ROOT / ".github" / "workflows" / "pages.yml").read_text(encoding="utf-8")
        self.assertIn("https://api.github.com/advisories/GHSA-55pc-7v4h-jf7c", workflow)
        self.assertIn("python scripts/check_public_advisory.py /tmp/e3-advisory.json", workflow)
        self.assertIn("advisory_ready", workflow)
        self.assertIn("ready=$ready", workflow)


if __name__ == "__main__":
    unittest.main()
