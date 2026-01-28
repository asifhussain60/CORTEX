# CORTEX Discovery - Quick Reference Guide

**Generated:** 2026-01-24 | **Version:** 1.0 | **Status:** ✅ READY

---

## 🗺️ Discovery Quick Reference

### What Was Discovered?

```
CORTEX SYSTEM COMPONENTS
│
├── ORCHESTRATORS (23)
│   ├── Core (6)              → Central hub & TDD
│   ├── Domain (3)            → Business operations
│   ├── Support (8)           → Infrastructure
│   └── Specialized (6)       → Advanced features
│
├── MCP TOOLS (24)
│   ├── Governance (5)        → Rules & compliance
│   ├── Deployment (5)        → Release & rollback
│   ├── Multi-Repo (3)        → Context management
│   ├── Knowledge (1)         → Best practices
│   ├── Orchestration (varies)
│   └── Utility (varies)
│
└── GOVERNANCE RULES (29)
    └── CORE-001 through CORE-029
```

---

## 📍 Where to Find What

### ORCHESTRATORS
**Document:** `/docs/03-discovery/ORCHESTRATOR-DISCOVERY-REPORT.md`

| Need | Find | Section |
|------|------|---------|
| All orchestrators | ORCHESTRATOR-DISCOVERY-REPORT.md | Executive Summary |
| Core orchestrators | ORCHESTRATOR-DISCOVERY-REPORT.md | TIER 0: CORE ORCHESTRATORS |
| Domain orchestrators | ORCHESTRATOR-DISCOVERY-REPORT.md | TIER 1: DOMAIN ORCHESTRATORS |
| Support orchestrators | ORCHESTRATOR-DISCOVERY-REPORT.md | TIER 2: SUPPORT ORCHESTRATORS |
| Specialized orchestrators | ORCHESTRATOR-DISCOVERY-REPORT.md | TIER 3: SPECIALIZED ORCHESTRATORS |
| MasterOrchestrator | ORCHESTRATOR-DISCOVERY-REPORT.md | TIER 0 - MasterOrchestrator |
| TDD Orchestrator | ORCHESTRATOR-DISCOVERY-REPORT.md | TIER 0 - TDDOrchestrator |
| Quick start | ORCHESTRATOR-DISCOVERY-REPORT.md | Quick Start: Using Orchestrators |
| Entry points | ORCHESTRATOR-DISCOVERY-REPORT.md | Each orchestrator section |

### MCP TOOLS
**Document:** `/docs/03-discovery/MCP-TOOLS-REGISTRY.md`

| Need | Find | Section |
|------|------|---------|
| All tools | MCP-TOOLS-REGISTRY.md | Summary |
| Governance tools | MCP-TOOLS-REGISTRY.md | 1. GOVERNANCE TOOLS (5) |
| Deployment tools | MCP-TOOLS-REGISTRY.md | 2. DEPLOYMENT TOOLS (5) |
| Multi-repo tools | MCP-TOOLS-REGISTRY.md | 3. MULTI-REPO TOOLS (3) |
| Knowledge tools | MCP-TOOLS-REGISTRY.md | 4. KNOWLEDGE TOOLS (1) |
| Tool examples | MCP-TOOLS-REGISTRY.md | Using MCP Tools |
| Authentication | MCP-TOOLS-REGISTRY.md | Authentication Levels |

### GOVERNANCE RULES
**Document:** `/docs/03-discovery/GOVERNANCE-RULES-REFERENCE.md`

| Need | Find | Section |
|------|------|---------|
| All rules | GOVERNANCE-RULES-REFERENCE.md | CORE Governance Rules (29) |
| Singleton pattern | GOVERNANCE-RULES-REFERENCE.md | CORE-001 |
| Type hints | GOVERNANCE-RULES-REFERENCE.md | CORE-002, CORE-011 |
| Docstrings | GOVERNANCE-RULES-REFERENCE.md | CORE-003, CORE-012 |
| TDD workflow | GOVERNANCE-RULES-REFERENCE.md | CORE-004, CORE-008 |
| Exception handling | GOVERNANCE-RULES-REFERENCE.md | CORE-005, CORE-013 |
| Tier precedence | GOVERNANCE-RULES-REFERENCE.md | CORE-007, CORE-016 |
| Compliance matrix | GOVERNANCE-RULES-REFERENCE.md | Governance Compliance Matrix |

---

## 🚀 Common Tasks

