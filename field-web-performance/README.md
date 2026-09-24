# field-web-performance

A skill for web performance work where field data and observed traces decide, and simulated lab
scores are a thermometer, not a backlog.

Part of [looties-skills](https://github.com/looties-io/looties-skills), open-source agent skills by
[Looties](https://looties.io).

## The observation behind it

Look at a red Lighthouse report and a real trace of the same load side by side, and one pattern
dominates:

> **The number everyone was arguing about was a projection, and the work it implied could not
> reach the target anyway.**

In one audit the simulated LCP was 11 seconds and the observed LCP in the same run was half a
second. The report's own estimated savings for all unused code added up to less than half the gap
to the budget. Three of four recurring findings were not product defects. A change that removed
code "regressed" LCP in simulation and changed nothing under real throttling. A merged fix was
still not in production when the "after" numbers were being prepared.

## What it does

Gives you ten steps, from labeling numbers to confirming production.

- **Four kinds of number:** simulated lab, observed lab, applied-throttling lab and field (CrUX or
  RUM p75). Label every number and never mix kinds in one comparison.
- **Arithmetic first:** sum the report's estimated savings against the gap to budget as a ceiling
  check, so impossible targets do not become projects.
- **Harness before product:** placeholder keys, self-inflicted cache headers, host-only endpoints,
  uncompressed local servers and automation-browser paint stalls, ruled out before touching code.
- **Trace, then fix:** first paint, the LCP element, and which node shifted and what moved it. Ship
  only changes backed by a visible defect, field evidence or provably unnecessary startup code.
- **Honest measurement:** exact base revision, full production build, raw/gzip/brotli bytes apart
  from scores, paired alternating runs, per-metric medians with spread, no deleted runs, and an
  applied-throttling check when the simulation disagrees.
- **Keep it fixed:** a bundle-graph guard in the production build plus a browser check, and an
  asset-hash check that the revision actually reached production.

**Best for:** red Lighthouse or PageSpeed scores, "make the site faster" requests, performance pull
requests that need evidence, Core Web Vitals regressions, and competitor speed comparisons.

## Install

```bash
npx skills@latest add looties-io/looties-skills --skill field-web-performance
```

## Usage

```
Use $field-web-performance on our red Lighthouse issue before anyone starts trimming bundles.
```

## Contents

```
field-web-performance/
|-- SKILL.md                        <- the workflow the agent loads
|-- README.md                       <- this file
|-- agents/
|   `-- openai.yaml                 <- UI metadata for agent runtimes
|-- evals/
|   `-- evals.json                  <- realistic trigger prompts
`-- references/
    `-- measurement-protocol.md     <- paired runs, CDP throttling, CrUX and PSI field data, byte report
```

## License

MIT, see [LICENSE](../LICENSE).
