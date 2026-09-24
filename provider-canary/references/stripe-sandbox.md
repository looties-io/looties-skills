# Stripe sandbox measurement recipe

Read this when a business rule depends on Stripe behavior you have not observed: who keeps an
application fee on a refund or a dispute, which account bears a dispute fee, in which order events
arrive, what a Connect object looks like for your platform's country. The recipe runs entirely in
test mode. Everything here comes from one measured Connect run; re-measure when your charge type,
country or account type differs, because the answers are specific to that combination.

## 1. Keys

- Use test-mode keys only. If your application env files hold only live or restricted keys, the
  Stripe CLI's config file usually holds the test secret and publishable keys for the platform
  (`test_mode_api_key`, `test_mode_pub_key`). Read them inside the script; never print them.
- Refuse any secret that does not start with `sk_test_`, before the first request.
- Read `livemode` on every object you create and abort if it is not `false`.

## 2. A connected account you can actually charge

- Platforms in some countries cannot create Custom accounts directly; the API answers that
  accounts must be created through **account tokens**. Create the token with the **publishable**
  key (`POST /v1/tokens` with `account[individual][...]`, a `tos_shown_and_accepted` flag, and
  Stripe's documented test values: a test date of birth, `address_full_match` as the address
  line, `file_identity_document_success` as the identity document), then create the account with
  the secret key (`POST /v1/accounts` with `account_token`, `type=custom`, and Stripe's documented
  test IBAN for the country). Charges were enabled within seconds.
- Express accounts cannot finish onboarding without Stripe's hosted flow in a browser. If your
  production sellers are Express, measure money movement on a Custom test account and record that
  onboarding and the Express dashboard were not exercised.
- Leave the test account in the sandbox and record its id in the evidence file.

## 3. Charges shaped like production

- Use the charge type production uses (direct charges with the `Stripe-Account` header, or
  destination charges), with the same `application_fee_amount` logic your pricing code computes.
  Import that pricing code rather than typing the numbers.
- To force a dispute, confirm with a documented dispute test payment method, for example
  `pm_card_createDispute` or `pm_card_createDisputeProductNotReceived`.

## 4. Drive both outcomes

- **Lost:** `POST /v1/disputes/{id}/close` (accepting the dispute).
- **Won:** `POST /v1/disputes/{id}` with `evidence[uncategorized_text]=winning_evidence` and
  `submit=true`. In test mode it resolves as won shortly after; poll the dispute status rather than
  sleeping a fixed time.

## 5. What to read, and from which side

| Question | Where to read it |
|---|---|
| Was the application fee refunded? | The platform's application fee object, `amount_refunded` |
| What left and came back to the seller? | The connected account's balance transactions |
| Dispute id format | The dispute object (these disputes had a `du_` prefix; do not pattern-match on an assumed one) |
| Event order | `GET /v1/events` with the `Stripe-Account` header, sorted by `created` |

## 6. What one run measured

Direct charges with an application fee, on a Custom connected account, one dispute lost and one won:

| Measured | Lost | Won |
|---|---|---|
| Application fee refunded to the seller | No (`amount_refunded` 0) | No |
| Debited from the connected balance at opening | Charge amount plus the dispute fee | Same |
| Credited back at closing | Nothing | Charge amount (pending, like a charge); the dispute fee is not returned |
| Events sharing a creation second | `funds_withdrawn` with `created` | `funds_withdrawn` with `created`; `closed` with `funds_reinstated` |
| Evidence submission fee | n/a | None charged in test mode, even where live pricing lists one |

Consequences that reached the code:

- Either `created` or `funds_withdrawn` can be the first event a handler sees, so both must be
  able to open the case.
- `funds_reinstated` can arrive after `closed`. A handler that ignores events on a closed case
  drops the reinstatement. Record it anyway, using Stripe's event time rather than receipt time.
- The creation second is the only order you can measure. Stripe does not guarantee delivery order.

## 7. Turn it into a regression test

Save the raw events from the run (they contain only sandbox ids) as a fixture and replay them, in
order and shuffled, through the real webhook handler in your harness. The measurement then keeps
paying for itself.

## Limits to write down

Test mode does not model everything live mode bills (the evidence submission fee above is one
example), and hosted flows (Express onboarding, dashboard links into a connected account's
dispute) need a browser session. List what was not measured next to what was.
