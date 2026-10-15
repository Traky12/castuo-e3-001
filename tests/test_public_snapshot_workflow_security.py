from pathlib import Path
import unittest


ROOT = Path(__file__).parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "public-snapshot.yml"


class PublicSnapshotWorkflowSecurityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = WORKFLOW.read_text(encoding="utf-8")

    def test_dispatch_inputs_are_not_interpolated_into_shell_source(self):
        self.assertIn("INPUT_BUNDLE_PATH: ${{ inputs.bundle_path }}", self.workflow)
        self.assertIn("INPUT_SOURCE_COMMIT: ${{ inputs.source_commit }}", self.workflow)
        self.assertIn('python scripts/preflight_public_snapshot.py "$INPUT_BUNDLE_PATH"', self.workflow)
        self.assertNotIn('python scripts/preflight_public_snapshot.py "${{ inputs.bundle_path }}"', self.workflow)
        self.assertNotIn('--source-commit "${{ inputs.source_commit }}"', self.workflow)

    def test_publication_is_restricted_to_main(self):
        self.assertEqual(self.workflow.count("if: github.ref == 'refs/heads/main'"), 2)

    def test_signing_key_and_write_permission_are_isolated_to_publish_job(self):
        verify, publish = self.workflow.split("  publish:", 1)
        self.assertNotIn("secrets.CASTUO_SNAPSHOT_SIGNING_KEY_B64", verify)
        self.assertIn("permissions:\n      contents: read", verify)
        self.assertIn("permissions:\n      contents: write", publish)
        self.assertIn("environment:\n      name: public-snapshot", publish)
        self.assertIn("persist-credentials: false", verify)

    def test_external_validation_uses_the_governed_trust_store(self):
        self.assertIn("--trusted-key-store trust/e3-001-trust-store.json", self.workflow)

    def test_publication_transfers_only_validation_json_artifacts(self):
        self.assertIn("name: e3-001-snapshot-validation", self.workflow)
        self.assertIn("artifacts/external-evidence-validation.json", self.workflow)
        self.assertIn("artifacts/g2-decision.json", self.workflow)
        self.assertNotIn("upload-artifact", self.workflow.split("  publish:", 1)[1])


if __name__ == "__main__":
    unittest.main()
