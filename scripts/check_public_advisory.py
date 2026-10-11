#!/usr/bin/env python3
"""Fail-closed validation of published GitHub Advisory Database metadata.

This helper does not infer that a code fix is publicly acknowledged. It only
passes when the public advisory explicitly marks e3bundle 0.1.3 as the first
patched version. It is used by the GitHub Pages publication gate.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

EXPECTED_GHSA = "GHSA-55pc-7v4h-jf7c"
EXPECTED_PACKAGE = "e3bundle"
EXPECTED_ECOSYSTEM = "pip"
EXPECTED_FIXED_VERSION = "0.1.3"


def _version_identifier(value: Any) -> str | None:
    """Support the current object form and the documented string form."""
    if isinstance(value, dict):
        identifier = value.get("identifier")
        return identifier if isinstance(identifier, str) else None
    if isinstance(value, str):
        return value
    return None


def validate_advisory(document: Any) -> tuple[bool, str]:
    """Return whether public advisory metadata confirms the fixed version."""
    if not isinstance(document, dict):
        return False, "advisory response is not a JSON object"
    if document.get("ghsa_id") != EXPECTED_GHSA:
        return False, f"unexpected advisory ID; expected {EXPECTED_GHSA}"
    if not document.get("published_at"):
        return False, "advisory is not publicly published"
    if document.get("withdrawn_at"):
        return False, "advisory is withdrawn"

    vulnerabilities = document.get("vulnerabilities")
    if not isinstance(vulnerabilities, list):
        return False, "advisory has no valid vulnerabilities list"

    for vulnerability in vulnerabilities:
        if not isinstance(vulnerability, dict):
            continue
        package = vulnerability.get("package")
        if not isinstance(package, dict):
            continue
        ecosystem = package.get("ecosystem")
        package_name = package.get("name")
        if not isinstance(ecosystem, str) or not isinstance(package_name, str):
            continue
        if ecosystem.lower() != EXPECTED_ECOSYSTEM:
            continue
        if package_name.lower() != EXPECTED_PACKAGE:
            continue
        fixed = _version_identifier(vulnerability.get("first_patched_version"))
        if fixed == EXPECTED_FIXED_VERSION:
            return True, f"{EXPECTED_PACKAGE} {EXPECTED_FIXED_VERSION} is listed as the first patched version"

    return (
        False,
        f"public advisory does not list {EXPECTED_PACKAGE} {EXPECTED_FIXED_VERSION} as the first patched version",
    )


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print(f"usage: {Path(sys.argv[0]).name} ADVISORY_JSON", file=sys.stderr)
        return 2
    try:
        document = json.loads(Path(args[0]).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"advisory_gate=BLOCKED: cannot read valid advisory JSON ({exc.__class__.__name__})", file=sys.stderr)
        return 1

    passed, reason = validate_advisory(document)
    print(f"advisory_gate={'PASS' if passed else 'BLOCKED'}: {reason}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
