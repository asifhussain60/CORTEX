# DEPLOYMENT PHASE IMPLEMENTATION PLAN
**Reference:** Issue #7 - Deployment gaps redesign  
**Author:** Asif Hussain | **Created:** January 19, 2026  
**Timeline:** Weeks 1-4 (Jan 20 - Feb 16, 2026)  
**Status:** ⏳ AWAITING APPROVAL (see success criteria below)

---

## EXECUTIVE SUMMARY - IMPLEMENTATION ROADMAP

This document translates the **DEPLOYMENT-PHASE-REDESIGN-20260119.md** architecture into actionable implementation tasks with estimated effort, dependencies, and deliverables.

### Quick Facts
- **Total Effort:** 18-20 engineer-days across 4 weeks
- **Parallel Work:** Yes (8 tasks can run in parallel after Week 1)
- **Critical Path:** Session Context → Repo Isolation → Integration Tests
- **Production Go-Live:** Feb 16, 2026 (subject to approval)
- **Rollback Risk:** LOW (phased approach, feature flags available)

### Approval Required
✅ **Decision Point:** Approve 3-Tier Architecture before starting Week 1?

---

## TASK BREAKDOWN & WEEKLY SCHEDULE

### WEEK 1: Foundation (Jan 20-24)

#### TASK-1: Session Context Injection (Days 1-2)
**Lead:** Backend engineer  
**Effort:** 1-2 days  
**Deliverable:** Enhanced `src/mcp/server.py` with session support

```yaml
Scope:
  New Classes:
    - MCPSession: Holds repo_id, repo_path, session_id, prompt_version
    - SessionManager: Create/retrieve/destroy sessions
  
  New Methods:
    - MCPServer.create_session(repo_config) → MCPSession
    - MCPServer.handle_tool_call() extended with __cortex_session__ injection
    - Orchestrators extract repo_id from context
  
  Database Changes:
    - NEW TABLE: sessions (session_id, repo_id, repo_path, created_at)
    - Modify audit_log to include repo_id (foreign key to sessions)

Dependencies: None (ready to start immediately)

Acceptance Criteria:
  ✓ Session created with unique session_id
  ✓ repo_id extracted from session and passed to orchestrators
  ✓ Audit entries include repo_id
  ✓ Unit tests: 100% coverage of MCPSession, SessionManager
  ✓ No regression: existing MCP tests pass

Verification:
  - pytest tests/unit/test_mcp_session.py -v
  - pytest tests/unit/test_mcp_server.py -v
  - Coverage report ≥95%
```

**Files to Create/Modify:**
- `src/mcp/server.py` (extend MCPServer class, add SessionManager)
- `src/mcp/models/session.py` (NEW - MCPSession class)
- `tests/unit/test_mcp_session.py` (NEW - unit tests)
- Database migration: `migrations/001_add_session_support.sql`

---

#### TASK-2: Health Check Endpoint (Day 3)
**Lead:** Backend engineer  
**Effort:** 1 day  
**Deliverable:** MCP `/health` and `/config/prompt-version` endpoints

```yaml
Scope:
  New Endpoints:
    GET /health
      Response: { status: ready, version: 1.0.0, db: connected, ... }
    
    GET /config/prompt-version
      Response: { current: 1.0.0, available: [...], recommended: 1.0.0 }
  
Dependencies: None (independent of TASK-1)

Acceptance Criteria:
  ✓ /health returns 200 with valid schema
  ✓ /health detects DB connection failure
  ✓ /health checks orchestrator registration
  ✓ /config/prompt-version returns current version
  ✓ Endpoints have <100ms latency (cached)
  ✓ Unit tests: 100% coverage

Verification:
  - curl http://127.0.0.1:8000/health
  - pytest tests/unit/test_mcp_health.py -v
```

**Files to Create/Modify:**
- `src/mcp/server.py` (add routes)
- `tests/unit/test_mcp_health.py` (NEW - endpoint tests)

---

#### TASK-3: Service Discovery (Day 4-5)
**Lead:** DevOps engineer  
**Effort:** 1 day  
**Deliverable:** Discovery logic (env var → config file → default)

