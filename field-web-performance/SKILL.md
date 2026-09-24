---
name: field-web-performance
description: "Use when a Lighthouse or PageSpeed score is red, when Core Web Vitals (LCP, CLS, INP) regress, when a performance pull request needs before and after evidence, or when comparing page speed against competitors. Sorts every number into simulated lab, observed lab, applied-throttling lab or field data (CrUX or RUM p75), checks the budget is reachable, triages the audit harness before the product, finds the real bottleneck in a trace, and ships only changes backed by a visible defect, field evidence or provably unnecessary startup code, measured in paired runs against the exact base revision. Triggers include \"make the site faster\", \"why is our Lighthouse score so low\", \"fix LCP\", \"our CLS is bad\", \"prove this PR is faster\", \"are we faster than competitor X\", \"PageSpeed says 40\", or a CI performance issue that keeps reopening. Not for accessibility findings in the same report (use a11y-audit), for code dead everywhere (use repo-wide-dead-code-sweep), or for backend query and API latency tuning."
license: MIT
metadata:
  author: Looties
  version: "1.0.0"
---

# Field Web Performance

A Lighthouse score is a **thermometer, not a backlog**. Field data (CrUX or your own RUM, at the
75th percentile) says what visitors experience. Observed traces say why. A simulated lab score is a
model's projection of one fast trace onto a slow phone, and it can be off by more than an order of
magnitude in either direction. Treat it as a signal to investigate, never as a list of work.

In one audit, the simulated LCP on the home page was 11,059 ms against a 6,000 ms budget. The
observed LCP in the same run was 531 ms. Neither number described real visitors, and the team
nearly spent weeks trimming bundles to move the first one.

The point of this skill is to make every performance claim traceable to the right kind of number,
and to stop work that cannot move the metric that matters.

## Quick reference

| Situation | Go to | Look at |
|---|---|---|
| Someone quotes a number | Step 1 | Its kind: simulated, observed, applied-throttling or field |
| Red budget, "fix the report" | Step 2 | Sum of estimated savings vs gap to budget |
| Console errors, bfcache, transfer size, paint stall in CI only | Step 3 | Does it reproduce on production in an ordinary browser? |
| Slow first paint, bad LCP, CLS | Step 4 | Trace: first frame, LCP element, what was inserted above the shifted node |
| Deciding whether to ship a fix | Step 5 | Visible defect, field evidence, or unnecessary startup code |
| PR needs before/after numbers | Steps 6-7, [`measurement-protocol.md`](references/measurement-protocol.md) sections 2-4 | Exact base build, byte table, paired ABBA runs |
| Simulation says a smaller page got slower | Step 8, protocol section 5 | CDP-throttled medians and LCP element identity |
| Keeping a module out of the entry | Step 9 | Graph guard plus browser request check |
| "Is it live? Did users benefit?" | Step 10, protocol sections 7-8 | Asset hash in production HTML, CrUX 28-day window |
| Competitor speed table | Competitor comparisons | Equal conditions, or CrUX p75 |

## Step 1: sort every number into one of four kinds

Before discussing any metric, label it. Most performance arguments are two people quoting different
kinds of number at each other.

| Kind | Where it comes from | What it can prove | What it cannot prove |
|---|---|---|---|
| Simulated lab | Lighthouse default (`throttlingMethod: simulate`, the Lantern model) | Relative ordering of opportunities in one trace | Absolute timings, or a regression, on its own |
| Observed lab | The unthrottled trace inside the same report (`observedLargestContentfulPaint`, etc.) | What the page did on that machine and network | What a phone on a slow network sees |
| Applied-throttling lab | Real CDP network and CPU throttling during the load | A before/after difference under controlled slow conditions | Field experience, or the spread of real devices |
| Field | CrUX (PageSpeed "Discover what your real users are experiencing" section, CrUX API) or first-party RUM, p75 | What visitors experience, by device class | Why, or which commit caused it |

Rules that follow from the table:

