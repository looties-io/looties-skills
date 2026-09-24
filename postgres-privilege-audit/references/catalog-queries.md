# Catalog queries for a privilege audit

Generic SQL for each step of the procedure in `SKILL.md`, written for PostgreSQL 15 or
later (`security_invoker` views need 15). Try each query on a local copy first, inside a
transaction you roll back.

Conventions used below:

- `api_roles` is the list of roles a client-held credential can become. On Supabase and
  plain PostgREST that is `anon` and `authenticated`; on your stack it may be different
  (Hasura roles, a `web_user` role, a read-only reporting role). Edit the `values` list.
- `'public'` is the exposed schema. Add every schema your API serves.
- Run the discovery queries as the schema owner or a superuser. `information_schema`
  views only show privileges where the current role is the grantor or grantee, so a
  low-privilege role sees an incomplete picture. The `has_*_privilege` functions and
  `aclexplode()` over `pg_catalog` do not have that limitation.

Contents:

1. Relation matrix (table level, with RLS, policies, view mode)
2. Explicit column grants
3. Credential-like columns readable or writable by a browser role
4. Functions executable by a browser role
5. Default privileges (what the next object will be born with)
6. Views that run as their owner
7. Set-role probe as a specific user
8. Dry run that aborts with its evidence
9. Proving a view's output did not change
10. Fix migration shape
11. pgTAP suite and the catalog invariant
12. Finding consumers and caller-scoped writers in application code

---

## 1. Relation matrix

One row per relation and role. `table_level` is empty when the grant is column-scoped;
`readable_cols` tells you whether that is "no access" or "narrowed access".

```sql
with api_roles(role) as (values ('anon'), ('authenticated'))
select n.nspname as schema,
       c.relname as relation,
       case c.relkind when 'r' then 'table' when 'p' then 'table' when 'v' then 'view'
                      when 'm' then 'matview' when 'f' then 'foreign' end as kind,
       c.relrowsecurity as rls_on,
       (select count(*) from pg_policy p where p.polrelid = c.oid) as policies,
       coalesce((select option_value from pg_options_to_table(c.reloptions)
                  where option_name = 'security_invoker'), 'false') as security_invoker,
       r.role,
       concat_ws(',',
         case when has_table_privilege(r.role, c.oid, 'SELECT')   then 'S' end,
         case when has_table_privilege(r.role, c.oid, 'INSERT')   then 'I' end,
         case when has_table_privilege(r.role, c.oid, 'UPDATE')   then 'U' end,
         case when has_table_privilege(r.role, c.oid, 'DELETE')   then 'D' end,
         case when has_table_privilege(r.role, c.oid, 'TRUNCATE') then 'T' end) as table_level,
       (select count(*) from pg_attribute a
         where a.attrelid = c.oid and a.attnum > 0 and not a.attisdropped
           and has_column_privilege(r.role, c.oid, a.attnum, 'SELECT')) as readable_cols,
       (select count(*) from pg_attribute a
         where a.attrelid = c.oid and a.attnum > 0 and not a.attisdropped) as total_cols
from pg_class c
join pg_namespace n on n.oid = c.relnamespace
cross join api_roles r
where n.nspname = 'public'
  and c.relkind in ('r', 'p', 'v', 'm', 'f')
order by schema, relation, r.role;
```

Read it as follows:

- `rls_on = false` and any privilege: every row is exposed. Stop and fix first.
- `rls_on = true`, `policies = 0`: deny-all for browser roles. Usually intended (ledgers,
  queues, outboxes). A table-wide grant here is **latent**: one permissive policy added
  later turns it live.
- `table_level` empty but `readable_cols > 0`: a column-scoped grant. Do not report this
  as "no access".
- `T` (TRUNCATE) for a browser role: RLS does not apply to TRUNCATE. Revoke it.

## 2. Explicit column grants

```sql
select c.relname as relation, a.attname as column_name,
       acl.grantee::regrole as grantee, acl.privilege_type
from pg_attribute a
join pg_class c on c.oid = a.attrelid
join pg_namespace n on n.oid = c.relnamespace
cross join lateral aclexplode(a.attacl) acl
where n.nspname = 'public'
  and a.attacl is not null
  and acl.grantee <> 0                                   -- 0 = PUBLIC
  and acl.grantee::regrole::text in ('anon', 'authenticated')
order by 1, 2, 3, 4;
```

Note that `information_schema.role_column_grants` and `column_privileges` list a
**table-level** grant once per column as well (for SELECT, INSERT, UPDATE, REFERENCES).
That makes them the right source for "can this role touch this column at all", and this
`attacl` query the right source for "which columns were granted one by one".