```yaml
Scope:
  Discovery Sequence:
    1. Check env var: CORTEX_MCP_ENDPOINT
    2. Read cortex-config.yaml: cortex.hub_endpoint
    3. Default: 127.0.0.1:8000
  
  Implementation:
    - New module: cortex/core/discovery/mcp_discovery.py
    - Function: resolve_mcp_endpoint() → (host, port)
    - Function: validate_endpoint() → bool
    - Function: get_hub_health() → dict
  
Dependencies: TASK-2 (needs /health endpoint to test)

Acceptance Criteria:
  ✓ Env var takes precedence
  ✓ Config file used if env var missing
  ✓ Default used if config file missing
  ✓ Invalid endpoints detected (clear error)
  ✓ Health check validates endpoint connectivity
  ✓ Unit tests: 100% coverage

Verification:
  - pytest tests/unit/test_mcp_discovery.py -v
  - Export CORTEX_MCP_ENDPOINT=invalid && pytest (should detect error)
```

**Files to Create/Modify:**
- `cortex/core/discovery/mcp_discovery.py` (NEW)
- `tests/unit/test_mcp_discovery.py` (NEW)
- `src/mcp/client.py` (use discovery on connect)

---

#### WEEK 1 SYNC POINT (End of Day 5)
- [ ] TASK-1 complete + tests passing
- [ ] TASK-2 complete + /health endpoint working
- [ ] TASK-3 complete + discovery logic tested
- **Go/No-Go:** Can proceed to TASK-4?

---

### WEEK 2: Configuration & Versioning (Jan 27-31)

#### TASK-4: Prompt Version Manager (Days 1-3)
**Lead:** Backend engineer  
**Effort:** 2-3 days  
**Deliverable:** Version management system + cortex-brain/releases/ structure

```yaml
Scope:
  File Structure (NEW):
    cortex-brain/
      releases/
        v1.0.0/
          CORTEX.prompt.md
          CORTEX.prompt.schema.yaml  (version metadata)
        v1.1.0/
          CORTEX.prompt.md
          CORTEX.prompt.schema.yaml  (future)
  
  Version Manifest:
    cortex-brain/tier0/prompt-versions.yaml
    Contains:
      - current: 1.0.0
      - available: [1.0.0, 1.1.0 (future)]
      - deprecated: []
      - compatibility_matrix: {repo_can_use: [versions]}
  
  Implementation:
    - New class: PromptVersionManager
    - Methods:
      * get_current_version() → string
      * is_compatible(repo_version, hub_version) → bool
      * negotiate_version(repo_version) → string or error
      * get_prompt_content(version) → string
  
  Database:
    - NEW TABLE: prompt_versions (version, content_hash, released_date, deprecated_date)
    - Audit: Log every version change
  
Dependencies: TASK-3 (needs endpoint discovery for version checks)

Acceptance Criteria:
  ✓ v1.0.0 prompt released with hash
  ✓ Version negotiation works (repo can request v1.0)
  ✓ Incompatible version rejected with clear error
  ✓ Version history auditable
  ✓ Unit tests: 100% coverage

Verification:
  - pytest tests/unit/test_prompt_version_manager.py -v
  - python -c "from cortex.core.versioning import PromptVersionManager; m = PromptVersionManager(); print(m.get_current_version())"
```

**Files to Create/Modify:**
- `src/versioning/prompt_version_manager.py` (NEW)
- `cortex-brain/releases/v1.0.0/CORTEX.prompt.md` (copy from docs/)
- `cortex-brain/tier0/prompt-versions.yaml` (NEW)
- `tests/unit/test_prompt_version_manager.py` (NEW)

---

#### TASK-5: Repo Registry System (Days 2-3, parallel with TASK-4)
**Lead:** Backend engineer  
**Effort:** 1-2 days  
**Deliverable:** Repo registry + lookup logic

```yaml
Scope:
  Registry File:
    cortex-brain/tier0/repo-registry.yaml
    Example:
      repositories:
        - repo_id: api-service
          repo_name: CORTEX API
          repo_type: backend
          expected_path: ../repos/cortex-api
          registered_date: 2026-01-20
          status: active
        - repo_id: ui-app
          repo_name: CORTEX UI
          repo_type: frontend
          expected_path: ../repos/cortex-ui
          registered_date: 2026-01-20
          status: active
  
  Implementation:
    - New class: RepoRegistry
    - Methods:
      * register_repo(repo_id, repo_config) → bool
      * get_repo(repo_id) → RepoConfig
      * list_repos() → List[RepoConfig]
      * validate_isolation(repo_id, file_path) → bool
  
  Database:
    - NEW TABLE: repositories (repo_id, repo_name, status, registered_date)
  
Dependencies: TASK-1 (needs session management)

Acceptance Criteria:
  ✓ Repos registered in registry
  ✓ Registry queried for isolation checks
  ✓ Invalid repo_ids rejected
  ✓ Unit tests: 100% coverage

Verification:
  - pytest tests/unit/test_repo_registry.py -v
```

