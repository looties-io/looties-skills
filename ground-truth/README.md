# ground-truth

A skill for confirming a finding against the running system before anyone acts on it. A finding from
reading code is **a hypothesis with a severity attached to it**. Production decides whether it is a
risk, an outage, or nothing.

Part of [looties-skills](https://github.com/looties-io/looties-skills), open-source agent skills by
[Looties](https://looties.io).

## What it does

Answers three questions for every finding: is it happening, since when, and how far does it reach.

- Validates a destructive schema or permission change against the **real** state inside a
  transaction that is rolled back, with the rollback written first.
- Cross-checks what a scheduler actually sends against what the handler actually requires. Scheduler
  logs record dispatch, not acceptance, so a job whose target answers 401 on every run reports
  success indefinitely.
- Catches deployed-versus-repository config drift, and explains why that check belongs on a schedule
  rather than in the per-commit gate.
- Turns growth into a falsifiable prediction: measure the rate, extrapolate to the threshold, check
  the date against the incident.
- Finds swallowed errors by searching for **missing effects** rather than for errors, because a
  handler that catches per item and returns success leaves no error to find.
- Moves severity in both directions on evidence, and closes findings that live evidence deflates.

Ships with the safety rules: read-only by default, never invoke an endpoint to observe it, never
copy production data anywhere, count rather than list, bound your queries.

**Best for:** triaging an audit whose severities are guesses, diagnosing a cron that "succeeded",
dating a silent failure, and validating a migration before it ships.

## Install

```bash
npx skills@latest add looties-io/looties-skills --skill ground-truth
```

## Usage

```
Use $ground-truth to confirm whether this finding is actually happening in production and since when.
```

## Contents

```
ground-truth/
|-- SKILL.md          <- the workflow the agent loads
|-- README.md         <- this file
`-- agents/           <- UI metadata for agent runtimes
```

## License

MIT, see [LICENSE](../LICENSE).
