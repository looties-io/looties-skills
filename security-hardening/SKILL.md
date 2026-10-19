---
name: security-hardening
description: "Use for a scoped security validation campaign or scheduled cumulative hardening of a repository: map trust boundaries, construct an isolated synthetic test matrix, execute real code paths, reproduce findings, fix authorized defects and verify remediations. Not a production penetration test or permission to contact third-party systems."
license: MIT
metadata:
  author: Looties
  version: "1.0.0"
---

# Security Hardening

An inventory describes intended protections. Only an executed, reproducible matrix shows which protections work. Carry confirmed defects through authorized remediation; preserve the baseline evidence.

## Route the work

| Situation | Action |
|---|---|
| Periodic campaign | Read the harness's frozen cohort, integrated revision and open findings |
| Missing architecture | Map entrypoints, authority and trust boundaries before testing |
| Unverified protection | Mark unvalidated, name the missing test and owner |
| Reproduced defect | Freeze baseline evidence, fix within mandate, rerun the reproduction |
| Restricted operation | Block that action and its dependents; continue independent work |

## Procedure

1. Read repository instructions and the applicable existing skills. Use `agentic-peer-review` for cumulative history, `harness-testing` for real entrypoint tests and `impossible-by-design` for recurring failure classes. Avoid copying their workflows into a new competing checklist.
2. Inventory authentication, authorization, tenant isolation, agent/tool permissions, secrets, execution isolation, input validation, emails and attachments, web content, connectors/APIs, errors/logging, administrative operations, backups and restoration. For each, record expected behavior, security assumptions, real enforcing code and existing tests.
3. Build the matrix before execution. Cover positive and negative authorization, cross-tenant access, malformed inputs, denied tools, sensitive-action confirmation, recovery and non-regression. Treat emails, documents and web pages as untrusted data: test that embedded instructions cannot acquire privileged authority. Include interactions across the cohort and repository boundaries, not just individual PR diffs.
4. Prepare an isolated lab using fake users, organizations, documents, messages, connectors, services, secrets and verified test backups. Use synthetic markers to detect unauthorized access or disclosure. Verify the actual endpoints and credentials point to the lab. No production writes, real emails, third-party probing or customer data. Establish these prerequisites before unattended execution.
5. Execute the real code paths with existing tools. Split independent domains across fresh reviewers only when delegation is permitted. Capture command, revision, observed result and limits; correlate test output with logs. Preserve a domain's baseline before changing its protections. A missing tool, unavailable environment or incomplete run is unvalidated, never passed.
6. Classify findings as confirmed vulnerability, configuration defect, coverage gap or theoretical risk. Each needs component, violated requirement, isolated reproduction, expected/observed result, risk, probable cause, minimal correction and regression check. Scanner alerts alone are not confirmation.
7. Immediately implement authorized, reproduced corrections after freezing their baseline. Use micro PRs with explicit dependency order. An L2 plan already approved for this work is not a reason to request the same approval again. Record truly restricted actions as targeted blockers; keep progressing elsewhere.
8. Re-run the failing reproduction and legitimate neighboring cases. Test the deployed binary/configuration or disposable runtime when mocks cannot represent grants, parser versions, isolation or restart behavior. Obtain a fresh independent review when permitted; a self-review must never be labelled independent. Production deployment follows its separate authorization rules.

## Evidence and completion

Reuse existing equivalents of `SECURITY-CONTROLS.md`, `SECURITY-TEST-MATRIX.md`, `SECURITY-FINDINGS.md` and `SECURITY-REMEDIATION.md`; do not create duplicate authorities. Add focused automated regressions to the existing CI entrypoint.

Record every matrix cell as passed, failed or unvalidated with evidence. Freeze baseline reports; append remediation evidence separately. Link open findings to owners and next actions, and decisions to the existing decision register. An assessment can finish while a restricted remediation remains open, but the campaign must not claim security completion until that debt is resolved or explicitly accepted by the responsible human.

## Verification

- Baseline matrix executed at its recorded revision, with unavailable controls explicitly identified.
- Confirmed defects reproduced with synthetic data and corrected within the mandate.
- Regression checks detect the old failure and permit the intended behavior.
- Every remaining finding has an owner, next action and precise blocker if needed.
- Harness campaign state retains the evidence and open remediation debt across sessions.