**Files to Create/Modify:**
- `cortex/core/registry/repo_registry.py` (NEW)
- `cortex-brain/tier0/repo-registry.yaml` (NEW)
- `tests/unit/test_repo_registry.py` (NEW)

---

#### TASK-6: Hub Setup Script (Days 3-4)
**Lead:** DevOps engineer  
**Effort:** 2 days  
**Deliverable:** `scripts/setup-cortex-hub.py` for one-time hub initialization

```yaml
Scope:
  Script: scripts/setup-cortex-hub.py
  Actions:
    1. Verify Python version ≥ 3.9
    2. Check MCP server can start (test import)
    3. Initialize governance.db (migrations)
    4. Create cortex-brain/releases/v1.0.0/ directory
    5. Copy/hash CORTEX.prompt.md to v1.0.0/
    6. Initialize prompt-versions.yaml
    7. Create repo-registry.yaml template
    8. Output: { status: ready, endpoint: 127.0.0.1:8000, version: 1.0.0 }
  
  Idempotency:
    - Can run multiple times (re-running is safe)
    - Detects if already initialized (skips setup steps)
    - Validates existing state
  
Dependencies: TASK-4, TASK-5 (needs version manager + registry)

Acceptance Criteria:
  ✓ Script runs without errors
  ✓ Governance.db initialized (all tables present)
  ✓ Prompts in v1.0.0/ release
  ✓ Registry template created
  ✓ Health endpoint returns ready
  ✓ Running twice produces same result
  ✓ Clear output on success

Verification:
  - bash scripts/setup-cortex-hub.py
  - ls -la cortex-brain/releases/v1.0.0/
  - python -c "import cortex_brain.state.governance; print('DB ready')"
```

**Files to Create/Modify:**
- `scripts/setup-cortex-hub.py` (NEW)
- `scripts/templates/repo-registry.yaml.jinja2` (NEW)

---

#### WEEK 2 SYNC POINT (End of Day 4)
- [ ] TASK-4 complete (version manager working)
- [ ] TASK-5 complete (repo registry queryable)
- [ ] TASK-6 complete (hub setup script tested)
- **Go/No-Go:** Can proceed to TASK-7?

---

### WEEK 3: Repo Integration & Isolation (Feb 3-7)

#### TASK-7: Repo Setup Script (Days 1-3, parallel with TASK-8)
**Lead:** DevOps engineer  
**Effort:** 2-3 days  
**Deliverable:** `scripts/register-repo.sh` template for each repo

```yaml
Scope:
  Template: scripts/register-repo.sh (provided to users in docs)
  Actions (when run in each repo):
    1. Create .github/prompts/ directory
    2. Generate .github/cortex-config.yaml from template
      a. Prompt for: repo_id, repo_name, repo_type
      b. Set hub_endpoint from env var or default
    3. Copy/symlink CORTEX.prompt.md from central release
      a. On Linux/Mac: symlink (always latest)
      b. On Windows: copy (versioned)
    4. Validate MCP hub connectivity (call /health)
    5. Create .github/tier0/ stub (optional overrides)
    6. Git add/commit initial setup
    7. Output: {status: registered, repo_id: api-service, connected: true}
  
  Template Variables:
    - REPO_ID: unique repo identifier
    - REPO_NAME: human-readable name
    - REPO_TYPE: backend|frontend|database|cli|library
    - CORTEX_PATH: path to central CORTEX folder (env var)
  
Dependencies: TASK-4 (needs versioned prompts)

Acceptance Criteria:
  ✓ Script runs without errors in new repo
  ✓ cortex-config.yaml created with correct values
  ✓ Prompts copied/symlinked
  ✓ MCP connectivity validated
  ✓ Git commit created (AC-REPO-REG-001)
  ✓ Idempotent (running twice is safe)
  ✓ Works on macOS, Linux, Windows

Verification:
  - bash scripts/register-repo.sh --repo-id test-api --repo-name "Test API" --repo-type backend
  - ls -la .github/cortex-config.yaml
  - cat .github/cortex-config.yaml (verify values)
  - grep "AC-REPO-REG-001" .git/logs/HEAD
```

