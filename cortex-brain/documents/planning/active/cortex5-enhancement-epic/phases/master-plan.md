# CORTEX 5.0 Enhancement Epic: Business Domain Integration

**Epic ID:** cortex5-enhancement-epic  
**Created:** 2026-01-06  
**Status:** ✅ ACTIVE  
**Orchestrator:** Planning v5  
**Architecture:** Knowledge Extension + Orchestrator Registry + Hierarchical Goals

---

## 🎯 Executive Summary

### Vision
Transform CORTEX from a universal AI orchestration platform into a **business-aware, domain-extensible system** where companies can inject custom knowledge, orchestrators, and governance rules without corrupting core capabilities.

### Strategic Goals

**Primary Objectives:**
1. **Knowledge Extension Layer:** Enable company-specific documentation (architecture, tech stack, APIs, standards) to augment CORTEX knowledge library
2. **Custom Orchestrator Registry:** Allow companies to register domain-specific orchestrators (e.g., Selenium→Playwright converter) that inherit CORTEX best practices
3. **Intelligent Governance Layering:** Company rules override CORTEX defaults where explicitly defined, otherwise CORTEX wins
4. **Master Orchestrator Control:** Central routing system manages both CORTEX core and custom orchestrators seamlessly

**Success Metrics:**
- ✅ Company knowledge overrides CORTEX intelligently (95% accuracy)
- ✅ Custom orchestrators registered without core corruption (100% isolation)
- ✅ Knowledge merge overhead <50ms (efficiency requirement)
- ✅ 3+ reference custom orchestrators implemented (Selenium→Playwright, Legacy Migration, Domain API Builder)

---

## 📊 Epic-Level Goals (Auto-Inherit to ALL Phases)

**🔴 Mandatory Goals (Blocked if violated):**
- **G001:** Audit Trail Required - Every knowledge merge and orchestrator invocation logged
- **G002:** Core Isolation Mandatory - CORTEX core (Tiers 0-3, core orchestrators) never modified by company extensions
- **G003:** Atomic Operations - All knowledge updates and registry modifications atomic with rollback
- **G004:** Governance Validation - Every phase validates brain-protection-rules.yaml compliance

**🟡 Recommended Goals (Warning if violated):**
- **G005:** Backward Compatibility - All changes support existing CORTEX workflows (no breaking changes)
- **G006:** Performance Budget - Knowledge merge <50ms, orchestrator registry query <20ms
- **G007:** Documentation Complete - Every new component fully documented with examples

---

## 🏗️ Architecture Overview

### Three-Layer Knowledge System

**Layer 1: CORTEX Core Knowledge (Immutable)**
- Location: `docs/knowledge/` (existing)
- Content: Universal best practices, Python patterns, architecture guides
- Priority: Queried first, serves as foundation

**Layer 2: Company Knowledge (Extension)**
- Location: `cortex-brain/tier2/company-knowledge/{company-id}/`
- Content: Company-specific architecture, tech stack, APIs, coding standards
- Priority: Queried second, overrides CORTEX where defined

**Layer 3: Domain Knowledge (Scoped)**
- Location: `cortex-brain/tier2/company-knowledge/{company-id}/domains/{domain}/`
- Content: Domain-specific patterns (Finance, Healthcare, Logistics)
- Priority: Queried last, most specific context

### Orchestrator Registry System

**Registry Structure:**
```
cortex-brain/tier0/orchestrator-registry.yaml
├── core_orchestrators (CORTEX native: TDD, Planning, Toolkit, ADO, Vacuum, etc.)
└── custom_orchestrators (Company-specific: Selenium→Playwright, Legacy Migration, etc.)
```

**Custom Orchestrator Location:**
```
src/orchestrators/custom/
├── {company_id}/
│   ├── {orchestrator_name}_orchestrator.py
│   ├── manifest.yaml (capabilities, trigger patterns, CORTEX inheritance)
│   └── rules.yaml (company-specific governance)
```

**Master Orchestrator Flow:**
1. User request → Master Orchestrator
2. Query registry (core + custom orchestrators)
3. Match trigger patterns → Select orchestrator
4. Load governance (CORTEX rules + company rules)
5. Execute with merged context
6. Log to audit trail

---

## 📅 Implementation Timeline (10 Weeks, 4 Parallel Tracks)

### Track 0: Infrastructure Cleanup (Week 1) 🧹 FOUNDATION HYGIENE

