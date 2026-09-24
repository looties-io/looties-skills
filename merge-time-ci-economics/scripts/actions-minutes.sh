#!/usr/bin/env bash
# Reconstruct GitHub Actions billed minutes for one repository from the Actions API.
#
# Read-only: it only issues GET requests through the GitHub CLI.
#
# Why reconstruct instead of reading the invoice: the account billing endpoints
# need a token scope (`user` for a personal account, org admin for an organization)
# that a CI or agent token usually lacks, and the invoice does not say WHICH
# trigger spent the minutes. Hosted runners bill every job separately, rounded UP
# to the whole minute, so summing ceil(job duration) per job reproduces the bill
# closely enough to rank causes.
#
# Usage:
#   scripts/actions-minutes.sh OWNER/REPO [DAYS] [OUT_DIR]
#
#   DAYS     window ending now, default 30
#   OUT_DIR  where jobs.jsonl and the reports are written, default a temp dir
#
# Output (printed and saved in OUT_DIR):
#   by-workflow-event.tsv  billed minutes per workflow and trigger event
#   by-job.tsv             billed minutes, run count and average per job name
#   by-branch.tsv          billed minutes per head branch and event (finds the
#                          long-lived pull request that re-runs on every push)
#   short-jobs.tsv         jobs that ran under 60 s (paid the one-minute minimum)
#   instant-fail.tsv       jobs that failed in under 10 s (read their annotations
#                          before touching YAML: often a billing block)
#
# Caveats, printed again at the end:
#   - Minutes are raw runner minutes. Private repositories apply OS multipliers
#     (historically Linux 1x, Windows 2x, macOS 10x) and larger runners bill at
#     their own rate; check the labels column and your plan's current rates.
#   - Public repositories on standard hosted runners are not billed at all.
#   - Jobs refused by a spending-limit block still show a few seconds of duration
#     and are counted as one minute here although nothing was billed.
#   - Self-hosted runners are not billed by GitHub; they are listed with their labels.
#   - The runs endpoint returns at most 1 000 runs for a query filtered by
#     `created`. If "Runs found" is 1000, shorten DAYS and run it per window.
#   - One jobs request per run: about 1 000 runs uses about 1 000 of the 5 000
#     hourly API requests.
#
# Requires: gh (authenticated with read access to Actions), jq.

set -euo pipefail

repo="${1:-}"
days="${2:-30}"
out="${3:-}"

