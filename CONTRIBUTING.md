# Contributing

Thanks for helping improve SEI OS. This repository is the **upstream starter**: skills, scripts, the Build framework, links into the Build book, benchmarks and docs. Organizations keep their own rule book in a private copy ([docs/private-copy.md](docs/private-copy.md)).

## What belongs here

- Fixes and improvements to skills in `skills/`, to `scripts/`, `shared/` and `docs/`.
- New skills that are useful to most organizations and work from the rule book alone (live data optional).
- Corrections to `knowledge/` with a source: a Build framework or book URL, or a published benchmark.
- Better templates in `company/`.

## What never belongs here

- **Your organization's content.** Files under `company/` stay `status: template` upstream. CI fails if a pull request fills one in.
- Personal data, individual ratings, compensation, raw survey comments, credentials or real organization ids, anywhere in the repository, including examples and `company/teams/` (which holds a roster only in private copies). Example data must say it is fictional.
- Verbatim passages from the *Build* book. The book is not in this repository; `knowledge/build-concepts.md` only links to it. Do not add definitions or summaries of the book there. Quote under 15 words with a link to the web edition.

## How to make a change

1. Branch from `main`. If you work from a private copy, branch from `upstream/main` so none of your `company/` changes come along.
2. Edit sources, never generated copies: change `company/`, `knowledge/` or `shared/`, not the copies under `skills/*/references/`, `skills/*/assets/` or `skills/*/scripts/`. New shared files go into a bundle in `catalog.json`.
3. Run:

   ```bash
   python3 scripts/sync_shared.py
   python3 scripts/validate.py --upstream
   ```

   Both need only Python 3.9+ and the standard library.
4. For a new or changed skill, follow [docs/writing-skills.md](docs/writing-skills.md) and test it in at least one agent with three phrasings of the question it should trigger on. Say which agent in the pull request.
5. Open a pull request. Keep it to one change; describe the question the skill answers or the bug it fixes.

## Style

Plain, specific, numbers first. "Engineering effectiveness" for the whole system. No hype, no emoji in skill bodies. Teams and systems, never individuals. See [AGENTS.md](AGENTS.md).

## License

By contributing you agree that your contribution is licensed under the [Apache License 2.0](LICENSE), as described in its section 5.

`knowledge/build-framework.md` and `knowledge/build-concepts.md` hold only the structure, names and links of the Build framework and book, which are © Swarmia Oy (see [NOTICE](NOTICE)). Keep them that way: do not paste text from the framework page or the book into this repository.

## Conduct

This project follows the [Code of Conduct](CODE_OF_CONDUCT.md).
