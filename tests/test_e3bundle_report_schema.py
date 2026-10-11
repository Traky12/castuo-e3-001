import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).parents[1]
CLI = ROOT / "scripts" / "e3bundle.py"
EXAMPLES = ROOT / "examples" / "bundles"


class ReportSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads((ROOT / "schemas" / "e3bundle-report.schema.json").read_text(encoding="utf-8"))
        cls.validator = Draft202012Validator(cls.schema)

    def report(self, bundle, *args, code=0):
        proc = subprocess.run(
            [sys.executable, str(CLI), "verify", str(bundle), *map(str, args)],
            capture_output=True, text=True,
        )
        self.assertEqual(proc.returncode, code, proc.stdout + proc.stderr)
        self.assertEqual(proc.stderr, "")
        report = json.loads(proc.stdout)
        self.validator.validate(report)
        return report

    def test_schema_is_valid_draft_2020_12(self):
        self.assertEqual(self.schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        Draft202012Validator.check_schema(self.schema)

    def test_example_bundles_and_all_success_statuses(self):
        for name, code, status in (("valid", 0, "VERIFIED"), ("tampered", 1, "FAILED")):
            with self.subTest(bundle=name):
                report = self.report(EXAMPLES / name, "--min-signatures", 2,
                                     "--trusted-keys", EXAMPLES / "trusted-keys.json", code=code)
                self.assertEqual(report["status"], status)
                self.assertEqual(report["signatures_trusted"], 2)
        for args, status in (((), "VERIFIED_INTEGRITY_ONLY"),
                             (("--min-signatures", 2), "VERIFIED_TRUST_NOT_CHECKED")):
            with self.subTest(status=status):
                report = self.report(EXAMPLES / "valid", *args)
                self.assertEqual(report["status"], status)
                self.assertIsNone(report["signatures_trusted"])

    def test_minimal_error_reports(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            cases = ((root / "missing", ()), (root, ()),
                     (EXAMPLES / "valid", ("--min-signatures", -1)),
                     (EXAMPLES / "valid", ("--trusted-keys", root / "missing.json")),
                     (EXAMPLES / "valid", ("--strict",)))
            for bundle, args in cases:
                with self.subTest(bundle=bundle, args=args):
                    report = self.report(bundle, *args, code=2)
                    self.assertEqual(set(report), {"status", "findings", "limitations"})
                    self.assertEqual(report["status"], "ERROR")
            (root / "manifest.json").write_text("{broken", encoding="utf-8")
            self.report(root, code=2)

    def test_bundle_id_preserves_unvalidated_manifest_values(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = {"format": "e3.bundle.v1", "files": []}
            for value in (None, "id", 42, False, [], {}):
                with self.subTest(value=value):
                    manifest["bundle_id"] = value
                    (root / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
                    self.assertEqual(self.report(root)["bundle_id"], value)
            del manifest["bundle_id"]
            (root / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            self.assertIsNone(self.report(root)["bundle_id"])

    def test_rejects_missing_fields_and_extra_properties(self):
        full = self.report(EXAMPLES / "valid")
        error = self.report(EXAMPLES / "valid", "--strict", code=2)
        for report in (full, error):
            for field in report:
                with self.subTest(status=report["status"], missing=field):
                    invalid = copy.deepcopy(report)
                    del invalid[field]
                    self.assertFalse(self.validator.is_valid(invalid))
            invalid = dict(report, unexpected=True)
            self.assertFalse(self.validator.is_valid(invalid))
        self.assertFalse(self.validator.is_valid(dict(error, files_verified=0)))
        self.assertFalse(self.validator.is_valid(dict(full, status="ERROR")))

    def test_rejects_incorrect_field_types_and_values(self):
        report = self.report(EXAMPLES / "valid", "--min-signatures", 2,
                             "--trusted-keys", EXAMPLES / "trusted-keys.json")
        invalid_values = {
            "status": ["OK", None, 0], "format": ["e3.bundle.v2", None],
            "manifest_hash": ["sha256:abc", "sha256:" + "A" * 64, report["manifest_hash"] + "\n"],
            "findings": ["error", [1], None], "limitations": [None, []],
            "trust_mode": ["trusted", None], "signatures_trusted": [None, -1, 1.5, True, "2"],
        }
        for field in ("files_declared", "files_verified", "signatures_present", "signatures_valid", "min_signatures"):
            invalid_values[field] = [-1, 1.5, True, "0", None]
        for field, values in invalid_values.items():
            for value in values:
                with self.subTest(field=field, value=value):
                    invalid = dict(report, **{field: value})
                    self.assertFalse(self.validator.is_valid(invalid))
        self.assertFalse(self.validator.is_valid(dict(report, trust_mode="none")))
        for invalid in (None, [], "report"):
            self.assertFalse(self.validator.is_valid(invalid))


if __name__ == "__main__":
    unittest.main()
