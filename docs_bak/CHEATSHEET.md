# CORTEX Cheatsheet

> Quick reference for CORTEX - COgnitive Real-Time EXecution System

## 🚀 Quick Start

```bash
# Activate environment
source .venv/bin/activate

# Run CLI
python -m cortex.cli --help

# Check status
python -m cortex.cli status

# Run tests
pytest tests/ -n auto
```

## 📋 Key Commands

| Command | Description |
|---------|-------------|
| `python -m cortex.cli status` | System status |
| `python -m cortex.cli governance list` | List governance rules |
| `python -m cortex.cli governance check <file>` | Check file compliance |
| `python -m cortex.cli lens analyze-remote <repo> <file>` | Remote file analysis |
| `python -m cortex.cli ask "<question>"` | Ask about codebase |

## 🎼 Orchestrators (23 Wired)

### Core (6)
- **MasterOrchestrator** - Main coordination, 5-stage pipeline
- **IntentRouter** - Intent classification, routing
- **TDDOrchestrator** - RED→GREEN→REFACTOR workflow
- **InteractionOrchestrator** - ChallengeEngine, user interaction
- **WorkflowOrchestrator** - Multi-step execution
- **WrappedTDDOrchestrator** - TDD with governance wrapper

### Domain (6)
- **RefactoringOrchestrator** - SOLID principles, pattern extraction
- **PlanningOrchestrator** - Phase planning, dependencies
- **DomainOrchestrator** - Business domain logic
- **ConversationOrchestrator** - Multi-turn state
- **SeleniumPlaywrightOrchestrator** - Browser automation
- **DocumentationOrchestrator** - Doc generation

### Support (11)
- **OnboardingOrchestrator** - Guided setup
- **ToolDiscoveryOrchestrator** - Capability catalog
- **SetupOrchestrator** - Environment setup
- **LENSOrchestrator** - Code intelligence (git, AST, comments)

## 📜 Governance Rules (Tier 0)

| Rule | Description |
|------|-------------|
| CORE-008 | TDD - Tests BEFORE code |
| CORE-011 | Type hints MANDATORY |
| CORE-012 | Google-style docstrings |
| CORE-013 | No bare except clauses |
| CORE-026 | Git checkpoint before major changes |
| CORE-027 | Audit trail (AC_START → AC_COMPLETE) |
| CORE-028 | File naming - snake_case for Python |
| CORE-029 | Response header enforcement |
| CORE-030 | Implementation Truth - verify code |
| CORE-035 | Single Canonical Implementation |
| CORE-038 | File Placement Policy |

## 🧠 LENS Intelligence

```python
from cortex.orchestrators.support.lens_orchestrator import LENSOrchestrator

# Analyze a file
orchestrator = LENSOrchestrator(repo_path=Path("/path/to/repo"))
context = orchestrator.analyze_file(Path("module.py"))

# Results include:
# - git_analysis: commits, blame, authors
# - ast_analysis: functions, classes, complexity
# - comment_analysis: TODOs, FIXMEs, docstrings
```

## 📁 File Locations

| Content | Location |
|---------|----------|
| Orchestrators | `cortex/orchestrators/` |
| Brain/Knowledge | `cortex_brain/` |
| Wiring Spec | `cortex/wiring/specifications/wiring.yaml` |
| Tests | `tests/` |
| Documentation | `docs/` |

## 🔧 Development

```bash
# Run specific tests
pytest tests/unit/orchestrators -v

# Run with coverage
pytest --cov=cortex --cov-report=html

# Format code
black cortex/ tests/

# Type check
mypy cortex/
```

## 📊 Metrics

- **10,500+** tests
- **23/23** orchestrators wired
- **35+** governance rules
- **431,000+** lines of code

---

*Full documentation: `docs/`*
*Copilot instructions: `.github/copilot-instructions.md`*
