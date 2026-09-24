# Measurement protocol

Read this before the first measurement of a performance change, and again before writing the
report. Commands assume a Vite/Rollup-style `dist/` with a built `index.html`; adapt paths to your
bundler. Everything here is read-only against production.

## 1. Control the environment

- Same machine, same Node version, same lockfile, same Chrome and Lighthouse versions for every run.
  Record all four in the report.
- Nothing else running: no build, test suite, second browser or screen recording during a series.
- Same server for both builds. If the local server does not compress, say so in the report and do
  not compare its transfer sizes with production.
- Same environment configuration for both builds. Placeholder backend keys produce 401s and empty
  data, which changes both console audits and rendered layout.
- Freeze what you can for visual checks (time, animations, rotating text, dismissed prompts) in the
  capture harness only, never in the product.

## 2. Build the pair

```bash
# Run from the repository root. Outputs land next to the repository (../dist-before, ../dist-after).
# Base: the exact commit the change will merge onto, in its own worktree.
git worktree add ../perf-base <base-sha>
(cd ../perf-base && npm ci && npm run build && cp -r dist ../dist-before)
# Change: the exact head under review.
npm ci && npm run build && cp -r dist ../dist-after
```

Run the **full** production build, including prerender and any post-build step. Some breakages
exist only there (see SKILL.md, step 9).

## 3. Byte report

Find the entry from `index.html`, never by size or name:

```bash
grep -oE '<script[^>]+type="module"[^>]+src="[^"]+"' ../dist-before/index.html
grep -oE '<link[^>]+rel="stylesheet"[^>]+href="[^"]+"' ../dist-before/index.html
```

Raw, gzip and brotli in one pass (Node's zlib defaults, so the numbers are reproducible):

```bash
node -e '
const fs=require("fs"),z=require("zlib"),c=require("crypto");
for (const f of process.argv.slice(1)) {
  const b=fs.readFileSync(f);
  console.log([f,b.length,z.gzipSync(b).length,z.brotliCompressSync(b).length,
    c.createHash("sha256").update(b).digest("hex").slice(0,16)].join("\t"));
}' ../dist-before/assets/index-XXXX.js ../dist-after/assets/index-YYYY.js
```

Report these as "local encodings", not transfer sizes. For transfer sizes, read Resource Timing
(`encodedBodySize` and `decodedBodySize`) in a browser against the real host.

To see what the entry contains, generate source maps for the measurement build only (or use a
bundle visualizer) and list modules by size. Confirm a removed module is absent from the entry and
present in a dynamic chunk.

## 4. Paired Lighthouse runs

- N of at least 3 per route per build; 5 or more when the expected effect is small.
- Alternate order: A B B A A B ... so drift (thermal, network, backend) spreads over both builds.
- Save every JSON and HTML report with build, route and run index in the file name.

Fields to extract from each report (`lhr`):

| Value | JSON path | Kind |
|---|---|---|
| Score | `categories.performance.score` | Simulated lab |
| LCP, FCP, TBT, CLS | `audits["largest-contentful-paint"].numericValue`, etc. | Simulated lab (CLS is from the trace) |
| Observed FCP, LCP | `audits.metrics.details.items[0].observedFirstContentfulPaint`, `observedLargestContentfulPaint` | Observed lab |
| Unused JS / CSS bytes | `audits["unused-javascript"].details.overallSavingsBytes`, same for CSS | Estimate |
| Total transfer | `audits["total-byte-weight"].numericValue` | Lab transfer, depends on the server |
| Throttling method | `configSettings.throttlingMethod` | Confirms which kind you measured |

Report the **median of each metric independently** and its min to max range. Do not report the
metrics of the run with the median score; that mixes runs.

Exclusion filters must be written down before the series, applied mechanically, and reported with
their count. Excluded runs stay in the raw table, marked.

## 5. Applied-throttling check

Use when simulated metrics move against a change that should not slow the page, or when you need a
before/after timing claim at all. Example with Playwright and CDP, matching Lighthouse's nominal
mobile profile:

```js
const context = await browser.newContext({ viewport: { width: 412, height: 823 }, locale: 'en-US' });
const page = await context.newPage();
const cdp = await context.newCDPSession(page);
await cdp.send('Network.enable');
await cdp.send('Network.emulateNetworkConditions', {
  offline: false,
  latency: 150,                        // ms
  downloadThroughput: 1_638_400 / 8,   // bytes per second (1.6 Mbit/s)
  uploadThroughput: 750_000 / 8,
});
await cdp.send('Emulation.setCPUThrottlingRate', { rate: 4 });
await page.addInitScript(() => {
  window.__lcp = null; window.__shifts = [];
  new PerformanceObserver((l) => { for (const e of l.getEntries()) window.__lcp = {
    t: e.startTime, el: e.element?.outerHTML.slice(0, 120) }; })
    .observe({ type: 'largest-contentful-paint', buffered: true });
  new PerformanceObserver((l) => { for (const e of l.getEntries()) if (!e.hadRecentInput)
    window.__shifts.push({ t: e.startTime, v: e.value,
      nodes: e.sources.map((s) => s.node?.id || s.node?.nodeName) }); })
    .observe({ type: 'layout-shift', buffered: true });
});
await page.goto(url);
// Wait for the page's own readiness signal, then observe a fixed extra window (e.g. 2.5 s).
```

Rules:

- A fresh browser context per visit. Alternate before and after.
- Confirm the LCP element is the same element in every visit; if it differs, you are comparing
  different things.
- The shift list is an unwindowed diagnostic sum. Report it as such, not as official CLS.
- Lighthouse's own `--throttling-method=devtools` applies adjusted values (higher request latency,
  slightly lower throughput) to approximate its simulation. State which values you used.

