# Rule file reference

One rule per file, `rules/<ID>.yml`, where the file name is the rule id. The schema is `schema/rule.schema.json`; this page says what each field is for.

## Identity

| Field | Purpose |
|---|---|
| `id` | `PREFIX-A-NNN`. The prefix is the pack's. The letter is an area the pack declares. The number is sequential within the area and never reused. |
| `title` | The failure, stated as a fact about the text. "The message stops at the problem." Not an instruction, not a question. |
| `area` | The area's name, matching the letter in the id. The loader checks them against each other. |
| `severity` | `block`, `warn`, or `note`. See the engine spec. |
| `kind` | `mechanical` or `judged`. |
| `scope` | Which unit types the rule reads. A rule about tool results does not fire on log lines. |
| `status` | `active` (default), `draft`, or `retired`. Drafts load and check but do not fire. Retired rules load and never fire. |

## Detection

For a mechanical rule:

| Field | Purpose |
|---|---|
| `detect.patterns` | Regular expressions. Any match on the unit text is a hit. Case-insensitive unless `case: true`. |
| `detect.unless` | Regular expressions that cancel a hit on the same unit. Use them to carve out the good form of a bad habit. |

For a judged rule:

| Field | Purpose |
|---|---|
| `detect.question` | One yes/no question about one unit. Written so a careful reader with the unit and its context can answer it. Yes is a hit. |
| `detect.evidence` | What a yes must quote. The finding is invalid without it. |
| `detect.prefilter` | Optional. Patterns that select candidate units. A unit that matches none is skipped. The contract check confirms the prefilter admits every example hit. |

Write the question so that the model's reasoning is forced through the text. "Does the message say the input is wrong without stating the rule it broke?" can be answered only by finding or failing to find the rule in the message. "Is this a good error message?" cannot.

## Explanation and fix

| Field | Purpose |
|---|---|
| `explain` | Why the text fails its reader. Voice-neutral: no persona, no jokes. Three to five sentences. The first sentence should stand alone, because the Markdown renderer shows only that one in the table. |
| `fix.kind` | `rewrite` when a corrected sentence can be templated. `procedure` when the fix is steps in code or structure. `none` when the rule informs and does not prescribe. |
| `fix.template` | For rewrites. The shape of the corrected text with `<angle>` slots. |
| `fix.steps` | For procedures. Ordered, imperative. |
| `fix.touches_tests` | True when applying the fix changes text that tests may assert on. Patch mode uses this to bring the test change along. |

## Exceptions

A list of `when` conditions under which the text may stand, each with `marker_required`. When the marker is required, the author writes `moly: allow <ID> <reason>` in the unit's context. When it is not, the exception is one the engine or the agent can see for itself, usually from the reader. Keep the list short. An exception that covers most hits means the rule is wrong.

## Examples

`examples.hits` and `examples.passes`, at least one each. Every example has `text`. It may have `context` (surrounding code or prose the judge needs), `reader`, and `note`. Notes teach: they say why this is a hit or a pass, and they are the first thing to read when a rule misfires.

For a mechanical rule, the examples are executable. For a judged rule, they calibrate the model and test the prefilter. Either way, a bug report becomes an example before it becomes a fix.

## A complete example

```yaml
id: RE-N-003
title: Retry advice with no condition
area: next
severity: warn
kind: mechanical
scope: [error-message, tool-result]
detect:
  patterns:
    - '\b(please\s+)?try\s+again(\s+later)?\W*$'
  unless:
    - '\b(after|in|at|once|when|if|until|before)\b'
    - '\d'
explain: >
  "Try again later" gives the reader a verb and no information. ...
fix:
  kind: rewrite
  template: "<Event>: <cause>. Retry <after N seconds | at <time> | once <condition>>."
  touches_tests: true
examples:
  hits:
    - text: "Service unavailable. Please try again later."
  passes:
    - text: "Service unavailable: the API is rate-limiting this key. Retry after 42 seconds."
```
