# Report template

## Review

```markdown
# Readable Errors review: <repository or path>

<N> units read (<n> error-message, <n> tool-result, <n> log-line, <n> error-test).
<B> block, <W> warn, <N> note. <A> allowed by marker.

Readers assigned: <surface> → <reader>; <surface> → <reader>; ...

## Findings

| Rule | Severity | Where | Message | Why it fails |
|---|---|---|---|---|
| RE-W-002 | block | src/weather.py:48 | `Unable to fetch alerts or no alerts found.` | The sentence hedges between a failure and an empty result. |
| ... | | | | |

## Block findings in full

### RE-W-002 at src/weather.py:48

> Unable to fetch alerts or no alerts found.

<The rule's explanation, in full.>

**Evidence.** <For judged findings: the quote the rule asked for. Here: the except clause at line 31 that returns None.>

**Proposed.**
- On timeout: `Could not fetch alerts for <state>: api.weather.gov timed out after 30 s. Retry in a minute.`
- On 4xx: `Could not fetch alerts: <state> is not a US state code. Pass two letters, like MN.`
- On an empty list: `No active alerts for <state>.` (a result, not an error)

**Tests touched.** tests/test_weather.py:77 asserts on the old sentence (RE-F-003). Change it to assert on `WeatherUnavailable` and the state code.

### ...

## Allowed

| Rule | Where | Reason given |
|---|---|---|
| RE-N-001 | cli.py:12 | the usage block prints on the next line |
```

## Patch (per module, in the pull request body)

```markdown
Readable Errors: <module>

| Before | After | Rules satisfied |
|---|---|---|
| `Invalid state code.` | `State code must be two letters, like MN. Got '<value>'.` | RE-Y-001, RE-N-001 |
| ... | | |

Tests changed: <file:line> now asserts on <type or code> (was the full sentence; RE-F-003).

Not changed, proposed: RE-F-004 found three wordings for the database-unreachable condition
(<file:line>, <file:line>, <file:line>). A one-entry catalog would replace them; see the steps in the rule.
```

## Gate (SARIF)

`--format sarif` produces a SARIF 2.1.0 log. Upload it with `github/codeql-action/upload-sarif` and the findings appear as annotations on the pull request, with allowed findings marked as suppressed in source.
