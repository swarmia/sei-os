#!/usr/bin/env python3
"""Render an SEI OS report: inject report-data JSON into the self-contained HTML template.

Usage:
    python3 render_report.py report-data.json report.html [--template path/to/report-template.html]

Standard library only. The output HTML has no external dependencies, so it can be
opened offline, attached to an email, or printed to PDF from any browser.
"""
import argparse
import json
import sys
from pathlib import Path

PLACEHOLDER = "/*__REPORT_DATA__*/"
CHART_TYPES = {"bar", "stacked", "line", "scorecard", "table"}
STATUSES = {"great", "good", "attention", "unknown", None}


def default_template() -> Path:
    here = Path(__file__).resolve().parent
    # Inside an installed skill: <skill>/scripts/render_report.py + <skill>/assets/report-template.html
    # Inside the repo: shared/scripts/render_report.py + shared/assets/report-template.html
    return here.parent / "assets" / "report-template.html"


def lint(data: dict) -> list:
    problems = []
    if not data.get("title"):
        problems.append("missing 'title'")
    if not data.get("method"):
        problems.append("missing 'method' (every report needs a 'How this was calculated' block)")
    for k in data.get("kpis", []):
        if k.get("status") not in STATUSES:
            problems.append(f"kpi '{k.get('label')}': status must be great|good|attention|unknown")
    for si, sec in enumerate(data.get("sections", [])):
        for ci, ch in enumerate(sec.get("charts", [])):
            where = f"sections[{si}].charts[{ci}]"
            t = ch.get("type")
            if t not in CHART_TYPES:
                problems.append(f"{where}: unknown type '{t}' (use one of {sorted(CHART_TYPES)})")
            if t == "stacked":
                n = len(ch.get("series", []))
                if n > 8:
                    problems.append(f"{where}: {n} series; fold the smallest into 'Other' (max 8)")
                for r in ch.get("rows", []):
                    if len(r.get("values", [])) != n:
                        problems.append(f"{where}: row '{r.get('label')}' has {len(r.get('values', []))} values for {n} series")
            if t == "line":
                xs = len(ch.get("x", []))
                if len(ch.get("series", [])) > 8:
                    problems.append(f"{where}: more than 8 series; use small multiples")
                for s in ch.get("series", []):
                    if len(s.get("values", [])) != xs:
                        problems.append(f"{where}: series '{s.get('name')}' has {len(s.get('values', []))} values for {xs} x labels")
            if t == "scorecard":
                for p in ch.get("pillars", []):
                    for g in p.get("groups", []):
                        if g.get("status") not in STATUSES:
                            problems.append(f"{where}: group '{g.get('name')}' has invalid status '{g.get('status')}'")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("data", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--template", type=Path, default=None)
    args = ap.parse_args()

    data = json.loads(args.data.read_text(encoding="utf-8"))
    problems = lint(data)
    if problems:
        print("Report data has problems:\n  - " + "\n  - ".join(problems), file=sys.stderr)
        return 1

    template = (args.template or default_template()).read_text(encoding="utf-8")
    if PLACEHOLDER not in template:
        print(f"Template has no {PLACEHOLDER} placeholder", file=sys.stderr)
        return 1
    # Escape "</" so data can never close the surrounding <script> tag.
    payload = json.dumps(data, ensure_ascii=False, indent=1).replace("</", "<\\/")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(template.replace(PLACEHOLDER, payload, 1), encoding="utf-8")
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
