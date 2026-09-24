---
name: postgres-privilege-audit
description: "Use when reviewing or hardening who can read which columns, write which rows and execute which functions in PostgreSQL behind Supabase, PostgREST or any API where the browser holds a database role. Builds the effective privilege matrix from the live catalog, finds credential columns (approval tokens, reset codes, counterparty IPs) that an owner-scoped policy hands to the user they authorize against, checks default privileges on new tables, columns and functions, SECURITY DEFINER functions and views, and callers that silently run as the end user, and proves a revoke in a dry run that aborts. Use when asked to \"audit our RLS\", \"check our grants\", \"is this column exposed\", \"triage the security advisor\", \"can a user read their own token\", or \"review this migration\" when it adds a table, column, view or function a client role can reach. Not for authorization of HTTP endpoints or edge functions (use endpoint-surface-map) or query tuning."
license: MIT
metadata:
  author: Looties
  version: "1.0.0"
---

# Postgres Privilege Audit

Row-level security decides **which rows** a role sees. Grants decide **which columns** of those
rows it sees, and which functions it may call. Most reviews, and most automated advisors, stop at
the first question. The expensive defect lives in the second: a policy that correctly returns a row
to its owner also returns every column on it, including the one value that authorizes a decision
*about* that owner.

When the client holds a database role (Supabase, PostgREST, Hasura, any "the browser talks to
Postgres" stack), grants are the API contract. So audit them the way you would audit an API: from
what is actually deployed, per caller, per field, with a probe that acts as the caller.

## Quick reference

| Intent or symptom | Go to | Look at |
|---|---|---|
| "Audit our grants / RLS", advisor triage | Steps 1-2 | Live matrix per browser role, then owner-visible columns |
| A token, code or secret sits on a row its subject can read | Step 3 | Consumer endpoint, set-role probe reporting length only |
| Reviewing a migration that adds a table, column, view or function | Step 4 | Default privileges on production vs the CI replay |
| About to revoke something | Steps 5-7 | Hybrid clients, `select('*')`, unchecked writes, aborting dry run |
| `has_table_privilege` says a role lost access | Step 1 | Column grants; the table check ignores them |
| `permission denied for column` / 42501 after a deploy | Steps 4, 9 | New or renamed columns, replay vs production grant model |
| A public view changes answer for signed-in visitors | Step 6 | `security_invoker` evaluates as `authenticated` for session holders |
| Stop the class from coming back | Step 8 | pgTAP in CI plus a scheduled catalog invariant |

SQL for every step is in `references/catalog-queries.md`. Load it when you start running
queries, not before; each step below names the section it needs.

## Vocabulary

- **Browser roles**: every role a client-held credential can become (`anon` and `authenticated`
  on Supabase and PostgREST). The dangerous one is often `authenticated`, not `anon`: it is the
  role the row owner uses.
- **Owner-visible row**: a row a SELECT policy returns to the user it is about (`owner_id =
  auth.uid()` and its relatives).
- **Bearer column**: a column whose value *is* an authorization. Anyone who reads it can act.
  Email-link approval tokens, password-reset codes, invitation tokens, signed-URL secrets.

## Step 1: take the matrix from the live catalog

Build the effective privilege matrix from the running database: table grants, column grants,
function EXECUTE, RLS status, policies, and whether each view runs as its caller. Do not build it
from migrations, from dashboard toggles, or from an advisor export.

Why each of the alternatives lies:

- **Migrations** describe how a replayed database is built, not how production got here. Dashboard
  edits, squashed baselines and one-off fixes all diverge. In one measurement, the same revoke
  migration withdrew 465 role-privilege pairs across 63 relations on a replayed database and 405
  across 56 in production.
- **Advisors and linters** check for the presence of policies and for function ACLs. None of them
  asks which columns an owner-visible row exposes.
- **`has_table_privilege`** returns `false` when access is granted column by column. Read column
  privileges too (`has_any_column_privilege`, or the per-column counts in section 1), or you will
  report narrowed access as missing access.

Queries: `references/catalog-queries.md` sections 1 to 6. Run them as the owner; the
`information_schema` views hide grants the current role neither gave nor received.

## Step 2: list what each owner-visible row exposes

For every table where a policy hands rows to the user they concern, list the columns that role can
read and classify each one.

| Class | Examples | Verdict for the row's owner |
|---|---|---|
| Display | status, timestamps, amounts, labels | Grant by name |
| Owner's own data | their address, their preferences | Grant by name |
| Bearer / authorization | approval token, reset code, invite token, webhook secret | Never grant |
| Counterparty data | the other party's IP, email, internal notes | Never grant to the other party |
| Internal state | provider ids, retry counters, fraud scores | Grant only with a reader that needs it |

The question for each column is not "is this sensitive?" but **"does this value authorize
something against the person who can read it?"** A token that lets an operator approve a request
is harmless in the operator's inbox and fatal in the requester's browser. Section 3 of the
reference scans for credential-like names; treat its hits as candidates, not verdicts.

## Step 3: trace every bearer column to its consumer, then prove readability

For each bearer candidate:

1. **Find the consumer.** Search the code for the lookup (`.eq('approval_token', token)`, `WHERE
   token = $1`). A consumer that is a public endpoint accepting the token as its only credential
   makes the column a door key. No consumer at all means the column should not be granted
   either.
2. **Name the party.** Which user does the policy hand this row to? If it is the user the token
   decides about, you have a self-approval path.
3. **Prove it as that party.** Switch to the browser role *with that user's identity claims*
   inside a transaction, select the column, report its length (never the value), roll back.
   Reference section 7.

An owner-level session (SQL editor, CLI, migration runner) bypasses column grants and RLS, so it
cannot show you the problem or the fix. Only a role switch can.

## Step 4: know what the next object will be born with

Most privilege regressions arrive in a new migration, through a default nobody wrote down.
Check each one on production and on your CI replay (reference section 5):

- **New functions.** A managed platform can set default privileges that grant EXECUTE on every new
  function to its API roles *by name*. `REVOKE ALL ... FROM PUBLIC` does not remove a named-role
  grant. Revoke from `PUBLIC` and from each role explicitly, then grant back the one that needs it.
- **New tables and views.** Either they are auto-granted to the API roles (so forgetting RLS
  publishes the table) or they are born with no grants at all, sometimes not even for the backend
  role (so forgetting a GRANT breaks the feature). Platforms change this default. Write every
  grant a new table needs, including for your server-side role, instead of inheriting either
  behavior.
- **New columns.** On a table that grants column by column, a new column is unreadable until it
  is named in a GRANT: the feature breaks with `permission denied for column`. On a table that
  grants table-wide, a new column is readable the moment it exists: add `reset_token` to such a
  table and you have shipped Step 3's bug. Know which kind each table is before adding columns.

## Step 5: find every path that runs as the caller before you revoke

A revoke breaks whatever depended on the grant, and the dependency is often server code you
believe is privileged. The classic shape is a **hybrid client**: a client built with the service
key but with the caller's `Authorization` header forwarded. With PostgREST the header decides the
role, so every query on that client runs as `authenticated`, subject to RLS and column grants. It
looks like an admin client and behaves like the browser.

Before revoking, list every reader and writer of the table (application code, background jobs,
database tests) and record which role each actually runs as. Reference section 12 has search
patterns. Move privileged work to a client with no caller header, keep it pinned to the verified
user id, and check the error of every write a revoke could refuse.

## Step 6: fix at the grant, keep the feature

The fix shape is almost always the same:

1. `REVOKE ALL` on the table from the browser roles. A table-level revoke also drops the matching
   column grants.
2. Re-grant, by name, the columns the product reads, and only the UPDATE columns a policy
   actually governs.
3. Change clients that `select('*')` to name their columns. `*` fails with 42501 once any column
   is ungranted.
4. For public projections, prefer a `security_invoker` view over a view that runs as its owner:
   declare the public rows with a policy on the base table and the public columns with column
   grants, then switch the view. Prove the output unchanged by hashing it as the reading role
   before and after (reference section 9).

A `security_invoker` view evaluates as whoever calls it. A browser that holds a persisted session
reads as `authenticated`, not `anon`, and gets a different answer. If sign-up is open (magic links
that create accounts, social login), any visitor can become `authenticated`, so that role is not a
trust level. Fix such breakage at the client (a session-less client for public reads, account
creation disabled where it was never meant to be possible), not by widening the policy.

Never remove a legitimate read to close a hole. Security that breaks a working feature gets
reverted, and the revert usually reopens more than the original hole.

## Step 7: dry-run the migration on production, inside a transaction that aborts

Apply the exact migration to the real database in one transaction, run the role-switched probes
from Step 3, and end with `RAISE EXCEPTION` whose message carries the probe results. Nothing
commits, and the evidence comes back even from runners that return only the last result set or
drop notices. Reference section 8 is the template; `ground-truth` owns the general technique and
its safety rules.

Probe both directions: the bearer column is now denied, **and** every legitimate read and write
the feature needs still works, as each role that performs it. This is the step that catches the
hybrid-client writer; unit tests with a mocked database cannot.

## Step 8: lock the class, not just the instance

Two layers, because each sees what the other cannot:

- **pgTAP in CI**, against a replay, asserting the specific columns are ungranted and the
  legitimate columns still are. It can fail a pull request; it cannot see production.
- **A catalog invariant on a schedule**, against production: no column matching the bearer naming
  rule may hold any browser-role privilege, with a named exclusion list where each entry carries
  its reason. It sees drift; it cannot fail a pull request.

Make the invariant fail loudly with the fix in its message, and add one assertion that it scanned
a non-trivial number of tables, so "wrong schema" does not pass as "clean". Reference section 11.
For the general method of turning the rule into a constraint, see `impossible-by-design`.

## Step 9: replay from zero, and know how the replay differs

Run every migration from an empty database on a disposable stack, then the test suite. This proves
the migration sequence is valid and your tests see the grants the migrations produce.

It does not prove production's grants. A squashed baseline can carry default privileges (such as
auto-granting new tables) that production no longer has, and compensating revokes that live only
in production's history. The result is the worst combination: CI green, production `42501`. Diff
reference section 5 between the replay and production, and make the replay match production, not
the other way round.

