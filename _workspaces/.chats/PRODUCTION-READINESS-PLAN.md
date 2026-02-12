# Production Readiness Enhancement Plan
# Generated from: chat01.md digest
# Date: 2026-02-11
# Status: READY FOR IMPLEMENTATION

## Executive Summary

**Source:** Comprehensive production architecture analysis  
**Total Enhancements:** 15 (8 P0, 7 P1)  
**Estimated Effort:** 19 days (12 days if parallelized)  
**Auto-Apply Eligible:** 10 enhancements (confidence ≥9.0)  
**Review Required:** 5 enhancements (confidence 8.0-8.9)

---

## Implementation Phases

### Phase 1: Critical Security Fixes (Week 1)
**Estimated Duration:** 5-7 days  
**Parallelizable:** Yes (4 engineers)

#### P0-001: MCP Server Authentication
- **Status:** 🔴 BLOCKED - No auth on 73 MCP tools
- **Impact:** Any localhost process can deploy to production
- **Effort:** 2 days
- **Owner:** TBD
- **Implementation:**
  - Add token-based auth to cortex/mcp/gateway.py
  - Integrate with VS Code auth flow
  - Update all 73 tool invocations
- **Acceptance Criteria:**
  - [ ] MCP server rejects unauthenticated requests
  - [ ] VS Code provides seamless token flow
  - [ ] All tools protected
  - [ ] Auth audit log created

#### P0-002: Command Injection Fix
- **Status:** 🔴 CRITICAL - Arbitrary code execution possible
- **Impact:** Attackers can execute commands via cortex_refactor
- **Effort:** 4 hours
- **Owner:** TBD
- **Files:**
  - cortex/mcp/tools/refactor_tool.py
  - cortex/refactoring/semantic_refactor.py
- **Implementation:**
  - Replace `subprocess(shell=True)` with argument lists
  - Add input validation
  - Create security tests
- **Acceptance Criteria:**
  - [ ] No shell=True with user input
  - [ ] Argument lists used throughout
  - [ ] Security tests pass

#### P0-005: Global Exception Handler
- **Status:** 🔴 CRITICAL - Single tool crash kills server
- **Impact:** 73 tools unavailable on any exception
- **Effort:** 4 hours
- **Owner:** TBD
- **Files:**
  - cortex/mcp/server.py
  - cortex/mcp/gateway.py
