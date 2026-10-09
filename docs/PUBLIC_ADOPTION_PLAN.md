# Public adoption roadmap

**Repository:** `Traky12/castuo-e3-001`  
**Plan status:** `IN PROGRESS`  
**Snapshot:** 2026-10-09

This roadmap is the maintainer's operational plan for making E3-001 useful and discoverable to developers outside CASTÚO-SYSTEM. It is not a claim that the planned milestones have been completed. The objective is sustainable adoption; GitHub stars are a secondary discovery signal.

## Operating principles

1. Deliver a working, reproducible example before asking communities to review the project.
2. Make the clean-clone path independent of private repositories, private credentials and hosted CASTÚO infrastructure.
3. Distinguish structural validation of a synthetic bundle from independent evidence. A demo must never pass G2 or be presented as S-001A evidence.
4. Prefer a small number of useful contributions, integrations and independent reproductions over volume of posts or commits.
5. Do not buy, exchange, automate or otherwise manipulate stars; do not spam communities or misrepresent maturity.

## Phase 0 — Safe, clean-clone quickstart

**Exit criteria**
- [ ] `requirements.txt` declares runtime dependencies.
- [ ] Synthetic valid bundle is clearly marked `DEMO_ONLY`.
- [ ] Demo result is `DEMO_VALIDATED`, never `VERIFIED_FOR_G2`.
- [ ] G2 evaluator returns `BLOCKED` for the synthetic bundle and reports no staging eligibility.
- [ ] Tamper cases fail closed.
- [ ] Linux CI passes on every supported Python version.
- [ ] The README quickstart succeeds from a fresh clone.
- [ ] The repository owner reviews the diff before merge.

## Phase 1 — First external users (0–30 days after merge)

- [ ] Publish a tagged release only after clean-clone instructions and CI are verified.
- [ ] Ask 5–10 external developers to try the documented demo and report friction; ask for feedback, not stars.
- [ ] Record issues with exact commands, platform/Python version, expected output and actual output.
- [ ] Publish one focused technical walkthrough showing both a valid synthetic check and a rejected tampered bundle.
- [ ] Keep every report explicit about what the demo does not prove.

## Phase 2 — Community-quality baseline (30–90 days)

- [ ] Use the issue templates and contribution checklist to collect actionable reports.
- [ ] Resolve onboarding blockers before adding features.
- [ ] Publish two narrowly scoped tutorials: artifact/hash integrity, and Ed25519 signature verification.
- [ ] Share each resource only in communities whose rules and topic make it relevant; engage in discussions without repeated promotional drops.
- [ ] Invite independent reviewers to critique the public protocol and its assumptions; record findings and responses publicly.

## Phase 3 — Distribution based on demonstrated demand (90–180 days)

- [ ] Consider package distribution or a reusable GitHub Actions integration only after users request it and the interface is stable.
- [ ] Tag releases with notes, compatibility information and a rollback path.
- [ ] Prioritize fixes and integrations supported by external issues or contributions.
- [ ] Re-check dependency freshness, license compatibility, security guidance and all public claims before each release.

## Visibility milestones

These are stretch milestones for this single repository, not forecasts or acceptance criteria for software quality.

| Milestone | Stars on this repository | Interpretation |
|---|---:|---|
| Initial discovery | 16 | First community-recognition threshold |
| Bronze | 128 | Broader discovery |
| Silver / Starstruck ×3 | 512 | Target achievement |

The achievement must come from people who independently decide that this one repository is useful. Stars across multiple repositories do not substitute for the threshold on a single repository.

## Monthly scorecard

Track stars and repo traffic as discovery indicators, alongside stronger product signals:

- External users who can complete the quickstart without live assistance.
- Reproducible issues raised and resolved.
- External contributors, review feedback and independent protocol critiques.
- CI reliability by supported Python version.
- Release usage and downloads, if a package is published.
- Open high-severity issues and stale or misleading claims.

Do not interpret a star increase as independent validation, production maturity, certification, commercial traction or user adoption.

## Stop conditions

Pause promotion and release activity if the clean-clone demo breaks, any demo artifact is mistaken for independent evidence, required CI is failing, a material security concern is unresolved, or the README overstates current capabilities. Resume after evidence for the relevant condition is recorded.
