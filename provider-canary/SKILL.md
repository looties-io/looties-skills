---
name: provider-canary
description: "Use before shipping, unblocking or declaring a blocker on any change that sends payloads to a third-party provider with real-world or money side effects, such as carrier labels, payments, payouts, refunds, disputes, checkout sessions or transactional email. Runs a small, reversible canary against the real provider (sandbox, or the real account with fictional parties and same-day cancellation) using the application's own payload builder, then verifies cleanup and files evidence. Also use when a provider error is unexplained, provider docs are ambiguous, or a money rule (who keeps which fee) is assumed rather than measured. Triggers include \"will the carrier accept this\", \"test against Stripe\", \"run it in the sandbox\", \"the provider rejected it\", \"is this a real blocker\", \"prove the label prints\", \"who pays the dispute fee\". Not for mocking the provider in-process to cover code branches (use harness-testing) or for verifying your own running system (use ground-truth)."
license: MIT
metadata:
  author: Looties
  version: "1.0.0"
---

# Provider Canary

Mocks and harnesses prove that your code does what you think the provider wants. Only the provider
can tell you what it actually wants. The gap between the two is where integrations fail: a field
the schema calls optional that one service requires, an HTTP 201 that carries a refusal, a fee the
documentation never says who keeps.

A provider canary closes that gap with a small, deliberate, reversible call to the real provider,
using **the exact payload the application sends**, followed by cleanup that is itself verified. It
is not "test in production". It is the provider-side counterpart of confirming a finding against
the running system: the repository cannot tell you how an external API behaves today.

The procedure below is ordered. Each step exists because skipping it produced a wrong answer at
least once.

## Quick reference

| Situation | Go to | What to look at |
|---|---|---|
| About to test a provider change | Steps 1-2 | Option codes production really sends (counts); the app's own builder |
| Choosing sandbox vs real account | Step 3 | Key prefix, `livemode` per object, free-cancellation window |
| Fixtures contain real names or addresses | Step 4 | Replace before anything else |
| One passing call, release pending | Step 5 | Option x field-variation matrix, repetition row when money moves |
| HTTP 2xx but nothing happened downstream | Step 6 | The provider's status field in the body |
| Canary finished | Steps 7-8 | Independent readback of each cleanup; evidence file |
| Blocker rests on provider terms | Step 9 | Docs of the company you actually contract with |
| Fee, refund or dispute rule unclear | Step 10, [references/stripe-sandbox.md](references/stripe-sandbox.md) | Measured sandbox money movement and event order |
| Writing the script | [references/canary-template.md](references/canary-template.md) | Mode guard, matrix, `finally` cleanup, evidence shape |
| Provider error nobody can explain | Pitfalls | Re-run the exact payload; vary one field at a time |

## Step 1: find what production actually sends

Before designing any scenario, read which option codes, service levels, currencies and amount
shapes production has really used. Query your own records, and return **counts grouped by option**,
never rows.

Why: code paths describe what the application *could* send. The data describes what it *does*
send. In one review, a release was blocked on a carrier option that failed a test; a count over
every production shipment showed all of them used three other option codes, and the failing code
had never been sent. The selection logic picked the cheapest option for the carrier, which was not
the one the reviewer assumed from reading the code.

This step also sizes the matrix in Step 5. Test every option that has been used, plus any option
the change newly makes reachable. Options nobody sends are a note, not a blocker.

## Step 2: build the payload with the application's own code

Write a throwaway script (kept in a scratch directory, not committed) that **imports the real
shared payload builder, the real presets and the real provider client** from the application, and
calls them with canary inputs. The announced payload is then byte-for-byte what the application
would send.

A hand-written payload proves nothing about the application. It proves that *some* payload works,
and the one you wrote by hand will quietly lack the field that breaks production, or quietly include
one the application never sends.

If the builder is not importable because it is inlined in two handlers, that is the first finding:
extract one shared builder, point both call sites at it, then canary it. Two copies of a payload
builder drift, and a retry path that rebuilds the payload differently from the first attempt can
undo whatever the first attempt got right.

See [references/canary-template.md](references/canary-template.md) for a script skeleton.

## Step 3: assert the mode before the first call

The script must refuse to run unless it can prove it is pointed at the environment you intend.

- **Sandbox providers:** check the key prefix before any request (for Stripe, refuse anything
  that does not start with `sk_test_`), and read back the mode flag on every object you create
  (`livemode=false` on each session, charge or account). A key check alone does not catch a script
  that later picks up a second client from the environment.
