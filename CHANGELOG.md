# Changelog

All notable changes to this repository are documented here. Versions follow [Semantic Versioning](https://semver.org/); before `1.0` the bundle format and command-line interface may change.

## [Unreleased]

No additional changes beyond the prepared v0.1.4 candidate are recorded on this branch.

## [0.1.4] — CANDIDATE PREPARATION (NOT RELEASED)

### Security
- Proposed on PR #85: harden Ed25519 verification and canonical Base64 handling for public keys and signatures.
- Proposed on PR #85: enforce signature-threshold counting by distinct decoded Ed25519 public-key bytes, not signer labels or alternate Base64 spellings.
- Add Python and browser/CLI regression coverage for alternate Base64 encodings, distinct-key threshold bypass attempts, and verifier consistency.

### Evidence gate — pending; these are requirements, not completed claims
- [ ] Independent security review recorded against PR #85 head `930e1d72e4821b07fbe84ce1d833194b53fc49b4`.
- [ ] CP-3 independent OVS-01 reproduction completed by a second operator with attributable evidence.
- [ ] PR #85 approved and merged after review.
- [ ] CI completed with PASS on the final release branch commit.
- [ ] Candidate artifacts built and verified independently.

### Notes
- This is a preparation branch only. No v0.1.4 tag, GitHub release, PyPI publish, GHCR publish, or advisory update is authorized by this changelog entry.
- PR #85 remains proposed and unmerged at the time this candidate was prepared; its correction must not be described as released.
- v0.1.3 does not contain this additional canonical-encoding hardening.
- Update GHSA-55pc-7v4h-jf7c only after the corrected release has been published and the published artifacts are verified.

## [0.1.3] - 2026-10-10

### Security
- `e3bundle verify` and the browser verifier count signatures by distinct public key: one key signing under several `signer_id` values counts once and is reported as `signatures[i]: duplicate key: <id> reuses the key of <id>` (GHSA-55pc-7v4h-jf7c).
- The GitHub Action no longer reports `VERIFIED` without pinned signatures. `min-signatures` defaults to `1` and `trusted-keys` is required; without them the status is `ERROR`. Hash-only checks need `integrity-only: "true"` and report `VERIFIED_INTEGRITY_ONLY`. **Breaking** for workflows that relied on the old defaults.
- Plain `VERIFIED` now always means pinned keys and a minimum of at least 1, in the CLI, the browser demo and the Action. Without `--trusted-keys` a passing result is `VERIFIED_TRUST_NOT_CHECKED`; with `--min-signatures 0` it is `VERIFIED_INTEGRITY_ONLY`. Both still exit 0. New `--strict` flag: without `--trusted-keys` and `--min-signatures >= 1` it exits 2 (`ERROR`); the Action always uses it unless `integrity-only` is set. **Breaking** for scripts that compare the status string with `VERIFIED`.

### Changed
- CLI errors for common input mistakes say what to fix and no longer include local filesystem paths. Contributed via #72, integrated in #73 (closes #34).

**Release status:** GitHub alpha prerelease `v0.1.3` is published from commit `3f622a2cfd5cf1826d22d9266b542710d8b0faf1`. It supersedes the withdrawn, never-released `v0.1.2` candidate. PyPI publication failed with `invalid-publisher`; the GHCR publication workflow succeeded. The public security-advisory fixed-version metadata and deployment of this CLI in the live browser demo remain unconfirmed. This release is not promoted for production or as independently validated.

### Changes carried over from the withdrawn v0.1.2 candidate

### Security
- `e3bundle verify` rejects manifest paths that alias the same file under another name (`./file`, `a//b`, `a/./b`, trailing `/`) and paths containing NUL, so one file cannot be declared twice under different names.
- `e3bundle verify` rejects a symlinked bundle directory and symlinked `manifest.json` / `signatures.json` before reading them, and reports symlinks inside the bundle even with `--allow-extra`.
- `e3bundle verify` refuses `--output` inside the bundle directory (verification must not modify the bundle) and a negative `--min-signatures` (exit 2).

### Added
- Browser demo, local bundles (`paquete.html`): verify a folder from your device in the tab. `importer.js` checks names and sizes before reading anything (≤200 files, ≤10 MiB each, ≤50 MiB total, safe unambiguous paths ≤255 chars / 16 levels; no ZIP) and verifies nothing if any entry is rejected. Imported public keys are not trusted until you select them; the selection can be downloaded as a keys file. Input order and decoding follow the CLI; the UI suite compares 13 local folders with `e3bundle verify` from the tag. Known difference: symlinks (see `docs/demo/THREAT-MODEL.md`).
- Browser demo, advanced mode: a Guided / Advanced switch (`#avanzado` deep link) over the same verification. Advanced shows the exact verifier data and answers four separate questions per signature (valid Ed25519, covers this manifest, key pinned by you, counts for the threshold) plus the threshold count, and downloads `e3bundle-report.json` built in the page (sorted keys and `limitations`, as the CLI writes it; no keys or file contents). Guided is the default.
- Browser demo hardening: restrictive Content-Security-Policy (`<meta>`; GitHub Pages cannot send headers), an input layer (`docs/demo/input.js`) that follows the CLI's input contract so unreadable input is `ERROR` (exit 2) and never a verdict, a "Reiniciar sesión" control on both pages, and a Playwright suite run in CI on Chromium, Firefox and WebKit (scenarios, malformed input, reset, same-origin-only requests, CSP enforcement, keyboard, no overflow at 375/768/1440). `tests/input-conformance.mjs` compares nine malformed inputs with the v0.1.1 CLI. Threat model in `docs/demo/THREAT-MODEL.md`. `verifier.js` is unchanged.
- Browser demo, guided journey: the problem it addresses, how it works, a per-scenario explanation, a result summary with what each finding means and the next step, a checks table with consequences, the limits of VERIFIED, local CLI steps, contribution and private vulnerability reporting, and a traceability block. Verification logic (`verifier.js`) is unchanged; a long manifest hash no longer overflows on phones.
- Container image `ghcr.io/traky12/e3bundle` for `linux/amd64` and `linux/arm64` (non-root, no `latest` tag), built from the release tag by `container.yml` with SBOM, build provenance and a GitHub artifact attestation. Pull requests that touch the image are built and smoke-tested (valid bundle exit 0, tampered bundle exit 1).
- Reproduction report form: tested path (CLI or browser demo), version, environment, commands, exit codes, friction, evidence and an independence confirmation, for the five-tester gate in #30.
- Browser demo source in `docs/demo/` verifies the `v0.1.1` example bundles with WebCrypto (SHA-256, Ed25519) under eight tampering scenarios, and creates/signs bundles that the CLI can verify. The Pages workflow now tests against the exact `v0.1.3` source commit; its publication gate remains closed, so this changelog does not claim that the live public URL serves the `v0.1.3` demo.

### Fixed
- Browser verifier now matches the v0.1.1 CLI on malformed manifest and signature content (#55): `manifest files must be an array`, per-entry `sha256:<64 lowercase hex>` check, non-object file entries and signatures, non-string `signer_id`, strict base64 for keys and signatures, CLI wording for missing values (`None`), and no prototype-property paths such as `constructor`. Before the fix a `null` signature made the verifier throw. 14 new cases in `tests/input-conformance.mjs`; the 8 scenarios are unchanged. Two known differences remain (see `docs/demo/THREAT-MODEL.md`).
- Create page: the empty result box was visible before any verification (`.result` display overrode `hidden`).

## [0.1.1] - 2026-10-09

### Added
- `e3bundle verify --format text`: human-readable summary on stdout; JSON stays the default, `--output` always writes JSON, exit codes unchanged. Without `--trusted-keys` the summary says `trust not checked`. Contributed by @AFLAHAFI (#32, closes #27).
- Unit/CLI tests on Ubuntu, macOS and Windows with Python 3.11–3.13 (closes #23).
- Regression tests for a malformed `signatures.json` (exit 1) and a non-UTF-8 manifest (exit 2) (closes #35).
- Community files: `CODE_OF_CONDUCT.md` (Contributor Covenant 2.1), `SUPPORT.md`, `GOVERNANCE.md` with the AI-assisted development policy, `CONTRIBUTORS.md`, a feature request form, and contribution levels in `CONTRIBUTING.md`.
- `docs/PUBLIC_ADOPTION_PLAN.md` and a demo image in the README.

### Changed
- The S-001A validator labels synthetic `DEMO-*` bundles `DEMO_VALIDATED` (`g2_eligible: false`) and the G2 evaluator blocks them; they cannot stand in for external replay or independent review.
- The full E3-001 protocol section moved from the README to `docs/E3-001.md`; the README keeps a short summary.

## [0.1.0] - 2026-10-09

### Added
- `scripts/e3bundle.py`: generic offline bundle tool (`keygen`, `manifest`, `sign`, `verify`) for format `e3.bundle.v1` (experimental). Detects modified, missing and undeclared files, unsafe paths, symlinks, forged or stale signatures and duplicate signers; supports pinned trusted keys and a signature threshold.
- `examples/make_demo_bundle.py`: synthetic S-001A demo bundle with in-memory keys and nine `--tamper` modes.
- `requirements.txt` declaring the `cryptography` dependency.
- `pyproject.toml`: installable package `e3bundle` with an `e3bundle` console command (`pip install git+https://github.com/Traky12/castuo-e3-001`).
- `action.yml`: reusable composite GitHub Action that runs `e3bundle verify`, writes the JSON report, exposes `status` and fails the step on verification failure unless `fail-on-error: "false"`.
- `examples/bundles/`: committed signed `valid` and `tampered` example bundles with pinned `trusted-keys.json`, regenerated by `examples/make_example_bundles.py`.
- Unit tests for both validators and a Linux CI workflow (Python 3.11–3.13) that also runs the README quickstarts.

### Changed
- README reorganised product-first (problem, install, demo, limits, security, roadmap); the E3-001 protocol, authority boundary and history follow below, unchanged in substance.
- `PROTOCOL.md` states that `scripts/run_s001a_foreign_replay.py` is not published in this repository.

[Unreleased]: https://github.com/Traky12/castuo-e3-001/compare/v0.1.3...HEAD
[0.1.3]: https://github.com/Traky12/castuo-e3-001/compare/v0.1.1...v0.1.3
[0.1.1]: https://github.com/Traky12/castuo-e3-001/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/Traky12/castuo-e3-001/releases/tag/v0.1.0
