# Reviewer prompts and adjudication rubric

Read this before starting the reviewer agents (Step 3) and again before adjudicating (Step 5).
The templates are runtime-neutral: paste them into a sub-agent, a separate CLI session, or any agent
runner that starts each reviewer with an empty context.

Fill the placeholders in angle brackets. Give every reviewer the same cohort block and the same
output schema. Never paste one reviewer's output into another reviewer's prompt.

## Shared cohort block

```
You are one of several independent reviewers. You will not see the others' work.

Cohort: <list of merged PRs or commit range>, deduplicated: <release PRs skipped>.
Integration deltas to read as well: <changes present only in release merges>.
Reference SHA: <sha>. Judge everything at this commit. File:line must point to <sha or tree>.
Out of scope: <open PRs, later work, documented known limits with links>.

Rules:
- Read the diffs, then the callers and the code each change now reaches.
- Look for defects created by COMBINING changes in the cohort, not only inside one PR.
- A claim with no file:line is not a finding.
- Do not derive expected behavior from the code under test. Name the external source
  (spec, provider documentation, caller, schema, product decision).
- Documentation marked stale or audit-required is not evidence of current behavior.
- Do not modify the repository. You may write scratch reproductions under <scratch dir> only.
- Do not contact production or any real provider.
```

## Required output schema

Every reviewer returns only a list of findings in this shape (JSON, YAML or a table, but these
fields and no others):

| Field | Content |
|---|---|
| `id` | reviewer prefix plus number, for example `SEC-3` |
| `claim` | one sentence, stated as a fact that can be false |
| `location` | `file:line` (or range) at the reference SHA, plus the PR that introduced it |
| `mechanism` | how the defect happens, in two to four sentences |
| `intent_source` | what says the current behavior is wrong |
| `reproduction` | the smallest test, canary or browser run that would fail today, and where it would live (outside the product tree) |
| `severity_guess` | P1, P2 or P3, marked as a guess |
| `confidence` | high, medium or low, with one line on what would change it |
| `interaction` | other PRs or helpers involved, or `none` |

Also return a short per-PR verdict (sound, sound with caveat, defective) with one reason each. A
reviewer that finds nothing still returns verdicts.

## Domain brief: security and money

```
Your lens: authorization, secrets, injection, and anything that moves, holds or withholds money.

For each change ask:
- Who can call this, with which credential, and does the check match what callers send?
- What input does this accept that a member controls, and which helper does it flow into?
  What did that helper assume about its inputs (escaping, URL trust, length, type)?
- Is any authorization expressed as an instruction (to a model, in a comment, in a doc) rather
  than a permission the runtime enforces?
- Can a secret on disk or in env be reached by a subprocess, tool or model that handles
  untrusted input?
- For money: partial amounts versus totals, refunds and disputes after earlier refunds, currency,
  idempotency keys that change when the payload changes, state that must survive a restart.
- For provider webhooks: signature check, replay, out-of-order delivery against terminal states.
```

## Domain brief: backend and data

```
Your lens: migrations, grants, triggers, concurrency, retries and silent failure.

For each change ask:
- Which roles gain or lose privileges? Does any code path now run as a role that lost one?
- Which triggers fire on the rows this migration or backfill touches, including maintenance
  triggers such as updated_at and activity stamps?
- Is there a read-then-write that a concurrent change can interleave?
- Does an error path report success (caught per item, result object ignored, 200 returned)?
- On replay or retry, which side effects are skipped because a record already exists?
- Which deployable units import a changed shared module, directly or dynamically?
- Would the change boot? (Mass edits, generated imports.)
```

## Domain brief: frontend and accessibility

```
Your lens: state across navigation, async ordering, focus, keyboard, layout and copy.

For each change ask:
- When a route parameter changes, which state still belongs to the previous parameter, and
  which effects act on it (redirects, analytics, writes)?
- Can a slower earlier response overwrite a faster later one?
- Does a new dialog, sheet or menu reuse the project's accessible primitive, or re-implement
  part of it? Check focus trap, Escape, focus restoration and scroll lock.
- At the smallest supported width, does anything overflow or overlap?
- Does any new text contradict the behavior the backend now has?
Reproduce in a real browser, not only with component tests.
```

## Fix-diff reviewer brief (Step 9)

```
You are reviewing a hardening diff. You did not write it and did not see the discussion.
Inputs: the audit record (findings as reproduced before the fix) and the diff <range>.

For each finding: does the diff close it at the root, or only at the reproduced symptom?
Then, independently of the findings: what did the diff itself break or couple? Look for new
dependencies between recipients, callers or steps, fail-open error handling, and claims in the
audit record that the diff shows to be false.
Return the same schema as the first round.
```

## Coordinator adjudication rubric

Process every reviewer output in this order. The coordinator does not add its own findings in the
first pass; it judges claims.

1. **Schema check.** Reject entries missing `location` or `intent_source`. Return them to the
   reviewer once; do not reconstruct them yourself.
2. **Reference check.** Confirm the location exists at the reference SHA. If a later PR in the
   cohort already fixed it, record it as closed history.
3. **Known-limit check.** If a spec, decision or runbook already documents it as an accepted limit,
   record it as known, not new.
4. **Deduplicate by root cause.** Merge findings that share a mechanism. Keep every reviewer's id in
   the merged entry so agreement is visible.
5. **Weigh agreement correctly.** Two isolated reviewers reaching the same root cause raises
   confidence. A claim only one reviewer made is not weaker for that reason; low confidence comes
   from the reasoning, not the headcount.
6. **Route disagreements to reproduction.** When reviewers contradict each other, the reproduction
   decides. Never vote.
7. **Queue reproductions.** Every surviving entry gets a reproduction owner, a scratch location and
   a statement of what the reproduction cannot prove.
8. **Rank after proof only.** Assign P1, P2, P3 from the reproduced effect. Discard severity guesses.
   Unreproduced claims are dropped or listed as unconfirmed, never ranked.
9. **Check the verdict table.** Every PR in the cohort has a verdict. A cohort with only defects
   listed and no sound verdicts reads as a hunt, not a review.

## Severity rubric

| Rank | Reproduced effect |
|---|---|
| P1 | Money paid, withheld or refunded wrongly; authorization bypass; secret readable by an untrusted party; injection into content the system sends or renders; unrecoverable data change |
| P2 | A real user journey broken or looping; accessibility regression on a new surface; a notification that is lost without retry; a state that blocks operators |
| P3 | Cosmetic, or a hardening opportunity with no reproduced path to harm |

Raise one level when the effect is silent (nothing alerts). Lower one level when an existing,
tested mechanism already mitigates it, and name that mechanism.