- **Providers with no sandbox** (many shipping brokers and carriers): the canary runs on the real
  account. Assert the contract or account id you intend, and confirm from the provider's own terms
  the window in which a cancellation is free (for example, "cancelled before midnight on the day of
  creation is not billed"). Run inside that window, or do not run.
- Load credentials into the script's environment only. Never print them, never write them to the
  evidence file, never paste them into a command line that is logged.

## Step 4: fictional parties only

Sender, recipient, customer, company: every party in the canary is invented. Use a fictional
person at an address you control (your own office is typical) and obviously fake names.

In one review, the new test fixtures had been copied from a real production order, names and
street addresses included. The code was correct and the fixture was a privacy incident in source
control. Treat a real person's data in a canary or fixture as a blocking finding, and replace it
before anything else.

For the provider's own verification steps, use the documented test values (test cards that force a
dispute, test identity documents that verify, test bank numbers). Never borrow a real one.

## Step 5: run a scenario matrix, not a single happy path

Rows are the option codes from Step 1. Columns are the variations of required fields that your
change touches or that the provider's docs say differ per service.

| Axis | Example variations |
|---|---|
| Option / service code | Every code production used, plus any newly reachable one |
| Required-field presence | Phone present / absent, company name present / absent |
| Size or amount preset | Each preset the application actually sends |
| Party role | The field changed for the sender vs the same field on the recipient |
| Repetition | Same request twice (idempotency), two concurrent webhook deliveries |

