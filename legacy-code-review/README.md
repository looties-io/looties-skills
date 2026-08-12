# legacy-code-review

A skill for reviewing and testing code nobody has read, without freezing its defects into your test
suite.

Legacy no longer means old. It means **in production and unread**, and generated code reaches that
state in weeks rather than years.

Part of [looties-skills](https://github.com/looties-io/looties-skills), open-source agent skills by
[Looties](https://looties.io).

## The trap it exists to prevent

Writing a characterization test for untested code is how a defect gets blessed. You read the
handler, assert what it currently returns, the test goes green, and the bug is now protected by CI.
Nobody can fix it later without arguing with the suite, so nobody does.

The canonical scar: a refund handler dropped a currency unit conversion and refunded 39 cents where
3900 was owed. Its own test asserted `amount === "39"`. Green for months. The test was not missing.
The test was the reason the bug survived.

## What it does

- **The one rule:** never derive an assertion from the code under test. Assertions come from the
  schema, the migrations, the callers, the provider contract, and the written spec.
- Scopes a cohort by shared suspicion and blast radius instead of file by file.
- Builds the caller map first: who calls it, with what credential, and whether anything calls it at
  all. Uncalled code carrying live authority is the cheapest large finding you will get.
- Triages through five fixed lenses: duplicated rules, boilerplate, security, silent failure,
  orphans.
- Separates the **inventory** pass from the **remediation** pass, and requires every fix to be proven
  red against the pre-fix code.
- Verifies the new coverage adversarially: weighted mutation testing, plus a second reviewer who
  re-derives the findings without reading the first reviewer's tests.
- Hands over an inventory where every finding names its intent source, and severity comes after
  evidence.

**Best for:** inherited codebases, AI-generated code left unreviewed, modules with zero coverage, and
any audit that is about to be written as prose.

## Install

```bash
npx skills@latest add looties-io/looties-skills --skill legacy-code-review
```

## Usage

```
Use $legacy-code-review to add first coverage to this untested module without asserting its bugs.
```

## Contents

```
legacy-code-review/
|-- SKILL.md          <- the workflow the agent loads
|-- README.md         <- this file
`-- agents/           <- UI metadata for agent runtimes
```

## License

MIT, see [LICENSE](../LICENSE).