## 3. Credential-like columns

Widen or narrow the name pattern for your schema. The policy text is printed next to each
hit so you can answer "who does this row go to" without a second query.

```sql
with api_roles(role) as (values ('anon'), ('authenticated'))
select c.relname as relation, a.attname as column_name, r.role,
       has_column_privilege(r.role, c.oid, a.attnum, 'SELECT') as can_select,
       has_column_privilege(r.role, c.oid, a.attnum, 'UPDATE') as can_update,
       c.relrowsecurity as rls_on,
       (select string_agg(p.polname || ': ' || coalesce(pg_get_expr(p.polqual, p.polrelid), 'true'), ' | ')
          from pg_policy p
         where p.polrelid = c.oid and p.polcmd in ('r', '*')) as select_policies
from pg_attribute a
join pg_class c on c.oid = a.attrelid
join pg_namespace n on n.oid = c.relnamespace
cross join api_roles r
where n.nspname = 'public'
  and c.relkind in ('r', 'p', 'v', 'm')
  and a.attnum > 0 and not a.attisdropped
  and a.attname ~* '(^|_)(token|secret|password|passwd|hash|otp|code|nonce|key|signature|ip|ip_address)$'
  and (has_column_privilege(r.role, c.oid, a.attnum, 'SELECT')
       or has_column_privilege(r.role, c.oid, a.attnum, 'UPDATE'))
order by 1, 2, 3;
```

Expect false positives (a carrier `code`, an idempotency `key`). Each hit needs a human
verdict: does the value authorize anything, and against whom?

## 4. Functions executable by a browser role

`prokind = 'f'` excludes aggregates, window functions and procedures. Keep that filter in
any loop that later calls `pg_get_functiondef()`, which raises on an aggregate.
Extension-owned functions are excluded through `pg_depend`.

```sql
with api_roles(role) as (values ('anon'), ('authenticated'))
select p.oid::regprocedure as function,
       r.role,
       p.prosecdef as security_definer,
       coalesce(array_to_string(p.proconfig, ','), '') as config,   -- look for search_path
       p.proacl
from pg_proc p
join pg_namespace n on n.oid = p.pronamespace
cross join api_roles r
where n.nspname = 'public'
  and p.prokind = 'f'
  and has_function_privilege(r.role, p.oid, 'EXECUTE')
  and not exists (select 1 from pg_depend d
                   where d.classid = 'pg_proc'::regclass and d.objid = p.oid and d.deptype = 'e')
order by p.prosecdef desc, 1, 2;
```

For every SECURITY DEFINER row, read the body from the live catalog
(`select pg_get_functiondef('public.fn(uuid)'::regprocedure)`), not from the migration,
and confirm it pins the caller (`auth.uid()` or equivalent) and sets `search_path`.

## 5. Default privileges

What the next table, sequence or function will be born with. Run this before trusting
any statement of the form "new tables are private by default".

```sql
select pg_get_userbyid(d.defaclrole) as for_objects_created_by,
       coalesce(n.nspname, '(all schemas)') as schema,
       case d.defaclobjtype when 'r' then 'tables' when 'S' then 'sequences'
            when 'f' then 'functions' when 'T' then 'types' when 'n' then 'schemas' end as object_type,
       case when acl.grantee = 0 then 'PUBLIC' else acl.grantee::regrole::text end as grantee,
       acl.privilege_type
from pg_default_acl d
left join pg_namespace n on n.oid = d.defaclnamespace
cross join lateral aclexplode(d.defaclacl) acl
order by 1, 2, 3, 4;
```

Two consequences to check on your own stack:

```sql
begin;
create function public.zz_probe() returns int language sql security definer
  set search_path = '' as 'select 1';
revoke all on function public.zz_probe() from public;
select has_function_privilege('anon', 'public.zz_probe()', 'EXECUTE');  -- true if a default ACL names anon
revoke all on function public.zz_probe() from public, anon, authenticated;
select has_function_privilege('anon', 'public.zz_probe()', 'EXECUTE');  -- false

create table public.zz_probe_t (id int);
select has_table_privilege('anon', 'public.zz_probe_t', 'SELECT');     -- true means new tables auto-grant
rollback;
```

Run the second block on **both** production and your CI replay. If the answers differ,
your CI is testing a different permission model from the one you ship to.

## 6. Views that run as their owner

