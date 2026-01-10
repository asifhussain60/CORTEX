# CORTEX Architecture & Governance Summary

**Version:** 5.5.0 | **Date:** January 10, 2026  
**Author:** Asif Hussain  
**Scope:** Architecture, Brain, SKULL Protection, Agents, Configuration  
**Copyright © 2025-2026 Asif Hussain. All rights reserved.**

---

## 1. Executive Overview

CORTEX (Cognitive Orchestration Runtime for Technology EXcellence) is an AI-powered development assistant built on a 4-tier cognitive brain architecture. This document covers the foundational architecture, governance through SKULL protection rules, agent system, and configuration framework that enable CORTEX's intelligent development capabilities.

### Key Architectural Principles

| Principle | Implementation |
|-----------|----------------|
| **Long-Term Memory** | 4-tier brain with specialized databases |
| **Immutable Governance** | 61 SKULL rules enforced at Tier 0 |
| **Context Awareness** | Knowledge graph learning across projects |
| **Local-First** | Distributed database architecture |
| **Agent-Based** | 9 specialist agents for focused tasks |

---

## 2. Four-Tier Brain Architecture

### Architecture Overview

CORTEX implements a hierarchical memory system with four specialized tiers, each optimized for specific latency and storage requirements.

| Tier | Name | Latency | Purpose | Storage |
|------|------|---------|---------|---------|
| **Tier 0** | Instincts Layer | <10ms | Immutable governance rules (61 SKULL rules) | cortex-brain/tier0/governance.db |
| **Tier 1** | Working Memory | <100ms | Active session context (70 conversations, 90 days) | cortex-brain/tier1/conversations.db |
| **Tier 2** | Knowledge Graph | <150ms | Learned patterns (54 patterns, 9 categories) | ~/.cortex/shared/tier2/knowledge-graph.db |
| **Tier 3** | Development Context | <1ms | Project metrics (cached) | cortex-brain/tier3/metrics.db |

### Tier 0: Instincts Layer (v2.4)

**Characteristics:**
- Immutable - cannot be bypassed at runtime
- Contains all 61 SKULL protection rules across 24 layers
- Enforces core architectural integrity
- Sub-10ms latency for governance checks

**Contents:**
- 61 SKULL protection rules (TDD, security, git isolation, planning, documentation)
- SOLID principles enforcement
- Security policies (OWASP patterns, threat modeling)
- Architectural constraints

### Tier 1: Working Memory (v5.5)

**Characteristics:**
- Session-based memory boundaries
- Automatic cleanup (90-day retention or 70 conversation max)
- Idle gap threshold: 2 hours
- Conversation history in JSONL + SQLite

**Capacity:**
- Max Conversations: 70
- Retention: 90 days
- Cleanup: Optional on startup

### Tier 2: Knowledge Graph (v2.1)

**Characteristics:**
- Cross-project pattern learning
- Confidence-scored patterns (threshold: 0.5)
- Shared across repositories (~/.cortex/shared/)
- Bootstrap from cortex-brain/knowledge-graph.yaml

**Learning:**
- 54 learned patterns across 9 categories
- Validation insights from past conversations
- Workflow optimizations
- Common mistake prevention

### Tier 3: Development Context (v5.5)

**Characteristics:**
- Cached for sub-millisecond access
- Project-specific metrics and configuration
- Git history context
- Test results and coverage data

---

## 3. SKULL Protection System v2.4

**SKULL = Secure Knowledge Unified Logical Layer**

### Protection Statistics

| Metric | Value |
|--------|-------|
| Total Rules | 61 |
| Protection Layers | 24 |
| Blocked Rules | 47 |
| Warning Rules | 12 |
| Info Rules | 2 |
| Enforcement | Automated via Brain Protector agent |

### Rule Categories & Key Examples

#### TDD Enforcement (6 rules)
- **TDD_ENFORCEMENT** - Intelligent TDD for high-value code (controllers, services, repositories)
- **RED_PHASE_VALIDATION** - Tests must fail before implementation
- **GREEN_PHASE_VALIDATION** - Minimal implementation only
- **REFACTOR_CODE_CLEANUP_ENFORCEMENT** - Mandatory whole-file cleanup