- **Implementation:**
  - Add try-except at gateway level
  - Log exceptions with context
  - Return error responses (don't crash)
- **Acceptance Criteria:**
  - [ ] Exceptions logged, don't crash server
  - [ ] Failed tool returns error response
  - [ ] Server continues processing

#### P0-008: AWS Credentials Cleanup
- **Status:** 🔴 SECURITY - Credentials in git history
- **Impact:** Unauthorized AWS access
- **Effort:** 1 day
- **Owner:** TBD
- **Implementation:**
  - Scan git history for credentials
  - Rotate all exposed credentials in AWS
  - Use environment variables in tests
  - Add pre-commit hook (git-secrets)
- **Acceptance Criteria:**
  - [ ] Exposed credentials rotated
  - [ ] Tests use env vars
  - [ ] Pre-commit hook blocks credentials

---

### Phase 2: Reliability & Performance (Week 2)
**Estimated Duration:** 3 days  
**Parallelizable:** Partial (2 engineers)

#### P0-003: Circuit Breakers
- **Status:** 🟡 RELIABILITY - Git ops can deadlock server
- **Impact:** Slow git operations hang all threads
- **Effort:** 1 day
- **Owner:** TBD
- **Files:**
  - cortex/repositories/git_operations.py
  - cortex/lens/analyzers/*.py
  - cortex/wiring/registry/git_backed_registry.py
- **Implementation:**
  - Add circuit breaker wrapper (pybreaker or custom)
  - 50% failure threshold, 30s trip duration
  - Fail-fast after trip
- **Acceptance Criteria:**
  - [ ] Circuit trips at 50% failure rate
  - [ ] Operations fail fast
  - [ ] Auto-recovery after cooldown

#### P0-006: Async Git Operations
- **Status:** 🟡 PERFORMANCE - Event loop blocked 2-5s
- **Impact:** Server unresponsive during git ops
- **Effort:** 1 day
- **Owner:** TBD
- **Files:**
  - cortex/repositories/git_operations.py
  - cortex/wiring/registry/git_backed_registry.py
- **Implementation:**
  - Use asyncio.to_thread() for git commands
  - Executor pool for concurrent ops
  - Async wrappers for all git functions
- **Acceptance Criteria:**
  - [ ] Git ops don't block event loop
  - [ ] Server responsive during git ops
  - [ ] Concurrent git ops supported

#### P0-004: Debug Race Condition Fix
- **Status:** 🟡 CORRECTNESS - File corruption under concurrency
- **Impact:** Concurrent debug sessions corrupt source files
- **Effort:** 6 hours
- **Owner:** TBD
- **Files:**
  - cortex/orchestrators/support/debug_orchestrator.py
  - cortex/tools/debug_marker_injection.py
- **Implementation:**
  - Add file locking (fcntl on Unix, msvcrt on Windows)
  - Lock acquisition/release logging
  - 5s lock timeout
- **Acceptance Criteria:**
  - [ ] Concurrent debug sessions safe
  - [ ] Lock logging present
  - [ ] Timeout prevents deadlocks

---

### Phase 3: Operability & Monitoring (Week 2-3)
**Estimated Duration:** 2 days  
**Parallelizable:** Yes (2 engineers)

#### P0-007: Liveness Probe
- **Status:** 🟡 OPERABILITY - Deadlocks undetectable
- **Impact:** Frozen servers appear healthy
- **Effort:** 3 hours
- **Owner:** TBD
- **Files:**
  - cortex/mcp/server.py
  - deployment/health_checks.yaml
- **Implementation:**
  - Add /health/live endpoint
  - Timestamp validation (fail if >30s old)
  - Thread pool health check
- **Acceptance Criteria:**
  - [ ] Liveness fails when frozen
  - [ ] Detects thread pool exhaustion
  - [ ] Monitoring alerts on failure

#### P1-013: Structured Logging
- **Status:** 🟢 ENHANCEMENT - Manual log analysis slow
- **Impact:** 30+ min MTTR
- **Effort:** 1 day
- **Owner:** TBD
- **Files:**
  - cortex/*/*.py (all modules)
- **Implementation:**
  - Migrate to structlog
  - JSON output format
  - Structured fields: timestamp, level, orchestrator, tool, duration
- **Acceptance Criteria:**
  - [ ] All logs in JSON
  - [ ] Queryable via jq
  - [ ] Log aggregation ready

#### P1-015: Distributed Tracing
- **Status:** 🟢 ENHANCEMENT - Multi-orchestrator failures hard to diagnose
- **Impact:** Long MTTR for complex failures
- **Effort:** 2 days
- **Owner:** TBD
- **Files:**
  - cortex/mcp/server.py
  - cortex/orchestrators/master_orchestrator.py
  - cortex/orchestrators/*/*.py
- **Implementation:**
  - OpenTelemetry integration
  - Trace propagation across orchestrators
  - Jaeger exporter
- **Acceptance Criteria:**
  - [ ] Request traced end-to-end
  - [ ] Orchestrator transitions visible
  - [ ] Jaeger UI shows execution path

---

### Phase 4: Authorization & Security (Week 3)
**Estimated Duration:** 3 days  
**Parallelizable:** Partial (2 engineers)

#### P1-011: RBAC Implementation
- **Status:** 🟡 SECURITY - Unauthorized deployments possible
- **Impact:** Any user can deploy to production
- **Effort:** 2 days
- **Owner:** TBD
- **Files:**
  - cortex/mcp/gateway.py
  - cortex/mcp/tools/deploy_tool.py
- **Implementation:**
  - Define roles: read-only, developer, operator, admin
  - Tool-to-role mapping
  - Authorization at gateway level
- **Acceptance Criteria:**
  - [ ] Only admin can deploy to prod
  - [ ] RBAC enforced at gateway
  - [ ] Authorization audit log

#### P1-014: Path Traversal Fix
- **Status:** 🟡 SECURITY - Arbitrary file reads
- **Impact:** Attackers can read sensitive files
- **Effort:** 4 hours
- **Owner:** TBD
- **Files:**
  - cortex/mcp/tools/onboard_tool.py
  - cortex/orchestrators/support/repository_onboarding_orchestrator.py
- **Implementation:**
  - Validate paths (reject ..)
  - Resolve against workspace root
  - Security tests
- **Acceptance Criteria:**
  - [ ] Rejects paths with ..
  - [ ] Workspace boundary enforced
  - [ ] Security tests pass

---

### Phase 5: Configuration & State Management (Week 4)
**Estimated Duration:** 3 days  
**Parallelizable:** Yes (2 engineers)

#### P1-009: Configuration Drift Fix
- **Status:** 🟡 RELIABILITY - Inconsistent configs
- **Impact:** Runtime failures from config mismatch
- **Effort:** 2 days
- **Owner:** TBD
- **Files:**
  - cortex/__wiring_contract__.yaml
  - cortex/wiring/specifications/wiring.yaml
  - cortex/wiring/registry/git_backed_registry.py
- **Implementation:**
  - Designate wiring.yaml as single source of truth
  - Use __wiring_contract__.yaml as validation schema only
  - Startup validation
- **Acceptance Criteria:**
  - [ ] Single config file
  - [ ] Contract validates at startup
  - [ ] No drift tests pass

#### P1-010: Session Persistence
- **Status:** 🟡 RELIABILITY - State lost on restart
- **Impact:** MCP restart causes retry loops
- **Effort:** 1 day
- **Owner:** TBD
- **Files:**
  - cortex/interaction/comprehension_session.py
  - cortex/mcp/server.py
- **Implementation:**
  - Redis-backed session store
  - TTL-based expiration (24h)
  - Session recovery logic
- **Acceptance Criteria:**
  - [ ] Sessions persist across restarts
  - [ ] TTL prevents unbounded growth
  - [ ] Recovery tests pass

---

### Phase 6: Scalability & Resource Management (Week 4)
**Estimated Duration:** 1 day

#### P1-012: Event History Bounds
- **Status:** 🟡 SCALABILITY - Unbounded memory growth
- **Impact:** Memory leak → OOM crashes
- **Effort:** 1 day
- **Owner:** TBD
- **Files:**
  - cortex/orchestrators/event_bus.py
  - cortex/phase_management/event_history.py
- **Implementation:**
  - Ring buffer with max 10K events
  - TTL-based expiration (7 days)
  - Memory usage monitoring
- **Acceptance Criteria:**
  - [ ] Event history capped at 10K
  - [ ] Old events expire
  - [ ] Memory usage bounded

---

## Architectural Cleanup (Future Quarters)

### Deprecation Candidates
- **SeleniumPlaywrightOrchestrator** - 0 references, replace with Playwright-only
- **WorkflowOrchestrator** - Superseded by OrchestratorEventBus
- **MigrationOrchestrator** - One-time use, now obsolete

### Consolidation Opportunities
- **ConversationOrchestrator** - 70% overlap with InteractionOrchestrator
  - Action: Merge into InteractionOrchestrator
  - Effort: 2 days

### File Structure Cleanup
- **cortex/orchestrators/** - 300+ misplaced files
  - Action: Reorganize by domain (core, support, domain)
  - Effort: 1 week

---

## Risk Assessment

### Implementation Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| **Auth breaks VS Code integration** | Medium | High | Thorough integration testing, rollback plan |
| **Async git ops introduce new race conditions** | Low | High | Comprehensive concurrency tests |
| **Circuit breaker too aggressive** | Medium | Medium | Tunable thresholds, monitoring |
| **Redis dependency adds complexity** | Low | Medium | Optional feature flag, fallback to in-memory |
| **RBAC blocks legitimate users** | Medium | Medium | Granular permissions, audit logging |

### Production Impact Assessment

| Phase | Production Impact | Rollout Strategy |
|-------|------------------|------------------|
| **Phase 1 (Security)** | High (auth changes) | Canary deploy, VS Code beta testing |
| **Phase 2 (Reliability)** | Medium (behavior changes) | Feature flags, gradual rollout |
| **Phase 3 (Operability)** | Low (additive only) | Deploy immediately |
| **Phase 4 (Authorization)** | Medium (access changes) | Granular permissions first, then enforce |
| **Phase 5 (Configuration)** | Medium (schema changes) | Blue-green deployment |
| **Phase 6 (Scalability)** | Low (internal only) | Deploy immediately |

---

## Success Metrics

### Phase 1 Metrics (Security)
- [ ] 0 unauthenticated MCP requests succeed
- [ ] 0 command injection vulnerabilities in security scan
- [ ] 0 AWS credentials in git history (new commits)
- [ ] 100% exception handling coverage in MCP layer

### Phase 2 Metrics (Reliability)
- [ ] 0 server lockups from git operations (30-day period)
- [ ] <100ms P99 latency for git operations
- [ ] 0 file corruptions from concurrent debug sessions

### Phase 3 Metrics (Operability)
- [ ] <5 min MTTR for common failures (down from 30+ min)
- [ ] 100% liveness probe detection rate for deadlocks
- [ ] 100% logs queryable via structured fields

### Phase 4 Metrics (Authorization)
- [ ] 0 unauthorized production deployments
- [ ] 100% tool invocations authorized and logged

### Phase 5 Metrics (Configuration)
- [ ] 0 configuration drift incidents
- [ ] 0 session state lost on MCP restart

### Phase 6 Metrics (Scalability)
- [ ] Event history memory usage <50MB (down from unbounded)
- [ ] 0 OOM crashes from event history growth

---

## Implementation Schedule

```
Week 1: Phase 1 (Security Fixes)
├─ Mon-Tue: P0-001 MCP Authentication
├─ Wed AM: P0-002 Command Injection Fix
├─ Wed PM: P0-005 Global Exception Handler
└─ Thu-Fri: P0-008 AWS Credentials Cleanup

Week 2: Phase 2 (Reliability) + Phase 3 (Operability)
├─ Mon: P0-003 Circuit Breakers
├─ Tue: P0-006 Async Git Operations
├─ Wed AM: P0-004 Debug Race Condition
├─ Wed PM: P0-007 Liveness Probe
├─ Thu: P1-013 Structured Logging
└─ Fri: P1-015 Distributed Tracing (Day 1)

Week 3: Phase 4 (Authorization) + Phase 3 cont'd
├─ Mon: P1-015 Distributed Tracing (Day 2)
├─ Tue-Wed: P1-011 RBAC Implementation
└─ Thu AM: P1-014 Path Traversal Fix

Week 4: Phase 5 (Configuration) + Phase 6 (Scalability)
├─ Mon-Tue: P1-009 Configuration Drift Fix
├─ Wed: P1-010 Session Persistence
└─ Thu: P1-012 Event History Bounds

Week 5: Integration Testing & Validation
├─ Mon-Tue: End-to-end testing
├─ Wed: Performance benchmarking
├─ Thu: Security audit
└─ Fri: Production deployment planning
```

---

## Next Actions

### Immediate (Today)
1. **Create GitHub Issues** - One issue per enhancement (15 total)
2. **Assign Owners** - Allocate engineers to phases
3. **Setup Tracking** - Project board with phases
4. **Schedule Kickoff** - Team meeting to review plan

### This Week
1. **Begin Phase 1** - Start with P0-002 (command injection, 4h quick win)
2. **MCP Auth Design** - Architect VS Code integration approach
3. **Security Audit** - Scan entire codebase for similar issues
4. **Setup Monitoring** - Baseline current metrics

### Documentation Updates
- [ ] Update `.github/prompts/cortex-architect.prompt.md` with new security requirements
- [ ] Add security section to `cortex/knowledge/best-practices/`
- [ ] Create runbook for each P0 incident response
- [ ] Document RBAC role definitions and tool mappings

---

## References

### Source Materials
- **Original Analysis:** `_workspaces/.chats/chat01.md`
- **Digest YAML:** `_workspaces/.chats/chat01-digest.yaml`
- **System Manifest:** `_workspaces/cortex-architecture/CORTEX_SYSTEM_MANIFEST.md`

### Related Documentation
- **MCP Security:** `.github/prompts/MCP-SETUP-GUIDE.md`
- **Governance Rules:** `cortex-registry/_cortex-master/governance/core-rules.yaml`
- **Best Practices:** `cortex/knowledge/best-practices/security-first.yaml`

---

**Plan Status:** ✅ READY FOR IMPLEMENTATION  
**Confidence:** 9.5/10  
**Estimated Effort:** 19 days (12 days parallelized)  
**Expected Impact:** High (addresses 8 P0 critical issues)
