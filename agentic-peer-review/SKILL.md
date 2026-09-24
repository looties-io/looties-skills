---
name: agentic-peer-review
description: "Use when a batch of already-merged changes needs an independent second look after the fact, especially when CI was green but nobody else read the code. Runs isolated reviewer agents split by domain (security and money, backend and data, frontend and accessibility) over the last N merged pull requests or a large branch, adjudicates their findings, reproduces each one as a failing test or canary outside the product tree before ranking it, keeps a frozen audit record separate from the hardening record, fixes in priority order, sends the fix diff to a fresh reviewer, and verifies the deployment. Triggers include \"review the last ten PRs\", \"peer review what we shipped\", \"second pair of eyes on this branch\", \"audit recent merges before the release\", \"the AI wrote a lot of code this week, check it\", \"review the fix diff\". Not for taking ownership of old or untested code nobody has read (use legacy-code-review), nor for reviewing a single open pull request before merge."
license: MIT
metadata:
  author: Looties
  version: "1.0.0"
---

# Agentic Peer Review

A green CI run proves that the checks someone wrote passed on some commit. It does not prove that
anyone read the change, that the checks ran on the commit that shipped, or that two changes which
were each fine alone are fine together. When code arrives faster than people can read it (a burst
of AI-generated pull requests, a release train, a week of solo merges), the missing second look
becomes a backlog of unreviewed decisions sitting in production.

This skill is the after-the-fact second look, run by several independent reviewer agents and one
coordinator. Its value is not the number of findings. It is three disciplines that single-pass
reviews skip: **reviewers that cannot contaminate each other**, **reproduction before ranking**, and
**a fresh review of the fix diff**, followed by a deployment that is verified rather than assumed.

## Quick reference

| Intent or symptom | Go to | Look at |
|---|---|---|
| "Review what merged since X" | Step 1 | Cohort list, reference SHA, release-merge integration deltas |
| "It was all green" | Step 2 | Check rollup of each merged SHA, merge time versus CI end, runtime version |
| Starting the reviewers | Steps 3-4, `references/reviewer-prompts.md` | Domain briefs, shared output schema, cross-PR interaction questions |
| Merging reviewer outputs | Step 5, `references/reviewer-prompts.md` | Adjudication rubric: root-cause dedupe, disagreements go to reproduction |
| Deciding severity | Step 6 | Reproduction outside the product tree, stated proof limits, P1-P3 |
| About to fix | Steps 7-8, `references/record-templates.md` | Frozen audit record first, then test-first fixes reusing existing mechanisms |
| Fixes are done | Step 9 | Fresh reviewer on the fix diff; budget a second round |
| Ready to deploy | Step 10, `references/record-templates.md` | Derived order, shared-helper importers, post-deploy probes |
| A fix looks too easy | Pitfalls | Partial versus total, terminal states, stale async, triggers, grants |

## Boundary with `legacy-code-review`

The two skills overlap in spirit and differ in object. Pick by the question you are answering.

| Question | Skill |
|---|---|
| "Nobody has read this old or generated code, and it has no tests. Take ownership of it." | `legacy-code-review` |
| "These N changes merged recently. Were they right, alone and together, and is what we ship now safe?" | `agentic-peer-review` |

`legacy-code-review` owns the rule that **an assertion is never derived from the code under test**.
Every reproduction in this skill obeys it; read it there rather than here.

## The procedure

Ten steps, in order. The order matters: ranking before reproduction, or fixing before the audit
record exists, destroys the evidence you need later.

### Step 1: freeze the cohort and a reference SHA

Write down, before reading any diff:

- **The cohort.** "The last N merged PRs", "everything merged since the last release", or "this
  branch". Say the count out loud. Note gaps in numbering (numbers that were issues, not PRs) so a
  reader does not think something was skipped.
- **The reference SHA.** The integrated commit the review is judged against. If you also inspect
  a later tree (for example the current default branch), record both SHAs and say which one the
  file:line references point to.
- **What is out of scope.** Open PRs, later work that touches the same files, known limits already
  documented in a spec. A limit the team already wrote down is not a new finding.

Deduplicate release or merge PRs (a release that only carries earlier PRs adds nothing to read),
but **diff the integration delta**: changes that exist only in the release merge, such as a conflict
resolution or a last-minute commit, were reviewed by nobody. In one cohort of 21 PRs, a release
merge carried product changes that appeared in no earlier PR of the cohort.

