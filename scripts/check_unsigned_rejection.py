#!/usr/bin/env python3
"""Assert semantic policy rejection of an unsigned candidate by E3.

Never interprets an import error, crash or absent report as a security PASS.
Does not independently verify signatures or attest human reviewers.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def _reject_duplicates(pairs):
    result = {}
    for name, value in pairs:
        if name in result:
            raise ValueError("duplicate JSON property")
        result[name] = value
    return result


def check_unsigned_report(exit_code: int, path: Path) -> bool:
    if type(exit_code) is not int or exit_code != 1 or not path.is_file():
        return False
    try:
        report = json.loads(path.read_text(encoding="utf-8"),
                            object_pairs_hook=_reject_duplicates)
    except (OSError, UnicodeError, ValueError):
        return False
    if not isinstance(report, dict):
        return False
    if (report.get("status") != "BLOCKED"
            or report.get("mode") != "EXTERNAL_EVIDENCE"
            or report.get("claim_boundary") != "NO_CLAIM"
            or report.get("promotion") != "BLOCKED"):
        return False
    for key in ("g2_eligible", "foreign_replay_verified",
                "human_review_verified", "oneR", "oneV", "oneA"):
        if report.get(key) is not False:
            return False
    findings = report.get("findings")
    if not isinstance(findings, list) or not all(
            isinstance(value, str) for value in findings):
        return False
    mandatory = ("manifest", "result", "envelope", "attestation", "reviewers")
    return all(any(finding.startswith("missing " + key + ":")
                   for finding in findings) for key in mandatory)


def main() -> int:
    if len(sys.argv) != 3:
        return 2
    try:
        code = int(sys.argv[2])
    except ValueError:
        return 2
    accepted = check_unsigned_report(code, Path(sys.argv[1]))
    print("UNSIGNED_POLICY_REJECTION_CONFIRMED" if accepted
          else "INVALID_NEGATIVE_EVIDENCE_BLOCKED")
    return 0 if accepted else 1


if __name__ == "__main__":
    raise SystemExit(main())