| Phase | Name | Duration | Dependencies | Priority |
|-------|------|----------|--------------|----------|
| **P0** | Vacuum Orchestrator v3 | 1 week | Phase 0 | 🔥 CRITICAL |

**Track Goal:** Clean and optimize CORTEX infrastructure before building new features

**Snowball Effect:** Clean folder structure reduces complexity for all subsequent phases

---

### Track 1: Core Intelligence (Weeks 2-5) 🎯 FOUNDATION

| Phase | Name | Duration | Dependencies | Priority |
|-------|------|----------|--------------|----------|
| **P1** | Company Knowledge Extension | 2 weeks | P0 | 🔥 CRITICAL |
| **P2** | Orchestrator Registry System | 1 week | P1 | 🔥 CRITICAL |
| **P3** | Intelligent Goal Detection | 1 week | P2 | 🔥 HIGH |

**Track Goal:** Establish foundation for business domain integration

---

### Track 2: Business Extensibility (Weeks 4-7) 🚀 CAPABILITY

| Phase | Name | Duration | Dependencies | Priority |
|-------|------|----------|--------------|----------|
| **P4** | Custom Orchestrator Framework | 2 weeks | P2 (parallel with P3) | 🔥 CRITICAL |
| **P5** | Knowledge Merge & Override Logic | 1 week | P1, P4 | 🔥 HIGH |
| **P6** | Selenium→Playwright Reference | 1 week | P4, P5 | 🟡 MEDIUM |

**Track Goal:** Enable companies to extend CORTEX with custom capabilities

---

### Track 3: Quality & UX (Weeks 6-9) ✨ POLISH

| Phase | Name | Duration | Dependencies | Priority |
|-------|------|----------|--------------|----------|
| **P7** | Goal Inheritance Resolver | 1 week | P3 (parallel) | 🔥 HIGH |
| **P8** | TDD Test Harness | 1 week | P7 | 🔥 HIGH |
| **P9** | Plan Viewer + Response Templates | 1 week | P8 | 🟡 MEDIUM |

**Track Goal:** Ensure quality and improve developer experience

---

### Track 4: Integration & Validation (Weeks 9-10) ✅ DELIVERY

| Phase | Name | Duration | Dependencies | Priority |
|-------|------|----------|--------------|----------|
| **P10** | End-to-End Integration Testing | 1 week | P6, P9 | 🔥 CRITICAL |
| **P11** | Performance Optimization & Docs | 1 week | P10 | 🔥 HIGH |

**Track Goal:** Validate entire system and prepare for production

---

## 🎢 Snowball Effect Optimization

### Phase Sequencing Strategy

**Week 1: Infrastructure Cleanup (P0)**
- **P0: Vacuum Orchestrator v3**
- Reorganizes folder structures per CORTEX specifications
- Consolidates redundant reports and artifacts
- Enforces governance rules for clean file management
- **Snowball:** Clean codebase reduces cognitive load and accelerates all subsequent development

**Week 2-3: Foundation Phase (P1)**
- **P1: Company Knowledge Extension**
- Establishes company knowledge folder structure
- Creates `CompanyKnowledgeProvider` class
- **Snowball:** All subsequent phases benefit from company knowledge context + clean folder structure

**Week 4: Registry Infrastructure (P2 + P3 start)**
- **P2: Orchestrator Registry** (completes Week 4)
- **P3: Goal Detection** (starts Week 4, continues Week 5)
- Registry enables custom orchestrators
- **Snowball:** Custom orchestrators can be registered immediately after P2

**Week 5-6: Parallel Execution (P3 + P4)**
- **P3: Goal Detection** (completes Week 5)
- **P4: Custom Orchestrator Framework** (Weeks 5-6, parallel with P3)
- Independent streams maximize throughput
- **Snowball:** Goal detection improves all orchestrators, framework enables customization

**Week 6-7: Business Integration (P5 + P6 + P7 start)**
- **P5: Knowledge Merge Logic** (Week 6)
- **P6: Selenium→Playwright** (Week 7)
- **P7: Goal Inheritance** (starts Week 6, parallel)
- Reference implementation validates entire architecture
- **Snowball:** Selenium→Playwright demonstrates value to stakeholders

**Week 7-9: Quality Pipeline (P7 + P8 + P9)**
- **P7: Goal Inheritance** (completes Week 7)
- **P8: TDD Harness** (Week 8)
- **P9: Plan Viewer + UX** (Week 9)
- Quality gates prevent technical debt
- **Snowball:** TDD ensures all prior work is tested

