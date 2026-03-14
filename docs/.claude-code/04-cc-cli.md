# CLI Commands & Flags

---
title: Claude Code CLI Reference — Essential Commands and Flags
path: 01-basic
type: reference
audience: [All Developers]
last_verified: 2026-03-14
order: 4
source: https://code.claude.com/docs/en/cli-usage
---

## Core Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `claude` | Start interactive session | `claude` |
| `claude "query"` | Start with initial prompt | `claude "explain this project"` |
| `claude -p "query"` | Non-interactive (print mode) | `claude -p "list API endpoints"` |
| `cat file \| claude -p` | Process piped content | `cat logs.txt \| claude -p "explain"` |
| `claude -c` | Continue most recent session | `claude -c` |
| `claude -r "name"` | Resume session by name/ID | `claude -r "auth-refactor"` |
| `claude update` | Update to latest version | `claude update` |
| `claude auth login` | Log in to Anthropic | `claude auth login --sso` |
| `claude agents` | List all configured subagents | `claude agents` |
| `claude mcp` | Configure MCP servers | `claude mcp add` |

---

## Essential Flags

### Session Management

| Flag | Purpose | Example |
|------|---------|---------|
| `--continue, -c` | Resume most recent session | `claude -c` |
| `--resume, -r` | Resume by name or show picker | `claude -r auth-refactor` |
| `--name, -n` | Name the session | `claude -n "my-feature"` |
| `--fork-session` | Fork when resuming | `claude -r abc --fork-session` |
| `--from-pr` | Resume sessions linked to PR | `claude --from-pr 123` |

### Model & Effort

| Flag | Purpose | Example |
|------|---------|---------|
| `--model` | Set model (sonnet/opus/full ID) | `claude --model opus` |
| `--effort` | Set effort (low/medium/high/max) | `claude --effort high` |

### Output & Input

| Flag | Purpose | Example |
|------|---------|---------|
| `--print, -p` | Non-interactive print mode | `claude -p "query"` |
| `--output-format` | text / json / stream-json | `claude -p --output-format json "query"` |
| `--json-schema` | Validated JSON output | `claude -p --json-schema '{...}' "query"` |
| `--verbose` | Full turn-by-turn output | `claude --verbose` |

### Permission Controls

| Flag | Purpose | Example |
|------|---------|---------|
| `--permission-mode` | Set mode (default/plan/acceptEdits) | `claude --permission-mode plan` |
| `--allowedTools` | Tools that skip permission prompts | `--allowedTools "Bash(git *)" "Read"` |
| `--disallowedTools` | Tools removed from context | `--disallowedTools "Edit"` |
| `--tools` | Restrict available tools | `--tools "Bash,Read"` |

### System Prompt

| Flag | Purpose | Example |
|------|---------|---------|
| `--system-prompt` | Replace entire system prompt | `claude --system-prompt "You are a Python expert"` |
| `--append-system-prompt` | Append to default prompt | `claude --append-system-prompt "Always use TypeScript"` |
| `--system-prompt-file` | Replace with file contents | `claude --system-prompt-file ./review.txt` |

### Advanced

| Flag | Purpose | Example |
|------|---------|---------|
| `--worktree, -w` | Start in isolated git worktree | `claude -w feature-auth` |
| `--add-dir` | Add extra working directories | `claude --add-dir ../apps ../lib` |
| `--agent` | Use specific agent | `claude --agent my-agent` |
| `--max-turns` | Limit agentic turns (print mode) | `claude -p --max-turns 3 "query"` |
| `--max-budget-usd` | Cap API spend (print mode) | `claude -p --max-budget-usd 5.00 "query"` |
| `--chrome` | Enable Chrome browser integration | `claude --chrome` |
| `--ide` | Auto-connect to IDE | `claude --ide` |
| `--debug` | Enable debug logging | `claude --debug "api,mcp"` |

---

## In-Session Commands

| Command | Purpose |
|---------|---------|
| `/help` | Show all available commands |
| `/clear` | Reset context window |
| `/compact [instructions]` | Manually compact context |
| `/init` | Generate starter CLAUDE.md |
| `/memory` | Browse/toggle memory files |
| `/model` | Switch model mid-session |
| `/effort` | Adjust effort level |
| `/hooks` | Browse configured hooks |
| `/agents` | Manage subagents |
| `/permissions` | Manage tool permissions |
| `/resume` | Switch to different session |
| `/rename` | Rename current session |
| `/rewind` | Restore to checkpoint |
| `/context` | View loaded context |
| `/config` | Toggle settings |

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Esc` | Stop current action (context preserved) |
| `Esc + Esc` | Open rewind menu |
| `Shift+Tab` | Cycle permission modes |
| `Ctrl+G` | Open plan in editor |
| `Ctrl+O` | Toggle verbose mode |
| `Ctrl+B` | Background current task |
| `Ctrl+T` | Toggle task list (agent teams) |
| `Option+T` / `Alt+T` | Toggle thinking mode |
| `Shift+Down` | Cycle teammates (agent teams) |

---

## Non-Interactive Patterns

```bash
# One-off query
claude -p "Explain what this project does"

# Structured JSON output
claude -p "List all API endpoints" --output-format json

# Streaming for real-time processing
claude -p "Analyze this log file" --output-format stream-json

# Piped input
cat data.csv | claude -p "summarize this data" > summary.txt

# CI/CD linting
claude -p "review changes vs main for security issues" --output-format json
```

---

## Next Steps

- **05-cc-workflows.md** → Common development workflows
- **09-cc-context.md** → Deep dive into context management (intermediate)
