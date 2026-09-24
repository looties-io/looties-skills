# provider-canary

A skill for proving a third-party integration against the real provider, with the application's own
payload, before anyone ships it or blocks it.

Part of [looties-skills](https://github.com/looties-io/looties-skills), open-source agent skills by
[Looties](https://looties.io).

## The observation behind it

Review a run of integration incidents and release blockers, and most of them share a shape:

> **The mock agreed with the code, and nobody had asked the provider.**

A carrier refused a payload the schema called valid. An HTTP 201 carried a refusal and was recorded
as a success. A blocker rested on a carrier option production had never once sent, or on terms that
did not govern the account. A money rule assumed who keeps a fee that nobody had measured.

## What it does

Gives you a ten-step canary procedure and the rules that keep it reversible.

- **Ground the matrix in production:** count which option codes are really sent before testing any.
- **Use the real builder:** a throwaway script imports the application's payload builder and
  presets, so the canary payload is byte-for-byte the application's.
- **Guard the mode:** refuse non-test keys in code, read `livemode` back on every object, or on
  providers without a sandbox run only inside the free same-day cancellation window.
- **Fictional parties, full matrix:** every option code times every required-field variation,
  including concurrency and replay when money moves.
- **Judge by the provider's status field**, not the HTTP code, and fix callers that do not.
- **Clean up and read the cleanup back**, then file evidence with ids, final states and document
  hashes, never credentials.
- **Cite the contract you have** (the broker's docs, not the downstream carrier's consumer terms)
  and **measure money behavior in the sandbox** instead of assuming it.

**Best for:** shipping-label, payment, refund, payout, dispute, checkout and transactional-email
integrations; unexplained provider errors; and release reviews about to declare a provider blocker.

## Install

```bash
npx skills@latest add looties-io/looties-skills --skill provider-canary
```

## Usage

```
Use $provider-canary to prove the carrier accepts our new label payload before we release it.
```

## Contents

```
provider-canary/
|-- SKILL.md                      <- the workflow the agent loads
|-- README.md                     <- this file
|-- agents/
|   `-- openai.yaml               <- UI metadata for agent runtimes
|-- evals/
|   `-- evals.json                <- realistic trigger prompts
`-- references/
    |-- canary-template.md        <- script skeleton: mode guard, matrix, cleanup, evidence
    `-- stripe-sandbox.md         <- measuring fees, disputes and event order in test mode
```

## License

MIT, see [LICENSE](../LICENSE).
