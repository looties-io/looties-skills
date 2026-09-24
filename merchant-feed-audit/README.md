# merchant-feed-audit

A skill for getting products into Google Merchant Center and keeping them there, by asking Google
what it decided before trusting anything you published.

Part of [looties-skills](https://github.com/looties-io/looties-skills), open-source agent skills by
[Looties](https://looties.io).

## The observation behind it

A product feed can be well formed, served, smoke-tested and green in CI for months while reaching
nobody. Local gates see the file. They cannot see whether the file is registered as a data source,
whether Google fetched it, or what Google decided about each item:

> **A valid feed is a file. A listed product is a decision Google made about that file.**

In one audit the feed was registered nowhere, and the account was publishing an automatic crawl of
the site instead, including other sellers' marketplace listings under the store's own shipping
settings. Once the real feed was registered, every item was refused for a single missing attribute.

## What it does

Gives you ten steps, from Google's side of the fence inward.

- **Ask Google first:** list data sources and their input type, last fetch and item count, account
  issues and per-destination product statuses through the Merchant API, before reading your runbook.
- **One source of truth:** register your feed as the primary source, turn autofeed off, delete
  leftover hand-made sources, and expect a drain period.
- **One reason code at a time:** group disapprovals by code, fix the largest first, leave
  `NOT_IMPACTED` advisories alone.
- **Required versus recommended:** know which attributes disapprove and which only cost ranking,
  including the apparel branch of the taxonomy that quietly contains jewelry.
- **Derive, do not invent:** price, weight, availability and taxonomy each come from the value
  checkout already depends on, or through a reviewed mapping table.
- **Image provenance:** trust the per-image record over summary flags, disclose allowed synthetic
  images in metadata, and look at the pixels.
- **Fail closed:** reviewed `NOT NULL` columns, an exclusion table with reasons, unbuyable items held
  out, categories left out rather than guessed.
- **Dry-run, rebuild on change, monitor:** a rolled-back production dry-run with asserted counts, a
  change queue so the feed never names deleted images, and a scheduled check that fails when Google
  says something is wrong.

**Best for:** products missing, disapproved or stuck in Merchant Center or free listings, first-time
feed setup, widening a feed to new categories or sellers, and Merchant API access errors.

## Install

```bash
npx skills@latest add looties-io/looties-skills --skill merchant-feed-audit
```

## Usage

```
Use $merchant-feed-audit to find out why our products are not showing in Google Shopping even though the feed validates.
```

## Contents

```
merchant-feed-audit/
|-- SKILL.md                        <- the workflow the agent loads
|-- README.md                       <- this file
|-- references/
|   |-- merchant-api.md             <- auth, access traps, read and write endpoints, triage recipe
|   `-- attribute-matrix.md         <- required, conditional and recommended attributes and their sources
|-- agents/
|   `-- openai.yaml                 <- UI metadata for agent runtimes
`-- evals/
    `-- evals.json                  <- realistic prompts for testing the skill
```

## License

MIT, see [LICENSE](../LICENSE).
