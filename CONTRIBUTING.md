# Contributing to E3-001

Thank you for considering a contribution. E3-001 is a public, evidence-scoped verification protocol and supporting Python tooling. Changes should improve reproducibility, clarity, defensive behavior or usability without overstating what the evidence proves.

## Development setup

Python 3.11 or newer is supported by CI.

```bash
python -m pip install -r requirements.txt pytest
python -m pytest tests -v
```

To exercise the public validator quickstart:

```bash
python examples/make_demo_bundle.py demo/ok
python scripts/validate_external_evidence_bundle.py demo/ok --output demo/ok-validation.json
```

The expected result for the synthetic bundle is `DEMO_VALIDATED`, not `VERIFIED_FOR_G2`. The G2 evaluator must block this demo. This is an intentional assurance boundary, not a failing test.

## Contribution expectations

- Open an issue for material behavior changes before implementing them.
- Include a focused test for new behavior and negative cases for security-sensitive code.
- Keep claims bounded. Passing local tests or a synthetic bundle is not independent validation, certification, production readiness or evidence that a real-world claim is true.
- Never commit private keys, tokens, customer data, internal CASTÚO-SYSTEM source or other non-public material.
- Do not add dependencies without explaining the need and reviewing their maintenance and license posture.
- Keep CI permissions minimal and pin third-party GitHub Actions to immutable commit SHAs.
- Preserve the promotion firewall: `oneA: false` and `promotion: BLOCKED` unless a separately authorized process changes the governing evidence; this repository does not grant that authorization.

## Pull request checklist

- [ ] Scope and expected behavior are described.
- [ ] Tests cover success and relevant failure cases.
- [ ] README/protocol claims reflect implementation.
- [ ] No secrets or non-public evidence are included.
- [ ] Python test suite and all required GitHub Actions checks pass.
- [ ] Any limitations or incomplete work are stated explicitly.

External reproduction and review must be performed by genuinely independent parties. Do not self-label a run as independent or treat generated demo identities as people or organizations.
