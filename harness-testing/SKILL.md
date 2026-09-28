---
name: harness-testing
description: "Use when writing, designing, or strengthening harness tests: tests that boot a larger unit of a system (an HTTP handler, a job, a UI flow) into a realistic but controlled environment (fake requests, mocked services/APIs, controlled env vars, an in-memory/seeded database, fake timers) and assert end-to-end behavior. Use when asked to \"test the whole handler\", \"integration test without a real DB/network\", \"mock the services and run the real code path\", \"add a test harness\", or to improve reliability of code that only misbehaves when wired to its dependencies. Framework-agnostic; includes notes for TypeScript/Deno/Node, Python, and Go."
license: MIT
metadata:
  author: Looties
  version: "1.1.0"
---

# Harness Testing

A **harness test** runs your real code inside a wrapper that simulates the runtime just enough to
verify behavior: fake inputs, mocked services, controlled env, a seeded in-memory database, fake
timers, and setup/teardown. Instead of testing one function in isolation, you plug a *larger* unit
(a request handler, a worker, a screen-level flow) into a realistic-but-controlled environment and
assert what it actually does.

Use it for behavior that only appears when code is wired up: auth and status codes, payload assembly,
branching, persistence, retries, error handling. Keep pure-logic unit tests for isolated helpers.

## Start from the project's own harness
If the project already has a harness toolkit, its names, options and known pitfalls win over the
illustrative ones below: read its source and one existing harness test before writing a new one. A
project that vendors this skill may keep that map in `references/project.md` next to this file; when
the file exists, read it first.

## The one rule: non-invasive
**Never change production code to make it testable.** No dependency-injection refactors, no "export
the handler just for tests", no test-only flags in shipped code. A harness that demands production
changes isn't riskless and won't be adopted for the code that matters most. Intercept a *seam*
instead (below). If you genuinely cannot reach a seam without touching production, that's a design
finding to raise, not a reason to weaken the rule.

## Step 1: Find the one seam
A harness is only as simple as its interception point. Find the single boundary that *every* external
dependency crosses, and mock there, not once per dependency.

- **Outbound network** is usually the seam: most SDKs (DB clients, payment, email, storage) ultimately
  call the platform's HTTP primitive. Intercept that and you mock them all with one mechanism.
  - TypeScript/Deno/Node: replace `globalThis.fetch` (verify your SDKs use it; many do in modern
    runtimes), or use `nock`/`msw`.
  - Python: `responses`/`respx`, or monkeypatch `requests`/`httpx`.
  - Go: inject an `http.RoundTripper` / `httptest.Server`.
- **The entrypoint** is the other seam: capture the handler the framework would serve, and call it
  with a fake request, without starting a server. (E.g. intercept the serve call to grab the handler
  closure; build a fake `Request`; assert on the returned `Response`.)
- **The data client, for a UI flow.** A screen-level test replaces the one data-client module the app
  imports (a module mock) with a chainable fake over seeded tables, then renders the real component
  inside the real router and providers. Real component, real hook, real query code; only the client
  is fake.
- **The clock**: swap in fake timers so time-dependent logic (timeouts, retries, TTLs) is deterministic.

One seam = one mental model. Resist per-dependency mocks; they drift and multiply.

## Step 2: Build the harness toolkit
Small, composable, single-purpose pieces. The names follow one reference implementation; a project's
own toolkit keeps its names.

1. `loadHandler(module)`: boot the real handler (intercepting the entrypoint, not editing it) and
   throw if nothing was captured.
2. `fetchRouter(routes)`: match `method + url → canned response`, **record every call** (method, URL,
   body and headers: an idempotency key or an account header is often the whole correctness of a
   call), and throw on anything unmatched.
3. `storeRoutes(seed)`: translate an in-memory dataset into the responses the data layer expects;
   record writes so tests can assert persistence.
4. `withEnv(vars)`: snapshot, set, and restore environment variables.
5. `makeRequest(...)`: build fake inbound requests.
6. `createHarness({...})`: wire the above plus fake timers, expose `request()` and the recorders, and
   register **one** `restore()`.

Order the routes from specific to generic: scripted overrides (stored procedures, a refused call, a
recovered operation) first, then the generic store routes, then external services. A generic store
route placed first answers calls it was never meant to model.

## Step 3: Write the test
Arrange (env + seed + routes) → boot the real unit → act (one fake request / one render) → assert on
the real output *and* the recorded outbound calls → `restore()` in `finally`.

```ts
// Illustrative (TypeScript). Adapt the seam to your stack.
const h = await createHarness({
  module: new URL('./checkout/index.ts', import.meta.url).href, // booted, not modified
  env: { SERVICE_KEY: 'test', API_BASE: 'https://api.payments.test' },
  db: { tables: { orders: [], items: [{ id: 'i1', price: 100 }] } },
  routes: [{ method: 'POST', url: 'https://api.payments.test/charges', respond: () => json({ id: 'pay_1' }) }],
  fakeTime: Date.parse('2026-01-01T00:00:00Z'), // pinned at construction
});
try {
  const res = await h.request({ method: 'POST', url: 'https://fn.local/checkout', body: { itemId: 'i1' } });
  expect(res.status).toBe(200);
  expect(h.db.tables.orders).toHaveLength(1); // persistence
  expect(h.fetchCalls.some((c) => new URL(c.url).hostname === 'api.payments.test')).toBe(true); // outbound
} finally {
  h.restore();
}
```

