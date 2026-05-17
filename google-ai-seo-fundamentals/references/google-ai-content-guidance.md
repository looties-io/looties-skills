# Google AI Content Guidance

Last checked: 2026-05-17

Primary source: https://developers.google.com/search/docs/fundamentals/using-gen-ai-content

## Core Rule

Google's position is content-quality based: automation and generative AI can be
acceptable when the result is helpful, reliable, and created for people. Using
automation primarily to manipulate rankings can violate Google's spam policies,
especially scaled content abuse.

## Review Checklist

- The page has a real audience purpose beyond ranking capture.
- AI-assisted text is fact-checked by a human before publication.
- Product details, visible image details, brands, event names, dates, prices,
  availability, and legal claims are accurate.
- The page does not imply first-hand experience, expertise, or review activity
  that does not exist.
- Titles, meta descriptions, and alt text are specific to the page and not
  keyword-stuffed.
- Structured data matches visible content and does not invent facts.
- The content adds something useful or specific beyond generic AI output.

## Metadata And Alt Text

AI can assist with titles, descriptions, and alt text, but the output must remain
accurate, distinctive, and relevant. Reject metadata that overpromises, repeats
keywords unnaturally, or describes image details that are not visible.

## Structured Data

Structured data must describe what users can see on the page. Do not generate
ratings, offers, authors, organizations, FAQs, products, prices, availability,
or image metadata unless those facts are visible, accurate, and supported by the
page or backend source of truth.

## Ecommerce AI Content Notes

When a site acts as an ecommerce merchant and uses Google Merchant Center:

- AI-generated images may require IPTC `DigitalSourceType` metadata.
- AI-generated product data such as title and description attributes may need to
  be specified and labeled separately.

Skip these merchant-specific checks for marketplaces or publishers that are not
submitting merchant product data.

## Red Flags

- Many near-duplicate pages generated from keyword variants.
- AI descriptions that guess brands, origin, condition, age, materials, or
  provenance from weak evidence.
- Fake authors, fake reviews, fake comparisons, or fake first-hand experience.
- Alt text that is written for keywords instead of accessibility and accuracy.
- JSON-LD that says more than the page visibly says.

## Recommended Output

When using this skill, report:

1. Safe to publish / edit before publishing / do not publish.
2. Highest-risk factual or policy issues.
3. Exact edits needed.
4. Optional quality improvements.
