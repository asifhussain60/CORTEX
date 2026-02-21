# CORTEX

**CO**gnitive **R**eal-**T**ime **EX**ecution System — AI-powered development orchestrator.

[![Architecture: MCP-First Service-Oriented](https://img.shields.io/badge/Architecture-MCP--First%20Service--Oriented-blue)](docs/04-architecture/mcp-architecture.md)
[![Orchestrators: 28](https://img.shields.io/badge/Orchestrators-28-green)](docs/02-orchestrators/)
[![MCP Tools: 24](https://img.shields.io/badge/MCP%20Tools-24-orange)](docs/11-mcp-tools/)
[![Python: 3.9+](https://img.shields.io/badge/Python-3.9+-blue)](https://python.org)
[![Tests: 15,633 Passing](https://img.shields.io/badge/Tests-15,633%20Passing-success)]()
[![Status: Production Ready](https://img.shields.io/badge/Status-Production%20Ready-success)](cortex-registry/CORTEX-STATUS-2026-02-14.yaml)

## 🚀 Recent Updates (2026-02-17)

**Phase 103: Registry & Intelligence Consolidation** ✅ COMPLETE
- ✅ **Brain Architecture**: `cortex_brain` → `cortex/intelligence/` (cognitive alignment)
- ✅ **Memory Hierarchy**: `tier0-3` → `memory/{core, tier1_learned, tier2_adaptive, tier3_scratch}`
- ✅ **Registry Cleanup**: Eliminated `_cortex-master/` wrapper for semantic top-level structure
- ✅ **Testing**: 235 golden tests passing (100% pass rate)
- 📖 **Migration Guide**: See `cortex-registry/archive/PHASE-103-MIGRATION-GUIDE.md`

**4 Autonomous Waves Completed (2026-02-14):**
- ✅ **WAVE-1:** Documentation Vacuum (81% file reduction, 119→23 files)
- ✅ **WAVE-2:** MCP Enforcement (native tool interception, 19 tests)
- ✅ **WAVE-3:** Automation Hooks (StatusUpdateHook, RecommendationGate, RegistryValidator, 24 tests)
- ✅ **WAVE-4:** Governance Audit (0 P0 violations, production ready, 11 tests)

**Architecture:** MCP-First SaaS (Pylance-style auto-start)  
**Governance:** 0 P0 violations | 26/30 CORE rules automated (87%)  
**Quality:** 15,633 tests passing | Production-ready

## 🏗️ Architecture: MCP-First Service-Oriented Design

**CORTEX operates as a MCP-First architecture** where all 28 orchestrators are exposed as MCP (Model Context Protocol) tools.

### MCP Architecture: Pylance-Style (ENH-066)

**CORTEX MCP runs locally within VS Code, similar to how Pylance operates:**

```
┌─────────────────────────────────────────────────────────────┐
│                    VS Code                                  │
│  ┌─────────────────┐    ┌────────────────────────────────┐  │
│  │  Copilot Chat   │───▶│  MCP Server (Auto-Started)     │  │
│  │                 │    │  • stdio transport             │  │
│  │  User: /impl    │◀───│  • JSON-RPC 2.0                │  │
│  │                 │    │  • python -m cortex.mcp        │  │
│  └─────────────────┘    └────────────────────────────────┘  │
│                                    │                        │
│                                    ▼                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │            cortex_* Tools                            │   │
│  │  • cortex_process_request  • cortex_lens_analyze    │   │
│  │  • cortex_challenge        • cortex_detect_duplicates│   │
│  │  • cortex_plan_execute_autonomous                    │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘

❌ OLD (Wrong): User manually runs "python -m cortex.mcp.server"
✅ NEW (Correct): VS Code auto-starts MCP when Copilot invokes tools
```

**Key Characteristics:**
- 🔄 **Auto-Started:** VS Code launches MCP automatically (no manual startup)
- 📡 **stdio Transport:** Uses stdin/stdout for JSON-RPC communication
- 🔒 **Process Isolation:** MCP runs as child process of VS Code
- 🎯 **Zero Configuration:** Just run setup script, then reload VS Code

**Setup Time:** 30 seconds (down from 30 minutes)

**Key Benefits:**
- ✅ **Independent Scaling:** Each orchestrator scales horizontally via replicas
- ✅ **Language Agnostic:** MCP JSON-RPC protocol (Python, TypeScript, any language)
- ✅ **Failure Isolation:** Circuit breaker per orchestrator (3-failure threshold)
- ✅ **Dynamic Discovery:** Tools register at runtime, enabling hot-reload
- ✅ **Service Isolation:** No direct imports, protocol-driven communication

**Learn More:** [MCP Architecture Documentation](docs/04-architecture/mcp-architecture.md)

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/asifhussain60/CORTEX.git
cd CORTEX

# 2. Set up Python environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Configure MCP for VS Code (Pylance-Style Architecture)
# MCP runs locally within VS Code - NO manual server startup needed!
python .cortex-runtime/setup-mcp.py

# 4. Reload VS Code to activate MCP
# Command Palette → Developer: Reload Window

# 5. Verify MCP integration
# In Copilot Chat, you should see cortex_* tools available
# Check .cortex-runtime/setup.log for confirmation

# 6. Configure git hooks (IMPORTANT for team collaboration)
make setup-hooks
# or: ./scripts/setup-hooks.sh
```

### 🔧 After Pulling from Git (Cross-Platform MCP Setup)

**CORTEX uses platform-specific Python paths that CANNOT be committed to git:**
- macOS/Linux: `.venv/bin/python`
- Windows: `.venv/Scripts/python.exe`

**Automatic (via git hooks):**
```bash
# Post-checkout hook auto-runs after every git pull/checkout:
python .cortex-runtime/setup-mcp.py --silent

# This regenerates .vscode/settings.json with correct platform paths
# Then reload VS Code: Cmd+Shift+P → Developer: Reload Window
```

**Manual (if hook fails or first-time setup):**
```bash
# Regenerate platform-specific MCP configuration
python .cortex-runtime/setup-mcp.py

# Reload VS Code
# Command Palette → Developer: Reload Window

# Verify MCP tools are available
python .cortex-runtime/verify-setup.py
```

**Troubleshooting:**
```bash
# If MCP tools not available after reload:
python .cortex-runtime/diagnose-mcp.py  # Diagnostic report

# Or check logs:
cat .cortex-runtime/setup.log           # Last setup attempt
cat .vscode/settings.json       # Verify Python path

# Common fix: Delete and regenerate
rm .vscode/settings.json
python .cortex-runtime/setup-mcp.py
```

**Why this matters:** Without correct paths, MCP tools won't be available in Copilot Chat, blocking all IMPLEMENT/FIX/REFACTOR operations (CORE-051).

## MCP-FIRST Enforcement (Phase 51)

CORTEX enforces production-quality standards through **MCP-FIRST** architecture:

**✅ ENABLED (when MCP running):**
- IMPLEMENT/FIX/REFACTOR operations via `cortex_process_request`
- TDD enforcement (CORE-008: tests before code)
- Security gates (ARCH-012: OWASP compliance)
- Audit trail (CORE-027: AC markers)
- Quality validation (CORE-050: No degradation)

**❌ BLOCKED (when MCP unavailable):**
- Direct file creation (`create_file` tool)
- Direct file editing (`replace_string_in_file`)
- "Basic mode" / "quick fix" quality degradations
- Test skipping or bypassing

**Environment Check:**
```python
from cortex.governance.enforcement.agents.environment_integrity_agent import EnvironmentIntegrityAgent

agent = EnvironmentIntegrityAgent()
result = agent.check_mcp_availability()
print(f"MCP Available: {result.available} ({result.detection_method})")
```

**Why MCP-FIRST?** Ensures TDD, security gates, and audit trails are never bypassed. See [CORE-050](cortex-registry/governance/core-rules.yaml#L438) for details.

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

This configures Git to use version-controlled hooks from `.cortex-runtime/hooks/`.

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
- **[CORTEX Intelligence](docs/01-cortex-brain/)** - Governance & cognitive architecture (formerly "Brain")
- **[Orchestrators](docs/02-orchestrators/)** - 28 specialized coordinators
- **[LENS Protocol](docs/05-lens-protocol/)** - Code intelligence system
- **[LENS Dashboard](docs/11-lens-dashboard/)** - Visual intelligence (NEW ✨)
- **[Architecture](docs/04-architecture/)** - System design
- **[API Reference](docs/06-api-reference/)** - Complete API docs
- **[MCP Tools](docs/11-mcp-tools/)** - Model Context Protocol integration

### Core Package Structure

```
cortex/                    # Main CORTEX package
  orchestrators/          # 21 wired orchestrators across 3 tiers (core, domain, support)
  mcp/                    # MCP server & 23 tool registry
  governance/             # Enforcement agents & validators
  intelligence/           # Cognitive architecture (LENS, knowledge, memory)
    memory/               # Tiered knowledge hierarchy
    domain/               # Domain logic
    perception/           # Pattern detection
    reasoning/            # Decision logic
    action/               # Execution logic

cortex-registry/          # Knowledge & governance registry
  core/                   # Governance rules, config, specifications
  artifacts/              # Templates, workflows
  integration/            # Interaction patterns
  metrics/                # Performance baselines
  planning/phases/        # Phase definitions
  archive/                # Migration guides & legacy files
```

**Migration Note**: References to `cortex_brain` or `cortex_intelligence` are stale — use `cortex.intelligence` or `cortex.orchestrators` per the canonical package structure.

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
