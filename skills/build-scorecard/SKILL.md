---
name: build-scorecard
description: Baselines an engineering organization across the Build framework's three pillars (AI leverage, Effectiveness, Return on engineering) and nine metric groups, using the organization's own metrics and survey history from its rule book, a short structured self-assessment with the leader, and live data when a metrics source such as Swarmia is connected; rates each group great / good / attention / unknown with the evidence behind it, picks the one or two problems worth working on first, and renders a shareable scorecard report. Use when a leader asks "where do we stand", "baseline us", "run the Build framework on us", "Build framework scorecard", "how effective is our engineering org", "what should we work on first", or prepares a quarterly engineering review.
license: Apache-2.0
compatibility: Works without any data connection (self-assessment mode). Uses the Swarmia MCP server when connected. Python 3 to render the HTML report; without it, answers in chat.
metadata:
  pillar: foundation
  roles: cto director
---

# Build scorecard

The Build framework says: start from your own baseline, read the three pillars together, pick one problem, work on it, repeat. This skill produces that baseline from whatever evidence exists, and is honest about which ratings rest on data and which on judgement.

Read `references/build-framework.md` first. Bands are in `references/benchmarks.md`; answer rules in `references/answer-contract.md`.

## Inputs

- Scope: the whole engineering organization (default) or one group of teams.
- Period: last full quarter vs the quarter before (default), as absolute dates.

## Workflow

1. **Read the rule book.** `references/company/profile.md` (teams, size, tooling), `goals.md`, `metrics.md` (baselines and targets you can use directly), the two latest files in `surveys/`, and `decisions/` for changes made during the period. Note which files are still templates.
2. **Pick the mode** and say it in one line:
   - **Data mode**: a metrics source is connected. Use the organization's key metrics first (`ListKeyMetrics` / `EvaluateKeyMetric` in Swarmia), then predefined reports (`EntityReport`, list the index first) for the groups not covered. Both periods, medians for durations, `n` for every rate.
   - **Self-assessment mode**: no live source. Use numbers from `company/metrics.md` and `surveys/`, then ask the leader the questions below for what is still missing.
   - Mixed is normal. Every rating records its evidence type: `data`, `rule book`, or `judgement`.
3. **Fill the gaps with questions.** Ask only for groups the rule book and data do not cover, in one message, at most nine questions, each answerable in a sentence. Use the framework's "questions to ask" per group, for example:
   - AI adoption: roughly what share of engineers use AI tools weekly; what share of merged work is AI-assisted?
   - AI readiness: how long does the main CI pipeline take, and how often does it fail for reasons unrelated to the change?
   - AI autonomy: what kinds of tasks are delegated to autonomous agents today, and how often is that work merged?
   - AI development culture: do teams write specs and prototype before building?
   - Developer productivity: typical time from first commit to production; where does work wait?
   - Quality and maintenance: share of effort on maintenance, firefighting and rework; incident trend?
   - Developer experience: latest survey score and change (if not in `surveys/`)?
   - Business outcomes: share of effort on the goals in `goals.md`; are initiatives on track?
   - Engineering cost: is AI spend known per engineer; is cost per unit of work tracked at all?
4. **Rate each group** `great` / `good` / `attention` / `unknown` against `benchmarks.md` where a band exists, else against the organization's own target in `metrics.md` and its trend. Every rating has a one-line headline with the number or the answer behind it, the comparison, `n` when it is data, and the evidence type. A judgement-only answer can support `good` or `attention`, never `great`. No evidence: `unknown`.
5. **Read the pillars together.** Look for the tensions the framework names: AI adoption up while CI or review strains; spend up faster than output; throughput up while maintenance or failures rise; new work squeezed. Cross-pillar stories are the findings.
6. **Check against the rule book.** Does the scorecard support or contradict the goals in `goals.md`? Did a recent survey theme or decision predict a finding? Say so.
7. **Pick one or two focus problems**: the biggest gap with the clearest lever, ideally tied to a goal. For each: why it matters (cite the framework or book section), the first experiment, the owner, the metric to watch.
8. **List the questions the evidence could not answer**, and the rule book file or data source that would answer them next time.
9. **Render** per `references/report-schema.md`: up to six KPI tiles; a `scorecard` chart with all nine groups (put the evidence type in each headline, for example "(self-assessed)"); one section per focus problem; a method block listing sources, which ratings are self-assessed, and every caveat. `assets/build-scorecard.json` is a complete sample to copy the structure from.
   `python3 scripts/render_report.py report-data.json sei-reports/<date>-build-scorecard/report.html`
10. **Chat reply:** the summary in three lines, the focus problems, the report path, and an offer to add the focus metrics to `company/metrics.md` and the scorecard summary to `company/decisions/` so next quarter starts from this baseline.

## Rules

- ROI is an outcome of changing how the organization works, not the first thing to optimise. Do not lead with cost.
- Team-level only. Team names are fine; individuals never appear.
- Do not rate a group `attention` on fewer than ~20 items or ~5 failures; say "too little data".
- Every rating cites its evidence. Self-assessed ratings are labelled as such in the report.
- Null is "not available", never zero. Reports go to `./sei-reports/`, which is git-ignored; never commit them.
