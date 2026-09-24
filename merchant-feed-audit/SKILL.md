---
name: merchant-feed-audit
description: "Use when products are missing, disapproved, pending or stuck in Google Merchant Center, Shopping or free listings, when building a product feed or widening one to a new category or seller segment, or when \"the feed is valid but nothing shows up\". Covers asking Google what it actually ingested before trusting your runbook (data sources, autofeed, fetch results, per-destination statuses), working disapprovals one reason code at a time, required versus recommended attributes including the apparel taxonomy trap, deriving every attribute from the field checkout already uses, image provenance and AI-image disclosure, failing closed, dry-running on production data, rebuilding on catalogue change, and a scheduled live-status check. Also use for Merchant API errors such as API keys rejected with 401, GCP_NOT_REGISTERED or V1BETA_RAMP_DOWN. Not for on-page Product structured data or general SEO (use google-ai-seo-fundamentals), nor for Google Ads bidding, budgets or campaign structure."
license: MIT
metadata:
  author: Looties
  version: "1.0.0"
---

# Merchant Feed Audit

A product feed that validates is a file. A product that shows up is a **decision Google made about
that file**, combined with account settings, a crawl of your landing pages, an image fetch and a
policy review. Every local check you own sees only the first of those. The typical failure is not a
malformed feed; it is a well-formed feed that nobody fetches, or one that is fetched and refused for a
reason your gates never model.

So this skill starts from Google's side of the fence, works the refusals it reports in order of size,
and only then widens the feed, one derivation at a time, with every new attribute tied to a source of
truth the business already depends on.

## Quick reference

| Intent or symptom | Go to | What to look at |
|---|---|---|
| Feed validates, nothing shows up | Step 1, Step 2 | Data sources and their input type; is your feed URL a `FILE` source at all |
| Products you never published appear | Step 2 | `AUTOFEED` source, `autofeedSettings.enableProducts`, leftover `UI` sources |
| Many items disapproved | Step 3 | Issues grouped by `code` and `severity`, largest `DISAPPROVED` first |
| Adding a category, seller segment or country | Steps 4, 5, 7 | Full taxonomy path, required attributes, the source column for each; `references/attribute-matrix.md` |
| Image refused or AI-image question | Step 6 | Per-image provenance record, the pixels, IPTC `DigitalSourceType` |
| Feed names deleted images or stale prices | Step 9 | Change queue and rebuild trigger |
| 401, 409 or registration errors from the API | `references/merchant-api.md` section 1 | Principal type, `registerGcp`, `v1` paths |
| Want a monitor that catches all of the above | Step 10 | Scheduled read-only status job |

## Step 1: ask Google first, not your runbook

Before reading your own documentation, read the live account through the Merchant API. Your runbook
describes an intention; the account holds the state. Answer these, in this order:

1. **Which data sources exist, and what is each one's input type?** `FILE` (a fetched URL), `API`,
   `UI` (created by hand in the console) or `AUTOFEED` (Google crawling your site on its own).
2. **For each file source: last fetch state, time and item count.** A source whose last fetch is days
   old, failed, or carried zero items is the answer to "why did nothing change".
3. **Account-level issues.** One account issue can suspend every product regardless of item quality.
4. **Per-product, per-destination status.** Approved, pending and disapproved countries per reporting
   context (free listings and Shopping ads are separate), plus item-level issues with severity.

Read `references/merchant-api.md` for the auth recipe, the endpoints and the four access traps that
cost hours (API keys rejected, a GCP project that must be registered by API call, a retired beta
version, a retired predecessor API). Do this step even if a runbook says the feed is live.

## Step 2: make one source of truth

Confirm that **your** feed is registered as a primary product source and is the one being fetched.
Then remove everything else:

- **Turn off autofeed** when you publish your own feed. Autofeed crawls your site and builds offers
  from whatever structured data it finds. On a marketplace, that includes listings from third-party
  sellers, which Google then publishes under the store's own merchant identity, shipping and return
  settings. You are neither the seller nor the shipper of those items.
- **Delete leftover `UI` sources** (test products created by hand, often without images).
- **Expect a drain period.** Offers from deleted sources linger for a while. Record the count and
  re-check rather than treating the leftovers as a new problem.

The generalization: two sources describing the same catalogue will disagree, and Google will not
tell you which one it believed.

## Step 3: work disapprovals one reason code at a time, largest first

Group item-level issues by `code` and `severity`, sort by count, and fix the top code before looking
at the next. One reason code usually has one root cause, and fixing it often clears most of the
account at once.

| Severity | Meaning | Action |
|---|---|---|
| `DISAPPROVED` | Item is not shown in that destination and country | Fix now, largest code first |
| `DEMOTED` | Shown with reduced reach | Fix when the disapprovals are gone |
| `NOT_IMPACTED` | Advisory, eligibility unaffected | Read once, usually leave alone |

