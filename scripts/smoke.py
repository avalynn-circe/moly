#!/usr/bin/env python3
"""Feed every mechanical rule's hit examples through scan as units and confirm each produces its finding.

The contract check tests the matcher. This tests the whole CLI path: load, scan, render, exception marker.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

pack = Path(sys.argv[1])
units, expected = [], set()
for rf in sorted((pack / "rules").glob("*.yml")):
    r = yaml.safe_load(rf.read_text())
    if r["kind"] != "mechanical":
        continue
    for i, ex in enumerate(r["examples"]["hits"]):
        uid = f"{r['id']}#{i}"
        units.append({"type": r["scope"][0], "text": ex["text"], "id": uid})
        expected.add((r["id"], uid))
# One allowed unit with a reason, one without, to exercise the marker path.
units.append({"type": "error-message", "text": "Something went wrong.", "id": "allowed",
              "context": "# moly: allow RE-W-001 last-resort handler; detail is logged under an id"})
units.append({"type": "error-message", "text": "Something went wrong.", "id": "allowed-no-reason",
              "context": "# moly: allow RE-W-001"})

with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
    json.dump(units, f)
    path = f.name
out = subprocess.run([sys.executable, "-m", "moly", "scan", str(pack), "--units", path, "--format", "json"],
                     capture_output=True, text=True, check=True).stdout
findings = json.loads(out)
got = {(f["rule"], f["unit"].get("id")) for f in findings}
missing = expected - got
problems = [f"no finding for {r} on unit {u}" for r, u in sorted(missing)]
allowed = [f for f in findings if f["unit"].get("id") == "allowed"]
if not (allowed and allowed[0].get("exception", {}).get("allowed")):
    problems.append("marker with reason did not mark the finding as allowed")
if not any(f["rule"] == "MOLY-X-001" and f["unit"].get("id") == "allowed-no-reason" for f in findings):
    problems.append("marker without reason did not raise MOLY-X-001")
for fmt in ("markdown", "sarif"):
    subprocess.run([sys.executable, "-m", "moly", "scan", str(pack), "--units", path, "--format", fmt],
                   capture_output=True, text=True, check=True)
Path(path).unlink()
for p in problems:
    print("FAIL", p)
print(f"smoke: {len(units)} units, {len(findings)} findings, {len(expected)} expected hits, {len(problems)} problem(s)")
sys.exit(1 if problems else 0)
