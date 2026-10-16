# Public adoption roadmap

**Repository:** `Traky12/castuo-e3-001`  
**Snapshot date:** 2026-10-16  
**Status:** `IN PROGRESS · BROAD PROMOTION BLOCKED BY RELEASE GATES`  
**Primary objective:** sustainable, independent use of e3bundle. Starstruck is a visibility side-effect, never a quality or assurance metric.

## Decision summary

Use `castuo-e3-001` as the single public adoption surface for e3bundle. Do not create another repository or parallel product page to chase stars. Improve first-run success, reconcile existing release and security gates, obtain independent reproduction reports, then share specific technical material with the communities most likely to benefit.

**Observed baseline (GitHub API, 2026-10-16):** 2 stars, 1 fork and 20 open issues on this repository. The open queue also contains multiple dependency and maintenance PRs. Re-check these counts before using them in a public update; never present them as adoption or validation evidence.

## Existing GitHub work to reconcile first

**Snapshot: 2026-10-16.** These are pointers into the current backlog, not a substitute for re-checking their live checks and reviews. Reuse these threads and branches; do not open duplicate issues for the same work.

| Item | Current purpose | Required next step before the relevant gate can close |
|---|---|---|
| [PR #85](https://github.com/Traky12/castuo-e3-001/pull/85) | Canonical Base64 key identity follow-up | Verify exact-head security, CLI and browser/CLI conformance checks; do not claim v0.1.3 contains this follow-up. |
| [PR #91](https://github.com/Traky12/castuo-e3-001/pull/91) | Demo CSP and public-evidence publication hardening | Complete review of the trust boundary and exact-head negative tests before merging or promoting. |
| [PR #90](https://github.com/Traky12/castuo-e3-001/pull/90) and [issue #87](https://github.com/Traky12/castuo-e3-001/issues/87) | Align demo/release wording and preserve publication gates | Review the source pin and new status-contract test; do not retarget or rewrite the existing v0.1.3 tag. |
| [PR #89](https://github.com/Traky12/castuo-e3-001/pull/89) | Correct PyPI Trusted Publisher diagnosis | Keep root cause `UNCONFIRMED`; only the account owner can read back the saved Pending Publisher row and compare its fields. |
| [PR #88](https://github.com/Traky12/castuo-e3-001/pull/88) | Spanish legal/claim boundary documentation | Obtain the required owner/legal wording review; do not present it as a legal compliance assessment. |
| [PR #94](https://github.com/Traky12/castuo-e3-001/pull/94) | Playwright dependency update | A Pages workflow check was observed failing on this PR head; diagnose the failed check before considering merge. Recheck the live result rather than assuming it is still failing. |
| [issue #30](https://github.com/Traky12/castuo-e3-001/issues/30) | Five independent CLI testers | Keep `PAUSED` until the PyPI package, fixed-version advisory and matching public Pages deployment are verified. |

Do not merge any of these solely because another PR is green. In particular, separate a source-code fix from the released artifact, and separate a candidate browser build from a successful public Pages deployment.

## Non-negotiable principles

1. **No artificial engagement.** Never buy, exchange, automate, or coordinate stars; do not use alternate accounts or mass unsolicited promotion.
2. **No claim without provenance.** Stars, traffic and downloads are discovery signals, not proof of use, quality, validation, certification, production maturity or commercial traction.
3. **Test before broad promotion.** A new user must be able to follow published instructions from a clean environment without private access, secrets or live assistance.
4. **Separate demo from evidence.** Synthetic demo results must remain labelled synthetic. They must never be counted as an independent E3-001 replay or as proof about CASTÚO-SYSTEM.
5. **Publish only after gates.** Keep broad promotional activity paused while material release, package, advisory or deployment gates remain unresolved. Technical maintenance and bounded, non-promotional documentation work can continue.
6. **One canonical public surface.** Send product discovery, reproducible reports and contribution traffic to this repository; do not split the same tool across duplicate repos.
7. **Independent feedback is independent.** Do not count the author, repository CI, bots, coordinated star exchanges or synthetic identities as external users or reviewers.

## Starstruck milestones

Each milestone concerns **one repository created by the account**, not the sum of stars across repositories. Thresholds below follow GitHub community guidance; achievement processing may not be instantaneous.

| Milestone | Threshold on one repository | CASTÚO target |
|---|---:|---|
| Initial Starstruck | 16 stars | First reach goal |
| Bronze / Starstruck x2 | 128 stars | Second reach goal |
| Silver / Starstruck x3 | 512 stars | Long-range reach goal |
| Gold / Starstruck x4 | 4,096 stars | Aspirational; do not forecast |

Do not advertise these badge targets as product milestones. The primary outcome is more independent people successfully using or reviewing the tool. If the badge tiers change, re-check GitHub's current achievement UI before editing this table.

## Stage 0 — Baseline and stop/go decision

**Current decision: maintain, but do not run a broad promotional campaign.**

- [x] Pick one primary public repository: `castuo-e3-001`.
- [x] Keep alpha, synthetic-demo and assurance boundaries visible in the README.
- [x] Maintain a public adoption plan and an existing tester issue rather than creating duplicate work items.
- [ ] Re-confirm release artefacts and public security advisory metadata.
- [ ] Resolve or formally close the PyPI Trusted Publisher blocker; record the evidence and chosen publishing route.
- [ ] Re-confirm the public Pages URL serves the intended version, not the older synthetic v0.1.1 interaction.
- [ ] Reconcile release/tag documentation and review relevant dependency/security alerts.
- [ ] Check current main-branch CI, not only passing pull-request checks, before declaring the release gate clear.

**Stop/go gate:** broad promotion stays `BLOCKED` until the relevant release, advisory and demo-publication gates are confirmed from current evidence. A successful CI run does not by itself unblock distribution or imply production readiness.

## Stage 1 — First-run clarity and repository hygiene

Complete these tasks before asking new users to evaluate the tool:

- [ ] Keep the first screen of README focused on the job-to-be-done, who benefits, the simplest successful command, and the tampered-input failure case.
- [ ] Keep copy-paste commands aligned with an actually available source/release; do not make `pip install e3bundle` the primary path until PyPI availability is verified.
- [ ] Make supported Python versions and environment requirements consistent across README, package metadata, CI and release notes.
- [ ] Link directly to valid and tampered fixtures, the CLI report schema, the threat model, the contribution guide and the security reporting route.
- [ ] Preserve the explanation that integrity/signature verification does not prove content truth, real-world identity, independence of signers or field validity.
- [ ] Remove duplicate explanations and stale release wording, without rewriting historical release tags.
- [ ] Review open PRs and issues before adding new ones. Prefer closing loops on the existing backlog; do not create duplicate tasks.
- [ ] Keep project topics and repository description specific, accurate and searchable. Avoid buzzword-only metadata.

**Acceptance evidence:** a clean-clone walkthrough can be followed from the documented source, and the valid and tampered examples produce the stated outcomes. Record exact commit, environment, commands, exit codes and test outputs.

## Stage 2 — Independent reproduction (tester gate)

The existing [issue #30](https://github.com/Traky12/castuo-e3-001/issues/30) is the source of record for recruiting five independent testers. Respect its paused status until the blockers recorded there are reconciled; do not create another tester issue.

Once the gate is opened:

1. Recruit five people who are not the author and are not dependent on private repository access.
2. Give every tester the same public instructions, test fixtures and report template. Do not coach them through the run while they test.
3. Ask them to record OS, Python version, exact commands, expected and actual result, exit code and any reproducible friction. Never ask them to send private keys or confidential data.
4. Triage each defect into an issue with a minimal reproduction. Record successful attempts as tester reports with consent; distinguish a clean CLI run from the separate S-001A replay protocol.
5. Count only completed, attributable independent tests. CI, the author's own machine and the synthetic browser demo do not count.

- [ ] 0/5 → 1/5 → 3/5 → 5/5 independent clean-clone reports, with evidence links.
- [ ] Publish a short aggregate summary only with tester consent and appropriate redaction.
- [ ] Do not claim independent validation or certification from this exercise.

## Stage 3 — Contribution and maintenance loop

Use the existing public queue and contribution rules.

- [ ] Triage issues and open PRs into: `security/release blocker`, `onboarding/documentation`, `bug`, `feature`, or `needs external evidence`.
- [ ] Prioritise release blockers, first-run defects and small reproducible work over feature expansion.
- [ ] Make a contributor task genuinely bounded: expected behaviour, affected path, test command and acceptance criterion.
- [ ] Require meaningful tests and review for code changes; do not merge solely to increase activity or contribution counts.
- [ ] Credit substantive contributions accurately, with contributor consent where required.
- [ ] Publish a changelog entry for user-visible changes and keep known limitations explicit.

Existing candidate tasks include the [cross-platform install guide](https://github.com/Traky12/castuo-e3-001/issues/22), [cross-platform CI](https://github.com/Traky12/castuo-e3-001/issues/23), [trusted-key bootstrap and rotation](https://github.com/Traky12/castuo-e3-001/issues/24), [reusable GitHub Actions example](https://github.com/Traky12/castuo-e3-001/issues/25), [threat model](https://github.com/Traky12/castuo-e3-001/issues/26) and [tampering tutorial](https://github.com/Traky12/castuo-e3-001/issues/29). Recheck issue state and avoid doing work already covered by open PRs.

## Stage 4 — Evidence-led technical distribution

**Entry criteria:** the stop/go gate is cleared, the README is coherent, and the five-tester gate has been completed or a transparent reason for a narrower scope is documented.

- [ ] Publish one concise walkthrough showing both successful verification and rejection of a tampered bundle.
- [ ] Make a short, reproducible demo or terminal recording; redact local paths, usernames, secrets and irrelevant private data.
- [ ] Explain the threat model, what the result means, and what it does not mean.
- [ ] Share the specific technical resource in relevant Python, cryptography, auditability, reproducible research or data-integrity communities, following each community's rules.
- [ ] Participate in related discussions by answering the actual question first; mention e3bundle only when it directly helps and disclose your authorship.
- [ ] Invite bug reports, reproducibility reports and code review—not a star in exchange for help.
- [ ] Avoid mass cross-posting, unsolicited direct messages, unrelated comments and repetitive posts.
- [ ] Record where a resource was shared, date, community rules, useful replies and attributable feedback; do not track or expose individuals unnecessarily.

**Suggested release-note / community copy** (use only after the relevant publication gate has passed):

> I built e3bundle, a small offline Python tool that hashes files into a manifest and checks Ed25519 signatures against explicitly trusted keys. The repository includes a signed valid example and a deliberately tampered example so the verification and failure paths can both be reproduced. It is alpha software: a successful result checks integrity and configured signatures; it does not prove the underlying data is true or certify a real-world process. I would value reproducible bug reports and technical review.

Do not publish this copy while linked artefacts or claims are stale. Adjust it to the actual release and the rules of the target community.

## Stage 5 — Profile and discovery path

- [ ] Keep the profile README's first call-to-action pointed to this canonical repository and its working demo, with the demo version clearly labelled.
- [ ] Pin a small, coherent portfolio: e3bundle first; then one field/edge project and one assurance/evidence project. Do not pin every experiment.
- [ ] Remove duplicate explanations, stale release claims and links that do not resolve.
- [ ] Keep project names and descriptions distinct: e3bundle for offline evidence integrity, `castuo-agro-edge` for edge/IoT experiments, `castuo-evidence` for bounded evidence packages, and `Cast-o` for assurance tooling.
- [ ] Ensure each pinned repository has a clear README, license/IP state, maintenance status, contribution path and explicit limitations.
- [ ] Review the profile and pinned repos monthly; avoid profile language that implies independent verification or production readiness.

Pin selection is a manual profile setting; do not claim it has been changed unless the GitHub UI confirms it.

## Stage 6 — Monthly measurement and decision

Record the date and evidence source for each measurement. Use GitHub Insights for traffic when available, repository metadata for stars/forks, and issue/PR records for engineering outcomes.

| Metric | What it helps measure | What it does not prove |
|---|---|---|
| Unique visitors / clones | Discovery and repeat interest | Successful installation or usage |
| Stars and forks | Interest in the repository | Adoption, correctness or quality |
| Independent clean-clone reports | Reproducibility in external environments | Certification or field validity |
| External contributors / substantive reviews | Collaboration and scrutiny | Independent assurance by itself |
| Issues resolved / onboarding friction | Maintenance and usability | Absence of vulnerabilities |
| Package downloads, if published | Distribution activity | Active users or production deployments |
| High-severity open findings and failed gates | Residual risk | That unobserved risk is absent |

- [ ] Update the scorecard once per month, not after every star.
- [ ] Compare the current state with the prior month's baseline.
- [ ] Prefer user-observed outcomes over vanity metrics.
- [ ] Publish no adoption number without a source and a date.
- [ ] Reassess whether each additional feature helps a demonstrated user need.

## Stop conditions

Pause external promotion if any of the following occurs:

- a valid bundle fails or a tampered bundle passes;
- the synthetic S-001A demo becomes eligible for G2 or is mistaken for independent evidence;
- required main-branch checks fail or their status cannot be verified;
- a material security issue or release blocker remains unresolved;
- public instructions point to an unavailable or mismatched artefact;
- README, demo, package and release metadata materially disagree;
- user-facing wording overstates implemented scope, validation or adoption.

Resume only when corrective evidence is recorded and the responsible maintainer re-evaluates the gate.

## Source of record and review cadence

- Tester gate: [issue #30](https://github.com/Traky12/castuo-e3-001/issues/30)
- Reproduction/review: [issue #86](https://github.com/Traky12/castuo-e3-001/issues/86) and [PROTOCOL.md](../PROTOCOL.md)
- Public status: [STATUS.md](../STATUS.md)
- Release and packaging: [release runbook](PYPI-RELEASE-RUNBOOK.es.md)
- Security reporting: [SECURITY.md](../SECURITY.md)
- Contribution rules: [CONTRIBUTING.md](../CONTRIBUTING.md)

Review this plan monthly, and whenever a release, security, deployment or independent-review gate changes. Update the snapshot date and star count only after checking the live sources. All promotion and publication remain subject to owner review; this plan itself does not authorise a release, deployment, merge or external claim.
