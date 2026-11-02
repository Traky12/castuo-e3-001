"""E3 actual CLI test of an offline, synthetic Agro Edge contract bridge."""
import json
from pathlib import Path
import subprocess
import sys

import pytest

from scripts.demo_ecosystem_bridge import Refused, build, load_fixture


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "examples" / "ecosystem" / "synthetic-edge.jsonl"
CLI = ROOT / "scripts" / "e3bundle.py"


def verify(bundle, *args):
    return subprocess.run(
        [sys.executable, str(CLI), "verify", str(bundle), *args,
         "--format", "json"],
        text=True, capture_output=True, check=False,
    )


def test_real_cli_reports_integrity_only(tmp_path):
    bundle = tmp_path / "bundle"
    result = build(FIXTURE, bundle)
    assert result["status"] == "CREATED_UNSIGNED_SYNTHETIC"
    assert result["event_count"] == 3
    manifest = json.loads((bundle / "manifest.json").read_text())
    assert manifest["format"] == "e3.bundle.v1"
    assert len(manifest["files"]) == 2
    report = verify(bundle)
    assert report.returncode == 0, report.stderr
    assert json.loads(report.stdout)["status"] == "VERIFIED_INTEGRITY_ONLY"
    evidence = json.loads((bundle / "data" / "evidence-object.json").read_text())
    assert evidence["scope"] == "SYNTHETIC_LOCAL_ONLY"
    assert evidence["review_status"] == "PENDING"
    assert evidence["assurance"] == {"oneD": False, "oneV": False, "oneR": False, "oneA": False}
    assert not (bundle / "signatures.json").exists()


def test_real_cli_detects_tampering(tmp_path):
    bundle = tmp_path / "bundle"
    build(FIXTURE, bundle)
    file = bundle / "data" / "edge-events.jsonl"
    file.write_bytes(file.read_bytes().replace(b"21.4", b"99.9"))
    result = verify(bundle)
    assert result.returncode == 1
    assert json.loads(result.stdout)["status"] == "FAILED"


def test_strict_policy_never_approves_unsigned_bundle(tmp_path):
    bundle = tmp_path / "bundle"
    build(FIXTURE, bundle)
    trusted = ROOT / "examples" / "bundles" / "trusted-keys.json"
    result = verify(bundle, "--min-signatures", "2",
                    "--trusted-keys", str(trusted), "--strict")
    assert result.returncode != 0
    assert json.loads(result.stdout)["status"] != "VERIFIED"


@pytest.mark.parametrize("overrides", [
    {"source_system": "LIVE_CUSTOMER"},
    {"ingestion_mode": "WRITE"},
    {"review_status": "APPROVED"},
    {"qms_reference": "CUSTOMER_QMS"},
    {"secret_token": "SHOULD_NOT_BE_HERE"},
    {"value": True},
    {"value": float("inf")},
    {"source_event_id": "real-person-record"},
    {"event_type": "ACTUATE"},
    {"metric": "humidity"},
])
def test_unsafe_inputs_fail_closed(tmp_path, overrides):
    event = json.loads(FIXTURE.read_text().splitlines()[0])
    event.update(overrides)
    file = tmp_path / "input.jsonl"
    file.write_text(json.dumps(event, allow_nan=True) + "\n")
    with pytest.raises(Refused):
        load_fixture(file)


def test_duplicate_events_and_json_keys_fail_closed(tmp_path):
    original = FIXTURE.read_text().splitlines()[0]
    file = tmp_path / "input.jsonl"
    file.write_text(original + "\n" + original + "\n")
    with pytest.raises(Refused):
        load_fixture(file)
    file.write_text(original.replace('"value":21.4', '"value":21.4,"value":22.1') + "\n")
    with pytest.raises(Refused):
        load_fixture(file)


def test_symlinks_and_missing_inputs_fail_closed(tmp_path):
    with pytest.raises(Refused):
        load_fixture(tmp_path / "not-found.jsonl")
    link = tmp_path / "link"
    link.symlink_to(FIXTURE)
    with pytest.raises(Refused):
        load_fixture(link)


def test_output_never_overwritten(tmp_path):
    bundle = tmp_path / "bundle"
    build(FIXTURE, bundle)
    with pytest.raises(Refused):
        build(FIXTURE, bundle)


def test_demo_shows_no_field_or_g2_claims():
    html = (ROOT / "docs" / "demo" / "index.html").read_text()
    section = html.split('id="ecosystem-security"', 1)[1].split("</section>", 1)[0]
    for word in (
        "Agro Edge", "EvidenceObject", "e3bundle", "sintéticos",
        "no es una integración operativa", "revisión humana", "G1/G2",
    ):
        assert word in section
