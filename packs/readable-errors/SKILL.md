---
name: readable-errors
description: Finds error messages in a codebase that leave their reader guessing, explains what each one withholds, and rewrites it to say what happened, why, and what to do next. Reads user-facing errors, log lines, and the strings tools return to models. Use when a user asks to review, improve, audit, or rewrite error messages, error handling output, validation messages, or MCP tool results, or asks why users cannot act on an error.
---

# Readable Errors

Every error message owes its reader three answers: what happened, why, and what to do next. This skill finds the messages that withhold one or more of them, in the user's own codebase, and proposes the message that would not. Fourteen rules in `rules/`, one YAML file each, decide what counts as withholding. The rules are the authority. When this document and a rule file disagree, the rule file wins.

## Before anything: decide who reads each surface

Walk the codebase's surfaces and name the reader of each. Four readers:

| Reader | Sees the message | Can |
|---|---|---|
| `user` | in a UI, a CLI they did not write, an API response they consume | change their input, wait, contact someone |
| `operator` | while running or deploying the software | change configuration, permissions, infrastructure |
| `developer` | in a log, a trace, a test | read code |
| `model` | as the result of a tool call | change an argument, call another tool, tell the user |

Write the mapping down before judging a single message. Several rules give a different answer for a different reader, and a review that mixes them up will tell a developer to hide the stack trace from themselves.

## Step 1. Extract units

Follow `references/extraction.md`. For each language present, run the greps it lists and collect every string that reaches a reader. Record each as a unit:

```json
{"type": "error-message", "text": "Invalid state code.", "file": "src/weather.py", "line": 42, "reader": "user", "context": "<the 6 lines above and 2 below>"}
```

Unit types: `error-message`, `tool-result`, `log-line`, `error-test`. The context matters: RE-Y-002 reads the catch clause above the message, and allow-markers live in the context too. Write all units to one JSON file.

Do not sample. A review that read half the messages will be trusted as if it read all of them.

## Step 2. Run the mechanical tier

Write `scripts/moly_lite.py` from this package to a temporary file, unchanged, and run it:

```bash
python3 -I /tmp/moly_lite.py scan <this skill's directory> --units units.json --format json > mechanical.json
python3 -I /tmp/moly_lite.py candidates <this skill's directory> --units units.json > candidates.json
```

The first command gives the findings from the four mechanical rules. The second gives, for each of the ten judged rules, the units its prefilter admits. Remove the temporary file when done.

## Step 3. Judge the candidates

For each judged rule, read its file with `explain <RULE-ID>` or open `rules/<RULE-ID>.yml`. Then for each candidate unit:

1. Read the unit's text and context, with its reader in mind.
2. Answer `detect.question` for this unit. Yes or no.
3. On yes, quote what `detect.evidence` asks for. If you cannot quote it, the answer is no.
4. Record a finding in the shape of `schema/finding.schema.json`, with `confidence` set to `high` when the evidence is explicit in the text, `medium` when it needs the context, `low` when it needs an assumption about the reader or the code path.

Read the rule's `examples` first. The notes under each example are the calibration. A unit that resembles a `passes` example is a pass.

RE-F-004 is different: it judges the whole set of units at once. Run it last, over every `error-message` and `tool-result` unit, looking for one failure under several wordings.

## Step 4. Apply exceptions

A unit whose context carries `moly: allow <RULE-ID> <reason>` keeps its finding, flagged as allowed, with the reason. A marker with no reason gets a second finding, `MOLY-X-001`. Each rule's `exceptions` list names conditions where the text may stand without a marker (a developer reading a log line, for RE-W-003 and RE-F-002). Apply those by the reader you assigned in step 0.

## Step 5. Report

Use the template in `references/output.md`. In short: a summary line with counts by severity; a table of every finding sorted block, warn, note; then one section per `block` finding with the quote, the full explanation, the proposed rewrite, and the test changes it needs. Allowed findings appear in the table with their reason and nowhere else.

Every row has a verbatim quote. A finding you cannot quote does not go in the report.

## Patch mode

Only when the user asks for changes, not for a review. Then, per module:

1. Rewrite each message that has a `block` or `warn` finding, using the rule's `fix.template` and the three-question method in `references/method.md`. Keep every value and cause the original carried. Add what it withheld.
2. For each rewrite, find the tests RE-F-003 flagged that assert on the old text. Change them in the same commit: to the error type or code where one exists, to a meaningful fragment where it does not.
3. Where a `procedure` fix applies (RE-W-002, RE-Y-002, RE-F-002, RE-F-004), do the procedure or, where it changes structure the user did not ask about, write the steps into the pull request body as a proposal.
4. One pull request per module. In the body, list each changed message with the rules it now satisfies.

Do not rewrite a message with only `note` findings unless the user asks.

## Gate mode

When asked to add this as a check: the four mechanical rules run in a workflow over units a script extracts. `block` findings that are not allowed fail the job. Output SARIF with `--format sarif` and upload it so the pull request shows annotations. Judged rules do not run in a gate in this version.

## What this skill does not do

- It does not read messages in languages other than English with the mechanical rules. Judged rules can be applied to a source-language catalog.
- It does not decide the product's voice. RE-F-001 flags ornament; a product that wants it marks the exception.
- It does not know the user's error id scheme, support process, or localization pipeline. Rewrites leave those as visible slots.
- It never silences a rule to make a report shorter. Allowed findings stay in the table.
