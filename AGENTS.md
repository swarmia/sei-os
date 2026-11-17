# AGENTS.md

Instructions for AI coding agents (Claude Code, Codex, Gemini CLI, GitHub Copilot, Cursor and any client that reads `AGENTS.md`) working **with** or **on** this repository.

This repository is the organization's engineering-leadership rule book: its own context in `company/`, Swarmia's [Build framework](https://www.swarmia.com/framework/) and the book [*Build: Elements of an Effective Software Organization*](https://www.swarmia.com/build/) in `knowledge/`, and shared skills in `skills/` that every leader's agent loads the same way.

## When you answer a leader's question

1. **Pick a skill.** Skills live in `skills/<name>/SKILL.md`. Match the question to a skill's description and read the whole `SKILL.md` before answering. With no match, follow the answer contract directly.
2. **Read the company rule book.** `company/` holds this organization's goals, metrics, principles, culture, career framework, past surveys and decisions. It wins over generic advice; say so when they disagree. Files with `status: template` are not filled in yet: say what is missing, never invent it.
3. **Follow the answer contract** (`knowledge/answer-contract.md`): a comparison and `n` behind every number, medians for durations, no invented benchmarks (use `knowledge/benchmarks.md`), cite sources.
4. **Ground advice in Build.** Cite the framework (`knowledge/build-framework.md`) or the book's web edition, found through the concept index and question router in `knowledge/build-concepts.md`, with the web URL.
5. **Teams and systems, not individuals.** Never rank or score individual engineers, never assess a named person against the career framework, paraphrase survey comments.
6. **Actions need confirmation.** Tools that change something are called only when the user asked for that change.
7. **Reports stay local.** Write rendered reports to `./sei-reports/` (git-ignored).
8. **End with "How this was calculated"**: sources, timeframe, aggregate, `n`, caveats, links.

## When you change this repository

- **Layout.** `company/` (the organization's rule book), `knowledge/` (Build framework, Build book concept index, benchmarks, answer contract, report schema; these four Build and contract files form the `foundation` bundle every skill carries), `skills/` (one folder per skill), `shared/` (report template and renderer), `examples/` (fictional sample data), `docs/`, `scripts/`, `catalog.json` (skill manifest).
- **Shared files are copied, not linked.** Each skill must work when its folder is copied on its own into an agent's skills directory. Edit the source in `company/`, `knowledge/` or `shared/`, list bundles in `catalog.json`, then run `python3 scripts/sync_shared.py`. Never edit files under `skills/*/references/`, `skills/*/assets/` or `skills/*/scripts/` that sync manages.
- **Validate before committing:** `python3 scripts/validate.py` checks skill frontmatter, catalog consistency, sync drift, `company/` frontmatter and freshness, and privacy guards.
- **Company content:** aggregates and agreed decisions only. No personal data, individual ratings, compensation, raw survey comments or credentials. See `company/README.md`.
- **Team roster exception:** `company/teams/` holds people (names, emails, Swarmia IDs, every custom attribute) in an organization's private copy. In this public template it stays empty; `validate.py --upstream` enforces it. It is never copied into skills; other skills read the people-free `company/team-structure.md`. Never flag roster data in a private copy as a privacy problem, and never add any to the template.
- **Skill format:** follow `docs/writing-skills.md`. Frontmatter `name` (kebab-case, matches folder) and `description` (what it does + "Use when …" triggers, under 1024 characters). Body under ~150 lines.
- **Voice:** plain, specific, numbers first. "Engineering effectiveness" for the whole system. No hype, no emoji in skill bodies.
