# Onboarding: from empty repository to every leader using it

A four-phase plan for rolling SEI OS out in your organization. Move to the next phase when the current one's "done when" checks pass, not by the calendar. Each step has an owner, a time box and a "done when" check, so you can tell where you are. Expect about 6 to 8 hours of the rule book owner's time in total, and under an hour each for everyone else.

You can go faster. Do not skip step 2: a rule book with empty `profile.md`, `goals.md` and `metrics.md` gives generic answers, and leaders stop asking.

## Roles

| Role | Who | Time |
|---|---|---|
| **Sponsor** | CTO or VP Engineering | 1 hour in phase 1, 30 minutes in phase 3 |
| **Rule book owner** | A director, chief of staff or platform lead who can get answers from the leadership team | 6 to 8 hours across the four phases, then about 1 hour a month |
| **Pilot leaders** | 3 to 5 people: one director, two or three engineering managers, one platform or product lead | 30 minutes to install, then normal use |
| **File owners** | Whoever owns each document (goals, metrics, career framework…) | Review one draft each |

## Phase 1: Set up

### 1. Make the private copy (owner, 30 minutes)

- [ ] Create a private repository from this one: [docs/private-copy.md](private-copy.md). Do not fork: a fork of a public repository cannot be private.
- [ ] Give the sponsor and file owners write access. Protect `main` so changes go through pull requests.
- [ ] Install the skills for yourself: `./scripts/install.sh --target claude` (or your agent; see [docs/install.md](install.md)).

**Done when:** asking your agent *"What does our rule book say about code review?"* runs `ask-rulebook` and reports that `company/engineering-principles.md` is still a template.

### 2. Fill in the three core files (owner with sponsor, 2 to 3 hours)

Open the repository in your agent and run the `company-context` skill, one file at a time:

> *"Set up our rule book, starting with profile.md. Here's our org chart and team list: …"*
> *"Fill in goals.md from this OKR doc: …"*
> *"Fill in metrics.md. These are the metrics we agreed to track: …"*

- [ ] `company/profile.md`: teams, size, products, tooling.
- [ ] `company/goals.md`: this period's goals, and what you are explicitly not doing.
- [ ] `company/metrics.md`: two to four metrics per goal, each with a definition, owner and where it lives.
- [ ] Sponsor reviews `goals.md` and `metrics.md`, in a 30-minute session or a pull request review.
- [ ] Each file has `status: current`, an `owner` and today's `last_reviewed`.

**Done when:** `python3 scripts/validate.py` passes, and *"What are our engineering goals this quarter, and how do we measure them?"* gets an answer that cites `goals.md` and `metrics.md` and that the sponsor agrees with.

### 3. Connect live data and pull your teams (owner, 30 minutes, optional)

