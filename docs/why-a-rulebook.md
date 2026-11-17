# Why one rule book beats a hundred prompts

Most engineering organizations already use AI assistants for leadership work: drafting a board update, preparing a retro, making sense of a survey, deciding whether to split a team. Each leader writes their own prompt, pastes in whatever context they remember, and gets an answer. That works for one person once. It does not work for an organization.

This repository is the alternative: **one shared rule book** (your company context, the Build framework, an answer contract) and **shared skills** (tested workflows for recurring questions) that every leader's agent loads the same way.

## What goes wrong with one-shot prompts

| Problem | What it looks like |
|---|---|
| **Every answer starts from zero.** | Each prompt carries only the context its author remembered to paste. The agent does not know your goals, your teams, what "done" means here, or that you tried a review rota last year and dropped it. |
| **Same question, different answers.** | Two directors ask "how is delivery going?" with different prompts, get different metrics, different timeframes and different definitions, and spend the next meeting arguing about the numbers instead of the decision. |
| **Generic advice.** | Without your culture and constraints, the agent imports someone else's playbook: the advice that fits a 2,000-person company lands on a 60-person one. |
| **Invisible guardrails.** | Whether an answer ranks individual engineers, quotes survey comments, or invents a benchmark depends on whoever wrote the prompt that day. |
| **Nothing improves.** | A good prompt lives in one person's notes. A mistake gets made again by the next person. There is no review, no history, no owner. |
| **Stale context.** | Pasted goals and metrics are whatever version was in someone's clipboard. Nobody knows which answer was based on last quarter's plan. |

## What a shared rule book changes

**Context is written once and maintained.** Goals, metrics, principles, culture, career framework and survey history live in `company/`, each with an owner and a review date. Every skill reads them. When the goals change, one file changes and every answer after that uses the new goals.

**Recurring questions get a tested workflow.** A skill is a short, reviewed playbook for one question: which sources to read, in what order, how to compare, what to watch out for, what shape the answer takes. The Build scorecard runs the same way for every leader, every quarter, so this quarter's result is comparable to last quarter's.

**Guardrails are part of the system, not the prompt.** The answer contract (`knowledge/answer-contract.md`) applies to every skill: teams not individuals, a comparison and a sample size behind every number, no invented benchmarks, paraphrased survey comments, ask before acting, a "How this was calculated" block. Nobody has to remember to ask for it.

**Shared vocabulary.** The Build framework gives every leader the same map (AI leverage, Effectiveness, Return on engineering) and the book gives the reasoning. Your glossary adds your own words. Conversations get shorter because the terms mean the same thing to everyone.

**It improves through review.** Skills and context are files in a repository. A leader who finds a better way to prepare a retro opens a pull request; once merged, every agent in the organization uses it. Mistakes get fixed once.

**It works in every agent.** Skills use the open [Agent Skills](https://agentskills.io) format, so the same rule book works in Claude, Codex, Gemini CLI, GitHub Copilot and Cursor. People keep the tool they prefer; the organization keeps one source of truth.

## A concrete example

A new engineering manager asks: *"My team's PRs wait too long for review. What should we do?"*

**One-shot prompt.** The agent suggests generic fixes: a review SLA of four hours, a review rota, smaller PRs. Two of these the organization already tried; one conflicts with an agreed principle. The manager does not know that.

**With the rule book.** The `build-coach` skill reads `company/engineering-principles.md` (review expectation: first review within one working day, owners review), `company/decisions/` (the 2025 review rota was dropped because it pulled seniors out of focus time), `company/metrics.md` (time to first review is a tracked metric with a baseline) and the latest file in `company/surveys/` (review waits were the second-lowest score). It answers with the Build book's reasoning, inside the organization's own agreements, avoids the experiment that already failed, and names the metric the organization already watches.

Same agent, same model. The difference is the context and the workflow.

## What this is not

- **Not a replacement for judgement.** Skills prepare the evidence and the options. Leaders decide.
- **Not a performance-management tool.** The rule book describes roles, systems and teams. It never scores people.
- **Not a dumping ground.** A short, current rule book beats a complete, stale one. Link out to full documents; keep the files here to what an agent needs to answer well.

## Getting started

1. Copy this repository into a **private** repository for your organization ([docs/private-copy.md](private-copy.md); a GitHub fork of a public repository cannot be private).
2. Fill in `company/`, starting with `profile.md`, `goals.md` and `metrics.md` (an hour is enough for a first version). Or ask the `company-context` skill to interview you.
3. Sync, validate and install the skills for your leadership team (see the README).
4. Pick one recurring question your team asks every month and write a skill for it ([writing-skills.md](writing-skills.md)).
5. Review the rule book quarterly, with your planning cycle.
