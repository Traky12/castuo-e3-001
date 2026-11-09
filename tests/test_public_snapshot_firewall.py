import base64
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
import validate_public_snapshot_firewall


class PublicSnapshotFirewallTests(unittest.TestCase):
    def snapshot(self):
        self.publisher_key_id = "CASTUO-E3-SNAPSHOT-SIGNER-1"
        self.publisher_private_key = Ed25519PrivateKey.generate()
        raw_public = self.publisher_private_key.public_key().public_bytes(
            serialization.Encoding.Raw,
            serialization.PublicFormat.Raw,
        )
        public_key_b64 = base64.b64encode(raw_public).decode("ascii")
        self.trust_store = {
            "format": "castuo.e3-001.trust-store.v1",
            "keys": [{
                "key_id": "unit-test-publisher-key-1",
                "subject_id": self.publisher_key_id,
                "role": "publisher",
                "status": "trusted",
                "public_key_b64": public_key_b64,
                "approved_by": "independent-unit-test",
                "approval_ref": "test-fixture-only",
            }],
        }
        value = {
            "snapshot_id": "CASTUO-E3-TEST",
            "promotion": "BLOCKED",
            "authority_verified": False,
            "assurance": {"oneA": False},
        }
        payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
        value["public_verification"] = {
            "algorithm": "Ed25519",
            "key_id": self.publisher_key_id,
            "public_key_b64": public_key_b64,
            "signed_payload_sha256": "sha256:" + hashlib.sha256(payload).hexdigest(),
            "signature_b64": base64.b64encode(self.publisher_private_key.sign(payload)).decode("ascii"),
        }
        return value

    def run_gate(self, value, trust_store=None):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            snapshot_path = root / "status-snapshot.json"
            trust_path = root / "trust-store.json"
            snapshot_path.write_text(json.dumps(value), encoding="utf-8")
            store = self.trust_store if trust_store is None else trust_store
            trust_path.write_text(json.dumps(store), encoding="utf-8")
            with patch.object(sys, "argv", [
                "validate_public_snapshot_firewall.py",
                str(snapshot_path),
                "--trusted-key-store",
                str(trust_path),
            ]):
                return validate_public_snapshot_firewall.main()

    def test_secure_signed_and_trusted_snapshot_passes(self):
        self.assertEqual(self.run_gate(self.snapshot()), 0)

    def test_one_a_true_is_blocked(self):
        value = self.snapshot()
        value["assurance"]["oneA"] = True
        self.assertEqual(self.run_gate(value), 1)

    def test_authorized_promotion_is_blocked(self):
        value = self.snapshot()
        value["promotion"] = "AUTHORIZED"
        self.assertEqual(self.run_gate(value), 1)

    def test_missing_signature_is_blocked(self):
        value = self.snapshot()
        value["public_verification"]["signature_b64"] = "not base64"
        self.assertEqual(self.run_gate(value), 1)

    def test_valid_self_signed_snapshot_is_blocked_without_pinned_publisher(self):
        value = self.snapshot()
        empty_store = {"format": "castuo.e3-001.trust-store.v1", "keys": []}
        self.assertEqual(self.run_gate(value, trust_store=empty_store), 1)

    def test_snapshot_signature_tampering_is_blocked(self):
        value = self.snapshot()
        value["public_verification"]["signature_b64"] = base64.b64encode(b"x" * 64).decode("ascii")
        self.assertEqual(self.run_gate(value), 1)

    def test_snapshot_canonical_payload_hash_is_checked(self):
        value = self.snapshot()
        value["public_verification"]["signed_payload_sha256"] = "sha256:" + "0" * 64
        self.assertEqual(self.run_gate(value), 1)

    def test_trusted_key_id_mismatch_is_blocked(self):
        value = self.snapshot()
        value["public_verification"]["key_id"] = "UNAPPROVED-PUBLISHER"
        self.assertEqual(self.run_gate(value), 1)


if __name__ == "__main__":
    unittest.main()