A typical first code on a new account is `missing_shipping_weight`: the account's shipping service
prices delivery from weight bands, so Google cannot compute a shipping cost for an item without a
weight and refuses it. The fix is in the feed (a per-item weight), not in the shipping settings.

Resist "fixing" `NOT_IMPACTED` advisories such as `language_mismatch` or `low_image_quality` on
approved products. They do not affect eligibility, and changes made to silence them carry real risk.

## Step 4: know required from recommended before you widen scope

A missing **required** attribute is a disapproval. A missing **recommended** attribute costs ranking.
Treat the distinction as the first question for any new category you admit, not something you learn
from the disapproval wave.

The trap that catches most teams: under Google's specification, colour is required for free listings
across the whole **Apparel & Accessories** branch of the product taxonomy (node 166), and that branch
contains more than clothing. Jewelry (node 188) sits under it, and Brooches & Lapel Pins (node 197)
under Jewelry, so pins, badges and similar small accessories inherit the apparel requirements. Walk the taxonomy path of every node you map, not just
the leaf name.

Read `references/attribute-matrix.md` before admitting a new category. It lists the attributes, when
each is required, and the source each one should be derived from. Always re-check it against Google's
current product data specification, which changes.

## Step 5: derive each attribute from the field checkout already uses

Every attribute you send is a claim about what a buyer will experience. Derive it from the value the
purchase path already depends on, so the feed and checkout cannot disagree:

- **Price** from the same helper that computes the landing page price, the Product structured data
  and the checkout subtotal. Include mandatory fees the buyer always pays; exclude delivery if the
  account computes delivery separately.
- **Shipping weight** from the parcel presets the carrier is quoted with, packaging included.
- **Availability** only from states you actually track. If stock is not tracked in real time, do not
  claim it; publish only rows that are purchasable now and let removal from the feed do the rest.
- **Taxonomy** (`google_product_category`) through a **reviewed mapping table**, never an automatic
  mapping from your internal categories. Internal categories are merchandising labels chosen by
  people: in one catalogue a bomber jacket was stored under "Vests", so an automatic mapping would
  have published a jacket as a vest.
- **Attributes you do not collect** (colour, gender, age group) from a reviewed side table with a
  `source` column recording how each value was obtained, so a later automated pass can be told
  apart from a human reading.

Keep one source for structured data. If the page's Product markup and the feed are built by two code
paths, they will drift; see `google-ai-seo-fundamentals` for the structured-data honesty rules.

## Step 6: prove image provenance from the per-image record, and from the pixels

Google refuses images with overlays that are not part of the product (watermarks, promotional text,
generator badges), and requires machine-readable disclosure for AI-generated images it does allow.

- **Read the per-image provenance record, not a summary flag.** In one catalogue a legacy boolean
  "cover is AI-generated" flag disagreed with the per-image source record in both directions (7
  listings one way, 10 the other). Keying the feed off the flag would have published seven
  watermarked covers.
- **Exclude AI-staged or watermarked images** from the image slot, and fall back to the first image
  recorded as a real photograph. An item with none stays out.
- **For synthetic images you choose to publish**, embed the IPTC `DigitalSourceType` value (for
  example `trainedAlgorithmicMedia`) in the file's metadata. A visible label does not replace it.
  Adding an XMP chunk to a WebP need not re-encode the pixels.
- **Look at the pixels.** Some overlays exist only in the image: a crop or re-encode step can strip
  every provenance marker while the badge stays burned in. In one pass, four listings recorded as
  real photographs carried a generator overlay that no metadata-based rule could see.
- **Check bytes, not extensions or status codes**, when validating image URLs. Files named `.webp`
  may hold JPEG, and a single-page app answers 200 with HTML for any unknown path.

## Step 7: fail closed

The feed must refuse to publish rather than guess. Make omission the default outcome of missing data:

- Reviewed attributes live in `NOT NULL` columns, so an item cannot enter until someone fills them.
- Exclusions live in an **explicit table with a reason per row**, not in "we just left it out". The
  table survives refactors and tells the next person why.
- **Hold out items nobody can buy**: seller away, payouts disabled, unsupported destination country.
  An offer that cannot be purchased must not be advertised as in stock.
- **Leave a category out rather than guess.** In one catalogue, baby clothing sized "0-3 months" to
  "18-24 months" would have been declared `age_group=adult` because the lane declared one age group
  per category. Waiting for per-item data beat publishing a false age.
- **Never manufacture identifiers.** No verified GTIN or MPN means `identifier_exists=no`, derived
  automatically so that adding a real identifier flips it.

This is `impossible-by-design` applied to a feed: the unsafe item is unconstructible, not discouraged.

## Step 8: dry-run on production data, inside a rolled-back transaction

