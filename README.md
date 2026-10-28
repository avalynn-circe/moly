# Moly

A shared rules engine for text that pretends to inform. Moly reads a unit of text, finds where it fails its reader, explains why, and proposes the text that would not. One engine; many packs. The first pack is **Readable Errors**: error messages that say what happened, why, and what to do next.

The name is the herb that let Odysseus see through Circe's enchantment.

## What is here

| Path | What |
|---|---|
| `docs/engine.md` | The engine specification: units, readers, two tiers of rules, the pipeline, severity, exceptions, findings, modes, the contract, stability. |
| `docs/rule-format.md` | Field-by-field reference for a rule file. |
| `docs/packs.md` | What a pack is, how the voice layer works, how rules are shared across packs. |
| `docs/readable-errors.md` | The first pack: who buys it, the fourteen rules, the four readers, modes, limits. |
| `docs/roadmap.md` | What comes next, in order. |
| `schema/` | JSON Schema for a rule, a pack, and a finding. |
| `packs/readable-errors/` | The pack: `pack.yml`, fourteen rules, `SKILL.md`, references, and the drafted Agensi listing. |
| `moly/` | Reference implementation: load, validate, contract check, mechanical scan, candidates for the judged tier, renderers. |
| `scripts/build_pack.py` | Assembles a pack into a self-contained skill folder with a one-file engine. |
| `styles/Circe/` | The Circe Editorial Standard as a Vale style. Prose in this repository is held to it. |

## The idea in one paragraph

Every rule is either **mechanical** (regular expressions, deterministic, runs in CI) or **judged** (a yes/no question a model answers about one unit, with evidence it must quote). Both kinds share one file format, one finding record, and one contract: a rule's examples are its test, and `moly check` fails a pack whose mechanical rules miss their own examples or whose judged rules' prefilters hide them. A pack adds a method, the kinds of text it reads, who reads them, and a voice. The voice may restyle an explanation and may never change its claim. Readable Errors uses a plain voice; packs with a persona are on the roadmap and the seam for them already exists.

## Run it

```bash
pip install -r requirements.txt

# Validate the schemas and run the fixture contract for a pack
python -m moly check packs/readable-errors

# Print one rule
python -m moly explain packs/readable-errors RE-N-004

# Mechanical tier over units an agent extracted (see packs/readable-errors/references/extraction.md)
python -m moly scan packs/readable-errors --units units.json --format markdown
python -m moly scan packs/readable-errors --units units.json --format sarif --fail-on block   # gate mode

# Units each judged rule wants the agent to read
python -m moly candidates packs/readable-errors --units units.json

# Build the skill folder for a marketplace
python scripts/build_pack.py packs/readable-errors dist/
```

A unit is `{"type": "error-message", "text": "...", "file": "...", "line": 42, "reader": "user", "context": "..."}`. Extraction is the agent's job in this version; mechanical extractors are the first roadmap item.

## What runs on a push

| Job | What happens |
|---|---|
| Rule contract | Every pack validates against the schemas and passes its fixture contract. The Readable Errors skill folder builds and its one-file engine passes the same check. A smoke test runs every mechanical hit example through the CLI, including the allow-marker path. |
| Circe Editorial Standard | Vale lints the prose with the `Circe` style. Error-level rules fail the job. |

## Status

Readable Errors 0.1.0: fourteen rules, four mechanical and ten judged, contract green. Not yet listed. The listing fields are drafted in `packs/readable-errors/agensi.yml`.

## Add a rule

1. Create `packs/<pack>/rules/<ID>.yml`. Follow `docs/rule-format.md`. Include at least one hit and one pass.
2. Run `python -m moly check packs/<pack>`. Fix what it reports.
3. If the rule is judged and has a prefilter, confirm the prefilter admits every hit. The check does this for you.
4. Open a pull request. The checks run on it.

## Add a pack

1. Create `packs/<slug>/pack.yml` with a method, units, areas, and a voice. Pick a prefix no other pack uses.
2. Add rules as above.
3. Add `SKILL.md` and `references/` when the pack is for a marketplace.
4. Add the pack to the build step in `.github/workflows/quality.yml`.
