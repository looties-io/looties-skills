# A11y Audit (WCAG 2.1 AA)

A skill for running an **evidence-based web accessibility audit** — keyboard navigation,
focus management, screen-reader semantics (landmarks, headings, ARIA), and color
contrast — and then shipping fixes without waiting on design: every change is split
into a **non-breaking bucket** (additive, invisible to sighted mouse users — ships now)
and a **design-gated bucket** (anything visible, quarantined with measured contrast
ratios so the design decision is informed).

Born from a full audit-and-fix pass on a production app: one afternoon took it from zero
focus management to a verified modal focus contract, a skip link, a keyboard-operable
checkout autocomplete, labeled landmarks, and an axe e2e gate that blocks regressions,
with pixel-identical UI.

Part of [looties-skills](https://github.com/looties-io/looties-skills), open-source agent
skills by [Looties](https://looties.io).

## What it gives you

- A four-lens audit method (keyboard / focus / content / landmarks) with per-lens
  checklists, grep patterns, and WCAG success-criterion mapping.
- Three objective instruments so findings are measured, not vibes: an accessibility lint
  run, a WCAG contrast calculator that reads your own Tailwind config
  (`scripts/contrast.mjs`), and an axe e2e gate — including the trap where a "passing"
  axe suite silently scans an unmounted SPA shell.
- The **"truly additive" test** for what ships without design sign-off (sr-only markup,
  ARIA, same-class tag swaps, `focus-visible:` on buttons — but *not* on text inputs,
  which match `:focus-visible` on mouse click).
- A fix cookbook (`references/fix-patterns.md`): modal focus contract via a shared
  hook, skip link, combobox keyboard pattern, heading repairs, landmark labels.
- Pitfalls that actually happened, not hypotheticals ("lint-clean ≠ accessible",
  "`aria-modal` doesn't trap focus").

Written for React and Tailwind. The skill opens by locating the five a11y primitives it
depends on in *your* codebase (modal contract, skip link, route-change focus, combobox
pattern, in-text link style), and treats any that is missing as a finding in its own
right. The method, checklists, instruments and cookbook patterns port to any
component-based frontend.

## Install

```bash
npx skills@latest add looties-io/looties-skills --skill a11y-audit
```

## Use

Ask your agent for an accessibility audit, a WCAG pass, or just describe the symptom —
"can't use checkout with a keyboard", "focus disappears when the modal closes", "is
this text readable enough". Say "report only" for an audit record with ready-to-apply
snippets, or "fix it" for the non-breaking implementation pass.

## Files

- `SKILL.md` — the workflow the agent loads.
- `references/audit-lenses.md` — per-lens checklists, grep patterns, WCAG SC mapping.
- `references/fix-patterns.md` — the non-breaking fix cookbook with adoption snippets.
- `scripts/contrast.mjs` — WCAG contrast calculator (Tailwind-config-aware, or
  `--pair '#fg,#bg'` for ad-hoc checks).
- `evals/evals.json` — realistic test prompts for iterating on the skill.
