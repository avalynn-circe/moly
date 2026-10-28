# The Moly engine

Moly reads text that claims to inform a reader, finds the places where it does not, explains each one, and proposes the text that would. One engine; many packs. A pack supplies the rules, the kinds of text they read, and the voice that delivers the findings. The engine supplies everything else: the rule format, the pipeline, the finding record, the exception mechanism, the renderers, and the contract that keeps a rule honest.

The name is the herb that let Odysseus see through Circe's enchantment. The engine's job is seeing through text that pretends.

## Vocabulary

| Term | Meaning |
|---|---|
| Unit | One piece of text the engine judges on its own. An error message, a sentence with a number in it, a paragraph. The pack defines its unit types and where to find them. |
| Reader | Who the unit is for: `user`, `developer`, `operator`, or `model`. Several rules depend on it. |
| Rule | One way a unit can fail its reader. Pattern or question, explanation, fix, examples. |
| Area | A pack-defined group of rules, one letter in the rule id. For Readable Errors, the areas are the three questions of the method plus form. |
| Pack | A set of rules with a shared method, unit types, areas, and voice. The product a person buys. |
| Voice | How a pack phrases findings. Plain for Readable Errors; a persona for packs that want one. The voice changes the wording of an explanation and never its claim. |
| Finding | One hit, in the record every renderer and pack shares. |
| Mode | What the engine does with findings: `review` reports, `patch` rewrites, `gate` fails a build. |

## Two tiers of detection

Every rule is one of two kinds, and the kind is declared in the rule file.

**Mechanical** rules are regular expressions. They run anywhere, in milliseconds, with no model, and they are deterministic: the same text gives the same finding every time. A mechanical rule can say `unless`, a second list of patterns that cancels a hit on the same unit. That is how "Error" is a hit and "Error: state code must be two letters" is not. Mechanical rules are the tier a continuous integration gate can trust.

**Judged** rules need a reader. The rule file carries a yes/no question about one unit and names the evidence a yes must quote. An agent running the pack answers the question for each candidate unit. A judged finding without the required evidence is invalid and is dropped. A judged rule may carry a `prefilter`, a list of cheap patterns that select candidates, so the model reads the units that could fail and skips the rest. A rule with no prefilter considers every unit in its scope.

The engine keeps the two tiers in one format and one finding record on purpose. A rule can begin judged, grow a prefilter as its patterns settle, and become mechanical once the patterns alone carry it, with its id, its examples, and its history intact.

## The pipeline

1. **Extract.** Find the units. For prose, this is splitting. For code, it is finding the string literals that reach a reader, which depends on the language and the framework. The pack's `units[].locate` field tells an agent where to look. The reference implementation accepts units as JSON and leaves extraction to the agent; mechanical extractors per language are on the roadmap.
2. **Prefilter.** For each judged rule, select the candidate units.
3. **Mechanical pass.** Run every mechanical rule in scope over every unit. Produce findings.
4. **Judged pass.** For each judged rule and each candidate, answer the question. A yes with evidence produces a finding with a confidence of `high`, `medium`, or `low`.
5. **Exceptions.** Apply inline allow-markers and pack exceptions. The finding stays in the record, flagged as allowed. Nothing is deleted; a reader of the report sees what was waved through and why.
6. **Voice.** Restyle each explanation in the pack's voice, within the pack's `may` and `may_not` lists.
7. **Render.** Markdown table, JSON, or SARIF. Same findings, three shapes.

## Severity

Three tiers, the same three as the Circe Editorial Standard, named for what they do to the reader.

| Severity | Meaning | In gate mode |
|---|---|---|
| `block` | The text does not do its job. The reader cannot act on it. | Fails. |
| `warn` | The text does its job badly. The reader can act, with effort or risk. | Reports. |
| `note` | The text could do its job better. | Reports. |

A pack sets each rule's severity once. A finding inherits it. The voice may not change it.

