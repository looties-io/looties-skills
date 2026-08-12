---
name: ground-truth
description: Use when a finding from code reading, static analysis, an audit or an LLM review needs to be confirmed against the running system before anyone acts on it. Covers proving whether a suspected bug is actually happening, since when, and how far it reaches; validating a destructive schema or config change inside a transaction that is rolled back; catching deployed-versus-repository config drift; and diagnosing scheduled jobs that report success while doing nothing. Use when asked "is this actually happening", "is this a real problem or a theoretical one", "why did the cron not run", "the job says it succeeded", "check production", "how long has this been broken", or when triaging an audit whose severities are guesses.
---

# Ground Truth

A finding from reading code is a **hypothesis with a severity attached to it**. The running system is
the only thing that can tell you whether it is a risk, an outage, or nothing at all. That difference
routinely spans three severity levels, in both directions.

The point of this skill is not "test in production". It is that a class of defect is *undetectable*
from the repository, because the repository is an input to the deployed state and not a copy of it.

## The three questions

For any finding, answer these before assigning a severity or writing a fix:

1. **Is it happening?** Not "could it happen". Find the effect in the data, or find the absence of
   the effect that should be there.
2. **Since when?** A date turns "risk" into "outage", and it tells you the size of the backlog you
   are about to create by fixing it.
3. **How far does it reach?** Which rows, which users, which money, which downstream jobs.

A finding that survives all three unchanged was worth reading the code for. Most do not survive
unchanged.

## Technique 1: prove it on the real state, inside a transaction you roll back

Before applying a schema change, a permission change, or a bulk update, apply it to the **real
current state** inside an explicit transaction and roll back. This validates against the actual
constraints, the actual data distribution and the actual permissions, none of which your local copy
reproduces faithfully.

```sql
BEGIN;
  -- the change exactly as it will ship
  -- then the assertions: counts, permissions, a representative query
ROLLBACK;
```

Rules that make this safe rather than reckless:

- The rollback is written **before** the change, never added afterwards.
- No statement in the block may have an effect outside the transaction (no notifications, no
  external calls, no autonomous transactions).
- Assert inside the block. A rolled-back transaction that printed nothing proved nothing.
- Never do this against a system where a long-held lock is itself the incident.

## Technique 2: schedulers lie, so cross-check the credential

A scheduler's own log records that it **dispatched** the call. It does not record whether the target
accepted it. A job whose target answers 401 on every run shows as "succeeded" indefinitely.

This produces the most durable class of silent failure: a feature that has never worked once, with a
green scheduler log and no alert. When you cross-check, you find things that broke months ago.

The cross-check has three parts, and you need all three:

1. **What credential does the scheduler actually send?** Read the job definition, including the
   secret it resolves. Not the documentation of the job.
2. **What credential does the handler actually require?** Read the guard in the handler.
3. **Do they match?** A mismatch means every run has failed since the day one of the two changed.

Then confirm from the transport layer's own response log, not the scheduler's. Most platforms have
one (the HTTP extension's response table, the queue's dead-letter, the gateway's access log). That
log holds the status code the scheduler did not check.

Finally, and most cheaply: **query for the absence of the effect.** If the job is supposed to write
rows, count them by day. A flat zero since a given date is the whole story, and it takes one query.

## Technique 3: the repository is a deploy input, not the deployed state

Any setting that lives both in your repository and on a platform will drift, because the platform
can be changed from a console, from an older checkout, or from another person's machine, and nothing
reconciles it afterwards.

So for anything security-relevant, add a check that reads the **deployed** value and diffs it against
the declared one. Two constraints, both load-bearing:

- **Read only.** Never invoke a live endpoint to discover its behavior; you will fire side effects.
- **Run it on a schedule, not in the per-commit gate.** It needs network and credentials that
  pre-commit hooks do not have. A gate that is flaky or routinely skipped is worse than no gate,
  because it launders the absence of checking into a green tick.

The generalization: **drift that accumulates outside the repository is only visible from outside the
repository.**

## Technique 4: measure the rate, then predict the date

For anything that grows (a table, a queue, a log, a cache, a cost line), a snapshot tells you almost
nothing and a rate tells you everything. Take two measurements, derive growth per day, and
extrapolate to the threshold.

This converts a vague concern into a falsifiable claim, and the claim is often startling: in one
incident, a growth rate of about 6 MB/day against a 256 MB buffer predicted saturation at day 41,
which landed on the exact date of the first alert. That match is what proved the diagnosis, and it
also gave the deadline for the fix.

Corollary: when a system's own statistics say a resource is healthy while the measured rate says
otherwise, trust the rate. Statistics that feed automatic maintenance can be wrong in a
self-perpetuating way, where the wrong statistic prevents the maintenance that would correct it.

## Technique 5: hunt swallowed errors by looking for missing effects

A handler that catches an error per item, continues, and returns success at the end is invisible to
every monitor you have. The run is green, the log is quiet, and the work never happened.

You cannot find these by searching for errors, because there are none recorded. Search for the
missing effect instead:

- Rows that should exist and do not, grouped by day.
- A counter that should be non-zero and is flat.
- A downstream state that nothing ever advances out of.
- A provider-side log (mail, payments, storage) with fewer records than your side claims to have sent.

Then fix the reporting as well as the bug. A per-item failure must change the run's outcome or
increment a counter that someone watches, otherwise the next instance is equally silent.

## Technique 6: let live evidence move severity in both directions

The output of this skill is a re-scored finding list, and honesty requires that it moves down as well
as up:

| Static reading said | Live evidence says | Result |
|---|---|---|
| "Credential mismatch is a risk" | Every run has 401'd since April | Outage, not risk. Escalate. |
| "This query could be slow" | It runs twice a day on 40 rows | Close it. |
| "Unreachable branch" | It is the only branch taken in production | Rewrite the analysis, not the code. |
| "Race condition is possible" | Two matching rows exist today | Reproduce from those rows. |

Record the evidence next to the finding. A severity with no query behind it is an opinion, and it
will be re-litigated in three months.

## Safety rules

These are non-negotiable regardless of how urgent the question is:

- Read-only by default. Any write is inside a transaction you roll back, or it is a deliberate,
  announced change and no longer this skill.
- Never invoke an endpoint to observe it. Invoking is a side effect.
- Never copy production data into a scratch file, a test fixture, an issue, or a commit message.
  Report shapes, counts and dates, never the rows.
- Prefer a query that counts to a query that lists. You almost always need the count.
- Know the cost of your query before running it on a live system, and bound it.

## Verification

You are done when the finding list carries, for each entry: the query or log that proves it is
happening, the date it started, the scope in counts, and a severity that was set after that evidence
rather than before it.

## Related

- `endpoint-surface-map`: the declared-versus-deployed check applied specifically to who may call
  each endpoint.
- `legacy-code-review`: where these findings usually come from, and how to inventory them without
  freezing them into tests.
