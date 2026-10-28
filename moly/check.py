"""The contract check: every mechanical rule hits its hits and misses its passes.

Judged rules cannot be run here. For them, the check confirms that the prefilter
(when one exists) admits every hit, so the model is never prevented from seeing
a case the rule's own examples say it must catch.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from moly.rules import Pack


@dataclass
class CheckReport:
    pack: str
    rules: int = 0
    mechanical: int = 0
    judged: int = 0
    failures: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.failures


def check_pack(pack: Pack) -> CheckReport:
    report = CheckReport(pack=pack.slug, rules=len(pack.rules))
    for rule in pack.rules:
        hits = rule.data["examples"]["hits"]
        passes = rule.data["examples"]["passes"]
        if rule.kind == "mechanical":
            report.mechanical += 1
            for ex in hits:
                if not rule.mechanical_match(ex["text"]):
                    report.failures.append(f"{rule.id}: expected a hit, got none: {ex['text']!r}")
            for ex in passes:
                m = rule.mechanical_match(ex["text"])
                if m:
                    report.failures.append(
                        f"{rule.id}: expected a pass, pattern matched {m.group(0)!r} in {ex['text']!r}"
                    )
        else:
            report.judged += 1
            for ex in hits:
                probe = ex["text"] + "\n" + ex.get("context", "")
                if not rule.is_candidate(probe):
                    report.failures.append(
                        f"{rule.id}: prefilter excludes one of the rule's own hits: {ex['text']!r}"
                    )
    return report