**Week 9-10: Final Integration (P10 + P11)**
- **P10: E2E Testing** (Week 9)
- **P11: Optimization + Docs** (Week 10)
- End-to-end validation catches integration issues
- **Snowball:** Performance optimization benefits all components

---

## 📦 Deliverables by Track

### Track 0: Infrastructure Cleanup

**P0 Deliverables:**
- `src/orchestrators/vacuum/vacuum_orchestrator_v3.py` (enhanced version)
- Child orchestrator spawning framework
- Folder reorganization engine with CORTEX spec compliance
- Intelligent report consolidator (reduces footprint by 40%+)
- Redundant file detection with AST-based similarity analysis
- Governance rule enforcement middleware
- Integration with cleanup orchestrator and brain protection rules
- Real-time folder analysis dashboard
- Automated backup system (pre-destructive operations)
- Compliance tracker (cortex-brain tier structure validation)
- Recursive directory traversal with pattern matching (glob + regex)
- `cortex-brain/manifests/orchestrators/vacuum-v3-manifest.yaml`
- Vacuum operation audit trail (JSON + SQLite)

---

### Track 1: Core Intelligence

**P1 Deliverables:**
- `cortex-brain/tier2/company-knowledge/` folder structure
- `src/knowledge/company_knowledge_provider.py`
- Company knowledge schema (architecture.md, tech-stack.yaml, api-catalog.json)
- Knowledge query priority logic

**P2 Deliverables:**
- `cortex-brain/tier0/orchestrator-registry.yaml`
- `src/orchestrators/orchestrator_registry.py`
- Master Orchestrator registry integration
- Trigger pattern matching engine

**P3 Deliverables:**
- Goal pattern library (20 common goals)
- Keyword scanner for auto-detection
- Goal suggester with one-click acceptance

---

### Track 2: Business Extensibility

**P4 Deliverables:**
- `src/orchestrators/custom/` namespace
- Custom orchestrator base class
- Manifest schema (capabilities, triggers, inheritance)
- Rules layering system (CORTEX + company)

