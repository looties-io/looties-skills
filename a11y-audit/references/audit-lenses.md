# Audit lenses: checklists, grep patterns, WCAG mapping

Four lenses. For each: what to look for, how to find it mechanically, and which WCAG 2.1
success criterion it maps to. Findings need `file:line` evidence, and greps over-match, so
confirm each hit by reading it.

Patterns assume a React and Tailwind source tree under `src/`. Adjust the paths and class
names to your stack; the checks themselves are framework-independent.

## Lens 1: keyboard navigation

| Check | How to find | WCAG SC |
|---|---|---|
| Click handlers on non-interactive elements | `rg -n --multiline '<(div\|span\|li\|img)[^>]*onClick' src/` then check each for `role="button"` + `tabIndex={0}` + Enter/Space `onKeyDown`. Find one correctly guarded example in your codebase and use it as the reference | 2.1.1 |
| Positive `tabIndex` (focus-order corruption) | `rg -n 'tabIndex=\{[1-9]' src/` must stay at zero occurrences | 2.4.3 |
| Focus outline suppressed without replacement | `rg -n 'outline-none\|focus:outline-none' src/`. Passes only if paired with `focus:ring`, `focus:border-*` or `focus-visible:ring`, or covered by a global rule in your base stylesheet. Check whether that global net covers form fields; a rule scoped to `button, a, [role="button"]` does not | 2.4.7 |
| Hover-only reveals | `rg -n 'group-hover:opacity-100' src/`. Tab-reachable but invisible unless also `focus-visible:opacity-100` (self) or `group-focus-within:opacity-100` (container) | 2.4.7 |
| Mouse-only custom widgets | Any `onMouseDown` or `onMouseEnter` select-or-activate path with no keyboard equivalent. Autocompletes need the full combobox pattern | 2.1.1 |
| Missing arrow-key patterns | `rg -n "key === 'Arrow" src/` across menus (`role="menu"`), tabs (`role="tablist"`), carousels. Tab plus Enter operability is degraded and lower priority; complete inoperability is a blocker | 2.1.1 |
| Drag-only interactions | Drag or reorder with no keyboard path. Provide move buttons revealed on focus | 2.1.1 |
| Hover side-effects without focus equivalent | `onMouseEnter` without a paired `onFocus`, common on prefetch-on-hover links | 2.1.1 |

## Lens 2: focus management

| Check | How to find | WCAG SC |
|---|---|---|
| Modal contract | Inventory `*Modal*`, `*Popover*`, `*Sheet*`, `*Drawer*` and lightboxes. Each needs focus-in on open, Tab trap, Escape close, focus restore to trigger, `role="dialog" aria-modal aria-labelledby`, and a scroll lock that RESTORES the previous overflow value rather than resetting it. All six should come from one shared hook; a modal not using it is a finding | 2.4.3, 2.1.2 |
| Focus restore exists at all | `rg -n 'previousActiveElement\|trigger\?\.focus' src/`. Zero hits outside the shared hook means no modal restores focus | 2.4.3 |
| Skip link | First focusable element on the page, `sr-only focus:not-sr-only`, targeting the main landmark's id | 2.4.1 |
| Route-change focus | On SPA navigation, focus must move to `<main>`, and the document title must update | 2.4.3 |
| Smooth scroll vs reduced motion | JS `scrollTo({behavior:'smooth'})` ignores CSS reduced-motion rules, so it must check `matchMedia('(prefers-reduced-motion: reduce)')` itself | 2.3.3 |
| Live regions | Toasts and status: `role="status" aria-live="polite"`; errors: `role="alert"`. Ad-hoc inline toasts are the usual gap. Loading states: `role="status"` plus `sr-only` text plus `aria-hidden` skeleton shapes | 4.1.3 |
| Backdrop click-close semantics | Backdrop `role="presentation"` is fine; the dialog PANEL must never be `role="presentation"`. Portaled modals need `e.stopPropagation()` plus `target === currentTarget` before closing, because React events bubble through the React tree rather than the DOM tree | 1.3.1 |

## Lens 3: content and readability

| Check | How to find | WCAG SC |
|---|---|---|
| One h1 per rendered state | `rg -c '<h1' src/pages/`. Multi-h1 files are usually mutually exclusive early-return branches, so verify rather than flag blindly; zero-h1 pages are real findings. Fix by promoting the top heading with unchanged classes, or adding an `sr-only` h1 | 1.3.1, 2.4.6 |
| Level skips or inversions | Sketch the rendered sequence per major page, looking for `h1` to `h3` skips and `h2` after `h3` | 1.3.1 |
| Contrast | Run `scripts/contrast.mjs` against your own config. Expect mid-scale neutrals to fail AA-normal on dark surfaces, and white text on saturated brand fills to fail nearly everywhere; dark text on brand fills usually passes. Record the measured floors in the audit so the next pass starts from numbers | 1.4.3 |
| In-text links distinguishable | Links inside prose need `underline underline-offset-2`, not `hover:underline` (axe rule `link-in-text-block`). Freestanding data links, such as a tracking number rendered in a card, are exempt | 1.4.1 |
| Text size floor | `rg -n 'text-\[(9\|10\|11)px\]' src/`. New code should floor at `text-xs` (12px). Flag tiny plus low-contrast plus uppercase combinations hardest | 1.4.4 |
| Rich text safety and alt text | Any HTML rendered from a CMS or user input must be sanitized, and images injected that way need alt attributes enforced programmatically | 1.1.1 |
| Reduced motion | `rg -n 'prefers-reduced-motion\|motion-safe' src/`. New animations gate with `motion-safe:` | 2.3.3 |
| Language | `<html lang>` and `dir` must track the active locale, and stay wired as the app shell is refactored | 3.1.1 |

## Lens 4: landmarks

| Check | How to find | WCAG SC |
|---|---|---|
| Exactly one `<main>` | `rg -n '<main' src/` must be 1, with an id the skip link targets and `tabIndex={-1}` | 1.3.1 |
| Every `<nav>` labeled | `rg -n '<nav' src/`. Each needs a translated `aria-label` that does not contain the word "navigation", or `aria-labelledby` pointing at a visible heading | 2.4.6 |
| No nav-in-nav | A `<nav>` wrapping another `<nav>` is landmark noise, so demote the styling wrapper to `<div>`. Check for tag-based CSS selectors before changing the tag | 1.3.1 |
| Content outside landmarks | Banners rendered between `</header>` and `<main>` need `role="region"` plus `aria-label` | 1.3.1 |
| Explicit role attributes | `role="banner|main|contentinfo"` on the matching semantic element is redundant. Implicit roles are preferred, and zero explicit ones is the healthy state | Nothing |

## Instruments (run all three, every audit)

1. The project's linter, filtered to its accessibility rules. Target: zero errors, zero
   suppressions, no inline disable comments for a11y rules.
2. `node scripts/contrast.mjs` (from the repository root, or with `--config`).
3. The end-to-end suite with an axe scan. Confirm the app actually mounts first: a
   behavioral test such as the skip-link one must pass, because page-only axe passes can
   be vacuous.
