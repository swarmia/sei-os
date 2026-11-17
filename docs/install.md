# Install

Skills are plain folders (`SKILL.md` plus `references/`, `scripts/`, `assets/`) in the open [Agent Skills](https://agentskills.io) format. `scripts/install.sh` copies them where each agent looks. Each installed skill carries its own copy of `company/`, so **re-run the install (or update the plugin) after every rule book change**.

## Skills

| Agent | Command |
|---|---|
| Claude Code (plugin) | `/plugin marketplace add swarmia/sei-os` then `/plugin install sei-os@swarmia` (or your private copy: `/plugin marketplace add <your-org>/<your-repo>`) |
| Claude Code (files) | `./scripts/install.sh --target claude` (or `--project .` for one project) |
| Claude Desktop / claude.ai | Zip each skill folder and upload under Settings → Capabilities → Skills, or have an org admin provision them |
| OpenAI Codex | `./scripts/install.sh --target codex` |
| Gemini CLI | `./scripts/install.sh --target gemini` |
| GitHub Copilot | `./scripts/install.sh --target copilot` (or `--project <repo>` for `.github/skills`) |
| Cursor | `./scripts/install.sh --target cursor` |
| Anything else | `./scripts/install.sh --dir <path>` |

`--link` symlinks instead of copying, so a `git pull` updates the skills in place. `--only build-coach,ask-rulebook` installs a subset.

Zips for Claude Desktop and claude.ai:

```bash
mkdir -p dist && cd skills && for s in */; do (cd "$s" && zip -qr "../../dist/${s%/}.zip" . -x '.sei-shared'); done
```

Once your private copy is filled in, the plugin marketplace needs access to it: each person signs in to GitHub, or an admin distributes the zips.

## Optional: live data

Every skill works without a data connection, from the rule book, the Build framework and the Build book's web edition (so agents need web access). Connecting a metrics source lets `build-coach` check advice against numbers and lets `build-scorecard` rate groups from data instead of self-assessment.

The [Swarmia MCP server](https://help.swarmia.com/settings/integrations/mcp-server) is `https://app.swarmia.com/api/v1/mcp`. Claude Code:

```bash
claude mcp add swarmia --transport http https://app.swarmia.com/api/v1/mcp
```

The Claude Code plugin declares it in `.mcp.json`. For other clients, add the same URL as a remote HTTP MCP server; clients without OAuth use a Swarmia API token with the MCP scope (Swarmia → Settings → API tokens) as a bearer token. Remove `.mcp.json` if you do not use Swarmia.

## Verify

Ask your agent: *"What does our rule book say about code review?"* The `ask-rulebook` skill should trigger. On a fresh copy it will report that `company/engineering-principles.md` is still a template, which is the expected answer.
