# Non-breaking fix cookbook

Adoption snippets for shared a11y primitives. Every pattern here passes the "sighted mouse
user sees nothing different" test. When implementing, ship unit tests alongside; a jsdom
environment usually needs `offsetParent` and `matchMedia` shims for focus and
reduced-motion assertions.

Names like `useModalA11y`, `SkipLink` and `ScrollToTop` below stand for the primitives in
your own codebase. Substitute yours, or build them once if they do not exist.

## Modal: the shared focus hook

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

Backdrop, especially when portaled, since React events bubble through the React tree and a
backdrop click would otherwise reach the host card's onClick:

```tsx
<div
  role="presentation"                    // backdrop only, NEVER on the panel
  onClick={(e) => {
    e.stopPropagation();
    if (e.target === e.currentTarget) onClose();
  }}
>
```

Remove any hand-rolled Escape handlers and scroll locks the modal had. The hook owns them,
and hand-rolled locks that reset overflow to `'unset'` clobber the previous value.

## Skip link and main target

```tsx
<SkipLink />                                          // first child of the root div
<main id="main-content" tabIndex={-1} className="focus:outline-none">
```

The link is `sr-only focus:not-sr-only …` and must focus the target in `onClick`
explicitly, because browsers disagree on focusing fragment targets (Safari never does).

## Heading fixes: pixel-identical

Tailwind Preflight unstyles headings, so a tag swap with unchanged classes renders
identically:

```tsx
// before                                       // after
<h2 className="text-2xl font-bold …">…</h2>     <h1 className="text-2xl font-bold …">…</h1>
```

Pages with no heading at all get an invisible one. Translate it, and check the page's
namespace for an existing title key before adding a new one:

```tsx
<h1 className="sr-only">{t('page_title')}</h1>
```

Multi-`h1` files whose h1s live in mutually exclusive early-return branches are CORRECT,
because that is one h1 per rendered state. Do not "fix" them.

## Hover-revealed controls

```tsx
// control is itself focusable (button):
className="opacity-0 group-hover:opacity-100 focus-visible:opacity-100 …"
// container revealing when any child is focused:
className="opacity-0 group-hover:opacity-100 group-focus-within:opacity-100 …"
```

`focus-visible:` is keyboard-only for buttons and links, so it is safe. For text inputs it
also matches on mouse click, so it is not non-breaking. Quarantine those.

## Combobox and autocomplete keyboard pattern

Roving `activeIndex` state reset on `[suggestions, isOpen]`; input `onKeyDown` handles
ArrowDown and ArrowUp (with `e.preventDefault()`), Enter (`preventDefault` first so the
surrounding form does not submit, then select), and Escape (close). ARIA wiring:

```tsx
// input
role="combobox" aria-autocomplete="list"
aria-expanded={open} aria-controls={open ? 'listbox-id' : undefined}
aria-activedescendant={open && activeIndex >= 0 ? `option-${activeIndex}` : undefined}
// list
<ul id="listbox-id" role="listbox" aria-label={…}>
// options: keep onMouseDown for mouse users; the highlight matches the hover style
<li id={`option-${i}`} role="option" aria-selected={i === activeIndex}
    className={`… hover:bg-slate-700 ${i === activeIndex ? 'bg-slate-700' : ''}`}>
```

## Landmark labels

```tsx
<nav aria-label={t('primary_nav_label')}>              // translated; no "navigation" in label
<nav aria-labelledby="footer-discover-heading">        // when a visible heading exists
<h3 id="footer-discover-heading">Discover</h3>
<div role="region" aria-label="Announcement">          // banners outside landmarks
```

Add label keys to every locale the project ships, or a locale-parity test will fail.

## Route-change focus

Skip the first paint with an `isInitialLoad` ref, call `focus({ preventScroll: true })` on
the main element, and gate smooth scrolling on
`matchMedia('(prefers-reduced-motion: reduce)')`, because CSS reduced-motion rules do not
affect JS-initiated smooth scroll.

## In-text links

```tsx
// in prose: SC 1.4.1, since a hover-only underline relies on color alone
className="<your-link-color> underline underline-offset-2"
```

Freestanding data links, such as tracking numbers in order cards or nav links, are exempt.

## Loading states

```tsx
<div role="status" className="…">
  <span className="sr-only">{t('loading')}</span>
  <div aria-hidden="true">{/* skeleton shapes */}</div>
</div>
```

## Escalation guardrails

Once accessibility lint rules are at error severity they will block some naive fixes. The
sanctioned resolutions:

- `interactive-supports-focus` on a `role="menu"` div with onKeyDown: add `tabIndex={-1}`.
- `click-events-have-key-events` or `no-noninteractive-element-interactions` on a dialog
  panel's click-guard: remove the panel handler and use the backdrop
  `target === currentTarget` pattern above instead.
- Never resolve a rule by adding `role="presentation"` to something semantic, by disabling
  the rule, or with an inline disable comment.
