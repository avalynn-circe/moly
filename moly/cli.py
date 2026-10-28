"""moly command line.

  python -m moly check <pack-dir>                 validate schemas and run the fixture contract
  python -m moly scan  <pack-dir> --units f.json  mechanical tier over extracted units
  python -m moly candidates <pack-dir> --units f  units each judged rule wants the agent to read
  python -m moly explain <pack-dir> <RULE-ID>     print one rule, for an agent or a person
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

from moly.check import check_pack
from moly.render import RENDERERS
from moly.rules import PackError, load_pack
from moly.scan import candidates, scan_units


def _load_units(path: str) -> list[dict]:
    data = json.loads(Path(path).read_text()) if path != "-" else json.load(sys.stdin)
    if not isinstance(data, list):
        raise SystemExit("units must be a JSON list of {type, text, ...}")
    for i, u in enumerate(data):
        if "type" not in u or "text" not in u:
            raise SystemExit(f"unit {i} needs 'type' and 'text'")
    return data


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="moly", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("check", help="validate a pack and run its fixture contract")
    p.add_argument("pack")

    p = sub.add_parser("scan", help="run mechanical rules over units")
    p.add_argument("pack")
    p.add_argument("--units", required=True, help="JSON file of units, or - for stdin")
    p.add_argument("--format", choices=sorted(RENDERERS), default="markdown")
    p.add_argument("--fail-on", choices=["block", "warn", "note", "never"], default="never",
                   help="exit 1 when a finding at this severity or above is not allowed (gate mode)")

    p = sub.add_parser("candidates", help="units each judged rule's prefilter admits")
    p.add_argument("pack")
    p.add_argument("--units", required=True)

    p = sub.add_parser("explain", help="print one rule")
    p.add_argument("pack")
    p.add_argument("rule_id")

    args = ap.parse_args(argv)
    try:
        pack = load_pack(Path(args.pack))
    except PackError as e:
        print(f"moly: {e}", file=sys.stderr)
        return 2

    if args.cmd == "check":
        report = check_pack(pack)
        print(f"{report.pack}: {report.rules} rules ({report.mechanical} mechanical, {report.judged} judged)")
        for f in report.failures:
            print(f"  FAIL {f}")
        print("contract holds" if report.ok else f"{len(report.failures)} contract failure(s)")
        return 0 if report.ok else 1

    if args.cmd == "scan":
        units = _load_units(args.units)
        findings = scan_units(pack, units)
        sys.stdout.write(RENDERERS[args.format](findings))
        if args.fail_on == "never":
            return 0
        rank = {"block": 0, "warn": 1, "note": 2}
        bad = [f for f in findings if rank[f["severity"]] <= rank[args.fail_on]
               and not f.get("exception", {}).get("allowed")]
        return 1 if bad else 0

    if args.cmd == "candidates":
        units = _load_units(args.units)
        print(json.dumps(candidates(pack, units), indent=2, ensure_ascii=False))
        return 0

    if args.cmd == "explain":
        for r in pack.rules:
            if r.id == args.rule_id.upper():
                sys.stdout.write(yaml.safe_dump(r.data, sort_keys=False, allow_unicode=True, width=100))
                return 0
        print(f"moly: no rule {args.rule_id} in {pack.slug}", file=sys.stderr)
        return 2
    return 0
