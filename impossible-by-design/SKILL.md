---
name: impossible-by-design
description: Use when the same class of bug keeps coming back, when a fix would otherwise be "remember to do X next time", or when a correct mechanism already exists in the codebase but calling it is optional. Turns conventions into constraints so the wrong path becomes unbuildable rather than discouraged: single-owner rules, unconstructible privileged objects, structural contracts, one way in and one way out, loud failure on missing configuration, and gates that enumerate the whole universe instead of the compliant subset. Use when asked to "stop this happening again", "add a guardrail", "make this a lint rule", "why do we keep forgetting this", "remove the footgun", "enforce this convention", or during a post-incident review that is about to end in a documentation change.
---

# Impossible by Design

Review a batch of real defects in a mature codebase and one observation dominates:

> **The correct mechanism already existed, and using it was optional.**

The shared helper was there and the handler held a copy of the formula. The guard existed and the
new endpoint did not call it. The dedupe registry existed and the send path skipped it. The
accessible component existed and each usage re-implemented it. Nobody lacked knowledge. Nothing
enforced the knowledge.

This skill is the conversion: **take the convention and make the wrong path unbuildable.**

## The test

After any fix, ask what prevents the next occurrence. If the honest answer is one of these, you have
not finished:

- "We documented it."
- "The reviewer will catch it."
- "We told the team."
- "The agent instructions now mention it."

All four decay, and they decay fastest exactly where volume is highest: generated code, new joiners,
the third service, the rushed Friday. A rule that depends on someone remembering has a failure rate,
and the failure rate is proportional to how often the rule applies.

The bar to clear: **a new contributor, or an agent with no context, tries the wrong thing and cannot
make it work.**

## The ladder

Every rule sits somewhere on this ladder. The work is to move it up until the cost of climbing
exceeds the cost of the bug.

| Rung | Mechanism | Fails when |
|---|---|---|
| 1 | Convention, tribal knowledge | Anyone new, anyone rushed |
| 2 | Documentation | Nobody reads it at the moment of writing |
| 3 | Review | The reviewer is the same person, or tired |
| 4 | Lint rule or test | Easy to disable, easy to not-write |
| 5 | Type or API shape | The wrong call does not compile or does not exist |
| 6 | Unconstructible | The dangerous object cannot be created at all |

Rungs 1 to 3 are people. Rungs 4 to 6 are machines. The whole game is moving from the first group to
the second. You do not always need rung 6, but you should know which rung you settled for and why.

## Six conversions that carry most of the value

### 1. One owner per rule
Any rule with real consequences (money, authorization, retention, idempotency) gets exactly one
implementation, exported, and every caller calls it. A hand copy is a defect generator: when the
rule changes, the owner is updated and the copy is not, so the copy is where the bug lives.

The signature: two places compute the same thing with slightly different code. One of them is wrong,
and it is usually the one with fewer tests.

**Do:** extract, export, and delete the copies in the same change. Then add a check that fails if the
computation reappears outside its owner. A grep-based test is enough and is better than nothing.

### 2. Make the dangerous object unconstructible by accident
A privilege-escalating client (admin credential, service role, root key, unrestricted DB handle)
that is exported as a plain factory will eventually be imported by a caller-facing path.

**Do:** make construction require an explicit, named scope: who is this acting for, and why does it
need this authority. A factory that cannot be called without stating its caller cannot be called
absent-mindedly. The privileged path stays possible, it just stops being the path of least
resistance.

Same pattern for raw SQL execution, unbounded queries, unsigned outbound requests, and file
deletion.

### 3. Make the contract structural, not per-usage
When a correctness requirement is a checklist each usage must satisfy (a dialog needs a label, focus
trapping, an escape route; a form field needs an id, a label, an error region), most usages will
satisfy most of it and no usage will satisfy all of it.

**Do:** move the requirement into a component, wrapper, or base class that provides it, and make the
raw primitive unavailable. Usages then get it by construction, and auditing the requirement becomes
auditing one file.

### 4. One way in, one way out
Multiple response envelopes, multiple ways to read a secret, multiple HTTP clients, multiple error
shapes: each variant is a place a future change will be applied to some of them.

**Do:** collapse to one, then make the alternatives inaccessible rather than merely deprecated. The
test that this landed is not "we standardized", it is "you cannot build the other shape".

### 5. Make omission fail loudly, at the earliest moment
Missing configuration that falls back to a default, an empty string, or a silent no-op produces the
worst failure mode there is: a system that runs, reports success, and does nothing. Errors caught
per item with a success returned at the end are the same failure wearing different clothes.

**Do:** read required configuration at startup and refuse to start without it. Make a per-item
failure change the run's outcome or increment a counter someone watches. **Absence must be noisy.**

### 6. Make the gate's input the universe, not the compliant subset
This one is subtle and it is the highest-leverage of the six.

A checker built from the items that already carry a marker is structurally blind to the item with no
marker. Check the endpoints that have a guard, and the unguarded endpoint is not in your model, so
the gate is green while the actual danger sits outside it.

**Do:** enumerate from the ground truth (the filesystem, the route table, the deployed inventory) and
require every item to carry a declaration. Undeclared is a failure. This inverts a gate that
confirms compliance into a gate that finds gaps, and it is usually a small change to an existing
script.

Two properties keep such a gate honest:

- **Unknown is a failure**, not a warning, or the manifest dies within a month.
- **Acknowledged findings keep reporting.** When a row is knowingly risky and not yet fixed, mark it
  as an open acknowledgement that still warns. A finding silenced by the mechanism that records it
  is a finding you have deleted.

## When not to do this

Constraints have a cost, and pretending otherwise is how a codebase becomes hostile.

- **The bug happened once and is cheap.** Fix it. Move on.
- **The rule has legitimate exceptions you cannot enumerate.** A constraint that must be bypassed
  weekly teaches everyone to bypass constraints. Stay at rung 4 and accept it.
- **The constraint costs more than the bug.** Rung 6 on something that fails harmlessly is theatre.
- **You would break a working feature to satisfy it.** Hardening that removes capability is a
  regression with a good vocabulary. Constrain the wrong path, never the legitimate one.

Always leave a deliberate escape hatch, and make using it *visible* rather than *impossible*: an
explicit named override, recorded, reported, and greppable. The goal is that nobody does the wrong
thing by accident, not that nobody can ever do it.

## How to verify a constraint actually landed

The mistake is to verify the good path still works. That proves nothing about the constraint.

**Write the test that attempts the wrong thing and assert it fails.** Try to construct the
privileged client without a scope. Try to add an endpoint with no declaration. Try to build the
second response envelope. Try to start the service without the required secret. Each attempt should
fail, and fail with a message that tells the reader what to do instead.

A constraint with no test proving the wrong path is closed is a convention with better branding.

## Checklist

Before closing a fix for a recurring class of bug:

- [ ] Named the rung the rule was on and the rung it is on now.
- [ ] The wrong path fails at build, boot, or construction time rather than at review time.
- [ ] A test attempts the wrong path and asserts the failure.
- [ ] The error message names the right path.
- [ ] The escape hatch is explicit, recorded, and greppable.
- [ ] Existing violations were fixed or explicitly acknowledged in a way that keeps reporting.
- [ ] No legitimate capability was removed to get here.

## Related

- `legacy-code-review`: where the recurring findings come from, and the pass whose durable output
  should be constraints rather than fixes.
- `endpoint-surface-map`: conversion 6, worked end to end on the authorization surface of a service.
- `ground-truth`: prove the class of bug is really happening, and how often, before paying for a
  constraint.
