# CORTEX

**CO**gnitive **R**eal-**T**ime **EX**ecution System — AI-powered development orchestrator.

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/asifhussain60/CORTEX.git
cd CORTEX

# 2. Set up Python environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Configure git hooks (IMPORTANT for team collaboration)
make setup-hooks
# or: ./scripts/setup-hooks.sh
```

## Git Hooks

CORTEX uses automated verification hooks to ensure code quality:

| Hook | Trigger | Checks |
|------|---------|--------|
| `pre-commit` | Before commit | CORE-011 (type hints), CORE-013 (no bare except), CORE-028 (naming), CORE-038 (file placement) |
| `pre-push` | Before push | 12 production readiness checks including prompt-code synchronization |

**After cloning, run:**
```bash
make setup-hooks
```

This configures Git to use version-controlled hooks from `.cortex/hooks/`.

## Development Commands

```bash
make help          # Show all commands
make verify        # Run production readiness verification
make test          # Run wiring tests
make test-all      # Run all tests
```

## Documentation

- **[START HERE](docs/START-HERE.md)** - New to CORTEX? Begin here
- **[Getting Started](docs/03-getting-started/)** - Installation & setup
- **[CORTEX Brain](docs/01-cortex-brain/)** - Governance & knowledge system
- **[Orchestrators](docs/02-orchestrators/)** - 23 specialized coordinators
- **[LENS Protocol](docs/05-lens-protocol/)** - Code intelligence system
- **[LENS Dashboard](docs/11-lens-dashboard/)** - Visual intelligence (NEW ✨)
- **[Architecture](docs/04-architecture/)** - System design
- **[API Reference](docs/06-api-reference/)** - Complete API docs
- **[MCP Tools](docs/11-mcp-tools/)** - Model Context Protocol integration

### LENS Dashboard (Phase 14 - NEW ✨)

Generate interactive dashboards for any repository:

```bash
# Generate dashboard for current repository
cortex dashboard generate .

# Serve dashboard locally
cortex dashboard serve . --port 8080

# List generated dashboards
cortex dashboard list
```

**Features:**
- 🎨 5 universal tabs (Overview, Dependencies, Classes, Timeline, Authors)
- 🧠 3 CORTEX-specific tabs (Brain, Governance, Orchestrators)
- 📊 D3.js & Mermaid.js visualizations
- 🔐 Multi-dimensional overlays (Security, Performance, Compliance)
- 🚀 Self-contained SPA (no external CDN)
- ⚡ Alpine.js reactive UI

See **[LENS Dashboard Documentation](docs/11-lens-dashboard/)** for details.

## License

See LICENSE file.