A single passing call answers one cell. The failures that matter sit in the cells nobody ran. In
one canary a home-delivery refusal first looked like the change under test (which removed the
sender's phone) was at fault. The matrix showed the refusal came from a missing **recipient**
phone: the same payload with a recipient phone passed, and the application's checkout already made
that field mandatory.

Include the repetition row whenever money moves. One real canary (34 checks) delivered two
simultaneous signed webhooks for the same checkout session and asserted that exactly one return
label resulted and the refund succeeded, then repeated the confirmation step and asserted there was
still exactly one refund.

## Step 6: judge by the provider's status field, not the HTTP status

Many providers accept the request and reject the operation in the body. In one integration, a
shipping broker answered HTTP 201 with a parcel status of `ANNOUNCEMENT_FAILED` and an error
message. Both application call sites treated 201 as a successful label, recorded it, and moved the
order on.

So:

- The canary asserts on the documented status field for every call (announcement, cancellation,
  refund, session state), and records it.
- If the canary finds this gap, the fix belongs in the application too: every caller must assert
  the status, checkpoint the provider ids, and leave the order retryable rather than marking it
  done. Add a real-handler test that feeds a 201-with-failure body.
- A later retry that finds a provider id but no document (a 404 on the label) is still pending,
  not recovered.

## Step 7: clean up the same day, and read the cleanup back

Every object the canary creates is undone before the end of the run, and the undo is verified by an
independent read.

| Created | Cleanup | Readback |
|---|---|---|
| Announced shipment | Cancel it | Status reads `CANCELLED` |
| Shipment whose announcement failed | Cancel it anyway (it may still exist as a draft) | Deleted (one broker answered HTTP 410 with status `deleted`) |
| Unpaid checkout session | Expire it | Status reads `expired` |
| Test connected account, test customer | Delete, or leave in the sandbox and record the id | Listed in the evidence file |
| Rows in your own disposable database | Delete | A count of zero, run separately |

A cancel call that returned 202 means "accepted", not "done". Read the object again. Where the
provider bills for cancellations after a deadline, the readback is also your proof that you are not
going to be billed.

## Step 8: write an evidence file

Store a small JSON or Markdown file next to the review record: date, reviewed commit, and per
scenario the option code, provider ids, the status at each step, the final readback state, the
HTTP code of the cleanup, and a SHA-256 of any document the provider returned (label PDF, invoice).
State explicitly what was **not** done (no customer order, no email sent, no parcel deposited, no
payment captured).

Never include credentials, and never include a real person's data. Ids and hashes are enough for a
reviewer, weeks later, to re-read the provider state without re-running anything. One deployment
used exactly that: before release, it re-read the earlier canaries by id to confirm their final
state instead of creating new shipments.

## Step 9: rest policy on the contract you actually have

When the question is "what does the provider do in case X" (where does a returned parcel go, who
keeps the fee, is a field required), cite the documentation of **the provider you contract with**,
for the product you are on.

If you go through a broker or aggregator, the downstream carrier's consumer terms usually do not
govern your account. In one review, a second release blocker came from the carrier's consumer
terms, which describe returns going to the deposit point. The account was a professional contract
through a broker, whose own documentation says a returned parcel goes to the sender address printed
on the label. The blocker dissolved once the governing document was read.

When a doc page is ambiguous, prefer the canary's observed behavior over an inference from a
generic schema, and write down which you relied on.

## Step 10: measure money behavior instead of assuming it

When a money rule depends on provider behavior you have not observed (does a fee come back on a
refund, who bears a dispute fee, what order events arrive in), measure it in the sandbox before the
business rule is frozen. Documentation is often silent on exactly the combination you use.

Worked example from one Stripe Connect sandbox run (direct charges with an application fee, then a
lost dispute and a won dispute):

- The platform's application fee was never refunded, lost or won.
- The dispute fee was debited from the connected account and stayed there even on a win.
- `charge.dispute.funds_withdrawn` shared a creation second with `charge.dispute.created`, and
  `funds_reinstated` shared one with `closed`. Stripe does not guarantee delivery order, so a
  handler that ignored events arriving after `closed` was dropping the reinstatement.

Keep the raw sandbox events as a fixture and replay them through the real handler in a test. That
turns a one-off measurement into a regression guard. The setup steps are in
[references/stripe-sandbox.md](references/stripe-sandbox.md).

## When no real run should happen at all

Some flows are too consequential to canary even in a sandbox, or have no sandbox for the part that
matters (a payout batch paying real sellers). Prove the state machine inside a database transaction
that is rolled back (claim, idempotent re-entry, duplicate persist, failure releasing the claim),
cover the provider calls with harness tests, and write in the record that **no real run was
executed**. Saying so is part of the evidence.

## Pitfalls

| Symptom | Wrong move | What to do |
|---|---|---|
| Carrier refuses the exact application payload with an odd precision error (one case: volumetric weight) | Declare a design blocker | Check the documented rule (the divisor put that payload well within spec), re-run the same payload later; it announced the next day |
| A diagnostic passes once you drop a field (for example parcel dimensions) | Ship the reduced payload | Forbidden: the checkout quote used those dimensions and the provider bills on what you announce. A differing diagnostic can localize a problem, never close one |
| Refusal about "a phone number" right after changing the sender | Blame the change | Read which party the error names (it was the recipient); vary one field at a time |
| Blocker cites the downstream carrier's consumer terms | Accept it | Read the broker or contract you actually have (Step 9); this cost a full extra review cycle |
| Key prefix says test mode | Trust it | Read `livemode` (or equivalent) off every created object |
| Canary passed on a signed local webhook replay or a zero-cost label | Claim end-to-end proof | It proves the handler or the announcement, not webhook delivery or billing; write the limits next to the result |

## Safety rules

- Never run a canary with a live key when a sandbox exists. Refuse in code, not by habit.
- On providers with no sandbox, run only inside the free-cancellation window and cancel before the
  script exits, even on failure (use `finally`).
- Fictional parties only. Never copy production data into the script, fixture or evidence file.
- Read production for **counts** of option codes, never for rows.
- Never send a real email, create a real order, capture a real payment or deposit a real parcel.
  If the scenario needs one, it is not a canary; ask the owner.
- Write the script file first, then run it as a separate step, so the content is reviewable before
  it executes.
- A canary is not authorization to deploy. The release decision stays with whoever owns it.

## Verification

You are done when:

1. Every option code production uses (from Step 1) has a passing cell, run through the
   application's own builder.
2. Every created object has a final state read back independently (cancelled, expired, deleted),
   and nothing is left billable.
3. The evidence file lists ids, statuses, cleanup codes and document hashes, and states what was
   not exercised.
4. Any gap the canary exposed in the application (status not asserted, retry treated as recovery)
   has a real-handler test that fails before the fix.
5. Each policy claim cites the governing provider's own documentation or a measured sandbox result.

## Related

- `ground-truth`: the same discipline for your own running system; this skill extends it to
  systems you do not control.
- `harness-testing`: the in-process harness that mocks the provider. Use it for the branches;
  use the canary to prove the mock matches reality, then turn canary output into harness fixtures.
- `impossible-by-design`: for making "every caller asserts the provider status" structural rather
  than remembered.
- `agentic-peer-review`: the review that should demand canary evidence before a provider change
  merges.
