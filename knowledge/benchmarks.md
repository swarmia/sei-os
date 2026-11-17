# Benchmarks

Reference bands for reading engineering metrics. Use them as **directional guidance**, never as targets to optimise blindly, and always next to the organization's own baseline and team-to-team spread.

Sources: [swarmia.com/benchmarks](https://www.swarmia.com/benchmarks/), the Swarmia help center ([Benchmarks & comparisons](https://help.swarmia.com/guides/benchmarks-and-comparisons)), and the [Build framework](https://www.swarmia.com/framework/) (customer percentiles, Q2 2026). Refresh this file when those pages change.

## Delivery and code review

| Metric | Great | Good | Needs attention | Notes |
|---|---|---|---|---|
| PR cycle time | < 24 hours | < 5 working days | ≥ 5 working days | First commit → merged. Includes draft time unless excluded. Benchmark is for a typical PR: read the median, not the average. |
| Time to first review | ≤ 4 hours | ≤ 24 hours | > 24 hours | Weekends excluded in Swarmia's definition. Undefined for never-reviewed PRs. |
| Time to merge (after approval) | ≤ 4 hours | ≤ 24 hours | > 24 hours | |
| Review rate | ≥ 90% | ≥ 80% | < 80% | Share of merged PRs that got a review. |
| Batch size (lines changed) | < 200 | < 500 | ≥ 500 | Excludes generated files. Bigger PRs stretch cycle and review time on their own. |
| Flow efficiency (issues) | > 95% active | > 70% | < 70% | Share of in-progress days an issue was actively worked on. |

## DORA and deployment

| Metric | Great | Good | Needs attention | Notes |
|---|---|---|---|---|
| Deployment frequency | Continuously (≥ 10 / week) | Daily (≥ 5 / week) | Less than daily | Production only. Check for apps that always deploy together. |
| Change lead time | < 24 hours | < 5 working days | ≥ 5 working days | First commit → running in production. |
| Time to deploy | < 15 min | < 60 min | ≥ 60 min | Merge → production. |
| Change failure rate | < 5% | < 15% | ≥ 15% | Say how many failures the rate rests on. Empty (not 0%) when no failures are detected. |
| Mean time to recovery | < 1 hour | < 3 hours | ≥ 3 hours | Rare events: use a quarter, not a month. |

## Investment balance (Balance framework)

Swarmia's default balance framework splits effort (FTE) into **New things**, **Improving things**, **Productivity**, and **Keeping the lights on (KTLO)**.

| Signal | Great | Good | Needs attention |
|---|---|---|---|
| KTLO share | ~10% | ~30% | ~50% |
| Productivity share | ~15% | ~10% | < 10% |
| New + Improving combined | ~60% | | |
| Uncategorized effort | < 5% | < 10% | > 10% (fix data before reading the rest) |

A deliberate balance beats a maximum. A KTLO share bending back up after a heavy shipping period is usually rework surfacing: check bugs and incidents before concluding.

## AI leverage (Build framework, Swarmia customers, Q2 2026)

| Metric | p75 (top quartile) | p90 (top decile) | n |
|---|---|---|---|
| Share of merged PRs that are AI-assisted | 82% | 90% | 352 orgs |
| Share of merged PRs authored by autonomous agents | 3.9% | 12% | 486 orgs |
| Share of merged PRs with AI-assisted review | | 88% | 719 orgs |
| AI spend per developer | | ~5× a typical org; 10–20% of fully loaded headcount cost | |

More autonomy is not automatically better. It should be task-appropriate and tracked next to delegation failures (agent work abandoned or rewritten by a human).

## How to use benchmarks responsibly

1. **Baseline first.** Report the org's own value and the prior period before the benchmark band.
2. **Spread beats benchmark.** The gap between the fastest and slowest team shows what is already possible in this org's context. Close that gap before chasing an external number.
3. **Medians for durations.** A few long-running items pull averages up. Quote P50 and, when the tail matters, P90.
4. **Sample size.** State `n` behind every rate. Fewer than ~20 items (or fewer than ~5 failures for CFR) is an anecdote, not a trend.
5. **Like for like.** Compare PRs of similar size when comparing groups (AI vs non-AI, reviewed vs not, agent vs human).
6. **Label, don't rank.** Use "great / good / needs attention" and "fastest / slowest team", never "best / worst".

## Rules of thumb from the Build book

The book deliberately sets few hard numbers. These are the ones it does give (for context, see `build-concepts.md` or [the book](https://www.swarmia.com/build/)):

| Topic | Guidance |
|---|---|
| Investment mix | At least ~10% of effort on productivity; KTLO 10–30%. KTLO persistently above 30% signals a structural problem (debt, ownership, team sized wrong for what it owns). |
| Investment review cadence | Quarterly at org level; monthly or per sprint at team level. A deliberate shift should show within one or two quarters. |
| WIP | Starting limit for roadmap items: number of developers ÷ 2. WIP above team headcount is a warning sign. |
| Utilization | Plan for 75–85%, never 100%: full utilization slows teams down and stretches cycle time. |
| Focus time | At least 4 hours of uninterrupted focus on 4 days a week per engineer. A 30-minute gap between meetings is not coding time. |
| Flow efficiency | 15–40% is typical on first measurement. |
| Code review | A PR that waits a day or more for pickup is a bottleneck. |
| CI | A 20% CI failure / flaky-test rate is a good first thing to fix; getting to ~2% speeds every team up. |
| Team size | 5–7 engineers per team remains healthy with AI. |
| Surveys | Beyond ~10 engineers, set up intentional feedback mechanisms. Overview survey quarterly, 5–7 point Likert scale. |
| OKR overhead | Under one week per quarter per team. |
