---
name: harness-testing
description: Use when writing, designing, or strengthening harness tests — tests that boot a larger unit of a system (an HTTP handler, a job, a UI flow) into a realistic but controlled environment (fake requests, mocked services/APIs, controlled env vars, an in-memory/seeded database, fake timers) and assert end-to-end behavior. Use when asked to "test the whole handler", "integration test without a real DB/network", "mock the services and run the real code path", "add a test harness", or to improve reliability of code that only misbehaves when wired to its dependencies. Framework-agnostic; includes notes for TypeScript/Deno/Node, Python, and Go.
---

# Harness Testing

A **harness test** runs your real code inside a wrapper that simulates the runtime just enough to
verify behavior: fake inputs, mocked services, controlled env, a seeded in-memory database, fake
timers, and setup/teardown. Instead of testing one function in isolation, you plug a *larger* unit —
a request handler, a worker, a screen-level flow — into a realistic-but-controlled environment and
assert what it actually does.

Use it for behavior that only appears when code is wired up: auth and status codes, payload assembly,
branching, persistence, retries, error handling. Keep pure-logic unit tests for isolated helpers.

## The one rule: non-invasive
**Never change production code to make it testable.** No dependency-injection refactors, no "export
the handler just for tests", no test-only flags in shipped code. A harness that demands production
changes isn't riskless and won't be adopted for the code that matters most. Intercept a *seam*
instead (below). If you genuinely cannot reach a seam without touching production, that's a design
finding to raise — not a reason to weaken the rule.

## Step 1 — Find the one seam
A harness is only as simple as its interception point. Find the single boundary that *every* external
dependency crosses, and mock there — not once per dependency.

- **Outbound network** is usually the seam: most SDKs (DB clients, payment, email, storage) ultimately
  call the platform's HTTP primitive. Intercept that and you mock them all with one mechanism.
  - TypeScript/Deno/Node: replace `globalThis.fetch` (verify your SDKs use it — many do in modern
    runtimes), or use `nock`/`msw`.
  - Python: `responses`/`respx`, or monkeypatch `requests`/`httpx`.
  - Go: inject an `http.RoundTripper` / `httptest.Server`.
- **The entrypoint** is the other seam: capture the handler the framework would serve, and call it
  with a fake request — without starting a server. (E.g. intercept the serve call to grab the handler
  closure; build a fake `Request`; assert on the returned `Response`.)
- **The clock**: swap in fake timers so time-dependent logic (timeouts, retries, TTLs) is deterministic.

One seam = one mental model. Resist per-dependency mocks; they drift and multiply.

## Step 2 — Build the harness toolkit
Small, composable, single-purpose pieces:

1. `loadUnit(...)` — boot the real handler/component/job (intercepting the entrypoint, not editing it).
2. `router(routes)` — match `method + url → canned response`, and **record every call** for assertions.
3. `seededStore(data)` — translate an in-memory dataset into the responses the data layer expects;
   record writes so tests can assert persistence.
4. `withEnv(vars)` — snapshot, set, and restore environment variables.
5. `makeRequest(...)` — build fake inbound requests.
6. `createHarness({...})` — wire the above + fake timers, expose `request()` and the recorders, and
   register **one** `teardown()`.

## Step 3 — Write the test
Arrange (env + seed + routes) → boot the real unit → act (one fake request / one render) → assert on
the real output *and* the recorded outbound calls → `teardown()` in `finally`.

```ts
// Illustrative (TypeScript). Adapt the seam to your stack.
const h = await createHarness({
  unit: './handlers/checkout',          // booted, not modified
  env: { SERVICE_KEY: 'test', API_BASE: 'https://api.test' },
  db: { tables: { orders: [], items: [{ id: 'i1', price: 100 }] } },
  routes: [{ method: 'POST', url: 'api.payments.test', respond: () => json({ id: 'pay_1' }) }],
});
try {
  const res = await h.request({ method: 'POST', url: '/checkout', body: { itemId: 'i1' } });
  expect(res.status).toBe(200);
  expect(h.db.tables.orders).toHaveLength(1);            // persistence
  expect(h.calls.some((c) => c.url.includes('payments'))).toBe(true); // outbound
} finally {
  h.teardown();
}
```

## Principles (the difference between a harness that helps and one that lies)

1. **Boot the real thing.** Mock *dependencies*, never the unit under test. The value is exercising
   real code against fakes — not re-implementing its logic in the test.
2. **Loud unmatched, never silent.** An unhandled dependency call must *throw* with a clear message,
   not return `undefined` or hang. Silent gaps produce green tests that assert nothing.
3. **Seed lazily, tear down completely.** Read seeded data at execution time so tests arrange before
   acting. One `teardown()` reverts every global you touched (network, entrypoint, env, timers) in
   reverse order; call it in `finally`. Cross-test leakage is the #1 harness failure mode.
4. **Pin actual behavior, not assumed behavior.** The first boot will surprise you — that's the point.
   Assert what the code *does* (the real status code, the real error text), record the surprise, and
   don't quietly "fix" production to match your assumption.
5. **Keep the fake minimal; extend on demand.** Emulate only the verbs the unit uses. A smaller fake
   is easier to trust. Add a verb deliberately when a test needs it — never loosen matching to pass.
6. **Own only what you can clean up.** Real clients start background work (refresh timers, pools) the
   unit never disposes because the runtime tears it down. Disable leak/resource sanitizers for harness
   tests specifically rather than editing production to satisfy a detector.
7. **Fast, separate, gated.** No real I/O. Name harness tests distinctly (e.g. `*.harness.test.*`) so
   the unit suite stays quick, and fold them into the one verification command the whole team and
   every agent runs — so they're backpressure that rejects regressions, with CI as the mechanical
   ratchet.

## Anti-patterns
- A test that passes whether or not the code under test runs (over-mocked, asserts nothing real).
- Editing production code "just a little" for testability — start over from a seam.
- A bespoke mock per dependency — collapse to one seam.
- Matching `*` / catch-all routes everywhere — fine for a "did it reach real work" smoke, but specific
  routes are what let you assert the *right* calls happened.

## Background reading
Anthropic — *Harness Design for Long-Running Apps*; *Effective Harnesses for Long-Running Agents*.
OpenAI — *Harness Engineering*. Geoffrey Huntley — *Ralph Wiggum as a Software Engineer*.
celesteanders/harness — `docs/best-practices.md`.

See `references/checklist.md` for a copy-pasteable pre-flight checklist.
