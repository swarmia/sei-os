#!/usr/bin/env python3
"""Validate the rule book: skill frontmatter, catalog consistency, shared-file sync,
referenced files, company/ frontmatter and freshness, and privacy guards.

Usage: python3 scripts/validate.py [--upstream]
  --upstream  also require every company/ file to still be a template (for the public repository).
Standard library only.
"""
import contextlib
import datetime
import importlib.util
import io
import json
import tempfile
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
REF_RE = re.compile(r"`((?:references|scripts|assets)/[A-Za-z0-9_.\-/]+)`")
UUID_RE = re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b")
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
TOKEN_RE = re.compile(r"\b(sk-[A-Za-z0-9]{16,}|gh[pousr]_[A-Za-z0-9]{20,}|xox[abpr]-[A-Za-z0-9-]{10,}|AKIA[0-9A-Z]{16})\b")
STATUSES = {"template", "draft", "current"}
STALE_DAYS = 183
MAX_BODY_LINES = 160
SOURCE_TYPES = {"research", "report", "book", "manifesto", "vendor-docs", "internal"}
SOURCE_AUTHORITIES = {"reference", "benchmark", "policy"}
FOUNDATION = "foundation"  # bundle every skill must carry (shared Build vocabulary and answer rules)
errors, warnings, notes = [], [], []
UPSTREAM = "--upstream" in sys.argv[1:]


def frontmatter(text: str, where: str, report=True) -> dict:
    if not text.startswith("---\n"):
        if report:
            errors.append(f"{where}: missing YAML frontmatter")
        return {}
    end = text.find("\n---\n", 4)
    if end == -1:
        if report:
            errors.append(f"{where}: unterminated frontmatter")
        return {}
    data, parent = {}, None
    for line in text[4:end].splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith("  ") and parent:
            k, _, v = line.strip().partition(":")
            data.setdefault(parent, {})[k.strip()] = v.strip()
            continue
        k, _, v = line.partition(":")
        k, v = k.strip(), v.split(" #")[0].strip()
        if v == "":
            parent, data[k] = k, {}
        else:
            parent, data[k] = None, v
    return {k: ("" if v == {} else v) for k, v in data.items()}


def check_skills(catalog: dict) -> None:
    listed = {s["name"]: s for s in catalog["skills"]}
    folders = {p.name for p in (ROOT / "skills").iterdir() if p.is_dir()}
    for missing in sorted(set(listed) - folders):
        errors.append(f"catalog.json lists '{missing}' but skills/{missing}/ does not exist")
    for extra in sorted(folders - set(listed)):
        errors.append(f"skills/{extra}/ is not listed in catalog.json")

    if FOUNDATION not in catalog.get("bundles", {}):
        errors.append(f"catalog.json: missing the '{FOUNDATION}' bundle every skill builds on")
    for name, skill in sorted(listed.items()):
        if FOUNDATION not in skill.get("bundles", []):
            errors.append(f"catalog.json: skill '{name}' must list the '{FOUNDATION}' bundle")

    for name in sorted(folders & set(listed)):
        sdir = ROOT / "skills" / name
        where = f"skills/{name}/SKILL.md"
        if not (sdir / "SKILL.md").exists():
            errors.append(f"{where}: missing")
            continue
        text = (sdir / "SKILL.md").read_text(encoding="utf-8")
        fm = frontmatter(text, where)
        if fm.get("name") != name:
            errors.append(f"{where}: name '{fm.get('name')}' must match folder '{name}'")
        if not NAME_RE.match(name) or len(name) > 64:
            errors.append(f"{where}: name must be kebab-case, max 64 chars")
        desc = fm.get("description", "")
        if not desc:
            errors.append(f"{where}: missing description")
        elif len(desc) > 1024:
            errors.append(f"{where}: description is {len(desc)} chars (max 1024)")
        elif "Use when" not in desc:
            errors.append(f"{where}: description must include 'Use when …' triggers")
        meta = fm.get("metadata", {})
        if isinstance(meta, dict) and meta.get("pillar") != listed[name]["pillar"]:
            errors.append(f"{where}: metadata.pillar '{meta.get('pillar')}' != catalog '{listed[name]['pillar']}'")
        body_lines = text.split("\n---\n", 1)[1].count("\n") if "\n---\n" in text else 0
        if body_lines > MAX_BODY_LINES:
            warnings.append(f"{where}: body is {body_lines} lines; move detail into references/")
        for ref in sorted(set(REF_RE.findall(text))):
            if ref.endswith("/"):
                ok = (sdir / ref).is_dir()
            else:
                ok = (sdir / ref).exists()
            if not ok:
                errors.append(f"{where}: mentions `{ref}` but the skill does not carry it (add its bundle in catalog.json, then sync)")


def check_sync() -> None:
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "sync_shared.py"), "--check"], capture_output=True, text=True)
    if r.returncode:
        errors.append("shared files out of sync:\n    " + r.stderr.strip().replace("\n", "\n    "))


