---
name: code-cleanup
description: Safe, behavior-preserving code cleanup and refactoring workflow for recently changed, staged, or user-selected code. Use when asked to clean up code before a commit, improve readability, simplify/refactor without changing behavior, apply project coding conventions, review staged diffs for maintainability issues, or organize small validation-backed cleanup batches.
---

# Code Cleanup

Use this skill to make existing code easier to read, safer to maintain, and more consistent with the surrounding project without changing what it does.

## Core Rules

- Preserve behavior. Treat bug fixes, feature changes, and public API changes as separate work unless the user explicitly includes them.
- Follow the repository's local conventions before generic style preferences. Read relevant project instructions, nearby code, package scripts, and config files before editing.
- Keep scope tight. Prefer recently changed files, staged hunks, or the specific files the user named.
- Protect user work. Inspect `git status` before edits and do not revert or overwrite unrelated changes.
- Validate proportionally. Run the most relevant existing tests, type checks, linters, or formatters for touched code. If a validation command is unavailable or too broad for the change, say so.
- Avoid cleanup that is only personal taste. A change should improve intent, reduce real complexity, remove duplication, or align with established project patterns.

## Scope Modes

- **Staged cleanup**: default when staged changes exist and the user asks for pre-commit cleanup. Review `git diff --cached` and edit only files represented in the staged work unless the user allows propagation.
- **Changed-file cleanup**: use when there are no staged changes or the user asks for uncommitted work. Review `git diff` plus named files or recent edits.
- **Targeted cleanup**: use for explicit files, directories, symbols, or a commit SHA. Keep edits inside that target unless a dependency update is required.
- **Full-file cleanup**: use only when the user asks for a deeper pass. Keep behavior stable and validate more broadly.

State the selected scope briefly before editing when it affects risk or validation.

## Workflow

1. **Discover context**
   - Run or inspect `git status`, the relevant diff, and the touched file list.
   - Identify language, framework, package manager, and available commands from files such as `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `Makefile`, CI config, and repo docs.
   - Read nearby code to match naming, error handling, component structure, data flow, and abstraction style.

2. **Screen exclusions**
   - Skip generated, vendored, third-party, minified, migration-generated, or scheduled-for-deletion code.
   - Do not refactor around an active suspected bug unless the user asks to fix it first.
   - Flag high-churn or cross-branch conflicts when visible, but do not block small safe edits solely on churn.

3. **Find cleanup candidates**
   - Look for unclear names, avoidable nesting, duplicated logic with a shared concept, oversized functions, mixed abstraction levels, dead code, stale comments, nested ternaries, flag arguments, and error handling tangled with primary logic.
   - Note bug risks separately from cleanup opportunities. Do not silently fold bug fixes into cleanup.

4. **Batch edits**
   - Prefer small batches grouped by dependency chain or file proximity.
   - Start with mechanical, low-risk changes before structural extraction or cross-module movement.
   - Keep public API and exported behavior stable unless the user authorized a broader refactor.

5. **Validate**
   - Run focused tests for touched behavior when possible.
   - Run type checks, lint, format, or pre-commit hooks when the project already defines them and they fit the touched scope.
   - If validation fails after cleanup, inspect whether the failure is related. Fix cleanup-caused failures; report unrelated pre-existing failures clearly.

6. **Report**
   - Summarize what changed, what was intentionally left alone, and which validation commands ran.
   - Mention any bugs or follow-up cleanup candidates that were not addressed.

## Transformation Guide

Apply these only when they make the code easier to understand in context:

| Signal | Prefer |
|---|---|
| Vague names such as `data`, `info`, `tmp`, or `res` | Rename to communicate role or domain meaning |
| Deep nesting or arrow-shaped conditionals | Guard clauses, early returns, or clearer branching |
| Repeated logic with one real concept | Extract a function, constant, or helper with a meaningful name |
| Long function with separable responsibilities | Extract cohesive blocks; keep call order readable |
| Dense one-liners or nested ternaries | Explicit intermediate variables, `if`/`else`, or `switch` |
| Comments that restate code | Remove the comment or improve naming |
| Non-obvious business rule or magic value | Add a short why-focused comment or named constant |
| Unused imports, variables, branches, or helpers | Remove only when clearly unused and not part of a public surface |
| Function mutates and returns derived data | Split command/query behavior when the split is natural |
| Boolean flag changes behavior | Split into named functions when call sites become clearer |

## Conflict Rules

- Correctness beats clarity; clarity beats cleverness; local convention beats generic advice.
- Prefer duplication when extraction would hide simple logic or force unnecessary jumping between files.
- Prefer explicit steps over compact chains when debugging or reviewing would be harder.
- Keep an abstraction when it names a real concept, owns repeated behavior, or matches a project pattern.
- Inline an abstraction when its name merely repeats the implementation.
- If a proposed cleanup is not obviously better, leave it alone and mention it as a possible follow-up.

## Validation Heuristics

- For purely mechanical edits, a focused type check, lint, or affected test can be enough.
- For structural refactors, run affected tests plus the relevant type/import checks.
- For cross-module changes, validate all known consumers and check for stale imports or circular dependencies where tooling exists.
- For hot paths, large loops, rendering code, parsers, and data transformations, avoid extraction or allocation changes unless the readability gain is worth the performance risk.
- Do not modify test assertions just to make cleanup pass. Add or adjust tests only when exposing an extracted unit or preserving behavior more directly.

## Anti-Patterns

- Refactoring without understanding the current behavior.
- Mixing unrelated formatting churn into logic cleanup.
- Renaming symbols for preference rather than clarity.
- Introducing a new abstraction for one small call site.
- Removing duplication that is only coincidentally similar.
- Compacting code until the reader must mentally expand it.
- Touching unrelated files to make the diff look cleaner.
- Continuing after cleanup-caused validation failures without investigating.
