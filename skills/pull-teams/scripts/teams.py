#!/usr/bin/env python3
"""Work with the team structure in company/teams/ (people.md plus one folder per team).

Every command that takes TEAMS accepts the folder or a JSON model of it.

Commands:
    teams.py check   TEAMS                              validate structure (keys, parents, people, attributes)
    teams.py summary TEAMS team-structure.md            write the people-free summary other skills read
    teams.py write   model.json company/teams           write a model as the folder (keeps your extra sections)
    teams.py read    company/teams --out model.json     read the folder into a model
    teams.py from-swarmia raw.json --out new.json [--merge company/teams] [--drop-local]
                          [--users u.json] [--roles r.json] [--attributes a.json] [--team-ids t.json]
                          [--repos r.json --repo-names n.json] [--agreements w.json] [--ownership o-*.json]
                                                        convert Swarmia's ListTeamsAndMembers output, keeping local
                                                        missions, ownership and attributes from --merge; team context
                                                        (main repositories, issue ownership, working agreements) is
                                                        refreshed when its input is passed, else kept from --merge
    teams.py extract [--transcript session.jsonl] --out DIR
                                                        write the Swarmia responses of this Claude Code session
                                                        to input files, unchanged (no re-typing)
    teams.py from-compact compact.tsv --out DIR         the same input files from compact tab-separated text
                                                        (agents without a readable transcript)
    teams.py detach  company/teams TEAM [--github-team NAME]
                                                        cut a GitHub sync: copy the GitHub team's people into Members
                                                        and mark it (unlink) for the next push
    teams.py diff    OLD NEW                            readable list of changes from OLD to NEW (folders or models)
    teams.py plan    TEAMS remote.json [--allow-delete]
                                                        print the Swarmia PlanTeamUpdates input that makes
                                                        Swarmia match TEAMS; a readable summary goes to stderr

remote.json is the current Swarmia structure as a model (made with from-swarmia
from a saved ListTeamsAndMembers response).

Standard library only.
"""
import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

STATUSES = {"template", "draft", "current"}
MIN_GROUP = 5  # smallest group for which attribute counts are shown in the summary


def load(path: str) -> dict:
    """A team folder (company/teams/) or a JSON file (Swarmia responses, internal models)."""
    if Path(path).is_dir():
        return read_folder(path)
    return json.loads(Path(path).read_text(encoding="utf-8"))


def problems(data: dict) -> list:
    out = list(data.get("folderErrors", []))
    if data.get("status") not in STATUSES:
        out.append(f"status must be one of {', '.join(sorted(STATUSES))}")
    teams = data.get("teams", [])
    if not isinstance(teams, list):
        return out + ["teams must be a list"]
    declared = data.get("attributes", {}) or {}
    keys = [t.get("key") for t in teams]
    for k, n in Counter(keys).items():
        if not k:
            out.append("every team needs a key (its Swarmia external ID, or a new slug for a team to create)")
        elif n > 1:
            out.append(f"team key '{k}' is used {n} times")
    by_key = {t.get("key"): t for t in teams}
    for t in teams:
        where = f"team '{t.get('key')}'"
        if not t.get("name"):
            out.append(f"{where}: needs a name")
        parent = t.get("parent")
        if parent is not None and parent not in by_key:
            out.append(f"{where}: parent '{parent}' is not a team in this file")
        seen, p = {t.get("key")}, parent
        while p is not None and p in by_key:
            if p in seen:
                out.append(f"{where}: parent chain loops through '{p}'")
                break
            seen.add(p)
            p = by_key[p].get("parent")
        for m in people_of(t):
            if not m.get("name"):
                out.append(f"{where}: every member needs a name")
            for attr, value in (m.get("attributes") or {}).items():
                if attr not in declared:
                    out.append(f"{where}: member attribute '{attr}' is not declared in 'attributes'")
                elif declared[attr] and value not in declared[attr]:
                    out.append(f"{where}: '{value}' is not an allowed value of '{attr}'")
    seen_attrs = {}
    for t in teams:
        for m in people_of(t):
            if not m.get("attributes"):
                continue
            pid = min(identities(m))
            if pid in seen_attrs and seen_attrs[pid] != m["attributes"]:
                out.append(f"'{m.get('name')}' has different attributes on different teams; keep one set per person")
            seen_attrs.setdefault(pid, m["attributes"])
    for m in data.get("people", []):
        for attr, value in (m.get("attributes") or {}).items():
            if attr not in declared:
                out.append(f"people.md: column '{attr}' is not listed under Attributes")
            elif declared[attr] and value not in declared[attr]:
                out.append(f"people.md: '{value}' is not an allowed value of '{attr}' (for {m.get('name')})")
    for k, n in Counter(min(identities(m)) for m in data.get("people", []) if m.get("swarmiaAuthorId") or m.get("email")).items():
        if n > 1:
            out.append(f"people.md: the same person ({k.split(':', 1)[1]}) has {n} rows")
    if data.get("status") == "template" and (any(people_of(t) for t in teams) or data.get("people")):
        out.append("a template must not list people")
    return out


def people_of(t: dict) -> list:
    """Direct members plus the members of linked GitHub teams (read-only, managed in GitHub)."""
    return list(t.get("members", [])) + [m for g in t.get("githubTeams", []) for m in g.get("members", [])]


def is_bot(m: dict) -> bool:
    return m.get("name", "").lower().endswith("[bot]")


def cmd_check(args) -> int:
    errs = problems(load(args.file))
    for e in errs:
        print("error:", e, file=sys.stderr)
    if not errs:
        print("team structure OK")
    return 1 if errs else 0


def unique_people(people: list) -> list:
    """People counted once, matched on Swarmia ID or email; bot accounts left out."""
    out, seen = [], []
    for m in people:
        if is_bot(m):
            continue
        ids = identities(m)
        if any(ids & s for s in seen):
            continue
        seen.append(ids)
        out.append(m)
    return out


def headcount(t: dict) -> int:
    n = len(unique_people(people_of(t)))
    # GitHub teams recorded without their member list still count by memberCount
    return n + sum(int(g.get("memberCount") or 0) for g in t.get("githubTeams", []) if not g.get("members"))


def group_counts(c: Counter) -> str:
    """Counts per value, with values held by fewer than MIN_GROUP people folded into 'other' (and 'unset' kept)."""
    shown = {k: n for k, n in c.items() if n >= MIN_GROUP or k == "unset"}
    other = sum(n for k, n in c.items() if k not in shown)
    parts = [f"{k} {n}" for k, n in sorted(shown.items()) if k != "unset"]
    if other:
        parts.append(f"other {other}")
    if c.get("unset"):
        parts.append(f"unset {c['unset']}")
    return ", ".join(parts)


def cmd_summary(args) -> int:
    data = load(args.file)
    errs = problems(data)
    if errs:
        print("\n".join("error: " + e for e in errs), file=sys.stderr)
        return 1
    teams = data.get("teams", [])
    by_key = {t["key"]: t for t in teams}
    children = {}
    for t in teams:
        children.setdefault(t.get("parent"), []).append(t)

    rows = []

    def walk(parent, depth):
        for t in sorted(children.get(parent, []), key=lambda x: x["name"].lower()):
            gh = ", ".join(g.get("name") or g.get("id", "") for g in t.get("githubTeams", []))
            rows.append(
                f"| {'↳ ' * depth}{t['name']} | `{t['key']}` | {by_key[t['parent']]['name'] if t.get('parent') else ''} "
                f"| {t.get('mission', '')} | {', '.join(t.get('owns', []))} | {headcount(t)} | {len(t.get('admins', []))} | {membership(t)} | {gh} |"
            )
            walk(t["key"], depth + 1)

    walk(None, 0)
    fm = "\n".join(
        [
            "---",
            "title: Team structure",
            f"status: {data.get('status', 'template')}",
            f"owner: {data.get('owner', '')}",
            f"last_reviewed: {data.get('last_reviewed', '')}",
            "generated_from: company/teams/",
            "---",
        ]
    )
    lines = [
        fm,
        "",
        "# Team structure",
        "",
        "Generated from `company/teams/` by `teams.py summary`. Do not edit by hand: change the team folders (or pull from Swarmia) and regenerate. "
        "This file holds no names, so every skill can read it.",
        "",
        f"Source: {data.get('source', 'manual')}" + (f", pulled {data['pulled_at']}" if data.get("pulled_at") else "") + ".",
        "",
        "| Team | Key | Parent | Mission | Owns | Headcount | Team admins | Membership | GitHub teams |",
        "|---|---|---|---|---|---|---|---|---|",
    ] + (rows or ["| | | | | | | | | |"])

    detailed = [t for t in teams if any(t.get(f) for f in PULLED_SECTIONS.values())]
    if detailed:
        lines += ["", "## Team context from Swarmia", "", "Main repositories, issue ownership and working agreements per team, as pulled from Swarmia."]
        order = []

        def walk_keys(parent):
            for t in sorted(children.get(parent, []), key=lambda x: x["name"].lower()):
                order.append(t)
                walk_keys(t["key"])

        walk_keys(None)
        for t in order:
            if t not in detailed:
                continue
            lines += ["", f"### {t['name']}"]
            for title, field in PULLED_SECTIONS.items():
                if t.get(field):
                    lines += ["", f"{title}:", ""] + [f"  - {l.strip()}" if l.startswith("  ") else f"- {l}" for l in t[field]]

    declared = data.get("attributes", {}) or {}
    if declared and teams:
        everyone = unique_people([m for t in teams for m in people_of(t)])
        lines += ["", "## Composition", "",
                  f"Counts by attribute, each person once, bots left out. This file holds no individual data: a value held by fewer than "
                  f"{MIN_GROUP} people is counted under `other`, teams with fewer than {MIN_GROUP} people are only in the organization total, "
                  f"and attributes whose values mostly identify single people (IDs, dates) are not summarized. People.md keeps every value."]
        skipped = []
        for attr in declared:
            org = Counter(m.get("attributes", {}).get(attr, "unset") for m in everyone)
            if sum(n for k, n in org.items() if k != "unset" and n >= MIN_GROUP) < sum(n for k, n in org.items() if k != "unset") / 2:
                skipped.append(attr)  # most people would land in 'other': the attribute is individual, not a grouping
                continue
            lines += ["", f"**{attr}**: organization: " + group_counts(org)]
            for t in sorted(teams, key=lambda x: x["name"].lower()):
                team_people = unique_people(people_of(t))
                if len(team_people) >= MIN_GROUP:
                    c = Counter(m.get("attributes", {}).get(attr, "unset") for m in team_people)
                    lines.append(f"- {t['name']}: " + group_counts(c))
        if skipped:
            lines += ["", "Not summarized (values mostly identify single people): " + ", ".join(skipped) + "."]
    Path(args.out).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {args.out} ({len(teams)} teams)")
    return 0


