#!/usr/bin/env python3
"""Three-public-repository synthetic candidate: Edge → Evidence → E3.

This script reads sources from immutable local checkout paths. It neither attests
an independent operator nor claims physical/production interoperability.
The host controls networking; this script does not prove network isolation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory

EDGE_SHA = "a0639d6a234807c4f323d6e4a7b786cda9fd51e2"
EVIDENCE_SHA = "8b23f4370bccdf8c7dcbd93d395b41b70d6ba1de"
EVIDENCE_RUNNER_SHA256 = "41077a6848ec1429e34cf20babcf5fb2b37ab2fbc4f675b20c840ab8f49ca360"
EDGE_EXPORT_SHA256 = "9a4fab8571346254269f984b620566a794465ddcd1ed40c273f428d1aec37177"
FIXED_TIME = "2026-10-31T12:00:00Z"
SCOPE = "EB-POC-001"


def assert_head(folder: Path, sha: str) -> None:
    result = subprocess.run(
        ["git", "-C", str(folder), "rev-parse", "HEAD"],
        check=False, capture_output=True, text=True, timeout=12,
    )
    if result.returncode or result.stdout.strip() != sha:
        raise ValueError("source checkout SHA does not match reviewed pinned commit")


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(edge: Path, evidence: Path, e3: Path) -> dict:
    edge, evidence, e3 = (p.resolve(strict=True) for p in (edge, evidence, e3))
    assert_head(edge, EDGE_SHA)
    assert_head(evidence, EVIDENCE_SHA)
    if file_sha256(edge / "evidence_bridge/bridge/export_pack.py") != EDGE_EXPORT_SHA256:
        raise ValueError("Edge export script SHA-256 mismatch")
    if file_sha256(evidence / "runners/s001a_runner.py") != EVIDENCE_RUNNER_SHA256:
        raise ValueError("Evidence runner SHA-256 mismatch")

    # This CI workspace contains public code only, with a fully synthetic event
    # collection. The same exported bytes become the Evidence replay fixture.
    sys.path.insert(0, str(edge))
    sys.path.insert(0, str(e3 / "scripts"))
    from evidence_bridge.bridge.provenance import apply_provenance
    from evidence_bridge.bridge.export_pack import export_pack
    from evidence_bridge.bridge.verify_pack import verify_pack
    from run_s001a_foreign_replay import run_candidate

    prev = None
    events = []
    for i in range(1, 4):
        event = apply_provenance({
            "event_id": f"synthetic-edge-{i}",
            "source_system": "SYNTHETIC_NO_FIELD_DEVICE",
            "source_event_id": f"synthetic-{i}",
            "operation_scope_id": SCOPE,
            "event_type": "TELEMETRY_READING",
            "metric": "temperature",
            "value": float(20 + i),
            "unit": "degC",
            "occurred_at": FIXED_TIME,
            "ingestion_mode": "READ_ONLY",
            "schema_version": "1.0.0",
        }, prev)
        events.append(event)
        prev = event["payload_hash"]

    with TemporaryDirectory(prefix="castuo-joint-candidate-") as temp:
        root = Path(temp)
        pack = root / "edge-pack"
        exported = export_pack(events, pack, source_commit=EDGE_SHA,
                               generated_at=FIXED_TIME, operation_scope_id=SCOPE)
        good = verify_pack(pack)
        if good["status"] != "VALID_LOCAL_INTEGRITY_ONLY" or good["events"] != 3:
            raise ValueError("Edge portable packet verification failed")

        # Negative controls: source event tampering must invalidate the same
        # source package before its bytes are consumed by Evidence.
        bad = root / "tampered-pack"
        shutil.copytree(pack, bad)
        data = bad / "events.jsonl"
        old = data.read_bytes()
        if b"21.0" not in old:
            raise ValueError("synthetic tamper target not present")
        data.write_bytes(old.replace(b"21.0", b"99.0", 1))
        if verify_pack(bad)["status"] != "INVALID":
            raise ValueError("tampered Edge pack unexpectedly accepted")

        # Evidence consumes the unmodified *actual Edge artifact*, not an
        # unrelated synthetic fixture constructed in the E3 repository.
        candidate = run_candidate(
            fixture=pack / "events.jsonl",
            runner_script=evidence / "runners/s001a_runner.py",
            runner_script_sha256=EVIDENCE_RUNNER_SHA256,
            source_commit=EVIDENCE_SHA,
            runner_id="CI-SYNTHETIC-UNATTESTED",
            output=root / "e3-candidate",
            stress_repetitions=3,
        )
        if candidate["status"] != "CANDIDATE_REPLAY_ONLY" or not candidate["equivalent"]:
            raise ValueError("Evidence → E3 functional replay mismatch")
        if candidate["fixture_hash"] != "sha256:" + file_sha256(pack / "events.jsonl"):
            raise ValueError("Evidence fixture hash does not bind to Edge export")
        if (candidate["promotion"] != "BLOCKED"
            or candidate["signed_attestation"] is not False
            or candidate["reviewer_signatures"] != 0
            or any(candidate[k] is not False for k in ("oneR", "oneV", "oneA"))):
            raise ValueError("claim firewall failed")

        return {
            "schema": "castuo.edge-evidence-e3.candidate.v1",
            "status": "SYNTHETIC_TRIPLE_REPO_CANDIDATE_ONLY",
            "edge_source_commit": EDGE_SHA,
            "evidence_source_commit": EVIDENCE_SHA,
            "edge_export_sha256": EDGE_EXPORT_SHA256,
            "evidence_runner_sha256": EVIDENCE_RUNNER_SHA256,
            "edge_manifest_hash": exported["manifest_hash"],
            "edge_event_count": good["events"],
            "tampered_pack_rejected": True,
            "shared_fixture_hash": candidate["fixture_hash"],
            "evidence_candidate_replays": 3,
            "equivalent": candidate["equivalent"],
            "independent_replay": "NOT_ATTESTED",
            "host_network_isolation": "NOT_ATTESTED",
            "reviewers": 0,
            "G1": "BLOCKED", "G2": "BLOCKED",
            "promotion": "BLOCKED",
        }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--edge", required=True, type=Path)
    p.add_argument("--evidence", required=True, type=Path)
    p.add_argument("--e3", required=True, type=Path)
    a = p.parse_args()
    try:
        result = run(a.edge, a.evidence, a.e3)
    except (OSError, ValueError, ImportError, subprocess.TimeoutExpired) as exc:
        print("TRIPLE_REPO_CANDIDATE_BLOCKED:", type(exc).__name__, str(exc), file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
