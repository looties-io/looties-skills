---
name: website-ai-agent-readiness
description: Audit or implement website readiness for AI agents and answer engines, including llms.txt, llms-full.txt, index.md, OKF/Open Knowledge Format bundles, machine-readable pricing files, ai-index.json, sitemap.xml, robots.txt, schema alignment, static asset headers, and SEO smoke tests. Use when the user mentions AI agent readiness, agent-readable site, llms.txt, OKF, Open Knowledge Format, knowledge bundle, AI-search readiness, answer engine readiness, machine-readable pricing, or agent-readable website assets.
---

# Website AI Agent Readiness

## Overview

Use this skill to make a public website easier for AI agents, answer engines, browser agents, partners, and direct machine readers to understand. Treat these assets as discoverability and convenience infrastructure, not as guaranteed traffic levers.

Keep Google Search claims separate. Google AI Overviews and AI Mode do not require `llms.txt`, OKF, Markdown mirrors, machine-readable pricing, or special AI markup.

## Source First

- Read [references/agent-readable-stack.md](references/agent-readable-stack.md) when auditing or implementing the website asset stack.
- Read [references/okf-v0.1.md](references/okf-v0.1.md) when the task mentions OKF, Open Knowledge Format, knowledge bundles, or `okf.md`.

## Workflow

1. Set the scope and boundary.
   - Identify the canonical domain, important public page types, supported languages, pricing model, and source of truth for facts.
   - Separate Google SEO blockers from optional agent-readable assets in the report.
   - Skip private, draft, expired, retired, and user-specific URLs unless the user explicitly asks to expose them.

2. Inventory the current surface.
   - Check `robots.txt`, `sitemap.xml`, canonical URLs, structured data, public Markdown files, and static asset headers.
   - Look for `llms.txt`, `llms-full.txt`, `index.md`, `pricing.md`, `okf.md`, `ai-index.json`, `entities.json`, and similar agent-readable resources.
   - Confirm each machine-readable file is reachable, accurate, current, and linked from at least one adjacent discovery file.

3. Decide which assets belong.
   - Use `llms.txt` for a short agent briefing and canonical links.
   - Use `llms-full.txt` or `index.md` for fuller public context when the site has enough stable content to justify it.
   - Use `pricing.md` when price, fee, subscription, commission, or transaction terms matter.
   - Use `okf.md` only when an experimental knowledge bundle is useful and can be kept current.
   - Use `ai-index.json` or `entities.json` when structured public facts help agents reconcile pages, entities, or resources.

4. Author or update assets.
   - Write concise, factual, source-backed content with canonical absolute URLs.
   - Include last-updated dates or timestamps where freshness matters.
   - Mirror visible public facts; do not invent schema, prices, claims, availability, support terms, reviews, or guarantees.
   - Add an honest note when an asset is experimental or not required by Google Search.

5. Expose the assets.
   - Link related machine-readable files from `llms.txt`, `llms-full.txt`, `index.md`, `okf.md`, and any JSON index.
   - Add static hosting headers for Markdown, JSON, robots, sitemap, and content-signal policies when the platform supports them.
   - Keep sitemap and robots behavior aligned with what the site actually wants indexed.

6. Add regression coverage.
   - Add or update SEO/static smoke tests for file presence, parseability, canonical URLs, OKF frontmatter, pricing facts, stale or retired links, and header rules.
   - Test that agent-readable files do not make false Google Search claims.
   - Run the narrow SEO test suite first, then the broader build or smoke suite when the change affects routing or deployment output.

7. Report the result.
   - Mark each item as green, warning, blocker, or skipped.
   - Call out freshness risks and owner-maintained facts, especially pricing and legal policies.
   - Keep optional agent-readiness work separate from confirmed Google Search SEO issues.

## Guardrails

- Do not claim `llms.txt`, OKF, Markdown mirrors, or machine-readable pricing are Google Search requirements.
- Do not claim a crawler or answer engine will use an asset unless there is evidence.
- Do not create agent-readable files that drift from visible pages or backend sources of truth.
- Do not expose private routes, internal APIs, staging domains, customer data, or unpublished policy details.
