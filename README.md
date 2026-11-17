# SEI OS

**One rule book for every engineering leader's AI agent: your company context, Swarmia's Build framework and book, and shared skills, instead of a hundred one-off prompts.**

SEI OS is an open-source starter. Copy this repository into a private repository of your own, add your goals, metrics, principles, culture, career framework and past survey results to `company/`, and install the skills into Claude, Codex, Gemini CLI, GitHub Copilot or Cursor. From then on, when a CTO, a director or a new engineering manager asks the same question, their agents read the same context, follow the same workflow and the same guardrails, and give answers that can be compared.

> *"What are our engineering goals this quarter?"* · *"How should we handle the flood of AI-generated PRs?"* · *"Run a Build scorecard on us."* · *"What does a senior engineer do here?"* · *"What did the last survey say, and did we act on it?"*

Why this beats everyone writing their own prompts: [docs/why-a-rulebook.md](docs/why-a-rulebook.md).

## What is in the box

| Folder | What it is | Who edits it |
|---|---|---|
| [`company/`](company/) | **Your rule book.** Templates for profile, team structure, goals, metrics, engineering principles, culture, career framework and reviews, past surveys, decisions, glossary, and the trusted sources (research, reports, books, vendor docs) your leadership agrees on. Empty until you fill it. | You |
| [`knowledge/`](knowledge/) | The [Build framework](https://www.swarmia.com/framework/) (© Swarmia, not Apache-licensed, see [License](#license)) and a map of links into the web edition of the book [*Build*](https://www.swarmia.com/build/), sourced benchmarks, the answer contract every skill follows, and the report schema. | Upstream; refresh occasionally |
| [`skills/`](skills/) | Shared, tested workflows. Six to start; add your own. | You |
| [`shared/`](shared/) | A self-contained HTML report renderer (no CDN, no tracking). | Upstream |
| [`docs/`](docs/) | Onboarding plan, why a rule book, how to add company context, how to write skills, install. | |
| [`scripts/`](scripts/) | `sync_shared.py`, `validate.py`, `install.sh`. | |

## The starter skills

| Skill | Answers | Works without data? |
|---|---|---|
| [`ask-rulebook`](skills/ask-rulebook/SKILL.md) | "How do we do things here?" Goals, metric definitions, review policy, levels, survey results, past decisions, with the file each answer comes from and gaps flagged | Yes |
| [`build-coach`](skills/build-coach/SKILL.md) | "How should we…?" Advice from the Build book and framework, fitted to your goals, principles, culture and what you already tried | Yes; checks against live data when connected |
| [`build-scorecard`](skills/build-scorecard/SKILL.md) | "Where do we stand?" All nine Build metric groups rated great / good / attention / unknown, one or two focus problems, a shareable report | Yes (self-assessment); uses live data when connected |
| [`company-context`](skills/company-context/SKILL.md) | Sets up and audits the rule book: interviews you, imports your docs, drafts files with privacy guards, flags stale or missing context | Yes |
| [`pull-teams`](skills/pull-teams/SKILL.md) | Imports your team structure and roster from Swarmia into `company/teams/`, keeping your own missions, ownership and attributes | Needs Swarmia |
| [`push-teams`](skills/push-teams/SKILL.md) | Makes Swarmia's teams match the reviewed `company/teams/` file, previewed and confirmed before anything changes | Needs Swarmia |

Ideas for the skills to add next: [docs/writing-skills.md](docs/writing-skills.md#ideas-that-work-well-on-top-of-a-rule-book).

## Quick start

Rolling it out across your leadership team? Follow the four-phase plan with owners and checklists: [docs/onboarding.md](docs/onboarding.md). The short version:

**1. Make a private copy.** Once `company/` holds real content, this repository is your internal handbook, so it must be private. GitHub forks of public repositories cannot be made private: use **Use this template → Create a new repository → Private** (steps and how to pull upstream updates: [docs/private-copy.md](docs/private-copy.md)).

**2. Fill in the rule book.** Start with `company/profile.md`, `goals.md` and `metrics.md`. Either edit the templates, or open the repository in your agent and ask:

> *"Set up our rule book. Here's our OKR doc and engineering handbook: …"*

Guide per document type, and what never goes in: [docs/company-context.md](docs/company-context.md).

**3. Sync, validate, install.**

```bash
python3 scripts/sync_shared.py    # copies company/ and knowledge/ into each skill
python3 scripts/validate.py       # frontmatter, privacy guards, freshness, sync
./scripts/install.sh --target claude   # or codex, gemini, copilot, cursor, all
```

Other agents, the Claude Code plugin, and the optional Swarmia data connection: [docs/install.md](docs/install.md).

**4. Ask.** *"What does our rule book say about code review?"* · *"Run a Build scorecard for last quarter."*

## How it works

```
 question ──▶ skill (SKILL.md) ──▶ references/company/   your goals, metrics, principles, surveys…
                 │                 references/            Build framework, book, benchmarks, contract
                 │                 live data (optional)   e.g. Swarmia MCP server
                 ▼
     answer that cites its sources, flags gaps in the rule book,
     and ends with "How this was calculated"
```

- **The rule book wins over generic advice.** When the Build book suggests something your organization decided against, skills say so and show the trade-off.
- **Empty is honest.** A template file counts as missing. Skills tell the user what is not filled in, and never invent company facts.
- **Every skill is self-contained.** `sync_shared.py` copies `company/` and the shared knowledge into each skill, so a skill folder works on its own in any agent. Re-sync and re-install after rule book changes.
- **Changes go through pull requests.** The rule book improves the way code does: reviewed, versioned, owned.

## Principles

1. **Teams and systems, not individuals.** No skill ranks engineers or assesses a named person against the career framework. Survey comments are paraphrased.
2. **No number without context.** A comparison, a sample size and a source.
3. **Company context first, then Build, then your trusted sources and benchmarks.** Cited by file path or URL.
4. **Aggregates only in `company/`, except the team roster.** No personal data, ratings, compensation or raw comments, except `company/teams/`, which holds your full roster in your private copy and stays empty in this template. `validate.py` guards both.
5. **Ask before acting.** Skills draft rule book changes and tool actions; people approve them.
6. **Your data stays yours.** Reports are local files in a git-ignored folder; nothing here phones home.

## Going further with live data

Every skill works from the rule book alone. Connect [Swarmia](https://www.swarmia.com)'s [MCP server](https://help.swarmia.com/settings/integrations/mcp-server) and the same skills check advice against your delivery, quality, AI adoption, investment and survey data, and the Build scorecard rates groups from measurements instead of self-assessment.

## Contributing

Improvements to skills, scripts, `knowledge/` and docs are welcome: see [CONTRIBUTING.md](CONTRIBUTING.md). Never open a pull request here with your own `company/` content; that belongs in your private copy. Security issues: [SECURITY.md](SECURITY.md).

## License

Code, skills, templates and docs: [Apache License 2.0](LICENSE).

The [Build framework](https://www.swarmia.com/framework/) and the [*Build* book](https://www.swarmia.com/build/) are © 2026 Swarmia Oy and are not included. `knowledge/build-framework.md` and `knowledge/build-concepts.md` hold only their structure, names and links, and skills read the full text on the web. See [NOTICE](NOTICE).

Content you add to `company/` is yours.
