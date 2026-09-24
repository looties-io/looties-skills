# Merge-time CI: reference skeleton

Read this when writing or reviewing the workflow, the required-checks configuration, or the guard test.
Adapt names and branches; keep the structure. Every choice below is explained in `SKILL.md` step 5.

## 1. The merge workflow

```yaml
name: CI

# Merge-time CI. Every commit is already checked by the local pre-commit hook,
# so no push starts this workflow. A merge is attempted by marking a draft pull
# request ready for review, the only pull-request event listened to, so every
# job runs in full and none is ever skipped (a skipped job counts as a passing
# required check). A push to a ready pull request leaves its new head without
# checks until the pull request goes back to draft and is marked ready again.
# workflow_dispatch runs are NOT attached to a pull request and never satisfy
# its required checks; dispatch only checks a branch.
on:
  pull_request:
    branches: [main]            # every branch you merge into with --auto
    types: [ready_for_review]
  workflow_dispatch:
    inputs:
      full_proof:
        description: Run the expensive proof whatever the change touches
        type: boolean
        default: false
  schedule:
    - cron: '23 5 * * 1'        # weekly: backs the diff-scoped proof

permissions:
  contents: read

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  # The main suite. Skipped on the schedule, which only exists for the proof.
  test:
    name: test
    if: github.event_name != 'schedule'
    runs-on: ubuntu-latest
    timeout-minutes: 40
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: npm }
      - run: npm ci
      - run: npm run typecheck
      - run: npm run lint
      - run: npm test
      - run: npm run build
      - run: npx playwright install --with-deps chromium
      - run: npx playwright test
      # Scores and reports that can never block a merge live in a scheduled
      # workflow, not here.

  # Fast static gates share ONE runner: each separate job would pay checkout,
  # setup and the one-minute billing minimum for 10-40 seconds of work.
  static:
    name: static checks
    if: github.event_name != 'schedule'
    runs-on: ubuntu-latest
    timeout-minutes: 20
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }    # secret scanning over full history
      - name: Secret scan
        run: ./scripts/secret-scan.sh
      - name: Dependency audit
        run: npm audit --omit=dev --audit-level=high
      - name: Dead code
        run: npm run check:unused
      - name: Docs (advisory, never fails)
        run: npm run check:docs      # must exit 0; see SKILL.md step 10

  # Heavy integration job. Runs at merge time AND on the weekly schedule.
  integration:
    name: integration
    runs-on: ubuntu-latest
    timeout-minutes: 30
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }    # the scope step diffs against the merge base
      - run: ./scripts/start-database.sh
      - run: ./scripts/run-db-tests.sh
      - name: Decide whether the expensive proof is in scope
        id: scope
        if: github.event_name != 'schedule' && !inputs.full_proof
        run: node scripts/proof-scope.mjs   # writes run=true|false to $GITHUB_OUTPUT
      - name: Expensive proof
        if: github.event_name == 'schedule' || inputs.full_proof || steps.scope.outputs.run == 'true'
        run: ./scripts/run-expensive-proof.sh
```

Note that skipping a **step** is safe; skipping a **job** reports a passing check. That is why the scope
decision lives inside the job.

## 2. The scheduled informational workflow

```yaml
name: Scheduled reports
on:
  schedule:
    - cron: '17 6 * * *'
  workflow_dispatch:
permissions:
  contents: read
concurrency:
  group: scheduled-reports
  cancel-in-progress: true
jobs:
  reports:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    steps:
      - uses: actions/checkout@v4
        with: { ref: main }
      - run: npm ci
      - run: npm run build
      - run: npx lhci autorun || true   # a score is a thermometer, not a gate
```

## 3. The diff-scope script, in outline