#### Code Quality (5 rules)
- **HOLISTIC_CODE_DISCOVERY_ENFORCEMENT** - Search before create (prevents duplication)
- **SOLID_SRP** - Single Responsibility (>250 line classes trigger)
- **SOLID_DIP** - Depend on abstractions
- **INLINE_CSS_PROHIBITION** - Centralized CSS only

#### Security (3 rules)
- **SECURITY_INJECTION** - Prevent SQL injection, XSS, command injection
- **SECURITY_AUTHENTICATION** - Strong passwords, MFA support
- **THREAT_MODELING_ENFORCEMENT** - STRIDE analysis required

#### Git Protection (5 rules)
- **GIT_ISOLATION_ENFORCEMENT** - CORTEX code never commits to user repos
- **GIT_CHECKPOINT_ENFORCEMENT** - Checkpoint before development
- **GIT_CHECKPOINT_PHASE_PROTECTION** - Commit after each phase
- **PREVENT_DIRTY_STATE_WORK** - Clean working directory required
- **GIT_COMMIT_PRIVACY_VALIDATION** - No secrets in commits

#### Planning (6 rules)
- **MANDATORY_PLANNING_ENFORCEMENT** - Planning creates plans only, never implements
- **INCREMENTAL_PLAN_GENERATION** - Plans >20KB trigger modularization (80% faster loads)
- **TIERED_PLANNING_ENFORCEMENT** - 4-tier complexity routing
- **PLAN_ARTIFACT_LOCATION_ENFORCEMENT** - All plans in cortex-brain/documents/planning/
- **AUTONOMOUS_EXECUTION_PROTECTION** - Safety checks for autonomous mode

#### Documentation (3 rules)
- **DOCUMENT_ORGANIZATION_ENFORCEMENT** - All docs in cortex-brain/documents/
- **MACHINE_READABLE_FORMATS** - YAML/JSON for structured data
- **API_DOCUMENTATION_REQUIRED** - All public APIs documented

#### Integration (3 rules)
- **KNOWLEDGE_LIBRARY_INTEGRATION_ENFORCEMENT** - Reference best practices
- **VISION_API_INTEGRATION_ENFORCEMENT** - Automatic image analysis
- **CONTINUOUS_RISK_ANALYSIS_ENFORCEMENT** - Risk analysis every planning turn

#### Architecture (3 rules)
- **BRAIN_ARCHITECTURE_INTEGRITY** - 4-tier brain immutable
- **DISTRIBUTED_DATABASE_ARCHITECTURE** - Tier 2 shared, others repo-specific
- **CORTEX_PROMPT_FILE_PROTECTION** - CORTEX.prompt.md is source of truth

### Enforcement Levels

**Blocked (47 rules):** Operation cannot proceed. Provides alternatives.  
**Warning (12 rules):** Proceed with caution. Suggests best practice.  
**Info (2 rules):** Informational guidance. Optimization tip.

---

## 4. Agent System v5.5

### Agent Overview

CORTEX employs 9 specialist agents organized by hemisphere (strategic, operational, tactical, governance):

| Agent | Purpose | Hemisphere | Key Responsibilities |
|-------|---------|------------|----------------------|
| **Change Governor** | Architecture change validation | Strategic | Impact analysis, risk assessment |
| **Health Validator** | System health checks | Operational | 11-phase pipeline, metrics collection |
| **Code Executor** | Safe code execution | Tactical | Validation checks, error handling |
| **Test Generator** | Test case generation | Tactical | Edge case identification, framework adaptation |
| **Debug Agent** | Runtime debugging | Tactical | Instrumentation, variable capture, session replay |
| **ADO Agent** | Azure DevOps integration | Operational | Work item generation, story point estimation |
| **LLM Intent Classifier** | Intelligent intent detection | Strategic | Context-aware classification, confidence scoring |
| **Learning Librarian** | Knowledge library management | Strategic | Pattern learning, best practice curation |
| **Brain Protector** | SKULL rule enforcement | Governance | 61 rules enforcement, integrity protection |
| **Security Scanner** | Vulnerability scanning | Operational | OWASP Top 10 detection, pattern validation |

