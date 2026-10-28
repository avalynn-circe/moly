# Readable Errors

The first pack. Point an agent at a codebase and it finds the error messages that leave their reader guessing, explains what each one withholds, and rewrites it to say what happened, why, and what to do next. The three questions are the method; the fourteen rules are the ways a message fails them.

## Who buys it

- A team whose support queue is full of "I got an error" tickets with no detail, because the error had none.
- A developer shipping a tool to agents, whose tool results are strings a model has to act on. The MCP server tutorial review found that the official quickstart fails this in four of its own findings. Those four are now rules RE-W-002, RE-Y-002, RE-N-004, and RE-W-001.
- A documentation engineer who wants an error reference and has no error catalog to write it from. RE-F-004 produces the catalog.

## The three questions, and the areas

| Area | Asks | Rules |
|---|---|---|
| W, what | What happened? | RE-W-001 any-failure message. RE-W-002 one string, two outcomes. RE-W-003 mechanism named, event not. |
| Y, why | Why did it happen? | RE-Y-001 rejected without the rule. RE-Y-002 cause caught and discarded. RE-Y-003 thing named, value missing. |
| N, next | What does the reader do? | RE-N-001 stops at the problem. RE-N-002 someone else's step. RE-N-003 retry with no condition. RE-N-004 the model has nothing to act on. |
| F, form | Does the form serve the reader? | RE-F-001 shouts, apologizes, jokes. RE-F-002 leaks internals. RE-F-003 a test pins the sentence. RE-F-004 one failure, many wordings. |

Six of the fourteen are `block`. A message that trips one does not do its job.

## The reader decides

Four readers: `user`, `operator`, `developer`, `model`. The pack asks the agent to decide, per surface, who reads it, before judging anything. "ECONNREFUSED 10.0.0.4:5432" is a complete log line for a developer and a leak and a riddle for a user. RE-W-003 and RE-F-002 have the reader in their questions, and the fixtures carry `reader` so the model sees the distinction in examples before it sees it in code.

The `model` reader is the pack's distinct contribution. A tool result is an error message whose reader has no logs, no support line, and one turn to recover. RE-N-004 reads only tool results and asks one question: what would the model's next call be? If the agent cannot say, the message fails.

## The four unit types

| Unit | Reader | Where it lives |
|---|---|---|
| `error-message` | user, operator | raise, throw, exit, HTTP error bodies, validation text, message catalogs |
| `tool-result` | model | the return paths of registered tools |
| `log-line` | developer, operator | error-level log calls |
| `error-test` | developer | assertions on message text |

The fourth is not an error. It is included because it decides what a rewrite costs. RE-F-003 reads it, and patch mode uses its findings to bring test changes along with message changes, in the same commit.

## Modes

**Review** produces a findings table, grouped by severity, each row with the quote, the rule, and the first sentence of the explanation. Below the table, one section per `block` finding with the full explanation and the proposed rewrite.

**Patch** produces, per module, a diff of the message changes, the test changes RE-F-003 identified, and a short note for the pull request body listing which rules each change satisfies. One pull request per module; a wholesale rewrite is a diff nobody merges.

**Gate** runs the four mechanical rules in continuous integration over units a workflow extracts. RE-W-001 and RE-W-002 are `block` and fail the job. RE-N-003 and RE-F-001 report. Output as SARIF annotates the pull request. The ten judged rules report in a gate and do not fail it until the pack's next major version says they may.

## Extraction

Version 0.1 asks the agent to extract units, with `references/extraction.md` as the guide: per language, the constructs where a string reaches a reader, and the grep that finds them. The agent writes units as JSON, runs the mechanical tier, asks for candidates, and judges those. A mechanical extractor for Python and TypeScript is the first roadmap item, because it makes gate mode run without an agent.

## Known limitations

- The pack reads messages written in English. Patterns and examples are English. A localized catalog can be judged by the ten judged rules through its source language, and the four mechanical rules will miss it.
- RE-F-004 (duplicate wordings) needs the whole set of units at once. It does not run in gate mode.
- The pack does not decide what the product's voice should be. RE-F-001 flags ornament and says so; a product with a deliberate playful voice marks its exceptions and moves on.
- A rewrite is a proposal. The agent cannot know a product's support process, its error id scheme, or its localization pipeline. Patch mode writes the message that answers the three questions and leaves those choices visible as slots or comments.

## Pricing and listing

For the Agensi listing: category Code Quality & Review, with Technical Documentation and Testing & Debugging as secondary tags. Paid, one-time. The sample input is a Python tool function with a catch-all; the sample output is the review table for it and the rewrite. Known limitations above go in the listing verbatim. See `packs/readable-errors/agensi.yml` for the drafted fields.
