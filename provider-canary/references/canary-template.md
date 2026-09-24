# Canary script template

Read this when you are about to write the throwaway canary script for Step 2 of `SKILL.md`. It is
runtime-agnostic pseudo-code in TypeScript syntax: adapt the imports and the HTTP client to your
stack (Node, Deno, Bun, Python). Keep the script in a scratch directory, never in the repository,
and write the file before running it as a separate command so it can be reviewed.

The six parts are in the order they must run. Do not reorder them: the mode guard goes before any
network call, and cleanup runs in `finally` so a failing scenario still cancels what it created.

```ts
// 1. Imports: the application's own code, never a copy.
import { buildShipmentPayload } from "<app>/shared/shipment-builder";   // the real builder
import { PRESETS } from "<app>/shared/parcel-presets";                 // the real presets
import { createProviderClient } from "<app>/shared/provider-client";   // the real client

// 2. Mode guard: refuse before the first request.
const key = env("PROVIDER_SECRET");            // loaded into this process only, never printed
const EXPECTED_ACCOUNT = env("CANARY_ACCOUNT_ID");

function assertMode() {
  // Sandbox provider: prefix check (Stripe example).
  if (PROVIDER_HAS_SANDBOX && !key.startsWith("sk_test_")) {
    throw new Error("Refusing to run: not a test-mode key");
  }
  // No-sandbox provider: pin the contract and the free-cancellation window.
  if (!PROVIDER_HAS_SANDBOX) {
    if (!withinFreeCancellationWindow(new Date())) {
      throw new Error("Refusing to run: outside the same-day free cancellation window");
    }
  }
}

function assertObjectMode(obj: { livemode?: boolean }) {
  // Read the mode off every created object, not only off the key.
  if (PROVIDER_HAS_SANDBOX && obj.livemode !== false) {
    throw new Error("Created object is not in test mode, aborting");
  }
}

// 3. Fictional parties: invented people at an address you control.
const SENDER = { name: "Canary Sender", street: "<your office street>", city: "<city>",
                 postal: "<postal>", country: "<cc>" };
const RECIPIENT_BASE = { name: "Canary Recipient", street: "<your office street>", city: "<city>",
                         postal: "<postal>", country: "<cc>" };

// 4. Scenario matrix: option codes from the production count x field variations.
const OPTION_CODES = ["<code used in prod A>", "<code used in prod B>", "<newly reachable code>"];
const VARIATIONS = [
  { label: "recipient phone set", recipient: { ...RECIPIENT_BASE, phone: "<test phone>" } },
  { label: "recipient phone absent", recipient: { ...RECIPIENT_BASE } },
];

type Result = {
  scenario: string; option: string; providerIds: string[];
  httpStatus: number; providerStatus: string; providerError?: string;
  documentSha256?: string; cleanupHttp?: number; finalReadback?: string;
};
const results: Result[] = [];
const created: { id: string; kind: string }[] = [];

async function runScenario(client, option: string, variation) {
  const payload = buildShipmentPayload({
    sender: SENDER, recipient: variation.recipient, option,
    parcel: PRESETS.small,                 // exactly the preset production sends
  });
  const res = await client.announce(payload);
  const body = await res.json();
  created.push({ id: body.id, kind: "shipment" });   // record before judging, so cleanup sees it
  assertObjectMode(body);

  // 5. Status assertion: the provider's status field decides, not the HTTP code.
  const ok = body.status === "<documented success status>";
  const r: Result = {
    scenario: variation.label, option, providerIds: [body.id],
    httpStatus: res.status, providerStatus: body.status,
    providerError: ok ? undefined : summarizeError(body),   // message only, no personal data
  };
  if (ok && body.documentUrl) {
    const pdf = await client.download(body.documentUrl);
    r.documentSha256 = sha256(pdf);
    // Inspect the document too: extract text and assert the fields you changed.
  }
  results.push(r);
}

// 6. Cleanup with independent readback, then the evidence file.
async function cleanup(client) {
  for (const obj of created) {
    const c = await client.cancel(obj.id);           // 202 means accepted, not done
    const after = await client.get(obj.id);          // separate read
    const r = results.find((x) => x.providerIds.includes(obj.id));
    if (r) { r.cleanupHttp = c.status; r.finalReadback = after?.status ?? `http ${c.status}`; }
  }
}

async function main() {
  assertMode();
  const client = createProviderClient(key);
  try {
    for (const option of OPTION_CODES) {
      for (const v of VARIATIONS) await runScenario(client, option, v);
    }
  } finally {
    await cleanup(client);
    writeEvidence({
      date: today(),
      reviewedCommit: gitHead(),
      mode: PROVIDER_HAS_SANDBOX ? "sandbox" : "live account, same-day cancel",
      results,
      notExercised: ["no customer order", "no email sent", "no parcel deposited",
                     "no payment captured"],
      // Never: keys, tokens, real names, real addresses.
    });
  }
  const unclean = results.filter((r) => !["cancelled", "deleted", "expired"]
    .includes(String(r.finalReadback).toLowerCase()));
  if (unclean.length) throw new Error(`Cleanup not confirmed for ${unclean.length} objects`);
}
```

## Adapting it

- **Payments with a checkout session:** the "announce" is session creation; cleanup is `expire`;
  readback asserts `status=expired` and `livemode=false`. Assert line items and totals to the cent
  against what your own pricing code computed. Call the create path twice and assert the second
  call returns the same session (idempotency).
- **Webhooks:** fire concurrent deliveries of the same real event at the handler (signed with the
  test signing secret), then assert the side effect happened exactly once. Replay once more after
  the first run settles.
- **Refunds and disputes:** see [stripe-sandbox.md](stripe-sandbox.md).
- **Transactional email:** send only to an inbox you own, or use the provider's documented test
  recipient addresses; assert on the provider's delivery event, not on the API's 200.

## Evidence file shape

```json
{
  "date": "YYYY-MM-DD",
  "reviewed_commit": "<sha>",
  "mode": "sandbox | live account, same-day cancel",
  "scenarios": [
    {
      "option_code": "<code>",
      "variation": "recipient phone set",
      "provider_ids": ["<id>"],
      "http": 201,
      "provider_status": "<status>",
      "document_sha256": "<hash>",
      "cleanup_http": 202,
      "final_readback": "CANCELLED"
    }
  ],
  "not_exercised": ["physical deposit", "billing of a kept label"],
  "live_application_mutations": false
}
```
