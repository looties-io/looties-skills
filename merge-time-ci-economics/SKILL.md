---
name: merge-time-ci-economics
description: "Use when a GitHub Actions bill or minutes quota is too high, when CI jobs fail within seconds for no code reason, when a pull request stays blocked while every visible check is green, when agents open many pull requests, or when choosing which events start CI. Reconstructs billed minutes per workflow and trigger from the Actions API, groups cost by cause (duplicate runs, long-lived release pull requests, informational jobs, one-minute minimums, rarely needed heavy suites), then redesigns CI to run once at merge time behind a local pre-commit gate, with a draft-to-ready trigger, required checks, auto-merge, diff-scoped proofs backed by a scheduled run and advisory checks that never block. Triggers include \"our Actions bill exploded\", \"we ran out of CI minutes\", \"spending limit\", \"merge blocked but all checks are green\", \"CI runs on every push\", \"which jobs should be required\". Not for speeding up or de-flaking tests, nor for reviewing agent pull request content (use agentic-peer-review)."
license: MIT
metadata:
  author: Looties
  version: "1.0.0"
---

# Merge-Time CI Economics

CI minutes are spent per **trigger**, not per change. Most oversized bills come from proving the same
commit several times (on the branch push, on the pull request, again on the merge into the integration
branch, again on the release pull request) and from paying for checks that can never change a merge
decision. When a local hook already checks every commit, CI has exactly one job left: prove the commit
that is about to merge. Run it once, at that moment, and make the merge wait for it.

This matters more once agents open pull requests. An agent pushes often, in small increments, and every
push on a naive setup buys a full CI run that nobody reads.

The skill has two halves: **measure** (steps 1 to 4) and **redesign** (steps 5 to 10). Do not skip the
first half. The fix for a bill you have not decomposed is usually a cache tweak that barely moves it.

## Quick reference

| Intent or symptom | Go to | Look at |
|---|---|---|
| Bill or quota too high, cause unknown | Steps 1-3 | `scripts/actions-minutes.sh` output grouped by cause; ruled-out hypotheses |
| Deciding whether CI can move to merge time | Step 4 | What the pre-commit hook runs; what runs only in CI today |
| Writing or reviewing the workflow YAML | Step 5 | [`references/workflow-skeleton.md`](references/workflow-skeleton.md) sections 1-3 |
| Setting required checks and auto-merge | Step 6 | Skeleton section 4; `rules/branches/BRANCH` to confirm enforcement |
| Agents opening and merging pull requests | Step 7 | Draft, ready, `--auto`, undo-and-ready after a push |
| Keeping the design from regressing | Step 8 | Skeleton section 5 (guard test) |
| Choosing the budget and recording trade-offs | Step 9 | Estimate formula; decision record |
| Merge blocked while every visible check is green | Pitfalls | Required checks absent from the head commit |
| Every job fails in about three seconds | Pitfalls | Check-run annotations, not YAML |
| A branch turned red with no commit | Step 10 | Calendar or live-service dependent required check |

## Step 1: reconstruct the bill from the jobs, not the invoice

The invoice tells you the total. It does not tell you which trigger, workflow or job spent it, and the
billing endpoints need a token scope (account-level `user` scope, or organization admin) that a CI or
agent token usually lacks. The Actions API has everything you need anyway:

- Hosted runners bill **each job separately, rounded up to the whole minute**. A 12-second job costs one
  minute. Sum `ceil(completed_at - started_at)` per job, never per run.
- Re-run attempts bill again; fetch jobs with `filter=all`.
- Skipped jobs never receive a runner and bill nothing.
- Cancelled jobs bill for the time they ran.
- Private repositories apply runner OS multipliers (Windows and macOS cost several times Linux); public
  repositories on standard runners are free. Check the runner labels before trusting a total.

Run [`scripts/actions-minutes.sh`](scripts/actions-minutes.sh) `OWNER/REPO 30`. It is read-only (GET
requests through `gh`) and prints billed minutes by workflow and event, by job, by branch, the jobs that
paid the one-minute minimum, and the jobs that failed in under ten seconds. Keep its `jobs.jsonl`: you
will reuse it in step 9 to estimate the redesign.