**Files to Create/Modify:**
- `scripts/register-repo.sh.template` (NEW)
- `_workspaces/roadmap/templates/cortex-config.yaml.jinja2` (NEW)
- Documentation: `docs/DEPLOYMENT-SETUP-GUIDE.md` (new section)

---

#### TASK-8: Repo Isolation Rules (Days 1-2, parallel with TASK-7)
**Lead:** Backend engineer  
**Effort:** 1-2 days  
**Deliverable:** Isolation enforcement in orchestrators + MCP

```yaml
Scope:
  Changes to Orchestrators:
    - Extract session.repo_id from __cortex_session__ context
    - Validate all file operations match repo_id
    - Reject cross-repo file access with clear error
  
  Example (in any orchestrator):
    def execute(self, file_path: str, __cortex_session__: dict):
        repo_id = __cortex_session__["repo_id"]
        repo_path = __cortex_session__["repo_path"]
        
        # Security check: file must be within repo
        if not is_within_repo(file_path, repo_path):
            raise RepositoryIsolationError(
                f"Cannot modify {file_path} from repo {repo_id}"
            )
        
        # Now safe to proceed
        return self.do_work(file_path)
  
  Audit Logging:
    - Every operation includes repo_id (inherited from session)
    - Rejection logged as AC_EXECUTE_FAILED with isolation_reason
  
  Database:
    - Audit log: add column repo_id (non-null)
    - Migration: backfill existing entries with NULL repo_id (legacy)
  
Dependencies: TASK-1 (needs session context available)

Acceptance Criteria:
  ✓ File operations scoped to repo_path
  ✓ Cross-repo access rejected immediately
  ✓ Audit includes repo_id on success + failure
  ✓ Clear error message on isolation violation
  ✓ Unit tests: 100% coverage (isolation tests)

Verification:
  - pytest tests/unit/test_repo_isolation.py -v
  - pytest tests/integration/test_isolation_violations.py -v
```

**Files to Create/Modify:**
- `cortex/orchestrators/*.py` (modify all orchestrators to respect isolation)
- `cortex/core/security/isolation.py` (NEW - isolation utilities)
- `tests/unit/test_repo_isolation.py` (NEW)
- `tests/integration/test_isolation_violations.py` (NEW)
- Database migration: `migrations/002_add_repo_id_to_audit.sql`

---

#### TASK-9: Integration Tests (Days 3-5)
**Lead:** QA engineer  
**Effort:** 2-3 days  
**Deliverable:** Multi-repo integration tests (all 9 edge cases)

```yaml
Scope:
  Test Suite: tests/integration/test_multi_repo_deployment.py
  
  Test Cases (all must pass):
    1. SingleRepoConnects
       ✓ 1 repo connects to MCP
       ✓ Session created with correct repo_id
       ✓ Audit trail includes repo_id
    
    2. FiveReposConnectIsolated
       ✓ 5 repos connect to same MCP
       ✓ Each has unique session_id
       ✓ No session interference
       ✓ Audit trail shows 5 separate connections
    
    3. IsolationViolationBlocked
       ✓ Repo A tries to modify Repo B's file
       ✓ MCP rejects with RepositoryIsolationError
       ✓ Audit logs rejection (AC_EXECUTE_FAILED)
    
    4. PromptVersionMismatch
       ✓ Repo A requests incompatible version
       ✓ MCP rejects with IncompatibleVersionError
       ✓ Clear error message
    
    5. OfflineFallback
       ✓ MCP hub unavailable
       ✓ Read-only operations work (local rules)
       ✓ Write operations queued locally
       ✓ Clear "OFFLINE" indication
    
    6. OfflineSyncOnReconnect
       ✓ Changes made while offline
       ✓ Reconnect to hub
       ✓ Queued changes replayed
       ✓ Hub audit trail updated
    
    7. RepoOverrideConflict
       ✓ Repo tries to relax Tier 0 rule
       ✓ MCP rejects with GovernanceConflict
       ✓ Error suggests escalation
    
    8. ConcurrentReposAtomicity
       ✓ 2 repos modify shared code file
       ✓ Operations serialized (not parallel race)
       ✓ Audit shows transaction_id for both
    
    9. HealthCheckWorks
       ✓ GET /health returns 200
       ✓ Status shows ready
       ✓ All components healthy
  
  Coverage:
    ✓ All 9 test cases must pass
    ✓ No regressions (existing tests still pass)
    ✓ Code coverage ≥95% for new code
  
Dependencies: TASK-1 through TASK-8 (all core components)

Acceptance Criteria:
  ✓ All 9 test cases passing
  ✓ No new test failures in existing suite
  ✓ Coverage ≥95%
  ✓ Tests run in <30 seconds
  ✓ Clear test output (no warnings)

Verification:
  - pytest tests/integration/test_multi_repo_deployment.py -v
  - pytest tests/ --cov=cortex --cov-report=html
  - open htmlcov/index.html (review coverage)
```

