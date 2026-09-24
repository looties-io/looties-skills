# Recipes for a repo-wide dead code sweep

Read the section you need when you reach it in the procedure. Every recipe is read-only. Adapt
schema names, paths and tools to your stack; the shapes are what matter.

Contents:

1. Analyzer run with everything on
2. Production-only import graph
3. Deployed catalog
4. SQL cross-reference query
5. Translation key search
6. Finding the last consumer with git
7. Positive controls

## 1. Analyzer run with everything on

knip, as a worked example (other analyzers have equivalent switches):

```bash
# Everything, regardless of what the config excludes for CI
npx knip --include files,exports,types,nsExports,nsTypes,dependencies --reporter json > knip.json

# Closer to "what production reaches": excludes test files and devDependencies as entries
npx knip --production --reporter json > knip-prod.json
```

Diff the two reports. An item flagged only in the production run is reachable only from tests.

Triage buckets, in order:

1. **Export keyword only**: the symbol is referenced in its own file. Remove the `export` keyword,
   one commit for all of them.
2. **Invisible entry**: consumed by a root file outside the project glob, an ambient `.d.ts`, a type
   query (`keyof import('./x').T`), a config string, or a script. Add it to the config as an entry or
   ignore it with a comment, so the next run is quieter.
3. **Candidate**: goes to the dossier (SKILL.md Step 5).

## 2. Production-only import graph

Seeds: the HTML entry, server or edge middleware, worker and function entrypoints, route modules,
scripts invoked by CI, package scripts or schedulers. Never test files, stories or fixtures.

Any resolver works (dependency-cruiser, madge, or a short script over the TypeScript compiler API).
Two things to get right:

- Normalize ESM specifiers: an import of `./foo.js` may resolve to `foo.ts` or `foo.tsx`.
- Honor path aliases from `tsconfig.json`, or every aliased import looks like a missing edge.

Listing files with git, without the glob trap:

```bash
# Wrong: git's ** needs at least one directory, so src/main.tsx is skipped
git ls-files 'src/**/*.tsx'

# Right
git ls-files -- src | grep -E '\.(ts|tsx)$'
git ls-files -- ':(glob)src/**/*.tsx' 'src/*.tsx'
```

Output: every file in the project not reachable from a production seed. Anything reachable only
from tests is a candidate, not a verdict.

## 3. Deployed catalog

Compare what the platform runs against what the repo declares. Examples:

| What | Where the truth is |
|---|---|
| Serverless functions | The platform's management API (JSON is easier to diff than a CLI's table output) |
| SQL functions, views, tables | `pg_proc`, `pg_views`, `pg_matviews`, `pg_class` on the live database |
| Scheduled jobs | The scheduler's own table (for pg_cron, `cron.job`) |
| Email templates | The provider's templates API |
| CMS assets | The CMS content itself, including HTML stored in database columns |

Lists that are **not** evidence of use: manifests, allow-lists and trust-boundary files that
enumerate functions for a gate, and archived history rows. They mention a name because a tool
requires every name, not because anything calls it.

## 4. SQL cross-reference query (Postgres)

Run read-only. It lists candidate functions in your application schemas with a flag per place that
can reference them. A row with every flag false is a candidate for the repository search, not yet a
verdict. `LIKE` over-matches (a name that is a prefix of another name stays "referenced"), which errs
toward keeping.

```sql
with candidates as (
  select p.oid, n.nspname as schema_name, p.proname as fn,
         pg_get_function_identity_arguments(p.oid) as args
  from pg_proc p
  join pg_namespace n on n.oid = p.pronamespace
  where n.nspname in ('public')              -- your application schemas
    and p.prokind in ('f', 'p')
    and not exists (                          -- skip extension-owned functions
      select 1 from pg_depend d
      where d.classid = 'pg_proc'::regclass and d.objid = p.oid and d.deptype = 'e')
)
select c.schema_name, c.fn, c.args,
  exists (select 1 from pg_trigger t where t.tgfoid = c.oid)                      as trigger_fn,
  exists (select 1 from pg_event_trigger e where e.evtfoid = c.oid)               as event_trigger_fn,
  exists (select 1 from pg_proc o
          where o.oid <> c.oid and o.prosrc like '%' || c.fn || '%')              as in_other_fn,
  exists (select 1 from pg_policy pol
          where coalesce(pg_get_expr(pol.polqual, pol.polrelid), '') ||
                coalesce(pg_get_expr(pol.polwithcheck, pol.polrelid), '')
                like '%' || c.fn || '%')                                          as in_policy,
  exists (select 1 from pg_views v where v.definition like '%' || c.fn || '%')    as in_view,
  exists (select 1 from pg_matviews m where m.definition like '%' || c.fn || '%') as in_matview,
  exists (select 1 from pg_attrdef ad
          where pg_get_expr(ad.adbin, ad.adrelid) like '%' || c.fn || '%')        as in_default,
  exists (select 1 from pg_constraint co
          where pg_get_constraintdef(co.oid) like '%' || c.fn || '%')             as in_constraint,
  exists (select 1 from pg_index i
          where (i.indexprs is not null or i.indpred is not null)
            and pg_get_indexdef(i.indexrelid) like '%' || c.fn || '%')            as in_index,
  exists (select 1 from pg_rewrite r
          where r.rulename <> '_RETURN'
            and pg_get_ruledef(r.oid) like '%' || c.fn || '%')                    as in_rule,
  exists (select 1 from pg_aggregate a
          where c.oid in (a.aggtransfn::oid, a.aggfinalfn::oid))                          as aggregate_support,
  exists (select 1 from pg_operator op where op.oprcode::oid = c.oid)             as operator_fn,
  exists (select 1 from pg_cast ca where ca.castfunc = c.oid)                     as cast_fn
from candidates c
order by c.fn;
```

