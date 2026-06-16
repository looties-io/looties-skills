# code-cleanup

A Codex / Claude Code skill for safe, behavior-preserving code cleanup before review or commit.

Part of [looties-skills](https://github.com/looties-io/looties-skills) - open-source agent skills by [Looties](https://looties.io).

## What it does

Guides an agent through practical cleanup work without turning refactoring into a hidden feature change:

- Scopes cleanup to staged, changed, targeted, or explicitly selected files
- Preserves behavior and separates bug fixes from refactoring
- Follows local project conventions before generic style preferences
- Groups edits into small validation-backed batches
- Uses existing tests, type checks, lint, format, and pre-commit commands when available
- Calls out follow-up risks instead of silently widening scope

**Best for:** pre-commit cleanup, readability passes, small refactors, removing accidental complexity, and aligning touched code with the surrounding project style.

## Install

```bash
npx skills add looties-io/looties-skills --skill code-cleanup
```

## Contents

```
code-cleanup/
|-- SKILL.md          <- main workflow guide (agent entry point)
|-- README.md         <- this file
`-- agents/           <- UI metadata for agent runtimes
```

## Usage

Once installed, activate the skill in Claude Code or Codex with:

```
Use $code-cleanup to clean up my staged changes before commit.
```

The agent loads `SKILL.md` as its workflow guide and chooses validation commands from the target repository.

## License

MIT - see [LICENSE](../LICENSE).