**Files to Create/Modify:**
- `tests/integration/test_multi_repo_deployment.py` (NEW - main test file)
- `tests/fixtures/mock_repos.py` (NEW - 5 test repos)
- `tests/fixtures/mock_mcp_server.py` (NEW - for testing)

---

#### WEEK 3 SYNC POINT (End of Day 5)
- [ ] TASK-7 complete (repo setup script tested)
- [ ] TASK-8 complete (isolation rules enforced)
- [ ] TASK-9 complete (all 9 edge cases passing)
- **Go/No-Go:** Can proceed to Week 4 (IDE integrations)?

---

### WEEK 4: IDE Integrations & Production Readiness (Feb 10-14)

#### TASK-10: VS Code MCP Extension (Days 1-3, parallel with TASK-11)
**Lead:** Frontend engineer  
**Effort:** 2-3 days  
**Deliverable:** vscode-cortex extension (new MCP consumer)

```yaml
Scope:
  VS Code Extension: vscode-cortex
  Functionality:
    1. Load CORTEX.prompt.md from .github/prompts/
    2. Connect to MCP via cortex-config.yaml (endpoint discovery)
    3. Display governance violations inline (squiggly lines)
    4. Show violation details on hover
    5. Quick-fix suggestions (auto-fix) if applicable
    6. Audit trail viewer (sidebar panel)
    7. Health check indicator (connection status)
  
  Implementation:
    - Consume MCP via JSON-RPC
    - Call /health on extension load
    - Listen for /mcp/tools/governance_check results
    - Display violations using VS Code Diagnostics API
    - Update in real-time as user types
  
  Config Discovery:
    - Read .github/cortex-config.yaml
    - Extract hub_endpoint
    - Validate connectivity on startup
    - Show warning if hub unreachable
  
Dependencies: TASK-2 (needs health check endpoint), TASK-3 (discovery logic)

Acceptance Criteria:
  ✓ Extension loads in VS Code
  ✓ Connects to MCP hub
  ✓ Displays violations inline
  ✓ Quick-fix works (1 test case)
  ✓ Audit panel shows recent changes
  ✓ Health indicator shows connection status
  ✓ Works with all 5 test repos

Verification:
  - Install extension in VS Code
  - Open test repo
  - Make code change (violate governance rule)
  - Verify: red squiggly line appears
  - Hover: see violation details
  - Quick-fix: apply suggestion
```

**Files to Create/Modify:**
- `extensions/vscode-cortex/` (NEW directory)
  - `package.json`
  - `src/extension.ts`
  - `src/mcp_client.ts`
  - `src/diagnostics.ts`

---

#### TASK-11: VS Studio 2019+ LSP Adapter (Days 1-3, parallel with TASK-10)
**Lead:** Backend engineer  
**Effort:** 3-5 days  
**Deliverable:** cortex-lsp-adapter (.NET Core bridge)