Evaluate each finding at the reference SHA. A gap that a later PR in the same cohort already closed
is history, not an open defect.

### Step 2: treat CI as unproven, per PR

For every PR, read the check rollup attached to **the SHA that merged**, not the PR's last green
badge. You are answering two questions: which jobs ran, and did they finish before the merge.

In one audit, 20 of 21 PRs showed the three application jobs green. The 21st showed only the
static-analysis and preview-deploy checks, with no application jobs at all. Separately, a release
in the same window had merged before its CI finished (auto-merge on a branch with no required
checks). Neither fact proves the code was broken. Both prove that "it was green" is a claim to be
checked, not a premise.

Also check the runtime the evidence ran on. A test run on a newer language runtime than the one the
project declares is not evidence for the declared one; rerun on the declared version.

See `merge-time-ci-economics` for why required checks and merge-time runs are configured the way
they are.

### Step 3: split by domain across independent reviewers

Start one reviewer agent per domain, each in a fresh context, each seeing the cohort list, the
reference SHA and its own brief, and nothing from the other reviewers:

| Domain | Reads for |
|---|---|
| Security and money | authorization, secrets, injection, anything that moves or withholds money, provider webhooks, idempotency |
| Backend and data | migrations, grants, triggers, concurrency, retries, error paths that report success |
| Frontend and accessibility | state across navigation, stale async responses, focus and keyboard, responsive layout, copy |

Why isolation: a reviewer who has read another reviewer's conclusions anchors on them, and two
agreeing reviewers who shared context are one reviewer. Disagreement between isolated reviewers is
the signal you are paying for.

Why domains rather than PRs: one reviewer per PR reads each change alone, which is exactly the view
that CI already had. One reviewer per domain reads every PR through one lens, which is how
cross-PR defects surface.

Give every reviewer the same required output schema (claim, `file:line`, reproduction plan,
severity guess, confidence) so the coordinator can merge findings mechanically. The per-domain
prompt templates and the schema are in `references/reviewer-prompts.md`; read it before starting
the reviewers.

### Step 4: review interactions, not only PRs

Tell every reviewer explicitly to look for defects created by **combining** changes. They are the
class a per-PR review cannot see, because each half is correct.

The worked example: one PR restored a previously removed notification email. A shared
email-rendering helper had long skipped HTML escaping for any template variable whose name ended in
`_url`, on the assumption that URLs are trusted. The restored email passed a member-editable profile
field into a variable ending in `_url`. Neither the helper nor the restoration was wrong alone;
together, any member could inject markup (a phishing link) into an email the platform sent in its
own name.

Questions that find this class:

- What new input reaches an old helper, and what did the helper assume about its inputs?
- Which PR added a caller to code another PR changed?
- Which fix in the cohort assumed a state that another PR made possible?

### Step 5: adjudicate with one coordinator

One coordinator agent (or person) merges the reviewer outputs. It does not review code first; it
judges claims. Its job, with the full rubric in `references/reviewer-prompts.md`:

- **Deduplicate** by root cause, not by symptom. Two reviewers reporting two symptoms of one bad
  helper is one finding.
- **Check each claim against the reference SHA** and against the documented limits from Step 1.
- **Keep disagreements visible.** When the security reviewer and the backend reviewer disagree
  about a grant, that disagreement goes into the reproduction queue, not into a vote.
- **Discard severity guesses.** Severity is assigned in Step 6, after proof.

Static analysis output is input to adjudication, not a finding list. In one triage, 102 of 145 open
code-scanning alerts were a single rule firing on URL matching inside test stubs, while the one
critical issue of that review (a token column readable by the very member it authorized) appeared in
no scanner output at all.

### Step 6: reproduce before ranking

Every surviving claim becomes a reproduction **outside the product tree**: a failing test in a
temporary directory, a copy of the existing test harness, a browser run against the real component,
a canary with fake secrets, a rolled-back transaction. Nothing is added to the product while the
audit is open.

Rules:

- **Reproduce with the real code path.** The real handler behind the existing harness, the real
  template parsed by a real HTML parser, the real component in a real browser.
- **State each proof's limits in the same sentence as the proof.** "Injected markup creates two
  extra links in the rendered email; this is a phishing vector, not proof of script execution."
  "The canary ran on a newer CLI version than the deployed one." "Mocked RPCs prove neither the SQL
  locks nor the deployed grants." A proof without its limits will be read as broader than it is.
