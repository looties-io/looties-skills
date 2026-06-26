# Harness Test — Pre-flight Checklist

Run through this before and after writing a harness test.

## Design
- [ ] Identified the **one seam** every dependency crosses (outbound network and/or the entrypoint).
- [ ] Confirmed the unit boots **without editing production code** (intercept, don't refactor).
- [ ] Listed exactly which dependency calls this unit makes (so routes/seed cover them).

## Toolkit
- [ ] `loadUnit` boots the real handler/flow and **throws** if nothing was captured.
- [ ] `router` matches `method + url`, **records every call**, and **throws on unmatched**.
- [ ] `seededStore` reads data **lazily** and records writes for assertions.
- [ ] `withEnv` restores prior values (including unsetting vars that didn't exist).
- [ ] One `teardown()` reverts network, entrypoint, env, and timers in reverse order.

## The test
- [ ] Arranges env + seed + routes, then boots the real unit.
- [ ] Asserts on the **real output** (status/body/UI) AND the **recorded outbound calls**.
- [ ] Covers at least one failure branch (bad auth, missing field, dependency error).
- [ ] Calls `teardown()` in `finally`.
- [ ] Pins **actual** behavior — no assertion written to match an assumption you didn't verify.

## Hygiene
- [ ] No real network/disk/clock I/O; deterministic.
- [ ] Named distinctly (e.g. `*.harness.test.*`) and folded into the team's one verify command + CI.
- [ ] Fake kept minimal; any new verb added deliberately, matching never loosened to force a pass.
- [ ] Any production surprise found while harnessing is recorded as a follow-up, not silently patched.