def identities(m: dict) -> set:
    ids = set()
    if m.get("swarmiaAuthorId"):
        ids.add("id:" + m["swarmiaAuthorId"])
    if m.get("email"):
        ids.add("email:" + m["email"].lower())
    if not ids:
        ids.add("name:" + m.get("name", "").lower())
    return ids


MEMBERSHIP_NOTE = {
    "github": "synced from GitHub: members come only from linked GitHub teams; change them in GitHub",
    "mixed": "linked GitHub teams plus people added directly",
    "manual": "people added directly in Swarmia or here",
}


def linked(t: dict) -> list:
    """GitHub teams that stay linked. A GitHub team marked `(unlink)` in team.md is to be unlinked on the next push."""
    return [g for g in t.get("githubTeams", []) if not g.get("unlink")]


def membership(t: dict) -> str:
    """How a team gets its members: 'github' (only linked GitHub teams, kept in sync by Swarmia),
    'mixed' (GitHub teams plus direct members) or 'manual' (direct members only, or none).
    Team admins are a role, not membership; Viewer and Editor are organization-wide roles."""
    if linked(t):
        return "mixed" if t.get("members") else "github"
    return "manual"


def member_diff(local: dict, remote: dict) -> tuple:
    """(added, removed) counts; a person matches on Swarmia ID or email, whichever both sides have."""
    rem = [identities(m) for m in remote.get("members", [])]
    matched, added = set(), 0
    for m in local.get("members", []):
        ids = identities(m)
        hit = next((i for i, r in enumerate(rem) if i not in matched and r & ids), None)
        if hit is None:
            added += 1
        else:
            matched.add(hit)
    removed = len(rem) - len(matched)
    lg = {str(g["id"]) for g in linked(local)}
    rg = {str(g["id"]) for g in linked(remote)}
    return added + len(lg - rg), removed + len(rg - lg)


def push_members(t: dict, where: str, errs: list) -> list:
    out = []
    for m in t.get("members", []):
        if m.get("swarmiaAuthorId"):
            out.append({"authorId": m["swarmiaAuthorId"]})
        elif m.get("email"):
            out.append({"name": m["name"], "email": m["email"]})
        else:
            errs.append(f"{where}: member '{m.get('name')}' has no swarmiaAuthorId or email, so Swarmia cannot match them")
    out += [{"githubTeamId": g["id"]} for g in linked(t)]
    return out


def cmd_plan(args) -> int:
    local, remote = load(args.local), load(args.remote)
    errs = problems(local)
    if not args.preview and local.get("status") != "current":
        errs.append("company/teams/people.md must be status: current (reviewed) before pushing")
    lt = {t["key"]: t for t in local.get("teams", [])}
    rt = {t["key"]: t for t in remote.get("teams", [])}
    plan = {"create": [], "update": [], "delete": []}
    notes = []

    for key, t in lt.items():
        where = f"team '{t['name']}'"
        if key not in rt:
            plan["create"].append({"teamKey": key, "name": t["name"], "parent": t.get("parent"), "members": push_members(t, where, errs)})
            notes.append(f"create  {t['name']} ({key})")
            continue
        r, change = rt[key], {"teamKey": key}
        if t["name"] != r.get("name"):
            change["name"] = t["name"]
            notes.append(f"rename  {r.get('name')} -> {t['name']}")
        if t.get("parent") != r.get("parent"):
            change["parent"] = t.get("parent")
            def label(k):
                return "(top level)" if k is None else (lt.get(k) or rt.get(k) or {"name": k})["name"]

            notes.append(f"move    {t['name']}: under {label(r.get('parent'))} -> under {label(t.get('parent'))}")
        # Protect GitHub syncs, judged on Swarmia's current state so a local edit cannot switch it off.
        # Unlinking needs intent in the file (`(unlink)` on the GitHub team line, see `detach`) or --allow-unlink.
        desired = dict(t)
        listed = {str(g["id"]): g for g in t.get("githubTeams", [])}
        rg = {str(g["id"]): g for g in r.get("githubTeams", [])}
        missing = [g for gid, g in rg.items() if gid not in listed]
        if missing and not args.allow_unlink:
            desired["githubTeams"] = list(t.get("githubTeams", [])) + missing
            for g in missing:
                notes.append(f"keep    {t['name']}: GitHub team '{g.get('name') or g['id']}' stays linked: its line is gone from team.md, "
                             f"but unlinking needs `(unlink)` on that line (teams.py detach) or --allow-unlink")
        # GitHub team member lists in team.md are for reference: edits there do nothing
        for gid, g in listed.items():
            if gid in rg and not g.get("unlink"):
                plus, minus = member_diff({"members": g.get("members", [])}, {"members": rg[gid].get("members", [])})
                if plus or minus:
                    notes.append(f"ignored {t['name']}: GitHub team '{g.get('name') or gid}' lists +{plus} -{minus} people that differ from GitHub. "
                                 f"Its members change in GitHub; to take them over here, run teams.py detach")
        added, removed = member_diff(desired, r)
        if added or removed:
            change["members"] = push_members(desired, where, errs)
            effects = []
            keep_ids = {str(x["id"]) for x in linked(desired)}
            dropped = [g.get("name") or gid for gid, g in rg.items() if gid not in keep_ids]
            added_links = [g.get("name") or str(g["id"]) for g in linked(desired) if str(g["id"]) not in rg]
            if dropped:
                effects.append("UNLINKS GitHub team " + ", ".join(f"'{d}'" for d in dropped) + ": its sync stops, only the listed Members stay")
            if added_links:
                effects.append("links GitHub team " + ", ".join(f"'{d}'" for d in added_links))
            before, after = membership(r), membership(desired)
            if before != after:
                effects.append(f"{before} -> {after}")
            elif not effects and after != "manual":
                effects.append(f"{after} team: GitHub links kept")
            notes.append(f"members {t['name']}: +{added} -{removed}" + (f" ({'; '.join(effects)})" if effects else ""))
        if len(change) > 1:
            plan["update"].append(change)

    for key, r in rt.items():
        if key in lt:
            continue
        if args.allow_delete:
            plan["delete"].append({"teamKey": key})
            notes.append(f"DELETE  {r.get('name')} ({key})")
        else:
            notes.append(f"skip    {r.get('name')} ({key}) is in Swarmia but not in company/teams/; not deleted without --allow-delete")

    if errs:
        print("\n".join("error: " + e for e in errs), file=sys.stderr)
        return 1
    if args.preview:
        print("\n".join(notes) if notes else "no changes")
        return 0
    print("\n".join(notes) if notes else "no changes: Swarmia already matches company/teams/", file=sys.stderr)
    print(json.dumps({k: v for k, v in plan.items() if v}, indent=2))
    return 0


ROLE_ATTR = "Swarmia role"
JOB_ATTR = "Swarmia job description"