```yaml
Scope:
  LSP Adapter: cortex-lsp-adapter (standalone .NET Core app)
  Architecture:
    ┌─────────────────────────┐
    │  Visual Studio 2019+    │
    │  (LSP client)           │
    └────────────┬────────────┘
                 │ LSP over TCP/IPC
                 ↓
    ┌─────────────────────────────────────────┐
    │  cortex-lsp-adapter (C# .NET Core)      │
    │  • LSP server (listens on TCP/IPC)      │
    │  • MCP client (connects to hub)         │
    │  • Local Python validator               │
    │  • Config discovery                     │
    └─────────────────────────────────────────┘
                 │ JSON-RPC via MCP
                 ↓
    ┌─────────────────────────────────────────┐
    │  CORTEX MCP Hub (127.0.0.1:8000)        │
    └─────────────────────────────────────────┘
  
  Features:
    1. Listen for LSP requests from VS
    2. Parse Python files locally (syntax validation)
    3. Call MCP hub for governance checks
    4. Convert MCP results to LSP Diagnostics
    5. Return results to VS
    6. Validate Python environment compatibility
  
  Endpoint Configuration:
    - VS config file: cortex-lsp-config.json in repo root
    - Specifies: MCP hub endpoint, Python version, etc.
  
Dependencies: TASK-2 (needs health check), TASK-3 (discovery)

Acceptance Criteria:
  ✓ LSP adapter starts without errors
  ✓ Connects to MCP hub
  ✓ Validates local Python environment
  ✓ Receives LSP requests from VS
  ✓ Returns violations as LSP Diagnostics
  ✓ VS displays violations correctly
  ✓ Works with VS 2019 community edition

Verification:
  - Start adapter: dotnet run
  - Open VS 2019
  - Configure LSP endpoint in VS
  - Open test repo
  - Make code violation
  - Verify: diagnostic shown in VS
```

**Files to Create/Modify:**
- `extensions/cortex-lsp-adapter/` (NEW directory)
  - `cortex-lsp-adapter.csproj`
  - `Program.cs`
  - `MCPClient.cs`
  - `LSPServer.cs`
  - `PythonEnvironmentValidator.cs`

---

#### TASK-12: Documentation (Days 4-5)
**Lead:** Technical writer  
**Effort:** 2-3 days  
**Deliverable:** Complete deployment guides + architecture docs

```yaml
Scope:
  1. Deployment Setup Guide
     - Step 1: Setup CORTEX Hub (run setup-cortex-hub.py)
     - Step 2: Register Each Repo (run register-repo.sh)
     - Step 3: Configure IDE (VS Code or VS 2019+)
     - Step 4: Verify Setup (health checks)
     - With screenshots + examples
  
  2. Architecture Decision Records (ADR)
     - ADR-001: Why 3-Tier Architecture?
     - ADR-002: Why Session Context?
     - ADR-003: Why MCP over alternatives?
     - ADR-004: Why LSP for VS Studio?
  
  3. Troubleshooting Runbook
     - Issue: "Cannot connect to MCP hub"
       Solution: Check CORTEX_MCP_ENDPOINT, verify setup-cortex-hub.py ran
     - Issue: "Prompt version mismatch"
       Solution: Update cortex-config.yaml prompt_version
     - Issue: "VS Studio 2019 shows no diagnostics"
       Solution: Verify LSP adapter running, check cortex-lsp-config.json
     - (5+ scenarios covered)
  
  4. API Reference
     - MCP Endpoints: /health, /config/prompt-version, /mcp/tools/...
     - Session API: create_session(), destroy_session()
     - Registry API: get_repo(), list_repos()
  
  5. FAQ
     - "Can repos run offline?"
       Answer: Yes, read-only operations work offline
     - "What if MCP hub goes down?"
       Answer: Fallback to local rules, changes queued for sync
     - "How do I add a new repo?"
       Answer: Run register-repo.sh in new repo

Dependencies: All tasks complete (Tasks 1-11)

Acceptance Criteria:
  ✓ Setup guide has 3-repo example (works end-to-end)
  ✓ Architecture documents explain decisions
  ✓ Troubleshooting covers 5+ common issues
  ✓ API reference complete
  ✓ No broken links
  ✓ Reviewed by tech lead

Verification:
  - Follow setup guide from scratch (3-repo example)
  - Verify all 3 repos connect to MCP
  - Verify all 3 repos isolated
  - Verify audit trail includes all 3 repos
```

**Files to Create/Modify:**
- `docs/DEPLOYMENT-SETUP-GUIDE.md` (NEW - main guide)
- `docs/DEPLOYMENT-ARCHITECTURE-ADRs.md` (NEW - architecture decisions)
- `docs/DEPLOYMENT-TROUBLESHOOTING.md` (NEW - issue resolution)
- `docs/DEPLOYMENT-API-REFERENCE.md` (NEW - MCP API)
- `docs/DEPLOYMENT-FAQ.md` (NEW - common questions)

---

#### WEEK 4 SYNC POINT (End of Day 5)
- [ ] TASK-10 complete (VS Code extension tested)
- [ ] TASK-11 complete (VS Studio LSP adapter tested)
- [ ] TASK-12 complete (documentation reviewed)
- **GO LIVE DECISION:** All success criteria met?