### LLM Intent Classifier (New in 5.5)

**Confidence Thresholds:**
- High (≥0.8): Execute immediately
- Medium (≥0.5): Confirm with user
- Low (<0.5): Fallback to keyword regex or ask clarification

**Fallback Chain:** LLM Classification → Keyword Regex → User Clarification

**Features:**
- Context-aware classification
- Confidence scoring
- Cache-enabled for speed
- Seamless fallback to regex patterns

---

## 5. Configuration System v4.0

### Core Configuration

**Main Config:** cortex.config.json (v4.0)  
**Environment:** Development  
**Deployment:** Local-first hybrid

### Brain Configuration

| Setting | Value |
|---------|-------|
| Tier 0 Rules | ~/.cortex/shared/skull_rules.yaml |
| Tier 1 DB | {repo}/cortex-brain/tier1/conversations.db |
| Tier 2 DB | ~/.cortex/shared/tier2/knowledge-graph.db |
| Tier 3 DB | {repo}/cortex-brain/tier3/metrics.db |
| Max Conversations | 70 |
| Retention Days | 90 |
| Pattern Confidence | 0.5 |
| Cross-Repo Learning | Enabled |

### Token Optimization

| Parameter | Value |
|-----------|-------|
| Enabled | Yes |
| Soft Limit | 40,000 tokens |
| Hard Limit | 50,000 tokens |
| Target Reduction | 60% |
| Quality Threshold | 90% |
| Cache Check Frequency | Every 5 operations |

### Governance

| Setting | Value |
|---------|-------|
| Auto-Chain Tasks | Enabled |
| Auto-Chain Phases | Disabled |
| Require Build Validation | Disabled |
| Require Git Validation | Enabled |
| Test Quality Threshold | 70% |

### Planning

**YAML Modularization Threshold:** 20KB  
Plans exceeding 20KB automatically modularized for 80%+ faster loads.

### Integration Settings

**Vision API:** Configurable (currently disabled)  
**LLM Intent Routing:** Configurable (currently disabled)  
**MCP Gateway:** Disabled  
**Response Templates v4:** Disabled (direct implementation)

---

## 6. Knowledge Library v5.5

### Library Structure

**Base Path:** cortex-brain/knowledge-library/  
**Auto-Reference:** Enabled

### Knowledge Domains

| Domain | Resources | Count |
|--------|-----------|-------|
| **Architecture** | ai-architecture.yaml, microservices-transition.yaml, reactive-systems.yaml | 3 |
| **Security** | threat-modeling-framework.md, owasp-top-10-guide.md, api-security-foundations.md, access-control-patterns.md, data-protection-framework.md | 5 |
| **Compliance** | gdpr-compliance-checklist.md, hipaa-compliance-checklist.md, pci-dss-compliance-checklist.md, soc2-compliance-checklist.md | 4 |
| **Design Patterns** | csharp-patterns.yaml | 1 |
| **Standards** | diagram-guidelines.md | 1 |

**Total Resources:** 14 knowledge files

---

## 7. File Organization v5.5

### Forbidden Locations

❌ Repository root (no documentation files)  
❌ Outside cortex-brain/documents/ (all generated docs)

### Required Structure

**Base:** cortex-brain/documents/

