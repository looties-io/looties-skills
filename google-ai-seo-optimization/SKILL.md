---
name: google-ai-seo-optimization
description: Google-specific SEO workflow for AI Overviews and AI Mode readiness. Use when auditing or optimizing a site for generative AI features on Google Search, including crawlability, indexability, snippet eligibility, Googlebot access, JavaScript SEO, structured data accuracy, Search Console checks, and mythbusting AEO/GEO tactics.
---

# Google AI SEO Optimization

Use this skill to optimize for Google's generative AI Search features by improving normal SEO foundations. For Google Search, AEO and GEO are not separate systems to hack; they are SEO applied to AI Overviews, AI Mode, and the broader Search experience.

## Source First

Read [references/google-ai-optimization-guide.md](references/google-ai-optimization-guide.md) when the task needs official Google-specific constraints, mythbusting, or audit criteria.

## Workflow

1. Set the Google boundary.
   - Confirm whether the task is about Google Search, or about other AI answer engines such as ChatGPT or Perplexity.
   - For Google Search, prioritize Googlebot access, indexing, snippet eligibility, content quality, and Search Console evidence.

2. Check technical eligibility.
   - Verify that important pages return healthy status codes and canonical URLs.
   - Check `robots.txt`, robots meta tags, canonical tags, sitemap inclusion, hreflang where relevant, and snippet controls.
   - Confirm pages are indexable and eligible for snippets. AI feature inclusion is not guaranteed even when requirements are met.
   - For JavaScript sites, inspect rendered HTML or browser-rendered DOM instead of relying only on static HTML.

3. Improve content usefulness.
   - Favor unique, first-hand, non-commodity content over summaries of generic web knowledge.
   - Organize pages for human scanning with clear headings, paragraphs, images, and video where useful.
   - Reduce duplicate, thin, parameterized, or near-empty pages that waste crawl attention.

4. Use structured data correctly.
   - Keep schema aligned with visible content and Google rich-result guidelines.
   - Add or fix structured data only where it supports the page type.
   - Do not add "AI schema" or over-markup pages solely for generative AI visibility.

5. Handle business and commerce surfaces only when relevant.
   - If the business is a merchant or local business, consider Merchant Center, product data, and Google Business Profile readiness.
   - Skip merchant-specific work when the site is not acting as a merchant or not sending product data to Google merchant surfaces.

6. Report with guardrails.
   - Separate confirmed issues, likely risks, and optional improvements.
   - Include a short regression check for the site: status, title, canonical, noindex, snippet controls, visible content, structured data, sitemap, and retired/private URL behavior.

## Ignore For Google Search

- `llms.txt`, Markdown mirrors, and special AI text files as requirements.
- Chunking content into tiny blocks only for AI systems.
- Rewriting pages only to target AI systems.
- Inauthentic third-party mentions.
- Special schema.org markup for AI Overviews or AI Mode.
- `Google-Extended` as a control for AI Overviews, AI Mode, or Google Search indexing.
