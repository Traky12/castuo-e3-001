# Contributing

Thank you for helping improve E3-001. Bug reports, reproduction attempts and small, focused pull requests are welcome. Changes should improve reproducibility, clarity, defensive behaviour or usability without overstating what the evidence proves.

## Before you start

- Read the scope section in [README.md](README.md): this repository verifies declared integrity and signature predicates; it does not assess whether evidence content is true.
- Open an issue for material behaviour changes before implementing them.
- Never commit private keys, tokens, customer data, internal CASTÚO-SYSTEM source or other non-public material. Test fixtures must be synthetic.

## Development setup

Python 3.11 or newer.

```bash
python -m pip install -r requirements.txt pytest
python -m pytest tests -v
```

Tests run on Linux in CI (Python 3.11, 3.12 and 3.13); that run is the reference result. Tests that need symlinks are skipped where the platform does not allow them.

To exercise the S-001A validator quickstart:

```bash
python examples/make_demo_bundle.py demo/ok
python scripts/validate_external_evidence_bundle.py demo/ok --output demo/ok-validation.json
```

The expected result for the synthetic bundle is `DEMO_VALIDATED`, not `VERIFIED_FOR_G2`. The G2 evaluator must block this demo. This is an intentional assurance boundary, not a failing test.

## Pull requests

- One purpose per pull request; add a focused test for every behaviour change and negative cases for security-sensitive code (tests first is preferred).
- Keep claims bounded. Passing local tests or a synthetic bundle is not independent validation, certification, production readiness or evidence that a real-world claim is true.
- Do not add dependencies without explaining the need and reviewing their maintenance and licence posture.
- Keep CI permissions minimal and pin third-party GitHub Actions to immutable commit SHAs.
- Preserve the promotion firewall: `oneA: false` and `promotion: BLOCKED` unless a separately authorized process changes the governing evidence; this repository does not grant that authorization.
- Use conventional commit prefixes: `feat:`, `fix:`, `docs:`, `ci:`, `refactor:`, `test:`.
- Do not bypass hooks or checks.

Checklist:

- [ ] Scope and expected behaviour are described.
- [ ] Tests cover success and relevant failure cases.
- [ ] README/protocol claims reflect the implementation.
- [ ] No secrets or non-public evidence are included.
- [ ] Python test suite and all required GitHub Actions checks pass.
- [ ] Any limitations or incomplete work are stated explicitly.

## Reporting a reproduction

If you ran the demo or verified your own bundle, open an issue with the *Reproduction report* template. Reports of failures are as valuable as successes.

External reproduction and review must be performed by genuinely independent parties. Do not self-label a run as independent or treat generated demo identities as people or organizations.

## Security

Do not open public issues for vulnerabilities; follow [SECURITY.md](SECURITY.md).
