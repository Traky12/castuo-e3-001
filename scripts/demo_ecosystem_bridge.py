#!/usr/bin/env python3
"""Synthetic-only, offline Edge -> EvidenceObject -> E3 bundle adapter.

NOT a live Edge exporter, field proof, signer enrollment or independent replay.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import sys

FIELDS = frozenset(
    "event_id event_type source_system source_event_id operation_scope_id "
    "device_id device_id_status metric value unit occurred_at occurred_at_status "
    "received_at received_at_status sequence_number sequence_status "
    "source_config_version ingestion_mode schema_version qms_reference "
    "qms_reference_status review_status".split()
)
REQUIRED = frozenset(
    "event_id event_type source_system source_event_id operation_scope_id "
    "metric value unit occurred_at ingestion_mode schema_version "
    "review_status qms_reference".split()
)
EVENT_ID = re.compile(r"EVT-[A-Za-z0-9-]{1,48}\Z")
SOURCE_ID = re.compile(r"synthetic-[A-Za-z0-9-]{1,60}\Z")
TIME = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z\Z")


class Refused(ValueError):
    """Unsafe or unauthenticated-to-the-demo input."""


def no_duplicates(pairs):
    result = {}
    for name, value in pairs:
        if name in result:
            raise Refused("duplicate JSON field")
        result[name] = value
    return result


def hash_bytes(raw):
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("utf-8")


def load_fixture(source):
    if source.is_symlink() or not source.is_file():
        raise Refused("fixture must be a local regular file")
    raw = source.read_bytes()
    if not raw or len(raw) > 131072 or b"\x00" in raw:
        raise Refused("empty/oversized/binary input")
    try:
        lines = raw.decode("utf-8").splitlines()
    except UnicodeDecodeError as exc:
        raise Refused("input is not UTF-8") from exc
    if not 1 <= len(lines) <= 128:
        raise Refused("event count not allowed")
    seen = set()
    events = []
    for line in lines:
        try:
            event = json.loads(line, object_pairs_hook=no_duplicates,
                               parse_constant=lambda _: (_ for _ in ()).throw(Refused("nonfinite JSON")))
        except (ValueError, TypeError) as exc:
            raise Refused("invalid Edge JSON") from exc
        if not isinstance(event, dict) or not REQUIRED <= event.keys() or event.keys() - FIELDS:
            raise Refused("missing/unknown Edge field")
        if (event["source_system"] != "SYNTHETIC_CULTIVATION_SAAS"
                or event["operation_scope_id"] != "EB-POC-001"
                or event["ingestion_mode"] != "READ_ONLY"
                or event["event_type"] != "TELEMETRY_READING"
                or event["schema_version"] != "1.0.0"
                or event["review_status"] != "PENDING"
                or event["qms_reference"] is not None):
            raise Refused("source is not synthetic, pending or read-only")
        if not isinstance(event["event_id"], str) or not EVENT_ID.fullmatch(event["event_id"]):
            raise Refused("invalid event ID")
        if not isinstance(event["source_event_id"], str) or not SOURCE_ID.fullmatch(event["source_event_id"]):
            raise Refused("source event not marked synthetic")
        if event["event_id"] in seen:
            raise Refused("duplicate event")
        seen.add(event["event_id"])
        value = event["value"]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise Refused("nonfinite/invalid metric")
        if (event["metric"], event["unit"]) not in (("temperature", "degC"), ("humidity", "%")):
            raise Refused("metric and unit mismatch")
        if not isinstance(event["occurred_at"], str) or not TIME.fullmatch(event["occurred_at"]):
            raise Refused("invalid event timestamp")
        events.append(event)
    return events, raw


def build(source, output):
    events, raw = load_fixture(source)
    if output.exists() or output.is_symlink() or not output.parent.is_dir():
        raise Refused("output must be new under an existing directory")
    payload = b"".join(canonical(event) + b"\n" for event in events)
    source_hash = hash_bytes(raw)
    evidence = {
        "schema_version": "2.0.0",
        "evidence_id": "SYNTHETIC-EDGE-" + hashlib.sha256(payload).hexdigest()[:20],
        "capability_id": "CAP-EDGE-E3-DEMO",
        "contract_id": "EB-POC-001",
        "implementation_id": "synthetic-fixture-adapter-v1",
        "execution_id": "OFFLINE_DEMO_NOT_ATTESTED",
        "fixture_hash": source_hash,
        "input_hash": source_hash,
        "output_hash": hash_bytes(payload),
        "scope": "SYNTHETIC_LOCAL_ONLY",
        "review_status": "PENDING",
        "claim_boundary": "INTEGRITY_ONLY_NOT_FIELD_NOT_G2",
        "rollback_reference": "NOT_APPLICABLE",
        "assurance": {"oneD": False, "oneV": False, "oneR": False, "oneA": False},
    }
    output.mkdir(mode=0o700)
    (output / "data").mkdir(mode=0o700)
    (output / "data" / "edge-events.jsonl").write_bytes(payload)
    (output / "data" / "evidence-object.json").write_bytes(canonical(evidence) + b"\n")
    subprocess.run(
        [sys.executable, str(Path(__file__).with_name("e3bundle.py")),
         "manifest", str(output), "--bundle-id", evidence["evidence_id"]],
        check=True, stdout=subprocess.DEVNULL,
    )
    return {
        "status": "CREATED_UNSIGNED_SYNTHETIC",
        "bundle": str(output),
        "event_count": len(events),
        "fixture_sha256": source_hash,
        "independent_review": "PENDING",
        "field_validation": "NOT_TESTED",
        "g1_g2": "BLOCKED",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(build(args.fixture, args.out), sort_keys=True))
    except (Refused, OSError, subprocess.CalledProcessError) as exc:
        print("BLOCKED: " + str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
