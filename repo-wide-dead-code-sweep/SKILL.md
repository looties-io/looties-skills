---
name: repo-wide-dead-code-sweep
description: "Use when hunting dead code across a whole repository rather than a diff. Covers unused exports, orphan files and scripts, serverless functions that are deployed but no longer called, orphan SQL functions, views and tables, unused translation keys, email templates and static assets, and the cleanup after a feature is retired. Gives a four-part evidence dossier per candidate, the blind spots of analyzers such as knip (tests counted as entry points, dynamically built i18n keys, type-only consumers, assets referenced from outside the repo), a catalog-level SQL cross-reference, and a removal plan in revertible micro-commits with rollback dry-runs. Use when asked \"what can we delete\", \"find dead code\", \"unused exports\", \"orphan functions\", \"unused translation keys\", \"is this still used anywhere\", \"clean up after we killed feature X\", or before a large refactor. Not for tidying a diff or a few files (see code-cleanup), nor for mapping callers of one module you will keep (see legacy-code-review)."
license: MIT
metadata:
  author: Looties
  version: "1.0.0"
---

# Repo-Wide Dead Code Sweep

"Unused" is a claim about **every** caller, and most callers are not in the graph an analyzer sees.
They are in a scheduler, a database trigger, a template stored at a provider, a build script that
iterates over numbered keys, an external website embedding your badge, or a README that says "kept
for reactivation". A static analyzer's report is a list of candidates, not a list of deletions.

Deleting is cheap. Being wrong is expensive, because a removed capability is usually rediscovered by
a user, weeks later, with no error pointing back at the commit. So the deliverable of a sweep is a
dossier first and deletions second, and each deletion ships with the name of whatever covers the
capability today.

## Quick reference

| Intent or symptom | Go to | Look at |
|---|---|---|
| "What can we delete?" | Steps 1 to 5 | Analyzer with exports on, test-free graph, deployed catalog, dossier |
| Analyzer report is huge | Step 1 | Split "export keyword only" from real candidates |
| Module looks alive only because of its test | Step 2 | Graph seeded from production entries, tests excluded |
| Function or SQL object may still run somewhere | Step 3, recipes 3-4 | Platform list API, live catalog, scheduler table |
| Candidate is behind a flag or in a README | Step 4 | Dormant-by-design surfaces; ask the owner |
| Translation keys "unused" per grep | Step 6, recipe 5 | Namespaced, last-segment, prefix and numbered forms; build scripts |
| Template or asset with no reference in the repo | Step 6 | Provider, CMS, external embeds; delete at the source first |
| Every search comes back empty | Step 7, recipe 7 | Positive control on a known-live name |
| Ready to remove | Steps 8-9 | Micro-commits, rollback dry-run plus early full replay |

Exact commands, the SQL cross-reference query and the i18n search script are in
[`references/recipes.md`](references/recipes.md). Read the numbered section when the table points to it.

## Classify before you delete

Every candidate lands in exactly one of these buckets. Only the first and third are deletions.

| Verdict | Meaning | Action |
|---|---|---|
| Dead | Nothing calls it and nothing needs it | Remove |
| Dormant by design | Kept on purpose for reactivation, behind a flag or a README | Keep; ask the owner before touching |
| Covered | A newer path does the same job | Remove, and name the replacement in the commit |
| Gap | Looks like a duplicate, but the replacement does not do the same thing | Decision for the owner, not a deletion |
| Broken | Something should call it and nothing does | Restore or escalate; this is a bug, not dead code |

The last two matter most. A template with no sender may be a feature that silently stopped working.
Deleting it removes the only evidence that the feature ever existed.

## Step 1: run the analyzer with everything switched on

Run your analyzer (knip for TypeScript, vulture for Python, `staticcheck` or `deadcode` for Go, or
the equivalent) with unused-export and unused-type detection **on**, even when CI turns them off.
Projects commonly disable export checks in CI because the signal is noisy, which means nobody has
looked at that list in months.

Then triage the noise mechanically. The largest category is usually "exported but only used inside
its own file": the symbol is alive, only the `export` keyword is dead. Dropping those keywords is a
safe, separate commit that shrinks the public surface and makes the next sweep quieter.

Read the analyzer's config before trusting its silence. Ignored globs, a `project` pattern that
covers only `src/`, and root files outside that pattern (edge middleware, scripts) are never
reported, in either direction.

## Step 2: build your own graph from the real entry points

Most analyzers treat test files as entry points. A module whose only importer is its own test
therefore reads as alive, forever. Build a second graph seeded only from what production actually
executes: the HTML entry, server or edge middleware, route files, workers, and scripts that CI or a
scheduler runs. Exclude tests as seeds. Anything reachable only from tests is a candidate. (knip's
production mode does something close; check what your version counts as an entry.)

