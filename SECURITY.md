# Security

## Reporting a vulnerability

Please report security issues privately through GitHub: **Security → Report a vulnerability** on this repository. Do not open a public issue. We aim to acknowledge reports within three working days.

In scope: the scripts in `scripts/` and `shared/`, the HTML report template, the install script, and any skill instruction that could cause an agent to leak data or take an action the user did not ask for.

Out of scope: the Swarmia product and MCP server (report those to Swarmia directly), and agent clients themselves.

## How this repository handles data

- Nothing here sends data anywhere. Reports render to local files in the git-ignored `sei-reports/` folder, with no CDN or tracking.
- `.mcp.json` declares the optional Swarmia MCP server for the Claude Code plugin. Remove it if you do not use Swarmia.
- `scripts/validate.py` blocks obvious personal data and credentials in `company/`, but review is the real guard. Keep your filled-in copy private ([docs/private-copy.md](docs/private-copy.md)).
