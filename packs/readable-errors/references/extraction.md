# Finding the units

Per language, where a string reaches a reader, and a grep that finds it. Run them all; the skill does not sample. Each hit becomes one unit with its file, line, six lines of context above and two below, a type, and a reader.

## Python

| Construct | Unit type | grep |
|---|---|---|
| `raise X("...")`, `raise X(f"...")` | error-message | `grep -rnE 'raise\s+\w+\((f?["'\''])' --include='*.py'` |
| `sys.exit("...")`, `parser.error("...")`, `click.BadParameter(` | error-message | `grep -rnE '(sys\.exit|\.error|BadParameter|UsageError)\(\s*f?["'\'']' --include='*.py'` |
| `logger.error(`, `logging.error(`, `log.exception(` | log-line | `grep -rnE '\b(log|logger|logging)\.(error|critical|exception|warning)\(' --include='*.py'` |
| Return paths of `@mcp.tool` or `@tool` functions | tool-result | find the decorated functions, then every `return` of a string literal or f-string inside them, and every `return None` after an `except` |
| `except Exception:` with `return None` / `return "..."` | context for RE-Y-002 | `grep -rnE -A3 'except(\s+\w+)?\s*:' --include='*.py'` |
| `assert str(e)`, `pytest.raises(..., match=`, `assertRaisesRegex` | error-test | `grep -rnE '(str\((e|exc|err)\S*\)\s*==|match=|assertRaisesRegex|in str\()' --include='test_*.py' --include='*_test.py'` |

## TypeScript and JavaScript

| Construct | Unit type | grep |
|---|---|---|
| `throw new Error("...")`, `new HttpError(`, `createError(` | error-message | `grep -rnE 'throw new \w*(Error|Exception)\(' --include='*.ts' --include='*.tsx' --include='*.js'` |
| `res.status(4xx\|5xx).json({ error: "..." })`, `.send("...")` | error-message | `grep -rnE 'status\((4|5)[0-9]{2}\)' --include='*.ts' --include='*.js'` |
| `console.error(`, `logger.error(`, `log.error(` | log-line | `grep -rnE '\b(console|logger|log)\.(error|warn)\(' --include='*.ts' --include='*.js'` |
| `server.tool(...)` handlers, `content: [{ type: "text", text: "..." }]` on failure paths | tool-result | find each registered tool, then every return whose text is produced on a failure path |
| `toThrow("...")`, `expect(err.message).toBe(` | error-test | `grep -rnE '(toThrow\(\s*["'\''`]|\.message\)\.to(Be|Equal|Match)\()' --include='*.test.*' --include='*.spec.*'` |

## Go

| Construct | Unit type | grep |
|---|---|---|
| `errors.New("...")`, `fmt.Errorf("...")` | error-message or log-line by where it is returned | `grep -rnE '(errors\.New|fmt\.Errorf)\(' --include='*.go'` |
| `http.Error(w, "...", code)` | error-message | `grep -rnE 'http\.Error\(' --include='*.go'` |
| `log.Printf("...error...")`, `slog.Error(`, `zap...Error(` | log-line | `grep -rnE '\b(slog|log|logger|zap\S*)\.(Error|Fatal|Printf)\(' --include='*.go'` |
| `if err != nil { return nil, errors.New("...") }` discarding `err` | context for RE-Y-002 | `grep -rnE -A2 'if err != nil' --include='*.go'` and look for returns that do not wrap `err` |

## Rust

| Construct | Unit type | grep |
|---|---|---|
| `Err("...")`, `anyhow!("...")`, `bail!("...")`, `panic!("...")` | error-message | `grep -rnE '(anyhow!|bail!|panic!|Err\()\s*\(?["'\'']' --include='*.rs'` |
| `#[error("...")]` on thiserror enums | error-message | `grep -rnE '#\[error\(' --include='*.rs'` |
| `tracing::error!(`, `log::error!(` | log-line | `grep -rnE '(tracing|log)::(error|warn)!' --include='*.rs'` |

## Any language

- Message catalogs and i18n bundles: `errors.json`, `messages.properties`, `*.po`, `locales/*/`. Every value under an error key is an `error-message` unit; the catalog file and key are its location.
- Enum-to-string tables keyed by error code: each string is a unit, and the code is its `id`.
- OpenAPI or JSON Schema `description` fields on 4xx and 5xx responses: `error-message`, reader `user` or `model` depending on who consumes the API.

## Assigning the reader

| If the string is | Reader |
|---|---|
| shown in a UI, printed by a CLI meant for end users, returned in an API body to external callers | `user` |
| printed by deploy, migration, or admin tooling; returned to internal callers | `operator` |
| written to a log, included in a trace, asserted in a test | `developer` |
| returned from a function registered as an agent tool | `model` |

When a string reaches two readers (an API body that both a model and a person consume), record two units with the same text and different readers. The rules may answer differently.

## Context lines

Capture six lines above and two below. The lines above hold the catch or except clause (RE-Y-002), the variable that held the missing value (RE-Y-003), and any `moly: allow` marker. The lines below catch a multi-line string.
