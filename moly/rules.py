"""Load and validate packs and rules against the schemas in schema/."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_DIR = ROOT / "schema"
ID_RE = re.compile(r"^([A-Z]{2,5})-([A-Z])-(\d{3})$")


class PackError(Exception):
    """A pack or rule file does not meet the contract."""


@dataclass
class Rule:
    data: dict
    path: Path
    compiled: list[re.Pattern] = field(default_factory=list)
    compiled_unless: list[re.Pattern] = field(default_factory=list)
    compiled_prefilter: list[re.Pattern] = field(default_factory=list)

    @property
    def id(self) -> str:
        return self.data["id"]

    @property
    def kind(self) -> str:
        return self.data["kind"]

    @property
    def severity(self) -> str:
        return self.data["severity"]

    @property
    def scope(self) -> list[str]:
        return self.data["scope"]

    def __post_init__(self) -> None:
        flags = 0 if self.data["detect"].get("case") else re.IGNORECASE
        d = self.data["detect"]
        try:
            self.compiled = [re.compile(p, flags) for p in d.get("patterns", [])]
            self.compiled_unless = [re.compile(p, flags) for p in d.get("unless", [])]
            self.compiled_prefilter = [re.compile(p, flags) for p in d.get("prefilter", [])]
        except re.error as e:
            raise PackError(f"{self.id}: bad regular expression: {e}") from e

    def mechanical_match(self, text: str) -> re.Match | None:
        """Return the first pattern match, unless an `unless` pattern cancels it."""
        if self.kind != "mechanical":
            return None
        for pat in self.compiled:
            m = pat.search(text)
            if m:
                if any(u.search(text) for u in self.compiled_unless):
                    return None
                return m
        return None

    def is_candidate(self, text: str) -> bool:
        """Judged rules: does the unit pass the prefilter? No prefilter means every unit is a candidate."""
        if not self.compiled_prefilter:
            return True
        return any(p.search(text) for p in self.compiled_prefilter)


@dataclass
class Pack:
    data: dict
    path: Path
    rules: list[Rule]

    @property
    def slug(self) -> str:
        return self.data["slug"]

    @property
    def prefix(self) -> str:
        return self.data["prefix"]

    @property
    def unit_types(self) -> set[str]:
        return {u["type"] for u in self.data["units"]}

    @property
    def area_letters(self) -> dict[str, str]:
        return {a["letter"]: a["name"] for a in self.data["areas"]}


def _schema(name: str) -> dict:
    return json.loads((SCHEMA_DIR / f"{name}.schema.json").read_text())


def _validate(instance: dict, schema_name: str, where: Path) -> None:
    validator = jsonschema.Draft202012Validator(_schema(schema_name))
    errors = sorted(validator.iter_errors(instance), key=lambda e: list(e.path))
    if errors:
        lines = [f"{where}: does not match {schema_name} schema"]
        for e in errors:
            loc = "/".join(str(p) for p in e.path) or "<root>"
            lines.append(f"  at {loc}: {e.message}")
        raise PackError("\n".join(lines))


def load_pack(pack_dir: Path) -> Pack:
    """Load pack.yml and every rules/*.yml, validate both, and cross-check them."""
    pack_dir = Path(pack_dir)
    pack_file = pack_dir / "pack.yml"
    if not pack_file.exists():
        raise PackError(f"{pack_dir}: no pack.yml. A pack directory holds pack.yml and rules/.")
    pack_data = yaml.safe_load(pack_file.read_text())
    _validate(pack_data, "pack", pack_file)

    rules: list[Rule] = []
    problems: list[str] = []
    for rule_file in sorted((pack_dir / "rules").glob("*.yml")):
        data = yaml.safe_load(rule_file.read_text())
        _validate(data, "rule", rule_file)
        rule = Rule(data, rule_file)
        if rule_file.stem != rule.id:
            problems.append(f"{rule_file}: file is named {rule_file.stem} but the rule id is {rule.id}")
        m = ID_RE.match(rule.id)
        prefix, letter = m.group(1), m.group(2)
        if prefix != pack_data["prefix"]:
            problems.append(f"{rule.id}: prefix {prefix} is not the pack prefix {pack_data['prefix']}")
        areas = {a["letter"]: a["name"] for a in pack_data["areas"]}
        if letter not in areas:
            problems.append(f"{rule.id}: area letter {letter} is not declared in pack.yml")
        elif areas[letter] != data["area"]:
            problems.append(f"{rule.id}: area is '{data['area']}' but letter {letter} means '{areas[letter]}'")
        unit_types = {u["type"] for u in pack_data["units"]}
        for s in data["scope"]:
            if s not in unit_types:
                problems.append(f"{rule.id}: scope '{s}' is not a unit type in pack.yml")
        rules.append(rule)

    ids = [r.id for r in rules]
    for dup in {i for i in ids if ids.count(i) > 1}:
        problems.append(f"{dup}: declared more than once")
    if not rules:
        problems.append(f"{pack_dir}: no rules in rules/")
    if problems:
        raise PackError("\n".join(problems))
    return Pack(pack_data, pack_dir, rules)