- Never put two kinds in the same column of a table, and never subtract one kind from another.
- A fast observed-lab number disproves a scary simulated number; it does not prove visitors are fast.
  One review had to correct its own earlier claim that the 531 ms observed value "is what users see".
- Field data is the only kind that can justify saying "users are affected". If there is none (low
  traffic sites often have no CrUX record), say "field performance is unknown", not "fine".
- Say which page, form factor, revision and date every number belongs to.

## Step 2: do the arithmetic before the work

Lighthouse prints an estimated saving next to each opportunity. Sum the relevant ones and compare
the total to the gap between the current simulated value and the budget.

In one audit, all unused JavaScript was estimated at 1,800 ms and all unused CSS at 600 ms: about
2.4 s of possible savings against a 5 s gap. Perfect work on both could not reach the budget. That
became a standing decision: a red budget alone does not schedule work.

Use the sum as a **ceiling check only**. The estimates overlap and interact on the critical path, so
they are not additive guarantees. A later review of the same decision made the opposite point too:
an independently verified improvement is worth shipping even if it does not turn the budget green.
The arithmetic stops fantasy projects; it does not veto real ones.

## Step 3: triage the harness before the product

Audit setups generate findings that no visitor ever sees. Check each finding against the harness
first. In one batch of automated performance issues, **3 of 4 recurring findings were not product
defects**: two came from the audit environment and one from a deliberate configuration choice.
Harness-made findings seen across audits:

- **Console errors** were a 404 on an analytics script path that only the hosting platform serves.
  The bare static server in CI did not have it. In an earlier run, the "errors" were 401s from a
  build made with placeholder backend keys.
- **Back/forward cache blocked** was caused by the audit server's own `Cache-Control: no-store`
  header. Production never sent it. Switching the harness to `no-cache` fixed the finding.
- **A paint stall of about 2.4 s** on every mobile run turned out to be the automation browser.
  Plain headless Chrome never stalled. Windowed Chrome and Lighthouse-driven Chrome did, by a
  near-constant ~2.37 s. Blocking all JavaScript, fonts and images left the stall unchanged. An
  in-page probe showed timers running normally while the first animation frame arrived at 1.31 s.
- **Transfer size** looked 6x worse in CI because the local server did not compress. The same
  stylesheet was about 28 KB encoded and 172 KB decoded in production.

For each finding, ask: does it reproduce against the production URL in an ordinary browser? If
not, fix the harness and write down why, so the finding is not re-litigated next month. Then keep
the fix mechanical (a stub route, a header) and test it.

## Step 4: find the real bottleneck in a trace

Scores do not tell you what to change. A trace does. Answer three questions with evidence:

1. **When does the first paint happen, and what is blocking it?** Look for the gap between
   resources finishing and the first frame. One audit found an inline loading skeleton that never
   painted at all, because the app replaced it synchronously before the browser could paint.
2. **What is the LCP element?** Read it from the trace or a `largest-contentful-paint` observer.
   In one throttled reproduction, the LCP element was the loading skeleton's background image. The
   metric was measuring the placeholder, not the moment products became visible.
3. **Which node shifted, and what moved it?** The node a CLS audit names is usually the victim.
   Walk the render chain to find what was inserted above it. In one case a 0.328 shift on a content
   section came from a lazily loaded shelf above it: the lazy boundary's fallback was `null`, and
   the component itself also returned `null` while its data loaded. Two zero-height phases, one
   visible insertion. Fixing only one of the two leaves the shift in place.

