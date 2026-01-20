# Detailed AC-ID Inventory: Next 9 Implementation Phases

**Date**: 2026-01-18  
**Total AC-IDs**: 71 across 9 phases  
**Status**: ✅ Ready for implementation  

---

## Phase 1: PHASE-03 - Safety, Reliability & Observability (6 ACs)

**Requirements**: PHASE-02 (LOCKED & COMPLETE) ✓  
**Blocks**: PHASE-04  
**Estimated Hours**: 0 (estimated in ACs)  
**Description**: Production Reliability, Graceful Degradation, Circuit Breaker Patterns, OpenTelemetry Metrics Integration

| # | AC-ID | Title | Description | Estimated Hours | Tests |
|---|-------|-------|-------------|-----------------|-------|
| 1 | TBD | Production Reliability Framework | Framework for handling production failures gracefully | TBD | TBD |
| 2 | TBD | Graceful Degradation Strategy | Implement degradation patterns for service disruptions | TBD | TBD |
| 3 | TBD | Circuit Breaker Patterns Implementation | Circuit breaker + fallback mechanisms | TBD | TBD |
| 4 | TBD | Fallback Mechanisms | Cascading fallback for critical paths | TBD | TBD |
| 5 | TBD | OpenTelemetry Metrics Integration | OTEL integration for production observability | TBD | TBD |
| 6 | TBD | Observability Dashboard | Real-time metrics and health visualization | TBD | TBD |

---

## Phase 2: PHASE-04 - Production Hardening & Security (12 ACs)

**Requirements**: PHASE-03 (must complete)  
**Blocks**: PHASE-05  
**Estimated Hours**: 0  
**Description**: Security Hardening, Secret Redaction, Hash Verification, Cross-File Coherence Validation

| # | AC-ID | Category | Title | Description | Estimated Hours | Tests |
|---|-------|----------|-------|-------------|-----------------|-------|
| 1 | TBD | Security | Security Framework | Production security hardening framework | TBD | TBD |
| 2 | TBD | Security | Secret Management | Secret detection and redaction | TBD | TBD |
| 3 | TBD | Security | Credential Protection | Secure credential handling | TBD | TBD |
| 4 | TBD | Security | API Key Protection | API key security patterns | TBD | TBD |
| 5 | TBD | Verification | Hash Verification | Hash chain integrity verification | TBD | TBD |
| 6 | TBD | Verification | Hash Validation | Continuous hash validation | TBD | TBD |
| 7 | TBD | Verification | Integrity Checks | Data integrity verification | TBD | TBD |
| 8 | TBD | Coherence | Cross-File Validation | Cross-file consistency checks | TBD | TBD |
| 9 | TBD | Coherence | Coherence Enforcement | Enforce coherence across modules | TBD | TBD |
| 10 | TBD | Coherence | Sync Validation | Synchronization validation | TBD | TBD |
| 11 | TBD | Compliance | Security Audit | Security audit trail | TBD | TBD |
| 12 | TBD | Compliance | Compliance Report | Compliance reporting | TBD | TBD |

---

## Phase 3: PHASE-05 - Brittleness Fixes & Stabilization (17 ACs)

**Requirements**: PHASE-04 (must complete) + PHASE-PARALLEL (must complete)  
**Blocks**: None (foundation complete)  
**Estimated Hours**: 0  
**Description**: Import Path Resolution, Cross-Platform Compatibility, Test Stabilization, Final Verification

