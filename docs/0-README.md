# CORTEX Documentation

**Last Updated:** 2026-01-20  
**Version:** 1.0.0  
**Status:** Production Ready (All 25 phases complete, 3000+ tests passing)

**CORTEX** is an intelligent AI-powered orchestration platform with multi-tier governance architecture, REST/MCP/CLI APIs, and resilience-first design. It provides safe, auditable AI-assisted development through the LENS Protocol (intent comprehension), Domain Brain (knowledge management), and ConversationProtocol (turn-by-turn execution).

## Quick Navigation

### 🚀 Getting Started
- **[Installation & Setup](01-getting-started/0-installation.md)** - Prerequisites and environment setup
- **[Quick Start](01-getting-started/1-quickstart.md)** - 15-minute hands-on tutorial
- **[First Orchestrator](01-getting-started/2-first-orchestrator.md)** - Create your first orchestrator
- **[Troubleshooting Setup](01-getting-started/3-troubleshooting.md)** - Common setup issues

### 🏗️ Architecture
- **[System Overview](02-architecture/1-system-overview.md)** - Multi-tier architecture and components
- **[Design Principles](02-architecture/2-design-principles.md)** - Core design philosophy
- **[Orchestration Engine](02-architecture/3-orchestration-engine.md)** - ConversationProtocol, complexity gate, response composition
- **[Domain Brain](02-architecture/4-domain-brain.md)** - Knowledge ingestion, BKIO, conflict resolution
- **[Resilience Patterns](02-architecture/5-resilience-patterns.md)** - Circuit breakers, retries, rollback
- **[Architecture Decision Records](02-architecture/adrs/)** - Design decisions and rationale

### 📡 API Reference
- **[REST API](03-api-reference/rest-api/0-guide.md)** - REST endpoints for orchestrators, knowledge, governance
- **[MCP Protocol](03-api-reference/mcp-protocol/0-specification.md)** - JSON-RPC 2.0 MCP server specification
- **[CLI Commands](03-api-reference/cli/0-guide.md)** - Command-line reference
- **[Schemas](03-api-reference/schemas/)** - Data structure definitions

### 📚 How-To Guides
- **[Deployment](04-guides/deployment/0-overview.md)** - Local, staging, and production deployment
  - [Local Development](04-guides/deployment/1-local-development.md)
  - [Troubleshooting](04-guides/operations/4-troubleshooting.md)
  - [FAQ](04-guides/deployment/4-faq.md)
- **[Integration](04-guides/integration/0-overview.md)** - Building custom orchestrators and integrations
- **[Operations](04-guides/operations/0-overview.md)** - Monitoring, alerting, and compliance
- **[Advanced](04-guides/advanced/0-overview.md)** - Resilience configuration and optimization

### 📖 Reference
- **[Glossary](05-reference/glossary.md)** - Term definitions
- **[FAQ](05-reference/faq.md)** - Frequently asked questions
- **[Known Issues](05-reference/known-issues.md)** - Issues and workarounds
- **[Changelog](05-reference/changelog.md)** - Version history
- **[Compliance](05-reference/compliance-mappings.md)** - GDPR/HIPAA/SOC2 mappings

### 🎓 Tutorials
- **[Orchestrator Tutorials](06-tutorials/orchestrator-tutorials/0-index.md)** - Hands-on examples
- **[API Integration](06-tutorials/api-integration/0-index.md)** - API integration patterns
- **[Operations](06-tutorials/operations/0-index.md)** - Operational tasks

### 🤝 Contributing
- **[Contributing Guidelines](07-contributing/1-contributing-guidelines.md)** - How to contribute
- **[Development Setup](07-contributing/2-development-setup.md)** - Local development environment
- **[Testing](07-contributing/3-testing-strategy.md)** - Testing approach
- **[Pull Request Process](07-contributing/5-pull-request-process.md)** - PR workflow

---

## Core Capabilities

### Completed & Production-Ready

| Capability | Description | Phase | Tests |
|------------|-------------|-------|-------|
| **LENS Protocol** | 4-phase intent comprehension (Language, Examination, Navigation, Synthesis) | PHASE-07 | 400+ |
| **ConversationProtocol** | Turn-by-turn execution with ContinuationDecision pattern | PHASE-16 | 155 |
| **Complexity Gate** | Stage 2.5 complexity-aware confirmation with approval matrix | PHASE-23 | - |
| **Response Composition** | 6 modes, 5 tones, 5 profiles, template system | PHASE-24 | 172 |
| **Domain Brain** | Knowledge ingestion, BKIO, conflict resolution, 4 adapters | PHASE-17 | 353 |
| **MCP Server** | JSON-RPC 2.0, stdio transport, tool discovery | PHASE-22 | - |
| **Governance Framework** | 29 CORE rules, Tier 0-3 architecture, audit trail | PHASE-09 | 133 |
| **Hallucination Prevention** | Behavioral boundaries, intent canonicalization, coherence | PHASE-11 | 160 |
| **Knowledge Ecosystem** | Tier 3 expansion, semantic search, quality curation | PHASE-12 | 243 |
| **Observability** | Telemetry, audit visualization, business domain | PHASE-13 | 141 |
| **Universal Dashboard** | Multi-repo visualization, real-time metrics | PHASE-15 | 48 |
| **Template System** | 80+ Tier 2 templates, scaffolding, validation | PHASE-19/20 | 157 |
| **Governance Composition** | Intent-driven rule profiling, composite evaluation | PHASE-25 | 183 |

