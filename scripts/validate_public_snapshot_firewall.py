#!/usr/bin/env python3
"""Fail-closed CI gate for the public E3 snapshot projection."""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from validate_external_evidence_bundle import (
    canonical,
    decode_canonical_public_key,
    load,
    load_trust_store,
    trusted_key_finding,
)


def blocked(findings: list[str]) -> int:
    print(json.dumps({"status": "BLOCKED", "findings": findings}, indent=2))
    return 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("snapshot", type=Path)
    parser.add_argument("--trusted-key-store", type=Path, required=True)
    args = parser.parse_args()
    findings: list[str] = []

    try:
        snapshot: Any = load(args.snapshot)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError):
        return blocked(["snapshot is unreadable or has duplicate JSON keys"])

    if not isinstance(snapshot, dict):
        return blocked(["snapshot root must be a JSON object"])

    assurance = snapshot.get("assurance")
    verification = snapshot.get("public_verification")
    if not isinstance(assurance, dict):
        findings.append("assurance must be an object")
        assurance = {}
    if not isinstance(verification, dict):
        findings.append("public_verification must be an object")
        verification = {}

    if snapshot.get("promotion") != "BLOCKED":
        findings.append("promotion must remain BLOCKED")
    if snapshot.get("authority_verified") is not False:
        findings.append("authority_verified must remain false")
    if assurance.get("oneA") is not False:
        findings.append("assurance.oneA must remain false")
    if verification.get("algorithm") != "Ed25519":
        findings.append("public Ed25519 verification is required")

    public_key_bytes: bytes | None = None
    signature_bytes: bytes | None = None
    public_key_text = verification.get("public_key_b64")
    signature_text = verification.get("signature_b64")
    if not isinstance(verification.get("key_id"), str) or not verification.get("key_id"):
        findings.append("public_verification.key_id is required")
    try:
        public_key_bytes = decode_canonical_public_key(public_key_text)
    except (ValueError, TypeError):
        findings.append("public_verification.public_key_b64 must be a canonical Ed25519 public key")
    try:
        if not isinstance(signature_text, str):
            raise ValueError("signature must be base64 text")
        signature_bytes = base64.b64decode(signature_text, validate=True)
        if base64.b64encode(signature_bytes).decode("ascii") != signature_text or len(signature_bytes) != 64:
            raise ValueError("signature must be canonical Base64 encoding of 64 bytes")
    except (ValueError, TypeError):
        findings.append("public_verification.signature_b64 must be a canonical Ed25519 signature")

    payload = {key: value for key, value in snapshot.items() if key != "public_verification"}
    payload_bytes = canonical(payload)
    expected_digest = "sha256:" + hashlib.sha256(payload_bytes).hexdigest()
    if verification.get("signed_payload_sha256") != expected_digest:
        findings.append("signed_payload_sha256 does not match the canonical unsigned snapshot")

    if public_key_bytes is not None and signature_bytes is not None:
        try:
            Ed25519PublicKey.from_public_bytes(public_key_bytes).verify(signature_bytes, payload_bytes)
        except (InvalidSignature, ValueError):
            findings.append("snapshot Ed25519 signature is invalid")

    try:
        trust_store = load_trust_store(args.trusted_key_store)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError):
        return blocked(findings + ["trusted publisher key store is missing, unreadable or invalid"])

    trust_issue = trusted_key_finding(
        trust_store,
        "publisher",
        verification.get("key_id"),
        public_key_text,
    )
    if trust_issue:
        findings.append("publisher trust check failed: " + trust_issue)

    if findings:
        return blocked(findings)
    print(json.dumps({
        "status": "PASS",
        "oneA": False,
        "promotion": "BLOCKED",
        "authority_verified": False,
        "publisher_key_id": verification["key_id"],
        "signature_verified": True,
        "publisher_trusted": True,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
