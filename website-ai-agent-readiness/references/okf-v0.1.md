# OKF v0.1 Reference

OKF means Open Knowledge Format in this workflow: a Markdown knowledge bundle with YAML frontmatter and agent-readable body content.

## Status

Treat OKF as experimental. The current practical use is to register a structured, public knowledge bundle early for agents, partners, and direct machine readers. Do not describe OKF as a Google Search ranking factor or as a requirement for AI Overviews, AI Mode, or indexing.

Google's OKF work was announced for data-team metadata exchange. Using it for website agent-readiness is a secondary application. No known crawler depends on website OKF bundles today.

## File Placement

Use a root-level public file when possible:

```text
/okf.md
```

Link it from `llms.txt`, `llms-full.txt`, `index.md`, `ai-index.json`, and related machine-readable files when those exist.

## Frontmatter

Required:

- `type`

Recommended:

- `title`
- `description`
- `resource`
- `tags`
- `timestamp`

Example:

```markdown
---
type: knowledge-bundle
title: Example Agent-Readable Site Bundle
description: Public facts and canonical machine-readable resources for Example.
resource: https://example.com/
tags:
  - example
  - agent-readable-site
timestamp: 2026-06-16T00:00:00Z
---

# Example Agent-Readable Site Bundle

This OKF v0.1 bundle is an experimental convenience file for agents and direct machine readers. Google Search does not require OKF.
```

## Body Sections

Use only sections that are accurate and maintainable:

- Entity summary.
- Canonical machine-readable resources.
- Public human pages.
- Products, features, or discovery tools.
- Pricing summary.
- Trust, policy, or transaction model.
- Structured data surface.
- Update policy.

## When To Skip OKF

Skip OKF when:

- The site has no maintained owner for machine-readable facts.
- Public facts change often and cannot be tested.
- The asset would mostly duplicate stale marketing copy.
- The site is private, internal, or not intended for agent discovery.
- The user expects immediate Google Search impact from OKF alone.

## Review Checklist

- The file has valid YAML frontmatter.
- `type` is present.
- `resource` is the canonical public URL.
- `timestamp` is ISO-like and updated with material changes.
- URLs are absolute, public, canonical, and not retired.
- Pricing, policies, and claims match visible pages or backend constants.
- The file states experimental/non-Google framing when useful.
