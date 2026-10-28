# Packs and voices

A pack is the product. It is a directory:

```
packs/<slug>/
  pack.yml          method, units, areas, voice, modes
  rules/<ID>.yml    one rule per file
  SKILL.md          the agent-facing procedure, for marketplaces that take one
  references/       material SKILL.md points to: extraction hints, output templates, the method
```

`pack.yml` answers five questions.

**What is the method?** `method.test` is the short list of questions every unit must answer. The rules are the ways a unit fails them. A pack with no method is a pile of regexes; the method is what makes the findings cohere and what the buyer is paying for.

**What does it read?** `units` lists the unit types, who reads each, and where an agent finds them. The reader matters: the same words can be a leak to a user and the content to a developer.

**How are rules grouped?** `areas` maps a letter to a name and to the method question it serves.

**How does it sound?** `voice` has a name, a register, what it may change, what it may not, and one sample of a neutral explanation beside its voiced form.

**What can it do?** `modes`, from `review`, `patch`, `gate`.

## The voice layer

The engine keeps every rule's explanation voice-neutral so that one rule can serve several packs. The voice restyles the explanation at render time. Two lists bound it.

`may` is what the voice can do: shorten, address the reader by role, add a persona's turn of phrase. `may_not` is what it can never do: change the rule, the severity, or the claim, or propose a fix that drops information the original carried.

Readable Errors uses the `plain` voice and the sample in its `pack.yml` shows how little that changes. A pack with a persona changes more. Here is a rule written once and voiced twice, to show the seam:

> **Neutral.** The claim gives a percentage increase and no base figure, so the reader cannot judge its size.
>
> **Tía Jo.** Forty percent more than what, mija? Forty percent of three is one extra. Show me the number you started from or I am not impressed.

Same rule, same quote, same fix. The persona is a rendering.

## Sharing rules across packs

Rules live with their pack, under its prefix. When two packs want the same detection, the second pack writes its own rule with its own id and lists the first under `see`. Duplication of a few lines is cheaper than a dependency between products that sell separately, and the examples diverge anyway, because the units differ.

## What makes a good pack

- A method a person could learn without the tool.
- Units the agent can find without guessing. If `locate` is vague, the pack will miss things and the buyer will blame the rules.
- A voice the buyer would choose on purpose.
- Every rule with both kinds of example, and the contract check green.
