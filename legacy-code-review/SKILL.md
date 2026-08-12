---
name: legacy-code-review
description: Use when reviewing, testing or taking ownership of code nobody has looked at in a long time, especially untested code and code an AI agent generated and then left. Covers scoping a cohort, building the caller map, adding first coverage to code that has never been executed without freezing its defects into assertions, inventorying findings with evidence, and adversarially verifying that the new tests actually hold. Use when asked to "review this legacy code", "add tests to this old module", "audit the code we inherited", "clean up AI-generated code", "we have no tests on this", "write characterization tests", or when a codebase has grown faster than anyone has read it.
---

# Legacy Code Review

Legacy no longer means old. It means **code that is in production and that nobody has read**, and
generated code reaches that state in weeks rather than years. It arrives with plausible structure,
consistent naming, and no history of anyone verifying that it does what it appears to do.

The trap is specific and it is the reason this skill exists.

## The one rule: never derive an assertion from the code under test

Writing a characterization test for untested code is how a defect gets **blessed**. You read the
handler, you assert what it currently returns, the test goes green, and the bug is now protected by
your test suite. Nobody can fix it later without arguing with CI, so nobody does.

The canonical scar: a refund handler dropped a currency unit conversion and refunded 39 cents where
3900 was owed. Its own test asserted `amount === "39"`. Green in CI for months. The test was not
missing. The test was the reason the bug survived.

So the assertions come from **outside** the code under test:

- the schema and the migrations (what the data actually permits and means)
- the callers (what they pass and what they do with the answer)
- the provider's API contract (units, required fields, idempotency semantics)
- the project's own standards and specifications
- the domain rule as a human states it, written down before you open the file

And where the code disagrees with what you derived, **report the disagreement instead of asserting
it**. That inventory is the deliverable of the pass. Not the fix.

## Step 1: scope a cohort, not a file

Pick a set with a shared reason to be suspect, so the findings compound instead of scattering:

- everything written in a given period, or by a given generator
- everything with zero test coverage, ranked by what it touches
- everything on one blast radius: money, authorization, deletion, outbound messages

Rank by consequence, not by size. The riskiest untested handler is worth more than ten small ones.
Say the cohort's size out loud and hold to it; scope creep here is what turns a review into an
abandoned branch.

## Step 2: build the caller map before reading any handler

For each item, answer three questions from outside it:

1. **Who calls this?** The frontend, a scheduler, another service, a provider webhook, or nothing.
2. **With what credential?** And does the handler require the one that is actually sent.
3. **Does anything call it at all?**

This is cheap and it front-loads the largest findings. Items with **no caller** are dead weight
carrying live authority: archive them before deleting so a rollback is possible. Items whose caller
sends a different credential than the handler checks have been failing on every invocation, possibly
for months, which `ground-truth` will date for you.

The caller map also gives you the intent source for Step 3. What a caller does with a response is
often the only surviving statement of what the response was supposed to be.

## Step 3: triage the cohort through fixed lenses

Read each item once per lens rather than once in total. Mixed-lens reading finds the first thing and
stops. The five that earn their keep:

- **Duplication of an owned rule.** Is this a hand copy of a rule that already has an owner
  elsewhere? Copies drift, and the copy is where the defect lives, because the owner is the one that
  gets fixed. Every money and authorization formula should have exactly one implementation.
- **Boilerplate.** Repeated envelopes, repeated client construction, repeated secret reads. Each
  copy is a place the next change will be forgotten.
- **Security.** Who can call it, what does it act on, does it act on something the caller named.
- **Silent failure.** Errors caught per item, run reports success. See `ground-truth`.
- **Orphans and drift.** Deployed but uncalled, or pointing at a host, table, or field that no
  longer exists.

## Step 4: write tests that pin the intended behavior

Now write coverage, with the assertions derived in Step 3 and never from the handler body.

For each test, be explicit about which of two things you are pinning:

- **Intended:** derived from an external source. Assert it. If the code disagrees, the test fails,
  and that failure is a finding, not a broken test.
- **Merely current:** you could not establish the intent. Do not assert it as correct. Either leave
  it uncovered and inventory the ambiguity, or assert it with a comment naming it as unverified so
  the next person knows the assertion carries no authority.

The second category is where blessing happens. Making it visible is most of the cure.

Do not fix as you go. Mixing an inventory pass with a remediation pass makes both unreviewable, and
you will lose the ability to prove any given fix worked. Fix in a separate pass, test-first, with
each fix **proven red against the pre-fix code**.

## Step 5: adversarially verify the coverage

New tests on old code feel like progress. Verify they are, with two independent checks that do not
trust the person who wrote them:

- **Mutation testing, weighted.** Deliberately break the production code in the places that matter
  most (a comparison in an authorization check, a unit conversion, a signature verification, an
  amount) and confirm each mutation turns a test red, and that it is the test which claims to guard
  it. Anything that survives is a coverage gap wearing a passing test. Expect the survivors to be
  few and genuinely instructive.
- **Independent re-derivation.** A second reviewer re-derives the findings from the schema, the
  migrations and the callers, without reading the first reviewer's tests. Agreements are confirmed,
  disagreements are the interesting part. In practice this both downgrades some findings and adds
  ones the first pass missed, which is exactly why it is worth the cost.

If you are orchestrating agents, these two are the roles to keep separate: the one who wrote the
tests must not be the one who validates them.

## Step 6: hand over an inventory, not a narrative

Each finding needs four fields, and nothing else:

| Field | Why |
|---|---|
| Location | `file:line`, so it can be checked in ten seconds |
| Current behavior | What it does, stated as fact |
| Intended behavior | What it should do, **and the source that says so** |
| Evidence | Live confirmation, or explicitly "not confirmed in production" |

Severity comes after the evidence, never before. A finding with no named intent source is not a
finding, it is a preference.

## The law you will keep rediscovering

Across this kind of review, one observation repeats almost without exception:

> **The correct mechanism already existed in the codebase, and using it was optional.**

The shared helper was there and the handler contained a copy. The guard existed and the endpoint did
not call it. The dedupe registry existed and the send path skipped it. Very little of what you find
is missing knowledge. Almost all of it is a convention that nothing enforced.

That means the durable output of a legacy review is not the fixed files. It is the set of
conventions you convert into constraints so the next generated handler cannot repeat them. That
conversion is `impossible-by-design`, and it is where the value of this pass actually lands.

## Verification

You are done when:

- Every item in the cohort has a caller answer, including "nothing calls it".
- Every assertion you added names an external intent source, or is explicitly marked unverified.
- No fix shipped without first being red against the pre-fix code.
- A weighted mutation run turned the money and authorization tests red, and the survivors are closed.
- A second reviewer re-derived the findings independently and their disagreements were resolved.
- At least one finding was converted into a constraint rather than a fix.

## Related

- `ground-truth`: date each finding and confirm it is really happening before assigning severity.
- `endpoint-surface-map`: the systematic version of Step 2 for services with many endpoints.
- `impossible-by-design`: turn the recurring findings into constraints so the cohort cannot regrow.