```js
// proof-scope.mjs: does this change reach anything the proof exercises?
// 1. Inputs that always require the proof: the proof itself, its config, this script.
// 2. Watched objects: parse them FROM THE PROOF SOURCE, so a new case widens the
//    scope with no second list to maintain.
// 3. Exclude broad fixtures that nearly every change names; the weekly run covers them.
// 4. Diff the branch against `git merge-base origin/main HEAD`:
//      changed files       -> rule 1
//      added/removed lines -> rule 2, ignoring the +++/--- headers
// 5. Print the reason and append `run=true|false` to $GITHUB_OUTPUT.
```

Before trusting it, replay it over the last few dozen merges and count how many it selects. Inspect the
extra hits of any broader variant; comments and unrelated identifiers are the usual false positives.

## 4. Required checks and auto-merge

Enable auto-merge on the repository:

```bash
gh api -X PATCH repos/OWNER/REPO -F allow_auto_merge=true
```

Ruleset payload (`ruleset.json`), created with `gh api -X POST repos/OWNER/REPO/rulesets --input ruleset.json`:

```json
{
  "name": "merge-time-ci",
  "target": "branch",
  "enforcement": "active",
  "conditions": { "ref_name": { "include": ["refs/heads/main"], "exclude": [] } },
  "bypass_actors": [
    { "actor_type": "OrganizationAdmin", "actor_id": 1, "bypass_mode": "always" }
  ],
  "rules": [
    {
      "type": "required_status_checks",
      "parameters": {
        "strict_required_status_checks_policy": false,
        "required_status_checks": [
          { "context": "test" },
          { "context": "static checks" },
          { "context": "integration" }
        ]
      }
    }
  ]
}
```

- `context` is the check run name, which is the job `name:` when one is set.
- `strict_required_status_checks_policy: true` re-proves the merge after the target moves, at the cost of
  one more run per update. Choose deliberately and record it.
- Drop `bypass_actors` if direct pushes to the branch should be refused. `OrganizationAdmin` with
  `actor_id: 1` exists only for organization repositories; on a personal repository use
  `{ "actor_type": "RepositoryRole", "actor_id": 5, "bypass_mode": "always" }` (the admin role).
- Confirm enforcement: `gh api repos/OWNER/REPO/rules/branches/main` must list the rule. Availability on
  private repositories depends on the plan.

## 5. The guard test

Any test runner works. The assertions are what matter:

```js
import { readdirSync, readFileSync } from 'node:fs';
import { parse } from 'yaml'; // YAML 1.2: the `on` key stays a string (js-yaml 1.1 may turn it into true)

const dir = '.github/workflows';
for (const file of readdirSync(dir).filter((f) => /\.ya?ml$/.test(f))) {
  const wf = parse(readFileSync(`${dir}/${file}`, 'utf8'));
  // `on` may be a string (`on: push`), a list (`on: [push]`) or a map.
  const on = typeof wf.on === 'string' ? [wf.on] : Array.isArray(wf.on) ? wf.on : Object.keys(wf.on ?? {});
  assert(!on.includes('push'), `${file} starts on push`);
  assert(!on.includes('pull_request_target'), `${file} uses pull_request_target`);
  if (file !== 'ci.yml') assert(!on.includes('pull_request'), `${file} starts on a pull request`);
  for (const [name, job] of Object.entries(wf.jobs ?? {})) {
    assert(job['timeout-minutes'] > 0, `${file}:${name} has no timeout`);
  }
}
const ci = parse(readFileSync(`${dir}/ci.yml`, 'utf8'));
assertDeepEqual(ci.on.pull_request.types, ['ready_for_review']);
// and: the scoped proof keeps its schedule and manual-override conditions
```

## 6. Agent procedure (for the repository's agent instructions)

```text
Open every pull request as a draft. Push all commits. Then:
  gh pr ready <n>
  gh pr merge <n> --auto --merge --delete-branch
After any further push:
  gh pr ready <n> --undo && gh pr ready <n>
  gh pr merge <n> --auto --merge --delete-branch   (returning to draft disarms auto-merge)
A PR opened non-draft by mistake: same undo-and-ready sequence.
Red is expected: fix locally, push, restart. Never merge with --admin.
Before calling a PR green, read ALL checks, not only the required ones.
```
