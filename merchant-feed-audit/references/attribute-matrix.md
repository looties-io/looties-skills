# Attribute requirement matrix

Read this before admitting a new category, seller segment or destination country to a feed (Step 4
and Step 5 of the skill), and when a disapproval names an attribute you thought was optional.

This matrix summarizes Google's product data specification as it applied to free listings in one
European audit. **It is a starting point, not the authority.** Requirements vary by destination
country, by destination (free listings versus Shopping ads) and over time. Open Google's current
specification for every attribute you change and record the date you checked it.

## How to read it

- **Required**: missing means the item is disapproved in that destination. No ranking trade-off.
- **Conditional**: required only when the stated condition holds. The condition is usually where
  teams get caught, because it depends on an account setting or a taxonomy path, not on the item.
- **Recommended**: missing costs ranking or matching quality, not eligibility.
- **Derive from**: the source of truth the value should come from. If the answer is "a new field we
  would have to invent", the item is not ready for the feed.

## Core attributes

| Attribute | Status | Derive from |
|---|---|---|
| `id` | Required | A stable internal identifier that never gets reused (a UUID, not a slug that can change) |
| `title` | Required | The title the landing page shows |
| `description` | Required | The description the landing page shows |
| `link` | Required | The canonical landing-page URL, the same one your canonical tag and sitemap use |
| `image_link` | Required | The first image your provenance record says is a real photograph (see Step 6) |
| `availability` | Required | Only states you track in real time; publish `in_stock` rows only and let removal do the rest |
| `price` | Required | The helper that computes the landing-page price, the Product structured data and the checkout subtotal |
| `condition` | Conditional: required for used or refurbished items | The condition field the listing already carries |
| `brand` | Conditional: required for new items in most categories | The brand record the listing joins to |
| `gtin` | Conditional: required when the manufacturer assigned one | A verified identifier only; never generate or guess |
| `mpn` | Conditional: required when there is no GTIN, for new items | Same rule as GTIN |
| `identifier_exists` | Conditional: `no` when an item has no GTIN and no MPN | Derived, so adding a real identifier flips it automatically |
| `google_product_category` | Recommended (Google assigns one if absent) | A reviewed mapping table from your categories to numeric taxonomy ids |
| `product_type` | Recommended | Your own merchandising path |

## Shipping and returns

| Attribute | Status | Derive from |
|---|---|---|
| `shipping_weight` | Conditional: required when the account prices delivery by weight (weight bands or carrier-calculated rates) | The parcel presets the carrier is quoted with, packaging included, rounded up |
| `shipping` (per item) | Optional when account-level shipping settings cover the item | Prefer the account setting as the single owner; do not invent a fixed per-item price |
| Return policy | Account-level setting in most setups | The published returns page, approved by whoever owns it legally |

Watch for this pattern: a required-when-configured attribute (`shipping_weight`) disapproves every
item the day someone switches the account's shipping service to weight bands. The feed did not
change and still broke. When you change account shipping settings, re-read this row.

## Apparel & Accessories (taxonomy node 166)

At the time of the audit, Google listed these as required for free listings for **all** products
under node 166, in the destinations that audit targeted. The branch is wider than clothing: Jewelry
(node 188) sits under it, Brooches & Lapel Pins (node 197) under Jewelry, and so do other
accessories. Walk the full taxonomy path of every node you map.

| Attribute | Status under 166 | Derive from |
|---|---|---|
| `color` | Required | A reviewed side table with a `source` column. Read the material in the photograph, not the print on it; text extraction names the colours of a printed logo as readily as those of the garment |
| `gender` | Required | The size or cut field if it already encodes it (for example a women's cut stored in the size value); otherwise a reviewed value. `unisex` is a valid answer, a guess is not |
| `age_group` | Required | Per item. If your data only supports one age group per category, leave out the categories where that is false (infant and toddler sizes) |
| `size` | Required for clothing and shoes subtrees | The stored size, normalized (strip prefixes you use for gender) |

## AI-generated content disclosure

| Attribute | When | Rule |
|---|---|---|
| IPTC `DigitalSourceType` in image metadata | Any AI-generated image you publish | Embed it in the file (for example as an XMP packet). A visible label does not replace it |
| `structured_title` / `structured_description` with a digital source type | Title or description written by a generator | Emit exactly one shape per item: either the plain field or the structured one, never both, so the disclosure cannot be ignored in favour of the plain value |

Images carrying overlays that are not part of the product (watermarks, promotional text, generator
badges) are refused regardless of disclosure. Exclude them from `image_link`; do not try to disclose
your way past them.

## Before you widen scope: a checklist

For each new category or segment:

1. Write down its numeric taxonomy id and its **full path**. Does any ancestor carry extra
   requirements (node 166 is the usual one)?
2. For each required and conditional attribute above, name the column it comes from. Any blank
   means the category stays out.
3. Check the account's shipping service. Weight-based pricing makes `shipping_weight` required.
4. Check destination countries. Only those checkout actually ships to.
5. Decide which items the new lane must hold out (unbuyable sellers, generated-only images, sizes
   that contradict the declared age group) and put each in the exclusion table with a reason.
6. Dry-run on production data in a rolled-back transaction and count what the lane would admit.
