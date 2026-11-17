# Changelog

Notable changes to SEI OS. Versions follow `catalog.json` and `.claude-plugin/plugin.json`.

## 0.1.0 (2026-11)

First public release.

### Unreleased

- Replaced the Build book digest (`knowledge/build-book.md`) with `knowledge/build-concepts.md`, a section map, concept index and question router made only of titles and links to the web edition. Skills read the book on the web; none of its content is in the repository.
- New `foundation` bundle (answer contract, benchmarks, Build framework, Build concepts) that every skill carries; `validate.py` enforces it. Replaces the `contract`, `framework` and `book` bundles.
- Trusted sources in `company/sources/`: research, reports, books, manifestos, vendor docs and internal reports the organization agrees to trust, linked with an owner, `use_for` and `authority`. Three defaults ship as templates (Swarmia help center, DORA, SPACE). Answer contract, `validate.py`, `company-context`, `ask-rulebook` and `build-coach` support them.
- Team structure in `company/teams/`: one folder per team (`team.md`, sub-teams as sub-folders) and a shared `people.md`, editable by hand and kept across pulls (empty template upstream; full roster with attributes in private copies, never copied into installed skills), plus a generated, people-free `company/team-structure.md`. Team files link members to `people.md` by email (`Name <email>`), never by name; all Swarmia custom attributes are imported. New skills `pull-teams` (from Swarmia, including Swarmia roles, team admins, job descriptions and custom attributes) and `push-teams` (to Swarmia, previewed and confirmed), `shared/scripts/teams.py`, `!path` exclusions in bundles, and `validate.py` checks.
- `pull-teams` also pulls each team's main repositories (by merged PRs it owns, last 90 days), issue ownership (projects, tracker teams, sprint board) and working agreements into pull-only sections of `team.md`, and `company/team-structure.md` gains a people-free "Team context from Swarmia" section with them.
- Faster team pulls and pushes: `teams.py extract` writes a Claude Code session's Swarmia responses to input files straight from the transcript (no re-typing), `teams.py from-compact` turns a compact tab-separated format (about a fifth of the JSON) into the same files for other agents, and `from-swarmia --inputs DIR` reads them all. `pull-teams` writes its result to `company/teams/`; `sei-reports/` holds only working files and dry runs.
- Teams synced from GitHub are marked and protected: every pull writes `membership: github | mixed | manual` into `team.md` and `team-structure.md` (teams may mix direct members, several GitHub teams and team admins). `push-teams` never unlinks a GitHub team linked in Swarmia unless its line is marked ` (unlink)`, reports edits to GitHub member lists as ignored, and `teams.py detach` cuts a sync by copying the GitHub team's people into Members so they can be edited. Team-level roles are pulled without a TeamAdmin filter. `extract` keeps only the latest run of each query.
- `team-structure.md` Composition no longer lists individual values: values held by fewer than 5 people are counted as `other`, and attributes that mostly identify single people (IDs, dates) are not summarized. `pull-teams` imports every attribute, HR fields included, unless the user excludes some.
- `docs/onboarding.md`: a four-phase rollout plan with owners, checklists and done-when checks.

- Company rule book templates in `company/`: profile, goals, metrics, engineering principles, culture, career framework, surveys, decisions, glossary.
- `knowledge/`: Build framework, paraphrased Build book digest, sourced benchmarks, answer contract, report schema.
- Four skills: `ask-rulebook`, `build-coach`, `build-scorecard`, `company-context`.
- Self-contained HTML report renderer, `sync_shared.py`, `validate.py`, `install.sh` for Claude, Codex, Gemini CLI, GitHub Copilot and Cursor.
- Claude Code plugin and marketplace manifest; optional Swarmia MCP server.
