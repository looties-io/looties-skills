# Audit lenses — checklists, grep patterns, WCAG mapping

Four lenses. For each: what to look for, how to find it mechanically, and which WCAG 2.1
success criterion it maps to. Findings need `file:line` evidence; greps over-match, so
confirm each hit by reading it.

## Lens 1 — Keyboard navigation

| Check | How to find | WCAG SC |
|---|---|---|
| Click handlers on non-interactive elements | `rg -n --multiline '<(div\|span\|li\|img)[^>]*onClick' src/` — then check each for `role="button"` + `tabIndex={0}` + Enter/Space `onKeyDown` (the repo's canonical guarded example: `SwagCard.tsx` card) | 2.1.1 |
| Positive `tabIndex` (focus-order corruption) | `rg -n 'tabIndex=\{[1-9]' src/` — must stay at zero occurrences | 2.4.3 |
| Focus outline suppressed without replacement | `rg -n 'outline-none\|focus:outline-none' src/` — pass only if paired with `focus:ring`/`focus:border-*`/`focus-visible:ring`, or covered by the global net in `index.css` (`button/a/[role="button"]:focus-visible`) — note the net does NOT cover form fields | 2.4.7 |
| Hover-only reveals (`opacity-0 group-hover:opacity-100`) | `rg -n 'group-hover:opacity-100' src/` — Tab-reachable but invisible unless also `focus-visible:opacity-100` (self) or `group-focus-within:opacity-100` (container) | 2.4.7 |
| Mouse-only custom widgets | Any `onMouseDown`/`onMouseEnter` select-or-activate path with no keyboard equivalent; autocompletes need the combobox pattern (see `PlacesAutocomplete`) | 2.1.1 |
| Missing arrow-key patterns | `rg -n "key === 'Arrow" src/` — menus (`role="menu"`), tabs (`role="tablist"`), carousels. Tab+Enter operability = degraded (lower priority); complete inoperability = blocker | 2.1.1 |
| Drag-only interactions | Drag/reorder with no keyboard path — provide move buttons revealed on focus | 2.1.1 |
| Hover side-effects without focus equivalent | `onMouseEnter` without paired `onFocus` (good counter-example: `Footer.tsx` prefetch pairs both) | 2.1.1 |

## Lens 2 — Focus management

| Check | How to find | WCAG SC |
|---|---|---|
| Modal contract | Inventory `*Modal*`, `*Popover*`, `*Sheet*`, `*Drawer*`, lightboxes. Each needs: focus-in on open, Tab trap, Escape close, focus restore to trigger, `role="dialog" aria-modal aria-labelledby`, scroll lock that RESTORES the previous overflow value. All six come from `useModalA11y` — a modal not using it is a finding | 2.4.3, 2.1.2 |
| Focus restore exists at all | `rg -n 'previousActiveElement\|trigger\?\.focus\|useModalA11y' src/` — zero hits outside the hook means no modal restores focus | 2.4.3 |
| Skip link | First focusable element on the page, `sr-only focus:not-sr-only`, targets `#main-content` | 2.4.1 |
| Route-change focus | On SPA navigation, focus must move to `<main>` (via `ScrollToTop`); `document.title` must update (`usePageMeta`) | 2.4.3 |
| Smooth scroll vs reduced motion | JS `scrollTo({behavior:'smooth'})` ignores the CSS reduced-motion rules — must check `matchMedia('(prefers-reduced-motion: reduce)')` | 2.3.3 |
| Live regions | Toasts/status: `role="status" aria-live="polite"`; errors: `role="alert"`. Ad-hoc inline toasts are the usual gap. Loading states: `role="status"` + `sr-only` text + `aria-hidden` skeleton shapes | 4.1.3 |
| Backdrop click-close semantics | Backdrop `role="presentation"` is fine; the dialog PANEL must never be `role="presentation"`. Portaled modals: React events bubble through the React tree, so backdrops need `e.stopPropagation()` + `target === currentTarget` before closing | 1.3.1 |

## Lens 3 — Content & readability

| Check | How to find | WCAG SC |
|---|---|---|
| One h1 per rendered state | `rg -c '<h1' src/pages/` — multi-h1 files are usually mutually-exclusive branches (verify, don't flag blindly); zero-h1 pages are real findings. Fix: promote the top heading (same classes) or add an `sr-only` h1 | 1.3.1, 2.4.6 |
| Level skips / inversions | Sketch the rendered sequence per major page (`h1→h3` skip, `h2` after `h3`) | 1.3.1 |
| Contrast | Run `scripts/contrast.mjs`. Known floors (baseline audit): `slate-500`/`slate-600` fail AA-normal on every dark surface; `slate-400` fails on `bg-slate-700`; white-on-neon fails nearly everywhere — dark `text-slate-950` on neon is the house pattern; `neon-indigo`/`neon-purple` are large-text-only | 1.4.3 |
| In-text links distinguishable | Links inside prose need `underline underline-offset-2`, not `hover:underline` (axe: `link-in-text-block`). Freestanding data links (e.g. tracking numbers in cards) are exempt | 1.4.1 |
| Text size floor | `rg -n 'text-\[(9\|10\|11)px\]' src/` — new code floors at `text-xs` (12px); flag tiny + low-contrast + uppercase combos hardest | 1.4.4 |
| Rich text safety + alt text | Blog HTML must pass `DOMPurify.sanitize` + `ensureImgAlts`; user content through `escapeHTML` | 1.1.1 |
| Reduced motion | `rg -n 'prefers-reduced-motion\|motion-safe' src/` — new animations gate with `motion-safe:` | 2.3.3 |
| Language | `useDocumentLocale` keeps `<html lang>`/`dir` synced — verify still wired in `AppContent` | 3.1.1 |

## Lens 4 — Landmarks

| Check | How to find | WCAG SC |
|---|---|---|
| Exactly one `<main>` | `rg -n '<main' src/` — must be 1, with `id="main-content"` + `tabIndex={-1}` | 1.3.1 |
| Every `<nav>` labeled | `rg -n '<nav' src/` — each needs `aria-label` (i18n'd; don't include the word "navigation") or `aria-labelledby` pointing at a visible heading | 2.4.6 |
| No nav-in-nav | A `<nav>` wrapping another `<nav>` is landmark noise — demote the styling wrapper to `<div>` (check for tag-based CSS selectors first: `rg '\bnav\b' src/index.css`) | 1.3.1 |
| Content outside landmarks | Banners rendered between `</header>` and `<main>` need `role="region"` + `aria-label` | 1.3.1 |
| Explicit role attributes | `role="banner\|main\|contentinfo"` on semantic elements is redundant — implicit roles preferred; zero explicit ones is the healthy state | — |

## Instruments (run all three, every audit)

1. `npx eslint . --format json` → filter `ruleId.startsWith('jsx-a11y/')`. Baseline: 0
   errors, 0 suppressions, no `eslint-disable.*jsx-a11y` comments.
2. `node .claude/skills/a11y-audit/scripts/contrast.mjs` (from repo root).
3. `npm run test:e2e` — confirm the SPA actually mounts (a behavioral test like the
   skip-link one must pass; page-only axe passes can be vacuous).
