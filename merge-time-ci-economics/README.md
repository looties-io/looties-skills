# merge-time-ci-economics

A skill for cutting a GitHub Actions bill by running CI once, when a merge is attempted, instead of on
every push, without letting anything unproven reach the protected branch.

Part of [looties-skills](https://github.com/looties-io/looties-skills), open-source agent skills by
[Looties](https://looties.io).

## The observation behind it

Decompose a CI bill by trigger and one pattern dominates:

> **The same commit is proven several times, and some of the proofs cannot change any decision.**

The branch push runs CI, the pull request runs it again on every push, the merge into the integration
branch runs it a third time, and a long-lived release pull request re-runs it on every upstream push.
Meanwhile scores and reports that can never block a merge ride along in blocking jobs, and a handful of
10-second jobs each pay a full billed minute. In one audit, about 8,500 minutes in 30 days came down to
an estimated 1,700 per month, with the same checks still guarding every merge.

## What it does

- **Measure:** reconstructs billed minutes per workflow, event, job and branch from the Actions API
  (each job rounded up to the minute), without needing billing scopes.
- **Attribute:** groups the cost by cause, and records the hypotheses that did not hold so nobody
  re-tries them.
- **Redesign:** no push triggers; a single `ready_for_review` pull-request trigger; small jobs merged;
  informational checks on a schedule; expensive proofs scoped by diff and backed by a scheduled run;
  timeouts everywhere.
- **Enforce:** required checks plus auto-merge, a one-page agent procedure (draft, ready, auto-merge,
  undo-and-ready after a push), and a test that fails the build if a push trigger comes back.
- **Diagnose:** jobs failing in three seconds (read annotations, often billing), pull requests blocked
  while `gh pr checks` looks green, skipped or dispatched runs that silently satisfy or fail to satisfy
  required checks, and advisory checks that turn a branch red with no commit.

**Best for:** private repositories over their included minutes, teams where coding agents open many
pull requests, and anyone deciding which checks should be required.

## Install

```bash
npx skills@latest add looties-io/looties-skills --skill merge-time-ci-economics
```

## Usage

```
Use $merge-time-ci-economics to find out why our GitHub Actions minutes tripled and redesign CI to fit the budget.
```

## Contents

```
merge-time-ci-economics/
|-- SKILL.md                        <- the workflow the agent loads
|-- README.md                       <- this file
|-- scripts/
|   `-- actions-minutes.sh          <- read-only billed-minutes reconstruction (gh + jq)
|-- references/
|   `-- workflow-skeleton.md        <- workflow, ruleset, scope script and guard test skeletons
|-- agents/
|   `-- openai.yaml                 <- UI metadata for agent runtimes
`-- evals/
    `-- evals.json                  <- test prompts
```

## License

MIT, see [LICENSE](../LICENSE).
