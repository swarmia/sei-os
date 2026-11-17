#!/usr/bin/env python3
"""Copy shared knowledge, assets, scripts and the company rule book into each skill folder.

Skills must work when their folder is copied on its own into an agent's skills
directory, so shared files are vendored into each skill instead of linked:

    knowledge/<f>       -> skills/<skill>/references/<f>
    company/<path>      -> skills/<skill>/references/company/<path>
    shared/assets/<f>   -> skills/<skill>/assets/<f>
    shared/scripts/<f>  -> skills/<skill>/scripts/<f>
    examples/<f>        -> skills/<skill>/assets/<f>

Which files each skill gets is defined by its "bundles" in catalog.json. A bundle
entry ending in "/" means every file under that folder. An entry starting with "!"
excludes that file or folder, whichever bundle added it (used to keep the team
roster, which may hold personal data, out of every installed skill).

Usage:
    python3 scripts/sync_shared.py          # write copies
    python3 scripts/sync_shared.py --check  # exit 1 if any copy is missing or stale
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ".sei-shared"  # lists the files sync manages inside a skill
MANAGED_DIRS = ("references", "assets", "scripts")


def target_for(src: str) -> str:
    p = Path(src)
    top = p.parts[0]
    if top == "knowledge":
        return str(Path("references") / p.name)
    if top == "company":
        return str(Path("references") / p)
    if top == "shared":
        return str(Path(p.parts[1]) / p.name)  # assets/ or scripts/
    if top == "examples":
        return str(Path("assets") / p.name)
    raise ValueError(f"Unsupported shared source: {src}")


def expand(entry: str) -> list:
    if not entry.endswith("/"):
        return [entry]
    base = ROOT / entry
    return sorted(
        str(f.relative_to(ROOT))
        for f in base.rglob("*")
        if f.is_file() and not f.name.startswith(".")
    )


def plan(catalog: dict) -> dict:
    out = {}
    for skill in catalog["skills"]:
        files, excluded = [], set()
        for b in skill.get("bundles", []):
            for entry in catalog["bundles"][b]:
                if entry.startswith("!"):
                    excluded.update(expand(entry[1:]))
                else:
                    files += expand(entry)
        out[skill["name"]] = sorted(set(files) - excluded)
    return out


def prune_empty_dirs(sdir: Path) -> None:
    for d in MANAGED_DIRS:
        top = sdir / d
        if not top.exists():
            continue
        for sub in sorted((p for p in top.rglob("*") if p.is_dir()), key=lambda p: len(p.parts), reverse=True):
            if not any(sub.iterdir()):
                sub.rmdir()
        if not any(top.iterdir()):
            top.rmdir()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    catalog = json.loads((ROOT / "catalog.json").read_text())
    problems = []
    for name, files in plan(catalog).items():
        sdir = ROOT / "skills" / name
        if not (sdir / "SKILL.md").exists():
            problems.append(f"{name}: skills/{name}/SKILL.md missing")
            continue
        wanted = {target_for(f): ROOT / f for f in files}
        manifest = sdir / MANIFEST
        previous = set(manifest.read_text().split()) if manifest.exists() else set()

        for rel, src in wanted.items():
            if not src.exists():
                problems.append(f"{name}: source {src.relative_to(ROOT)} missing")
                continue
            dst = sdir / rel
            same = dst.exists() and dst.read_bytes() == src.read_bytes()
            if args.check:
                if not same:
                    problems.append(f"{name}: {rel} is {'stale' if dst.exists() else 'missing'}")
            elif not same:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(src, dst)
                if dst.suffix == ".py":
                    dst.chmod(0o755)

        for rel in previous - set(wanted):
            stale = sdir / rel
            if args.check:
                problems.append(f"{name}: {rel} no longer in its bundles")
            elif stale.exists():
                stale.unlink()

        if not args.check:
            if wanted:
                manifest.write_text("\n".join(sorted(wanted)) + "\n")
            elif manifest.exists():
                manifest.unlink()
            prune_empty_dirs(sdir)
        elif set(wanted) != previous:
            problems.append(f"{name}: {MANIFEST} out of date")

    if problems:
        print("\n".join(problems), file=sys.stderr)
        if args.check:
            print("\nRun: python3 scripts/sync_shared.py", file=sys.stderr)
        return 1
    print("Shared files in sync." if args.check else "Synced shared files into skills.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
