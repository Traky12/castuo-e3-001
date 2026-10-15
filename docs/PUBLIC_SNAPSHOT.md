# Public verified snapshot

The public snapshot is an optional, read-only projection of `validate_external_evidence_bundle.py` and `evaluate_g2.py`. It is not an authority object and it never authorizes production. The generated contract retains `oneA: false` and `promotion: BLOCKED` even when G2 passes.

## Execution boundary

The workflow `.github/workflows/public-snapshot.yml` runs on a protected GitHub environment named `public-snapshot`. The evidence bundle must be supplied by an external operator. The runner validates the bundle, evaluates G2, and only then calls `scripts/publish_public_snapshot.py`.

The private Ed25519 key is read from the protected `CASTUO_SNAPSHOT_SIGNING_KEY_B64` secret. It is not committed, printed, sent to the dashboard, or embedded in the generated JSON. The snapshot contains only the public key, key identifier, payload digest and signature. These fields provide self-contained signature material, not publisher trust; the public key must be pinned out of band.

## Required operator configuration

An administrator must create the protected environment and add the signing secret outside the repository. Reviewers should require the workflow run to be approved before it can write `public/status-snapshot.json` to `main`.

```bash
gh secret set CASTUO_SNAPSHOT_SIGNING_KEY_B64 \
  --repo Traky12/castuo-e3-001 \
  --env public-snapshot \
  --body <base64-ed25519-private-key>
```

The key must be generated and stored by the approved external operator or signing device. Do not paste it into a browser form or commit it to the repository.

## External signer identity gate

The snapshot workflow passes `trust/e3-001-trust-store.json` to the evidence validator. This registry is deliberately empty at present. Consequently, an external bundle cannot qualify for G2 merely by carrying self-signed runner/reviewer records: it remains `BLOCKED` until the public keys are verified out of band, approved through a separate reviewed change, and enrolled with explicit role and identity. The registry must retain revocation records; revoked keys never satisfy validation. This is an additional gate independent of the publication signing secret.

## Dashboard contract

The dashboard reads:

```text
https://raw.githubusercontent.com/Traky12/castuo-e3-001/main/public/status-snapshot.json
```

The embedded public key is **not a trust root**. The publishing firewall checks the canonical unsigned payload digest and Ed25519 signature, and also requires `public_verification.key_id` plus its public key to match an active `role: publisher` entry in `trust/e3-001-trust-store.json`. The dashboard itself must pin the expected publisher key independently of the fetched snapshot; verifying only with the key embedded in the same untrusted JSON would allow an attacker to replace both the payload and key. Until a separate reviewed change enrolls the real publisher public key and the consuming dashboard verifies that pin, public snapshot publication remains blocked and dashboard-side authenticity is not claimed. A missing artifact, invalid signature or unsupported browser crypto implementation falls back to the local declared snapshot and keeps promotion blocked.

## Non-claims

A signed public snapshot proves that the configured runner signed the declared projection. It does not, by itself, prove that the runner was independent, that the evidence was substantively inspected, that staging is production, or that an AuthorityObject exists. The E3 validator and G2 evaluator remain the source of the evidence decision; the dashboard is a read-only surface.

## Current operator handoff

As of the latest verification, the `public-snapshot` environment exists with protected-branch policy and a required reviewer rule for `Traky12` with self-review prevention. The environment has no configured `CASTUO_SNAPSHOT_SIGNING_KEY_B64` secret, and `public/status-snapshot.json` is intentionally absent. The public snapshot workflow therefore cannot be run successfully yet. This is the expected fail-closed state, not a workflow failure.

To close the external gate, an authorized operator must first verify and enroll the external runner/reviewer public keys in the trust store through a separately reviewed change, add the publication secret through GitHub environment secrets, supply a real externally generated E3-001 bundle, and dispatch `E3-001 public verified snapshot` with the exact frozen source commit. The workflow then validates the bundle, evaluates G2, verifies the signed payload and the pinned publisher identity, runs the public claim firewall, and writes the signed snapshot only if all checks pass. The publisher-key entry is intentionally absent from the initial trust store, so this gate remains blocked until a real public key is independently checked and approved. A successful run still keeps `oneA=false` and `promotion=BLOCKED`.

The available local candidate was also checked read-only and returned `status: BLOCKED` with `claim_boundary: NO_CLAIM`; it lacks the external runner attestation and signed reviewer quorum and does not satisfy the E3-001 manifest contract. It is therefore not promoted, copied or relabeled as external evidence.