Local fixtures do not reproduce your real category distribution, image provenance mix or seller
states. Before shipping a feed change, run the generator against production inside a transaction
that is rolled back (the technique is owned by `ground-truth`), and assert:

- item count per lane (for example reviewed versus derived) against the number you expect;
- **zero generated or watermarked covers** in the image slot;
- every held-out item is absent;
- every apparel item carries colour, size, gender and age group.

A dry-run that prints counts without asserting them proved nothing.

## Step 9: rebuild on catalogue change, not only on a timer

Once a day is too slow when images can be deleted on edit. In one catalogue a daily rebuild was
serving eight `image_link` URLs that already answered 404, because the edit flow removed old photos
from storage immediately. The fix:

- every write that can change the feed (listing insert, delete, relevant column update, seller state,
  mapping or exclusion table write) appends a row to a **change queue**;
- a frequent job (every 15 minutes) regenerates only when the queue is non-empty, draining it
  **before** reading the catalogue so a change committed mid-run is kept for the next pass;
- the daily rebuild stays as a backstop for anything no trigger watches.

Derived values tied to images (such as a colour read from a photo) must be invalidated when the
image set changes, so the item leaves the feed until it is re-derived.

## Step 10: schedule a live-status check that asks Google

Your CI can prove the file is well formed. Only Google can say it was fetched and accepted. Run a
read-only scheduled job (after the feed rebuild and after Google's fetch) that **fails** on:

- any account-level issue;
- no file data source registered;
- last fetch not succeeded, older than your threshold (for example 48 hours), or with zero items;
- any disapproved product;
- zero products approved anywhere.

Report `DEMOTED` and `NOT_IMPACTED` issues as warnings grouped by code, not as failures. Make an
expired or revoked credential fail the job loudly: a monitor that silently stops authenticating is
indistinguishable from a healthy account. Keep this out of the per-commit gate; it needs network and
credentials. Endpoints are in `references/merchant-api.md`.

Also confirm the feed's own smoke test actually runs in some job. A test that exists in the
repository but is wired into no workflow protects nothing.

## Pitfalls from real audits

- **Registered nowhere for months.** One team's feed file passed every local and deployed check for
  months while the account published nothing: the only active sources were Google's autofeed and a
  hand-made test source, and the feed URL was registered as a data source nowhere. The account held
  over a hundred products against 8 intended items; the autofeed share included other sellers'
  marketplace listings, offered under the store's own shipping settings.
- **All items refused for one reason.** Once registered, all 8 items were disapproved for
  `missing_shipping_weight` alone. One reviewed column cleared the whole account.
- **Widening without the required attribute.** A marketplace lane that admitted apparel without
  colour would have produced roughly 108 disapprovals on an account that had just cleared its first
  policy review. An independent review caught it, along with three other defects (the provenance flag,
  the baby-size age group, and the smoke test wired into no job). Review feed changes before the
  first fetch, not after; see `agentic-peer-review`.
- **Text is not the product.** Extracting colour from descriptions named an olive cap "Black/White",
  because descriptions name the colours of a print as readily as those of the garment. Reading each
  photograph and naming the material, not the print, was what worked. Doing that for the held-back
  apparel took the feed from 158 to 269 items.

## Safety rules

- Read the account through the API with read-only calls when auditing. Creating, deleting or
  re-fetching a data source is a deliberate, announced change.
- Never copy production catalogue rows, seller data or account identifiers into fixtures, issues or
  commit messages. Report counts and codes.
- Do not add destination countries the console suggests unless checkout actually ships there;
  declaring a country you cannot serve produces a wave of shipping disapprovals.
- Do not claim availability, shipping prices, return windows or identifiers you do not hold. Leave
  account-level shipping and return settings as the single owner of those values.
- A lower weight or price in the feed than at checkout is a misrepresentation risk. Round towards
  what the buyer is actually charged.

## Verification

You are done when:

- the API shows exactly one primary product source for the feed, autofeed off, no leftover `UI`
  source, and a recent successful fetch with the expected item count;
- disapprovals are zero, or each remaining code has a named owner and reason;
- every admitted category's taxonomy path has been checked for inherited required attributes;
- a rolled-back production dry-run asserted per-lane counts and zero generated covers;
- the feed rebuilds on catalogue change, and a scheduled live-status check is green and has been
  seen to fail on a bad credential.

## Related

- `ground-truth`: the rolled-back transaction dry-run and "the repository is not the deployed state".
- `google-ai-seo-fundamentals`: AI-generated content and image labelling, and not inventing prices
  or availability in structured data.
- `google-ai-seo-optimization`: whether merchant surfaces are in scope for the site at all.
- `impossible-by-design`: the fail-closed patterns behind Step 7.
- `agentic-peer-review`: independent review of a feed change before it reaches Google.
- `provider-canary`: proving a third-party integration with a minimal real call before trusting it.