| # | AC-ID | Category | Title | Description | Estimated Hours | Tests |
|---|-------|----------|-------|-------------|-----------------|-------|
| 1 | TBD | Import Resolution | Import Path Analysis | Analyze import path issues | TBD | TBD |
| 2 | TBD | Import Resolution | Path Resolution | Implement portable path resolution | TBD | TBD |
| 3 | TBD | Import Resolution | Relative Imports | Fix relative import patterns | TBD | TBD |
| 4 | TBD | Import Resolution | Import Validation | Validate all imports | TBD | TBD |
| 5 | TBD | Platform | Windows Compatibility | Windows path compatibility | TBD | TBD |
| 6 | TBD | Platform | macOS Compatibility | macOS path compatibility | TBD | TBD |
| 7 | TBD | Platform | Linux Compatibility | Linux path compatibility | TBD | TBD |
| 8 | TBD | Platform | Platform Abstraction | Cross-platform abstraction layer | TBD | TBD |
| 9 | TBD | Platform | File Operations | Cross-platform file operations | TBD | TBD |
| 10 | TBD | Testing | Test Flakiness | Fix flaky tests | TBD | TBD |
| 11 | TBD | Testing | Test Stability | Test stability improvements | TBD | TBD |
| 12 | TBD | Testing | Test Isolation | Test isolation enforcement | TBD | TBD |
| 13 | TBD | Testing | Cleanup | Test cleanup procedures | TBD | TBD |
| 14 | TBD | Verification | Final Testing | Final comprehensive test suite | TBD | TBD |
| 15 | TBD | Verification | Smoke Tests | Smoke test suite | TBD | TBD |
| 16 | TBD | Verification | Integration Tests | Integration test suite | TBD | TBD |
| 17 | TBD | Verification | Readiness Check | Production readiness verification | TBD | TBD |

---

## Phase 4: PHASE-PARALLEL - Folder Migration & Organization (3 ACs)

**Requirements**: PHASE-01 (LOCKED & COMPLETE) ✓  
**Must Complete Before**: PHASE-05  
**Execution**: Parallel with PHASE-02, PHASE-03, PHASE-04 (non-blocking)  
**Estimated Hours**: 0  
**Description**: Nested Folder Structure Organization, Import Updates, Non-Blocking Parallel Execution

| # | AC-ID | Title | Description | Estimated Hours | Tests |
|---|-------|-------|-------------|-----------------|-------|
| 1 | TBD | Folder Structure Planning | Design nested folder structure | TBD | TBD |
| 2 | TBD | Migration Script | Implement folder migration script | TBD | TBD |
| 3 | TBD | Import Updates | Update all import paths | TBD | TBD |

---

## Phase 5: PHASE-21 - Intelligent Knowledge Protocol (8 ACs)

**Requirements**: PHASE-20-TEMPLATE-CONTENT ✓  
**Estimated Hours**: 39 total  
**Priority**: P1  
**Description**: Unified knowledge access layer, intelligent routing, change detection, bulk ingestion

### AC-IKP-001: KnowledgeProvider Protocol (2 ACs)

| AC-ID | Title | Description | Hours | Tests |
|-------|-------|-------------|-------|-------|
| AC-IKP-001-01 | Protocol Definition | Define typing.Protocol interface for knowledge backends | 2 | 10 |
| AC-IKP-001-02 | Compliance Verification | Verify both repositories satisfy protocol + add tests | 1 | 8 |

### AC-IKP-002: IntelligentKnowledgeRouter (2 ACs)

| AC-ID | Title | Description | Hours | Tests |
|-------|-------|-------------|-------|-------|
| AC-IKP-002-01 | Router Implementation | Query-aware router with confidence scoring | 4 | 20 |
| AC-IKP-002-02 | Master Integration | Integrate into MasterOrchestrator | 2 | 12 |

### AC-IKP-003: Change Detection Service (2 ACs)

| AC-ID | Title | Description | Hours | Tests |
|-------|-------|-------------|-------|-------|
| AC-IKP-003-01 | Service Implementation | Monitor for schema drift, semantic shift, anomalies | 6 | 25 |
| AC-IKP-003-02 | Alert System | Configure thresholds, notification channels | 2 | 10 |

### AC-IKP-004: Ingestion & Refinement (2 ACs)

| AC-ID | Title | Description | Hours | Tests |
|-------|-------|-------------|-------|-------|
| AC-IKP-004-01 | Pipeline Architecture | Extensible ingestion pipeline with registry pattern | 8 | 30 |
| AC-IKP-004-02 | RefinementEngine | Entity extraction, deduplication, CORTEX optimization | 6 | 20 |

### AC-IKP-005: Unified Facade (1 AC)

