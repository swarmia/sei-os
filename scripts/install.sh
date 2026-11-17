#!/usr/bin/env bash
# Install SEI OS skills into one or more AI agents' skill directories.
#
#   ./scripts/install.sh                      # Claude Code, user level (~/.claude/skills)
#   ./scripts/install.sh --target codex       # Codex (~/.codex/skills)
#   ./scripts/install.sh --target all         # every supported agent
#   ./scripts/install.sh --target copilot --project ~/code/app   # project level (.github/skills)
#   ./scripts/install.sh --link               # symlink instead of copy (stays current with git pull)
#   ./scripts/install.sh --only build-coach,ask-rulebook
#   ./scripts/install.sh --uninstall --target all
#
# Directories follow each client's documented skills location at the time of writing.
# If your client version uses another path, pass --dir <path>.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGETS="claude"
PROJECT=""
MODE="copy"
ONLY=""
DIR=""
UNINSTALL=0

usage() { sed -n '2,14p' "$0" | sed 's/^# \{0,1\}//'; exit "${1:-0}"; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target) TARGETS="$2"; shift 2 ;;
    --project) PROJECT="$2"; shift 2 ;;
    --link) MODE="link"; shift ;;
    --only) ONLY="$2"; shift 2 ;;
    --dir) DIR="$2"; shift 2 ;;
    --uninstall) UNINSTALL=1; shift ;;
    -h|--help) usage 0 ;;
    *) echo "Unknown option: $1" >&2; usage 1 ;;
  esac
done

[[ "$TARGETS" == "all" ]] && TARGETS="claude,codex,gemini,copilot,cursor,agents"

dir_for() {
  local t="$1"
  if [[ -n "$PROJECT" ]]; then
    case "$t" in
      claude)  echo "$PROJECT/.claude/skills" ;;
      codex)   echo "$PROJECT/.codex/skills" ;;
      gemini)  echo "$PROJECT/.gemini/skills" ;;
      copilot) echo "$PROJECT/.github/skills" ;;
      cursor)  echo "$PROJECT/.cursor/skills" ;;
      agents)  echo "$PROJECT/.agents/skills" ;;
      *) return 1 ;;
    esac
  else
    case "$t" in
      claude)  echo "$HOME/.claude/skills" ;;
      codex)   echo "${CODEX_HOME:-$HOME/.codex}/skills" ;;
      gemini)  echo "$HOME/.gemini/skills" ;;
      copilot) echo "$HOME/.copilot/skills" ;;
      cursor)  echo "$HOME/.cursor/skills" ;;
      agents)  echo "$HOME/.agents/skills" ;;
      *) return 1 ;;
    esac
  fi
}

skills=()
for d in "$ROOT"/skills/*/; do
  name="$(basename "$d")"
  if [[ -n "$ONLY" && ",$ONLY," != *",$name,"* ]]; then continue; fi
  skills+=("$name")
done
[[ ${#skills[@]} -eq 0 ]] && { echo "No skills matched." >&2; exit 1; }

IFS=',' read -r -a target_list <<< "$TARGETS"
for t in "${target_list[@]}"; do
  if [[ -n "$DIR" ]]; then dest="$DIR"; else dest="$(dir_for "$t")" || { echo "Unknown target: $t" >&2; exit 1; }; fi
  mkdir -p "$dest"
  for s in "${skills[@]}"; do
    if [[ $UNINSTALL -eq 1 ]]; then
      rm -rf "${dest:?}/$s"
      continue
    fi
    rm -rf "${dest:?}/$s"
    if [[ "$MODE" == "link" ]]; then
      ln -s "$ROOT/skills/$s" "$dest/$s"
    else
      cp -R "$ROOT/skills/$s" "$dest/$s"
      rm -f "$dest/$s/.sei-shared"
    fi
  done
  verb=$([[ $UNINSTALL -eq 1 ]] && echo "Removed" || echo "Installed")
  echo "$verb ${#skills[@]} skills ($MODE) → $dest  [$t]"
  [[ -n "$DIR" ]] && break
done

if [[ $UNINSTALL -eq 0 ]]; then
  cat <<'EOF'

Skills carry a copy of company/. After editing it, run scripts/sync_shared.py and install again.
Optional: connect a metrics source such as the Swarmia MCP server (see docs/install.md).
Then ask, for example: "What are our engineering goals this quarter?" or "Run a Build scorecard."
EOF
fi