Reproduce timing-dependent defects under throttling, with the delayed-response recipe in
[protocol section 6](references/measurement-protocol.md#6-reproducing-a-layout-shift). Three unthrottled production checks showed no
shift above 0.01. The same page under throttling shifted by 0.328. A fast-machine smoke test cannot
disprove a race.

## Step 5: fix only what clears the bar

A change qualifies when it has at least one of:

- A **reproducible, user-visible defect**, such as a layout shift you can trigger with a delayed
  response, a blank first screen, or an interaction that stalls.
- **Field evidence** that real users are affected, segmented by device.
- **Startup code that is provably unnecessary**: a module in the entry bundle that the first render
  never calls (an image encoder only used on upload, a page's rendering code dragged in by a
  footer's count import).

Everything else is score chasing. Two constraints apply on top:

- **Do not trade away owner-mandated behavior for a score.** Deferring the analytics tag, delaying
  session restore or hiding products until idle can all improve a lab number, and each may be
  forbidden by a product decision. Ask before touching them, and record the answer.
- **Check that the fix does not move the defect.** A fixed-height placeholder for a shelf that may
  be empty trades an insertion shift for a collapse shift, or leaves a permanent blank. Define the
  loading contract for pending, empty, failed and loaded states first.

## Step 6: measure against the exact base revision

The comparison is only as good as its baseline.

- Build the **exact base commit** and the change with the same toolchain, lockfile and environment
  configuration, using the **full production build** including every post-build step.
- Identify the entry chunk by reading the built `index.html`, not by picking the largest file whose
  name looks like an entry.
- Report bytes as **raw, gzip and brotli, separately**, and say they are local encodings, not
  captured transfer sizes. Report them in a different table from scores.
- Keep a hash of assets that should not change (the stylesheet, for example) and show they did not.

In one change, the entry went from 574,967 to 508,011 raw bytes (11.6% smaller, 13.8% gzip, 13.7%
brotli), with a byte-identical stylesheet. That was the claim. Nothing about LCP was claimed.

The protocol, commands and a report template are in
[`references/measurement-protocol.md`](references/measurement-protocol.md). Read it before running
the first measurement, not after.

## Step 7: paired runs, medians, no deleted runs

- Run **N paired runs**, alternating before and after (ABBA order), on an idle machine with no
  build or test suite running alongside.
- Report the **median per metric** (not the metrics of whichever run had the median score) and the
  spread (min to max) of every metric.
- Keep and publish **every run**. If a filter excludes runs, it must be declared before measuring,
  mechanical, and reported with the count it excluded. Example of a legitimate filter: excluding
  lab runs with observed FCP above 1,500 ms on a machine known to produce the windowed-browser
  stall. Do not carry that filter into real throttled tests, where a slow FCP may be genuine.

## Step 8: when the simulation disagrees, apply real throttling

If simulated numbers move against a change that cannot plausibly slow the page (a smaller identical
page, for example), do not report a regression and do not ignore it. Run an applied-throttling
check with CDP network and CPU throttling, fresh browser contexts and alternating order.

In one review, the simulated LCP of a legal page worsened from 8.58 s to 11.18 s after a change that
only removed code. Under applied throttling, the medians were 4,908 ms before and 4,904 ms after,
with the same paragraph as LCP every time. Conclusion recorded: no LCP claim either way. The real,
defensible saving was 11.6% of the entry bundle.

## Step 9: guard the bundle graph, then check the browser

Once an optional module leaves the entry, stop it creeping back. Add a check to the production build
that walks each entry's static imports, across shared chunks and every entrypoint, and fails when a
forbidden module appears. Allow it in dynamically imported chunks. Prove the guard fails on the old
code before trusting it.

A static graph check is necessary, not sufficient. **A dynamic import can still be called eagerly**
at startup, and the graph would look perfect. Load the page in a browser and assert the optional
chunk is not requested until the feature is used.

Also run the **real production build as a gate** for any change near startup code. Some breakages
exist only there, while type checks and tests stay green:

- A CSS framework's `theme()` call with a path that does not resolve can silently drop the entire
  hand-written rule. Every element keeps its class; the class matches nothing.
- A prerender script that runs outside the bundler cannot read bundler-only environment
  (`import.meta.env`). Statically importing a module that reads it at load time breaks the build,
  while the test runner, which provides that environment, stays green. In one case several hundred
  test files passed on the commit that broke the deploy.

## Step 10: confirm the revision reached production

A merge is not a promotion. Before claiming anything about production, fetch the production HTML
and check that it references the new entry asset hash.

In one review, the change had been merged to the integration branch, and production still served
the old entry bundle and the old skeleton markup. Any "after" measurement taken then would have
measured the "before" code.

After promotion, measure the public URL with the same protocol, and watch field data over its
collection window (CrUX uses a rolling 28 days) before saying users benefited. CrUX, PageSpeed
Insights and RUM queries, with their unit quirks, are in
[protocol section 7](references/measurement-protocol.md#7-field-data).

## Competitor comparisons

A comparison table is only valid if the conditions are equal. One team's table ranked four sites,
and none of these held:

- Their own site ran on localhost without compression; competitors ran over their CDNs.
- One competitor showed a country selector and another a cookie dialog, so different visible
  states were measured.
- Their own site got three runs with a selection rule; each competitor got one.
- The pages were not equivalent journeys (a marketing landing page against product grids).
- On a later attempt, one competitor returned HTTP 403 on all three runs. That is a missing value,
  not a score.

Measure all sites from the same location, device profile, network, consent state and run count,
record screenshots of what was measured, and reject challenge or error pages. Field data from CrUX
is the fairest comparison when every site has a record. Until then, claim no lead.

## Pitfalls

| Pitfall | Why it misleads | Do instead |
|---|---|---|
| Treating the CI score as a to-do list | Issues that reopen on every run for deliberate choices (hidden source maps, for instance) teach people to ignore all of them | Classify accepted diagnostics explicitly in the audit config |
| Chasing unused CSS per page | One global stylesheet always looks mostly unused on any single route | Treat page coverage as a hint, never as proof a rule can be deleted |
| A unit test asserting a CSS class as proof CLS improved | The class can be present and the shift unchanged | Browser trace with a delayed response ([protocol section 6](references/measurement-protocol.md#6-reproducing-a-layout-shift)) |
| Local score vs production score as before/after | Different server, compression and network: a different experiment | Same server for both builds, then a separate production check |
| Comparing two PageSpeed lab runs | Data center load shows up as TBT swings of ten points or more | Field section of PSI, or your own paired runs |
| Promising a score | The simulation is not under your control | Promise a measured byte or trace change; report scores as observed |

## Safety rules

- Measure production read-only. Do not submit forms, create orders or write data to get a trace.
- Do not change analytics, consent, session, cart or source-map behavior to improve a metric
  without an explicit owner decision.
- Never delete or cherry-pick runs after seeing them.
- Do not close automated performance issues by hand to make a dashboard green; change the
  monitoring policy and say "tracking moved", not "fixed".

## Verification

You are done when:

1. Every number in the write-up is labeled with its kind, page, form factor, revision and date.
2. Each harness finding is either fixed at the harness with a note, or shown to reproduce against
   production.
3. Each shipped change cites its bar (visible defect, field evidence, or unnecessary startup code)
   and has a test that failed before the fix.
4. Byte tables (raw, gzip, brotli) and score tables are separate, against the exact base revision,
   with all runs retained and medians plus spread reported.
5. Any simulated movement against the change was checked under applied throttling.
6. The production HTML references the new asset hash, and the write-up says what field data will
   confirm and when.

## Related

- `ground-truth`: the same discipline of confirming a finding against the running system before
  assigning it a severity.
- `impossible-by-design`: for turning "keep the encoder out of the entry bundle" into a build that
  fails, instead of a convention.
- `harness-testing`: for testing the audit harness's stubs and filters like any other code.
- `repo-wide-dead-code-sweep`: when the unnecessary startup code is actually dead code everywhere.
- `a11y-audit`: accessibility findings share the same reports but need their own scoped review;
  reduced-motion behavior matters when deferring animations or video.
- `google-ai-seo-optimization`: page experience as one input to search visibility; field data is
  what search systems see.
- `merge-time-ci-economics`: where a slow, noisy performance job belongs (scheduled, not per
  commit).