- **Drop what does not reproduce,** or keep it as an explicitly unconfirmed note. Do not rank it.
- **Use `ground-truth`** when the question is whether the defect is happening in production, since
  when, and to how many rows.

Then rank:

| Rank | Meaning |
|---|---|
| P1 | Reproduced loss or exposure: money, authorization, secrets, injection, data that cannot be recovered |
| P2 | Reproduced regression of a real user journey or of accessibility, no money or privilege impact established |
| P3 | Reproduced but cosmetic, or a hardening opportunity with no current path to harm |

In one cohort, reproduction produced three P1 findings (HTML injection, a model sandbox that could
read the worker's secret, a partial loss that zeroed a full payout) and four P2 findings (a redirect
loop, an out-of-order event, an email never retried, a modal that leaked focus).

### Step 7: write the audit record before fixing anything

The audit record holds the findings **as reproduced against the pre-fix code**: location, mechanism,
proof, proof limits, minimal correction, and the checks that ran. Write it before the first fix, and
never rewrite it afterwards. The fixes go in a separate **hardening record** with red/green evidence
and the deployment contract.

Why two records: the audit is the only place where "this failed before" is preserved. If fixes are
folded into it, nobody can later tell a reproduced defect from a speculative one, and the red half
of every red/green claim is lost. Templates for both are in `references/record-templates.md`.

Include a per-PR verdict table in the audit. Most changes will be judged sound, and saying so
explicitly (with the reason) is what makes the defects credible.

### Step 8: fix in priority order, reusing existing mechanisms

Fix P1 first, then P2. Each fix is test-first: the Step 6 reproduction is promoted into the product
test suite, observed red on the pre-fix code, then green.

Prefer the mechanism the codebase already has over a new copy. In the reference cohort, the fixes
reused the existing durable delivery log instead of adding a retry loop, and the existing accessible
modal hook instead of patching focus handling by hand. A reviewer finding that says "this
re-implements X badly" is fixed by calling X, and `impossible-by-design` is where you make calling X
mandatory.

A fix that only adds a guard where the reproduction failed is often too narrow. Ask what state
the fix assumes and test the neighbors (see the pitfalls on `!loading` and on terminal states).

### Step 9: independently review the fix diff

Send the hardening diff to a **new** reviewer that saw neither the original findings' discussion nor
the implementation session. Give it the audit record and the diff, and ask whether each fix closes
its finding, and what the fix itself broke.

This round is not optional. In the reference cohort it found a residual coupling between two email
recipients (a missing profile field for one recipient blocked delivery to the other), closed with
two more red/green tests. In another review, the fix-diff reviewer corrected a claim in the audit
itself ("no signed-in surface reads these views" was false). One team used two skeptic reviewers
per finding on this round.

Budget for it: a first review of a large feature kept 30 findings (29 fixed, one accepted), and the
review of those fixes kept 11 more (10 fixed, one accepted). Plan two rounds from the start.

### Step 10: derive the deployment order and verify after deploy

Derive, do not remember, what must ship and in what order:

1. **Schema before code** that depends on it, and code that must ship with a migration in the same
   window (a handler that inserts through a newly restricted grant fails the moment the migration
   lands).
2. **Every deployable unit that imports a changed shared helper**, transitively, including dynamic
   imports. Changing a shared email helper can mean redeploying dozens of functions that no PR in
   the cohort touched.
3. Workers and anything built outside the main pipeline, rebuilt from the merged commit.

Dry-run schema changes against the real state inside a transaction that is rolled back (see
`ground-truth`). After deploying, verify with evidence rather than exit codes:

- every listed unit's version increased, and its entrypoint matches the merged commit;
- authentication flags (for example gateway JWT verification settings) are unchanged from the
  declared manifest;
- unauthenticated probes return the expected refusal (401 for an admin endpoint, 400 for a webhook
  without a signature) and never 200 or 500;
- a live inventory of deployed units matches the repository's manifest (`endpoint-surface-map`).

Record all of it in the hardening record.

## Pitfalls from real reviews

Each of these shipped with green CI and was found by reproduction, not by reading alone.

- **A prompt instruction is not access control.** A model call was told "nothing to read or run" and
  given a sandbox labeled read-only. A fake-secret canary placed outside the job directory was still
  readable, and the real response parser passed it through into the output. The fix closed file and
  tool permissions to the job directory, and was proven by the same canary refusing the read, plus a
  **negative control**: rerunning with the old broad permission and watching the canary succeed. A
  canary without a negative control does not prove the canary can detect anything.
