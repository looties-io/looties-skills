# Agent-Readable Website Stack

Use this reference when auditing or implementing public files that help agents and machine readers understand a site.

## Core Assets

| Asset | Purpose | Use When |
|---|---|---|
| `robots.txt` | Crawler permissions and sitemap discovery | Every public site |
| `sitemap.xml` | Canonical URL discovery | Every indexable site |
| `llms.txt` | Short AI-agent briefing with canonical links | The site wants a compact agent entrypoint |
| `llms-full.txt` | Longer public context bundle | The site has stable docs, policies, or product detail |
| `index.md` | Markdown mirror of key public pages | Agents benefit from clean text outside the app shell |
| `pricing.md` | Machine-readable fees, plans, commissions, limits | Pricing or transaction terms influence answers |
| `okf.md` | Experimental Open Knowledge Format bundle | A structured knowledge bundle can be maintained |
| `ai-index.json` | Structured index of pages, entities, and documents | JSON helps reconcile resources programmatically |
| `entities.json` | Public entity list or dataset | The site has important brands, people, events, products, or locations |
| `_headers` or platform config | Content types, caching, content-signal headers | Static host supports explicit headers |

## Implementation Rules

- Prefer root-level, stable, unauthenticated URLs for public agent assets.
- Use absolute canonical URLs inside machine-readable files.
- Include last-updated dates on files with pricing, policies, availability, or claims that can change.
- Link agent-readable files to each other so a crawler or browser agent can discover the full set from one file.
- Keep files concise enough to be useful. Large mirrors should be split or summarized when they become noisy.
- Reuse visible website copy and backend facts instead of creating a separate invented narrative.

## Pricing Files

Create `pricing.md` when the site has fees, plans, commissions, buyer fees, seller fees, subscriptions, quotas, usage limits, cancellation terms, or transaction protections.

Include:

- Who pays.
- Fixed and percentage fees.
- Currencies and conversion behavior.
- Free tiers or free listing rules.
- Taxes, duties, shipping, or third-party pass-through costs.
- Human-readable pricing and policy page links.
- A clear last-updated date.

## Static Header Checks

When the host supports headers, verify:

- Markdown files use a readable text or Markdown content type.
- JSON files use `application/json`.
- `robots.txt` uses `text/plain`.
- `sitemap.xml` uses XML content type.
- Content-signal headers are emitted from headers when robots validators reject unknown directives.
- Caching is not so aggressive that pricing or policy files stay stale after updates.

## Smoke Test Checklist

Add tests that fail when:

- A required machine-readable file is missing.
- OKF frontmatter is absent or malformed.
- Pricing facts drift from known constants.
- Canonical URLs point to staging, localhost, retired, or private routes.
- `llms.txt` omits newly added machine-readable resources.
- JSON files stop parsing.
- Headers for important public files are removed.
- Files claim Google requires assets that Google does not require.

## Report Shape

Separate findings into:

1. Confirmed blockers: broken URLs, stale pricing, malformed JSON, blocked crawl paths.
2. Gaps: missing useful assets, missing cross-links, missing tests.
3. Optional bets: OKF bundles, extra Markdown mirrors, entity datasets.
4. Google boundary: what is normal Google SEO versus non-Google agent-readiness.