Resolve imports the way your runtime does. ESM code importing `./foo.js` that is really `foo.ts`
must be normalized before lookup, or half your graph goes missing and everything looks dead.

## Step 3: catalog what is deployed, not what is in the repository

The repository is an input to the deployed state, not a copy of it. List, from the platform itself:

- deployed serverless functions (the platform's list API), compared with the folders in the repo
- SQL functions, views and tables from the live catalog (`pg_proc`, `pg_views`, `pg_class`)
- scheduled jobs from the scheduler's own table, not from the file that is supposed to create them
- templates held by the email provider or CMS

Differences in both directions are findings: code in the repo that is not deployed (probably dead),
and objects deployed that no longer exist in the repo (orphans with live permissions). Archived
folders are only safe to delete once the catalog confirms none of their names is still deployed.

## Step 4: check the dormant-by-design surfaces

Before anything is called dead, look for the places where a team parks code on purpose:

- feature flags and kill switches, including ones set to "off" in every environment
- READMEs or docs that list what is kept for reactivation
- analyzer ignore lists (a file ignored by name was usually ignored for a reason)
- routes deliberately unmounted, with a commit message explaining why

If a candidate is on any of these, it is not yours to delete. Ask the owner. One cheap question
beats a revert and an apology.

## Step 5: build the four-part dossier for each candidate

For every candidate that survives Steps 1 to 4, write down four things. A candidate missing any of
them stays.

1. **Scope.** What the code does, in one sentence of domain language, not a restatement of its name.
2. **Origin.** The introducing commit (`git log --diff-filter=A` on the file, or `git log -S` on the
   symbol) and the reason it was written. The reason tells you what to look for as its replacement.
3. **Evidence nothing calls it.** The searches you ran, where, and that each one returned nothing.
   Include the non-code places: schedulers, triggers, provider dashboards, other repositories.
4. **What covers the capability today.** The replacement, by name. If you cannot name one, the
   verdict is Gap or Broken, not Dead.

Mark each evidence line as **measured** (the command and its output, including the positive control
from Step 7) or **inferred** (reasoning, naming conventions, "looks like a duplicate"). A verdict of
Dead or Covered needs measured evidence for item 3 and a named, checked replacement for item 4.

The fourth item is the one that catches mistakes. "Nothing calls it" is often true of a feature that
broke; "X does this now" is only true of a feature that was replaced.

## Step 6: the specialized passes

Some categories need their own method because their consumers are invisible to import graphs. Read
recipes 4 (SQL), 5 (translation keys) and 6 (git archaeology) before running these passes.

**Translation keys.** Treat every key as consumed dynamically until proven otherwise. Search, for
each key: the literal, the `namespace:key` form, the last segment alone, each ancestor prefix (code
often passes `section.subsection` and appends the rest), and interpolation shapes such as
`step${i}_title` for numbered families. Also check build scripts that serialize a whole namespace or
hard-code a key list, and type-level consumers. Then run `git log -S` on the key to find the commit
that removed its last consumer: that commit tells you whether the copy moved somewhere else (Covered)
or a screen lost text it still needs (Broken). Keep locales in parity when removing.

**SQL objects.** Cross every candidate function in the live catalog against triggers, policies,
scheduled jobs, views, column defaults, check constraints, expression indexes, rewrite rules and the
bodies of every other function. Then search the repository and every external caller (RPC clients,
other services, notebooks) for the name. Only a candidate absent from all of them is dead. A useful
side effect: this pass finds functions that cannot run at all because they reference columns that no
longer exist, which is strong evidence they are dead.

**Assets.** A file in `public/` can be referenced by an external site (a launch-directory badge, an
embedded widget) or by HTML stored in a database (CMS posts, email bodies). A repo search cannot
prove an asset is unused. Check the CMS content and your list of external embeds, or keep it.

**Externally sourced artifacts.** When the source of truth lives outside the repo (email provider
templates, CMS entries, feature-flag service), delete **there first**, then run the sync that pulls
the local copy. Deleting only the local copy gets undone by the next sync. Check whether your sync
deletes local files for removed items; many only add and update, so the local file and any database
mapping row must then be removed by hand.

## Step 7: every search needs a positive control

A search that returns nothing looks exactly like proof of absence. Before trusting an empty result,
run the same command on a symbol you **know** is used and confirm it finds it. This catches the
failure modes that make everything look dead at once:

- a search tool that exists in your interactive shell (an alias or wrapper) but not in the
  subprocess a script spawns, so every call quietly returns empty
- a glob that silently skips files (in git, `src/**/*.tsx` requires at least one directory level and
  misses `src/main.tsx`; use `git ls-files -- src` and filter by extension, or a `:(glob)` pathspec)
- a regex that is escaped wrong on its way through a CLI, or uses the wrong boundary token

Prefer plain substring matching (`LIKE '%name%'`, `grep -F`) for liveness checks. It over-matches,
which errs toward keeping code, and that is the safe direction.

## Step 8: remove in revertible micro-commits

One commit per concern: dead scripts, dead exports, dropped `export` keywords, translation keys,
each retired function, each migration. Each commit must pass the full gate on its own, so any one of
them can be reverted without dragging the others. Put the replacement's name in the commit message
and, for SQL, in the migration header next to each dropped object.

Order deployments so nothing has a dangling reference for even one tick: deploy a new target before
the migration that schedules it, drop the function from the platform after its caller is gone, and
confirm deleted endpoints answer 404.

## Step 9: prove destructive database changes twice

A destructive migration needs two different proofs, because each catches what the other cannot.

1. **Dry-run against production inside `BEGIN ... ROLLBACK`** with assertions inside the block
   (the method is in `ground-truth`). This proves the drops succeed against the real dependency
   graph and real data.
2. **The full migration replay from zero, early.** This proves the change composes with every
   fixture, test and concurrency check your CI runs. Run it before you open the pull request, not at
   merge time.

The dry-run cannot see fixture assumptions; the replay cannot see production data. You need both.

## Pitfalls

Measured in one real sweep (counts from its record); each row changed how the procedure is written.

| What the sweep saw | What it really was | Caught by |
|---|---|---|
| About 250 analyzer hits | About 110 "export keyword only", most of the rest invisible entries (root middleware, ambient type files, a type read through `keyof import(...)`), about 10 truly dead | Step 1 triage |
| Three first-pass "dead" verdicts | A presenter component listed in a README as kept for reactivation; a nightly sync that logs only when it has work and is the only path between two systems; an undocumented script that is the only way to recreate a sandbox account the tests hard-code | Steps 4 and 5 (a caller search passes all three) |
| Hosted template with no sender | Not a duplicate: the rebuilt flow sends inline HTML instead. Left to the owner as a Gap | Step 5, item 4 |
| Email template with no sender | A broken feature; restored on a durable outbox, not deleted | Step 5, item 4 |
| Word-boundary regex matched nothing through the database CLI | Broken search (escaping in transit, or `\m` used where Postgres ends a word with `\M`); `LIKE` worked | Step 7 |
| Orphan validation function | A rule whose trigger was never attached; some rows already broke it. A restored check dry-ran green on production, then the replay's concurrency proof showed the generator filling that column at signup emits values the rule rejects. Withdrawn; the generator fix became a prerequisite | Step 9 (replay) |
| Four merge-time CI attempts | One conflict; two where the replay caught what the dry-run could not (a scheduled job missing a required setting, a fixture violating the withdrawn rule, an assertion assuming a row existed); one concurrency failure (row above) | Step 9, run early |
| Unread configuration table | Held a service credential in clear text, readable by the public roles. Dead objects keep their permissions | Step 3, then `postgres-privilege-audit` |
| Two "unused" translation namespaces | One iterated by numbered keys in server-side meta rendering and serialized whole into a generated manifest; the other hard-coded in a build script | Step 6 |

Net result of that sweep, for scale: 33 SQL functions, 72 translation keys and 109 `export` keywords
removed, two functions deleted from the platform, one feature restored. Of the functions dropped,
four could not run at all because they read columns or tables that no longer existed.

## Safety rules

- Read-only against production. Destructive changes run in a rolled-back transaction until the
  migration ships through the normal path.
- Never delete a dormant-by-design item without the owner's explicit yes.
- Never delete a candidate whose dossier lacks the "what covers it" entry.
- Never remove a public asset on repo evidence alone.
- Record production evidence as counts and names of objects, never as rows of user data.
- Do not mix a restoration (Broken) or a new rule into the deletion commits. Different review,
  different revert.

## Verification

You are done when:

- every candidate has a verdict from the table, and every removal has a four-part dossier
- every empty search in the dossier has a positive control next to it
- each micro-commit passes the full gate on its own
- destructive migrations passed both the production rollback dry-run and the full replay
- the platform catalog shows the deleted functions and objects gone, and deleted endpoints return 404
- a dated record lists what was removed, what covers each capability, what was kept and why, and
  what was left for a decision, so the next sweep does not re-propose the same items

## Related

- `code-cleanup`: behavior-preserving cleanup of a diff or a few files. This skill is the repo-wide,
  evidence-first counterpart.
- `legacy-code-review`: the caller map for code nobody has read; use it when a candidate turns out to
  be alive but unowned.
- `ground-truth`: the rollback dry-run, and proving whether a "broken" candidate is really failing
  and since when.
- `endpoint-surface-map`: deployed-versus-declared for endpoints, including orphans that still accept
  calls.
- `postgres-privilege-audit`: what to do about dead objects that still carry grants.
- `merge-time-ci-economics`: why the replay belongs before the pull request, not at merge.