---

## CRITICAL PATH ANALYSIS

**Dependency Chain (what must complete before next task):**

```
TASK-1 (Session Context)
  ↓
TASK-5 (Repo Registry)
  ↓
TASK-8 (Isolation Rules)
  ↓
TASK-9 (Integration Tests)
  ↓ SUCCESS
PRODUCTION READY

In Parallel:
  TASK-2 (Health Check) → TASK-4 (Versioning) → TASK-7 (Setup Script)
  TASK-3 (Discovery) ───↘
                         TASK-6 (Hub Setup)
  TASK-4 ──────────────→ TASK-7
  TASK-2 ──────────────→ TASK-10 (VS Code)
  TASK-2 ──────────────→ TASK-11 (VS Studio)
```

**Critical Path:** TASK-1 → TASK-5 → TASK-8 → TASK-9 (10 days minimum)  
**Total with Parallel:** 18-20 days across 4 weeks

---

## RESOURCE ALLOCATION

**Recommended Team:**
- Backend Engineers (2): TASK-1, TASK-4, TASK-5, TASK-8, TASK-11
- DevOps Engineers (1): TASK-2, TASK-3, TASK-6, TASK-7
- QA/Test Engineers (1): TASK-9
- Frontend Engineers (1): TASK-10
- Technical Writers (0.5): TASK-12

**Total:** 5.5 FTE across 4 weeks

---

## APPROVAL CHECKLIST

**Before starting Week 1, get sign-off on:**

```yaml
Architecture:
  - [ ] Approve 3-Tier Deployment Model
  - [ ] Approve Option A (VERSION TAGS) for prompt distribution
  - [ ] Approve LSP Adapter for VS Studio 2019+
  - [ ] Confirm repo isolation strategy acceptable

Timeline:
  - [ ] Confirm 18-20 day estimate acceptable
  - [ ] Confirm 4-week schedule viable (Jan 20 - Feb 16)
  - [ ] Confirm team availability (5.5 FTE)

Risks:
  - [ ] Accept MEDIUM risk level
  - [ ] Confirm mitigation strategies sufficient
  - [ ] Approve fallback plan if blockers arise

Success Criteria:
  - [ ] Confirm 10 success criteria acceptable (Section 8.1)
  - [ ] Confirm sign-off checklist complete (Section 8.2)
  - [ ] Confirm production readiness definition

Go-Live:
  - [ ] Approve Feb 16 target date for production deployment
  - [ ] Confirm rollback procedure acceptable
  - [ ] Confirm 3-repo pilot phase acceptable
```

---

## APPENDIX: ESTIMATED BUDGET

**Assuming $150/hour engineering cost:**

| Task | Effort (days) | Hours | Cost |
|------|---|---|---|
| TASK-1 | 1.5 | 12 | $1,800 |
| TASK-2 | 1 | 8 | $1,200 |
| TASK-3 | 1 | 8 | $1,200 |
| TASK-4 | 2.5 | 20 | $3,000 |
| TASK-5 | 1.5 | 12 | $1,800 |
| TASK-6 | 2 | 16 | $2,400 |
| TASK-7 | 2.5 | 20 | $3,000 |
| TASK-8 | 1.5 | 12 | $1,800 |
| TASK-9 | 2.5 | 20 | $3,000 |
| TASK-10 | 2.5 | 20 | $3,000 |
| TASK-11 | 4 | 32 | $4,800 |
| TASK-12 | 2.5 | 20 | $3,000 |
| **TOTAL** | **~24 days** | **~200 hours** | **~$30,000** |

---

## NEXT STEPS

1. **Review & Approve (24 hours)**
   - Review DEPLOYMENT-PHASE-REDESIGN-20260119.md (architecture)
   - Review this document (implementation plan)
   - Decision: PROCEED or REVISE?

2. **Kickoff Meeting (if approved)**
   - Present architecture to team
   - Assign tasks to engineers
   - Create Jira/GitHub issues for tracking
   - Set Week 1 standup schedule

3. **Start Week 1 (Jan 20)**
   - TASK-1: Session Context (backend)
   - TASK-2: Health Check (backend/devops)
   - TASK-3: Discovery (devops)

---

**Document Status:** ✅ READY FOR REVIEW  
**Next: Executive decision on approval (Jan 20, 2026)**
