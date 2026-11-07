# e3bundle — verify evidence bundles offline

[![Tests](https://github.com/Traky12/castuo-e3-001/actions/workflows/tests.yml/badge.svg)](https://github.com/Traky12/castuo-e3-001/actions/workflows/tests.yml)
![Python 3.11–3.13](https://img.shields.io/badge/python-3.11%E2%80%933.13-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green)
![Status: alpha](https://img.shields.io/badge/status-alpha-orange)

**Detect any change to a folder of evidence files, and check who signed it, without a server.**

`e3bundle` records the SHA-256 of every file in a directory, lets one or more people sign that manifest with Ed25519, and verifies the result offline: changed, missing or added files and forged or stale signatures are reported in a machine-readable JSON report with a clear exit code.

It is part of the E3-001 public protocol of CASTÚO-SYSTEM, but it works on any directory and needs nothing from CASTÚO.

## Why

Test reports, datasets, audit exports and lab results are often shared as plain folders or zips. Months later, nobody can easily show that the files are the ones that were reviewed, or who approved them. Hosted signing services solve this, but add accounts, network access and a third party. `e3bundle` keeps it to one Python file, one dependency (`cryptography`) and plain JSON you can read.

## Install

**Release status (2026-10-11):** `v0.1.3` is published as a GitHub alpha prerelease at source commit `3f622a2cfd5cf1826d22d9266b542710d8b0faf1`. The release's Linux tests and clean-wheel smoke test passed. The GitHub Actions container workflow also passed and published `ghcr.io/traky12/e3bundle:0.1.3` for `linux/amd64` and `linux/arm64`, with SBOM and build provenance ([run 38088766046](https://github.com/Traky12/castuo-e3-001/actions/runs/38088766046)).

**Important: the README inside the `v0.1.3` tag is a historical snapshot.** It was committed before publication and still contains the earlier pre-release notice. We are not rewriting the release tag; use this `main` README and the linked run records for current release state. The release remains an alpha: PyPI publication is blocked, public security-advisory fixed-version metadata has not been confirmed here, and the public Pages URL has not been verified as serving this release. No production or independent-validation claim is made.

**PyPI publication remains blocked; root cause is unconfirmed.** In [run 38088766020](https://github.com/Traky12/castuo-e3-001/actions/runs/38088766020), the build and clean-wheel smoke test passed, but PyPI rejected Trusted Publishing with `invalid-publisher`. Do **not** treat the immutable GitHub `sub` format as the leading cause: Warehouse merged [PR #19422 on 29 January 2026](https://github.com/pypi/warehouse/pull/19422) to stop checking `sub` for GitHub publishers because the structured claims are checked separately. The open [Warehouse issue #19347](https://github.com/pypi/warehouse/issues/19347) concerns generic OIDC support; it does not prove a defect in this GitHub flow. Next, verify that the Pending Publisher actually exists in the expected PyPI account and compare its saved project/owner/repository/workflow/environment fields against the run's non-secret claims, including whitespace and account/project scope. A similar [Warehouse report #20504](https://github.com/pypi/warehouse/issues/20504) received a maintainer response that no pending-publisher row existed for that reporter's project, despite the reporter saying it had been recreated; this is an example of why persistence must be confirmed, not evidence about e3bundle's own record. Stop blind retries, escalate if the stored record and claims appear to match, and keep the release blocked. The manual Twine contingency is a separate owner-approved risk decision, not a fix for OIDC.

For controlled source-level evaluation only, the immutable source commit for the GitHub alpha is `3f622a2cfd5cf1826d22d9266b542710d8b0faf1`. The published tag is an alpha prerelease, not a production recommendation. The command below is intentionally not presented as a general installation recommendation while the public advisory, PyPI and Pages gates remain open.

```bash
git clone --branch v0.1.3 --depth 1 https://github.com/Traky12/castuo-e3-001
cd castuo-e3-001
python -m pip install .
```

The tag's README contains a stale pre-publication statement; this current `main` README is the release-status source of record. PyPI availability, independent review, public advisory fixed-version metadata and deployment of a matching browser demo remain unconfirmed. Python 3.11 or newer.

## Try it in your browser

Verify the signed example bundles without installing anything: **[open the browser demo](https://traky12.github.io/castuo-e3-001/)**.

The demo uses the real `v0.1.1` example bundles and performs SHA-256 and Ed25519 verification locally with WebCrypto. You can tamper with the files in eight ways, create and sign your own bundle and verify it later with the CLI, or [verify a bundle folder from your device](https://traky12.github.io/castuo-e3-001/paquete.html) without uploading it (browser limits: 200 files, 50 MiB). On every change, CI checks that the demo gives the same result as the `v0.1.1` CLI (`docs/demo/tests/`) in Chromium, Firefox and WebKit. Data is synthetic; a successful verification does not certify that content is true.

## Run with Docker

The `v0.1.3` alpha image was published by GitHub Actions and attested with SBOM/build provenance. For reproducibility, pin the verified multi-platform image digest:

```bash
docker pull ghcr.io/traky12/e3bundle:0.1.3
docker run --rm -v "$PWD:/data:ro" ghcr.io/traky12/e3bundle@sha256:0b491cf8e37247f4b71089b891ad6d77081398f64c02fc46d88a69818500f994 \
  verify /data/examples/bundles/valid --min-signatures 2 \
  --trusted-keys /data/examples/bundles/trusted-keys.json --format text
```

The image workflow's build-test and publish jobs both passed ([run 38088766046](https://github.com/Traky12/castuo-e3-001/actions/runs/38088766046)). This establishes the container artifact and its release workflow, not independent review, a public fixed-version advisory, or production authorization.

## 30-second demo

![Terminal: the valid bundle verifies with exit code 0; the tampered bundle fails with hash mismatch: data/readings.csv and exit code 1](docs/assets/demo.svg)

The repository ships two signed example bundles: [`valid`](examples/bundles/valid) and [`tampered`](examples/bundles/tampered), which differs by one temperature value in `data/readings.csv`.

```console
$ e3bundle verify examples/bundles/valid --min-signatures 2 --trusted-keys examples/bundles/trusted-keys.json
{ ... "files_verified": 2, "signatures_trusted": 2, "status": "VERIFIED", "findings": [] ... }
$ echo $?
0

$ e3bundle verify examples/bundles/tampered --min-signatures 2 --trusted-keys examples/bundles/trusted-keys.json
{ ... "files_verified": 1, "status": "FAILED", "findings": ["hash mismatch: data/readings.csv"] ... }
$ echo $?
1
```

Both commands run in CI on every change, so this output is checked, not illustrative.

For a human-readable summary, add `--format text`:

```console
$ e3bundle verify examples/bundles/valid --min-signatures 2 --trusted-keys examples/bundles/trusted-keys.json --format text
VERIFIED  example-001  files 2/2  signatures 2 trusted / 2 valid
$ e3bundle verify examples/bundles/tampered --min-signatures 2 --trusted-keys examples/bundles/trusted-keys.json --format text
FAILED  example-001  files 1/2  signatures 2 trusted / 2 valid
  - hash mismatch: data/readings.csv
```

JSON remains the default (`--format json`). `--format` changes stdout only:
`--output reports/verification.json` still writes the full JSON verification
report, including limitations, even with `--format text`. Exit codes are
unchanged. Input errors print `ERROR` and its findings in the selected format;
as before, they do not write an output file. Without `--trusted-keys`, the text
summary says `trust not checked` rather than implying signer identity was verified.

The [verify report JSON Schema](schemas/e3bundle-report.schema.json) (draft 2020-12)
describes current JSON output, including all three success statuses, `FAILED`,
and the minimal `ERROR` report (`status`, `findings`, `limitations`).
It validates report structure, not evidence or trust. `bundle_id` is passed
through from the manifest without type validation and is `null` when absent.

`--format text` is available from v0.1.1; `v0.1.0` supports JSON output only.

## Use it on your own files

```bash
e3bundle keygen   --private-key ~/keys/alice.key --signer-id alice        # once per signer
e3bundle manifest my-bundle --bundle-id my-bundle-001                     # hash every file
e3bundle sign     my-bundle --private-key ~/keys/alice.key --signer-id alice --role reviewer
e3bundle verify   my-bundle --min-signatures 1 --trusted-keys trusted.json
```

`trusted.json` maps signer ids to public keys, for example `{"alice": "<public_key_b64 from ~/keys/alice.pub.json>"}`. Keep private keys outside the bundle and outside any repository.

| Exit code | Status | Meaning |
|---|---|---|
| `0` | `VERIFIED` | files unchanged, nothing undeclared, and at least `--min-signatures` (≥ 1) distinct keys **you pinned** with `--trusted-keys` signed this manifest |
| `0` | `VERIFIED_TRUST_NOT_CHECKED` | the same, but without `--trusted-keys`: valid signatures, unknown signers |
| `0` | `VERIFIED_INTEGRITY_ONLY` | files unchanged and nothing undeclared; no signature was required (`--min-signatures 0`) |
| `1` | `FAILED` | see `findings` |
| `2` | `ERROR` | unreadable manifest or invalid input, or `--strict` without `--trusted-keys` and `--min-signatures >= 1` |

Only plain `VERIFIED` says who signed. In CI, add `--strict` so a missing key file or minimum is an error instead of a weaker pass.

What `verify` detects: modified, missing and undeclared files; path traversal and symlinks; forged, stale or duplicate signatures; and non-canonical Base64 encodings of cryptographic fields. Signature thresholds count distinct decoded public keys, not signer IDs or their textual encodings. With `--trusted-keys`, signatures from keys you did not pin are rejected.

## Use it in GitHub Actions

The composite Action source is included in the `v0.1.3` alpha tag, but no versioned Action example is promoted here while PyPI publication and advisory closeout remain pending. For any evaluation, use the full 40-character commit SHA for `v0.1.3` (`3f622a2cfd5cf1826d22d9266b542710d8b0faf1`) and provide an explicit trusted-key set with a positive signature threshold. Do not treat this alpha as independently reviewed or production-authorized.

`trusted-keys` is required and `min-signatures` defaults to `1`; signatures count once per distinct key. To check file hashes only, set `integrity-only: "true"`: the status is then `VERIFIED_INTEGRITY_ONLY`, never `VERIFIED`.

The step writes the JSON report (`report-path`, default `e3bundle-report.json`), adds the findings to the job summary and fails when verification does not pass. Set `fail-on-error: "false"` to keep the job going and branch on the `status` output (`VERIFIED`, `VERIFIED_INTEGRITY_ONLY`, `FAILED` or `ERROR`) instead; GitHub does not expose outputs of a failed step.

## Limits

A `VERIFIED` result means the declared files are unchanged and enough valid signatures cover this exact manifest. It does not mean:

- that the content is true or correct;
- who signed, unless you pin keys with `--trusted-keys`;
- that signers are independent of each other or of the author;
- when something was signed (`signed_at` is self-declared, there is no timestamp authority);
- that keys were not compromised or have not been revoked (there is no revocation list);
- it is not a certification, regulatory compliance assessment or production authorization.

The bundle format `e3.bundle.v1` is **experimental** and may change before `1.0`.

## Security

Report vulnerabilities privately as described in [SECURITY.md](SECURITY.md). The tool never reads private keys during `verify`, makes no network calls and does not modify the bundle.

## Roadmap (proposed, not committed)

- PyPI distribution (`pip install e3bundle`): blocked at OIDC Trusted Publishing, likely due to the immutable OIDC subject format; follow [the release runbook](docs/PYPI-RELEASE-RUNBOOK.es.md), compare the saved publisher row, escalate if it matches, and use the manual upload contingency only if the owner accepts its temporary account-token risk.
- Detached signature export and key rotation guidance.
- Optional RFC 3161 timestamping.

Changes are recorded in [CHANGELOG.md](CHANGELOG.md). Contributions, bug reports and *reproduction reports* are welcome: see [CONTRIBUTING.md](CONTRIBUTING.md). The [public adoption roadmap](docs/PUBLIC_ADOPTION_PLAN.md) records tester-first milestones and community work.

## Community

Start in 10 minutes, improve the project in an hour, or become an independent E3-001 reviewer: see the contribution levels in [CONTRIBUTING.md](CONTRIBUTING.md). Questions: [SUPPORT.md](SUPPORT.md). Decisions and AI-assisted development: [GOVERNANCE.md](GOVERNANCE.md). Conduct: [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). Thanks to everyone in [CONTRIBUTORS.md](CONTRIBUTORS.md).

### What we need now

Targets for Phase 1 of the [public adoption plan](docs/PUBLIC_ADOPTION_PLAN.md), not achievements. Counts as of 2026-10-10, each checkable from the linked source:

| Target | Now | Source |
|---|---|---|
| Independent reproductions (CLI path) | 0 / 5 | [#30](https://github.com/Traky12/castuo-e3-001/issues/30), label [`tester-report`](https://github.com/Traky12/castuo-e3-001/labels/tester-report) |
| Merged pull requests from external contributors | 1 / 3 | [CONTRIBUTORS.md](CONTRIBUTORS.md) |
| Signed independent E3-001 reviews | 0 / 2 | [PROTOCOL.md](PROTOCOL.md) |
| Known uses of the GitHub Action outside this repository | 0 / 2 | open a [Discussion](https://github.com/Traky12/castuo-e3-001/discussions) to report one |

Scoped tasks: [`good first issue`](https://github.com/Traky12/castuo-e3-001/labels/good%20first%20issue) · [`help wanted`](https://github.com/Traky12/castuo-e3-001/labels/help%20wanted) · [`documentation`](https://github.com/Traky12/castuo-e3-001/labels/documentation) · [`testing`](https://github.com/Traky12/castuo-e3-001/labels/testing).

Every change goes through a pull request with public review and automated tests; changes without context, a test or a reason are not merged. An accepted contribution or a successful reproduction is not a validation, certification or institutional endorsement of the project.

---

## E3-001 protocol

`e3bundle` is also the public tooling of the CASTÚO-SYSTEM E3-001 public protocol for controlled independent reproduction. Controlled-review material may be provided under defined review conditions; the private core stays outside the public scope, and a successful reproduction does not validate, certify or promote it. Castuo-system remains the private canonical authority for current technical state and promotion decisions.

**Current state:** external replay pending · signed review 0/2 · promotion `BLOCKED`. The replay harness is not published here, so a clean clone reproduces the verifiers and example bundles, not the complete S-001A replay.

Full protocol, authority boundary, synthetic S-001A demo and history: [docs/E3-001.md](docs/E3-001.md) · [PROTOCOL.md](PROTOCOL.md) · [STATUS.md](STATUS.md).

## License

MIT — see [LICENSE](LICENSE).
