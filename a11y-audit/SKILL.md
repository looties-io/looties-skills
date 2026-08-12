---
name: a11y-audit
description: Audit and fix web accessibility (WCAG 2.1 AA) in a web app, covering keyboard navigation, focus management, screen-reader semantics (landmarks, headings, ARIA), and color contrast, then implement the non-breaking fixes using shared a11y primitives instead of hand-rolled ones. Use whenever the user mentions accessibility, a11y, WCAG, screen readers, keyboard navigation, focus management, contrast, ARIA, or skip links; and also when they describe a symptom without naming accessibility ("can't use checkout with a keyboard", "focus gets lost when the modal closes", "this text is hard to read"). Applies to a single component as much as a full-app audit.
---

# Web Accessibility Audit and Non-Breaking Fix Pass

Run an evidence-based WCAG 2.1 AA pass over an app (or a scoped part of it), write a
dated audit record, and when asked to implement, apply only changes that are
**additive and visually non-breaking**, quarantining anything that would change the UI
into a design-decision list. This two-bucket split is the core of the skill: it lets
accessibility work ship without design sign-off stalling it.

Written for React and Tailwind, but the method, lenses, instruments and pitfalls port to
any component-based frontend.

## Before you start

Read the project's frontend conventions and design-token documentation, and follow any
rule the repository states about which docs must be read before writing code. If a
previous accessibility audit record exists, read it first so you extend it rather than
rediscover it.

Then locate the project's existing a11y primitives, because Phase C depends on them:

| Primitive | What to look for |
|---|---|
| Modal contract | A hook or wrapper owning focus-in, Tab trap, Escape, focus restore, scroll lock |
| Skip link | An `sr-only focus:not-sr-only` link targeting the main landmark |
| Route-change focus | A component that focuses `<main>` on SPA navigation |
| Combobox pattern | An existing autocomplete with correct keyboard handling, to copy |
| In-text link style | The class combination used for links inside prose |

Any of these that does not exist is itself a finding, and building it once is cheaper
than fixing its absence per component.

## Mode: report or implement?

Default to **report-only** when the user asks to "audit", "check", or "review":
findings plus ready-to-apply snippets, no code changes. Implement only when asked
("fix it", "apply", "implement"). When implementing, the project's own definition of
done applies: unit tests for new behavior, the repository's verify and build commands
green, and any translated string added to every locale the project ships.

## Phase A: audit

Sweep the four lenses below. For a full-app audit, fan out one parallel read-only
exploration agent per lens; for a scoped audit (one page or component), check the lens
checklists inline. The per-lens checklists, grep patterns, and WCAG SC mappings are in
`references/audit-lenses.md`. Read it before sweeping.

1. **Keyboard navigation**: unreachable or invisible controls, mouse-only widgets,
   arrow-key patterns, `tabIndex` hygiene, hover-only reveals, drag-only interactions.
2. **Focus management**: modal contract (trap, restore, Escape, dialog ARIA), skip
   link, route-change focus, live regions for dynamic updates.
3. **Content and readability**: heading hierarchy per rendered state, text size floors,
   sanitized rich text, reduced-motion coverage.
4. **Landmarks**: one `<main>`, labeled `<nav>`s, banner and contentinfo, content
   stranded outside all landmarks.

Ground your findings in three objective instruments. Subjective sweeps alone miss things
and over-report others:

- **Lint**: run the project's linter and filter for the `jsx-a11y/*` rules (or the
  equivalent for your framework). If the codebase is clean at `error` severity, keep it
  that way, and note what that tells you: the *remaining* problems are exactly the ones
  static analysis cannot see, namely focus behavior, contrast, and landmark labeling.
  Never downgrade an a11y rule to make a finding go away.
- **Contrast math**: `node scripts/contrast.mjs` computes WCAG ratios from the real
  token values in the Tailwind config, or `--pair '#fg,#bg'` for ad-hoc checks. Never
  eyeball contrast, and never trust hex values written in documentation. Design docs
  drift from the config, and the config is what ships.
- **Automated scan in a real browser**: run axe against the built app end to end. Make
  sure it boots first (see the pitfall below), because a scan of an unmounted shell
  reports zero violations and looks like success.

Verify load-bearing claims first-hand before they go in the report: open the file at the
cited line. Exploration agents are good at coverage and mediocre at precision.

## Phase B: report

Write the report wherever the project keeps dated records, named for its own convention.
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

Rank by user impact, not by WCAG severity. Include what is already good, because it tells
the reader (and the next audit) which patterns to preserve. Every finding carries its
evidence as `file:line` and its fix as a snippet, so implementation is one approval away.

## Phase C: implement the non-breaking slice only

The "truly additive" test. A change qualifies only if a sighted mouse user sees nothing
different:

- `sr-only` markup, `aria-*` attributes, landmark labels: always safe.
- Same-class tag swaps (`h2` to `h1`, `h3` to `h2`, `nav` to `div`): pixel-identical,
  because Tailwind Preflight unstyles headings and all styling lives in the classes.
- `focus-visible:` styles on **buttons and links**: keyboard-only, safe.
- `focus-visible:` on **text inputs**: NOT safe. Text fields match `:focus-visible` on
  mouse click too, so the ring shows during normal mouse use. Visible change, so
  quarantine it.
- Color, text-size and underline changes: quarantine with measured before and after
  ratios.

Fix with the project's primitives (the ones you located above) instead of hand-rolling.
The cookbook with adoption snippets is `references/fix-patterns.md`. Read it before
writing fixes.

## Phase D: verify

1. Run the project's full verification command (lint, types, unit tests).
2. Run the end-to-end suite against a fresh build, and confirm the app actually mounted
   before trusting a clean axe result.
3. Gate on it: block critical and serious axe violations in CI. Exempting
   `color-contrast` while design decisions are pending is reasonable, as long as the
   exemption is recorded and temporary. Assert the skip-link and modal focus contracts
   behaviorally, not just structurally.
4. Add new pages and flows to the scanned list. Coverage only ratchets up.

Update the audit record with what shipped, what was corrected, and what stays
quarantined. The record is what the next audit builds on.

## Pitfalls

Each of these has burned a real audit at least once.

- **Lint-clean is not accessible.** `role="presentation"` on a clickable backdrop
  silences the linter while making a dialog semantically invisible. Lint verifies
  syntax; you verify behavior.
- **A passing e2e suite may be scanning an empty page.** If the app needs public
  environment variables to boot and CI supplies none, the SPA never mounts under a
  preview server and every axe scan passes vacuously against the boot skeleton. If axe
  reports zero violations on a page you know has issues, confirm the app mounted.
- **`aria-modal="true"` does not trap focus.** Only a keydown handler does. Counting
  attributes will tell you a codebase is compliant when almost none of its modals trap.
- **Do not fabricate landmark labels' language.** Screen readers append the role, so
  label a nav "Primary", not "Primary navigation".
- **Unknown attributes may be deliberate.** Custom attributes can belong to a
  machine-readable layer (agent or automation metadata) and be declared in the project's
  type definitions. Check before stripping them.
- **Documentation drifts from config.** If a documented hex or token value contradicts
  the Tailwind config, the config is truth. Fix the doc in the same change.