if [[ -z "$repo" || "$repo" != */* ]]; then
  echo "usage: $0 OWNER/REPO [DAYS] [OUT_DIR]" >&2
  exit 2
fi
command -v gh >/dev/null || { echo "gh is required" >&2; exit 2; }
command -v jq >/dev/null || { echo "jq is required" >&2; exit 2; }

# GNU date and BSD date spell "N days ago" differently.
if since="$(date -u -d "${days} days ago" +%Y-%m-%dT%H:%M:%SZ 2>/dev/null)"; then
  :
else
  since="$(date -u -v-"${days}"d +%Y-%m-%dT%H:%M:%SZ)"
fi

if [[ -z "$out" ]]; then
  out="$(mktemp -d "${TMPDIR:-/tmp}/actions-minutes.XXXXXX")"
fi
mkdir -p "$out"
runs_file="$out/runs.jsonl"
jobs_file="$out/jobs.jsonl"
: >"$runs_file"
: >"$jobs_file"

echo "Repository: $repo"
echo "Window:     runs created since $since ($days days)"
echo "Output:     $out"
echo

# 1. Every run in the window, one JSON object per line.
gh api --paginate -X GET "repos/${repo}/actions/runs" \
  -f per_page=100 -f created=">=${since}" \
  --jq '.workflow_runs[] | {id, name, event, head_branch, status, conclusion, run_attempt, created_at}' \
  >"$runs_file"

run_count="$(wc -l <"$runs_file" | tr -d ' ')"
echo "Runs found: $run_count"
if [[ "$run_count" -ge 1000 ]]; then
  echo "WARNING: the API caps filtered run listings at 1000; totals are truncated. Use a shorter DAYS window." >&2
fi

# 2. Every job of every run, all attempts included (re-runs bill again).
n=0
while IFS= read -r run; do
  n=$((n + 1))
  id="$(jq -r '.id' <<<"$run")"
  gh api --paginate -X GET "repos/${repo}/actions/runs/${id}/jobs" \
    -f per_page=100 -f filter=all \
    --jq '.jobs[] | {name, run_attempt, status, conclusion, started_at, completed_at, labels, runner_name}' </dev/null |
    jq -c --argjson run "$run" '
      . as $job
      | ($job.started_at // null) as $s
      | ($job.completed_at // null) as $c
      | (if $s != null and $c != null
           then (($c | sub("\\.[0-9]+"; "") | fromdateiso8601) - ($s | sub("\\.[0-9]+"; "") | fromdateiso8601))
           else null end) as $secs
      | {
          workflow: $run.name,
          event: $run.event,
          branch: $run.head_branch,
          run_id: $run.id,
          job: $job.name,
          attempt: $job.run_attempt,
          conclusion: $job.conclusion,
          labels: ($job.labels | join(",")),
          seconds: $secs,
          # Skipped jobs never get a runner and bill nothing.
          billed: (if $secs == null or $job.conclusion == "skipped" then 0
                   elif $secs <= 0 then 1
                   else (($secs + 59) / 60 | floor) end)
        }' >>"$jobs_file"
  if ((n % 50 == 0)); then echo "  jobs read for $n / $run_count runs" >&2; fi
done <"$runs_file"

tsv() { jq -r '@tsv'; }

echo
echo "== Billed minutes by workflow and event =="
jq -s '
  group_by([.workflow, .event])
  | map({w: .[0].workflow, e: .[0].event, m: (map(.billed) | add), runs: (map(.run_id) | unique | length)})
  | sort_by(-.m)
  | (["minutes", "runs", "workflow", "event"]), (.[] | [.m, .runs, .w, .e])' "$jobs_file" -c |
  jq -r '@tsv' | tee "$out/by-workflow-event.tsv" | column -t -s $'\t'

echo
echo "== Billed minutes by job =="
jq -s '
  group_by([.workflow, .job])
  | map({w: .[0].workflow, j: .[0].job, m: (map(.billed) | add), n: length,
         avg: ((map(.seconds // 0) | add) / length / 60 * 10 | floor / 10),
         labels: (map(.labels) | unique | join(" | "))})
  | sort_by(-.m)
  | (["minutes", "jobs", "avg_min", "workflow", "job", "labels"]), (.[] | [.m, .n, .avg, .w, .j, .labels])' "$jobs_file" -c |
  jq -r '@tsv' | tee "$out/by-job.tsv" | column -t -s $'\t'

echo
echo "== Billed minutes by branch and event (top 15) =="
jq -s '
  group_by([.branch, .event])
  | map({b: .[0].branch, e: .[0].event, m: (map(.billed) | add), runs: (map(.run_id) | unique | length)})
  | sort_by(-.m) | .[:15]
  | (["minutes", "runs", "branch", "event"]), (.[] | [.m, .runs, .b, .e])' "$jobs_file" -c |
  jq -r '@tsv' | tee "$out/by-branch.tsv" | column -t -s $'\t'

echo
echo "== Jobs that ran under 60 s (each billed a full minute) =="
jq -s '
  map(select(.seconds != null and .seconds < 60 and .conclusion != "skipped"))
  | group_by([.workflow, .job])
  | map({w: .[0].workflow, j: .[0].job, n: length, secs: ((map(.seconds) | add) / length | floor)})
  | sort_by(-.n)
  | (["jobs", "avg_seconds", "workflow", "job"]), (.[] | [.n, .secs, .w, .j])' "$jobs_file" -c |
  jq -r '@tsv' | tee "$out/short-jobs.tsv" | column -t -s $'\t'

echo
echo "== Jobs that failed in under 10 s (read annotations first) =="
jq -s '
  map(select(.conclusion == "failure" and .seconds != null and .seconds < 10))
  | (["run_id", "seconds", "workflow", "job"]), (.[:20][] | [.run_id, .seconds, .workflow, .job])' "$jobs_file" -c |
  jq -r '@tsv' | tee "$out/instant-fail.tsv" | column -t -s $'\t'

total="$(jq -s 'map(.billed) | add // 0' "$jobs_file")"
cancelled="$(jq -s 'map(select(.conclusion == "cancelled") | .billed) | add // 0' "$jobs_file")"
echo
echo "Total reconstructed billed minutes: $total  (of which cancelled jobs: $cancelled)"
echo
echo "Caveats: raw runner minutes before OS multipliers; public repos are free on standard"
echo "runners; spending-limit refusals count as 1 minute here but billed nothing; self-hosted"
echo "runners are not billed by GitHub. For a check run's annotations:"
echo "  gh api repos/${repo}/check-runs/<job-id>/annotations"
