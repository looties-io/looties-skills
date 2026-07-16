---
name: a11y-audit
description: Audit and fix web accessibility (WCAG 2.1 AA) in the Looties app — keyboard navigation, focus management, screen-reader semantics (landmarks, headings, ARIA), and color contrast — then implement the non-breaking fixes with the repo's established a11y primitives. Use whenever the user mentions accessibility, a11y, WCAG, screen readers, keyboard navigation, focus management, contrast, ARIA, or skip links; and also when they describe a symptom without naming accessibility ("can't use checkout with a keyboard", "focus gets lost when the modal closes", "this text is hard to read"). Applies to a single component as much as a full-app audit.
---

# Web Accessibility Audit & Non-Breaking Fix Pass

Run an evidence-based WCAG 2.1 AA pass over the app (or a scoped part of it), write a
dated audit record, and — when asked to implement — apply only changes that are
**additive and visually non-breaking**, quarantining anything that would change the UI
into a design-decision list. This two-bucket split is the core of the skill: it lets
accessibility work ship without design sign-off stalling it.

Read `agent_docs/frontend_patterns.md` and `agent_docs/design_tokens.md` before writing
any code (CLAUDE.md requirement). The 2026-07-15 baseline audit lives at
`docs/records/2026-07-15-accessibility-audit.md` — read it first so you extend it rather
than rediscover it.

## Mode: report or implement?

Default to **report-only** when the user asks to "audit", "check", or "review" —
findings + ready-to-apply snippets, no code changes. Implement only when asked
("fix it", "apply", "implement"). When implementing, the Definition of Done applies:
unit tests for new behavior, `npm run verify` green, `npm run build` clean, files under
size limits, i18n strings in both `en` and `fr`.

## Phase A — Audit

Sweep the four lenses below. For a full-app audit, fan out one parallel read-only
exploration agent per lens; for a scoped audit (one page/component), check the lens
checklists inline. The per-lens checklists, grep patterns, and WCAG SC mappings are in
`references/audit-lenses.md` — read it before sweeping.

1. **Keyboard navigation** — unreachable/invisible controls, mouse-only widgets,
   arrow-key patterns, `tabIndex` hygiene, hover-only reveals, drag-only interactions.
2. **Focus management** — modal contract (trap / restore / Escape / dialog ARIA),
   skip link, route-change focus, live regions for dynamic updates.
3. **Content & readability** — heading hierarchy per rendered state, text size floors,
   sanitized rich text, reduced-motion coverage.
4. **Landmarks** — one `<main>`, labeled `<nav>`s, banner/contentinfo, content
   stranded outside all landmarks.

Ground your findings in three objective instruments — subjective sweeps alone miss
things and over-report others:

- **ESLint**: `npx eslint . --format json`, filter `jsx-a11y/*`. The repo is clean at
  `error` severity — keep it that way; a lint-clean state tells you the *remaining*
  problems are exactly the ones static analysis cannot see (focus behavior, contrast,
  landmark labeling). Never downgrade a jsx-a11y rule to fix a finding.
- **Contrast math**: `node .claude/skills/a11y-audit/scripts/contrast.mjs` computes
  WCAG ratios for the real token values in `tailwind.config.js` (or pass
  `--pair '#fg,#bg'` for ad-hoc checks). Never eyeball contrast, and never trust the
  hex values written in docs — the design docs have drifted from the config before.
- **axe e2e**: `npm run test:e2e` (builds with CI's placeholder `VITE_SUPABASE_*` env —
  without it the SPA never boots under `vite preview` and every axe scan passes
  vacuously against the boot skeleton; this exact failure shipped once).

Verify load-bearing claims first-hand before they go in the report: open the file at
the cited line. Exploration agents are good at coverage and mediocre at precision — the
baseline audit run corrected two of their findings on close reading.

## Phase B — Report

Write the report to `docs/records/YYYY-MM-DD-<scope>-audit.md` (records naming rule).
Structure:

```
# YYYY-MM-DD — <scope> Accessibility Audit (WCAG 2.1 AA)
Status / scope / method
## Executive summary   (scorecard per lens + top issues ranked by user impact)
## Findings per lens   (file:line evidence, WCAG SC number, ready-to-apply snippet)
## Tooling ratchets    (zero-UI-impact CI/lint improvements)
## Quarantined: needs design sign-off   (every visible change, with measured ratios)
## Appendices          (contrast tables, capability matrices)
```

Rank by user impact, not by WCAG severity. Include what's already good — it tells the
reader (and the next audit) which patterns to preserve. Every finding carries its
evidence (`file:line`) and its fix as a snippet, so implementation is approval away.

## Phase C — Implement (non-breaking slice only)

The "truly additive" test — a change qualifies only if a sighted mouse user sees
nothing different:

- `sr-only` markup, `aria-*` attributes, landmark labels → always safe.
- Same-class tag swaps (`h2`→`h1`, `h3`→`h2`, `nav`→`div`) → pixel-identical, because
  Tailwind Preflight unstyles headings; all styling lives in the classes.
- `focus-visible:` styles on **buttons and links** → keyboard-only, safe.
- `focus-visible:` on **text inputs** → NOT safe: text fields match `:focus-visible`
  on mouse click too, so the ring shows during normal mouse use. Visible change →
  quarantine it (this is why the chromeless CMS editor fields are design-gated).
- Color, text-size, underline changes → quarantine with measured before/after ratios.

Fix with the repo's primitives instead of hand-rolling — the cookbook with adoption
snippets is `references/fix-patterns.md` (read it before writing fixes):

- `src/hooks/useModalA11y.ts` — the modal contract (frontend_patterns.md §6 rule 6)
- `src/components/SkipLink.tsx` + `<main id="main-content" tabIndex={-1}>`
- `src/components/ScrollToTop.tsx` — route-change focus + reduced-motion scroll
- `PlacesAutocomplete` — the combobox/listbox keyboard pattern to copy for new
  autocompletes
- In-text links: `text-neon-cyan underline underline-offset-2` (never hover-only
  underline in prose — SC 1.4.1)

## Phase D — Verify

1. `npm run verify` — lint + typecheck + Vitest + Deno tests.
2. `npm run test:e2e` — fresh placeholder-env build + the full Playwright suite. The
   axe gate in `e2e/a11y.spec.ts` blocks critical + serious violations (only
   `color-contrast` is exempt, pending design decisions in the baseline audit §6) and
   asserts the skip-link and modal focus contracts behaviorally.
3. New pages/flows: add them to `PAGES` in `e2e/a11y.spec.ts` — coverage only ratchets
   up.

Update the audit record with what shipped, what was corrected, and what stays
quarantined — the record is the source of truth the next audit builds on.

## Pitfalls (each of these burned the baseline audit once)

- **Lint-clean ≠ accessible.** `role="presentation"` on a clickable backdrop silences
  jsx-a11y while making a dialog semantically invisible. Lint verifies syntax; you
  verify behavior.
- **A passing e2e suite may be scanning an empty page.** If axe reports zero
  violations on a page you know has issues, confirm the SPA actually mounted.
- **`aria-modal="true"` does not trap focus.** Only a keydown handler does
  (`useModalA11y`). Nine modals had the attribute; one had the trap.
- **Don't fabricate landmark labels' language.** Screen readers append the role —
  label a nav "Primary", not "Primary navigation".
- **Unknown attributes may be deliberate.** `toolparamdescription` etc. are WebMCP
  attributes typed in `src/types/webmcp.d.ts` — leave them.
- **agent_docs drift.** If a doc hex/value contradicts `tailwind.config.js`, the config
  is truth; fix the doc in the same change (repo rule).
