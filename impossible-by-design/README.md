# impossible-by-design

A skill for turning conventions into constraints, so the wrong path becomes unbuildable rather than
discouraged.

Part of [looties-skills](https://github.com/looties-io/looties-skills), open-source agent skills by
[Looties](https://looties.io).

## The observation behind it

Review a batch of real defects in a mature codebase and one pattern dominates:

> **The correct mechanism already existed, and using it was optional.**

The shared helper was there and the handler held a copy of the formula. The guard existed and the new
endpoint did not call it. The dedupe registry existed and the send path skipped it. Nobody lacked
knowledge. Nothing enforced the knowledge.

## What it does

Gives you a test, a ladder, and six conversions.

- **The test:** if the answer to "what prevents the next occurrence" is "we documented it" or "the
  reviewer will catch it", the fix is not finished.
- **The ladder:** convention, documentation, review, lint or test, type or API shape, unconstructible.
  Rungs 1 to 3 are people, 4 to 6 are machines, and the work is moving from the first group to the
  second while knowing which rung you settled for.
- **Six conversions:** one owner per rule; make the dangerous object unconstructible by accident;
  make the contract structural rather than per-usage; one way in and one way out; make omission fail
  loudly at boot; and make the gate's input the whole universe instead of the compliant subset.
- **When not to:** constraints have a cost, exceptions you cannot enumerate teach people to bypass
  gates, and hardening that removes a working capability is a regression with a good vocabulary.
- **How to verify:** write the test that attempts the wrong thing and assert it fails. A constraint
  with no test proving the wrong path is closed is a convention with better branding.

**Best for:** post-incident reviews about to end in a documentation change, recurring bug classes,
footgun removal, and codebases where generated code arrives faster than anyone can review it.

## Install

```bash
npx skills@latest add looties-io/looties-skills --skill impossible-by-design
```

## Usage

```
Use $impossible-by-design to stop this class of bug coming back, not just fix this instance.
```

## Contents

```
impossible-by-design/
|-- SKILL.md          <- the workflow the agent loads
|-- README.md         <- this file
`-- agents/           <- UI metadata for agent runtimes
```

## License

MIT, see [LICENSE](../LICENSE).
