# Harness Test: Pre-flight Checklist

Run through this before and after writing a harness test.

## Design
- [ ] Read the project's own harness toolkit and one existing harness test (and `references/project.md` when present).
- [ ] Identified the **one seam** every dependency crosses (outbound network, the entrypoint, or the data client of a UI flow).
- [ ] Confirmed the unit boots **without editing production code** (intercept, don't refactor).
- [ ] Listed exactly which dependency calls this unit makes (so routes/seed cover them), stored procedures included.

## Toolkit
- [ ] `loadHandler` boots the real handler/flow and **throws** if nothing was captured.
- [ ] `fetchRouter` matches `method + url`, **records every call** with its headers, and **throws on unmatched**.
- [ ] Scripted overrides (stored procedures, refusals, recovered operations) sit **before** the generic store routes.
- [ ] `storeRoutes` reads data **lazily**, records writes for assertions, and rejects filter operators it does not implement.
- [ ] `withEnv` restores prior values (including unsetting vars that didn't exist).
- [ ] One `restore()` reverts network, entrypoint, env, and timers in reverse order.

## The test
- [ ] Arranges env + seed + routes, then boots the real unit.
- [ ] Pins the fake clock at construction, never by assigning a past instant afterwards.
- [ ] Asserts on the **real output** (status/body/UI) AND the **recorded outbound calls**, matching hosts by parsing the URL.
- [ ] Covers at least one failure branch (bad auth, missing field, dependency error).
- [ ] Emulates any column default or trigger the path depends on, and checks zero-row outcomes explicitly.
- [ ] Calls `restore()` in `finally`.
- [ ] Pins **actual** behavior: no assertion written to match an assumption you didn't verify.

## Beyond the harness
- [ ] A handler that touches tables directly under a privileged role was probed once on a disposable stack (grants, real columns).
- [ ] Behavior that rests on the runtime (aborts, gateway flags, leases) was run for real, not only simulated.

## Hygiene
- [ ] No real network/disk/clock I/O; deterministic.
- [ ] Named distinctly (e.g. `*.harness.test.*`) and folded into the team's one verify command + CI.
- [ ] Fake kept minimal; any new verb added deliberately, matching never loosened to force a pass.
- [ ] Any production surprise found while harnessing is recorded as a follow-up, not silently patched.

## Money and recovery cases
See `references/provider-recovery.md`.
- [ ] Charge account, measured fee, application fee, refund list and local facts describe one possible provider history.
- [ ] Same-operation retry exercises exact retrieval/list reads and proves no duplicate provider mutation.
- [ ] Conservation is checked at payment and cancellation boundaries, including fees above available application fee.
- [ ] Real SQL/concurrency and authorized provider Sandbox results are distinguished from offline harness results.
- [ ] A database corpus failure was compared against a clean control on the base branch and official bootstrap parity (roles, default ACLs, extensions and ordering) was established before attribution.