## Pitfalls

These happened. Numbers are from real audits, anonymized.

- **The advisor was clean on the critical finding.** Three admin email-link tokens (a moderation
  approval, an exceptional refund, an account reset) sat on tables whose policy handed the row to
  the member each one decided about. Each member could read their own token and call the public
  approval endpoint: self-approve, self-refund, self-reset. The platform's security advisor export
  that day held 68 INFO, 29 WARN and 2 ERROR items, and none of them was this: the tables had
  policies, so they did not even appear. Fixed with column-list grants, 53 pgTAP assertions and a
  naming invariant.
- **The dry run caught what the tests did not.** One of those tables was written by a server
  function through a hybrid client. After the revoke, its insert (and the read-back of the token
  it had just minted) would have run as `authenticated` and failed. Unit tests mocked the
  database and stayed green; the production dry run failed.
- **An unchecked write after a revoke.** Elsewhere, a shared helper received a caller-scoped
  client and issued six writes without checking their errors. Once browser writes were revoked,
  the payment refund (an HTTP call, not a database write) still succeeded, every database write
  returned 42501 and was discarded, and the caller got HTTP 200 on a refunded order that stayed
  live.
- **A view fix that broke signed-in visitors.** Switching two public views to `security_invoker`
  was proven identical for `anon` by hashing. An adversarial review then noticed the client
  persisted sessions and an admin login page created accounts on demand, so any visitor could
  read the views as `authenticated` and see a different result. The fix was a session-less
  client and disabling account creation on that login, not a wider policy.
