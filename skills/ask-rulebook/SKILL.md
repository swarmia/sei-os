---
name: ask-rulebook
description: Answers questions about how this organization works from its own rule book (goals, key metrics and their definitions, engineering principles and working agreements, culture, career framework and review process, past survey results, leadership decisions, glossary), citing the file each answer comes from, flagging gaps, stale files and contradictions, and pointing to the Build book only where the rule book is silent. Use when someone asks "what are our goals this quarter", "how do we define cycle time", "what's our review policy", "what does a senior engineer do here", "how do performance reviews work", "what did the last survey say", "why did we decide…", "what does <internal term> mean", or is new and wants to know how things work here.
license: Apache-2.0
compatibility: Works without any data connection.
metadata:
  pillar: foundation
  roles: cto director em platform pm
---

# Ask the rule book

The organization's answer to "how do we do things here?", from what it has written down and agreed. Useful for new leaders, for settling "what did we agree?" and for spotting where the rule book needs work.

## Sources

- `references/company/`: every file. Frontmatter carries `status`, `owner` and `last_reviewed`.
- `references/build-concepts.md` and `references/build-framework.md`: only as a fallback, clearly labelled as general guidance, not company policy. Read the guidance itself on the web (the book sections `build-concepts.md` links to, the framework at https://www.swarmia.com/framework/) and cite the section.
- `references/answer-contract.md`: rules every answer follows.

## Workflow

1. **Find the relevant files.** Start from `references/company/README.md` for the map, then read the files the question touches in full. Search the whole folder for the key terms and their synonyms in `glossary.md`.
2. **Check freshness.** For each file you use: if `status: template`, treat it as missing; if `last_reviewed` is more than six months ago, use it but say so; if no owner, note it.
3. **Answer from the rule book.** Lead with the direct answer, in the organization's own words. Cite every statement with its file path (and heading). When files disagree, show both and name the owner to resolve it.
4. **When the rule book is silent**, say so plainly. Then, if helpful, check `references/company/sources/` for a `current` source whose `use_for` covers the question and read it at its URL, or give the Build book's general guidance, labelled "General guidance, not company policy", with its web link, and name the file and owner that should hold the answer.
5. **Offer the follow-up**: `build-coach` when the user wants a recommendation rather than a lookup, or a drafted addition to the right `company/` file when the gap is worth closing.

## Output

- **Answer**: two to five sentences or a short list.
- **Sources**: the files and headings used, with owner and last review date.
- **Gaps**: missing, template or stale files that would change the answer.

## Rules

- Never invent company policy. "The rule book does not say" is a complete answer.
- Career framework questions are about roles and process. Do not assess a named person against it.
- Survey results stay aggregated and paraphrased, as written in `surveys/`.
- Do not edit `company/` files unless the user asks; then draft the change for review.