- [ ] Add the Swarmia MCP server ([docs/install.md](install.md#optional-live-data)).
- [ ] Ask *"Pull our teams from Swarmia"* (`pull-teams`). Review the result, add missions and ownership for the main teams, and declare the attributes you track (role, seniority…).

**Done when:** *"Run a Build scorecard for last quarter"* rates groups from data instead of asking self-assessment questions, and `company/team-structure.md` lists your teams with a mission for each.

## Phase 2: Deepen

### 4. Add how you work (owner with file owners, 2 hours)

- [ ] `company/engineering-principles.md`: review, testing, release, on-call, AI tool use and working agreements.
- [ ] `company/culture.md`: values, how decisions get made, feedback norms.
- [ ] `company/surveys/`: your last one or two developer experience surveys, aggregated, comments paraphrased, with what you did about them.
- [ ] `company/glossary.md`: team names, product names and acronyms that come up in phases 1 and 2.

Templates and what never goes in: [docs/company-context.md](company-context.md).

**Done when:** *"How should we handle the growing review load from AI-generated PRs?"* gets an answer from `build-coach` that cites one of your principles or survey themes, not only the Build book.

### 5. Choose your trusted sources (sponsor and owner, 45 minutes)

- [ ] Review the three shipped defaults in `company/sources/` (Swarmia help center, DORA, SPACE). Set the ones you trust to `status: current` with an owner. Delete the rest.
- [ ] Add up to five more that your leadership actually refers to: research, reports, books, manifestos, internal reports. Ask the agent: *"Add this report as a trusted source: <link>"*.
- [ ] For each, agree on `authority`: `reference` by default, `benchmark` only for research with published numbers, `policy` only if you formally adopted it.

**Done when:** every `current` source has an owner and a `use_for`, the list fits on one screen, and the sponsor would defend each entry in a leadership meeting.

## Phase 3: Pilot

### 6. Install for the pilot group (pilot leaders, 30 minutes each)

- [ ] Each pilot leader installs the skills ([docs/install.md](install.md)) and connects Swarmia if you use it.
- [ ] Share a starter list of questions with them:
  - *"What are our goals this quarter and which metrics track them?"* (`ask-rulebook`)
  - *"My team's reviews are slow. What should we try?"* (`build-coach`)
  - *"Where do we stand on the Build framework?"* (`build-scorecard`)
  - *"What did the last survey say, and did we act on it?"* (`ask-rulebook`)

### 7. Collect gaps for a week (owner, 15 minutes a day)

- [ ] Ask pilot leaders to post every answer that was wrong, generic or flagged a missing file in one shared channel or doc.
- [ ] Sort each into: missing or stale company file, wrong company content, skill behaviour, or a new skill idea.
- [ ] Fix company content through pull requests. Run `python3 scripts/sync_shared.py`, `python3 scripts/validate.py` and re-install after each merge (or use `install.sh --link` so a `git pull` is enough).

**Done when:** pilot leaders use it at least weekly without being reminded, and the last few days produced no new "missing file" gaps.

## Phase 4: Roll out

### 8. Open it to all leaders (sponsor and owner, 1 hour)

- [ ] Sponsor announces it: what it is for, the starter questions, where to report bad answers, and that it never ranks or assesses individuals.
- [ ] Distribute: plugin marketplace from your private repository, or zips from an admin ([docs/install.md](install.md)).
- [ ] Book the recurring upkeep below in the owner's calendar.

**Done when:** most engineering leaders have it installed, and two different leaders asking the same question get answers built on the same files.

## Keep it current

| When | What | Owner |
|---|---|---|
| Monthly, 30 minutes | Ask *"Audit our rule book"*. Fix the top three items it reports. | Rule book owner |
| Start of each planning period | Update `goals.md` and check `metrics.md` still serves it | Sponsor |
| After every survey | Add a file in `surveys/` and, later, what you did about it | Survey owner |
| After a reorg or team change | Edit the team folders in `company/teams/` in a pull request, merge, then ask *"Push our teams to Swarmia"* | Rule book owner |
| After a leadership decision | Ask *"Record this decision"* | Whoever made it |
| Every six months | Review each trusted source: still current, still trusted? | Rule book owner |
| When upstream changes | Pull updates: [docs/private-copy.md](private-copy.md#pulling-upstream-updates) | Rule book owner |

## When something goes wrong

| Symptom | Likely cause | Fix |
|---|---|---|
| Answers are generic, no file citations | Core files still templates, or skills not re-installed after edits | Fill in step 2; sync, validate and re-install |
| The skill does not trigger | Not installed for that agent, or the question is far from the skill's description | Check the install target; ask more directly (*"Use build-coach: …"*) |
| Answer contradicts what leadership agreed | The decision is not in the rule book, or two files disagree | Record it in `decisions/`; ask *"Audit our rule book"* for contradictions |
| `validate.py` fails on privacy | A file holds an email address, token or quoted survey comment | Remove or paraphrase it; the rule book holds aggregates only |
| Book or source links fail | The agent has no web access | Enable web access for the agent; skills read the Build book and trusted sources on the web |
