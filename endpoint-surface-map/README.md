# endpoint-surface-map

A skill for answering the question most services cannot answer: **for every endpoint, who is allowed
to call it, what credential proves that, and what authority does it run with?**

Part of [looties-skills](https://github.com/looties-io/looties-skills), open-source agent skills by
[Looties](https://looties.io).

## What it does

Turns a one-off authorization audit into a standing guarantee.

- Enumerates **every** endpoint from the route table, not just the ones that already have a guard.
  A guard-first audit is structurally blind to the unguarded handler, which is the only case that
  matters.
- Classifies each endpoint on three separate axes: caller, credential, authority.
- Produces a versioned manifest plus a CI gate where an undeclared endpoint fails the build.
- Adds a scheduled read-only check of the **deployed** configuration, because a config file in your
  repository is a deploy input and not a copy of production.
- Hunts five recurring shapes with a concrete test for each: platform auth mistaken for
  authorization, confused deputy, privileged client constructible by accident, callerless privileged
  worker, and orphan endpoints.
- Remediates in caller order, so tightening a gate does not silently break a scheduler.

**Best for:** serverless function fleets (Lambda, Workers, Vercel, Supabase edge functions, Cloud
Run), HTTP route tables, webhook receivers, internal job endpoints, and admin surfaces.

## Install

```bash
npx skills@latest add looties-io/looties-skills --skill endpoint-surface-map
```

## Usage

```
Use $endpoint-surface-map to audit who can call each of our endpoints and gate on it.
```

## Contents

```
endpoint-surface-map/
|-- SKILL.md          <- the workflow the agent loads
|-- README.md         <- this file
`-- agents/           <- UI metadata for agent runtimes
```

## License

MIT, see [LICENSE](../LICENSE).
