# Audit and hardening record templates

Read this at Step 7 (before the first fix) and again at Step 10 (before deploying). Put the records
wherever your project keeps dated evidence. The two records link to each other; neither replaces the
other.

The audit record is frozen once fixes start. Corrections to its claims (for example a fix-diff
reviewer proving one of them wrong) go into the hardening record, with a link back.

## Audit record

```markdown
# Retrospective review of <cohort>, <date>

This is a review of code and of interactions between changes, not a certification of
production. No fix, deployment, real email or real payment happened during this review.
Remediation: <link to hardening record, added later>.

**Verdict:** <one paragraph: overall quality, whether green CI was sufficient, counts per rank>.

## Scope and method

- Cohort: <N> merged PRs, <range>. Gaps: <numbers that are issues, not PRs>. Out of scope: <open
  PRs, later work>.
- Release PRs deduplicated; integration deltas read: <list>.
- Reference SHA: <sha>. Tree inspected for file:line: <sha>. Later overlapping work: <list>.
- Reviewers: <domains>, isolated contexts, one coordinator. Documents marked stale were not
  treated as evidence.
- Reproductions: <kinds>, all with fake data, outside the product tree at <scratch location>.
- CI per PR: <how many showed the full job set on the merged SHA; exceptions and what they do
  and do not prove>.

## Priority findings

### F<n>, P<rank>, <one-line title>

**Introduced by <PR>, shipped by <release>.** Location: `<file:line>`.

<Mechanism, two to five sentences. What input, what path, what effect.>

**Proof:** <what was run, against which real code path, and what it showed>.
**Limits of the proof:** <what this does not demonstrate>.
**Intent source:** <spec, provider documentation, caller, decision>.
**Minimal correction:** <the smallest change that closes the root cause, and the existing
mechanism it should reuse>. Test required: <the assertion that must hold>.

## Other findings

<Same shape, P2 and P3.>

## Per-PR verdicts

| PR / release | Verdict after integration |
|---|---|
| <pr> | <sound, with reason / sound with caveat / defective: F<n>> |

## Known limits kept visible

<Limits already documented elsewhere, linked, explicitly not counted as new findings.>

## Checks run and scope of evidence

- <command or run>: <result>. <what it covers and what it does not>.
- Expected failures: <reproductions that fail against current code, by finding>.
- Not done: <full replays, concurrency tests, live permission audits, real provider calls>.

## Proposed order of work

1. <P1 findings, grouped when they share a root cause>
2. <...>
```

## Hardening record

```markdown
# Hardening from the review of <cohort>

This record describes the corrections and their validation. The audit record
(<link>) keeps the pre-fix reproductions. Delivery: <branch flow and the rule that CI must pass
on the exact SHA before merge>.

## Corrections

| Finding | Correction and proof |
|---|---|
| F<n>, <title> | <what changed, which existing mechanism was reused>. <Red on pre-fix code, green after>. <Negative control if the proof is a canary>. |

## Fix-diff review

<Who reviewed (independent of the implementer), what they found, how each was closed, with
red/green evidence. Any audit claim they proved wrong, stated plainly.>

## Verification

- Full gate: <command>, <counts>, on the declared runtime version.
- Replays and races: <disposable environment, counts, red control before the fix>.
- Canaries: <what was faked, what refused, the negative control that succeeded with the old
  configuration>.

## Delivery contract

1. <Schema changes, in order, dry-run on real state in a rolled-back transaction first.>
2. <Units that must ship with or right after the schema change, and why.>
3. <Every unit importing a changed shared module, transitively, including dynamic imports.>
4. <Workers or artifacts built outside the main pipeline, rebuilt from the merged commit.>
5. <Frontend promotion.>

What this change cannot repair: <sealed batches, lost values, messages not re-sent in bulk>.

## Post-deploy evidence

| Unit | Version before | Version after | Auth flag (declared = deployed) |
|---|---:|---:|---|

- Entrypoints read back identical to the merged commit: <count>.
- Unauthenticated probes: <endpoint> 401, <webhook without signature> 400.
- Live inventory versus manifest: <result>.
- Schema invariants after migration: <result>.
```
