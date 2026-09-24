# agentic-peer-review

A skill for running an independent, after-the-fact review of recently merged changes with several
reviewer agents, and turning what they find into proven fixes and a verified deployment.

Part of [looties-skills](https://github.com/looties-io/looties-skills), open-source agent skills by
[Looties](https://looties.io).

## The observation behind it

Look at what a batch of green-CI merges actually carries and one pattern dominates:

> **Green CI proved the checks ran. It did not prove anyone looked.**

The rollup of one merged PR had no application jobs at all. A release merged before its CI
finished. A restored email fed a member-editable field into a helper that trusted anything ending
in `_url`. A model told "read nothing" could read a secret. Each change was fine alone, or looked
fine, and nobody had read them together.

## What it does

Gives you a ten-step review loop run by isolated agents and one coordinator.

- **Freeze the cohort:** the PR list, a reference SHA, release merges deduplicated but their
  integration deltas read, and known limits kept out of the findings.
- **Treat CI as unproven:** read the check rollup of each merged SHA, not the badge.
- **Isolate reviewers by domain:** security and money, backend and data, frontend and
  accessibility, in fresh contexts, with one output schema, looking for defects created by
  combining changes.
- **Adjudicate, then reproduce before ranking:** one coordinator dedupes by root cause, and every
  finding becomes a failing test or canary outside the product tree, with its limits stated.
- **Two records:** a frozen audit record of pre-fix reproductions, and a hardening record of fixes
  with red/green evidence.
- **Review the fix diff:** a fresh reviewer checks the hardening itself. Budget two rounds.
- **Verify the deployment:** derived order including every unit importing a changed shared helper,
  then bumped versions, unchanged auth flags and correct refusals from unauthenticated probes.

**Best for:** the week after a burst of AI-generated pull requests, the review before a release,
merges that nobody else read, and hardening passes where you need to prove each fix closed
something real.

## Install

```bash
npx skills@latest add looties-io/looties-skills --skill agentic-peer-review
```

## Usage

```
Use $agentic-peer-review on the last ten merged PRs: report first, then fix and have the fixes reviewed.
```

## Contents

```
agentic-peer-review/
|-- SKILL.md                      <- the workflow the agent loads
|-- README.md                     <- this file
|-- references/
|   |-- reviewer-prompts.md       <- per-domain reviewer prompts, output schema, adjudication rubric
|   `-- record-templates.md       <- audit and hardening record templates
|-- agents/
|   `-- openai.yaml               <- UI metadata for agent runtimes
`-- evals/
    `-- evals.json                <- realistic prompts for iterating on the skill
```

## License

MIT, see [LICENSE](../LICENSE).
