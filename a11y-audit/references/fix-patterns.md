# Non-breaking fix cookbook

Adoption snippets for the repo's a11y primitives. Every pattern here passed the
"sighted mouse user sees nothing different" test in the 2026-07-15 baseline pass.
When implementing, ship unit tests alongside (`src/__tests__/` — see the existing
`useModalA11y.test.tsx`, `ScrollToTop.test.tsx`, `PlacesAutocomplete.keyboard.test.tsx`
for the harness patterns, including the jsdom `offsetParent` and `matchMedia` shims).

## Modal → useModalA11y

Hooks must run before the `if (!isOpen) return null` early return:

```tsx
import { useModalA11y } from '../hooks/useModalA11y';

const dialogRef = useModalA11y(isOpen, onClose);   // before the early return
// Escape-guard while submitting:
// useModalA11y(isOpen, state === 'submitting' ? undefined : onClose)

<div
  ref={dialogRef}
  tabIndex={-1}
  role="dialog"
  aria-modal="true"
  aria-labelledby="my-modal-title"
  className="… focus:outline-none"      // panel is programmatically focused
>
  <h2 id="my-modal-title">…</h2>
```

Backdrop (especially when portaled — React events bubble through the React tree, so a
backdrop click would otherwise reach the host card's onClick):

```tsx
<div
  role="presentation"                    // backdrop only — NEVER on the panel
  onClick={(e) => {
    e.stopPropagation();
    if (e.target === e.currentTarget) onClose();
  }}
>
```

Remove any hand-rolled Escape handlers / scroll locks the modal had — the hook owns
them, and hand-rolled locks that reset to `'unset'` clobber the previous overflow value.

## Skip link + main target (already wired in App.tsx — pattern for reference)

```tsx
<SkipLink />                                          // first child of the root div
<main id="main-content" tabIndex={-1} className="focus:outline-none">
```

`SkipLink` is `sr-only focus:not-sr-only …` and focuses the target in `onClick`
explicitly, because browsers disagree on focusing fragment targets (Safari never does).

## Heading fixes — pixel-identical

Tailwind Preflight unstyles headings, so a tag swap with unchanged classes renders
identically:

```tsx
// before                                       // after
<h2 className="text-2xl font-bold …">…</h2>     <h1 className="text-2xl font-bold …">…</h1>
```

Pages with no heading at all get an invisible one (translate it — check the page's
namespace for an existing `page_title` key before adding new ones):

```tsx
<h1 className="sr-only">{t('page_title')}</h1>
```

Multi-`h1` files whose h1s live in mutually exclusive early-return branches are
CORRECT — one h1 per rendered state. Don't "fix" them.

## Hover-revealed controls

```tsx
// control is itself focusable (button):
className="opacity-0 group-hover:opacity-100 focus-visible:opacity-100 …"
// container revealing when any child is focused:
className="opacity-0 group-hover:opacity-100 group-focus-within:opacity-100 …"
```

`focus-visible:` is keyboard-only for buttons/links — safe. For text inputs it also
matches on mouse click — NOT non-breaking; quarantine those.

## Combobox / autocomplete keyboard pattern

Copy from `src/components/checkout/PlacesAutocomplete.tsx`: roving `activeIndex` state
reset on `[suggestions, isOpen]`; input `onKeyDown` handles ArrowDown/ArrowUp
(`e.preventDefault()`), Enter (`preventDefault` so the surrounding form doesn't
submit, then select), Escape (close). ARIA wiring:

```tsx
// input
role="combobox" aria-autocomplete="list"
aria-expanded={open} aria-controls={open ? 'listbox-id' : undefined}
aria-activedescendant={open && activeIndex >= 0 ? `option-${activeIndex}` : undefined}
// list
<ul id="listbox-id" role="listbox" aria-label={…}>
// options — keep onMouseDown for mouse users; highlight matches the hover style
<li id={`option-${i}`} role="option" aria-selected={i === activeIndex}
    className={`… hover:bg-slate-700 ${i === activeIndex ? 'bg-slate-700' : ''}`}>
```

## Landmark labels

```tsx
<nav aria-label={t('primary_nav_label')}>              // i18n; no "navigation" in label
<nav aria-labelledby="footer-discover-heading">        // when a visible heading exists
<h3 id="footer-discover-heading">Discover</h3>
<div role="region" aria-label="Announcement">          // banners outside landmarks
```

Add label keys to BOTH `src/i18n/locales/en/*.json` and `fr/*.json` — the locale-parity
test fails otherwise.

## Route-change focus (pattern lives in ScrollToTop.tsx)

Skip the first paint (an `isInitialLoad` ref), `focus({ preventScroll: true })` on the
main element, and gate smooth scrolling on
`matchMedia('(prefers-reduced-motion: reduce)')` — CSS reduced-motion rules do not
affect JS-initiated smooth scroll.

## In-text links

```tsx
// in prose — SC 1.4.1; hover-only underline relies on color alone
className="text-neon-cyan underline underline-offset-2"
```

Freestanding data links (tracking numbers in order cards, nav links) are exempt.

## Loading states

```tsx
<div role="status" className="…">
  <span className="sr-only">{t('loading')}</span>
  <div aria-hidden="true">{/* skeleton shapes */}</div>
</div>
```

## Escalation guardrails (jsx-a11y at error severity)

The escalated rules will block some naive fixes — the sanctioned resolutions:

- `interactive-supports-focus` on a `role="menu"` div with onKeyDown → add `tabIndex={-1}`.
- `click-events-have-key-events` / `no-noninteractive-element-interactions` on a dialog
  panel's click-guard → remove the panel handler; use the backdrop
  `target === currentTarget` pattern above instead.
- Never resolve a rule by adding `role="presentation"` to something semantic, disabling
  the rule, or `eslint-disable` comments.
