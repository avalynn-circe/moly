"""Renderers. Every renderer takes the same finding records."""

from __future__ import annotations

import json

SEVERITY_ORDER = {"block": 0, "warn": 1, "note": 2}
SARIF_LEVEL = {"block": "error", "warn": "warning", "note": "note"}


def _loc(f: dict) -> str:
    u = f["unit"]
    if "file" in u and "line" in u:
        return f"{u['file']}:{u['line']}"
    if "file" in u:
        return u["file"]
    return u.get("id", u["type"])


def to_markdown(findings: list[dict]) -> str:
    if not findings:
        return "No findings.\n"
    rows = sorted(findings, key=lambda f: (SEVERITY_ORDER[f["severity"]], f["rule"], _loc(f)))
    out = ["| Rule | Severity | Where | Message | Why it fails |", "|---|---|---|---|---|"]
    for f in rows:
        sev = f["severity"]
        if f.get("exception", {}).get("allowed"):
            sev = f"{sev} (allowed)"
        quote = f["quote"].replace("|", "\\|").replace("\n", " ")
        why = f["explain"].split(". ")[0].replace("|", "\\|") + "."
        out.append(f"| {f['rule']} | {sev} | {_loc(f)} | `{quote}` | {why} |")
    return "\n".join(out) + "\n"


def to_json(findings: list[dict]) -> str:
    return json.dumps(findings, indent=2, ensure_ascii=False) + "\n"


def to_sarif(findings: list[dict], tool_name: str = "moly", version: str = "0.1.0") -> str:
    rules: dict[str, dict] = {}
    results = []
    for f in findings:
        rules.setdefault(f["rule"], {
            "id": f["rule"],
            "shortDescription": {"text": f.get("title", f["rule"])},
            "fullDescription": {"text": f["explain"]},
            "defaultConfiguration": {"level": SARIF_LEVEL[f["severity"]]},
        })
        result = {
            "ruleId": f["rule"],
            "level": SARIF_LEVEL[f["severity"]],
            "message": {"text": f["explain"]},
        }
        if f.get("exception", {}).get("allowed"):
            result["suppressions"] = [{"kind": "inSource", "justification": f["exception"]["reason"]}]
        u = f["unit"]
        if "file" in u:
            region = {"startLine": u.get("line", 1)}
            if "column" in u:
                region["startColumn"] = u["column"]
            result["locations"] = [{
                "physicalLocation": {
                    "artifactLocation": {"uri": u["file"]},
                    "region": region,
                }
            }]
        results.append(result)
    sarif = {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [{
            "tool": {"driver": {"name": tool_name, "version": version, "rules": list(rules.values())}},
            "results": results,
        }],
    }
    return json.dumps(sarif, indent=2) + "\n"


RENDERERS = {"markdown": to_markdown, "json": to_json, "sarif": to_sarif}