def check_source(rel, fm: dict, status: str) -> None:
    """company/sources/<slug>.md: a trusted outside source, linked rather than copied."""
    for key in ("type", "url", "authority", "content_in_repo", "use_for"):
        if key not in fm:
            errors.append(f"{rel}: trusted source needs '{key}' in frontmatter")
    if status == "template":
        return  # placeholders allowed until adopted
    checks = (("type", SOURCE_TYPES), ("authority", SOURCE_AUTHORITIES), ("content_in_repo", {"yes", "no"}))
    for key, allowed in checks:
        if fm.get(key) and fm[key] not in allowed:
            errors.append(f"{rel}: {key} '{fm[key]}' must be one of {', '.join(sorted(allowed))}")
    if not fm.get("url", "").startswith(("https://", "http://")):
        errors.append(f"{rel}: url must be a link agents can open")
    if not fm.get("use_for") or fm.get("use_for", "").startswith("<"):
        errors.append(f"{rel}: use_for must say which questions this source answers")


def check_company() -> None:
    today = datetime.date.today()
    templates = []
    for p in sorted((ROOT / "company").rglob("*.md")):
        rel = p.relative_to(ROOT)
        text = p.read_text(encoding="utf-8")
        in_teams = rel.parts[:2] == ("company", "teams")
        if in_teams and not UPSTREAM:
            continue  # the team folder may hold names and emails in a private copy; check_teams validates it

        # Privacy guards apply to every file, READMEs included.
        if EMAIL_RE.search(text):
            errors.append(f"{rel}: contains an email address; the rule book must not carry personal data")
        if TOKEN_RE.search(text):
            errors.append(f"{rel}: contains something that looks like a credential or API token")
        if "surveys" in rel.parts and p.name != "README.md":
            if any(line.startswith(">") for line in text.splitlines()):
                errors.append(f"{rel}: contains a block quote; survey comments must be paraphrased, never quoted")

        if p.name == "README.md" or in_teams:
            continue
        fm = frontmatter(text, str(rel))
        if not fm:
            continue
        if p.name == "_template.md":
            continue
        for key in ("title", "status", "owner", "last_reviewed"):
            if key not in fm:
                errors.append(f"{rel}: frontmatter needs '{key}'")
        status = fm.get("status", "")
        if status and status not in STATUSES:
            errors.append(f"{rel}: status '{status}' must be one of {', '.join(sorted(STATUSES))}")
        if "sources" in rel.parts:
            check_source(rel, fm, status)
        if status == "template":
            templates.append(str(rel))
            continue
        if UPSTREAM:
            errors.append(f"{rel}: status '{status}'; company/ files must stay templates in the public repository")
            continue
        if not fm.get("owner"):
            warnings.append(f"{rel}: no owner")
        reviewed = fm.get("last_reviewed", "")
        try:
            age = (today - datetime.date.fromisoformat(reviewed)).days
            if age > STALE_DAYS:
                warnings.append(f"{rel}: last reviewed {reviewed} ({age} days ago)")
        except ValueError:
            warnings.append(f"{rel}: last_reviewed '{reviewed}' is not a yyyy-mm-dd date")
    if templates:
        notes.append(f"{len(templates)} company file(s) still templates: " + ", ".join(templates))


def check_teams() -> None:
    """company/teams/: valid structure, no people upstream, never vendored, summary up to date."""
    folder = ROOT / "company" / "teams"
    if not folder.exists():
        return
    spec = importlib.util.spec_from_file_location("sei_teams", ROOT / "shared" / "scripts" / "teams.py")
    teams = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(teams)
    model = teams.read_folder(folder)
    for p in teams.problems(model):
        errors.append(f"company/teams: {p}")
    if UPSTREAM:
        extra = sorted(str(f.relative_to(ROOT)) for f in folder.rglob("*") if f.is_file() and f.name not in ("README.md", "people.md"))
        if model.get("status") != "template" or model.get("people") or model.get("teams") or extra:
            errors.append("company/teams: must stay an empty template in the public repository (no teams, no people)" + (f"; found {', '.join(extra[:3])}" if extra else ""))
    for leaked in sorted((ROOT / "skills").glob("*/references/company/teams")):
        errors.append(f"{leaked.relative_to(ROOT)}: the team folder holds people's names and must never be copied into a skill")
    summary = ROOT / "company" / "team-structure.md"
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "team-structure.md"
        ns = type("A", (), {"file": str(folder), "out": str(out)})
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            ok = teams.cmd_summary(ns) == 0
        if ok and (not summary.exists() or summary.read_text(encoding="utf-8") != out.read_text(encoding="utf-8")):
            errors.append("company/team-structure.md is out of date: run python3 shared/scripts/teams.py summary company/teams company/team-structure.md")


def check_examples() -> None:
    for p in list((ROOT / "examples").glob("*.json")) + list((ROOT / "skills").glob("*/SKILL.md")):
        t = p.read_text(encoding="utf-8")
        if UUID_RE.search(t):
            errors.append(f"{p.relative_to(ROOT)}: contains a UUID; examples and skills must not carry real organization ids")
    for p in (ROOT / "examples").glob("*.json"):
        t = p.read_text(encoding="utf-8").lower()
        if "fictional" not in t and "sample" not in t:
            errors.append(f"{p.relative_to(ROOT)}: example data must say it is fictional / sample")


def main() -> int:
    catalog = json.loads((ROOT / "catalog.json").read_text())
    check_skills(catalog)
    check_sync()
    check_company()
    check_teams()
    check_examples()
    for n in notes:
        print("note:", n)
    for w in warnings:
        print("warning:", w)
    for e in errors:
        print("error:", e)
    if errors:
        print(f"\n{len(errors)} error(s).")
        return 1
    print(f"OK: {len(catalog['skills'])} skills valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
