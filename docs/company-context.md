# Adding your company context

`company/` is the part of the rule book only you can write. This guide covers what to put in each file, how to bring in documents you already have, and how to keep it current. The templates in `company/` show the expected structure.

## Where to start

You do not need everything on day one. In order of how much they improve answers:

1. **`profile.md`**: teams, size, products, tooling. Without it, advice cannot fit your situation.
2. **`goals.md`**: what you are trying to achieve this period. Lets skills connect any question to what matters now.
3. **`metrics.md`**: the metrics you agreed on, with definitions. Stops every leader from picking their own.
4. **`engineering-principles.md`** and **`culture.md`**: how you work. Keeps advice inside your agreements.
5. **`surveys/`**: the last two or three surveys. Lets skills check advice against what engineers said.
6. **`career-framework.md`**, **`decisions/`**, **`glossary.md`**: add as questions come up that need them.

The fastest way to a first version: ask your agent to run the **`company-context`** skill. It interviews you, reads documents you point it at, and drafts the files for you to review.

## Bringing in documents you already have

Most of this already exists somewhere: a Notion handbook, a Google Doc with OKRs, a career ladder spreadsheet, a survey export.

- **Summarize, then link.** Put the agreed content in the template's structure (a page or two) and link to the full source at the top. Agents read every file on every relevant question; a 40-page handbook pasted in wastes context and buries what matters.
- **Use the agent to draft.** "Read this OKR doc and fill in `company/goals.md`" works well. Review the result: you are publishing it to every leader's agent.
- **Keep the source of truth where it is.** If the career ladder is owned by HR in another system, `career-framework.md` summarizes and links to it; it does not fork it.
- **Extra files are fine.** Add files for things that do not fit the templates (`company/hiring.md`, `company/incident-process.md`, `company/planning-calendar.md`). Use the same frontmatter (`title`, `status`, `owner`, `last_reviewed`). Skills read the whole folder.

## Per document type

### Goals and OKRs (`goals.md`)

Write the current period only, with the period in the frontmatter. One short list: company goals, then engineering goals that each name the company goal they serve. Add the "explicitly not doing" list; it stops agents from recommending work you already decided against. Move the previous period's file to `decisions/` or delete it when the period ends.

### Metrics (`metrics.md`)

Two to four metrics per goal at most. For each: a one-line definition, the goal it serves, the Build framework group, the current baseline, the direction or target, an owner and where the live number lives. If you use Swarmia, these should match your Swarmia key metrics, so skills can evaluate them live. Write down metrics you chose *not* to use and why; that is a guardrail agents will respect.

### Engineering principles (`engineering-principles.md`)

What is practised, not aspired to. Working agreements with how you check them. Review, testing, release, on-call and AI-tool rules. Short principles with one line of reasoning each are more useful than long prose.

### Culture (`culture.md`)

Values with what they look like in practice *and* what they do not mean. How decisions get made. The unwritten rules a new leader would not guess. This is what stops generic advice from landing badly.

### Past survey results (`surveys/`)

One file per survey from `surveys/_template.md`. Aggregate scores by question, change since the previous survey, team-level movements only where at least ~5 people answered, comment themes paraphrased, and **what you did about it**. Never paste raw comments or anything that identifies a respondent. Two or three past surveys are enough to show trends.

### Performance review structure (`career-framework.md`)

Levels, expectations per dimension, and how the review cycle works: cadence, inputs, calibration, promotion process, and explicitly which data is and is not used. This lets agents help managers explain expectations, prepare growth conversations and write role descriptions. It must never contain individual ratings, review outcomes or compensation. Skills will not score named people against the framework.

### Decisions (`decisions/`)

One file per decision that shapes how teams work, from `decisions/_template.md`. The "alternatives considered" and "outcome" sections are what make this valuable: they stop the organization from re-running experiments that already failed, and they explain why things are the way they are.

### Team structure (`teams/`)

The teams, their hierarchy, missions and ownership, and who is on each, with custom attributes such as role and seniority. Start from Swarmia with the `pull-teams` skill, add what Swarmia does not hold, and from then on change teams through pull requests and push them back with `push-teams`. Each team is a folder with a `team.md` (sub-teams are sub-folders) and everyone is listed once in `people.md`, so admins can change structure by hand through pull requests. The folder holds names and emails in your private copy, so it is never copied into installed skills; every skill reads the generated, people-free `company/team-structure.md`. Format and privacy rules: [`company/teams/README.md`](../company/teams/README.md).

### Trusted sources (`sources/`)

The outside material your leadership agrees to trust: research (DORA, SPACE), reports, books, manifestos, vendor docs such as Swarmia's help center, and your own internal reports. One file per source, with a link, an owner, what it should answer (`use_for`) and its `authority` (`reference`, `benchmark` or `policy`). Three defaults ship as templates; set one to `current` to adopt it. Link, never paste: agents read the source at its URL. Keep the list to the 10 to 20 sources you would defend in a leadership meeting. Field reference: [`company/sources/README.md`](../company/sources/README.md).

## What never goes in

- Individual performance ratings, review text, compensation, health, leave or other personal data, except in `teams/`, which holds your full roster (see Team structure above).
- Raw survey comments, or team results with fewer than ~5 respondents.
- Credentials, API tokens, customer data.
- Drafts and proposals that are not agreed.

`scripts/validate.py` catches some of this (email addresses, tokens, raw survey comments marked as quotes), but the real guard is review: treat changes to `company/` like changes to your internal handbook.

## Keeping it current

- **Owner and date on every file.** Skills warn when `last_reviewed` is older than six months.
- **Review with your planning cycle.** Update `goals.md` and `metrics.md` when the period changes; add a survey file after each survey.
- **Changes by pull request.** The diff is the change log. A leader proposing a new working agreement opens a PR to `engineering-principles.md`.

## How skills see the context

Skills are installed folder by folder into each agent (`~/.claude/skills/<skill>/`, `~/.codex/skills/<skill>/`…), where they cannot see the rest of the repository. So `scripts/sync_shared.py` copies `company/` into every skill that declares the `company` bundle in `catalog.json`, under `references/company/`. After every change:

```bash
python3 scripts/sync_shared.py
python3 scripts/validate.py
./scripts/install.sh --target claude   # or reinstall the plugin / pull in each agent
```

When people use the agent inside the repository itself, `AGENTS.md` points it at `company/` directly.
