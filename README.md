# looties-skills

Agent skills published by [Looties](https://looties.io) — the marketplace where developers and tech enthusiasts can buy and sell conference swag, limited-edition merch, and developer gear from the events they love.

These are skills we actually use to build Looties. Each skill is a self-contained folder you can install into your Claude Code or Codex workflow.

## Skills

| Skill | Description |
|---|---|
| [a11y-audit](./a11y-audit/) | Evidence-based WCAG 2.1 AA audit (keyboard, focus, screen-reader semantics, contrast) plus a non-breaking fix pass — additive changes ship now, visible ones are quarantined with measured ratios for design sign-off |
| [agentic-peer-review](./agentic-peer-review/) | Independent after-the-fact review of the last N merged PRs by several reviewer agents split by domain: adjudicate, reproduce every finding before ranking it, fix, re-review the fix diff, verify the deploy |
| [changelog-to-video](./changelog-to-video/) | Turn a changelog into a feature-showcase video where every feature gets a real mock-up (asset waterfall), not a generic card |
| [cinematic-hyperframes](./cinematic-hyperframes/) | Cinematic, VFX-friendly Hyperframes motion design for HTML-to-video product films |
| [code-cleanup](./code-cleanup/) | Safe, behavior-preserving code cleanup for staged or recently changed files |
| [endpoint-surface-map](./endpoint-surface-map/) | Know who can actually call each endpoint: a manifest of caller, credential and authority, a CI gate that fails on undeclared routes, and a live check for deployed config drift |
| [field-web-performance](./field-web-performance/) | Treat a red Lighthouse score as a thermometer, not a backlog: separate simulated lab, observed lab, throttled lab and field data, triage the harness first, and ship only measured wins |
| [google-ai-seo-fundamentals](./google-ai-seo-fundamentals/) | Google Search guidance for safe, people-first AI-assisted content |
| [google-ai-seo-optimization](./google-ai-seo-optimization/) | Google-specific SEO workflow for AI Overviews and AI Mode readiness |
| [ground-truth](./ground-truth/) | Confirm a finding against the running system before acting on it: is it happening, since when, how far it reaches, and why a scheduler that reports success proves nothing |
| [harness-testing](./harness-testing/) | Design harness tests that boot real code into a controlled, mocked environment and assert end-to-end |
| [impossible-by-design](./impossible-by-design/) | Turn a convention into a constraint so the wrong path stops being buildable, because the correct mechanism usually already existed and using it was optional |
| [legacy-code-review](./legacy-code-review/) | Review and test code nobody has read, without freezing its defects into your suite: never derive an assertion from the code under test |
| [merchant-feed-audit](./merchant-feed-audit/) | Get products approved in Google Merchant Center: ask the Merchant API what Google actually ingested, clear disapprovals one reason code at a time, derive every attribute from checkout data, fail closed |
| [merge-time-ci-economics](./merge-time-ci-economics/) | Cut a GitHub Actions bill by reconstructing billed minutes per trigger, then running CI once at merge time behind a local pre-commit gate, with a draft-to-ready flow agents can follow |
| [postgres-privilege-audit](./postgres-privilege-audit/) | Audit who can read which columns and execute which functions in Postgres/Supabase/PostgREST from the live catalog, catch credential columns RLS hands to their own subject, prove revokes in an aborting dry run |
| [provider-canary](./provider-canary/) | Before shipping a change that sends real payloads to a carrier, payment or payout provider: a canary that reuses the app's own payload builder, asserts test mode, judges the provider status field and cleans up the same day |
| [repo-wide-dead-code-sweep](./repo-wide-dead-code-sweep/) | Repo-wide hunt for unused exports, files, functions, SQL routines and i18n keys with evidence per candidate, dormant-by-design checks and revertible micro-commits |
| [website-ai-agent-readiness](./website-ai-agent-readiness/) | Website readiness for AI agents, answer engines, and machine-readable assets |

## Install

Via [skills.sh](https://skills.sh):

```bash
npx skills@latest add looties-io/looties-skills --skill a11y-audit
npx skills@latest add looties-io/looties-skills --skill agentic-peer-review
npx skills@latest add looties-io/looties-skills --skill changelog-to-video
npx skills@latest add looties-io/looties-skills --skill cinematic-hyperframes
npx skills@latest add looties-io/looties-skills --skill code-cleanup
npx skills@latest add looties-io/looties-skills --skill endpoint-surface-map
npx skills@latest add looties-io/looties-skills --skill field-web-performance
npx skills@latest add looties-io/looties-skills --skill google-ai-seo-fundamentals
npx skills@latest add looties-io/looties-skills --skill google-ai-seo-optimization
npx skills@latest add looties-io/looties-skills --skill ground-truth
npx skills@latest add looties-io/looties-skills --skill harness-testing
npx skills@latest add looties-io/looties-skills --skill impossible-by-design
npx skills@latest add looties-io/looties-skills --skill legacy-code-review
npx skills@latest add looties-io/looties-skills --skill merchant-feed-audit
npx skills@latest add looties-io/looties-skills --skill merge-time-ci-economics
npx skills@latest add looties-io/looties-skills --skill postgres-privilege-audit
npx skills@latest add looties-io/looties-skills --skill provider-canary
npx skills@latest add looties-io/looties-skills --skill repo-wide-dead-code-sweep
npx skills@latest add looties-io/looties-skills --skill website-ai-agent-readiness
```

Install every skill at once:

```bash
npx skills@latest add looties-io/looties-skills --skill '*'
```

Or clone the collection:

```bash
git clone https://github.com/looties-io/looties-skills.git
```

## Adding a skill

Each skill lives in its own subfolder at the root of this repo:

```
<skill-name>/
|-- SKILL.md          <- required: the workflow the agent loads
|-- README.md         <- required: the human-facing page
|-- agents/openai.yaml
|-- references/       <- optional: detail loaded on demand
|-- scripts/          <- optional: deterministic helpers
`-- evals/evals.json  <- optional: realistic trigger prompts
```

Conventions every skill follows:

- **Frontmatter:** `name` equals the folder name; `description` is a double-quoted string of at most 1,024 characters that says what the skill does, when to use it (with real trigger phrases), and what it is **not** for; `license: MIT`; `metadata.author` and `metadata.version`.
- **Body:** a short thesis, a quick-reference table that routes an intent or symptom to a step, ordered steps that explain why, pitfalls drawn from real incidents, and a Verification section that says when the work is done. Keep `SKILL.md` under 500 lines and move long material to `references/`.
- **Earned content only:** every skill generalizes a procedure we ran on a real codebase. War stories are anonymized: no internal names, schemas, hosts, identifiers or dates.
- **Check it parses** before opening a pull request: `npx skills@latest add ./ --list` must list the skill.

## About Looties

Looties is the marketplace where developer culture meets resale. Browse rare conference merch, archived launch gear, and developer collectibles.

→ [looties.io](https://looties.io) · [GitHub org](https://github.com/looties-io) · [Discord](https://discord.gg/A6UcsyCHCb)

## License

MIT