Also collect step durations for the slowest job over about ten successful runs (`gh run view <id>
--json jobs`). You need to know which step is the heavy one before you can move it.

## Step 2: group the cost by cause

Totals by workflow are not actionable. Totals by **cause** are. Tag every block of minutes with one of
these:

| Cause | Signal in the data | Typical fix |
|---|---|---|
| CI runs twice per change | Same workflow billed on `pull_request` and on `push` to the integration branch, similar run counts | Drop the `push` trigger |
| Every push to a PR re-runs everything | Many `pull_request` runs per merged PR | Run on one event that means "merge now" |
| Long-lived release PR | One branch pair (integration to production) with dozens of runs | Same trigger rule; the release PR runs once when it is attempted |
| Informational work at merge time | Scores, reports, audits inside a blocking job, whose results cannot block | Move to a schedule |
| One-minute minimum | Several jobs averaging 10 to 40 seconds each | Merge them into one job |
| Heavy proof that rarely applies | One step of several minutes that only a small fraction of diffs can affect | Scope it by diff, back it with a scheduled unconditional run |
| Platform-managed scanning | Minutes from a workflow you never wrote (default code scanning, dependency graphs) | Decide explicitly; it sits outside your trigger rules |

Write the numbers into the table. In one audit of a single private repository: about **8,500 billed
minutes in 30 days**, of which pull-request runs were about 4,950, pushes to the integration and
production branches about 2,980, and the single long-lived release pull request alone about 1,110. Five
static jobs of 10 to 40 seconds each billed about 1,500 minutes together, roughly two minutes of real
work per run paid as five.

## Step 3: write down the hypotheses that did not hold

Before redesigning, record what you checked and ruled out, with the evidence. Otherwise the next person
(or agent) spends a day re-trying the obvious knobs. Common ones:

- **Expensive runner OS.** Check the labels column. In the audit above every job was Linux.
- **Missing cache.** Check `setup-*` steps for `cache:`. It was already on.
- **Superseded runs not cancelled.** Check for `concurrency` with `cancel-in-progress`. It was already
  on, and had already saved several hundred minutes.
- **Hung jobs.** Check the longest job. Nothing hung, so timeouts alone would have saved nothing.
- **Docs-only commits.** Count them. Path filters would have saved little, and some checks must still run
  on docs.

A ruled-out hypothesis is a finding. Put it in the record.

## Step 4: confirm the local gate before moving CI

Merge-time-only CI is safe **only if** every commit is already checked locally. Read the pre-commit hook
(or its equivalent) and list what it runs: lint, typecheck, unit tests, the fast static scans. Anything
that runs only in CI today (database replay, end-to-end tests, secret scanning over history) will now run
once per merge instead of once per push. That is the point, but say it out loud in the record.

If there is no local gate, stop here. Build the hook first; reducing CI without it just removes checks.

## Step 5: redesign the triggers

The rules, each with the reason it exists:

1. **No `push` trigger on any workflow.** The merge commit was already proven as the pull request's
   merge result. A push to the integration branch re-proves it for nothing.
2. **One pull-request event that means "attempt the merge".** Use `pull_request` with the single type
   `ready_for_review`. A draft pull request starts nothing; marking it ready starts the full run once.
   Pushes to a ready pull request (`synchronize`) start nothing either.
3. **Never gate jobs on draft status inside a broader trigger.** A job skipped by an `if:` reports a
   **passing** required check. If the workflow listens to `opened` or `synchronize` and skips jobs while
   the PR is a draft, marking it ready and merging immediately can merge on the skipped result.
4. **Do not use `workflow_dispatch` to satisfy a pull request.** A dispatched run can be green on the
   exact head commit and still not count: in the observed case the pull request's status rollup listed
   only other apps, and the merge was refused. Keep dispatch for checking a branch directly.
5. **Merge small jobs into one.** Each job pays checkout, setup and the one-minute minimum. Add a step to
   an existing job rather than creating a job, unless it needs different services or permissions.
