# repo-wide-dead-code-sweep

A skill for finding and removing dead code across a whole repository, with evidence for every
deletion and nothing removed that was merely dormant, replaced badly, or broken.

Part of [looties-skills](https://github.com/looties-io/looties-skills), open-source agent skills by
[Looties](https://looties.io).

## The observation behind it

Run an analyzer with everything switched on and you get a long list. In one sweep, about 250 hits
held about 10 genuinely dead items; most of the rest were exports used in their own file or entries
the analyzer could not see. A careful second pass then reversed three first-pass "dead" verdicts,
and one item that looked dead was a feature that had silently stopped working.

> **"Unused" is a claim about every caller, and most callers are not in the import graph.**

They live in schedulers, triggers, provider-hosted templates, build scripts that iterate numbered
keys, external sites that embed your assets, and READMEs that say "kept for reactivation".

## What it does

Gives you a verdict table, a nine-step procedure, and recipes.

- **Five verdicts:** dead, dormant by design, covered, gap, broken. Only dead and covered are
  deletions; broken is a bug to restore.
- **Two graphs:** the analyzer with export detection on, and your own graph from production entry
  points with tests excluded, because a module used only by its test otherwise looks alive.
- **The deployed catalog:** functions, SQL objects, scheduled jobs and templates read from the
  platform, since the repository is not the deployed state.
- **A four-part dossier per candidate:** scope, origin commit, evidence nothing calls it, and what
  covers the capability today. No replacement named, no deletion.
- **Specialized passes:** translation keys searched in every dynamic form, SQL functions crossed
  against the whole catalog, assets referenced from outside the repo, and externally sourced
  artifacts deleted at the source first.
- **Positive controls:** every empty search is re-run on a known-live name, because a broken search
  makes everything look dead at once.
- **Safe removal:** revertible micro-commits, a production rollback dry-run plus an early full
  migration replay, and a record of what was kept and why.

**Best for:** "what can we delete" audits, cleanup after a feature is retired, pre-refactor
inventories, and codebases where CI has had unused-export detection turned off for a long time.

## Install

```bash
npx skills@latest add looties-io/looties-skills --skill repo-wide-dead-code-sweep
```

## Usage

```
Use $repo-wide-dead-code-sweep to find what we can safely delete across the repo, with evidence for each item, before removing anything.
```

## Contents

```
repo-wide-dead-code-sweep/
|-- SKILL.md              <- the workflow the agent loads
|-- README.md             <- this file
|-- references/
|   `-- recipes.md        <- analyzer flags, SQL cross-reference, i18n search, git and control recipes
|-- evals/
|   `-- evals.json        <- test prompts
`-- agents/
    `-- openai.yaml       <- UI metadata for agent runtimes
```

## License

MIT, see [LICENSE](../LICENSE).