## Principles (the difference between a harness that helps and one that lies)

1. **Boot the real thing.** Mock *dependencies*, never the unit under test. The value is exercising
   real code against fakes, not re-implementing its logic in the test.
2. **Loud unmatched, never silent.** An unhandled dependency call must *throw* with a clear message,
   not return `undefined` or hang. Silent gaps produce green tests that assert nothing. The same
   holds inside the fake store: a filter operator it does not understand must fail, because a
   dropped filter matches more rows than production would.
3. **Seed lazily, tear down completely.** Read seeded data at execution time so tests arrange before
   acting. One `restore()` reverts every global you touched (network, entrypoint, env, timers) in
   reverse order; call it in `finally`. Cross-test leakage is the #1 harness failure mode.
4. **Pin actual behavior, not assumed behavior.** The first boot will surprise you; that's the point.
   Assert what the code *does* (the real status code, the real error text), record the surprise, and
   don't quietly "fix" production to match your assumption.
5. **Keep the fake minimal; extend on demand.** Emulate only the verbs the unit uses. A smaller fake
   is easier to trust. Add a verb deliberately when a test needs it; never loosen matching to pass.
6. **Own only what you can clean up.** Real clients start background work (refresh timers, pools) the
   unit never disposes because the runtime tears it down. Disable leak/resource sanitizers for harness
   tests specifically rather than editing production to satisfy a detector.
7. **Fast, separate, gated.** No real I/O. Name harness tests distinctly (e.g. `*.harness.test.*`) so
   the unit suite stays quick, and fold them into the one verification command the whole team and
   every agent runs, so they're backpressure that rejects regressions, with CI as the mechanical
   ratchet.
8. **Pin the clock when you build the harness.** A fake clock that starts at the real time and refuses
   to move backwards accepts a pinned instant assigned later only until that instant is in the past,
   then fails. Pass the instant to the constructor; move the clock forward mid-test only.
9. **Know what the fake store cannot see.** An in-memory store has no column defaults, no schema, no
   grants, no constraints and no triggers. A row inserted without a defaulted column stays without it,
   so a later filter on that column silently matches nothing; a read naming a column that does not
   exist passes; a single-row read or update of zero rows may error where the real API returns null.
   Emulate the default or the stored procedure explicitly in the test, and prove the real behavior
   once against a real database (see the runtime section).
10. **Match hosts by parsing, never by substring.** Filter recorded calls with
    `new URL(url).hostname === 'api.example.test'`. A substring also matches a query string, and
    static analysers such as CodeQL flag the substring form in test code too.

## Money, provider recovery and database evidence
When a harness covers payments, refunds, compensation, labels or any durable provider operation, read
[`references/provider-recovery.md`](references/provider-recovery.md): internally consistent provider
fixtures, recovery reads, provider success followed by local failure, conservation at the boundaries,
real database evidence and a separate provider Sandbox check.

## When the behavior depends on the runtime
A harness proves the handler's logic against seams you control. It cannot prove what only the runtime
or the real database provides: grants, whether a client that hangs up aborts `req.signal`, what a
gateway flag does to an opaque bearer, how a lease behaves when its holder dies. A harness that
simulates such a primitive passes whether or not the runtime implements it. On one local edge runtime
a disconnected client's request was never aborted, so a claim release built on that passed its
harness test and failed live. When a design rests on runtime behavior, run it:

1. **Use a disposable stack, never the running one.** Copy the project's local stack configuration,
   give the copy its own project id and its own ports, and pass its directory explicitly to every
   command. A reset aimed at the wrong project wipes someone else's data.
2. Replay every migration, run the database test suite, and serve the real handlers with test-only
   secrets. Re-copy the configuration after changing a function's flag: a stale copy reproduces the
   old gateway.
3. **Probe a privileged handler live once.** A harness has no grants, so a handler that reads or
   writes a table directly under a service role is unproven until it runs for real: create a test user
   through the auth admin API, obtain a real token, call the served function, and read the rows back.
   Twenty-three green harness tests once hid a `permission denied` that only this probe showed.
4. Drive the real caller (the worker, `curl`), read rows back in the database container, and stop
   processes the way production does (`SIGTERM`, a dropped connection) before checking what is
   still claimed.
5. Mutation-test the SQL guards on that database: redefine one function without its guard, rerun the
   database test, expect a named failure, then restore the definition.
6. Stop the stack without a backup, and delete the test secrets and any seeded users.

## Anti-patterns
- A test that passes whether or not the code under test runs (over-mocked, asserts nothing real).
- Editing production code "just a little" for testability: start over from a seam.
- A bespoke mock per dependency: collapse to one seam.
- Matching `*` / catch-all routes everywhere: fine for a "did it reach real work" smoke, but specific
  routes are what let you assert the *right* calls happened.
- A stored procedure left unscripted and answered by a generic table route, which reads the procedure
  path as a table name and acknowledges the call as an ordinary write.

## Background reading
Anthropic: *Harness Design for Long-Running Apps*; *Effective Harnesses for Long-Running Agents*.
OpenAI: *Harness Engineering*. Geoffrey Huntley: *Ralph Wiggum as a Software Engineer*.
celesteanders/harness: `docs/best-practices.md`.

See `references/checklist.md` for a copy-pasteable pre-flight checklist.