## Exceptions and markers

Some text that trips a rule is right to stand. The rule file lists the conditions under which that is so, and whether the author must mark the exception inline. The marker is one comment:

```
moly: allow RE-N-001 the next step is the usage block printed on the next line
```

A marker names one rule and gives a reason. A marker with no reason is itself a finding, from the engine's own rule `MOLY-X-001`, because a silence with no reason is indistinguishable from a shortcut. The engine reads markers from the unit's `context`: the lines around a string literal, the comment above a paragraph.

A pack may define its own marker syntax in `pack.yml` when its units live somewhere a code comment cannot go.

## Findings

The record is in `schema/finding.schema.json`. Three fields carry the design:

- `quote` is required. A finding with no verbatim quote of the text it accuses is not a finding and is dropped at validation. This is the single strongest defense against a model that reports what it expected to read.
- `evidence` is required for judged findings, and is whatever the rule's `detect.evidence` field asked for. It is the second quote: the catch clause above the message, the variable in scope, the step written for someone else.
- `confidence` appears on judged findings only. Mechanical findings omit it; they are certain by construction. A renderer may hide `low` confidence findings by default. It may not hide `block` severity findings for any reason other than an allowed exception.

## Modes

| Mode | What happens | Who runs it |
|---|---|---|
| `review` | Findings, rendered. No text changes. | An agent, on request. Also the default. |
| `patch` | Each `rewrite` fix becomes a proposed replacement; each `procedure` fix becomes a checklist. Fixes marked `touches_tests` come with the test changes they require. The pack decides the granularity (for Readable Errors: one pull request per module, tests in the same commit). | An agent, with the author's say-so. |
| `gate` | The mechanical tier runs in continuous integration. `block` findings that are not allowed fail the job. SARIF output annotates the pull request. | A workflow. |

Gate mode runs the mechanical tier only. The judged tier can run in a gate when the workflow has a model, and the pack says whether its judged `block` rules are stable enough to fail a build. Until a pack says so, judged findings in a gate report and never fail.

## The contract

A rule's `examples` are not documentation. They are its test.

- A mechanical rule must hit every example under `hits` and miss every example under `passes`. `python -m moly check <pack>` runs this and fails the pack on the first rule that breaks it.
- A judged rule's prefilter must admit every example under `hits`. A prefilter that would hide one of the rule's own hits from the model is a bug, and the check catches it. (It caught two while this pack was being written.)
- Every rule needs at least one hit and one pass. A rule nobody can show failing, or nobody can show passing, is not finished.

Adding a rule means adding its examples. Changing a pattern means the examples still hold. A false positive reported by a user becomes a new `passes` example, then a pattern change, in that order.

## Stability

A rule id, once published, means one thing forever. To change what a rule looks for, write a new rule. To stop looking, set `status: retired` and keep the file, so a report from last year still resolves. Never reuse an id.

A pack carries a version. Rule additions bump the minor version. A severity change or a retirement bumps the major version, because it changes what a gate fails on.

## Built-in rules

The engine owns the `MOLY` prefix.

| Rule | Severity | Catches |
|---|---|---|
| MOLY-X-001 | warn | An allow-marker with no reason. |

## What the engine is not

- It is not a style checker for prose. That is Vale, and the Circe style already does it. Moly reads text for whether it informs, and leaves whether it is well written to the tools that do that.
- It is not a classifier. It never emits a score for a document. It emits findings, each tied to a quote, each with a reason and a fix.
- It is not a detector that renders verdicts on people. A pack that could be used that way (Tell, for one) is written to run on the user's own text, and its voice says so.

## Reference implementation

`moly/` is a small Python package with no dependencies beyond PyYAML and jsonschema. It loads and validates packs, runs the contract check, runs the mechanical tier over units, lists candidates for the judged tier, and renders findings. It is the engine a skill bundles, and the engine a workflow calls. See the README for commands.
