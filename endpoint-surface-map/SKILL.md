---
name: endpoint-surface-map
description: Use when you need to know who can actually call each endpoint in a service, and prove it. Covers auditing the authorization surface of serverless functions (AWS Lambda, Cloudflare Workers, Vercel functions, Supabase edge functions, Cloud Run), HTTP route tables, webhook receivers, internal/cron workers and admin endpoints. Use when asked to "audit our endpoints", "who can call this", "find unauthenticated endpoints", "check for privilege escalation", "is this endpoint protected", "map the attack surface", when a platform auth flag (verify_jwt, IAM authorizer, API gateway authorizer) may have drifted from what the repository declares, or when a privileged handler acts on a target the caller names (confused deputy). Produces a versioned manifest and a CI gate, not a one-off report.
---

# Endpoint Surface Map

Most services cannot answer a simple question: for each endpoint, who is allowed to call it, what
credential proves that, and what authority does it run with? The answer is spread across a platform
console, a config file, a middleware, and the handler bodies, and those four sources drift apart
silently.

This skill produces a **versioned manifest of every endpoint's trust boundary** and a CI gate that
fails when reality stops matching it. The report is a by-product. The manifest is the deliverable,
because a report ages the moment someone adds a route.

## The one rule: enumerate the universe, not the compliant subset

The instinct is to find the handlers that have a guard and check the guards agree. That check is
structurally blind to the only case that matters. **A privileged handler with no guard at all is
absent from a guard-first model, so the job stays green.**

Invert the direction. Enumerate every endpoint from the filesystem or the route table, then require
each one to carry a declaration. A new endpoint fails the build until someone states its trust
boundary. This single inversion finds more than any amount of reading handler bodies.

## Step 1: classify every endpoint on three axes

For each endpoint, record three independent facts. They are separate questions, and conflating them
is the source of most findings.

| Axis | Question | Not the same as |
|---|---|---|
| **Caller** | Who is allowed to invoke this? | Who happens to invoke it today |
| **Credential** | What proof of identity does the handler verify itself? | What the platform gateway checks |
| **Authority** | What privilege does the code run with? | What the caller's privilege is |

Four caller classes cover almost every service. Use these names or your own, but keep the set small
and closed:

- **machine**: a scheduler, a database trigger, another service, or an operator holding a secret.
  Must verify a private shared secret or a service credential inside the handler.
- **webhook**: an external provider. Must verify a provider signature or a shared secret, and must
  treat the request body as hostile until the signature checks out.
- **user**: a signed-in person. Must resolve the caller's identity from their own token, and must
  never accept an identity supplied in the payload.
- **public**: deliberately unauthenticated. Must not run with elevated authority without a recorded,
  reviewed reason.

## Step 2: write the manifest and gate on it

Emit a checked-in file keyed by endpoint, holding the three axes plus any platform flag that governs
access. Generate the first version from source, then have a human review every row, because
generation captures what the code does and the manifest must record what it *should* do.

Give the gate three modes:

```
check-endpoints            # verify: runs offline, in CI and pre-commit
check-endpoints --write    # regenerate from source, for review
check-endpoints --live     # compare against the deployed reality
```

Two properties make the gate worth having:

1. **Unknown endpoint is a failure.** Adding a route without declaring its boundary breaks the
   build. This is the part that keeps the manifest alive.
2. **Acknowledged findings stay visible.** When a row is deliberately risky and not yet fixed,
   record it as an open acknowledgement rather than a clean one, and have the gate keep warning
   about it. A finding that is silenced by the same mechanism that records it will be forgotten.

## Step 3: check the declaration against production, separately

Everything in Step 2 compares one declaration to another: the manifest against the config file.
**Neither is authoritative about what is deployed.** A config file reaches the platform only when
someone deploys it, and a function deployed from another machine, an older checkout, or the console
keeps whatever setting that deploy applied.

