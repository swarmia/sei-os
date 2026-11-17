# Writing a skill

The starter ships four skills. The value grows as you add your own: one skill for each question your leaders ask every month. A skill is a short, reviewed playbook, so the answer is built the same way no matter who asks.

## 1. Start from a real, recurring question

Write these down first:

- **Who asks** (CTO, director, EM, platform, PM, finance).
- **The question** in three or four phrasings people actually use.
- **The decision** the answer informs.
- **The rule book files** it needs (`company/goals.md`, `company/surveys/`…), and any data source.
- **The Build pillar and metric group** it belongs to (`knowledge/build-framework.md`), if any.

If an existing skill covers it, improve that skill instead.

### Ideas that work well on top of a rule book

| Skill | What it reads | What it produces |
|---|---|---|
| `quarterly-planning-prep` | `goals.md`, `metrics.md`, last scorecard in `decisions/` | Draft engineering goals tied to company goals, with "not doing" list |
| `survey-followup` | `surveys/` (latest two), `engineering-principles.md` | Themes, what changed, what was promised last time, one or two actions |
| `new-manager-onboarding` | All of `company/` | A first-30-days guide for a new EM: teams, goals, agreements, unwritten rules |
| `growth-conversation-prep` | `career-framework.md`, `culture.md` | Questions and framing for a growth conversation at a given level. Roles only, never an assessment of the person |
| `incident-review` | `engineering-principles.md` (incidents), `decisions/` | Blameless postmortem structure with follow-ups that match your process |
| `board-update` | `goals.md`, `metrics.md`, live data | One-page engineering update in your board's format |
| `working-agreement-proposal` | `engineering-principles.md`, `decisions/`, Build book | A proposed agreement, its reasoning, how to check it, and a PR to add it |

## 2. Folder and frontmatter

```
skills/<kebab-name>/
  SKILL.md
  references/   # vendored by sync (company/, knowledge/), plus skill-specific references you add
  scripts/      # vendored by sync, plus skill-specific scripts
  assets/       # vendored by sync, plus templates
```

```yaml
---
name: <kebab-name, same as the folder>
description: <What it does, concretely, in one or two sentences. Then "Use when …" with the phrasings from step 1.>  # ≤ 1024 chars
license: Apache-2.0
compatibility: <What it needs: nothing, file access, a data source.>
metadata:
  pillar: <foundation | ai-leverage | effectiveness | return-on-engineering>
  roles: <space-separated role ids from catalog.json>
---
```

The description is what agents match on. Make it specific: name the inputs, the outputs and the trigger phrases.

## 3. Body

Keep it under ~150 lines. Suggested sections:

1. **One paragraph of intent**, ideally anchored in a Build framework or book idea.
2. **Sources**: which `references/company/` files, in which order, and which Build references.
3. **Workflow**: numbered steps. What to read, what to ask the user, what to compute or query, how to compare.
4. **Output**: the answer shape, and the report layout if it renders one (`references/report-schema.md`).
5. **Rules**: guardrails specific to this question (sample sizes, privacy, what not to infer).

Every skill inherits `references/answer-contract.md`; you do not need to repeat it.

**Build the skill on the shared foundation.** Every skill carries the `foundation` bundle: the answer contract, benchmarks, `build-framework.md` and `build-concepts.md`. Use the concept names from `build-concepts.md` as vocabulary, cite the web edition section it links, and quote numbers only from `benchmarks.md`. The book itself is not in this repository. Skills read the book itself from the web edition at runtime: point the workflow at the sections to fetch. Keep `build-concepts.md` to titles, names and links, and `build-framework.md` to pillar, group and metric names with one-line notes in our own words; do not paste text or summaries of the book or the framework page into them or a skill's `references/`. Point the workflow at https://www.swarmia.com/framework/ when it needs the framework's reasoning.

## 4. Register and sync

Add the skill to `catalog.json` with its pillar, roles, bundles (always `foundation`, plus `company` for the rule book and `report` if it renders one) and a one-line summary, then:

```bash
python3 scripts/sync_shared.py
python3 scripts/validate.py
```

## 5. Test it

Install it (`./scripts/install.sh --link --only <name>`) and ask the question in two or three phrasings. Check:

- The skill triggers from natural phrasing.
- It cites the right `company/` files and says when one is missing or stale.
- Every number has a comparison and `n`.
- Failure paths: empty rule book, no data connection, tiny team.

## 6. Review like code

Open a pull request. Ask one leader who will use the skill to try it before merging. Once merged and installed, every agent in the organization uses the improved version.

## Style

- Plain, specific, numbers first. Short sentences.
- "Engineering effectiveness" for the system; "developer productivity" only as the Build metric group.
- "Fastest / slowest team", never "best / worst".
- Teams and systems, never individuals.
- Cite sources for every benchmark; do not invent targets.
