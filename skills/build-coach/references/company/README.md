# Company rule book

This folder is where your organization's own context lives. Every skill reads it before answering, so a CTO, a director and a new engineering manager asking the same question get answers built on the same goals, definitions and principles.

Each file starts as a template (`status: template` in its frontmatter). Fill it in, set `status: current`, name an `owner` and a `last_reviewed` date. Skills treat template files as missing and tell the user what is not filled in yet.

| File | What goes in it | Typical source |
|---|---|---|
| [`profile.md`](profile.md) | Size, shape, teams, products, stage, tooling: the starting factors every piece of advice depends on | Org chart, team pages |
| [`goals.md`](goals.md) | Company and engineering goals for the current period (OKRs, bets, initiatives) | Planning docs, OKR tool |
| [`metrics.md`](metrics.md) | The few metrics you agreed to track, their definitions, targets, owners and where they live | Metrics dashboards, Swarmia key metrics |
| [`engineering-principles.md`](engineering-principles.md) | How you build: working agreements, review, testing, release, on-call, AI tool use | Engineering handbook, RFCs |
| [`culture.md`](culture.md) | Values, how decisions get made, communication and feedback norms | Values page, onboarding docs |
| [`career-framework.md`](career-framework.md) | Levels, role expectations, and how the performance review cycle works | Career ladder, HR process docs |
| [`surveys/`](surveys/) | One file per past developer experience or engagement survey: aggregated scores, themes, what you did about it | Survey tool exports |
| [`decisions/`](decisions/) | Leadership and engineering decisions worth remembering, with the reasoning | ADRs, leadership meeting notes |
| [`glossary.md`](glossary.md) | Your words: team names, product names, internal acronyms, what "done" means here | Onboarding docs |
| [`teams/`](teams/) | Team structure: hierarchy, missions, ownership, and the full roster with custom attributes (role, seniority…). One folder per team and a `people.md`, edited by hand; skills read only the generated, people-free [`team-structure.md`](team-structure.md) | Swarmia (`pull-teams`), HR system, org chart |
| [`sources/`](sources/) | Trusted outside sources: research, reports, books, manifestos, vendor docs (such as Swarmia's help center), internal reports. Links, owners and what each should answer | Reading lists, leadership picks |

## Rules for what goes in

- **Aggregates, not people**, everywhere except `teams/`. No individual performance ratings, compensation, health or personal data. Survey results are team- or org-level, with comments paraphrased. The career framework describes roles, not the people in them.
- **`teams/` is the exception.** In your private copy it holds the full roster: names, emails, Swarmia IDs and every custom attribute Swarmia has. The public template keeps it empty. It is never copied into installed skills; they read the people-free `team-structure.md`.
- **Decisions, not drafts.** Put in what is agreed. Proposals in progress belong elsewhere until they are decided.
- **Short beats complete.** A one-page `goals.md` that is current is worth more than a long one that is a quarter old. Link out to the full source document.
- **Dated and owned.** Every file has an `owner` and a `last_reviewed` date. Skills flag files older than six months.
- **Private repository.** Once you fill this folder in, your copy of this repository holds company information. Keep it in a private repository and treat it like your internal handbook.

## After editing

```bash
python3 scripts/sync_shared.py   # copies company/ into every skill that uses it
python3 scripts/validate.py      # checks frontmatter, privacy guards and sync
```

Then re-install or update the skills for your team (see the README). How to add each kind of document, with examples: [docs/company-context.md](../docs/company-context.md). The `company-context` skill can also interview you and fill these files in.