| AC-ID | Title | Description | Hours | Tests |
|-------|-------|-------------|-------|-------|
| AC-IKP-005-01 | UnifiedKnowledgeService | Single entry point facade with cross-backend aggregation | 4 | 15 |

**Total**: 31 hours + 150 tests

---

## Phase 6: PHASE-22 - MCP Protocol Compliance (8 ACs)

**Requirements**: PHASE-21 (must complete) or PHASE-02 (minimum)  
**Priority**: P0 (CRITICAL - MCP Protocol Compliance)  
**Description**: Proper Model Context Protocol compliance, tool standardization, full tool exposure

| # | AC-ID | Title | Description | Estimated Hours | Tests |
|---|-------|-------|-------------|-----------------|-------|
| 1 | TBD | Protocol Compliance | Full MCP protocol implementation | TBD | TBD |
| 2 | TBD | Tool Standardization | Standardize tool definitions | TBD | TBD |
| 3 | TBD | Tool Registry | Implement tool registry | TBD | TBD |
| 4 | TBD | Tool Discovery | Tool discovery mechanism | TBD | TBD |
| 5 | TBD | Tool Execution | Tool execution framework | TBD | TBD |
| 6 | TBD | Error Handling | MCP error handling | TBD | TBD |
| 7 | TBD | Validation | Tool validation | TBD | TBD |
| 8 | TBD | Integration | MCP integration tests | TBD | TBD |

---

## Phase 7: PHASE-23 - Complexity-Aware Confirmation Gate (4 ACs)

**Requirements**: PHASE-22 (must complete)  
**Estimated Hours**: 23 total  
**Description**: Intelligent confirmation gate using complexity analysis, LENS confidence, relationship analysis

### AC-CONF-001: Complexity Assessment

| AC-ID | Title | Description | Hours | Tests |
|-------|-------|-------------|-------|-------|
| AC-CONF-001-01 | Complexity Engine | Aggregate LENS confidence + relationships into 5-level scale | 8 | 12 |

### AC-CONF-002: Approval Gate Logic

| AC-ID | Title | Description | Hours | Tests |
|-------|-------|-------------|-------|-------|
| AC-CONF-002-01 | Gate Logic | Confidence-based approval matrix with auto-approval | 6 | 8 |

### AC-CONF-003: Master Orchestrator Integration

| AC-ID | Title | Description | Hours | Tests |
|-------|-------|-------------|-------|-------|
| AC-CONF-003-01 | Master Integration | Insert Stage 2.5 into ConversationProtocol | 5 | 6 |

### AC-CONF-004: Governance & Audit

| AC-ID | Title | Description | Hours | Tests |
|-------|-------|-------------|-------|-------|
| AC-CONF-004-01 | Rules & Logging | 5 governance rules + audit trail | 4 | 4 |

**Total**: 23 hours + 30 tests

---

## Phase 8: PHASE-DEPLOYMENT - Universal Deployment (10 ACs)

**Requirements**: PHASE-22-MCP-PROTOCOL-COMPLIANCE (must complete)  
**Estimated Hours**: 60+ total  
**Priority**: P0 (CRITICAL)  
**Description**: Single-command installation, multi-repo deployment, production-ready deployment system

### AC-DEPLOY-001: Installation & Bootstrap (3 ACs)

| AC-ID | Title | Description | Hours | Tests |
|-------|-------|-------------|-------|-------|
| AC-DEPLOY-001-01 | Config Management | Environment-specific configs (dev/staging/prod) | 8 | 12 |
| AC-DEPLOY-001-02 | Blue-Green Setup | Dual environment for zero-downtime deployments | 12 | 15 |
| AC-DEPLOY-001-03 | MCP Registration | MCP tool registration in client | TBD | TBD |

### AC-DEPLOY-002: Multi-Repo Architecture (3 ACs)

| AC-ID | Title | Description | Hours | Tests |
|-------|-------|-------------|-------|-------|
| AC-DEPLOY-002-01 | Orchestration | CI/CD pipeline automation | 10 | 18 |
| AC-DEPLOY-002-02 | Rollback | Emergency rollback with point-in-time recovery | 8 | 14 |
| AC-DEPLOY-002-03 | Context Switching | Multi-repo context switching | TBD | TBD |

