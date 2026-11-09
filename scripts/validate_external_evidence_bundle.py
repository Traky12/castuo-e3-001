#!/usr/bin/env python3
"""Validate an externally replayed and human-reviewed S-001A evidence bundle.

The validator is intentionally read-only. It verifies portable hashes, a signed
runner attestation and signed independent reviewers. It never writes oneV/oneA
into repository state and never authorizes production.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
MAX_JSON_BYTES = 5 * 1024 * 1024
MAX_FIXTURE_BYTES = 20 * 1024 * 1024
MAX_RELATIVE_PATH_LENGTH = 255
MAX_PATH_DEPTH = 16
TRUST_STORE_FORMAT = "castuo.e3-001.trust-store.v1"
MAX_REVIEWER_RECORDS = 100


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _reject_duplicate_json_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_reject_duplicate_json_keys)


def safe_bundle_file(package: Path, relative: Any, max_bytes: int) -> tuple[Path | None, str | None]:
    """Resolve one regular artifact without traversal, symlinks or unbounded reads."""
    if not isinstance(relative, str) or not relative:
        return None, "path must be a non-empty relative string"
    if len(relative) > MAX_RELATIVE_PATH_LENGTH:
        return None, f"path exceeds {MAX_RELATIVE_PATH_LENGTH} characters"
    if any(ord(ch) < 32 or ord(ch) == 127 for ch in relative):
        return None, "path contains a control character"
    if "\\" in relative or ":" in relative or relative.startswith("/"):
        return None, "path must not be absolute or contain backslashes/colons"
    parts = relative.split("/")
    if len(parts) > MAX_PATH_DEPTH:
        return None, f"path exceeds {MAX_PATH_DEPTH} levels"
    if any(part in {"", ".", ".."} for part in parts):
        return None, "path contains an empty, dot or parent segment"

    candidate = package
    for part in parts:
        candidate = candidate / part
        if candidate.is_symlink():
            return None, "path must not traverse a symbolic link"
    try:
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(package)
    except FileNotFoundError:
        return None, "file does not exist"
    except (OSError, ValueError):
        return None, "path escapes the evidence bundle"
    if not resolved.is_file():
        return None, "path is not a regular file"
    try:
        if resolved.stat().st_size > max_bytes:
            return None, f"file exceeds the {max_bytes}-byte safety limit"
    except OSError:
        return None, "file size could not be determined"
    return resolved, None


def decode_canonical_public_key(value: Any) -> bytes:
    if not isinstance(value, str):
        raise ValueError("public key must be Base64 text")
    raw = base64.b64decode(value, validate=True)
    if base64.b64encode(raw).decode("ascii") != value:
        raise ValueError("public key Base64 is not canonical")
    Ed25519PublicKey.from_public_bytes(raw)
    return raw


def verify_signature(record: dict[str, Any]) -> bool:
    try:
        public_key_text = record["public_key_b64"]
        signature_text = record["signature_b64"]
        public_key = decode_canonical_public_key(public_key_text)
        signature = base64.b64decode(signature_text, validate=True)
        if base64.b64encode(signature).decode("ascii") != signature_text:
            return False
        payload = {key: value for key, value in record.items() if key != "signature_b64"}
        Ed25519PublicKey.from_public_bytes(public_key).verify(signature, canonical(payload))
        return True
    except (KeyError, ValueError, TypeError, InvalidSignature):
        return False


def load_trust_store(path: Path) -> list[dict[str, Any]]:
    data = load(path)
    if not isinstance(data, dict) or data.get("format") != TRUST_STORE_FORMAT:
        raise ValueError(f"trust store format must be {TRUST_STORE_FORMAT}")
    entries = data.get("keys")
    if not isinstance(entries, list):
        raise ValueError("trust store keys must be an array")

    key_ids: set[str] = set()
    key_bytes_seen: set[bytes] = set()
    active_subjects: set[tuple[str, str]] = set()
    parsed: list[dict[str, Any]] = []
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise ValueError(f"trust store keys[{index}] must be an object")
        key_id = entry.get("key_id")
        subject_id = entry.get("subject_id")
        role = entry.get("role")
        status = entry.get("status")
        if not isinstance(key_id, str) or not key_id:
            raise ValueError(f"trust store keys[{index}].key_id is required")
        if key_id in key_ids:
            raise ValueError(f"duplicate trust-store key_id: {key_id}")
        key_ids.add(key_id)
        if not isinstance(subject_id, str) or not subject_id:
            raise ValueError(f"trust store keys[{index}].subject_id is required")
        if role not in {"runner", "reviewer", "publisher"}:
            raise ValueError(f"trust store keys[{index}].role must be runner, reviewer or publisher")
        if status not in {"trusted", "revoked"}:
            raise ValueError(f"trust store keys[{index}].status must be trusted or revoked")
        if not isinstance(entry.get("approved_by"), str) or not entry["approved_by"].strip():
            raise ValueError(f"trust store keys[{index}].approved_by is required")
        if not isinstance(entry.get("approval_ref"), str) or not entry["approval_ref"].strip():
            raise ValueError(f"trust store keys[{index}].approval_ref is required")
        if status == "revoked":
            if not isinstance(entry.get("revocation_ref"), str) or not entry["revocation_ref"].strip():
                raise ValueError(f"revoked trust-store key {key_id} requires revocation_ref")
            if not isinstance(entry.get("revocation_reason"), str) or not entry["revocation_reason"].strip():
                raise ValueError(f"revoked trust-store key {key_id} requires revocation_reason")
        public_key = decode_canonical_public_key(entry.get("public_key_b64"))
        if public_key in key_bytes_seen:
            raise ValueError("the same public key must not appear more than once in the trust store")
        key_bytes_seen.add(public_key)
        subject = (role, subject_id)
        if status == "trusted":
            if subject in active_subjects:
                raise ValueError(f"more than one active key for {role} subject {subject_id}")
            active_subjects.add(subject)
        parsed.append({**entry, "_public_key_bytes": public_key})
    return parsed


def trusted_key_finding(
    trust_store: list[dict[str, Any]], role: str, subject_id: Any, public_key_b64: Any
) -> str | None:
    if not isinstance(subject_id, str) or not subject_id:
        return f"{role} identity is missing; no trust decision can be made"
    try:
        actual_key = decode_canonical_public_key(public_key_b64)
    except (ValueError, TypeError):
        return f"{role} {subject_id} has an invalid or non-canonical public key"
    subject_records = [
        entry for entry in trust_store
        if entry["role"] == role and entry["subject_id"] == subject_id
    ]
    if not subject_records:
        return f"{role} {subject_id} is not enrolled in the trusted key store"
    for entry in subject_records:
        if entry["_public_key_bytes"] == actual_key:
            if entry["status"] == "revoked":
                return f"{role} {subject_id} used a revoked key ({entry['key_id']})"
            return None
    return f"{role} {subject_id} key does not match its active trusted key"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package", type=Path)
    parser.add_argument("--min-reviewers", type=int, default=2)
    parser.add_argument(
        "--trusted-key-store", type=Path, default=None,
        help="Version-controlled trust store for external runner/reviewer identities; demo bundles do not use it.",
    )
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    if not 1 <= args.min_reviewers <= 100:
        parser.error("--min-reviewers must be between 1 and 100")

    findings: list[str] = []
    package: Path | None = None
    if args.package.is_symlink():
        findings.append("evidence bundle root must not be a symbolic link")
    else:
        try:
            package = args.package.resolve(strict=True)
        except OSError:
            findings.append("evidence bundle directory does not exist")
        else:
            if not package.is_dir():
                findings.append("evidence bundle path is not a directory")
                package = None

    required_names = {
        "manifest": "manifest.json",
        "result": "foreign-replay-result.json",
        "envelope": "evidence-envelope.json",
        "attestation": "runner-attestation.json",
        "reviewers": "reviewers.json",
    }
    required: dict[str, Path] = {}
    if package is not None:
        for name, filename in required_names.items():
            path, issue = safe_bundle_file(package, filename, MAX_JSON_BYTES)
            if issue:
                if issue == "file does not exist" or issue == "path is not a regular file":
                    findings.append(f"missing {name}: {filename}")
                else:
                    findings.append(f"invalid {name} artifact {filename}: {issue}")
            elif path is not None:
                required[name] = path

    objects: dict[str, Any] = {}
    if not findings:
        try:
            for name, path in required.items():
                objects[name] = load(path)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            findings.append(f"unreadable evidence bundle: {exc}")

    manifest = objects.get("manifest", {})
    result = objects.get("result", {})
    envelope = objects.get("envelope", {})
    attestation = objects.get("attestation", {})
    reviewers = objects.get("reviewers", [])

    if not isinstance(manifest, dict):
        findings.append("manifest must be an object")
        manifest = {}
    if not isinstance(result, dict):
        findings.append("foreign replay result must be an object")
        result = {}
    if not isinstance(envelope, dict):
        findings.append("evidence envelope must be an object")
        envelope = {}

    if manifest.get("scenario_id") != "S-001A":
        findings.append("manifest scenario_id must be S-001A")
    if manifest.get("protocol_id") != "E3-001-S001A-FOREIGN-REPLAY":
        findings.append("manifest protocol_id must be E3-001-S001A-FOREIGN-REPLAY")
    if manifest.get("foreign_replay") is not True:
        findings.append("manifest foreign_replay must be true")
    if manifest.get("external_runner") is not True:
        findings.append("manifest external_runner must be true")
    if manifest.get("production_claim") is not False or manifest.get("commercial_claim") is not False:
        findings.append("manifest production and commercial claims must be false")
    source_commit = manifest.get("source_commit")
    if not isinstance(source_commit, str) or not COMMIT_RE.fullmatch(source_commit):
        findings.append("manifest source_commit must be a 40-character lowercase commit")
    if not manifest.get("rollback_ref"):
        findings.append("manifest rollback_ref is required")

    expected_result_hash = digest(required["result"]) if "result" in required else None
    expected_envelope_hash = digest(required["envelope"]) if "envelope" in required else None
    expected_fixture_hash = None
    if package is not None:
        fixture_name = manifest.get("fixture_path", "fixture.json")
        if isinstance(fixture_name, str) and fixture_name in required_names.values():
            findings.append("manifest fixture_path must not reuse a protocol artifact path")
        else:
            fixture_path, fixture_issue = safe_bundle_file(package, fixture_name, MAX_FIXTURE_BYTES)
            if fixture_issue:
                findings.append(f"manifest fixture_path is unsafe or unavailable: {fixture_issue}")
            elif fixture_path is not None:
                expected_fixture_hash = digest(fixture_path)

    for label, value in (("result_hash", expected_result_hash), ("fixture_hash", expected_fixture_hash)):
        declared = manifest.get(label)
        if not isinstance(declared, str) or not SHA256_RE.fullmatch(declared):
            findings.append(f"manifest {label} must be a lowercase SHA-256 value")
        elif value is not None and declared != value:
            findings.append(f"manifest {label} does not match the artifact")
        elif value is None and label == "fixture_hash":
            findings.append("fixture_hash could not be verified")

    runner_value = result.get("runner", {}) if isinstance(result, dict) else {}
    replay_value = result.get("replay", {}) if isinstance(result, dict) else {}
    runner = runner_value if isinstance(runner_value, dict) else {}
    replay = replay_value if isinstance(replay_value, dict) else {}
    if result.get("status") != "PASS_WITHIN_DECLARED_SCOPE":
        findings.append("foreign replay result must be PASS_WITHIN_DECLARED_SCOPE")
    if runner.get("source_commit") != source_commit:
        findings.append("runner source_commit does not match manifest")
    if not runner.get("runner_id") or str(runner["runner_id"]).startswith(("github-actions-candidate-", "LOCAL-", "local-")):
        findings.append("runner_id must identify an external runner, not local or candidate CI")
    if runner.get("network") != "DISABLED_BY_HARNESS":
        findings.append("runner network must be DISABLED_BY_HARNESS")
    if replay.get("equivalent_decision") is not True or replay.get("equivalent_evidence_semantics") is not True:
        findings.append("replay equivalence must be true")
    if replay.get("oneR_candidate") is not True or replay.get("oneV") is not False or replay.get("oneA") is not False:
        findings.append("replay claim firewall is invalid")
    if replay.get("promotion") != "BLOCKED":
        findings.append("replay promotion must remain BLOCKED")

    assurance_value = envelope.get("assurance", {})
    assurance = assurance_value if isinstance(assurance_value, dict) else {}
    if envelope.get("scenario_id") != "S-001A":
        findings.append("envelope scenario_id must be S-001A")
    if envelope.get("promotion", "BLOCKED") != "BLOCKED":
        findings.append("envelope promotion must remain BLOCKED")
    if envelope.get("claim_boundary") in {None, "", "PRODUCTION", "COMMERCIAL"}:
        findings.append("envelope claim_boundary must be explicit and non-production")
    if not isinstance(assurance, dict) or assurance.get("oneD") is not True or assurance.get("oneR") is not True or assurance.get("oneV") is not False or assurance.get("oneA") is not False:
        findings.append("envelope assurance must be oneD=true, oneR=true, oneV=false, oneA=false")
    if expected_envelope_hash and manifest.get("evidence_hash") != expected_envelope_hash:
        findings.append("manifest evidence_hash does not match evidence-envelope")

    if not isinstance(attestation, dict) or attestation.get("independent") is not True:
        findings.append("runner attestation must declare independent=true")
    else:
        if attestation.get("runner_id") != runner.get("runner_id"):
            findings.append("runner attestation runner_id does not match result")
        if attestation.get("source_commit") != source_commit:
            findings.append("runner attestation source_commit does not match manifest")
        if attestation.get("result_hash") != expected_result_hash:
            findings.append("runner attestation result_hash does not match result")
        if not verify_signature(attestation):
            findings.append("runner attestation Ed25519 signature is invalid")

    # The synthetic demo exercises validation logic but is never external
    # evidence. Detect several explicit demo markers so a passing synthetic
    # bundle cannot be promoted to VERIFIED_FOR_G2 by changing one field.
    demo_only = (
        envelope.get("claim_boundary") == "DEMO_ONLY"
        or str(runner.get("runner_id", "")).startswith("DEMO-")
        or (
            isinstance(attestation, dict)
            and str(attestation.get("attestation_id", "")).startswith("DEMO-")
        )
        or (
            isinstance(reviewers, list)
            and any(
                isinstance(reviewer, dict)
                and str(reviewer.get("reviewer_id", "")).startswith("DEMO-")
                for reviewer in reviewers
            )
        )
    )

    if not isinstance(reviewers, list):
        findings.append("reviewers.json must be an array")
        reviewers = []
    if len(reviewers) > MAX_REVIEWER_RECORDS:
        findings.append(f"reviewers.json exceeds {MAX_REVIEWER_RECORDS} records")
        reviewers = reviewers[:MAX_REVIEWER_RECORDS]
    identities: set[str] = set()
    reviewer_public_keys: set[bytes] = set()
    for index, reviewer in enumerate(reviewers):
        prefix = f"reviewers[{index}]"
        if not isinstance(reviewer, dict):
            findings.append(f"{prefix} must be an object")
            continue
        identity = reviewer.get("reviewer_id")
        if not isinstance(identity, str) or not identity:
            findings.append(f"{prefix}.reviewer_id is required")
        elif identity in identities:
            findings.append(f"duplicate reviewer identity: {identity}")
        else:
            identities.add(identity)
        if reviewer.get("independence") is not True:
            findings.append(f"{prefix}.independence must be true")
        if reviewer.get("decision") != "APPROVE":
            findings.append(f"{prefix}.decision must be APPROVE")
        if reviewer.get("source_commit") != source_commit:
            findings.append(f"{prefix}.source_commit does not match manifest")
        if reviewer.get("evidence_hash") != expected_envelope_hash:
            findings.append(f"{prefix}.evidence_hash does not match envelope")
        if reviewer.get("replay_result_hash") != expected_result_hash:
            findings.append(f"{prefix}.replay_result_hash does not match result")
        try:
            reviewer_key = decode_canonical_public_key(reviewer.get("public_key_b64"))
        except (ValueError, TypeError):
            reviewer_key = None
        if reviewer_key is not None:
            if reviewer_key in reviewer_public_keys:
                findings.append(f"{prefix}.public_key_b64 reuses another reviewer's key")
            else:
                reviewer_public_keys.add(reviewer_key)
        if not verify_signature(reviewer):
            findings.append(f"{prefix}.signature is invalid")
    if len(identities) < args.min_reviewers:
        findings.append(f"independent reviewer quorum not met: {len(identities)} < {args.min_reviewers}")

    if not demo_only:
        trust_store: list[dict[str, Any]] | None = None
        trust_store_issue: str | None = None
        if args.trusted_key_store is None:
            trust_store_issue = "external evidence requires --trusted-key-store; self-declared keys do not establish signer identity"
        else:
            try:
                trust_store = load_trust_store(args.trusted_key_store)
            except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
                trust_store_issue = f"trusted key store is missing or invalid: {exc}"
        if trust_store_issue:
            findings.append(trust_store_issue)
        elif trust_store is not None:
            if not isinstance(attestation, dict):
                findings.append("runner attestation is not an object; trusted identity cannot be checked")
            else:
                issue = trusted_key_finding(
                    trust_store, "runner", runner.get("runner_id"), attestation.get("public_key_b64")
                )
                if issue:
                    findings.append(issue)
            for index, reviewer in enumerate(reviewers):
                if not isinstance(reviewer, dict):
                    continue
                issue = trusted_key_finding(
                    trust_store, "reviewer", reviewer.get("reviewer_id"), reviewer.get("public_key_b64")
                )
                if issue:
                    findings.append(f"reviewers[{index}]: {issue}")

    verified_for_g2 = not findings and not demo_only
    status = (
        "DEMO_VALIDATED"
        if demo_only and not findings
        else "VERIFIED_FOR_G2"
        if verified_for_g2
        else "BLOCKED"
    )
    output = {
        "scenario_id": "S-001A",
        "mode": "DEMO_ONLY" if demo_only else "EXTERNAL_EVIDENCE",
        "g2_eligible": verified_for_g2,
        "status": status,
        "foreign_replay_verified": verified_for_g2,
        "human_review_verified": verified_for_g2,
        "oneR": verified_for_g2,
        "oneV": verified_for_g2,
        "oneA": False,
        "promotion": "BLOCKED",
        "claim_boundary": (
            "DEMO_ONLY"
            if demo_only and not findings
            else "EXTERNAL_REPLAY_AND_SIGNED_REVIEW_ONLY"
            if verified_for_g2
            else "NO_CLAIM"
        ),
        "findings": findings,
    }
    # Validation is read-only by default. An optional report may be written only
    # outside the evidence package so the act of validating cannot mutate it.
    output_safe = True
    if args.output is not None and package is not None:
        try:
            output_resolved = args.output.resolve(strict=False)
            output_resolved.relative_to(package)
        except ValueError:
            pass
        except OSError:
            findings.append("validation output path cannot be resolved safely")
            output_safe = False
        else:
            findings.append("validation output must be outside the evidence bundle")
            output_safe = False
            output["status"] = "BLOCKED"
            output["g2_eligible"] = False
            output["foreign_replay_verified"] = False
            output["human_review_verified"] = False
            output["oneR"] = False
            output["oneV"] = False
            output["claim_boundary"] = "NO_CLAIM"
            output["findings"] = findings
    if args.output is not None and output_safe:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