- **Partial assumed to be total.** Losing a card dispute on part of an order marked the entire
  remaining payout as not due. Providers allow partial disputes; the fix records the exact lost
  amount in the one shared deduction calculation.
- **Out-of-order events overwrote a terminal state.** A guard protected closed tickets, but a lost
  dispute deliberately stays open until an operator acts, so an older event arriving later rewrote
  "lost" back to "under review" and blocked closure. Webhook ordering is not guaranteed by most
  providers; protect terminal states independently of workflow status.
- **A failed send was never retried.** The provider rejection returned `{ success: false }`, which
  nothing checked, and a replay of the event found the existing record and skipped the send. Returning
  an error status alone would not fix it while the replay path skipped delivery.
- **A stale async response caused a redirect loop.** Navigating from profile A to profile B kept A's
  data while B loaded; a canonical-URL effect compared B's route to A's slug and redirected back to
  A. Adding `!loading` to the effect is not enough, because the first render after the parameter
  changes can still carry the old flag. Tie each result to the parameter that requested it and
  ignore stale responses.
- **A backfill rewrote timestamps through triggers.** A data backfill that touched one column fired
  row-maintenance triggers and rewrote `updated_at` on 325 rows and an activity timestamp on 21
  related rows, changing sitemap dates and a synced marketing property. No copy had been taken, so
  the old values were lost. Disable exactly the maintenance triggers around a backfill.
- **A green harness hid grant errors.** A fully passing harness suite covered a handler that read a table
  its database role had no grant on. The in-memory harness has no grants, so only a live probe of the
  real handler on a disposable stack showed the permission error (see `harness-testing`).
- **Mass edits passed text-based gates and failed to boot.** A scripted import insertion landed
  inside another multi-line import in 13 serverless functions. Every commit gate and a test that
  grepped source text stayed green; a local runtime returned a boot error. After any mass edit,
  parse every entrypoint and boot each changed unit once.
- **State that must survive a restart lived in memory.** A payout repair held a seller for one
  invocation; a restart or the next scheduled run would have paid against a stale ledger. The hold
  became a durable, locked row.
- **Read-then-write undid a concurrent removal.** A "remembered consent" path read an active row
  and then upserted it, so a revocation between the two was silently reversed.

## Safety rules

- Reproductions live outside the product tree, use fake data and fake secrets, and never send a real
  email or move real money. Point provider calls at fakes or at sandbox accounts verified as such
  (for example a test-mode key checked by prefix before use).
- Never copy production rows into a record, a fixture or a prompt. Report shapes, counts and dates.
- Production checks are read-only or inside a transaction you roll back.
- Do not rewrite the audit record after fixes start, and do not refresh "last verified" dates on
  documents you did not compare against evidence.
- Do not bypass hooks, weaken tests or delete gates to make the hardening pass.
- Reviewer agents get read access to the code, not credentials to production.

## Verification

You are done when:

- The cohort, the reference SHA and the out-of-scope list are written down.
- Every PR has a CI verdict read from the merged SHA's rollup.
- Every ranked finding has a reproduction that failed on pre-fix code, with its limits stated.
- The audit record exists unchanged from before the first fix, and the hardening record carries
  red/green evidence for every fix.
- A reviewer that did not write the fixes reviewed the fix diff, and its findings are closed or
  explicitly accepted.
- The deployment order included every unit importing a changed shared helper, and post-deploy
  evidence shows bumped versions, unchanged auth flags and correct refusals from unauthenticated
  probes.

## Related

- `legacy-code-review`: taking ownership of unread code, and the rule for deriving assertions.
- `ground-truth`: whether a finding is happening in production, since when, and how far it reaches.
- `impossible-by-design`: turn the recurring findings into constraints so the next cohort cannot
  repeat them.
- `harness-testing`: building the harness the reproductions reuse, and its blind spots.
- `endpoint-surface-map`: the declared-versus-deployed check used after deployment.
- `postgres-privilege-audit`: the grant and column-privilege class that harnesses cannot see.
- `provider-canary`: exact-payload canaries against provider sandboxes.
- `merge-time-ci-economics`: why CI may not have run where you think it did.
- `a11y-audit`: the full method behind the frontend reviewer's accessibility lens.