def rows_of(data) -> list:
    """Rows from a saved EntityQuery response, a list of such responses (pages), or a plain list."""
    if isinstance(data, list):
        if data and isinstance(data[0], dict) and ("result" in data[0] or "rows" in data[0]):
            return [r for page in data for r in rows_of(page)]
        return data
    if "result" in data:
        return data["result"].get("rows", [])
    return data.get("rows", [])


def team_key_resolver(args, raw: dict):
    """Swarmia's internal team ID -> (team key, None) or (None, reason). Keys equal the ID unless the
    team has an external ID; then the team is matched by name through --team-ids."""
    keys = {t["teamKey"] for t in raw.get("teams", [])}
    by_name = {}
    for t in raw.get("teams", []):
        by_name.setdefault((t.get("name") or "").strip(), []).append(t["teamKey"])
    id_to_name = {r.get("id"): (r.get("name") or "").strip() for r in rows_of(load(args.team_ids))} if args.team_ids else {}

    def key_of(team_id):
        if team_id in keys:
            return team_id, None
        name = id_to_name.get(team_id)
        if len(by_name.get(name, [])) == 1:
            return by_name[name][0], None
        if not id_to_name:
            return None, "pass --team-ids to match teams whose key is not their ID"
        if team_id not in id_to_name:
            return None, "team id not in --team-ids"
        if name not in by_name:
            return None, f"team '{name}' is not in this pull"
        return None, f"several teams are named '{name}'"

    return key_of


# --- Team context pulled from Swarmia: main repositories, issue ownership, working agreements ---

REPOS_SECTION = "Main repositories"
OWNERSHIP_SECTION = "Issue ownership"
AGREEMENTS_SECTION = "Working agreements in Swarmia"
PULLED_SECTIONS = {REPOS_SECTION: "repositories", OWNERSHIP_SECTION: "issueOwnership", AGREEMENTS_SECTION: "workingAgreements"}
MAX_REPOS = 5
MIN_REPO_SHARE = 0.05  # a repository is "main" when it holds at least this share of the team's merged PRs


