---
name: company-context
description: Sets up and maintains the organization's rule book in the company/ folder (profile, goals, key metrics, engineering principles, culture, career framework and review process, past survey results, decisions, glossary, trusted sources) by interviewing a leader, reading documents they point to (OKR docs, handbooks, career ladders, survey exports), drafting each file in the template's structure with privacy guards, and auditing the folder for gaps, stale files and contradictions. Use when someone says "set up our rule book", "add our company context", "import our OKRs", "add our career ladder", "add the last survey results", "record this decision", "add this report as a trusted source", "is our rule book up to date", or a skill reports that company context is missing.
license: Apache-2.0
compatibility: Needs file access to the rule book repository (run inside the repo). Reads documents the user provides or that connected tools (Notion, Google Drive, Confluence) can open.
metadata:
  pillar: foundation
  roles: cto director em platform
---

# Company context

Every other skill is only as good as the rule book it reads. This one builds and maintains it. It works on the repository's `company/` folder, not on the copy vendored into installed skills.

Read `company/README.md` (the map and rules for what goes in) and `docs/company-context.md` (per-document guidance) before writing anything.

## Modes

Pick from the request; ask if unclear.

- **Set up**: first pass over the whole folder.
- **Add**: one document type (goals, metrics, a survey, a decision…).
- **Audit**: check the folder's health without changing it.

## Set up and add

1. **Inventory.** List `company/` files with `status`, `owner`, `last_reviewed`. Start set-up with `profile.md`, `goals.md`, `metrics.md`, in that order.
2. **Collect sources.** Ask the leader for existing documents (links or files) for the target file. Read what connected tools can open. If there are none, interview: at most five questions per file, built from the template's headings, one message at a time.
3. **Draft in the template's structure.** Summarize; link to the full source at the top. Use the organization's own words. Keep each file to what an agent needs, typically one or two pages. Mark anything you inferred rather than read as `(to confirm)`.
4. **Apply the privacy guards** before writing (see Rules). Strip or aggregate anything that fails; tell the user what you removed and why.
5. **Show the draft** and ask for corrections. On approval, write the file with `status: current`, the `owner` the user names, and today's date in `last_reviewed`.
6. **Sync and validate:** `python3 scripts/sync_shared.py` then `python3 scripts/validate.py`. Report errors and fix them.
7. **Suggest the next file** that would most improve answers, and remind the user to commit through a pull request so the change is reviewed.

Per type:

- **Goals**: current period only; each engineering goal names the company goal it serves; include "explicitly not doing".
- **Metrics**: two to four per goal; definition, Build group, baseline, direction, owner, where it lives. If Swarmia is connected, compare with `ListKeyMetrics` and flag mismatches.
- **Surveys**: new file `company/surveys/yyyy-mm-<survey>.md` from `_template.md`. Scores by question and change vs the previous survey; team rows only with at least ~5 respondents; comment themes paraphrased with rough counts; ask what was done about it.
- **Career framework**: levels, expectations per dimension, review cycle, which data is and is not used. Roles and process only.
- **Decisions**: new file `company/decisions/yyyy-mm-dd-<slug>.md` from `_template.md`, with alternatives considered and how to tell whether it worked.
- **Teams**: use the `pull-teams` skill to import from Swarmia, or edit the team folders in `company/teams/` by hand (format in `company/teams/README.md`), then regenerate the summary with `python3 shared/scripts/teams.py summary company/teams company/team-structure.md`. Never put ratings, compensation or personal circumstances in member attributes.
- **Trusted sources**: new file `company/sources/<slug>.md` from `_template.md`, or adopt a shipped default by setting it to `current`. Open the URL to confirm it works and says what the leader thinks it says. Ask who owns it, what questions it should answer (`use_for`) and its `authority`: `reference` by default, `benchmark` only for research with published numbers, `policy` only if the organization formally adopted it (then also record a decision). Link, never paste: `content_in_repo: yes` only for material the organization owns. Push back when the list passes about 20 sources or two sources say opposite things on the same question.

## Audit

Report, without editing:

- Files still `status: template`, and which skills lose most because of it.
- Files with `last_reviewed` older than six months, or no owner.
- `goals.md` period already ended.
- Metrics in `metrics.md` that serve no goal, and goals with no metric.
- Contradictions between files (a principle vs a decision, a metric definition vs the glossary).
- Survey files with no "what we did about it".
- Trusted sources whose URL no longer opens, with no `use_for`, or not reviewed in six months.
- Anything that breaks the privacy rules.

End with the three changes that would improve answers most, each with its owner.

## Rules

- **Never write personal data** outside `company/teams/`: individual ratings, review text, compensation, health, leave, or named feedback. The team roster in `company/teams/` holds people and all their Swarmia attributes in a private copy; leave it to `pull-teams` and the team files. Survey comments are paraphrased themes, never quotes. Team survey results only with at least ~5 respondents.
- **No credentials or customer data.**
- **Decisions, not drafts.** Only agreed content; label anything unconfirmed.
- Do not overwrite a `status: current` file without showing the diff and getting a yes.
- The repository should be private once `company/` holds real content. If it looks public (for example a public GitHub remote), warn before writing.
