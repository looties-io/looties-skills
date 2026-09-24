# postgres-privilege-audit

A skill for auditing who can read which columns, write which rows and call which functions in
PostgreSQL, when the client holds a database role.

Part of [looties-skills](https://github.com/looties-io/looties-skills), open-source agent skills by
[Looties](https://looties.io).

## The observation behind it

Row-level security answers "which rows". Grants answer "which columns of those rows" and "which
functions". Reviews and automated advisors mostly check the first question, so the expensive
defect sits in the second:

> **A policy that correctly returns a row to its owner also returns the one column that
> authorizes a decision about that owner.**

An approval token on a request row, readable by the requester, is a self-approval button. The
advisors are silent on it because the table has a policy, which is all they look for.

## What it does

Gives you a nine-step procedure and the catalog queries to run it.

- **Live matrix:** build table, column and function privileges from the running catalog, per
  browser role, never from migrations or advisor text, and read column grants so narrowed access
  is not mistaken for missing access.
- **Owner-visible columns:** classify every column a policy hands to its owner, and ask whether
  the value authorizes something against the person who can read it.
- **Bearer tokens:** trace each token column to the endpoint that consumes it, then prove
  readability by switching to the browser role with the owner's identity claims.
- **Defaults:** know what new functions, tables and columns are born with, why `REVOKE FROM
  PUBLIC` is not enough, and why a replay can grant what production does not.
- **Hidden callers:** find server code that runs as the end user (a privileged key with the
  caller's header forwarded) before a revoke breaks it.
- **Fix and prove:** revoke all, re-grant by column, prefer `security_invoker` views, hash view
  output before and after, dry-run on production in a transaction that aborts with its evidence.
- **Lock it:** pgTAP for the instance in CI, a catalog invariant for the class in production.

**Best for:** Supabase and PostgREST projects, security advisor triage, migrations that add a
table, column, view or SECURITY DEFINER function, and hardening passes that must not break a
working feature.

## Install

```bash
npx skills@latest add looties-io/looties-skills --skill postgres-privilege-audit
```

## Usage

```
Use $postgres-privilege-audit to check which columns our signed-in users can actually read, and whether any of them is a token that approves something about them.
```

## Contents

```
postgres-privilege-audit/
|-- SKILL.md                      <- the workflow the agent loads
|-- README.md                     <- this file
|-- agents/
|   `-- openai.yaml               <- UI metadata for agent runtimes
|-- evals/
|   `-- evals.json                <- realistic trigger prompts
`-- references/
    `-- catalog-queries.md        <- privilege matrix, token scan, set-role probe, aborting dry run, pgTAP invariant
```

## License

MIT, see [LICENSE](../LICENSE).