## 6. Reproducing a layout shift

Intercept only the request that feeds the suspect region and hold it (for example 3 s), then
release it with a populated, an empty and an error response. Measure the position of the content
below before and after release. A populated shelf that moves content by hundreds of pixels while
empty and error states move it by zero proves the insertion is the cause, and gives you the
acceptance test for the fix.

## 7. Field data

**CrUX API** (needs an API key; returns 404 when the page or origin has too little traffic):

```bash
curl -s -X POST "https://chromeuxreport.googleapis.com/v1/records:queryRecord?key=$CRUX_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"origin":"https://example.com","formFactor":"PHONE",
       "metrics":["largest_contentful_paint","interaction_to_next_paint","cumulative_layout_shift"]}' \
  | jq '{period: .record.collectionPeriod, p75: (.record.metrics | map_values(.percentiles.p75))}'
```

Use `"url"` instead of `"origin"` for a single page. CLS p75 may come back as a string. The
`records:queryHistoryRecord` endpoint gives weekly history for trend lines. Data is a rolling 28-day
window, so a fix shows fully about four weeks after promotion.

**PageSpeed Insights** mixes both kinds on one page. The top section ("Discover what your real users
are experiencing") is CrUX field data; the section below is a single simulated lab run from a
Google data center. In the API:

```bash
curl -s "https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=https%3A%2F%2Fexample.com%2F&strategy=mobile" \
  | jq '{url: .loadingExperience.metrics, origin_fallback: .loadingExperience.origin_fallback,
         origin: .originLoadingExperience.metrics}'
```

In this API, CLS percentiles are the value times 100. When `origin_fallback` is true, the "page"
field data is actually the origin's. A PSI lab score that swings by ten points or more between runs is
often data center load (it shows up as TBT spikes), not your code; never compare one PSI lab run with another.

**First-party RUM**: the `web-vitals` library's `onLCP`, `onINP` and `onCLS` (the attribution build
names the element and the shifting node). Before adding a new collector, check that the existing
one actually receives events: consent defaults, ad blockers and cookieless modes can make an
analytics pipeline silently empty. Report p75 by device class and route, with sample size.

Thresholds for "good" at p75: LCP at or below 2.5 s, INP at or below 200 ms, CLS at or below 0.1.

## 8. Production revision check

```bash
curl -s https://example.com/ | grep -oE 'assets/index-[A-Za-z0-9_-]+\.js'
```

Compare with the entry name from the build you deployed. If it does not match, nothing you measure
on production is "after". Environment-specific builds can produce different hashes for the same
source; then compare a marker you control (a build id meta tag, for instance).

## 9. Report template

```
Change: <one line>          Base: <sha>   Head: <sha>   Production revision: <asset hash or "not promoted">
Environment: Node <v>, Chrome <v>, Lighthouse <v>, server <compressed|uncompressed>, runs N per route, order ABBA

Bytes (local encodings)
| Asset | Before raw/gzip/br | After raw/gzip/br | Change |

Simulated lab (median, range), per route
| Metric | Before | After |

Observed lab / applied throttling (median, range, LCP element)
| Metric | Before | After |

Field (source, period, form factor, p75, sample)
| Metric | Value | or "no field data" |

Claims: <only what the evidence above supports>
Not claimed: <e.g. no LCP improvement, CLS unresolved, no competitive lead>
Excluded runs: <rule, count> or "none"
Raw reports: <location>
```
