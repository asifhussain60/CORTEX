# CORTEX Documentation

**CORTEX** — **CO**gnitive **R**eal-**T**ime **EX**ecution System

A sophisticated AI-powered development orchestrator for automated code analysis, generation, testing, and governance.

## 🚀 Quick Start

- **[Getting Started](01-getting-started/quickstart.md)** - Installation and first steps
- **[Architecture](02-architecture/overview.md)** - System design and components
- **[API Reference](03-api-reference/)** - Orchestrators, MCP tools, governance rules
- **[Guides](04-guides/)** - How-to guides for common tasks
- **[Tutorials](05-tutorials/)** - Step-by-step learning paths
- **[Reference](06-reference/)** - Glossary, best practices, examples

## 🧠 System Tiers

CORTEX is organized in 4 tiers:

- **Tier 0:** Immutable Governance (29 CORE rules)
- **Tier 1:** Acceptance Criteria (AC-ID specifications)
- **Tier 2:** Response Templates & Boundaries (Hallucination prevention)
- **Tier 3:** Knowledge & Best Practices (35+ YAML guides)

## 🎯 Key Features

- ✅ **TDD Orchestrator** - Test-driven development automation
- ✅ **Intent Router** - Intelligent request classification (LENS framework)
- ✅ **Master Orchestrator** - Unified execution hub
- ✅ **Documentation Orchestrator** - Automated doc generation with diagrams
- ✅ **MCP Tools** - 15+ integrated tools for development tasks
- ✅ **Governance Engine** - 29 CORE rules enforcement
- ✅ **Knowledge Graph** - Domain-specific intelligence and recommendations
- ✅ **Circuit Breaker** - Resilience and fault isolation

## 📊 Status

- ✅ Tests: 6,847+ (100% passing)
- ✅ Orchestrators: 20/23 wired
- ✅ MCP Tools: 15 active
- ✅ Governance Rules: 29/29 implemented
- ✅ Knowledge Files: 35+ best practices

## 📚 Documentation Structure

```
docs/
├── 00-README.md                    # Main entry point (this file)
├── 01-getting-started/             # Installation, quickstart, setup
├── 02-architecture/                # Brain tiers, orchestrators, flows
├── 03-api-reference/               # Components and APIs
├── 04-guides/                      # How-to guides
├── 05-tutorials/                   # Step-by-step tutorials
├── 06-reference/                   # Glossary, best practices
├── _diagrams/                      # All visualizations
└── serve-docs.sh                   # Launch documentation server
```

## 🔗 Entry Points

| Component | Purpose | Entry Point |
|-----------|---------|-------------|
| **TDD Orchestrator** | Test-driven development | `cortex.orchestrators.core.tdd_orchestrator` |
| **Intent Router** | Request classification | `cortex.orchestrators.core.intent_router` |
| **Master Orchestrator** | Main execution hub | `cortex.orchestrators.core.master_orchestrator` |
| **Documentation** | Doc generation | `cortex.orchestrators.documentation` |
| **Governance** | Rule enforcement | `cortex.brain.core.governance_registry` |

## 🚀 Getting Started

1. **Installation:** See [Getting Started](01-getting-started/quickstart.md)
2. **Understand Architecture:** Review [Architecture Overview](02-architecture/overview.md)
3. **Learn by Example:** Follow [Tutorials](05-tutorials/)
4. **API Reference:** Check [API Docs](03-api-reference/)

## 🆘 Support

- **Issues:** Check [Common Issues](06-reference/troubleshooting.md)
- **Best Practices:** See [Best Practices Guide](06-reference/best-practices.md)
- **Glossary:** Find terms in [Glossary](06-reference/glossary.md)

---

**Last Updated:** 2026-01-25