A view without `security_invoker` checks base-table grants and RLS as its owner, not as the
caller. When the owner owns the base tables (the usual case in migrations) or has
`BYPASSRLS`, the base tables' RLS does not apply to anyone reading through the view.

```sql
with api_roles(role) as (values ('anon'), ('authenticated'))
select c.oid::regclass as view, r.role, pg_get_userbyid(c.relowner) as runs_as
from pg_class c
join pg_namespace n on n.oid = c.relnamespace
cross join api_roles r
where n.nspname = 'public'
  and c.relkind in ('v', 'm')
  and coalesce((select option_value from pg_options_to_table(c.reloptions)
                 where option_name = 'security_invoker'), 'false') not in ('true', 'on', '1')
  and has_table_privilege(r.role, c.oid, 'SELECT')
order by 1, 2;
```

Materialized views have no `security_invoker` option; they are always a snapshot readable
under the matview's own grants.

## 7. Set-role probe as a specific user

Owner-level sessions (SQL editors, most CLIs, migration runners) are not subject to column
grants or RLS, so they cannot show a grant problem. Become the role, with the identity
claims your policies read. On Supabase and PostgREST the claims live in
`request.jwt.claims`; adapt the setting name to whatever your `auth.uid()` equivalent reads.

```sql
begin;
select set_config('request.jwt.claims',
                  json_build_object('sub', '<owner-uuid>', 'role', 'authenticated')::text,
                  true);                                  -- true = local to this transaction
set local role authenticated;

select id, length(approval_token) as token_len            -- never print the value itself
from public.approval_requests;

reset role;
rollback;
```

A row with a non-null `token_len` is the proof. `42501 permission denied for column` is the
proof of the fix. Zero rows proves nothing: either the policy hid the row or the probe used
the wrong identity, so pick an identity that owns at least one row first.

## 8. Dry run that aborts with its evidence

Some SQL runners (for example management HTTP APIs that wrap a database) return only the
last statement's result set and discard `RAISE NOTICE`. A failing statement always comes
back. So put the migration and the probes in one transaction and end it with an exception
that carries the probe results: nothing commits, and the evidence is in the error text.

```sql
begin;

-- 1. The migration body, verbatim.
-- revoke all on public.approval_requests from anon, authenticated;
-- grant select (id, owner_id, status, created_at) on public.approval_requests to authenticated;

-- 2. Probes, as the roles that matter.
do $$
declare
  report text := '';
  v text;
begin
  perform set_config('request.jwt.claims',
          json_build_object('sub', '<owner-uuid>', 'role', 'authenticated')::text, true);
  perform set_config('role', 'authenticated', true);

  begin
    execute 'select length(approval_token)::text from public.approval_requests limit 1' into v;
    report := report || E'\n  token read as owner: ALLOWED (len ' || coalesce(v, 'null') || ')';
  exception when insufficient_privilege then
    report := report || E'\n  token read as owner: denied (' || sqlstate || ')';
  end;

  execute 'select status from public.approval_requests limit 1' into v;
  report := report || E'\n  status read as owner: ' || coalesce(v, '(no row)');

  perform set_config('role', 'none', true);   -- back to the session role

  -- Add: the full invariant scan (section 11), counts of affected rows, view hashes.
  raise exception 'DRY RUN (rolled back). Probes:%', report;
end $$;

rollback;   -- never reached; the exception already aborted the transaction
```

Rules: no statement in the block may have an effect outside the transaction (HTTP
extensions, `NOTIFY`, dblink, sequence advances you care about). Keep the block short:
`REVOKE` and `ALTER VIEW` take locks until the abort.

## 9. Proving a view's output did not change

Hash the full output as the role that reads it, before and after, inside one transaction.

```sql
begin;
set local role anon;
create temp table view_hash_before as
  select md5(coalesce(string_agg(v::text, '|' order by v::text), '')) as h
  from public.public_items_view v;
reset role;

-- the change: base-table policies, column grants, then
-- alter view public.public_items_view set (security_invoker = true);

set local role anon;
select (select h from view_hash_before)
     = md5(coalesce(string_agg(v::text, '|' order by v::text), '')) as unchanged
from public.public_items_view v;
reset role;
rollback;
```

The temp table is created while the role is `anon`, so `anon` owns it and can read it
back. Repeat for `authenticated` if signed-in users also read the view: their answer can
differ, because a `security_invoker` view now applies their policies and grants.

## 10. Fix migration shape