This is not theoretical. A real audit of one service found 30 functions serving with the platform
auth flag disabled while both the manifest and the config declared it enabled. Every one was in the
unsafe direction, and the offline gate was green the entire time.

So add a `--live` mode that reads the deployed inventory and diffs the real flag. Two constraints:

- **It must only read.** Never invoke an endpoint to test it; you will fire side effects in
  production.
- **Keep it out of the per-commit gate.** It needs network and credentials, which the pre-commit
  path has neither of. Wiring it in makes the whole gate flaky or routinely bypassed, which is the
  exact failure mode you are fixing. Run it on a schedule instead. Drift that accumulates outside
  the repository is only visible from outside the repository.

## Step 4: hunt the five recurring shapes

With the manifest in hand, these are the findings that actually appear. Search for the shape, not
for a keyword.

### 1. Platform authentication mistaken for authorization
The gateway flag proves *a* credential was presented, not that *this* caller may do *this*. The
classic instance: the platform's public client key satisfies a gateway's "authenticated" check, so
an endpoint marked protected is reachable by anyone who has read the frontend bundle. Any endpoint
whose only guard is the platform flag is unguarded against the public.

**Test:** call it with the public client key. It should fail.

### 2. Confused deputy
A privileged handler performs an action on a target the caller names: send a notification to the
address in the payload, write to the row id in the body, generate a document for the account id in
the query string. The handler is trusted, the target is attacker-controlled, so the handler becomes
the attacker's tool. Mail-sending endpoints are the most common instance, and turn into open relays.

**Test:** call it with someone else's identifier. It should refuse, not succeed quietly.

### 3. Privileged client constructible by accident
The privilege-escalating client (service role, admin SDK, root credential) is exported as a plain
factory that any file can import. Sooner or later a caller-facing path imports it, and every row
becomes reachable. The fix belongs to `impossible-by-design`: make the privileged client require an
explicit, named caller scope so it cannot be constructed without stating who it is acting for.

**Test:** grep for constructions of the privileged client in caller-facing handlers. There should be
none, and it should be impossible rather than merely absent.

### 4. Callerless privileged worker
An internal job endpoint with elevated authority and no in-handler credential check, protected only
by the platform gateway. Since the gateway accepts a public key (shape 1), anyone can trigger the
job. These are invisible to a guard-first audit precisely because they have no guard.

**Test:** for every `machine` row, confirm the handler itself verifies a private secret.

### 5. Orphans
Endpoints that are deployed but that nothing calls. They carry authority, receive no traffic, get no
review, and are never patched. Build the caller map first (grep the frontend, the schedulers, the
other services, the webhooks registered with providers), then archive before deleting so a rollback
is possible.

## Step 5: remediate in caller order, not in severity order

Tightening a gate breaks any caller that does not present the credential the gate now demands. If a
scheduler sends an opaque shared secret and you enable a token-verifying gateway flag, every
scheduled run starts failing before its handler is reached, and the failure may be silent.

So for each endpoint you are about to tighten:

1. Identify every real caller and the exact credential it sends.
2. Confirm that credential satisfies the new gate, or change the caller first.
3. Only then tighten.
4. Confirm the caller still works, from the caller's side.

Endpoints with **no caller at all** are the easy half: tighten or remove them freely, and that is
usually most of the list.

## Verification

You are done when all of these hold:

- Every endpoint in the route table appears in the manifest, and an undeclared one fails the build.
- The gate distinguishes cleared rows from open acknowledgements, and still reports the open ones.
- A scheduled live check compares the deployed flags against the manifest, reads only, and is not
  part of the per-commit gate.
- For each of the five shapes, you ran the stated test rather than reasoning about the code.
- Every tightened endpoint was traced to its callers before the change, and confirmed from the
  caller's side after it.

## Related

- `impossible-by-design`: make the privileged client and the guard structural instead of optional,
  so the next endpoint cannot repeat these shapes.
- `ground-truth`: confirm a finding is actually happening in production, and since when, before
  assigning it a severity.