### AC-DEPLOY-003: Upgrade & Monitoring (2 ACs)

| AC-ID | Title | Description | Hours | Tests |
|-------|-------|-------------|-------|-------|
| AC-DEPLOY-003-01 | Monitoring | Production monitoring & alerting | 12 | 16 |
| AC-DEPLOY-003-02 | Health Checks | Health checks & readiness validation | 6 | 10 |

### AC-DEPLOY-004: Production Readiness (2 ACs)

| AC-ID | Title | Description | Hours | Tests |
|-------|-------|-------------|-------|-------|
| AC-DEPLOY-004-01 | Documentation | Release notes & user documentation | 8 | 8 |
| AC-DEPLOY-004-02 | User Training | Training materials & communication plan | 4 | 6 |

### SECTION D: Not yet detailed (2 ACs)

| AC-ID | Title | Description | Hours | Tests |
|-------|-------|-------------|-------|-------|
| AC-DEPLOY-005-01 | Compliance | Governance compliance verification | 6 | 10 |
| AC-DEPLOY-005-02 | Sign-Off | Production acceptance & sign-off | 6 | 8 |

**Total**: 80+ hours + 117 tests

---

## Phase 9: PHASE-REMEDIATION-07 - MCP Tool Exposure Gap (3 ACs)

**Requirements**: PHASE-REMEDIATION-06 (LOCKED & COMPLETE) ✓  
**Estimated Hours**: 8 total  
**Priority**: P1  
**Parallel Capable**: Yes (non-blocking)  
**Description**: Add @mcp_tool decorator, expose domain orchestrator operations, /list-tools endpoint

| AC-ID | Title | Description | Estimated Hours | Tests |
|-------|-------|-------------|-----------------|-------|
| AC-MCP-EXPOSURE-001 | @mcp_tool Decorator | Add @mcp_tool to get_relevant_business_knowledge_for_operation() | TBD | 4+ |
| AC-MCP-EXPOSURE-002 | Domain Operations | Expose domain orchestrator operations (15+ methods) as MCP tools | TBD | 10+ |
| AC-MCP-EXPOSURE-003 | Tool Discovery | Implement /list-tools MCP endpoint for programmatic discovery | TBD | 5+ |

**Impact**: 
- MCP tool count: 16 → 32+ tools
- Programmatic tool discovery enabled
- Domain orchestrators fully exposed

---

## Summary Statistics

### AC-ID Inventory

| Phase | AC Count | Est. Hours | Est. Tests | Priority |
|-------|----------|-----------|-----------|----------|
| PHASE-03 | 6 | ? | ? | CRITICAL |
| PHASE-04 | 12 | ? | ? | CRITICAL |
| PHASE-05 | 17 | ? | ? | CRITICAL |
| PHASE-PARALLEL | 3 | ? | ? | CRITICAL |
| PHASE-21 | 8 | 39 | 150+ | P1 |
| PHASE-22 | 8 | ? | ? | P0 |
| PHASE-23 | 4 | 23 | 30+ | P1 |
| PHASE-DEPLOYMENT | 10 | 80+ | 117+ | P0 |
| PHASE-REMEDIATION-07 | 3 | 8 | 19+ | P1 |
| **TOTAL** | **71** | **190+** | **316+** | **MIXED** |

### Execution Path

```
Week 1: PHASE-03 (6 ACs)
        PHASE-PARALLEL (3 ACs - parallel)
        ↓
Week 2: PHASE-04 (12 ACs)
        PHASE-REMEDIATION-07 (3 ACs - parallel)
        ↓
Week 3: PHASE-05 (17 ACs)
        ↓
Week 4: PHASE-21 (8 ACs) + PHASE-22 (8 ACs)
        ↓
Week 5: PHASE-23 (4 ACs)
        ↓
Week 6: PHASE-DEPLOYMENT (10 ACs)

Total Estimated: 5-6 weeks
```

---

**Ready to implement!** Follow cortex-builder.prompt.md workflow for each AC-ID.
