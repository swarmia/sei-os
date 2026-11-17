# Build framework: structure and where to read it

**What this is.** The shared map of Swarmia's [Build framework](https://www.swarmia.com/framework/): its three pillars, nine metric groups and the metrics in each, with a one-line note in our own words. It holds structure, names and links only. The framework's text is not in this repository: read it on the web, at https://www.swarmia.com/framework/.

**How to use it.**
1. Use the pillar, group and metric names below as shared vocabulary, and to place a question or a skill in the framework.
2. For the reasoning behind a group, its "questions to ask" or its recommendations, fetch https://www.swarmia.com/framework/ and read the matching section ("Part 2: Effectiveness, 2.1 Developer productivity"). Do not answer from these one-line notes alone when the leader wants the framework's guidance.
3. Cite the framework by section and URL. Paraphrase; quote only short named concepts (under 15 words).
4. Quote numbers only from `benchmarks.md`. It carries the framework's customer percentiles.
5. If the web page is unreachable, say so, answer from the structure here, and label the answer as working from the outline only.

**Companion:** `build-concepts.md` maps the [*Build* book](https://www.swarmia.com/build/), the reasoning behind the framework.

**Last checked against the web page:** 2026-11-13. When the page adds, removes or renames a pillar, group or metric, update this file and run `python3 scripts/sync_shared.py`.

## How the framework is meant to be read

- Start from the organization's own baseline, not an external target.
- Read the three pillars together. A gain in one (more AI-assisted PRs) means little without the others (quality holding, effort moving to new work).
- Treat return on engineering as the result of changing how the organization works, not the first number to optimize.
- Then pick one problem, work on it, and repeat.

## 1. AI leverage

Whether the organization gives AI tools and agents the conditions to succeed.

### 1.1 AI adoption

| Metric | Note |
|---|---|
| License adoption | Engineers with an AI seat, overall and per tool. |
| Active usage (DAU/WAU) | Engineers using AI tools daily and weekly. |
| Share of AI-assisted pull requests | Merged PRs with AI involvement; split by tool to see which tools earn their seats. |

### 1.2 AI readiness

| Metric | Note |
|---|---|
| Agent configuration maturity | Repositories rated low, medium or high on agent instructions (AGENTS.md, CLAUDE.md, docs, skills). |
| CI/CD pipeline health | Build time, failure rate and test flakiness; agents run pipelines far more often than people. |
| Custom agent environments | Whether purpose-built agent harnesses exist, and the share of changes made through them. |

### 1.3 AI autonomy

| Metric | Note |
|---|---|
| Share of completed work delegated to autonomous agents | Merged work authored by agents running without step-by-step human input; split by autonomy level. |
| Complexity of delegated tasks | Whether delegated work is getting harder; read with delegation failures (agent work abandoned or rewritten). |

### 1.4 AI development culture

Assessed through conversation and surveys rather than a metric: spec-driven work vs. open-ended product problems, prototyping before prioritizing, cross-functional collaboration, product taste.

## 2. Effectiveness

Whether value is delivered faster, and whether the pace is sustainable.

### 2.1 Developer productivity

| Metric | Note |
|---|---|
| Throughput | Coding and issue throughput read together, since raw counts inflate with AI use. |
| Delivery (WIP, cycle time, batch size) | Where work slows down; batch size growth confounds before/after comparisons. |
| Code review | Time to first review, review load, AI-assisted review share, AI findings per PR. |

### 2.2 Quality and maintenance

| Metric | Note |
|---|---|
| New feature development vs. KTLO | Effort in FTEs on new work vs. maintenance, firefighting and rework. |
| Bug backlog, incidents, change failure rate | The fast-moving quality signals. |

### 2.3 Developer experience

| Metric | Note |
|---|---|
| Developer satisfaction | Survey measure across direction, focus, tooling, work management and system health. |
| Cognitive load | Mental overhead from context switching, unfamiliar tools and more actors in the system. |
| Organizational and system friction | Ease of release and release confidence. |

## 3. Return on engineering

What business value engineering investment produces.

### 3.1 Business outcomes

| Metric | Note |
|---|---|
| Investment in new feature development and productivity improvements | Effort in FTEs on new customer value and internal productivity. |
| Share of work linked to organizational initiatives | Planned work tied to initiatives or OKRs vs. reactive work. |
| Progress towards initiatives, initiative completion | Steady progress, completion and on-time delivery. |

### 3.2 Engineering cost

| Metric | Note |
|---|---|
| Combined engineering cost | Fully loaded headcount cost plus AI spend. |
| AI cost per FTE per month | Licenses plus model usage, total and as a share of cost. |
| Cost per unit of work | Combined cost per merged PR and per user story; look at outliers. |