**Categories:**
- **reports/** - Generated reports and analysis
- **analysis/** - Deep-dive analysis documents
- **summaries/** - Executive summaries
- **investigations/** - Investigation findings
- **planning/** - Planning artifacts (active, temp-plans, completed)
- **implementation-guides/** - Implementation documentation
- **requirements/** - Requirements specifications

### Planning Output Structure

```
cortex-brain/documents/planning/active/{PLAN_NAME}/
├── 00-master-plan.md (mandatory: progress tracker, template reminder, REFACTOR phase)
├── context/ (context artifacts)
├── reports/ (progress reports)
├── artifacts/ (supporting files)
└── tracking/
    └── progress-tracker.json (mandatory)
```

**Enforcement:** DOCUMENT_ORGANIZATION_ENFORCEMENT (SKULL rule)

---

## 8. Truth Sources v5.5

### Single Source of Truth Registry

| Domain | File | Purpose |
|--------|------|---------|
| **Architecture** | cortex-brain/CORTEX-UNIFIED-ARCHITECTURE.yaml | System design, components, patterns |
| **Operations** | cortex-operations.yaml | Operation definitions, implementation status |
| **Implementation Status** | cortex-brain/cortex-2.0-design/status-data.yaml | Phase completion, task progress |
| **Knowledge Patterns** | cortex-brain/tier2/knowledge_graph.db | Learned patterns, validation insights |
| **Conversation History** | cortex-brain/conversation-history.jsonl | Conversation continuity |
| **Test Inventory** | pytest --collect-only | Available test inventory |

### Drift Prevention Rules

1. Update derived sources with truth source in same commit
2. Only ONE authoritative source per domain
3. Test before claim (>95% pass rate)
4. Status trinity sync (status-data.yaml, STATUS.md, CORTEX2-STATUS.MD)

---

## 9. Technical Specifications v5.5

### Languages

| Type | Technologies |
|------|-------------|
| **Primary** | Python 3.9+ |
| **Supporting** | TypeScript, PowerShell, YAML, SQL |

### Databases

| Tier | Technology |
|------|------------|
| Tier 0 | SQLite (governance) |
| Tier 1 | SQLite (conversations) |
| Tier 2 | SQLite (knowledge graph) |
| Tier 3 | SQLite (metrics) |

### IDE Integration

**Primary:** VS Code  
**Secondary:** Visual Studio  
**Auto-Detect:** Enabled

### Platforms

- Windows
- macOS
- Linux

### Dependencies

**Core:** python>=3.9, pyyaml, sqlite3  
**Optional:** playwright, pytest, openai

### Deployment

**Model:** Local-first hybrid  
**Distribution:** Repository-based  
**Installation:** Git clone + venv setup

---

## 10. Integration Protocols

### Hand-Off Protocol (Autonomous Orchestrators 🛡️)

**Visual Indicator:** 🛡️ in response header

**Forbidden Behaviors:**
- Do NOT read manifest and execute yourself
- Do NOT provide guidance based on manifest
- Do NOT implement after detecting planning intent
- Do NOT continue after loading orchestrator

**Required Behaviors:**
- Load manifest reference ONLY
- Use specified response template
- STOP immediately after hand-off header
- Let orchestrator Python code execute independently

### Vision API Protocol

**Trigger:** Image attachment detected (automatic)  
**Engagement:** AUTOMATIC (no user prompt needed)  
**Formats:** PNG, JPG, JPEG, WEBP, GIF  
**Visual Indicator:** 📷 in response header  
**Max Engagement Time:** 500ms

**Analysis Requirements:**
- UI elements extraction (components, text, icons, colors, layout)
- Technical details (URLs, technology stack, responsive breakpoints, accessibility)
- Structural mapping (page hierarchy, component nesting, DOM inference, CSS patterns)
- Actionable insights (interactive elements, form validation, navigation, test selectors, security)

### Risk Analysis Protocol

**Trigger:** Every planning turn  
**Visual Indicator:** 💀 in recommendations section  
**Frequency:** Continuous during planning

**12 Analysis Categories:**
Edge cases, failure modes, race conditions, integration pitfalls, deployment risks, security vulnerabilities, performance bottlenecks, scalability limits, rollback recovery, data integrity, dependency risks, maintainability issues

**Recommendation Format:**
Risk description + Impact + Recommendation + Accept/Reject

**Response Options:**
- Accept → Integrate into plan immediately
- Reject → Skip for now, re-analyze next turn

---

## 11. Document References

| Document | Purpose |
|----------|---------|
| **cortex-architecture-spec.yaml** | Full technical specification (this document's source) |
| **cortex-features-spec.yaml** | Orchestrators, capabilities, integrations |
| **brain-protection-rules.yaml** | Complete 61 SKULL rules with evidence templates |
| **cortex.config.json** | Main configuration file (v4.0) |
| **CORTEX-UNIFIED-ARCHITECTURE.yaml** | System design source of truth |

---

**Copyright © 2025-2026 Asif Hussain. All rights reserved.**