**Total:** 25 phases complete, 3000+ tests passing (100% pass rate)

### Key Architectural Patterns

| Pattern | Implementation | Benefit |
|---------|----------------|---------|
| **Multi-Tier Governance** | Tier 0 (immutable) → Tier 3 (knowledge) | Safety, flexibility |
| **ContinuationDecision** | Explicit turn termination reasons | Testability, auditability |
| **Approval Matrix** | Complexity-based confirmation | UX optimization |
| **Hash Chain Audit** | Tamper-evident logging | Compliance, trust |
| **Circuit Breaker** | Resilience with fail-fast | Reliability |
| **BKIO Conflict Resolution** | Hierarchical priority + LENS synthesis | Knowledge integrity |

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CORTEX Platform                                 │
├──────────────────┬──────────────────┬──────────────────┬───────────────────┤
│   REST API       │   MCP Server     │      CLI         │   Copilot Chat    │
│   (FastAPI)      │   (JSON-RPC)     │   (cortex-*)     │   (Prompts)       │
└────────┬─────────┴────────┬─────────┴────────┬─────────┴─────────┬─────────┘
         │                  │                  │                   │
         └──────────────────┴──────────────────┴───────────────────┘
                                     │
                    ┌────────────────▼────────────────┐
                    │     LENS Protocol (Intent)      │
                    │  Language → Examination →       │
                    │  Navigation → Synthesis         │
                    └────────────────┬────────────────┘
                                     │
         ┌───────────────────────────┼───────────────────────────┐
         │                           │                           │
         ▼                           ▼                           ▼
┌─────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│    TIER 0       │     │   Master Orchestrator│     │    Domain Brain     │
│  Governance     │     │   (Conversation      │     │  (Tier 3 Knowledge) │
│  (29 CORE rules)│     │    Protocol)         │     │  (4 Adapters, BKIO) │
└─────────────────┘     └─────────────────────┘     └─────────────────────┘
                                     │
                    ┌────────────────▼────────────────┐
                    │    Response Composition         │
                    │  (6 modes, 5 tones, templates)  │
                    └────────────────┬────────────────┘
                                     │
                    ┌────────────────▼────────────────┐
                    │    Audit Trail + Hash Chain     │
                    │  (5000+ entries, unbroken)      │
                    └─────────────────────────────────┘
```

---

## For Different Roles

**Architects & Designers**
→ Start with [System Overview](02-architecture/1-system-overview.md) then [Design Principles](02-architecture/2-design-principles.md)

**Developers**
→ Start with [Quick Start](01-getting-started/1-quickstart.md) then [First Orchestrator](01-getting-started/2-first-orchestrator.md)

**Integrators**
→ Start with [MCP Protocol](03-api-reference/mcp-protocol/0-specification.md) or [REST API](03-api-reference/rest-api/0-guide.md)

**Operators**
→ Start with [Deployment Guide](04-guides/deployment/0-overview.md) then [Troubleshooting](04-guides/operations/4-troubleshooting.md)

**Contributors**
→ Start with [Contributing Guidelines](07-contributing/1-contributing-guidelines.md) then [Development Setup](07-contributing/2-development-setup.md)

---

## Document Status

| Section | Status | Last Updated |
|---------|--------|--------------|
| Getting Started | ✅ Complete | 2026-01-20 |
| Architecture | ✅ Complete | 2026-01-20 |
| API Reference | ✅ Complete | 2026-01-20 |
| Guides | 🔄 Expanding | 2026-01-20 |
| Reference | ✅ Complete | 2026-01-20 |
| Tutorials | 🔄 In Progress | 2026-01-20 |
| Contributing | 🔄 In Progress | 2026-01-20 |
| Archive | ✅ Organized | 2026-01-20 |

---

**Source of Truth:** `_workspaces/roadmap/cortex-master.yaml`  
**Governance Database:** `cortex_brain/state/governance.db`  
**Test Suite:** 3000+ tests, 100% pass rate