6. **Move informational checks to a schedule.** If a check cannot block a merge, it does not belong at
   merge time. A daily run against the integration branch gives the same trend for a fraction of the cost.
7. **Scope expensive proofs by diff, and back the scope with a scheduled unconditional run.** Compute
   the scope from the merge base, from a list the proof itself declares (so it cannot drift), and keep a
   manual input that forces it. The weekly run catches whatever the scope rule misses.
8. **`timeout-minutes` on every job, `concurrency` with `cancel-in-progress` keyed on the ref.** Neither
   saves much on a healthy repo; they cap a hung job (the default limit is six hours) and a re-attempt.

A skeleton implementing all of this, plus the ruleset payload and a guard test, is in
[`references/workflow-skeleton.md`](references/workflow-skeleton.md). Read it when writing or reviewing
the YAML.

**Scope rules: prefer narrow and structural.** In one repository a proof taking about five minutes was
scoped by the objects it exercises. Replayed over 58 past merges, the narrow rule selected 3. A broader
identifier match selected 5, and the two extra hits were SQL comments. Exclude broad fixture tables that
almost every change names, and let the scheduled run cover them.

## Step 6: make the merge wait for the run

Without enforcement, merge-time CI is a suggestion.

- **Required status checks** on the integration branch (a ruleset or branch protection), naming each job
  exactly as its check run appears (the job `name:`, not its key, when a name is set).
- **Repository auto-merge enabled**, so `gh pr merge --auto` waits for those checks.
- **Every new required job must be added to the required list**, or auto-merge will not wait for it.
- **A bypass list** limited to administrators if direct pushes to the integration branch must stay
  possible.
- **Every branch you merge into with `--auto` needs required checks.** On a branch with none, auto-merge
  merges a mergeable pull request at once, before the run that marking it ready just started.
- **Verify enforcement, do not assume it.** Rulesets and protection on private repositories depend on the
  plan. In one case a ruleset existed with required checks and no bypass actor, and non-merge commits
  still reached the branch: it was not enforced on that account's plan. Push a test commit, or inspect
  `gh api repos/OWNER/REPO/rules/branches/BRANCH`.

## Step 7: give agents one procedure

The trigger design only works if every contributor, human or agent, attempts merges the same way.
Write it into the repository's agent instructions:

```bash
gh pr create --draft --base <integration> --title "..." --body "..."   # starts nothing
# push every remaining commit first: CI proves the head commit only
gh pr ready <n>                                                          # starts the one full run
gh pr merge <n> --auto --merge --delete-branch                           # merges when required checks pass
gh run list --workflow ci.yml --event pull_request --branch <branch> --limit 1
gh run watch <run-id> --exit-status
```

After any new push to a ready pull request, the new head has no checks and the merge stays blocked. Restart:

```bash
gh pr ready <n> --undo && gh pr ready <n>
gh pr merge <n> --auto --merge --delete-branch   # returning to draft disarms auto-merge; re-arm it
```

A red run is an expected outcome, not an incident: fix locally, push, restart. Never `--admin`.

## Step 8: pin the design with a test

The design is one careless YAML edit away from the old bill. Add a test that parses every workflow and
asserts: no `push` or `pull_request_target` trigger anywhere; `pull_request` only in the merge workflow
and only with `ready_for_review`; every job has `timeout-minutes`; the scoped proof keeps its scheduled and
manual override conditions. See `impossible-by-design` for why the rule must fail a build rather than
live in a README.

## Step 9: estimate, compare with the budget, record the trade-offs

Estimate before shipping, from the step 1 data. The step 2 table is measured; this number is an
inference from it. Label it as an estimate everywhere it appears.

```
monthly ~= merges_per_month * minutes_per_merge_run * (1 + retry_rate)
         + sum(scheduled_runs_per_month * minutes_per_scheduled_run)
         + platform-managed scanning
```

In the audit above the estimate was about 1,700 minutes per month at the observed 69 merges, against a
3,000-minute budget. Code scanning in default setup billed about 12 minutes per analysis and ran on its
own triggers, so it was listed separately as something to switch off or budget.

