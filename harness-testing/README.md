# Harness Testing

A skill for writing **harness tests** — tests that boot a *larger* unit of your system (an HTTP
handler, a background job, a UI flow) into a realistic but controlled environment (fake requests,
mocked services, controlled env vars, a seeded in-memory database, fake timers) and assert
end-to-end behavior.

It's the layer between isolated unit tests and slow, flaky end-to-end tests: real code paths, fake
dependencies, fast and deterministic.

## What it gives you

- A repeatable **design process**: find the one interception seam, build a small composable toolkit,
  and boot the real unit — **without modifying production code**.
- The **principles** that separate a harness that improves reliability from one that quietly asserts
  nothing (loud-unmatched, behavior-pinning, complete teardown, minimal-and-extend).
- Framework-agnostic guidance with notes for TypeScript/Deno/Node, Python, and Go.

## Install

```bash
npx skills@latest add looties-io/looties-skills --skill harness-testing
```

## Use

Ask your agent to "use harness-testing" when you want to test a whole handler/flow against mocked
services, add a test harness to a project, or strengthen integration coverage on code that only
misbehaves once wired to its dependencies.

## Files

- `SKILL.md` — the workflow the agent loads.
- `references/checklist.md` — a pre-flight checklist for a new harness test.
- `agents/openai.yaml` — Codex/OpenAI interface metadata.
