"""Run the mechanical tier over units and emit findings.

Units arrive as a JSON list of {type, text, file?, line?, reader?}. Extraction is the
agent's job in this version; see docs/engine.md, section Extract. A unit whose line
carries an allow-marker for the rule is still reported, flagged as allowed.
"""

from __future__ import annotations

import re

from moly.rules import Pack, Rule

MARKER_RE = re.compile(r"moly:\s*allow\s+([A-Z]{2,5}-[A-Z]-\d{3})\s*(.*)$", re.IGNORECASE)
ENGINE_RULE_EMPTY_REASON = "MOLY-X-001"


def parse_markers(context: str | None) -> dict[str, str]:
    """Return {rule_id: reason} for every allow-marker in the unit's context."""
    found: dict[str, str] = {}
    if not context:
        return found
    for line in context.splitlines():
        m = MARKER_RE.search(line)
        if m:
            found[m.group(1).upper()] = m.group(2).strip().strip('"').strip("'")
    return found


def _finding(rule: Rule, pack: Pack, unit: dict, quote: str) -> dict:
    fix = {"kind": rule.data["fix"]["kind"]}
    if "template" in rule.data["fix"]:
        fix["proposed"] = rule.data["fix"]["template"]
    if "steps" in rule.data["fix"]:
        fix["steps"] = rule.data["fix"]["steps"]
    if rule.data["fix"].get("touches_tests"):
        fix["touches_tests"] = True
    loc = {"type": unit["type"]}
    for k in ("file", "line", "column", "reader", "id"):
        if k in unit and unit[k] is not None:
            loc[k] = unit[k]
    return {
        "rule": rule.id,
        "pack": pack.slug,
        "title": rule.data["title"],
        "severity": rule.severity,
        "kind": rule.kind,
        "unit": loc,
        "quote": quote,
        "explain": rule.data["explain"].strip(),
        "fix": fix,
    }


def scan_units(pack: Pack, units: list[dict]) -> list[dict]:
    findings: list[dict] = []
    for unit in units:
        text = unit["text"]
        markers = parse_markers(unit.get("context"))
        for rule in pack.rules:
            if unit["type"] not in rule.scope:
                continue
            if rule.kind != "mechanical":
                continue
            m = rule.mechanical_match(text)
            if not m:
                continue
            f = _finding(rule, pack, unit, text)
            if rule.id in markers:
                reason = markers[rule.id]
                f["exception"] = {"allowed": bool(reason), "reason": reason or "(no reason given)"}
                if not reason:
                    findings.append({
                        "rule": ENGINE_RULE_EMPTY_REASON,
                        "pack": "moly",
                        "title": "An allow-marker gives no reason",
                        "severity": "warn",
                        "kind": "mechanical",
                        "unit": f["unit"],
                        "quote": f"moly: allow {rule.id}",
                        "explain": "The marker silences a rule and says nothing about why. "
                                   "A reader cannot tell a judged exception from a shortcut. Add the reason.",
                        "fix": {"kind": "rewrite", "proposed": f"moly: allow {rule.id} <why the text may stand>"},
                    })
            findings.append(f)
    return findings


def candidates(pack: Pack, units: list[dict]) -> dict[str, list[dict]]:
    """For each judged rule, the units the prefilter admits. The agent reads these, not everything."""
    out: dict[str, list[dict]] = {}
    for rule in pack.rules:
        if rule.kind != "judged":
            continue
        out[rule.id] = [
            u for u in units
            if u["type"] in rule.scope and rule.is_candidate(u["text"] + "\n" + (u.get("context") or ""))
        ]
    return out
