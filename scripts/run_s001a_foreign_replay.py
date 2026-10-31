#!/usr/bin/env python3
"""Execute candidate S-001A replays against a locally frozen public runner.

No network is used by this harness, but network isolation of the subprocess
MUST be enforced separately by the independent operator. Output is explicitly
UNATTESTED and can never satisfy the signed external acceptance gate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from tempfile import TemporaryDirectory

SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA64 = re.compile(r"^[0-9a-f]{64}$")


def canonical(obj: object) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                      allow_nan=False).encode("utf-8")


def sha(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def run_candidate(*, fixture: Path, runner_script: Path, runner_script_sha256: str,
                  source_commit: str, runner_id: str, output: Path,
                  stress_repetitions: int = 3) -> dict:
    if not SHA40.fullmatch(source_commit) or not SHA64.fullmatch(runner_script_sha256):
        raise ValueError("source_commit or runner_script_sha256 format invalid")
    if not runner_id.strip() or runner_id.lower().startswith(("local-", "demo-", "github-actions-")):
        raise ValueError("runner_id must be an externally assigned non-demo identifier")
    if stress_repetitions < 2 or stress_repetitions > 10:
        raise ValueError("stress repetitions must be in 2..10")
    runner_script = runner_script.resolve(strict=True)
    fixture = fixture.resolve(strict=True)
    if hashlib.sha256(runner_script.read_bytes()).hexdigest() != runner_script_sha256:
        raise ValueError("runner script SHA-256 mismatch")
    commit = subprocess.run(
        ["git", "-C", str(runner_script.parent), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=False, timeout=10,
    )
    if commit.returncode != 0 or commit.stdout.strip() != source_commit:
        raise ValueError("frozen runner source HEAD does not match source_commit")
    dirty = subprocess.run(
        ["git", "-C", str(runner_script.parent), "status", "--porcelain", "--untracked-files=no"],
        capture_output=True, text=True, check=False, timeout=10,
    )
    if dirty.returncode != 0 or dirty.stdout.strip():
        raise ValueError("frozen runner has modified tracked files")
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    fixture_hash = sha(fixture.read_bytes())
    results: list[dict] = []
    with TemporaryDirectory(prefix="s001a-candidate-") as base:
        for i in range(stress_repetitions):
            target = Path(base) / f"replay-{i+1}"
            cmd = [sys.executable, "-B", str(runner_script),
                   "--profile", "controlled-stress",
                   "--fixture", str(fixture),
                   "--output", str(target),
                   "--iterations", "36", "--seed", "20260819"]
            proc = subprocess.run(cmd, capture_output=True, text=True,
                                  check=False, timeout=60)
            if proc.returncode:
                raise ValueError(f"replay {i+1} exit={proc.returncode}; operator must inspect local logs")
            result_path = target / "result.json"
            if not result_path.is_file():
                raise ValueError("runner did not produce result.json")
            result = json.loads(result_path.read_text(encoding="utf-8"))
            if (result.get("scenario_id") != "S-001A"
                or result.get("output_hash_scope") != "S001A_DETERMINISTIC_FUNCTIONAL_V1"
                or result.get("fixture_hash") != fixture_hash
                or result.get("promotion") != "BLOCKED"
                or result.get("assurance", {}).get("oneV") is not False
                or result.get("assurance", {}).get("oneA") is not False):
                raise ValueError("runner violated scope, fixture, hash version or claim firewall")
            expected = {key: val for key, val in result.items() if key != "output_hash"}
            expected["metrics"] = {
                key: val for key, val in expected["metrics"].items()
                if key not in ("latency_ms", "throughput")
            }
            if sha(canonical(expected)) != result.get("output_hash"):
                raise ValueError("functional hash recomputation failed")
            results.append({
                "iteration": i+1, "functional_hash": result["output_hash"],
                "events_hash": sha(canonical(result["events"])),
                "event_count": len(result["events"]),
            })
    equivalent = len({x["functional_hash"] for x in results}) == 1 and len({
        x["events_hash"] for x in results
    }) == 1
    report = {
        "schema": "e3.s001a.candidate-replay.v1",
        "status": "CANDIDATE_REPLAY_ONLY" if equivalent else "REPLAY_MISMATCH",
        "independence": "NOT_AUTHENTICATED",
        "source_commit": source_commit,
        "runner_script_sha256": "sha256:" + runner_script_sha256,
        "runner_id_unverified": runner_id,
        "fixture_hash": fixture_hash,
        "replays": results,
        "equivalent": equivalent,
        "network_isolation": "NOT_VERIFIED_BY_THIS_HARNESS",
        "signed_attestation": False,
        "reviewer_signatures": 0,
        "oneR": False,
        "oneV": False,
        "oneA": False,
        "promotion": "BLOCKED",
    }
    (output / "candidate-replay.json").write_bytes(canonical(report) + b"\n")
    return report


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--fixture", type=Path, required=True)
    p.add_argument("--runner-script", type=Path, required=True)
    p.add_argument("--runner-script-sha256", required=True)
    p.add_argument("--source-commit", required=True)
    p.add_argument("--runner-id", required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--stress-repetitions", type=int, default=3)
    a = p.parse_args()
    try:
        result = run_candidate(**vars(a))
    except (OSError, ValueError, subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
        print(f"CANDIDATE_REPLAY_BLOCKED: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"status": result["status"], "equivalent": result["equivalent"]}))
    return 0 if result["equivalent"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