Overloads share a name, so a hit on one overload keeps all of them; split by `args` if it matters.
`prosrc` is empty for SQL functions written with a `BEGIN ATOMIC` body (Postgres 14+); on those
versions extend `in_other_fn` with `or coalesce(pg_get_function_sqlbody(o.oid), '') like ...`, or read
`pg_get_functiondef(o.oid)` for the few candidates left.

If pg_cron is installed, add the scheduler separately (the table may not exist elsewhere):

```sql
select c.fn, j.jobname
from (select distinct proname as fn from pg_proc p
      join pg_namespace n on n.oid = p.pronamespace
      where n.nspname in ('public')) c
join cron.job j on j.command like '%' || c.fn || '%';
```

Then, outside the database:

```bash
# Word match over the repo, excluding migrations and docs, which mention names without calling them
git grep -n -w -F 'the_function_name' -- . ':(exclude)db/migrations' ':(exclude)docs'
```

Also search every external caller you know of: RPC calls from other services and repositories,
notebooks, BI tools, webhook configurations.

Optional evidence: if `track_functions` is enabled (`pl` or `all`), `pg_stat_user_functions.calls`
counts calls since the last statistics reset. Zero calls over a long window supports "dead"; check
when stats were last reset before relying on it.

Bonus finding: a candidate whose body references a column or table that no longer exists cannot run
at all. Check with `plpgsql_check` if installed, or by reading the body against the current schema.

## 5. Translation key search

Treat every key as dynamically consumed until each of these returns nothing:

| Form | Example for key `checkout.summary.total_label` in namespace `orders` |
|---|---|
| Full literal | `checkout.summary.total_label` |
| Namespaced | `orders:checkout.summary.total_label` |
| Last segment | `total_label` |
| Each ancestor prefix | `checkout.summary`, `checkout` (code that builds the rest) |
| Numbered family | `step1_title` becomes `step${` or `step{{` or `'step' +` |

Also inspect, by hand, any build script or server module that imports a whole locale file (it may
serialize every key into a generated artifact) or hard-codes a key list, and any typed-keys
declaration file.

A script shape (bash plus jq; swap `git grep` for your search tool, but see section 7):

```bash
ns_file=locales/en/orders.json
ns=$(basename "$ns_file" .json)

jq -r 'paths(scalars) | map(tostring) | join(".")' "$ns_file" | while read -r key; do
  last=${key##*.}
  forms=("$key" "$ns:$key" "$last")
  prefix=$key
  while [[ $prefix == *.* ]]; do prefix=${prefix%.*}; forms+=("$prefix"); done
  stem=$(printf '%s' "$last" | sed -E 's/[0-9]+.*$//')
  [[ $stem != "$last" && -n $stem ]] && forms+=("${stem}\${" "${stem}{{")

  hit=0
  for f in "${forms[@]}"; do
    if git grep -q -F --untracked "$f" -- src server scripts ':(exclude)locales'; then hit=1; break; fi
  done
  [[ $hit -eq 0 ]] && echo "$ns:$key"
done
```

The last-segment and prefix forms produce many false "alive" results for short, generic segments
(`title`, `label`). That is the safe direction. Review those by hand only if the orphan count matters.

When removing, remove the key from every locale in the same commit and run your locale parity
check. If that check compares only top-level keys, nested namespaces are not really checked; verify
leaf parity yourself.

## 6. Finding the last consumer with git

```bash
# Commits that added or removed the string anywhere in source
git log -S 'total_label' --format='%h %ad %s' --date=short -- src server

# Introducing commit of a file
git log --diff-filter=A --format='%h %ad %s' --date=short -- path/to/file.ts

# What the removing commit put in its place
git show <sha> --stat
git show <sha> -- path/to/screen.tsx
```

The commit that removed the last consumer tells you the verdict. If it moved the copy to a new key or
namespace, the old key is Covered. If a screen was rewritten and lost the text, check whether the new
screen still needs it (possibly Broken). A key added with the initial locale files and never consumed
is plain Dead.

## 7. Positive controls

Before trusting any empty result, run the identical command on a known-live name:

```bash
git grep -q -F --untracked 'aKnownUsedSymbol' -- src && echo "search works" || echo "SEARCH IS BROKEN"
```

```sql
-- must return at least one row, or the pattern is broken
select proname from pg_proc where prosrc like '%' || 'a_function_you_know_is_called' || '%' limit 1;
```

Common causes of a search that always returns empty:

- a shell alias or wrapper function that does not exist in the `/bin/sh` a script spawns
  (use `git grep`, which is always there)
- a glob that skips top-level files (section 2)
- regex escaping lost between shell, CLI and SQL, or the wrong boundary token (in Postgres regex,
  `\m` starts a word and `\M` ends it); prefer `LIKE` or `grep -F`