Record the trade-offs in a decision, so nobody rediscovers them as bugs:

- Commits pushed directly to the integration branch are not checked by CI until the next run.
- A failure the local hook misses surfaces at merge time, not at push time.
- A pull-request run tests the synthetic merge with the target as it was then. If the target moves, the
  merge result is not re-proven unless you require up-to-date branches (which costs a run per update).
- The scoped proof can miss a change that the scope rule does not see; the scheduled run bounds how long.

Then re-run the script after two to four weeks and compare with the estimate.

## Step 10: advisory checks never block

A check that can go red **without any commit** does not belong among required checks. The classic case
is a documentation freshness check with a review-after date: the date expires on its own, and the
integration and production branches turn red overnight, blocking every merge for a reason unrelated to
the code. In one repository this happened during a release; the check was demoted to advisory (warnings
and CI annotations, exit 0, with a `--strict` flag kept for deliberate cleanups).

Rule: a required check must be a function of the commit. Anything that depends on the calendar, on a live
external service or on a score threshold is advisory or scheduled.

## Pitfalls

| Symptom | Cause | Fix |
|---|---|---|
| Merge blocked, auto-merge never fires, `gh pr checks` all green | PR opened ready (`opened` is not `ready_for_review`) or pushed to after ready, so required checks never started on the head commit; `gh pr checks` lists only checks that exist (apps, code scanning) | `gh pr ready <n> --undo && gh pr ready <n>`, then re-arm `gh pr merge <n> --auto` |
| Dispatched run green on the head commit, merge still refused | Runs from `workflow_dispatch` were not attached to the pull request in practice; the status rollup showed only other apps | Restart through `ready_for_review`; keep dispatch for checking a branch |
| Every job fails in about three seconds, nobody touched YAML | Usually billing: read `gh api repos/OWNER/REPO/check-runs/<id>/annotations`. One case said payments had failed or the spending limit was reached; nothing ran or billed | Owner raises the limit or fixes payment. A plan upgrade on an organization did nothing while the repository still belonged to a personal account |
| Integrations silent after moving the repository between accounts | Secrets, environments and rulesets moved; installed apps (deploy previews, database integrations) and a hosting project's Git link did not | Grant each app the repository again, reconnect the Git link, probe with a push |
| Red check appears after an auto-merge, then blocks a release step | A non-required check (often code scanning) finished after the merge | Read all checks, not only the required ones, before calling a pull request green |
| Budget met by moving a blocking security check to a schedule | Policy change disguised as optimisation | Only informational checks move freely; anything else needs an owner decision |

## Safety rules

- The measurement is read-only. The script issues GET requests only.
- Never merge with an admin bypass or `--no-verify` to get around the new flow. A merge is valid only when
  CI is green on the exact head commit.
- Change triggers and required checks in the same change, and verify enforcement right after; a window
  where jobs changed name but the required list did not blocks every merge, and the reverse lets merges
  through unchecked.
- Do not disable platform-managed scanning or change billing settings yourself; list them for the owner.

## Verification

You are done when:

- The cost table from step 2 has numbers for each cause, and the ruled-out hypotheses are recorded.
- The local gate is listed, and nothing blocking was dropped without an owner decision.
- A test pins the trigger rules and timeouts, and it fails when you add a `push` trigger.
- A draft pull request started nothing, marking it ready started exactly one run, a push afterwards left
  the merge blocked, and the undo-and-ready restart plus re-armed auto-merge merged it on green.
- A skipped or dispatched run cannot satisfy the required checks (confirmed on a real pull request).
- The estimate, the budget and the trade-offs are written in a decision, with a date to re-measure.

## Related

- `impossible-by-design`: turning "do not add a push trigger" into a test that fails the build.
- `ground-truth`: confirm a suspected cause in live data before acting on it; the billed-minutes
  reconstruction is the same idea applied to a bill.
- `agentic-peer-review`: how agent-authored pull requests are reviewed before the merge attempt this
  skill prices.
- `field-web-performance`: why lab performance scores are informational and belong on a schedule.