def duration(seconds: float) -> str:
    seconds = float(seconds)
    if seconds >= 86400 and seconds % 86400 == 0:
        n = int(seconds // 86400)
        return f"{n} day" + ("" if n == 1 else "s")
    if seconds >= 3600:
        n = round(seconds / 3600, 1)
        n = int(n) if n == int(n) else n
        return f"{n} hour" + ("" if n == 1 else "s")
    return f"{int(seconds // 60)} minutes"


def issues_of(cfg: dict) -> str:
    t = cfg.get("issueType")
    return f"{t} issues" if t else "issues"


AGREEMENT_TEXT = {
    "max_pull_request_review_time": lambda c: f"Review pull requests within {duration(c.get('maxAgeInMs', 0) / 1000)}",
    "max_pull_request_age": lambda c: f"Merge or close pull requests within {duration(int(c.get('maxAgeInDays', 0)) * 86400)}",
    "wip_pull_requests": lambda c: f"At most {c.get('maxPullRequests')} open pull requests at a time",
    "batch_size": lambda c: f"Keep pull requests under {c.get('threshold')} changed lines",
    "pull_request_linking": lambda c: "Link pull requests to issues",
    "no_direct_pushes_to_main_branch": lambda c: "No direct pushes to the main branch",
    "wip_issues": lambda c: f"At most {c.get('maxIssues')} {issues_of(c)} in progress at a time",
    "max_issue_age": lambda c: f"Finish {issues_of(c)} within {duration(c.get('maxAgeInSeconds', 0))}",
    "min_issue_contributors": lambda c: f"Avoid working alone on {issues_of(c)}",
}


def agreement_text(kind: str, cfg) -> str:
    cfg = cfg if isinstance(cfg, dict) else {}
    try:
        text = AGREEMENT_TEXT[kind](cfg)
    except (KeyError, TypeError, ValueError):
        text = kind.replace("_", " ").capitalize() + (f" {json.dumps(cfg, sort_keys=True)}" if cfg else "")
    return f"{text} `{kind}`"


def pulled_agreements(args, key_of) -> tuple:
    """Working agreements per team key, from a saved EntityQuery on WorkingAgreement (type, config, teamIds)."""
    out, unresolved = {}, []
    for r in rows_of(load(args.agreements)):
        for team_id in r.get("teamIds") or []:  # agreements of deleted teams have no team and are skipped
            key, why = key_of(team_id)
            if key is None:
                unresolved.append(f"working agreement {r.get('type')} on team {team_id}: {why}")
                continue
            out.setdefault(key, []).append(agreement_text(r.get("type") or "", r.get("config")))
    return {k: sorted(set(v)) for k, v in out.items()}, unresolved


def pulled_repositories(args, key_of) -> tuple:
    """Main repositories per team key from merged PRs grouped by [ownerTeamIds, repositoryId] (rows: _key, mergedPrs)
    and a Repository query (id, fullName)."""
    names = {}
    if args.repo_names:
        names = {r.get("id"): r.get("fullName") or r.get("name") for r in rows_of(load(args.repo_names))}
    counts, unresolved = {}, set()
    for r in rows_of(load(args.repos)):
        k = r.get("_key") or [r.get("ownerTeamIds"), r.get("repositoryId")]
        team_id, repo_id = (k[0], k[1]) if isinstance(k, list) and len(k) == 2 else (None, None)
        if not team_id or not repo_id:
            continue
        key, why = key_of(team_id)
        if key is None:
            unresolved.add(f"repositories of team {team_id}: {why}")
            continue
        repo = names.get(repo_id) or repo_id
        counts.setdefault(key, Counter())[repo] += int(r.get("mergedPrs") or r.get("count") or 0)
    window = args.repos_window
    out = {}
    for key, c in counts.items():
        total = sum(c.values())
        top = [(repo, n) for repo, n in c.most_common(MAX_REPOS) if total and n / total >= MIN_REPO_SHARE]
        out[key] = [f"{repo}: {n} merged PRs ({round(100 * n / total)}%{', ' + window if window else ''})" for repo, n in top]
    return out, sorted(unresolved)


OPERATOR_TEXT = {"in": "is", "notIn": "is not", "equals": "is", "notEquals": "is not", "startsWith": "starts with",
                 "endsWith": "ends with", "contains": "contains", "notContains": "does not contain"}


def words(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", " ", name or "").lower()


def condition_text(c: dict, refs: dict) -> str:
    """One ownership filter condition as text. Projects, tracker teams and repositories use the names Swarmia
    resolved; any other condition (title, labels, custom fields…) is written out from the filter itself."""
    kind = c.get("type")
    if kind in ("And", "Or"):
        parts = [condition_text(x, refs) for x in c.get("conditions") or []]
        return parts[0] if len(parts) == 1 else "(" + f" {kind.lower()} ".join(parts) + ")"
    if kind == "Not":
        inner = c.get("condition") or (c.get("conditions") or [{}])[0]
        return f"not {condition_text(inner, refs)}"
    if kind in refs:
        ids = c.get("in") or c.get("notIn") or []
        names = ", ".join(refs[kind].get(i, f"{i} (name not resolved)") for i in ids)
        label = {"AssigneeAuthor": "assignee ", "Author": "author "}.get(kind, "")
        return label + ("not " if "notIn" in c and "in" not in c else "") + names
    ops = [f"{OPERATOR_TEXT.get(k, words(k))} {', '.join(map(str, v)) if isinstance(v, list) else json.dumps(v) if isinstance(v, str) else v}"
           for k, v in c.items() if k != "type"]
    return " ".join([words(kind) or "condition"] + ops)


def ownership_lines(data: dict, people: dict = None) -> list:
    """Readable lines for one team's issueOwnership settings (GetSettings, scope team).
    people maps Swarmia author IDs to names, for filters on assignee or author."""
    lines = []
    for m in data.get("mappings") or []:
        named = {i: f"{n} <swarmia:{i}>" for i, n in (people or {}).items()}
        refs = {"Project": {}, "SourceTeam": {}, "Repository": {}, "AssigneeAuthor": named, "Author": named}
        for p in m.get("projects") or []:
            label = " ".join(x for x in [p.get("source"), "project", p.get("key")] if x)
            refs["Project"][p.get("id")] = f"{label} ({p.get('name')})" if p.get("name") else label
        for s in m.get("sourceTeams") or []:
            label = " ".join(x for x in [s.get("source"), "team", s.get("name") or "(name not resolved)"] if x)
            refs["SourceTeam"][s.get("id")] = label + (" (cycles on)" if s.get("cyclesEnabled") else "")
        for r in m.get("repositories") or []:
            refs["Repository"][r.get("id")] = f"repository {r.get('fullName') or r.get('name') or r.get('id')}"
        cond = (m.get("filter") or {}).get("condition") or {}
        kids = cond.get("conditions") or []
        if cond.get("type") in ("Or", "And") and len(kids) > 1:
            lines.append(f"Issues matching {'any' if cond['type'] == 'Or' else 'all'} of:")
            lines += [f"  {condition_text(k, refs)}" for k in kids]
        elif cond:
            lines.append(condition_text(cond, refs))
    board = data.get("sprintBoard")
    if board:
        if isinstance(board, dict):
            kind = {"kanban": "Jira kanban board", "scrum": "Jira sprint board", "simple": "Jira board"}.get(board.get("type"), "Jira board")
            lines.append(f"{kind}: {board.get('name')}")
        else:
            lines.append(f"Jira board: {board}")
    if not lines:
        lines.append("Combines the issues of its sub-teams" if data.get("writeBlockReason") == "parentTeam" else "No issue ownership set in Swarmia")
    return lines


def pulled_ownership(args, key_of) -> tuple:
    """Issue ownership per team key from saved GetSettings responses (scope team, section issueOwnership)."""
    out, unresolved = {}, []
    for path in args.ownership:
        resp = load(path)
        for r in resp if isinstance(resp, list) else [resp]:
            team_id = (r.get("team") or {}).get("id")
            section = (r.get("sections") or {}).get("issueOwnership") or {}
            if not team_id or "data" not in section:
                unresolved.append(f"{path}: not a team issueOwnership settings response")
                continue
            key, why = key_of(team_id)
            if key is None:
                unresolved.append(f"issue ownership of team {team_id}: {why}")
                continue
            lines = ownership_lines(section["data"], getattr(args, "author_names", None))
            if section.get("settingsUrl"):
                lines.append(f"Settings: {section['settingsUrl']}")
            out[key] = lines
    return out, unresolved


def swarmia_people(args, raw: dict) -> tuple:
    """Per-author Swarmia attributes (role, job description, custom attributes) and team admins per team key."""
    attrs = {}

    def put(author_id, name, value):
        if author_id and value not in (None, ""):
            attrs.setdefault(author_id, {})[name] = value

    users = []
    if args.users:
        for u in rows_of(load(args.users)):
            for aid in u.get("authorIds") or []:
                put(aid, ROLE_ATTR, u.get("role"))
                put(aid, JOB_ATTR, u.get("jobDescription"))
            aid = (u.get("authorIds") or [None])[0]
            person = {"name": (u.get("name") or "").strip(), "email": u.get("email") or "", "swarmiaAuthorId": aid or ""}
            person = {k: v for k, v in person.items() if v}
            if person.get("email") or person.get("swarmiaAuthorId"):
                users.append(person)
    if args.attributes:
        exclude = {a.strip().lower() for a in (args.exclude_attributes or "").split(",") if a.strip()}
        for path in args.attributes:
            for v in rows_of(load(path)):
                for name in v.get("attributeNames") or []:
                    if name.lower() in exclude:
                        continue
                    for aid in v.get("authorIds") or []:
                        put(aid, name, v.get("value"))

    admins, unresolved = {}, []
    if args.roles:
        key_of = team_key_resolver(args, raw)
        people = {}
        for t in raw.get("teams", []):
            for a in t.get("authors", []) + [m for g in t.get("githubTeams", []) for m in g.get("members", [])]:
                people.setdefault(a.get("authorId"), (a.get("name") or "").strip())
        for r in rows_of(load(args.roles)):
            for team_id in r.get("teamIds") or []:
                key, why = key_of(team_id)
                for aid in r.get("authorIds") or []:
                    if key is None:
                        unresolved.append(f"{r.get('role')} on team {team_id}: {why}")
                        continue
                    entry = {"name": people.get(aid, ""), "swarmiaAuthorId": aid, "role": r.get("role")}
                    admins.setdefault(key, []).append({k: v for k, v in entry.items() if v})
    return attrs, admins, unresolved, users


def cmd_from_swarmia(args) -> int:
    """Convert ListTeamsAndMembers output to a model, keeping local fields from --merge (folder or model)."""
    import datetime

    if args.inputs:
        fill_inputs(args)
        args.raw = args.raw or str(Path(args.inputs) / "teams-raw.json")
    if not args.raw:
        raise SystemExit("from-swarmia needs the ListTeamsAndMembers response (RAW) or --inputs DIR")
    raw = load(args.raw)
    old = load(args.merge) if args.merge else {}
    old_teams = {t["key"]: t for t in old.get("teams", [])}
    attrs_by_person = {}
    for t in old.get("teams", []) + [{"members": old.get("people", [])}]:
        for m in people_of(t):
            if m.get("attributes"):
                for i in identities(m):
                    attrs_by_person.setdefault(i, m["attributes"])

    swarmia_attrs, team_admins, unresolved, swarmia_users = swarmia_people(args, raw)
    declared = dict(old.get("attributes", {}) or {})
    sources = dict(old.get("attributeSources", {}) or {})
    for name in sorted({k for v in swarmia_attrs.values() for k in v}):
        declared.setdefault(name, None)
        sources[name] = "swarmia"

    def person(a: dict) -> dict:
        m = {"name": (a.get("name") or "").strip(), "email": a.get("email") or "", "swarmiaAuthorId": a.get("authorId") or ""}
        m = {k: v for k, v in m.items() if v}
        local = next((attrs_by_person[i] for i in identities(m) if i in attrs_by_person), {})
        merged = {k: v for k, v in local.items() if sources.get(k) != "swarmia"}  # Swarmia owns its attributes
        merged.update(swarmia_attrs.get(m.get("swarmiaAuthorId"), {}))
        if merged:
            m["attributes"] = dict(sorted(merged.items()))
        return m

    # Team context: refreshed when its input is passed, otherwise kept from --merge
    context = {}
    if args.repos or args.agreements or args.ownership:
        key_of = team_key_resolver(args, raw)
        args.author_names = {a.get("authorId"): (a.get("name") or "").strip() for t in raw.get("teams", [])
                             for a in t.get("authors", []) + [m for g in t.get("githubTeams", []) for m in g.get("members", [])]}
        for field, flag, fn in [("repositories", args.repos, pulled_repositories), ("workingAgreements", args.agreements, pulled_agreements), ("issueOwnership", args.ownership, pulled_ownership)]:
            if flag:
                context[field], miss = fn(args, key_of)
                unresolved += miss

    teams = []
    for r in raw.get("teams", []):
        key = r["teamKey"]
        prev = old_teams.get(key, {})
        pulled = {f: (context[f].get(key, []) if f in context else prev.get(f, [])) for f in PULLED_SECTIONS.values()}
        teams.append(
            {
                "key": key,
                "name": (r.get("name") or "").strip(),
                "parent": r.get("parentTeamKey"),
                "mission": prev.get("mission", ""),
                "owns": prev.get("owns", []),
                "githubTeams": [
                    {
                        "id": g["githubTeamId"],
                        "name": g.get("name", ""),
                        "memberCount": len(g.get("members", [])),
                        "members": [person(a) for a in g.get("members", [])],
                    }
                    for g in r.get("githubTeams", [])
                ],
                "members": [person(a) for a in r.get("authors", [])],
                "admins": team_admins.get(key, []),
                **{f: v for f, v in pulled.items() if v},
                **({"path": prev["path"]} if prev.get("path") else {}),
                **({"extra": prev["extra"]} if prev.get("extra") else {}),
            }
        )
    # people.md lists every Swarmia user (on a team or not), everyone on a team, and people added by hand
    people = [person({"authorId": u.get("swarmiaAuthorId"), "name": u.get("name"), "email": u.get("email")}) for u in swarmia_users]
    people += [person({"authorId": m.get("swarmiaAuthorId"), "name": m.get("name"), "email": m.get("email")}) for m in old.get("people", [])]
    people = merge_people(people)  # a merged folder lists the Swarmia users again: keep each person once, Swarmia's row first
    keys = {t["key"] for t in teams}
    local_only = [t for k, t in old_teams.items() if k not in keys]
    if local_only and not args.drop_local:
        teams += local_only
        for t in local_only:
            print(f"kept local-only team '{t['name']}' ({t['key']}): it will be created on the next push unless removed", file=sys.stderr)
    status = old.get("status", "draft")
    out = {
        "$comment": "Team roster, may hold personal data: keep this repository private. Never copied into installed skills. Format: company/teams/README.md.",
        "status": "draft" if status == "template" else status,
        "owner": old.get("owner", ""),
        "last_reviewed": old.get("last_reviewed", ""),
        "source": "swarmia",
        "pulled_at": datetime.date.today().isoformat(),
        "attributes": declared,
        "attributeSources": sources,
        "people": people,
        "teams": sorted(teams, key=lambda t: t["name"].lower()),
    }
    for u in unresolved:
        print(f"could not place: {u}", file=sys.stderr)
    Path(args.out).write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    bots = sum(1 for t in teams for m in people_of(t) if is_bot(m))
    print(f"wrote {args.out}: {len(teams)} teams, {len(unique_people([m for t in teams for m in people_of(t)]))} people" + (f", {bots} bot memberships" if bots else ""), file=sys.stderr)
    return 0


# ---------------------------------------------------------------------------
# Folder format: company/teams/
#   people.md                 frontmatter (status, owner, last_reviewed, source, pulled_at),
#                             an Attributes table and a People table (everyone once)
#   <team>/team.md            frontmatter (key, name, any extra keys) and sections:
#                             Mission, Owns, Members, GitHub teams, Team admins, plus any of your own
#   <team>/<sub-team>/team.md sub-teams are sub-folders
# ---------------------------------------------------------------------------

TEAM_FILE = "team.md"
PEOPLE_FILE = "people.md"
KNOWN_SECTIONS = ["Mission", "Owns", "Members", "GitHub teams", "Team admins"] + list(PULLED_SECTIONS)
SECTION_NOTES = {
    REPOS_SECTION: "Pulled from Swarmia: repositories holding most of the pull requests this team owns. Refreshed on every pull; list what the team is responsible for under Owns.",
    OWNERSHIP_SECTION: "Pulled from Swarmia: which issues this team owns (projects, tracker teams, boards). Change it in Swarmia's team settings.",
    AGREEMENTS_SECTION: "Pulled from Swarmia: working agreements the team has set up there. Change them in Swarmia; write your own agreements in a section of your own.",
}


def nested_bullets(text: str) -> list:
    """Bullets with one level of nesting kept as two leading spaces: ['Issues matching any of:', '  Jira project GRO']."""
    out = []
    for line in COMMENT_RE.sub("", text).splitlines():
        m = re.match(r"^(\s*)[-*]\s+(.*\S)\s*$", line)
        if m:
            out.append(("  " if m.group(1) else "") + m.group(2))
    return out
FIXED_COLUMNS = ["Name", "Email", "Swarmia ID"]
COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
MEMBER_RE = re.compile(r"^[-*]\s+(.+?)(?:\s+<([^>]+)>)?\s*$")
GH_RE = re.compile(r"^[-*]\s+(.+?)\s+`([^`]+)`(\s+\(unlink\))?\s*$")
ADMIN_RE = re.compile(r"^[-*]\s+(.+?)(?:\s+<([^>]+)>)?\s+\(([^)]+)\)\s*$")


def split_frontmatter(text: str) -> tuple:
    if not text.startswith("---\n"):
        return {}, [], text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, [], text
    fm, order = {}, []
    for line in text[4:end].splitlines():
        if ":" in line and not line.startswith(" "):
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip()
            order.append(k.strip())
    return fm, order, text[end + 5 :]


def sections(body: str) -> list:
    """[(title, text)] for each '## ' section; text before the first section is dropped (it is the H1)."""
    out, title, buf = [], None, []
    for line in body.splitlines():
        if line.startswith("## "):
            if title is not None:
                out.append((title, "\n".join(buf).strip("\n")))
            title, buf = line[3:].strip(), []
        elif title is not None:
            buf.append(line)
    if title is not None:
        out.append((title, "\n".join(buf).strip("\n")))
    return out


def bullets(text: str) -> list:
    return [l.rstrip() for l in COMMENT_RE.sub("", text).splitlines() if l.lstrip().startswith(("- ", "* "))]


def cells(line: str) -> list:
    parts = re.split(r"(?<!\\)\|", line.strip().strip("|"))
    return [c.strip().replace("\\|", "|") for c in parts]


def table(text: str) -> list:
    rows = [l for l in text.splitlines() if l.strip().startswith("|")]
    if len(rows) < 2:
        return []
    head = cells(rows[0])
    return [dict(zip(head, cells(r))) for r in rows[2:] if any(c for c in cells(r))]


def esc(v) -> str:
    return str(v if v is not None else "").replace("|", "\\|").replace("\n", " ")


def slug(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return (s or "team")[:60].rstrip("-")


def read_folder(root: str) -> dict:
    root = Path(root)
    fm, _, body = split_frontmatter((root / PEOPLE_FILE).read_text(encoding="utf-8")) if (root / PEOPLE_FILE).exists() else ({}, [], "")
    secs = dict(sections(body))
    declared, sources = {}, {}
    for r in table(secs.get("Attributes", "")):
        name = r.get("Attribute", "")
        if name:
            allowed = [v.strip() for v in r.get("Allowed values", "").split(",") if v.strip()]
            declared[name] = allowed or None
            if r.get("Source", "").lower() == "swarmia":
                sources[name] = "swarmia"
    people, errs = [], []
    for r in table(secs.get("People", "")):
        m = {"name": r.get("Name", ""), "email": r.get("Email", ""), "swarmiaAuthorId": r.get("Swarmia ID", "")}
        m = {k: v for k, v in m.items() if v}
        attrs = {k: v for k, v in r.items() if k not in FIXED_COLUMNS and v}
        if attrs:
            m["attributes"] = attrs
        people.append(m)
    by_email = {m["email"].lower(): m for m in people if m.get("email")}
    by_id = {m["swarmiaAuthorId"]: m for m in people if m.get("swarmiaAuthorId")}

    def resolve(name, key, where):
        """People are linked by email (Name <email>) or Swarmia ID (Name <swarmia:ID>), never by name."""
        if not key:
            errs.append(f"{where}: '{name}' has no email; write it as 'Name <email>' (names are not unique)")
            return {"name": name}
        if key.lower().startswith("swarmia:"):
            hit = by_id.get(key.split(":", 1)[1].strip())
            if hit:
                return hit
            errs.append(f"{where}: '{name} <{key}>' is not in people.md; add a row with that Swarmia ID")
            return {"name": name, "swarmiaAuthorId": key.split(":", 1)[1].strip()}
        hit = by_email.get(key.lower())
        if hit:
            return hit
        errs.append(f"{where}: '{name} <{key}>' is not in people.md; add a row with that email")
        return {"name": name, "email": key}

    teams = []
    for f in sorted(root.rglob(TEAM_FILE)):
        rel = f.parent.relative_to(root)
        tfm, order, tbody = split_frontmatter(f.read_text(encoding="utf-8"))
        where = str(Path("company/teams") / rel / TEAM_FILE)
        parent_file = f.parent.parent / TEAM_FILE
        parent_key = None
        if f.parent.parent != root:
            if parent_file.exists():
                parent_key = split_frontmatter(parent_file.read_text(encoding="utf-8"))[0].get("key")
            else:
                errs.append(f"{where}: its parent folder has no {TEAM_FILE}")
        tsecs = sections(tbody)
        known = dict(tsecs)
        team = {
            "key": tfm.get("key", ""),
            "name": tfm.get("name", ""),
            "parent": parent_key,
            "path": str(rel),
            "mission": " ".join(l.strip() for l in COMMENT_RE.sub("", known.get("Mission", "")).splitlines() if l.strip()),
            "owns": [b.lstrip("-* ").strip() for b in bullets(known.get("Owns", ""))],
            "members": [],
            "githubTeams": [],
            "admins": [],
            "extra": {
                "frontmatter": {k: tfm[k] for k in order if k not in ("key", "name", "membership")},
                "sections": [[s, txt] for s, txt in tsecs if s not in KNOWN_SECTIONS],
            },
        }
        for b in bullets(known.get("Members", "")):
            mm = MEMBER_RE.match(b.strip())
            if mm:
                team["members"].append(resolve(mm.group(1), mm.group(2), where))
        current = None
        for line in COMMENT_RE.sub("", known.get("GitHub teams", "")).splitlines():
            if not line.strip():
                continue
            if not line.startswith((" ", "\t")):
                g = GH_RE.match(line.strip())
                if g:
                    current = {"id": g.group(2), "name": g.group(1), "members": [], **({"unlink": True} if g.group(3) else {})}
                    team["githubTeams"].append(current)
            elif current is not None:
                mm = MEMBER_RE.match(line.strip())
                if mm:
                    current["members"].append(resolve(mm.group(1), mm.group(2), where))
        for g in team["githubTeams"]:
            g["memberCount"] = len(g["members"])
        for title, field in PULLED_SECTIONS.items():
            lines = nested_bullets(known.get(title, ""))
            if lines:
                team[field] = lines
        for b in bullets(known.get("Team admins", "")):
            a = ADMIN_RE.match(b.strip())
            if a:
                p = resolve(a.group(1), a.group(2), where)
                entry = {"name": p.get("name"), "swarmiaAuthorId": p.get("swarmiaAuthorId"), "role": a.group(3)}
                team["admins"].append({k: v for k, v in entry.items() if v})
        teams.append(team)
    return {
        "status": fm.get("status", "template"),
        "owner": fm.get("owner", ""),
        "last_reviewed": fm.get("last_reviewed", ""),
        "source": fm.get("source", ""),
        "pulled_at": fm.get("pulled_at", ""),
        "attributes": declared,
        "attributeSources": sources,
        "people": people,
        "teams": teams,
        "folderErrors": errs,
    }


def all_people(model: dict) -> list:
    """Everyone in the model once (people table, team members, GitHub team members, admins)."""
    pool = list(model.get("people", []))
    for t in model.get("teams", []):
        pool += people_of(t)
    return sorted(merge_people(pool), key=lambda m: m.get("name", "").lower())


def merge_people(pool: list) -> list:
    """People once each, matched on Swarmia ID or email, in first-seen order. Earlier rows win;
    later rows only fill fields and attributes the earlier one lacks."""
    out, seen = [], []
    for m in pool:
        ids = identities(m)
        hit = next((i for i, s in enumerate(seen) if s & ids), None)
        if hit is None:
            seen.append(set(ids))
            out.append(dict(m))
        else:
            seen[hit] |= ids
            for k, v in m.items():
                if k == "attributes":
                    out[hit].setdefault("attributes", {}).update({a: b for a, b in v.items() if a not in out[hit].get("attributes", {})})
                else:
                    out[hit].setdefault(k, v)
    return out


def write_folder(model: dict, root: str) -> list:
    """Write the model as people.md plus one folder per team. Keeps folder names, extra frontmatter
    and extra sections of teams already there. Returns notes about moved and removed teams."""
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    prev = read_folder(root) if (root / PEOPLE_FILE).exists() or any(root.rglob(TEAM_FILE)) else {"teams": []}
    prev_by_key = {t["key"]: t for t in prev["teams"]}
    teams = model.get("teams", [])
    by_key = {t["key"]: t for t in teams}
    people = all_people(model)
    canonical = {}
    for person in people:
        for i in identities(person):
            canonical[i] = person

    def ref(m):
        m = next((canonical[i] for i in identities(m) if i in canonical), m)  # use the people.md row's email
        if m.get("email"):
            return f"{m.get('name', '')} <{m['email']}>"
        if m.get("swarmiaAuthorId"):
            return f"{m.get('name', '')} <swarmia:{m['swarmiaAuthorId']}>"
        return m.get("name", "")

    # people.md
    declared = model.get("attributes", {}) or {}
    sources = model.get("attributeSources", {}) or {}
    ordered = sorted(declared, key=lambda a: (sources.get(a) != "swarmia" or a.startswith("Swarmia "), a.lower()))
    cols = ["Name", "Email"] + ordered + ["Swarmia ID"]
    lines = [
        "---",
        "title: People",
        f"status: {model.get('status', 'draft')}",
        f"owner: {model.get('owner', '')}",
        f"last_reviewed: {model.get('last_reviewed', '')}",
        f"source: {model.get('source', '')}",
        f"pulled_at: {model.get('pulled_at', '')}",
        "---",
        "",
        "# People",
        "",
        "Every Swarmia user (on a team or not), everyone on a team, and anyone added by hand, once each. Team files link to people by email, written `Name <email>` "
        "(or `Name <swarmia:ID>` for someone without an email); the name is only for reading. Add a row here before adding someone to a team. "
        "Format and privacy rules: [README.md](README.md).",
        "",
        "## Attributes",
        "",
        "Columns with source `swarmia` are refreshed on every pull from Swarmia: change them in Swarmia. "
        "Columns with source `local` are yours. Allowed values, comma-separated, are checked; leave empty for free text.",
        "",
        "| Attribute | Source | Allowed values |",
        "|---|---|---|",
    ] + [f"| {esc(a)} | {sources.get(a, 'local')} | {esc(', '.join(declared[a] or []))} |" for a in declared] + [
        "",
        "## People",
        "",
        "| " + " | ".join(cols) + " |",
        "|" + "---|" * len(cols),
    ]
    for m in people:
        row = [m.get("name", ""), m.get("email", "")] + [(m.get("attributes") or {}).get(a, "") for a in ordered] + [m.get("swarmiaAuthorId", "")]
        lines.append("| " + " | ".join(esc(c) for c in row) + " |")
    (root / PEOPLE_FILE).write_text("\n".join(lines) + "\n", encoding="utf-8")

    # team folders
    paths = {}

    def path_of(key, stack=()):
        if key in paths:
            return paths[key]
        t = by_key[key]
        parent = t.get("parent")
        base = Path(path_of(parent, stack + (key,))) if parent in by_key and parent not in stack else Path()
        old = prev_by_key.get(key, {}).get("path") or t.get("path")
        name = Path(old).name if old else slug(t["name"])
        taken = {Path(p).name for k, p in paths.items() if Path(p).parent == base}
        candidate, n = name, 2
        while candidate in taken:
            candidate, n = f"{name}-{n}", n + 1
        paths[key] = str(base / candidate)
        return paths[key]

    for t in sorted(teams, key=lambda x: x["name"].lower()):
        path_of(t["key"])

    notes = []
    for t in teams:
        old = prev_by_key.get(t["key"], {})
        extra = t.get("extra") or old.get("extra") or {"frontmatter": {}, "sections": []}
        fm = ["---", f"key: {t['key']}", f"name: {t['name']}", f"membership: {membership(t)}  # {MEMBERSHIP_NOTE[membership(t)]}"]
        fm += [f"{k}: {v}" for k, v in extra.get("frontmatter", {}).items() if k != "membership"] + ["---"]
        body = [
            "",
            f"# {t['name']}",
            "",
            "## Mission",
            "",
            t.get("mission") or "<!-- One or two sentences: why this team exists and what outcome it owns. -->",
            "",
            "## Owns",
            "",
        ]
        body += [f"- {o}" for o in t.get("owns", [])] or ["<!-- Products, services, repositories or areas, one per line: - checkout-service -->"]
        body += ["", "## Members", "", "<!-- People directly on this team, one per line: Name <email>, matching a row in people.md (top of company/teams/). -->", ""]
        body += [f"- {ref(m)}" for m in t.get("members", [])]
        body += ["", "## GitHub teams", "", "<!-- Linked GitHub teams, kept in sync by Swarmia. Members are listed for reference: change them in GitHub. To cut a sync and manage its people here, run teams.py detach (adds ' (unlink)'). -->", ""]
        for g in t.get("githubTeams", []):
            body.append(f"- {g.get('name') or g['id']} `{g['id']}`" + (" (unlink)" if g.get("unlink") else ""))
            body += [f"  - {ref(m)}" for m in g.get("members", [])]
        body += ["", "## Team admins", "", "<!-- Pulled from Swarmia; change team admins in Swarmia. -->", ""]
        body += [f"- {ref(a)} ({a.get('role', 'TeamAdmin')})" for a in t.get("admins", [])]
        for title, field in PULLED_SECTIONS.items():
            body += ["", f"## {title}", "", f"<!-- {SECTION_NOTES[title]} -->", ""]
            body += [f"  - {l.strip()}" if l.startswith("  ") else f"- {l}" for l in t.get(field, [])]
        for title, text in extra.get("sections", []):
            body += ["", f"## {title}", "", text]
        target = root / paths[t["key"]] / TEAM_FILE
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("\n".join(fm + body).rstrip() + "\n", encoding="utf-8")
        if old.get("path") and old["path"] != paths[t["key"]]:
            notes.append(f"moved   {t['name']}: {old['path']} -> {paths[t['key']]}")

    wanted = {str(root / p / TEAM_FILE) for p in paths.values()}
    for f in sorted(root.rglob(TEAM_FILE), key=lambda p: len(p.parts), reverse=True):
        if str(f) not in wanted:
            f.unlink()
            notes.append(f"removed {f.parent.relative_to(root)}")
    for d in sorted((p for p in root.rglob("*") if p.is_dir()), key=lambda p: len(p.parts), reverse=True):
        if not any(d.iterdir()):
            d.rmdir()
        elif not (d / TEAM_FILE).exists():
            notes.append(f"kept    {d.relative_to(root)}: holds other files but no team")
    return notes


def cmd_detach(args) -> int:
    """Cut a team's GitHub sync in the folder: copy the GitHub team's people into Members and mark the GitHub
    team `(unlink)`. Edit Members afterwards (replace people), then push: the sync stops in Swarmia and the
    team keeps exactly the people listed under Members."""
    model = read_folder(args.folder)
    want = args.team.strip().lower()
    hits = [t for t in model["teams"] if want in (t["key"].lower(), t["name"].strip().lower())]
    if len(hits) != 1:
        print(f"error: {'no team' if not hits else 'several teams'} match '{args.team}' (use the key)", file=sys.stderr)
        return 1
    t = hits[0]
    pick = (args.github_team or "").strip().lower()
    chosen = [g for g in linked(t) if not pick or pick in (str(g["id"]).lower(), (g.get("name") or "").lower())]
    if not chosen:
        print(f"error: team '{t['name']}' has no linked GitHub team" + (f" matching '{args.github_team}'" if pick else ""), file=sys.stderr)
        return 1
    have = [identities(m) for m in t["members"]]
    copied = 0
    for g in chosen:
        for m in g.get("members", []):
            if not any(identities(m) & h for h in have):
                t["members"].append(m)
                have.append(identities(m))
                copied += 1
        g["unlink"] = True
    errs = problems(model)
    if errs:
        print("\n".join("error: " + e for e in errs), file=sys.stderr)
        return 1
    write_folder(model, args.folder)
    names = ", ".join(f"'{g.get('name') or g['id']}'" for g in chosen)
    print(f"{t['name']}: marked GitHub team {names} (unlink) and copied {copied} of its people into Members. "
          f"Edit Members as needed; the next push unlinks the sync and keeps exactly those people.", file=sys.stderr)
    return 0


def cmd_write(args) -> int:
    model = load(args.model)
    errs = [e for e in problems(model)]
    if errs:
        print("\n".join("error: " + e for e in errs), file=sys.stderr)
        return 1
    for n in write_folder(model, args.folder):
        print(n, file=sys.stderr)
    print(f"wrote {args.folder}: {len(model.get('teams', []))} teams, {len(all_people(model))} people")
    return 0


def cmd_read(args) -> int:
    model = read_folder(args.folder)
    Path(args.out).write_text(json.dumps(model, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


# ---------------------------------------------------------------------------
# Getting Swarmia responses into files without re-typing them.
# Both commands write the same input files, which `from-swarmia --inputs DIR` reads:
#   teams-raw.json users.json roles.json team-ids.json attributes-1.json
#   repos.json repo-names.json agreements.json ownership-<team id>.json
# ---------------------------------------------------------------------------

INPUT_FILES = {"users": "users.json", "roles": "roles.json", "team_ids": "team-ids.json", "repos": "repos.json",
               "repo_names": "repo-names.json", "agreements": "agreements.json"}
ENTITY_FILES = {"User": "users.json", "UserRoleAssignment": "roles.json", "Team": "team-ids.json", "AuthorAttributeValue": "attributes-1.json",
                "PullRequest": "repos.json", "Repository": "repo-names.json", "WorkingAgreement": "agreements.json"}
SAVED_RE = re.compile(r"(?:saved to|Output has been saved to)\s+(\S+?\.(?:txt|json))", re.I)


def default_transcript() -> Path:
    """The newest Claude Code transcript for the current directory (~/.claude/projects/<cwd with non-alphanumerics as ->/)."""
    folder = Path.home() / ".claude" / "projects" / re.sub(r"[^A-Za-z0-9]", "-", str(Path.cwd()))
    found = sorted(folder.glob("*.jsonl"), key=lambda p: p.stat().st_mtime)
    if not found:
        raise SystemExit(f"no Claude Code transcript in {folder}; pass --transcript")
    return found[-1]


def tool_text(content) -> str:
    if isinstance(content, list):
        return "".join(c.get("text", "") for c in content if isinstance(c, dict))
    return content if isinstance(content, str) else ""


def tool_json(text: str):
    """A tool result as JSON: inline, or from the file the client saved an oversized result to. None for errors."""
    text = (text or "").strip()
    if text.startswith(("{", "[")):
        try:
            return json.loads(text)
        except ValueError:
            return None
    m = SAVED_RE.search(text)
    if m and Path(m.group(1)).exists():
        try:
            return json.loads(Path(m.group(1)).read_text(encoding="utf-8"))
        except ValueError:
            return None
    return None


def row_key(r: dict):
    k = r.get("_key", r.get("id"))
    return tuple(k) if isinstance(k, list) else k if k is not None else json.dumps(r, sort_keys=True)


def cmd_extract(args) -> int:
    """Write the Swarmia responses of a Claude Code session to input files, unchanged."""
    path = Path(args.transcript) if args.transcript else default_transcript()
    calls, results = {}, []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            rec = json.loads(line)
        except ValueError:
            continue
        for c in (rec.get("message") or {}).get("content") or []:
            if not isinstance(c, dict):
                continue
            if c.get("type") == "tool_use":
                calls[c.get("id")] = c
            elif c.get("type") == "tool_result" and c.get("tool_use_id") in calls:
                results.append((calls[c["tool_use_id"]], tool_text(c.get("content"))))
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    rows, teams_raw, ownership, skipped = {}, None, {}, Counter()
    for call, text in results:  # in transcript order: a later response wins
        tool = call.get("name", "").split("__")[-1]
        data = tool_json(text)
        if data is None:
            if tool in ("ListTeamsAndMembers", "EntityQuery", "GetSettings"):
                skipped[tool] += 1
            continue
        if tool == "ListTeamsAndMembers" and isinstance(data, dict) and "teams" in data:
            teams_raw = data
        elif tool == "EntityQuery":
            query = (call.get("input") or {}).get("query") or {}
            if isinstance(query, str):
                try:
                    query = json.loads(query)
                except ValueError:
                    query = {}
            name = ENTITY_FILES.get(query.get("entity"))
            if name == "repos.json" and query.get("groupBy") != ["ownerTeamIds", "repositoryId"]:
                name = None
            if name:
                # only the latest run of a query counts: a different query (pages aside) starts over
                sig = json.dumps({k: v for k, v in query.items() if k not in ("offset", "limit")}, sort_keys=True)
                run = rows.get(name)
                if run is None or run["sig"] != sig:
                    run = rows[name] = {"sig": sig, "pages": {}}
                run["pages"][query.get("offset") or 0] = rows_of(data)
        elif tool == "GetSettings" and isinstance(data, dict) and "issueOwnership" in (data.get("sections") or {}):
            team_id = (data.get("team") or {}).get("id")
            if team_id:
                ownership[team_id] = data
    written = []
    if teams_raw:
        (out / "teams-raw.json").write_text(json.dumps(teams_raw, ensure_ascii=False, indent=1), encoding="utf-8")
        written.append(f"teams-raw.json ({len(teams_raw.get('teams', []))} teams)")
    for name, run in sorted(rows.items()):
        bucket = {}
        for offset in sorted(run["pages"]):
            for r in run["pages"][offset]:
                bucket[row_key(r)] = r
        (out / name).write_text(json.dumps({"result": {"rows": list(bucket.values())}}, ensure_ascii=False), encoding="utf-8")
        written.append(f"{name} ({len(bucket)} rows, {len(run['pages'])} page{'s' if len(run['pages']) > 1 else ''})")
    for team_id, data in ownership.items():
        (out / f"ownership-{team_id}.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    if ownership:
        written.append(f"ownership-*.json ({len(ownership)} teams)")
    print(f"read {path}", file=sys.stderr)
    print("\n".join("wrote " + w for w in written) or "found no Swarmia responses", file=sys.stderr)
    for tool, n in skipped.items():
        print(f"skipped {n} {tool} result(s) that were errors or not JSON", file=sys.stderr)
    if not teams_raw:
        print("no ListTeamsAndMembers response found: call it in this session first", file=sys.stderr)
        return 1
    return 0


COMPACT_HELP = """Compact input: '## section' headers, one tab-separated row per line, '#' starts a comment.
Author and team IDs may be shortened to any unique prefix of at least 8 characters.
  ## people       authorId  name  email  [role  jobDescription]      (a row with a role is a Swarmia user; email is the
                                                                     Swarmia account email when the person has one)
  ## teams        key  name  parentKey  directMemberIds  githubTeams  (ids space-separated; githubTeams 'id;name;ids' joined by ' + ')
  ## team-ids     swarmiaTeamId  name                                  (only for teams whose key is not their ID)
  ## admins       teamId  authorId
  ## attributes   attribute  value  authorIds
  ## repos        teamId  repository  mergedPrs
  ## agreements   teamId  type  configJson
  ## ownership    teamId  issueOwnershipDataJson  [settingsUrl]"""


def cmd_from_compact(args) -> int:
    """Convert the compact text format into the same input files `extract` writes."""
    sections, current = {}, None
    for n, line in enumerate(Path(args.file).read_text(encoding="utf-8").splitlines(), 1):
        if line.startswith("## "):
            current = sections.setdefault(line[3:].strip().lower(), [])
        elif line.strip() and not line.lstrip().startswith("#"):
            if current is None:
                raise SystemExit(f"line {n}: row before any '## section' header")
            current.append((n, line.rstrip("\n").split("\t")))
    errs = []

    def col(row, i, default=""):
        return row[i].strip() if len(row) > i else default

    def resolver(full_ids, what):
        def resolve(short, n):
            if short in full_ids or re.fullmatch(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", short):
                return short  # a full ID needs no listing (attributes may name people who are on no team)
            hits = [f for f in full_ids if f.startswith(short)] if len(short) >= 8 else []
            if len(hits) == 1:
                return hits[0]
            errs.append(f"line {n}: {what} '{short}' " + ("matches several IDs" if hits else "is not listed"))
            return short
        return resolve

    people, users = {}, []
    for n, r in sections.get("people", []):
        aid, name, email = col(r, 0), col(r, 1), col(r, 2)
        people[aid] = {"authorId": aid, "name": name, **({"email": email} if email else {})}
        if col(r, 3):
            users.append({"name": name, "email": email or None, "role": col(r, 3), "jobDescription": col(r, 4) or None, "authorIds": [aid]})
    author = resolver(set(people), "author")
    team_rows = sections.get("teams", [])
    team_ids = {col(r, 0): col(r, 1) for _, r in sections.get("team-ids", [])}
    team_ids.update({col(r, 0): col(r, 1) for _, r in team_rows if re.fullmatch(r"[0-9a-f-]{36}", col(r, 0))})
    team = resolver(set(team_ids), "team")
    keys = {col(r, 0) for _, r in team_rows}

    def members(ids, n):
        return [people.get(author(i, n), {"authorId": i}) for i in ids.split()]

    raw = {"teams": []}
    for n, r in team_rows:
        parent = col(r, 2) or None
        if parent and parent not in keys:
            errs.append(f"line {n}: parent '{parent}' is not a team key")
        ghs = []
        for g in [x for x in col(r, 4).split(" + ") if x.strip()]:
            gid, gname, ids = (g.split(";") + ["", ""])[:3]
            ghs.append({"githubTeamId": gid.strip(), "name": gname.strip(), "members": members(ids, n)})
        raw["teams"].append({"teamKey": col(r, 0), "name": col(r, 1), "parentTeamKey": parent, "authors": members(col(r, 3), n), "githubTeams": ghs})

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    def put(name, rows_):
        (out / name).write_text(json.dumps({"result": {"rows": rows_}}, ensure_ascii=False), encoding="utf-8")

    attrs = [{"_key": f"{col(r, 0)}:{col(r, 1)}", "value": col(r, 1), "attributeNames": [col(r, 0)], "authorIds": [author(i, n) for i in col(r, 2).split()]}
             for n, r in sections.get("attributes", [])]
    repos = [{"_key": [team(col(r, 0), n), col(r, 1)], "mergedPrs": int(col(r, 2) or 0)} for n, r in sections.get("repos", [])]
    agreements = []
    for n, r in sections.get("agreements", []):
        try:
            cfg = json.loads(col(r, 2) or "{}")
        except ValueError:
            errs.append(f"line {n}: agreement config is not JSON")
            cfg = {}
        agreements.append({"type": col(r, 1), "config": cfg, "teamIds": [team(col(r, 0), n)]})
    admins = [{"role": "TeamAdmin", "teamIds": [team(col(r, 0), n)], "authorIds": [author(col(r, 1), n)]} for n, r in sections.get("admins", [])]
    ownership = {}
    for n, r in sections.get("ownership", []):
        tid = team(col(r, 0), n)
        try:
            data = json.loads(col(r, 1) or "{}")
        except ValueError:
            errs.append(f"line {n}: ownership data is not JSON")
            continue
        ownership[tid] = {"team": {"id": tid}, "sections": {"issueOwnership": {"data": data, **({"settingsUrl": col(r, 2)} if col(r, 2) else {})}}}
    if errs:
        print("\n".join("error: " + e for e in errs), file=sys.stderr)
        return 1
    (out / "teams-raw.json").write_text(json.dumps(raw, ensure_ascii=False, indent=1), encoding="utf-8")
    put("team-ids.json", [{"id": i, "name": nm} for i, nm in team_ids.items()])
    if users:
        put("users.json", users)
    if admins:
        put("roles.json", admins)
    if attrs:
        put("attributes-1.json", attrs)
    if repos:
        put("repos.json", repos)
        put("repo-names.json", [{"id": nm, "fullName": nm} for nm in sorted({r["_key"][1] for r in repos})])
    if agreements:
        put("agreements.json", agreements)
    for tid, data in ownership.items():
        (out / f"ownership-{tid}.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {out}: {len(raw['teams'])} teams, {len(people)} people, {len(ownership)} ownership files", file=sys.stderr)
    return 0


def fill_inputs(args) -> None:
    """--inputs DIR: use the standard input files in DIR for every flag not given explicitly."""
    d = Path(args.inputs)
    for flag, name in INPUT_FILES.items():
        if getattr(args, flag) is None and (d / name).exists():
            setattr(args, flag, str(d / name))
    if args.attributes is None:
        found = sorted(str(p) for p in d.glob("attributes-*.json"))
        args.attributes = found or None
    if args.ownership is None:
        found = sorted(str(p) for p in d.glob("ownership-*.json"))
        args.ownership = found or None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check")
    c.add_argument("file")
    c.set_defaults(fn=cmd_check)
    s = sub.add_parser("summary")
    s.add_argument("file")
    s.add_argument("out")
    s.set_defaults(fn=cmd_summary)
    p = sub.add_parser("plan")
    p.add_argument("local")
    p.add_argument("remote")
    p.add_argument("--allow-delete", action="store_true")
    p.add_argument("--allow-unlink", action="store_true", help="unlink GitHub teams that are linked in Swarmia (stops their sync)")
    p.set_defaults(fn=cmd_plan, preview=False)
    d = sub.add_parser("diff", help="readable changes from OLD to NEW, any status (used before writing a pull)")
    d.add_argument("remote", metavar="old")
    d.add_argument("local", metavar="new")
    d.set_defaults(fn=cmd_plan, preview=True, allow_delete=True, allow_unlink=True)
    f = sub.add_parser("from-swarmia", help="convert ListTeamsAndMembers output (saved as JSON) to a model")
    f.add_argument("raw", nargs="?", help="saved ListTeamsAndMembers response (default: teams-raw.json in --inputs)")
    f.add_argument("--inputs", help="folder written by extract or from-compact; fills every input flag not given")
    f.add_argument("--merge", help="existing team folder (or model) whose missions, ownership, sections and local attributes to keep")
    f.add_argument("--out", required=True)
    f.add_argument("--drop-local", action="store_true", help="drop teams that exist only in --merge")
    f.add_argument("--users", help="saved EntityQuery on User: name, email, role, jobDescription, authorIds (every user goes into people.md)")
    f.add_argument("--roles", help="saved EntityQuery on UserRoleAssignment: id, role, teamIds, authorIds")
    f.add_argument("--attributes", nargs="+", help="saved EntityQuery pages on AuthorAttributeValue: value, attributeNames, authorIds")
    f.add_argument("--exclude-attributes", help="comma-separated attribute names to leave out (all are imported by default)")
    f.add_argument("--team-ids", help="saved EntityQuery on Team: id, name (resolves team admins, repositories, agreements and ownership on teams whose key is not their ID)")
    f.add_argument("--repos", help="saved EntityQuery on PullRequest grouped by [ownerTeamIds, repositoryId] counting merged PRs as mergedPrs")
    f.add_argument("--repo-names", help="saved EntityQuery on Repository: id, fullName (names the repositories in --repos)")
    f.add_argument("--repos-window", default="", help="label for the --repos timeframe, e.g. 'last 90 days'")
    f.add_argument("--agreements", help="saved EntityQuery on WorkingAgreement: type, config, teamIds")
    f.add_argument("--ownership", nargs="+", help="saved GetSettings responses (scope team, section issueOwnership), one per team")
    f.set_defaults(fn=cmd_from_swarmia)
    x = sub.add_parser("extract", help="write this Claude Code session's Swarmia responses to input files, unchanged (no re-typing)")
    x.add_argument("--transcript", help="session transcript (.jsonl); default: the newest one for the current directory")
    x.add_argument("--out", required=True)
    x.set_defaults(fn=cmd_extract)
    k = sub.add_parser("from-compact", help="convert compact tab-separated input (for agents without a readable transcript) to input files",
                       description=COMPACT_HELP, formatter_class=argparse.RawDescriptionHelpFormatter)
    k.add_argument("file")
    k.add_argument("--out", required=True)
    k.set_defaults(fn=cmd_from_compact)
    w = sub.add_parser("write", help="write a model (JSON) as the team folder: people.md and one folder per team")
    w.add_argument("model")
    w.add_argument("folder")
    w.set_defaults(fn=cmd_write)
    dt = sub.add_parser("detach", help="cut a team's GitHub sync in the folder: copy its GitHub team's people into Members and mark it (unlink)")
    dt.add_argument("folder")
    dt.add_argument("team", help="team key or exact name")
    dt.add_argument("--github-team", help="only this linked GitHub team (name or ID); default: all of the team's GitHub teams")
    dt.set_defaults(fn=cmd_detach)
    r = sub.add_parser("read", help="read the team folder into a model (JSON)")
    r.add_argument("folder")
    r.add_argument("--out", required=True)
    r.set_defaults(fn=cmd_read)
    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
