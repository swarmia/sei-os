# Team structure

Your engineering organization as folders: one folder per team, sub-teams as sub-folders, and one table of people. It is the source of truth for team structure. Admins change it through pull requests, and the change is pushed to Swarmia after the checks pass. Beyond Swarmia, each team file can hold anything else teams should agree on: Slack channel, on-call, repositories, Jira project, working agreements.

```
company/teams/
  README.md                       this file
  people.md                       everyone once: name, email, attributes, Swarmia ID
  engineering/
    team.md                       the Engineering team
    payments/team.md              a sub-team of Engineering
    platform/team.md
company/team-structure.md         generated, no names: what every other skill reads
```

## The loop

1. **Pull** once from Swarmia to start: ask your agent *"Pull our teams from Swarmia"* (`pull-teams` skill). Commit the result through a pull request.
2. **Edit** in the repository: add a person to a team, move a team (move its folder), create a team (new folder with a `team.md`), write missions and ownership.
3. **Check** on every pull request: `python3 scripts/validate.py` (CI runs it) checks that every member's email resolves to a row in `people.md`, keys are unique, attributes use allowed values, and `team-structure.md` is regenerated.
4. **Push** after merge: ask *"Push our teams to Swarmia"* (`push-teams` skill). It shows exactly what will change in Swarmia and applies nothing without your yes.

Pull again only to bring in changes made in Swarmia. Push before pulling, or a pull will overwrite structure changes that were never pushed (`pull-teams` warns you).

Tip: add a `CODEOWNERS` rule per team folder (`company/teams/engineering/payments/ @payments-leads`) so team leads review changes to their own team.

## `team.md`

```markdown
---
key: payments
name: Payments
membership: mixed  # linked GitHub teams plus people added directly
slack: "#team-payments"
oncall: payments-primary
---

# Payments

## Mission

Make paying us effortless and safe.

## Owns

- checkout-service
- billing UI

## Members

- Alex Example <alex@…>
- Sam Example <sam@…>

## GitHub teams

- payments-eng `GITHUB-TEAM-ID`
  - Kim Example <kim@…>

## Team admins

- Alex Example <alex@…> (TeamAdmin)

## Main repositories

- acme/checkout-service: 212 merged PRs (71%, last 90 days)
- acme/web: 61 merged PRs (20%, last 90 days)

## Issue ownership

- Issues matching any of:
  - Jira project PAY (Payments)
  - Linear team Payments (cycles on)
- Settings: https://app.swarmia.com/settings/team/issues?teamId=…

## Working agreements in Swarmia

- Review pull requests within 1 day `max_pull_request_review_time`
- At most 3 Story issues in progress at a time `wip_issues`

## On-call and rituals

Anything you add as your own section is kept on every pull.
```

- **`key`**: the team's Swarmia key (its external ID, or its Swarmia ID when it has none). For a new team, pick a short slug. Never change the key of an existing team: it is how the team is matched in Swarmia.
- **`name`**: the team's name in Swarmia. Renaming here renames it in Swarmia on the next push. The folder name does not matter.
- **Other frontmatter keys** (Slack channel, on-call, Jira project…) are yours and kept on every pull.
- **Parent**: the folder the team sits in. Moving the folder re-parents the team on the next push.
- **Members**: people directly on the team, written `Name <email>`. The email links to the person's row in `people.md`; the name is only for reading, so renaming someone never breaks a team. Someone without an email is written `Name <swarmia:SWARMIA-ID>`. A bare name fails the checks.
- **GitHub teams**: linked GitHub teams, any number per team. Swarmia keeps their members in sync with GitHub; they are listed here for reference only, and editing that list does nothing (the push says `ignored`). To change who is in a synced team, change the GitHub team.
- **`membership`**: written by every pull, from the team itself: `github` (members come only from linked GitHub teams), `mixed` (one or more GitHub teams plus people added directly) or `manual` (people added directly). Editing it changes nothing. Adding a person directly to a `github` team is fine: it becomes `mixed`.
- **Cutting a sync:** `python3 shared/scripts/teams.py detach company/teams "Team name" [--github-team NAME]` copies the GitHub team's people into **Members** and marks its line ` (unlink)`. Edit **Members** as you like (replace a person who came from GitHub with someone else), review it in a pull request, and push: the sync stops and the team keeps exactly the people under **Members**. A push never unlinks a GitHub team that is linked in Swarmia unless its line is marked ` (unlink)`; a line that simply disappeared is kept linked (the push says `keep`).
- **Team admins**: team-level roles pulled from Swarmia, read-only here; an admin does not have to be a member. Change them in Swarmia. Viewer, Editor and Admin are organization-wide roles, shown as `Swarmia role` in `people.md`.
- **Main repositories**, **Issue ownership**, **Working agreements in Swarmia**: pulled from Swarmia on every pull and never pushed. Main repositories are the up to five repositories that hold at least 5% of the merged pull requests the team owns, in the pull's timeframe (90 days by default); write what the team is responsible for under **Owns**. Issue ownership and working agreements are changed in Swarmia's team settings. Write your own agreements in a section of your own (any title other than these).
- **Your own sections** after these are kept on every pull.

## `people.md`

One row per person: every Swarmia user (org admins, editors and viewers, on a team or not), everyone on a team, and anyone you add by hand. A person's email here is their Swarmia account email; team files use the same email. An **Attributes** table declares the columns:

- Columns with source `swarmia` are refreshed on every pull: Swarmia's custom attributes (Job title, City, Department…), `Swarmia role` (Admin, Editor, Viewer; empty when the person has no Swarmia account) and `Swarmia job description`. Change them in Swarmia.
- Columns with source `local` are yours (seniority, discipline…). Add a row to the Attributes table, then a column to the People table. Comma-separated allowed values are checked.
- Every Swarmia custom attribute is imported, HR fields included. To leave one out, the pull takes `--exclude-attributes`.
- `team-structure.md` only shows group counts: a value held by fewer than 5 people is counted as `other`, teams under 5 people only count in the organization total, and attributes whose values mostly identify single people (employee numbers, dates) are not summarized there.

Headcount counts each person once across direct and GitHub-team membership, and leaves out bot accounts (names ending in `[bot]`).

## Commands

From the repository root:

```bash
python3 shared/scripts/teams.py check company/teams
python3 shared/scripts/teams.py summary company/teams company/team-structure.md
```

## Privacy

- **The public template holds no people.** `validate.py --upstream` fails if this folder holds anything but this README and an empty `people.md`.
- **Your private copy holds the full roster**, including emails and Swarmia IDs. Keep the repository private, with access limited to people who need it.
- This folder is excluded from the files `sync_shared.py` copies into skills, so names and emails never reach installed skills, plugin bundles or uploaded zips. Other skills see `company/team-structure.md` only.
- The folder holds whatever custom attributes your Swarmia holds. Decide who can read the repository accordingly.