### "I want to understand CORTEX architecture"
1. Read: `/docs/03-discovery/INDEX.md` (overview)
2. Study: `/docs/03-discovery/ORCHESTRATOR-DISCOVERY-REPORT.md` (architecture)
3. Review: `/docs/03-discovery/GOVERNANCE-RULES-REFERENCE.md` (governance)

### "I need to use a specific orchestrator"
1. Find in: `ORCHESTRATOR-DISCOVERY-REPORT.md`
2. Get entry point from orchestrator section
3. Copy code example
4. Follow usage guide

### "I need a specific MCP tool"
1. Find in: `MCP-TOOLS-REGISTRY.md`
2. Check auth level and dependencies
3. Copy usage example
4. Call with parameters

### "I need to understand a governance rule"
1. Find rule (CORE-001, etc.) in: `GOVERNANCE-RULES-REFERENCE.md`
2. Read description and requirements
3. Review code examples
4. Check enforcement method

### "I'm adding a new component"
1. Follow governance rules (CORE-029)
2. Add response header with CORTEX format
3. Document in appropriate discovery file
4. Run `/doc-discover` to re-index

---

## 🎯 Key Numbers

| Item | Count |
|------|-------|
| **Core Orchestrators** | 6 |
| **Domain Orchestrators** | 3 |
| **Support Orchestrators** | 8 |
| **Specialized Orchestrators** | 6 |
| **Total Orchestrators** | 23 ✅ |
| **Governance Tools** | 5 |
| **Deployment Tools** | 5 |
| **Multi-Repo Tools** | 3 |
| **Knowledge Tools** | 1 |
| **Total MCP Tools** | 24 ✅ |
| **Governance Rules** | 29 ✅ |
| **Knowledge YAMLs** | 35+ ✅ |
| **Tests Passing** | 6,847+ ✅ |

---

## 📱 Orchestrator Cheat Sheet

### Core Orchestrators
```python
# Master Hub
from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
master = MasterOrchestrator.instance()

# Test-First Development
from cortex.orchestrators.core.tdd_orchestrator import TDDOrchestrator
tdd = TDDOrchestrator()

# Intent Routing
from cortex.orchestrators.core.intent_router import IntentRouter
router = IntentRouter()

# Multi-turn Interaction
from cortex.orchestrators.core.interaction_orchestrator import InteractionOrchestrator
interactor = InteractionOrchestrator()
```

### Domain Orchestrators
```python
# Code Refactoring
from cortex.orchestrators.domain.refactoring_orchestrator import RefactoringOrchestrator
refactor = RefactoringOrchestrator()

# Project Planning
from cortex.orchestrators.domain.planning_orchestrator import PlanningOrchestrator
planner = PlanningOrchestrator()
```

### Support Orchestrators
```python
# Developer Onboarding
from cortex.orchestrators.onboarding import OnboardingOrchestrator
onboard = OnboardingOrchestrator()

# Deployment
from cortex.orchestrators.support.rollback_orchestrator import RollbackOrchestrator
rollback = RollbackOrchestrator()
```

---

## 🔐 MCP Tools Cheat Sheet

### Accessing Tools
```python
from cortex.mcp.registry import get_mcp_tool_registry

registry = get_mcp_tool_registry()

# List all tools
all_tools = registry.list_tools()

# Get specific tool
tool = registry.get_tool("rule_evaluator")

# Call tool
result = tool.call({"rule_id": "CORE-008"})
```

### Tool Categories
```python
# Governance
"rule_evaluator"         # Evaluate rules
"policy_enforcer"        # Enforce policies
"compliance_reporter"    # Generate reports
"audit_query"           # Query audit trail
"tier_resolver"         # Resolve tier dependencies

# Deployment
"canary_deployer"       # Progressive rollout
"release_builder"       # Package releases
"health_checker"        # Check health
"rollback"              # Rollback deployments
"sanitizer"             # Data cleanup

# Multi-Repo
"profile_manager"       # Manage profiles
"context_switcher"      # Switch contexts
"project_scanner"       # Scan projects

# Knowledge
"guidance_tool"         # Get best practices
```

---

## 📖 Governance Rules Cheat Sheet

### Critical Rules (MUST implement)
- **CORE-001:** Singleton pattern for registries
- **CORE-002:** Type hints everywhere
- **CORE-004:** Test-Driven Development (tests first)
- **CORE-007:** Tier precedence (0 > 1 > 2 > 3)
- **CORE-027:** Audit trail logging (AC_START/COMPLETE)

### Quality Rules (SHOULD follow)
- **CORE-003:** Google docstrings
- **CORE-005:** No bare except clauses
- **CORE-011:** 100% type hints
- **CORE-012:** Google docstrings on all public APIs