```sql
-- Withdraw everything the browser roles hold on the table. A table-level REVOKE also
-- removes matching column-level grants, so the token column ends with no grant at all.
revoke all on public.approval_requests from anon, authenticated;

-- Hand back only what the product reads or writes, column by column.
grant select (id, owner_id, status, created_at, decided_at) on public.approval_requests to authenticated;
grant update (status) on public.approval_requests to authenticated;   -- only if a policy uses it

-- Functions: name every role. REVOKE FROM PUBLIC does not remove named-role grants.
revoke all on function public.decide_request(uuid, text) from public, anon, authenticated, service_role;
grant execute on function public.decide_request(uuid, text) to service_role;
```

If new tables in your environment are **not** auto-granted, add explicit grants for every
role that legitimately reads the table, including the server-side role your backend jobs
use. If they **are** auto-granted, add the revokes. Either way, write the grants the table
needs instead of relying on whichever default the environment happens to have.

## 11. pgTAP suite and the catalog invariant

Two layers, because each sees something the other cannot: pgTAP runs against a replay in
CI and can fail a pull request; the scheduled catalog check runs against production and
can see drift nothing in the repository explains.

pgTAP, pinning the specific fix:

```sql
begin;
create extension if not exists pgtap;
select plan(4);

select ok(not has_column_privilege('authenticated', 'public.approval_requests', 'approval_token', 'SELECT'),
  'the requesting member cannot read approval_requests.approval_token');
select ok(not has_column_privilege('anon', 'public.approval_requests', 'approval_token', 'SELECT'),
  'anon cannot read approval_requests.approval_token');
select ok(has_column_privilege('authenticated', 'public.approval_requests', 'status', 'SELECT'),
  'the requesting member still reads the status');          -- the feature must survive
select ok(not has_function_privilege('authenticated', 'public.decide_request(uuid, text)', 'EXECUTE'),
  'members cannot call decide_request');

select * from finish();
rollback;
```

The invariant, pinning the class (usable both in pgTAP and in a scheduled production check):

```sql
do $$
declare
  v record;
  violations text := '';
  n int := 0;
begin
  for v in
    select rcg.grantee, rcg.table_name, rcg.column_name, rcg.privilege_type
    from information_schema.role_column_grants rcg
    where rcg.grantee in ('anon', 'authenticated')
      and rcg.table_schema = 'public'
      and rcg.column_name ~ '(^|_)token$'
      and rcg.column_name not in ('shipping_rate_token')   -- exclusion: a rate quote id, authorizes nothing
    order by 2, 3, 1, 4
  loop
    n := n + 1;
    violations := violations || format(E'\n  [%s] %I.%I: %s',
                                       v.grantee, v.table_name, v.column_name, v.privilege_type);
  end loop;

  if n > 0 then
    raise exception E'% bearer-token column privilege(s) held by a browser role:%\n'
      'Fix: revoke table-wide from the browser roles and re-grant display columns by name.',
      n, violations;
  end if;
end $$;
```

Because `role_column_grants` expands table-level grants per column, this also fails when
someone later grants the whole table. Run it as the owner (see the note at the top).

Also assert that the check is looking at something: an invariant of the form "this set is
empty" is also satisfied by a wrong schema name or an empty database. Add one assertion
that the scanned table count is above a floor:

```sql
select cmp_ok((select count(*)::int from pg_tables where schemaname = 'public'), '>', 20,
  'the invariant scanned a real schema');   -- set the floor well below your table count
```

## 12. Finding consumers and caller-scoped writers

The database cannot tell you who consumes a token or which server path runs as the
caller. Search the code. Adjust the patterns to your client library.

```bash
# Who matches on the column? (a bearer token's consumer)
rg -n "\.eq\(\s*['\"]approval_token['\"]" .
rg -n "approval_token\s*=\s*\\\$[0-9]" .           # raw SQL placeholders

# Who reads or writes the table at all?
rg -n "from\(\s*['\"]approval_requests['\"]" .
rg -n "approval_requests" --glob '*.sql' --glob '*.ts' --glob '*.py' .

# Clients that hold a privileged key but forward the caller's identity.
# With PostgREST, the Authorization header decides the role, not the apikey.
# Multiline and lazy, because the key usually comes from a call such as env.get(...).
rg -n -U --multiline-dotall "createClient\(.{0,400}?SERVICE.{0,400}?Authorization" .

# Clients reading with select('*') on a table you are about to narrow (breaks with 42501).
rg -n -U "from\(\s*['\"]approval_requests['\"]\)[^;]*select\(\s*['\"]\*['\"]" .
```

Also search the test directories: database test suites often read the table too, and they
are easy to miss when grepping only application sources.