**P5 Deliverables:**
- Knowledge merge engine (CORTEX + company + domain)
- Conflict resolution logic (CORTEX core wins)
- Override validation (company can't disable blocked rules)
- Merge performance optimization (<50ms)

**P6 Deliverables:**
- `src/orchestrators/custom/reference/selenium_to_playwright_orchestrator.py`
- Selenium AST parser (Python/Java support)
- Playwright code generator (.NET/TypeScript)
- Reference manifest and rules files

---

### Track 3: Quality & UX

**P7 Deliverables:**
- `GoalInheritanceResolver` class
- Epic → Feature → Phase cascading logic
- Goal validation middleware
- Conflict detection and exemption workflow

**P8 Deliverables:**
- TDD test harness (20+ tests)
- Company knowledge tests
- Custom orchestrator tests
- Registry query tests

**P9 Deliverables:**
- Interactive plan-viewer.html
- Response template compliance (WCAG AA)
- Progress tracking with accessibility
- Concise/verbose mode support

---

### Track 4: Integration & Validation

**P10 Deliverables:**
- End-to-end test scenarios (5 scenarios)
- Cross-tenant isolation tests
- Performance benchmarks
- Integration test suite

**P11 Deliverables:**
- Performance optimization report
- Architecture documentation
- API reference guide
- Migration guide for existing users

---

## 🔗 Phase Dependencies (Critical Path)

**Critical Path (Longest):**
```
P0 (1w) → P1 (2w) → P2 (1w) → P4 (2w) → P5 (1w) → P6 (1w) → P10 (1w) → P11 (1w) = 10 weeks
```

**Parallel Streams:**
- **Stream 0:** P0 (Infrastructure Hygiene - enables all others)
- **Stream A:** P0 → P1 → P2 → P4 → P5 → P6 (Foundation + Extensibility)
- **Stream B:** P2 → P3 → P7 → P8 → P9 (Registry + Quality)
- **Stream C:** P10 → P11 (Integration)

**Efficiency Gain:**
- Sequential execution: 15 weeks
- Parallel execution: 10 weeks
- **Time saved: 5 weeks (33% faster)**
- **Bonus:** P0 clean infrastructure reduces debugging time by ~20% across all phases

---

## ✅ Acceptance Criteria (Epic Level)

### Functional Requirements
- [ ] Company knowledge stored in `tier2/company-knowledge/{company-id}/`
- [ ] Knowledge query returns CORTEX defaults + company overrides correctly
- [ ] Custom orchestrators registered in `orchestrator-registry.yaml`
- [ ] Master Orchestrator routes to custom orchestrators via registry
- [ ] Selenium→Playwright orchestrator converts tests successfully
- [ ] Custom orchestrator inherits TDD_ENFORCEMENT from CORTEX
- [ ] Company rules extend (not replace) CORTEX core rules

### Non-Functional Requirements
- [ ] Knowledge merge overhead <50ms (performance)
- [ ] Registry query overhead <20ms (performance)
- [ ] 100% isolation: CORTEX core unmodified by company extensions
- [ ] 95% knowledge merge accuracy (company overrides work correctly)
- [ ] 100% test coverage for new components
- [ ] WCAG AA accessibility compliance

### Documentation Requirements
- [ ] Architecture diagrams (knowledge layers, orchestrator registry)
- [ ] API reference (CompanyKnowledgeProvider, OrchestratorRegistry)
- [ ] Developer guide (creating custom orchestrators)
- [ ] Migration guide (existing users adopting new features)
- [ ] Example company knowledge structure

---

## 🚧 Risks & Mitigations

| Risk | Impact | Mitigation | Owner |
|------|--------|------------|-------|
| **Knowledge merge complexity** | 🔥 HIGH | Cache merged knowledge per company-domain pair | P5 |
| **Registry performance degradation** | 🟡 MEDIUM | Index trigger patterns for O(1) lookup | P2 |
| **Custom orchestrator quality** | 🟡 MEDIUM | Certification process + community ratings | P4 |
| **CORTEX core corruption** | 🔥 HIGH | Physical namespace isolation + validation middleware | P4 |
| **Breaking changes to existing users** | 🟡 MEDIUM | Feature flags + backward compatibility tests | P11 |

---

## 📈 Success Metrics & KPIs

### Adoption Metrics
- **Target:** 3 custom orchestrators implemented by end of epic
- **Target:** 2 companies using knowledge extension layer
- **Target:** 10+ company knowledge documents created

### Performance Metrics
- **Knowledge merge:** <50ms (target: 30ms average)
- **Registry query:** <20ms (target: 10ms average)
- **Custom orchestrator invocation:** <100ms overhead

### Quality Metrics
- **Test coverage:** ≥95% for new components
- **Zero regression:** All existing tests pass
- **Zero CORTEX core modifications:** 100% isolation maintained

### Business Metrics
- **Developer productivity:** 30% faster with company knowledge context
- **Custom orchestrator velocity:** 1 new orchestrator per week after P4
- **Knowledge reuse:** 50% of orchestrator queries use company knowledge

---

## 🎯 Next Steps

### Immediate Actions (Phase 0 - Week 1) 🧹 INFRASTRUCTURE CLEANUP
1. Implement `VacuumOrchestratorV3` with child orchestrator spawning
2. Build folder reorganization engine (CORTEX spec compliance)
3. Create intelligent report consolidator (AST-based deduplication)
4. Implement redundant file detection (similarity analysis)
5. Add governance rule enforcement middleware
6. Integrate with cleanup orchestrator and brain protection rules
7. Build real-time folder analysis dashboard
8. Create automated backup system (pre-destructive operations)
9. Add compliance tracker (tier structure validation)
10. Implement recursive directory traversal (glob + regex patterns)

### Following Actions (Phase 1 - Week 2-3)
1. Create `cortex-brain/tier2/company-knowledge/` folder structure (using cleaned structure from P0)
2. Implement `CompanyKnowledgeProvider` class
3. Design company knowledge schema (architecture.md, tech-stack.yaml)
4. Update CORTEX knowledge library query logic

### Following Actions (Phase 2 - Week 4)
1. Create `orchestrator-registry.yaml` schema
2. Implement `OrchestratorRegistry` class
3. Update Master Orchestrator to query registry
4. Document registry extensibility model

---

## 📚 Related Documentation

- **Architecture Proposal:** `.asif/AI-Learning/cortex-workings/multi-tenant-business-tier-architecture-proposal.md`
- **Brain Protection Rules:** `cortex-brain/brain-protection-rules.yaml`
- **Orchestrator Manifests:** `cortex-brain/manifests/orchestrators/`
- **Knowledge Library:** `docs/knowledge/`
- **Vacuum v2 Reference:** `cortex-brain/manifests/orchestrators/vacuum-v2-manifest.yaml`
- **Cleanup Rules:** `cortex-brain/cleanup-rules.yaml`

---

**Epic Owner:** Asif Hussain  
**Last Updated:** 2026-01-06  
**Status:** ✅ Ready for Phase 0 Execution (Vacuum Orchestrator v3)  
**Estimated Completion:** 2026-03-17 (10 weeks from start)

---

## 📋 Phase 0 Detailed Specification: Vacuum Orchestrator v3

### Overview
Enhanced autonomous file/folder management system that enforces CORTEX governance, consolidates artifacts, and maintains clean architecture.

### Core Capabilities

#### 1. Child Orchestrator Spawning
- Dynamic orchestrator instantiation following CORTEX design patterns
- Orchestrator lifecycle management (spawn → execute → collect results → terminate)
- Resource pooling for parallel folder processing
- Error isolation per child orchestrator

#### 2. Folder Structure Reorganization
- CORTEX specification compliance engine
- Automatic folder structure validation against `cortex-brain/brain-protection-rules.yaml`
- Migration plans for non-compliant structures
- Dry-run mode with preview reports

#### 3. Intelligent Report Consolidation
- AST-based similarity detection (40%+ footprint reduction target)
- Temporal consolidation (merge reports by date ranges)
- Content deduplication (hash-based + semantic similarity)
- Archival of consolidated reports to `cortex-brain/archives/`

#### 4. Redundant File Detection
- Multi-strategy detection:
  - Exact duplicates (SHA256 hashing)
  - Near-duplicates (fuzzy hashing + Levenshtein distance)
  - Semantic duplicates (AST comparison for code files)
- Whitelist management (preserve critical redundancy)
- Interactive deletion mode (confirm before remove)

#### 5. Governance Rule Enforcement
- Real-time validation against brain protection rules
- Automatic fixes for common violations
- Violation reporting with remediation suggestions
- Integration with `cortex-brain/compliance-tracking-schema.sql`

#### 6. Integration Points
- **Cleanup Orchestrator:** Delegates cache/log cleanup tasks
- **Brain Protection Rules:** Enforces SKULL rules during reorganization
- **Planning System:** Creates cleanup plans for complex migrations
- **Tier Structure:** Validates tier0/tier1/tier2/tier3 organization

#### 7. Real-Time Analysis Dashboard
- Live folder statistics (size, file count, compliance score)
- Interactive tree visualization
- Hot-path analysis (frequently accessed folders)
- Compliance metrics dashboard

#### 8. Automated Backup System
- Pre-operation snapshots (before any destructive action)
- Incremental backups to `cortex-brain/backups/vacuum-{timestamp}/`
- Rollback capability (restore from snapshot)
- Retention policy (7 days default)

#### 9. Compliance Tracking
- Tier structure validation (cortex-brain/tier0-3 compliance)
- Document organization checks (reports/, analysis/, summaries/ categorization)
- Naming convention enforcement
- SQLite audit trail (`cortex-brain/tier0/vacuum-compliance.db`)

#### 10. Recursive Traversal
- Glob pattern matching (e.g., `**/*.{json,yaml,md}`)
- Regex filtering for complex patterns
- Ignore rules (`.gitignore` + custom patterns)
- Depth limits and cycle detection

### Technical Architecture

**Module Structure:**
```
src/orchestrators/vacuum/
├── vacuum_orchestrator_v3.py (main orchestrator)
├── child_spawner.py (dynamic orchestrator instantiation)
├── folder_reorganizer.py (CORTEX spec compliance)
├── report_consolidator.py (AST-based deduplication)
├── redundancy_detector.py (multi-strategy detection)
├── governance_enforcer.py (rule validation)
├── backup_manager.py (snapshot/restore)
├── compliance_tracker.py (tier validation)
└── traversal_engine.py (recursive directory walking)
```

**Dependencies:**
- `ast` (Python AST parsing)
- `hashlib` (SHA256 hashing)
- `pathlib` (path manipulation)
- `sqlite3` (audit trail)
- `yaml` (configuration)
- `gitignore_parser` (ignore rules)

### Success Metrics
- ✅ 40%+ reduction in artifact footprint
- ✅ 100% compliance with brain protection rules
- ✅ <1% false positive rate on redundancy detection
- ✅ <5 minutes execution time for typical CORTEX workspace
- ✅ Zero data loss (backup/restore validation)

### Testing Requirements
- Unit tests for each module (95%+ coverage)
- Integration tests with cleanup orchestrator
- End-to-end tests on sample workspace
- Performance benchmarks (large workspace: 10K+ files)
- Rollback validation tests