- **A false regression.** A table-level privilege check reported that users had lost INSERT on a
  core table. They had not: the grant was column-scoped, and `has_table_privilege` returns false
  for that. Roughly 70 tables in that schema used column grants.
- **An invisible break.** A migration replaced two columns and dropped the ones carrying the
  column grant. Every visitor would have hit `permission denied for column`. The row existed, RLS
  allowed it, frontend tests mocked the database, and the dry run ran as an owner-level role that
  ignores column grants. Only the replayed database test suite caught it, and only indirectly.
- **A linter that checks for the line, not its content.** A regex check required a revoke line
  after every SECURITY DEFINER function. A new function had one, naming too few roles, and stayed
  executable by every signed-in user, who could probe another member's state through it. The
  pgTAP suite caught it; the linter could not.
- **Latent grants.** One audit counted about thirty tables where `anon` held table-wide write
  grants that no policy ever admitted. Effective exposure was nil. One permissive policy added
  later would have made it real. Revoke grants no policy uses.
- **A dashboard ratio.** A "29 of 168 tables exposed" banner counted relations where both browser
  roles held all four privileges. The other 139 were deliberately narrowed, not unprotected. Do
  not "fix" the ratio with dashboard toggles.
- **A catalog loop that crashed.** A verification `DO` block iterating `pg_proc` called
  `pg_get_functiondef()` on an aggregate and raised. Filter `prokind = 'f'`.

## Safety rules

- Against production, run only read-only queries, and changes only inside a transaction that
  aborts. Nothing in that transaction may reach outside it (HTTP extensions, `NOTIFY`, dblink).
- Report a secret's length or hash, never its value, in probes, logs, records and pull requests.
- Keep dry runs short and off-peak: revokes and view changes hold locks until the abort.
- Ship the client and server changes with or before the migration that revokes what they used,
  and say so in the deploy order.
- If a finding is live and exploitable, fix it before writing it up in a public place.

## Verification

You are done when all of these hold:

- [ ] The matrix came from the live catalog, at both table and column level, for every browser
      role, and the replay was diffed against it.
- [ ] Every owner-visible table has each exposed column classified; no bearer or counterparty
      column is granted to the party it authorizes against.
- [ ] Every bearer column has a named consumer, or it was withdrawn.
- [ ] Every new or changed function revokes from `PUBLIC` and from each API role by name.
- [ ] Every reader and writer of a narrowed table runs as the role you think, and clients name
      their columns.
- [ ] A production dry run (aborted) shows the bearer read denied and every legitimate read and
      write still allowed, per role; public views hash identical before and after.
- [ ] pgTAP pins the instance, the scheduled invariant pins the class, and both run on every
      change.

## Related

- `ground-truth`: the transaction-you-roll-back technique and its safety rules, and why the
  repository is not the deployed state.
- `impossible-by-design`: turning "remember to grant by column" into an invariant that fails.
- `endpoint-surface-map`: the same audit one layer up, for function and endpoint authorization;
  bearer-token endpoints found here belong in that map.
- `harness-testing`: handler tests against a seeded in-memory store; pair them with one live run
  on a real database, since an in-memory store has no grants to refuse anything.
- `provider-canary`: when the side effect a stolen token unlocks is a payment or provider call.
