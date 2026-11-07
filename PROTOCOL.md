# E3-001 operational protocol

## Scope

E3-001 verifies only the declared S-001A behavior: fault handling, evidence capture, recovery and deterministic replay within a frozen fixture and source commit. It does not prove production readiness, field operation, certification, commercial traction, customer adoption or vendor exit.

## 1. Freeze

The package owner records:

```yaml
scenario_id: S-001A
protocol_id: E3-001-S001A-FOREIGN-REPLAY
source_commit: <40-lowercase-hex>
fixture_path: fixture.json
rollback_ref: <immutable-tag-or-commit>
external_runner: true
foreign_replay: true
production_claim: false
commercial_claim: false
```

The manifest binds the SHA-256 of the fixture, replay result and evidence envelope. Any mutation after freeze invalidates the package.

## 2. Independent runner

The operator must not be the implementation author or the package author. The runner uses a clean checkout and an identity that is not a local fallback or GitHub candidate runner. The harness must be offline-only.

The repository now provides a **candidate replay harness** (not an
authenticated independent replay or a signing device). The operator must supply
a separately obtained, exact-HEAD checkout of the public `castuo-evidence`
runner and enforce network isolation outside Python. The harness rejects dirty
tracked files and verifies the runner's SHA-256 and Git commit. Example:

```bash
python3 scripts/run_s001a_foreign_replay.py \
  --fixture /trusted/frozen/fixture.json \
  --runner-script /trusted/castuo-evidence/runners/s001a_runner.py \
  --runner-script-sha256 <64-lowercase-hex> \
  --source-commit <exact-evidence-runner-commit> \
  --runner-id <operator-assigned-external-runner-id> \
  --output /isolated/output-folder \
  --stress-repetitions 3
```

The harness writes `candidate-replay.json` with
`status=CANDIDATE_REPLAY_ONLY`, `oneR=false`, `oneV=false`,
`oneA=false`, `promotion=BLOCKED` even if all repeats match.
It explicitly reports `network_isolation=NOT_VERIFIED_BY_THIS_HARNESS`:
the independent operator must enforce and evidence network isolation,
sign the actual external attestation, and obtain two independent human
reviewers. The candidate report is **not** the signed
`foreign-replay-result.json` consumed by the external evidence validator.
Never rename/promote it or claim `PASS_WITHIN_DECLARED_SCOPE` from this
candidate test. The E3 external acceptance remains BLOCKED until real signed
evidence is independently reviewed.

A CI candidate contract is provided at `.github/workflows/s001a-candidate-cross-repo.yml`:
it checks out the **public Evidence commit**
`8b23f4370bccdf8c7dcbd93d395b41b70d6ba1de`, verifies the runner SHA-256
`41077a6848ec1429e34cf20babcf5fb2b37ab2fbc4f675b20c840ab8f49ca360`,
runs three bounded candidate replays, checks exact functional/event digest
equivalence and **requires E3 to reject the unsigned candidate**. GitHub Actions
run `41248932917` recorded SUCCESS with all steps, including the rejection
test. **This is a CI candidate executing public code, not a foreign operator
attestation; the workflow has no proven runtime network isolation.**

The *independent* replay must separately show PASS_WITHIN_DECLARED_SCOPE,
deterministic equivalent decisions and equivalent evidence semantics, recovery
completion, negative behavior and an unchanged claim firewall.

## 3. Runner attestation

The runner creates `runner-attestation.json` and signs its canonical payload using Ed25519. The private key remains on the external runner or approved signing device and is never committed.

Required signed fields are `attestation_id`, `runner_id`, `independent`, `source_commit`, `result_hash`, `public_key_b64` and `signature_b64`.

## 4. Human review

At least two independent reviewers create `reviewers.json`. Each reviewer binds the same source commit, evidence hash and replay result hash, declares `independence: true`, decides `APPROVE` and signs their canonical entry with Ed25519.

A reviewer must inspect the fixture, commands, output, negative cases, recovery path, hashes, runtime and limitations. A signature without substantive inspection is not sufficient evidence.

## 5. Validation

```bash
python3 scripts/validate_external_evidence_bundle.py bundle \
  --min-reviewers 2 \
  --output external-evidence-validation.json
```

The command must return zero and report `VERIFIED_FOR_G2`. A successful report means the bundle is eligible for G2; it does not mutate repository state.

## 6. G2

```bash
python3 scripts/evaluate_g2.py \
  external-evidence-validation.json \
  --output g2-decision.json
```

G2 passes only when the external replay, signed human review, hashes, claim firewall and assurance predicates are all verified. The G2 output must retain `oneA: false` and `promotion: BLOCKED`.

## 7. Staging handoff

After G2 passes, an authorized operator may request the protected `staging-rls` workflow in `Castuo-system`. That environment must enforce reviewers, protected branches and secrets outside the repository. The RLS-001 integration job must run against an isolated real staging endpoint and publish JUnit and console artifacts.

A staging run is operational validation within its declared endpoint scope. It is not production authorization. Any missing environment, reviewer, endpoint, secret, artifact or rollback reference blocks the handoff.

## Acceptance table

| Predicate | Acceptance condition |
|---|---|
| Frozen source | Exact commit and rollback reference are recorded |
| Fixture integrity | SHA-256 matches the committed fixture |
| Replay | PASS_WITHIN_DECLARED_SCOPE with equivalent decisions and semantics |
| Independence | Runner identity and two human reviewers are external to the authoring path |
| Attestation | Ed25519 signature verifies over canonical payload |
| Review | Two distinct signed APPROVE entries with matching hashes |
| Claims | Production and commercial claims are false |
| G2 | Read-only evaluator returns PASS |
| Staging | Protected environment and real RLS-001 execution are available |
| Promotion | Remains BLOCKED until a separate AuthorityObject and decision |


### Three-repository synthetic contract verification (31 October 2026)

The same candidate CI workflow now pins **Agro Edge**
`a0639d6a234807c4f323d6e4a7b786cda9fd51e2` and **Evidence**
`8b23f4370bccdf8c7dcbd93d395b41b70d6ba1de` by exact Git commit.
`scripts/check_joint_candidate.py` creates three synthetic telemetry events through
Edge, exports a real canonical `events.jsonl` with chain and SHA-256 manifest,
verifies that package using the Edge verifier, and proves that a changed
event is rejected. The **actual exported events.jsonl** is then supplied as
the Evidence S-001A replay fixture. E3 checks three matching functional and
event hashes, fixture digest binding, and rejection of unsigned evidence.

GitHub run `41249634376` completed **SUCCESS** on E3 commit
`c3e4cf2d8c2d09d3684ddc7fd892d8e927a3258c`; its log reports
`SYNTHETIC_TRIPLE_REPO_CANDIDATE_ONLY`,
`tampered_pack_rejected=true`, `equivalent=true`,
`reviewers=0`, `G1/G2=BLOCKED`, `promotion=BLOCKED`.
The five workflows for that exact commit completed successfully.

**Acceptance limit:** this proves one cross-repository *synthetic* contract,
not unattended field transport, production identity, independence of the
external reviewer, offline host isolation, signatures, regulatory compliance
or permission for GO. A second qualified operator must run the separate
signed acceptance path and two real humans must independently review it.