### Governance Rules (MUST enforce)
- **CORE-017:** Governance registry enforcement
- **CORE-020:** Multi-repo governance
- **CORE-029:** Response header enforcement
- **CORE-029:** CORTEX LENS protocol

---

## 🔗 Document Links

### Discovery Documentation
- **INDEX.md** - Start here for overview
- **ORCHESTRATOR-DISCOVERY-REPORT.md** - All 23 orchestrators
- **MCP-TOOLS-REGISTRY.md** - All 24 tools
- **GOVERNANCE-RULES-REFERENCE.md** - All 29 rules

### Architecture Documentation
- `/docs/02-orchestrators/` - Orchestrator details
- `/docs/02-cortex-brain/` - Brain architecture
- `/docs/05-lens-protocol/` - Intent classification
- `/docs/11-mcp-tools/` - MCP protocol

### Implementation Guides
- `/docs/10-contributing/` - Contributing guide
- `/docs/16-testing/` - Testing strategies
- `/docs/14-deployment/` - Deployment guide

---

## ⚡ Most Used Components

### By Developers
1. **TDDOrchestrator** - Write tests first
2. **IntentRouter** - Route intent to handler
3. **MasterOrchestrator** - Access all services
4. **guidance_tool** - Get best practices

### By DevOps
1. **canary_deployer** - Progressive rollout
2. **health_checker** - Monitor health
3. **rollback** - Revert deployment
4. **audit_query** - Check operation history

### By QA
1. **TDDOrchestrator** - Test framework
2. **compliance_reporter** - Generate reports
3. **health_checker** - Verify stability
4. **test_validator** - Validate tests

### By Architects
1. **governance_registry** - Enforce rules
2. **orchestrator_registry** - Track components
3. **state_manager** - Manage state
4. **tier_resolver** - Resolve dependencies

---

## ✅ Validation Checklist

When using discovered components:

- [ ] Found in discovery document
- [ ] Read entry point/usage
- [ ] Understood capabilities
- [ ] Reviewed governance rules
- [ ] Checked examples
- [ ] Validated type hints (CORE-011)
- [ ] Added docstring (CORE-012)
- [ ] No bare excepts (CORE-013)
- [ ] Tests written first (CORE-008)
- [ ] Audit logging enabled (CORE-027)

---

## 🆘 Troubleshooting

### "Can't find component X"
→ Check discovery documents, search by name or keyword

### "What's the entry point for component X?"
→ See the orchestrator section, "Entry Point" subsection

### "What's the difference between components?"
→ See discovery document comparison tables

### "How do I call this component?"
→ See code examples in discovery documents

### "Is this rule mandatory?"
→ Check severity level in GOVERNANCE-RULES-REFERENCE.md

### "What do I do if component is deprecated?"
→ See alternative in same discovery document

---

## 🎓 Learning Path

1. **Start:** `/docs/03-discovery/INDEX.md`
2. **Learn Architecture:** `ORCHESTRATOR-DISCOVERY-REPORT.md`
3. **Understand Tools:** `MCP-TOOLS-REGISTRY.md`
4. **Study Rules:** `GOVERNANCE-RULES-REFERENCE.md`
5. **Deep Dive:** Reference architecture docs
6. **Practice:** Build with discovered components

---

## 📞 Quick Help

| Question | Answer | Location |
|----------|--------|----------|
| Where do I start? | INDEX.md | /docs/03-discovery/ |
| What orchestrators exist? | ORCHESTRATOR-DISCOVERY-REPORT.md | /docs/03-discovery/ |
| What tools are available? | MCP-TOOLS-REGISTRY.md | /docs/03-discovery/ |
| What are the rules? | GOVERNANCE-RULES-REFERENCE.md | /docs/03-discovery/ |
| How do I use X? | Respective discovery doc | /docs/03-discovery/ |
| How do I implement X? | Contributing guide | /docs/10-contributing/ |
| How do I deploy X? | Deployment guide | /docs/14-deployment/ |

---

**Quick Links:**
- 📍 **Discovery Index:** `/docs/03-discovery/INDEX.md`
- 🎯 **This Guide:** `/docs/03-discovery/QUICK-REFERENCE.md`
- 🏗️ **Architecture:** `/docs/02-orchestrators/0-overview.md`
- 📚 **All Docs:** `/docs/0-README.md`

---

**Last Updated:** 2026-01-24 | **Status:** ✅ Complete
