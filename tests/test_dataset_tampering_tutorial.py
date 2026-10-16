import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
CLI = ROOT / "scripts" / "e3bundle.py"


class DatasetTamperingTutorialTests(unittest.TestCase):
    """Exercise the tutorial's signed baseline and its three independent mutations."""

    def run_cli(self, *args, expected_code=0):
        result = subprocess.run(
            [sys.executable, str(CLI), *map(str, args)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(
            result.returncode,
            expected_code,
            msg=f"command: {args}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )
        self.assertEqual(result.stderr, "")
        return result.stdout

    def verify_args(self, bundle, trusted_keys):
        return (
            "verify",
            bundle,
            "--min-signatures",
            "2",
            "--trusted-keys",
            trusted_keys,
            "--strict",
            "--format",
            "text",
        )

    def test_signed_dataset_and_three_tampering_scenarios(self):
        with tempfile.TemporaryDirectory(prefix="e3bundle-tutorial-") as tmp:
            workspace = Path(tmp)
            bundle = workspace / "dataset-bundle"
            data = bundle / "data"
            data.mkdir(parents=True)
            (data / "readings.csv").write_text(
                "timestamp,temperature_c,plot\n"
                "2026-10-15T08:00:00Z,21.4,GH-01\n"
                "2026-10-15T09:00:00Z,21.7,GH-01\n",
                encoding="utf-8",
            )
            (bundle / "report.md").write_text(
                "Synthetic tutorial data only; not field evidence.\n",
                encoding="utf-8",
            )

            keys_dir = workspace / "keys"
            keys_dir.mkdir()
            operator_key = keys_dir / "operator.key"
            reviewer_key = keys_dir / "reviewer.key"
            operator_public = keys_dir / "operator.pub.json"
            reviewer_public = keys_dir / "reviewer.pub.json"

            self.run_cli(
                "keygen",
                "--private-key",
                operator_key,
                "--signer-id",
                "operator",
            )
            self.run_cli(
                "keygen",
                "--private-key",
                reviewer_key,
                "--signer-id",
                "reviewer",
            )

            trusted_keys = workspace / "trusted-keys.json"
            trusted = {
                "operator": json.loads(operator_public.read_text(encoding="utf-8"))[
                    "public_key_b64"
                ],
                "reviewer": json.loads(reviewer_public.read_text(encoding="utf-8"))[
                    "public_key_b64"
                ],
            }
            trusted_keys.write_text(
                json.dumps(trusted, indent=2) + "\n",
                encoding="utf-8",
            )

            self.run_cli("manifest", bundle, "--bundle-id", "tutorial-dataset-001")
            self.run_cli(
                "sign",
                bundle,
                "--private-key",
                operator_key,
                "--signer-id",
                "operator",
                "--role",
                "operator",
            )
            self.run_cli(
                "sign",
                bundle,
                "--private-key",
                reviewer_key,
                "--signer-id",
                "reviewer",
                "--role",
                "reviewer",
            )

            baseline = self.run_cli(*self.verify_args(bundle, trusted_keys))
            self.assertIn(
                "VERIFIED  tutorial-dataset-001  files 2/2  signatures 2 trusted / 2 valid",
                baseline,
            )

            scenario_paths = {}
            for name in ("scenario-edit", "scenario-add", "scenario-delete"):
                destination = workspace / name
                shutil.copytree(bundle, destination)
                scenario_paths[name] = destination

            edit_csv = scenario_paths["scenario-edit"] / "data" / "readings.csv"
            contents = edit_csv.read_text(encoding="utf-8")
            self.assertEqual(contents.count("21.4"), 1)
            edit_csv.write_text(contents.replace("21.4", "21.9"), encoding="utf-8")
            edited = self.run_cli(
                *self.verify_args(scenario_paths["scenario-edit"], trusted_keys),
                expected_code=1,
            )
            self.assertIn("hash mismatch: data/readings.csv", edited)
            self.assertIn("FAILED", edited)

            extra = scenario_paths["scenario-add"] / "data" / "extra.txt"
            extra.write_text("Added after signing.\n", encoding="utf-8")
            added = self.run_cli(
                *self.verify_args(scenario_paths["scenario-add"], trusted_keys),
                expected_code=1,
            )
            self.assertIn("undeclared file: data/extra.txt", added)
            self.assertIn("FAILED", added)

            (scenario_paths["scenario-delete"] / "report.md").unlink()
            deleted = self.run_cli(
                *self.verify_args(scenario_paths["scenario-delete"], trusted_keys),
                expected_code=1,
            )
            self.assertIn("missing file: report.md", deleted)
            self.assertIn("FAILED", deleted)


    def test_bilingual_tutorials_are_linked_and_cover_all_mutations(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        contributing = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
        english = (ROOT / "docs" / "tutorial-dataset-tampering.md").read_text(encoding="utf-8")
        spanish = (ROOT / "docs" / "tutorial-dataset-tampering.es.md").read_text(encoding="utf-8")

        for path in (
            "docs/tutorial-dataset-tampering.md",
            "docs/tutorial-dataset-tampering.es.md",
        ):
            self.assertIn(path, readme)
            self.assertIn(path, contributing)

        for tutorial in (english, spanish):
            self.assertIn("scenario-edit", tutorial)
            self.assertIn("scenario-add", tutorial)
            self.assertIn("scenario-delete", tutorial)
            self.assertIn("data/readings.csv", tutorial)
            self.assertTrue("exit code" in tutorial.lower() or "código de salida" in tutorial.lower())
            self.assertIn("trusted-keys.json", tutorial)

        self.assertIn("undeclared file: data/extra.txt", english)
        self.assertIn("undeclared file: data/extra.txt", spanish)
        self.assertIn("missing file: report.md", english)
        self.assertIn("missing file: report.md", spanish)


if __name__ == "__main__":
    unittest.main()
