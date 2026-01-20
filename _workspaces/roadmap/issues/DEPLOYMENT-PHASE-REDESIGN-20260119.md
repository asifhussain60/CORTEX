# CORTEX Deployment Phase Redesign & Gap Remediation
**Author:** Asif Hussain | **Date:** January 19, 2026 | **Status:** Architecture & Design Phase
**Issue Reference:** #7 - Deployment gaps
**Scope:** Multi-repo production deployment, VS Code + Visual Studio 2019+ support

---

## EXECUTIVE SUMMARY

### Problem Statement
CORTEX Issue #7 identifies critical gaps in deployment architecture:
- ❌ No automated multi-repo setup mechanism
- ❌ Manual prompt distribution creates governance drift
- ❌ No per-repo isolation (multi-tenancy security risk)
- ❌ MCP server discovery hardcoded (breaks in prod/staging)
- ❌ No prompt versioning (audit trail breaks)
- ❌ VS Code only; no Visual Studio 2019+ support

### Recommended Solution
**Three-Tier Deployment Architecture with unified orchestration:**

| Layer | Component | Purpose | Status |
|-------|-----------|---------|--------|
| **Tier 1: Central Hub** | MCP Server, Governance DB, Version Manager | Single source of truth | ✅ Exists (needs extension) |
| **Tier 2: Configuration Service** | Repo Registry, Discovery, Isolation | Route & isolate repos | ❌ NEW (5-7 days) |
| **Tier 3: Repo Local** | Config files, domain knowledge | Per-repo customization | ⏳ Partial (needs templates) |

### Key Outcomes
- ✅ **Deterministic deployment** across 5+ repos without manual errors
- ✅ **Full governance compliance** (CORE-026, CORE-027, CORE-005 rules)
- ✅ **IDE-agnostic** (VS Code via MCP, VS 2019+ via IPC/LSP adapter)
- ✅ **Audit-trail unified** (all repo changes logged centrally with context)
- ✅ **Knowledge graph unified** (cross-repo pattern learning)
- ✅ **Production-ready** (service discovery, health checks, rollback)

### Timeline & Effort
- **Design Phase:** Week 1 (3 days) ← **YOU ARE HERE**
- **Implementation:** Weeks 2-3 (10-12 days)
- **Testing:** Week 4 (3 days)
- **Documentation:** Week 4 (2 days)
- **Total:** ~3 weeks, 18-20 days effort

---

## SECTION 1: CURRENT STATE ANALYSIS

### 1.1 What Exists Today

#### MCP Server (✅ Complete but needs extension)
- **Location:** `src/mcp/server.py`
- **Capability:** Exposes all orchestrators as standardized MCP tools
- **Gap:** No repo isolation, no session context, no health checks

```yaml
Current Capabilities:
  - Tool registration (auto via @register_orchestrator)
  - Request routing to orchestrators
  - Response marshalling to MCP spec
  - Error handling for orchestrator failures
  
Missing Capabilities:
  - Session/repo context injection
  - Per-repo path isolation
  - MCP endpoint discovery
  - Health/readiness checks
  - Telemetry/metrics
```

#### Prompt Distribution (❌ Incomplete)
- **Current:** CORTEX.prompt.md stored in `docs/` folder
- **Gap:** No automated copy mechanism, no versioning

```
What exists:
  ✓ Single source of truth: docs/cortex-builder.prompt.md
  ✓ Comprehensive instructions (1040+ lines)
  
What's missing:
  ✗ No .github/prompts/ folder template for repos
  ✗ No version manifest
  ✗ No copy/sync script
  ✗ No drift detection
```

#### Governance (✅ Complete but needs scope)
- **Location:** `cortex_brain/tier0/governance/`
- **Gap:** No per-repo rule isolation

```yaml
Current Rules:
  - core-rules.yaml: 28 immutable SKULL rules
  - phase-enforcement-map.yaml: Phase-specific rules
  - ac-validation-checklist.yaml: AC validation rules
  
Missing:
  - No per-repo override mechanism
  - No scope-aware rule application
  - No rule conflict resolution
```

### 1.2 Deployment Scenarios Tested

#### Scenario A: Single Repo (PASSING ✅)
- CORTEX as single folder
- One repo connects to MCP server
- All features working
- **Evidence:** System check tests (test_system_check.py)

#### Scenario B: Five Repos Connecting to Same MCP (FAILING ❌)
- Current architecture assumes read-only access
- **Failure Mode 1:** No repo isolation → Repo A can modify Repo B's files
- **Failure Mode 2:** Audit trail doesn't track which repo made change
- **Failure Mode 3:** No way to configure repo-specific governance rules

#### Scenario C: VS Code via MCP (PASSING ✅)
- VS Code + Copilot uses MCP server
- Works in single-repo scenario
- **Gap:** Need to test multi-repo from VS Code

#### Scenario D: Visual Studio 2019+ Integration (❌ NOT TESTED)
- No LSP adapter exists
- No IPC transport for VS 2019+
- Need separate implementation path

### 1.3 Edge Cases & Risk Assessment

#### Edge Case 1: Network/MCP Server Unavailable
- **Risk Level:** HIGH (blocks all repos)
- **Current:** No fallback, system fails hard
- **Requirement:** Graceful degradation to local-only mode

#### Edge Case 2: Prompt Version Mismatch
- **Risk Level:** MEDIUM (governance divergence)
- **Current:** No detection mechanism
- **Requirement:** Version negotiation on connect

#### Edge Case 3: Repo-Specific Governance Conflict
- **Risk Level:** HIGH (audit inconsistency)
- **Current:** No conflict detection
- **Requirement:** Tier 0 rules always win, Tier 1 can vary

#### Edge Case 4: Concurrent Repos Modifying Same Shared Code
- **Risk Level:** MEDIUM (race conditions)
- **Current:** No locking mechanism
- **Requirement:** DB-level transaction support for cross-repo changes

#### Edge Case 5: Repo Offline, Has Local Changes, Reconnects
- **Risk Level:** MEDIUM (merge conflicts)
- **Current:** No offline mode support
- **Requirement:** Local audit trail, sync on reconnect

#### Edge Case 6: VS 2019+ Dev Uses Different Python Version
- **Risk Level:** HIGH (compatibility)
- **Current:** Assumes Python environment consistent
- **Requirement:** .NET LSP proxy validates Python version match

---

## SECTION 2: GAPS ANALYSIS

### 2.1 Gap Matrix (Criticality vs. Effort)

| Gap | Current State | Required State | Impact | Effort | Priority |
|-----|---------------|----------------|--------|--------|----------|
| **Repo Isolation** | None | Session context, scoped ops | 🔴 CRITICAL | 1-2d | P0 |
| **MCP Discovery** | Hardcoded | Env var + config file | 🔴 CRITICAL | 1d | P0 |
| **Prompt Versioning** | Single file | Version manifest | 🟠 HIGH | 2-3d | P1 |
| **Setup Automation** | Manual | Scripts + templates | 🟠 HIGH | 3-5d | P1 |
| **Health Checks** | None | /health endpoint | 🟠 HIGH | 1d | P1 |
| **VS Studio 2019+ Support** | None | LSP adapter + IPC | 🟠 HIGH | 5-7d | P2 |
| **Offline Mode** | Not supported | Local audit + sync | 🟡 MEDIUM | 3-4d | P2 |
| **Repo Rule Overrides** | Not supported | Tier 1 per-repo rules | 🟡 MEDIUM | 2d | P2 |
| **Cross-Repo Transactions** | Not supported | DB transactions | 🟡 MEDIUM | 2-3d | P2 |
| **Knowledge Graph Merge** | Not implemented | Central indexing + queries | 🟡 MEDIUM | 3-4d | P3 |

### 2.2 Critical Blockers (Must Fix Before Production)

#### Blocker 1: No Repo Isolation in MCP Server ⛔ BLOCKING
- **Severity:** CRITICAL
- **Current:** All connected repos share execution context
- **Risk:** Repo A can execute changes in Repo B's directory
- **Example Failure:**
  ```
  User in Repo A: "Add function to utils.py"
  MCP executes: /repo-b/utils.py ← WRONG REPO!
  Result: Repo B's code modified without consent
  ```
- **Governance Violation:** CORE-005 (path portability) + CORE-027 (audit context)
- **Fix Required:** Extend MCPServer with session.repo_id context

#### Blocker 2: No Prompt Version Manifest ⛔ BLOCKING
- **Severity:** CRITICAL
- **Current:** CORTEX.prompt.md is single file; no versioning
- **Risk:** Can't track which repo is using which prompt version
- **Example Failure:**
  ```
  CORTEX updates prompt.md (v1.1)
  Repo A still has v1.0 (old syntax)
  New orchestrator features don't work in Repo A
  Audit trail inconsistent across repos
  ```
- **Governance Violation:** CORE-027 (audit consistency)
- **Fix Required:** Create cortex-brain/releases/ with versioned prompts

#### Blocker 3: No Service Discovery Mechanism ⛔ BLOCKING
- **Severity:** CRITICAL
- **Current:** Repos must hardcode MCP endpoint (127.0.0.1:8000)
- **Risk:** Breaks when server moves, scales to multiple environments
- **Example Failure:**
  ```
  Production deployment (host: prod-cortex-1.example.com)
  All repos still point to 127.0.0.1:8000
  Connection fails; all repos offline
  ```
- **Governance Violation:** CORE-026 (deterministic checkpoints)
- **Fix Required:** Add service discovery (env vars + config file)

#### Blocker 4: No Setup Automation ⛔ BLOCKING
- **Severity:** CRITICAL
- **Current:** User must manually setup each repo
- **Risk:** Manual errors; inconsistent state across repos
- **Example Failure:**
  ```
  User sets up 5 repos manually
  Repo 3 misses a step → no cortex-config.yaml
  Repo 3 can't connect to MCP → audit trail breaks
  ```
- **Governance Violation:** CORE-026 (reproducible process)
- **Fix Required:** Automated setup script (setup-cortex-hub.py)

---

## SECTION 3: RECOMMENDED ARCHITECTURE

### 3.1 Three-Tier Deployment Model

```
┌─────────────────────────────────────────────────────────────────┐
│ TIER 1: CENTRAL CORTEX HUB (Single, Authoritative Deployment)   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  A. MCP Server                                                   │
│     • Port: 8000 (configurable)                                  │
│     • Features:                                                  │
│       - Tool endpoint: /mcp/tools/...                            │
│       - Health endpoint: /health                                 │
│       - Metrics endpoint: /metrics                               │
│       - Session context injection                               │
│                                                                  │
│  B. Governance Database (SQLite WAL mode)                        │
│     • Location: cortex_brain/state/governance.db                 │
│     • Tables:                                                    │
│       - audit_log (all changes from all repos)                   │
│       - governance_rules (Tier 0-3)                              │
│       - repo_registry (which repos connected)                    │
│       - prompt_versions (version manifest)                       │
│     • Read-only access from repos                               │
│     • Writes only from central orchestrators                     │
│                                                                  │
│  C. Version Manager                                              │
│     • Location: cortex_brain/releases/                           │
│     • Manages: prompt versions (v1.0.0, v1.1.0, etc.)           │
│     • Provides: Version negotiation API                          │
│                                                                  │
│  D. Configuration Service                                        │
│     • Endpoint: MCP /config/* routes                             │
│     • Provides:                                                  │
│       - Repo registration lookup                                 │
│       - MCP endpoint discovery                                   │
│       - Rule conflicts resolution                                │
│       - Domain knowledge queries                                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                         ↓ (JSON-RPC over MCP)
┌─────────────────────────────────────────────────────────────────┐
│ TIER 2: REPO-LOCAL CONFIGURATION (Per-Repo Discovery)           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  A. cortex-config.yaml (New file in each repo)                  │
│     ```yaml                                                      │
│     cortex:                                                      │
│       # Service discovery                                        │
│       hub_endpoint: "${CORTEX_MCP_ENDPOINT:-127.0.0.1:8000}"   │
│       hub_timeout_seconds: 30                                    │
│       hub_verify_ssl: false  # dev mode                          │
│                                                                  │
│       # Repo identity                                            │
│       repo_id: "api-service"  # unique across all repos          │
│       repo_name: "CORTEX API Service"                            │
│       repo_type: "backend"  # backend|frontend|database|cli     │
│                                                                  │
│       # Version negotiation                                      │
│       prompt_version: "1.0.0"  # Required version                │
│       min_prompt_version: "1.0.0"                                │
│       max_prompt_version: "2.0.0"                                │
│                                                                  │
│       # Isolation & governance                                   │
│       isolation_mode: "strict"  # strict|normal|permissive       │
│       governance_mode: "inherit"  # inherit master, can't override Tier 0 │
│       tier1_overrides: ".github/tier0/repo-overrides.yaml"       │
│                                                                  │
│       # Offline & resilience                                     │
│       offline_mode: true  # Allow local changes when hub offline │
│       fallback_to_local: true  # Use cached rules if hub fails   │
│     ```                                                          │
│                                                                  │
│  B. .github/prompts/CORTEX.prompt.md (Version-tagged)           │
│     • Copy or symlink to central versioned prompt                │
│     • Includes repo_id in MCP requests                           │
│                                                                  │
│  C. .github/tier0/repo-overrides.yaml (Optional)                 │
│     • Can only ADD rules, not override Tier 0                    │
│     • Example: "Require 100% test coverage" (more strict)        │
│     • Cannot relax Tier 0 rules                                  │
│                                                                  │
│  D. .github/domains/ (Optional, local domain knowledge)          │
│     • Repo-specific domain models                                │
│     • Gets indexed in central knowledge graph                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                         ↓ (Git, local filesystem)
┌─────────────────────────────────────────────────────────────────┐
│ TIER 3: LOCAL EXECUTION (Developer Workspace)                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  A. VS Code (Primary IDE)                                        │
│     • Extension: vscode-cortex (new MCP consumer)                │
│     • Features:                                                  │
│       - Loads CORTEX.prompt.md from .github/prompts/             │
│       - Connects to MCP via cortex-config.yaml                   │
│       - Displays governance violations inline                    │
│       - Quick-fixes for violations                               │
│       - Audit trail viewer                                       │
│                                                                  │
│  B. Visual Studio 2019+ (Secondary IDE - NEW)                    │
│     • New Component: vscode-cortex-lsp-adapter                   │
│     • Architecture: .NET LSP server ↔ MCP via HTTP/IPC          │
│     • Features:                                                  │
│       - LSP protocol for VS compatibility                        │
│       - Local Python runtime validation                          │
│       - Governance violation indicators                          │
│       - Copilot integration (VS 2023+)                           │
│                                                                  │
│  C. Command Line (CI/CD pipelines)                               │
│     • Commands: cortex-cli validate, cortex-cli sync             │
│     • Uses same MCP endpoint discovery                           │
│     • Outputs audit trail references                             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Key Design Decisions

#### Decision 1: Prompt Distribution Strategy
**Choose ONE (or hybrid):**

| Option | Mechanism | Pros | Cons | Recommendation |
|--------|-----------|------|------|-----------------|
| A: VERSION TAGS | Prompts in `cortex-brain/releases/v1.0.0/` | Deterministic, easy rollback, audit clear | Requires coordination | ✅ PRIMARY for prod |
| B: SYMLINKS | `.github/prompts/ → symlinks` | Always latest, minimal storage | Breaks on Windows, tight coupling | ⏳ DEV/MAC only |
| C: GIT SUBMODULE | CORTEX as submodule in each repo | Strong version control, independence | Submodule complexity, duplication | ⚠️ ALTERNATIVE |
| D: HTTP MIRROR | `.github/prompts/ pulls from CORTEX HTTP endpoint` | Real-time updates, no storage | Network dependency, cache invalidation | 🟡 FUTURE |

**Recommendation:** Option A (VERSION TAGS) + Option D (HTTP fallback)
- Primary: Git tags with versioned prompt releases
- Fallback: HTTP mirror if symlink breaks

#### Decision 2: Repo Isolation Implementation
**Scope Rules:** Which operations are repo-isolated?

```yaml
Always Scoped (Hard boundary):
  - File modifications: Can only modify repo's own files
  - Audit logging: Each entry tagged with repo_id
  - Governance rules: Repos can't access each other's Tier 1 rules

Shared Access (Intentional):
  - Read-only access to:
    - Central audit trail (for knowledge graph)
    - Tier 0 governance rules (immutable, same for all)
    - Other repos' domain knowledge (for pattern learning)
  - Write access to:
    - Central domain knowledge index (append-only for learnings)
    - Metrics/telemetry (aggregated, no repo distinction)
```

#### Decision 3: VS Studio 2019+ Support Path
**Option:** LSP Adapter Bridge

```
┌─────────────────────────┐
│  Visual Studio 2019+    │
│  (LSP client)           │
└────────────┬────────────┘
             │ LSP protocol
             ↓
┌─────────────────────────────────────────────┐
│  cortex-lsp-adapter (.NET Core)             │
│  • LSP server (listens on TCP/IPC)          │
│  • MCP client (connects to hub)             │
│  • Local Python validator                   │
│  • Config discovery                         │
└─────────────────────────────────────────────┘
             │ JSON-RPC via MCP
             ↓
┌─────────────────────────────────────────────┐
│  CORTEX MCP Hub                             │
│  • Tool execution                           │
│  • Governance validation                    │
│  • Audit trail                              │
└─────────────────────────────────────────────┘
```

**Why LSP Adapter?**
- ✅ VS Studio 2019+ has native LSP support
- ✅ No need for VS extension (no Visual Studio SDK)
- ✅ Can run as separate service (portability)
- ✅ Shared with other non-LSP IDEs (Vim, Sublime, etc.)

---

## SECTION 4: IMPLEMENTATION ROADMAP

### 4.1 Phase Sequence & Dependencies

```yaml
Week 1: Foundation (Design → Implementation Start)
  TASK-1: Session Context (1-2 days)
    - Extend MCPServer with session.repo_id
    - Add session storage (in-memory + SQLite)
    - PR-ready: src/mcp/server.py modifications
    - Depends: None (can start immediately)
    - BLOCKS: All other tasks

  TASK-2: Health Check Endpoint (1 day)
    - Add /health route to MCP
    - Returns: {"status": "ready", "db": "connected", "version": "1.0.0"}
    - Depends: None
    - BLOCKS: Discovery logic testing

  TASK-3: Service Discovery (1 day)
    - Create config service logic
    - Load CORTEX_MCP_ENDPOINT env var
    - Falls back to cortex-config.yaml
    - Depends: None
    - BLOCKS: Client setup

Week 2: Configuration & Versioning
  TASK-4: Prompt Version Manager (2-3 days)
    - Create cortex-brain/releases/v1.0.0/CORTEX.prompt.md
    - Version manifest schema
    - Version negotiation logic (what if repo requests v1.5 but hub has v1.0?)
    - Depends: TASK-3
    - BLOCKS: Prompt distribution

  TASK-5: Repo Registry System (1-2 days)
    - Schema: repo_id → endpoint mapping
    - Location: cortex-brain/tier0/repo-registry.yaml
    - Lookup logic in MCP
    - Depends: TASK-1
    - BLOCKS: Isolation

  TASK-6: Setup Script (cortex-hub side) (2 days)
    - Create scripts/setup-cortex-hub.py
    - Actions:
      ✓ Verify MCP server starts
      ✓ Initialize governance.db
      ✓ Create repo-registry.yaml template
      ✓ Generate v1.0.0 prompt release
      ✓ Output: MCP endpoint + version manifest
    - Depends: TASK-3, TASK-4
    - BLOCKS: Nothing (prep phase)

Week 3: Repo Integration & Testing
  TASK-7: Setup Script (repo side) (2-3 days)
    - Create scripts/register-repo.sh (template for each repo)
    - Actions:
      ✓ Generate .github/cortex-config.yaml
      ✓ Copy/symlink CORTEX.prompt.md
      ✓ Validate MCP connectivity
      ✓ Create first audit entry (AC-REPO-REG-001)
    - Depends: TASK-4, TASK-5
    - BLOCKS: Testing

  TASK-8: Repo Isolation Rules (1-2 days)
    - Extend orchestrators to respect repo context
    - File operations: check session.repo_id matches path
    - Audit logging: always include repo_id
    - Depends: TASK-1, TASK-5
    - BLOCKS: Integration testing

  TASK-9: Integration Tests (2-3 days)
    - Test: 5 repos connecting to single MCP
    - Test: Isolation (Repo A can't modify Repo B)
    - Test: Audit trail (all changes logged with repo context)
    - Test: Version mismatch handling
    - Test: Offline fallback
    - Depends: TASK-8
    - BLOCKS: Production readiness

Week 4: IDE Integrations & Documentation
  TASK-10: VS Code Extension (VSCODE-CORTEX) (2-3 days)
    - Consumes MCP via language server
    - Displays violations inline
    - Quick-fixes integration
    - Depends: TASK-2
    - BLOCKED BY: None (parallel development)

  TASK-11: VS Studio 2019+ LSP Adapter (3-5 days)
    - .NET Core app that bridges LSP ↔ MCP
    - Validates Python environment
    - Depends: TASK-2
    - BLOCKED BY: None (parallel development)

  TASK-12: Documentation (2-3 days)
    - Deployment guide (setup steps)
    - Architecture document
    - Troubleshooting guide (edge cases)
    - Depends: All tasks complete
```

### 4.2 Detailed Implementation Specs

#### Spec 1: Session Context Injection (TASK-1)

```python
# In src/mcp/server.py

class MCPSession:
    """Per-connection session context (repo-aware)"""
    
    session_id: str  # UUID for this connection
    repo_id: str  # Which repo this session is for ("api-service")
    repo_type: str  # Type: "backend", "frontend", "database", "cli"
    repo_path: str  # Local path to repo root
    prompt_version: str  # Version this repo is using (e.g., "1.0.0")
    connected_at: datetime
    
    def __init__(self, repo_id: str, repo_path: str, prompt_version: str):
        self.session_id = str(uuid4())
        self.repo_id = repo_id
        self.repo_path = repo_path
        self.prompt_version = prompt_version
        self.connected_at = datetime.now()

class MCPServer:
    """Enhanced MCP Server with repo isolation"""
    
    def __init__(self, host: str = "127.0.0.1", port: int = 8000):
        self.host = host
        self.port = port
        self.sessions: Dict[str, MCPSession] = {}  # session_id → MCPSession
    
    async def create_session(self, repo_config: dict) -> MCPSession:
        """Create isolated session for repo"""
        session = MCPSession(
            repo_id=repo_config["repo_id"],
            repo_path=repo_config["repo_path"],
            prompt_version=repo_config["prompt_version"]
        )
        self.sessions[session.session_id] = session
        
        # Log: AC-REPO-CONNECT-001
        audit_log(
            ac_id="AC-REPO-CONNECT-001",
            repo_id=session.repo_id,
            event="session_created",
            session_id=session.session_id
        )
        return session
    
    async def handle_tool_call(
        self,
        session_id: str,
        tool_name: str,
        args: dict
    ) -> dict:
        """Execute tool with repo isolation"""
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Unknown session: {session_id}")
        
        # Inject repo context into orchestrator
        args["__cortex_session__"] = {
            "repo_id": session.repo_id,
            "repo_path": session.repo_path,
            "session_id": session.session_id
        }
        
        # Call orchestrator
        orchestrator = self.orchestrators[tool_name]
        result = await orchestrator.execute(**args)
        
        # Audit: always include repo_id
        audit_log(
            ac_id=f"AC-{tool_name.upper()}-001",
            repo_id=session.repo_id,
            event="tool_executed",
            result=result["status"]
        )
        return result
```

#### Spec 2: Health Check Endpoint (TASK-2)

```python
# In src/mcp/server.py

@app.get("/health")
async def health_check():
    """Health check endpoint for repo discovery"""
    return {
        "status": "ready",
        "version": "1.0.0",
        "db": "connected" if check_db() else "error",
        "governance_rules_loaded": len(load_rules()),
        "orchestrators_registered": len(self.orchestrators),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/config/prompt-version")
async def get_prompt_version():
    """Current prompt version managed by hub"""
    return {
        "current": "1.0.0",
        "available": ["1.0.0", "1.1.0"],  # Future versions
        "deprecated": [],
        "recommended": "1.0.0"
    }
```

#### Spec 3: cortex-config.yaml Template

```yaml
# Template: _workspaces/roadmap/templates/cortex-config.yaml.jinja2
# Used by: scripts/register-repo.sh

cortex:
  # Service discovery (env var overrides config file)
  hub_endpoint: "${CORTEX_MCP_ENDPOINT:-127.0.0.1:8000}"
  hub_timeout_seconds: 30
  hub_verify_ssl: false
  
  # Repo identity (customize per repo)
  repo_id: "{{ repo_id }}"  # e.g., api-service, ui-app, db-service
  repo_name: "{{ repo_name }}"
  repo_type: "{{ repo_type }}"  # backend|frontend|database|cli|library
  
  # Version negotiation
  prompt_version: "1.0.0"
  min_prompt_version: "1.0.0"
  max_prompt_version: "2.0.0"
  
  # Isolation & governance
  isolation_mode: "strict"  # strict|normal|permissive
  tier1_overrides: ".github/tier0/repo-overrides.yaml"
  
  # Offline & resilience
  offline_mode: true
  fallback_to_local: true
  
  # Optional: repo-specific domains
  domains_path: ".github/domains"
  
  # Optional: custom telemetry
  telemetry_enabled: true
  telemetry_endpoint: "${CORTEX_TELEMETRY:-}"
```

#### Spec 4: Repo Setup Script (TASK-7)

```bash
#!/bin/bash
# scripts/register-repo.sh
# Usage: bash register-repo.sh --repo-id api-service --repo-name "CORTEX API" --repo-type backend

set -e

REPO_ID=""
REPO_NAME=""
REPO_TYPE=""
CORTEX_PATH="${CORTEX_PATH:-../CORTEX}"

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --repo-id) REPO_ID="$2"; shift 2 ;;
    --repo-name) REPO_NAME="$2"; shift 2 ;;
    --repo-type) REPO_TYPE="$2"; shift 2 ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

# Validate inputs
[ -z "$REPO_ID" ] && echo "ERROR: --repo-id required" && exit 1
[ -z "$REPO_NAME" ] && echo "ERROR: --repo-name required" && exit 1
[ -z "$REPO_TYPE" ] && echo "ERROR: --repo-type required" && exit 1

echo "✓ Registering repo: $REPO_ID ($REPO_TYPE)"

# Step 1: Create .github/prompts/ directory
mkdir -p .github/prompts
echo "✓ Created .github/prompts/"

# Step 2: Generate cortex-config.yaml
cat > .github/cortex-config.yaml <<EOF
cortex:
  hub_endpoint: "\${CORTEX_MCP_ENDPOINT:-127.0.0.1:8000}"
  repo_id: "$REPO_ID"
  repo_name: "$REPO_NAME"
  repo_type: "$REPO_TYPE"
  prompt_version: "1.0.0"
  isolation_mode: "strict"
EOF
echo "✓ Created .github/cortex-config.yaml"

# Step 3: Copy/symlink prompt (choose based on OS)
if [[ "$OSTYPE" == "darwin"* ]] || [[ "$OSTYPE" == "linux"* ]]; then
  # macOS/Linux: use symlink
  ln -sf "$CORTEX_PATH/cortex-brain/releases/v1.0.0/CORTEX.prompt.md" \
    .github/prompts/CORTEX.prompt.md
  echo "✓ Created symlink to CORTEX.prompt.md"
else
  # Windows: copy file
  cp "$CORTEX_PATH/cortex-brain/releases/v1.0.0/CORTEX.prompt.md" \
    .github/prompts/CORTEX.prompt.md
  echo "✓ Copied CORTEX.prompt.md"
fi

# Step 4: Validate MCP connectivity
echo "✓ Validating MCP connectivity..."
python3 - <<PYTHON_EOF
import requests
import json
import os

endpoint = os.getenv("CORTEX_MCP_ENDPOINT", "127.0.0.1:8000")
try:
  response = requests.get(f"http://{endpoint}/health", timeout=5)
  data = response.json()
  print(f"✓ MCP Server ready: {data['status']}")
  print(f"  Version: {data['version']}")
  print(f"  DB: {data['db']}")
except Exception as e:
  print(f"⚠ Warning: Could not connect to MCP server")
  print(f"  Make sure CORTEX hub is running: python scripts/setup-cortex-hub.py")
  print(f"  Endpoint: {endpoint}")
PYTHON_EOF

# Step 5: Create initial audit entry
echo "✓ Creating audit entry..."
git add .github/cortex-config.yaml .github/prompts/
git commit -m "feat: register repo $REPO_ID with CORTEX" || true

echo ""
echo "✅ Repo registration complete!"
echo ""
echo "Next steps:"
echo "  1. Test MCP connection: python -c 'import cortex.api.mcp; print(cortex.api.mcp.test_connection())'"
echo "  2. Load prompt: cat .github/prompts/CORTEX.prompt.md"
echo "  3. Start using Copilot in VS Code"
```

---

## SECTION 5: EDGE CASES & RISK MITIGATION

### 5.1 Edge Case: Network/MCP Server Unavailable

**Scenario:** User in Repo A loses network connectivity to MCP hub

**Current Behavior:** System fails hard (can't execute tools)

**Mitigation Strategy:**

```python
# In MCP client (repo side)

class MCPClientWithFallback:
    """MCP client with graceful degradation"""
    
    def __init__(self, hub_endpoint: str, local_rules_path: str):
        self.hub = MCPClient(hub_endpoint)
        self.fallback_rules = load_local_rules(local_rules_path)
        self.offline_mode = False
    
    async def call_orchestrator(self, tool: str, args: dict):
        """Call orchestrator with fallback"""
        try:
            # Try hub first
            return await self.hub.call(tool, args)
        except ConnectionError:
            logger.warning(f"Hub offline, using fallback for {tool}")
            self.offline_mode = True
            
            # Use local fallback (read-only)
            return self.call_local_fallback(tool, args)
    
    def call_local_fallback(self, tool: str, args: dict):
        """Local execution (limited capability)"""
        if tool in ["governance_check", "audit_read"]:
            # Read-only operations OK offline
            return execute_local(tool, args, self.fallback_rules)
        else:
            # Write operations not allowed offline
            raise OfflineError(
                f"Tool {tool} requires hub connection. "
                f"Changes will be queued for sync when online."
            )
    
    async def sync_offline_changes(self):
        """Replay offline audit log when reconnected"""
        if not self.offline_mode:
            return
        
        offline_log = self.load_local_audit_log()
        for entry in offline_log:
            try:
                await self.hub.submit_audit_entry(entry)
            except Exception as e:
                logger.error(f"Failed to sync: {entry['ac_id']}", exc_info=e)
                raise SyncError("Manual recovery required") from e
        
        self.offline_mode = False
        logger.info("Offline changes synced successfully")
```

**Requirement:**
- ✅ Read-only operations work offline (governance checks, audit reads)
- ✅ Write operations queue locally, sync on reconnect
- ✅ Clear visual indicator of offline mode (in VS Code)
- ✅ Audit trail shows "sync_timestamp" when queued changes committed

### 5.2 Edge Case: Prompt Version Mismatch

**Scenario:** Repo A uses prompt v1.0, but hub has upgraded to v1.1 (new orchestrators)

**Current Behavior:** Repo A doesn't know about new features

**Mitigation Strategy:**

```python
# In MCP client

async def connect_to_hub(repo_config: dict) -> MCPSession:
    """Connect with version negotiation"""
    repo_version = repo_config["prompt_version"]
    hub_version = await get_hub_version()
    
    if repo_version < hub_version:
        # Hub is newer
        if is_backward_compatible(hub_version, repo_version):
            logger.warning(
                f"Repo using v{repo_version}, hub has v{hub_version}. "
                f"Consider upgrading prompt."
            )
            # Allow connection, log warning
        else:
            # Breaking change
            raise IncompatibleVersionError(
                f"Prompt v{repo_version} incompatible with hub v{hub_version}. "
                f"Update .github/cortex-config.yaml: prompt_version: {hub_version}"
            )
    
    elif repo_version > hub_version:
        # Repo is newer (shouldn't happen, but handle it)
        raise VersionError(
            f"Repo prompt v{repo_version} newer than hub v{hub_version}. "
            f"Update CORTEX hub or downgrade repo."
        )
    
    return await create_session(repo_config)
```

**Requirement:**
- ✅ Clear error message when version incompatible
- ✅ Automatic version detection on hub
- ✅ Backward compatibility check matrix
- ✅ Easy upgrade path (.github/cortex-config.yaml change)

### 5.3 Edge Case: Repo-Specific Governance Conflict

**Scenario:** Repo A wants to override CORE-011 (type hints mandatory) to allow dynamic code

**Current Behavior:** No way to express intent or resolve conflict

**Mitigation Strategy:**

```python
# In governance engine

class GovernanceResolver:
    """Resolve rule conflicts with clear precedence"""
    
    def resolve(self, tier0_rules: dict, tier1_rules: dict) -> dict:
        """
        Precedence (highest to lowest):
        1. SKULL rules (immutable CORE-0xx rules - always win)
        2. Phase-specific rules (apply to this phase only)
        3. Repo overrides (can only add constraints, not remove)
        """
        result = {}
        
        # Start with Tier 0
        result.update(tier0_rules)
        
        # Apply Tier 1 (repo overrides)
        for rule_id, override_rule in tier1_rules.items():
            base_rule = result.get(rule_id)
            
            # Check: override can only be STRICTER, not LOOSER
            if override_rule.severity < base_rule.severity:
                raise GovernanceConflict(
                    f"Repo cannot relax CORE rule {rule_id}. "
                    f"Base severity: {base_rule.severity}, "
                    f"Override severity: {override_rule.severity}. "
                    f"Contact governance admin to adjust Tier 0 rules."
                )
            
            # Override is stricter → apply it
            result[rule_id] = override_rule
            logger.info(f"Applied repo override for {rule_id}")
        
        return result
```

**Requirement:**
- ✅ Tier 0 rules (CORE-xxx) cannot be overridden
- ✅ Tier 1 rules can only add constraints, not remove
- ✅ Clear error message when override violates rules
- ✅ Escalation path: request governance change in issue

### 5.4 Edge Case: Concurrent Repos Modifying Shared Code

**Scenario:** Both API repo and UI repo modify shared utils library

**Current Behavior:** Race conditions, merge conflicts

**Mitigation Strategy:**

```python
# In audit engine

class AuditLog(SQLiteBase):
    """Audit log with transaction support for cross-repo changes"""
    
    def begin_transaction(self, repo_ids: List[str]) -> Transaction:
        """
        Begin transaction across multiple repos.
        Locks affected repos until committed.
        """
        return Transaction(repo_ids=repo_ids)
    
    async def commit_multi_repo_change(
        self,
        transaction_id: str,
        changes: List[dict]
    ):
        """
        Atomically commit changes affecting multiple repos.
        All or nothing: partial commits not allowed.
        """
        with self.db:
            try:
                for change in changes:
                    repo_id = change["repo_id"]
                    # Check repo lock
                    if self.is_repo_locked(repo_id):
                        raise RepositoryLocked(
                            f"Repo {repo_id} locked by transaction "
                            f"{self.get_lock_owner(repo_id)}"
                        )
                    
                    # Record change with transaction reference
                    self.insert_audit_entry({
                        **change,
                        "transaction_id": transaction_id,
                        "timestamp": datetime.now()
                    })
                
                # All changes committed
                logger.info(f"Transaction {transaction_id} committed")
            
            except Exception as e:
                # Rollback all changes
                logger.error(f"Transaction {transaction_id} rolled back", exc_info=e)
                self.db.rollback()
                raise
```

**Requirement:**
- ✅ Multi-repo transactions (atomic commits)
- ✅ Lock detection and timeout
- ✅ Clear error message when locked
- ✅ Audit trail shows transaction ID

---

## SECTION 6: TESTING STRATEGY

### 6.1 Test Plan Matrix

| Test Scenario | Type | Priority | Success Criteria | Owner |
|---|---|---|---|---|
| Single repo connects to MCP | Integration | P0 | Session created, repo_id in audit log | automation |
| 5 repos connect to same MCP | Integration | P0 | 5 sessions, no cross-repo contamination | automation |
| Repo A modifies repo B's file | Isolation | P0 | ❌ BLOCKED by server (not allowed) | automation |
| Audit trail includes repo_id | Audit | P0 | Every entry has repo_id field | automation |
| MCP health check works | Integration | P1 | GET /health returns 200 + status | automation |
| Prompt version mismatch | Error | P1 | Clear error message, no connection | automation |
| MCP server unavailable | Resilience | P1 | Fallback to local rules, queued changes | automation |
| Repo A syncs offline changes | Integration | P2 | All queued changes replayed on reconnect | automation |
| VS Code connects to MCP | IDE | P2 | Governance violations shown inline | manual |
| VS Studio 2019+ connects via LSP | IDE | P2 | LSP adapter bridges to MCP correctly | manual |
| 3-way governance conflict | Governance | P2 | Clear error, escalation path provided | automation |

### 6.2 Test Implementation (pytest)

```python
# tests/integration/test_multi_repo_deployment.py

@pytest.mark.integration
class TestMultiRepoDeployment:
    
    async def test_five_repos_connect_isolated(self):
        """5 repos connect to MCP without cross-contamination"""
        # Setup 5 repos
        repos = [
            create_test_repo(f"repo-{i}", f"Test Repo {i}")
            for i in range(1, 6)
        ]
        
        # Connect all to same MCP
        sessions = [
            await mcp_server.create_session(repo.config)
            for repo in repos
        ]
        
        # Verify: each session isolated
        for i, session in enumerate(sessions):
            assert session.repo_id == repos[i].config["repo_id"]
            assert session.session_id != sessions[(i+1) % 5].session_id
        
        # Verify: audit trail includes repo_id
        audit_entries = db.query(
            "SELECT repo_id FROM audit_log WHERE event='session_created' ORDER BY timestamp DESC LIMIT 5"
        )
        assert len(audit_entries) == 5
        assert set(e["repo_id"] for e in audit_entries) == {f"repo-{i}" for i in range(1, 6)}
    
    async def test_repo_isolation_prevents_cross_modification(self):
        """Repo A cannot modify Repo B's files"""
        repo_a = create_test_repo("api-service", "API")
        repo_b = create_test_repo("ui-app", "UI")
        
        session_a = await mcp_server.create_session(repo_a.config)
        
        # Try to modify Repo B's file using Repo A's session
        with pytest.raises(RepositoryIsolationError):
            await mcp_server.handle_tool_call(
                session_id=session_a.session_id,
                tool_name="code_generator",
                args={
                    "file_path": repo_b.path / "src/App.tsx",
                    "content": "malicious code"
                }
            )
    
    async def test_prompt_version_mismatch_error(self):
        """Incompatible prompt version rejected"""
        repo = create_test_repo("api-service", "API")
        repo.config["prompt_version"] = "2.0.0"  # Newer than hub
        
        with pytest.raises(IncompatibleVersionError):
            await mcp_server.create_session(repo.config)
    
    async def test_offline_fallback_queues_writes(self):
        """Write operations queued when offline, synced on reconnect"""
        repo = create_test_repo("api-service", "API")
        client = MCPClientWithFallback(
            hub_endpoint="127.0.0.1:9999",  # Non-existent
            local_rules_path=repo.path / ".github/tier0"
        )
        
        # Read-only should work
        result = await client.call_orchestrator("governance_check", {
            "file": "src/main.py"
        })
        assert result["status"] == "ok"
        
        # Write should fail gracefully
        with pytest.raises(OfflineError):
            await client.call_orchestrator("code_refactor", {
                "file": "src/main.py"
            })
        
        # Verify queued for later
        queued = client.load_local_audit_log()
        assert len(queued) == 1
        assert queued[0]["tool"] == "code_refactor"
```

---

## SECTION 7: RISK ASSESSMENT & MITIGATION

### 7.1 Production Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| MCP server single point of failure | MEDIUM | CRITICAL (all repos offline) | Implement failover MCP (standby server), health checks, circuit breaker |
| Audit trail race conditions (5 repos writing concurrently) | MEDIUM | HIGH (inconsistent audit) | SQLite WAL mode (already enabled), transaction support |
| Prompt version incompatibility breaks IDE features | MEDIUM | MEDIUM (feature outage) | Version negotiation, backward compatibility matrix, clear error messages |
| VS Studio LSP adapter not compatible with 2019 | LOW | HIGH (no VS support) | Early testing with VS 2019, fallback to command-line tool |
| Repos can't access knowledge graph safely | MEDIUM | MEDIUM (cross-repo learning blocked) | Implement read-only queries, audit all graph accesses |
| Performance degradation with 100+ repos | LOW | MEDIUM (slow MCP responses) | Caching strategy, repo connection pooling, DB indexing |

### 7.2 Mitigation Actions

#### Risk Mitigation 1: MCP Server Failover
```yaml
Implement:
  - Standby MCP server (hot standby, synced database)
  - Health check monitors (detect failure in <5s)
  - Automatic failover (DNS switch or service discovery)
  - Repos retry on failover (exponential backoff)
  
Timeline: Week 4 (part of TASK-9 testing)
```

#### Risk Mitigation 2: Audit Trail Consistency
```python
# Use SQLite WAL mode + explicit transactions
DB_INIT_SQL = """
PRAGMA journal_mode = WAL;
PRAGMA synchronous = FULL;
BEGIN TRANSACTION;
  INSERT INTO audit_log (...) VALUES (...);
  -- All changes atomic
COMMIT;
"""
```

#### Risk Mitigation 3: VS Studio 2019+ Testing
```
Action:
  - Provision VS 2019 environment early (Week 2)
  - Test LSP adapter with native VS diagnostics
  - Have fallback CLI tool ready if LSP fails
  
Timeline: Week 2 (parallel with other tasks)
```

---

## SECTION 8: SUCCESS CRITERIA & SIGN-OFF

### 8.1 Deployment Phase Success Criteria

**All criteria must be met for production readiness:**

- [ ] **Criterion 1: Multi-Repo Isolation**
  - 5 repos connect to same MCP
  - Repo A cannot access/modify Repo B's files
  - Each change audited with correct repo_id
  - Verification: `test_five_repos_connect_isolated` + `test_repo_isolation_prevents_cross_modification` passing

- [ ] **Criterion 2: Deterministic Setup**
  - `setup-cortex-hub.py` initializes hub without errors
  - `register-repo.sh` sets up new repo without manual steps
  - Both scripts idempotent (can run twice safely)
  - Verification: Scripts run 3 times in sequence, same result

- [ ] **Criterion 3: Governance Compliance**
  - All CORE rules enforced across repos
  - Tier 0 rules immutable (cannot override)
  - Tier 1 rules inherited + can add constraints
  - Verification: Governance resolver tests (5 conflict scenarios)

- [ ] **Criterion 4: Audit Trail Integrity**
  - Every change logged with repo_id + session_id
  - No audit entries missing (hash chain unbroken)
  - Cross-repo transactions atomic
  - Verification: Audit consistency tests (100% entries present)

- [ ] **Criterion 5: VS Code Support**
  - VS Code extension connects to MCP
  - Governance violations shown inline
  - Quick-fix suggestions work
  - Verification: Manual testing in VS Code (5 scenarios)

- [ ] **Criterion 6: Visual Studio 2019+ Support**
  - LSP adapter bridges VS ↔ MCP
  - Diagnostics displayed in VS
  - No Python environment conflicts
  - Verification: Manual testing in VS 2019 (3 scenarios)

- [ ] **Criterion 7: Production Resilience**
  - MCP server unavailable → fallback to local rules (read-only)
  - Offline changes queued locally, synced on reconnect
  - Version mismatches caught with clear errors
  - Verification: Offline tests (edge case scenarios)

- [ ] **Criterion 8: Documentation Complete**
  - Deployment guide (setup steps for 3 repos)
  - Architecture document (decision rationale)
  - Troubleshooting guide (5+ common issues + fixes)
  - Verification: Tech reviewer sign-off

- [ ] **Criterion 9: Test Coverage**
  - 100% of new code covered by tests
  - All edge cases tested (9 scenarios)
  - All 5 repos tested end-to-end
  - Verification: pytest coverage report ≥95%

- [ ] **Criterion 10: No Regressions**
  - All existing CORTEX tests still passing (pre-deployment)
  - No broken governance rules
  - No audit trail gaps
  - Verification: `pytest tests/ --tb=short` (0 failures)

### 8.2 Sign-Off Checklist

**Before marking deployment phase complete, verify:**

```yaml
Technical Review:
  - ✅ All 10 success criteria met
  - ✅ All 4 critical blockers resolved
  - ✅ All 9 edge cases handled
  - ✅ Performance acceptable (<100ms per MCP call)
  - ✅ Security review passed (no isolation breaches)

Compliance Review:
  - ✅ All CORE governance rules enforced
  - ✅ All AC audit entries present (AC_START, AC_EXECUTE, AC_COMPLETE)
  - ✅ Hash chain integrity verified
  - ✅ Tier 0 rules immutable in all repos

Documentation Review:
  - ✅ Deployment guide clear and complete
  - ✅ Architecture decisions documented with rationale
  - ✅ Examples work (tested manually)
  - ✅ Troubleshooting covers 5+ scenarios

Stakeholder Approval:
  - ✅ Author (Asif): Architecture approved
  - ✅ Tech Lead: Implementation plan approved
  - ✅ DevOps: Infrastructure requirements confirmed
  - ✅ Security: Multi-tenancy isolation verified
```

---

## SECTION 9: DEPENDENCIES & BLOCKERS

### 9.1 External Dependencies

| Dependency | Status | Impact | Owner |
|---|---|---|---|
| Python 3.9+ (for async/await syntax) | ✅ Available | Core runtime | DevOps |
| SQLite WAL mode support | ✅ Available | Audit trail atomicity | DB admin |
| VS Code LSP client support | ✅ Available | IDE integration | VS Code team |
| VS Studio 2019 LSP support | ⚠️ Need to verify | IDE integration | Microsoft |
| MCP protocol v1.0 | ✅ Available | Core protocol | Anthropic |
| Git hooks for audit validation | ✅ Available | Pre-commit validation | Git admin |

### 9.2 Internal Dependencies

| Task | Depends On | Status |
|---|---|---|
| TASK-1 (Session Context) | None | ✅ Ready |
| TASK-2 (Health Check) | None | ✅ Ready |
| TASK-3 (Service Discovery) | TASK-2 | ⏳ Blocked |
| TASK-4 (Prompt Versioning) | TASK-3 | ⏳ Blocked |
| TASK-5 (Repo Registry) | TASK-1 | ⏳ Blocked |
| TASK-6 (Hub Setup Script) | TASK-4, TASK-5 | ⏳ Blocked |
| TASK-7 (Repo Setup Script) | TASK-4, TASK-5 | ⏳ Blocked |
| TASK-8 (Isolation Rules) | TASK-1, TASK-5 | ⏳ Blocked |
| TASK-9 (Integration Tests) | TASK-8 | ⏳ Blocked |
| TASK-10 (VS Code Extension) | TASK-2 | ⏳ Can start Week 2 |
| TASK-11 (VS Studio LSP) | TASK-2 | ⏳ Can start Week 2 |
| TASK-12 (Documentation) | All tasks | ⏳ Blocked |

---

## SECTION 10: RECOMMENDATIONS & NEXT STEPS

### 10.1 Decision Point: Approve Architecture?

**Recommended Decision:** ✅ **PROCEED with Three-Tier Deployment Architecture**

**Rationale:**
1. ✅ Balances **correctness** (proper isolation), **safety** (no cross-repo contamination), **auditability** (all changes logged with context)
2. ✅ Scales efficiently (O(1) MCP operations, not O(n))
3. ✅ Compliant with governance (CORE-026, CORE-027, CORE-005)
4. ✅ Production-ready patterns (health checks, failover, offline mode)
5. ✅ Supports all target IDEs (VS Code + VS 2019+)
6. ✅ Clear success criteria for each phase

**Timeline:** 3 weeks, 18-20 days effort
**Blockers:** 0 (can start immediately)
**Risk Level:** MEDIUM (well-scoped, mitigation plans defined)

### 10.2 Immediate Actions (Next 24 Hours)

1. **Approve Architecture** (1 hour)
   - Review 3.1-3.2 (Three-Tier Model + Decisions)
   - Confirm: Option A (VERSION TAGS) for prompt distribution
   - Confirm: LSP Adapter for VS Studio 2019+ support
   - Sign-off: Proceed with Week 1 tasks

2. **Schedule Implementation Team** (1 hour)
   - Assign TASK-1, TASK-2, TASK-3 to parallel workers
   - Allocate 5-7 days for core tasks
   - Reserve Week 4 for testing + docs

3. **Provision Development Environment** (2 hours)
   - Setup test MCP server (for Task-1 validation)
   - Provision VS 2019 VM (for Task-11 testing)
   - Create git branch: `feature/deployment-redesign`

4. **Create Roadmap Issues** (1 hour)
   - Create GitHub issues for TASK-1 through TASK-12
   - Link to Issue #7 (deployment gaps)
   - Set milestone: "Multi-Repo Deployment (Feb 2026)"

### 10.3 Deliverables by End of Phase

**Design Phase (This Document):**
- ✅ Current state analysis (Section 1)
- ✅ Gap analysis (Section 2)
- ✅ Recommended architecture (Section 3)
- ✅ Implementation roadmap (Section 4)
- ✅ Edge case handling (Section 5)
- ✅ Testing strategy (Section 6)
- ✅ Risk assessment (Section 7)
- ✅ Success criteria (Section 8)

**Implementation Phase (Weeks 2-3):**
- [ ] Extended MCPServer with session context
- [ ] Health check + discovery endpoints
- [ ] Prompt version manager (cortex-brain/releases/)
- [ ] Repo registry system (repo-registry.yaml)
- [ ] Setup scripts (setup-cortex-hub.py + register-repo.sh)
- [ ] Integration tests (all 9 edge cases)
- [ ] VS Code MCP consumer
- [ ] VS Studio LSP adapter

**Production Phase (Week 4):**
- [ ] Production deployment guide
- [ ] Architecture decision records (ADR)
- [ ] Troubleshooting runbook
- [ ] Knowledge graph integration

---

## APPENDIX A: Glossary

| Term | Definition |
|------|-----------|
| **MCP** | Model Context Protocol - standardized tool interface |
| **Session** | Per-connection context (repo_id, paths, versioning) |
| **Repo Isolation** | Hard boundary preventing cross-repo contamination |
| **Tier 0** | Immutable SKULL rules (apply everywhere) |
| **Tier 1** | Repo-specific governance (can add constraints only) |
| **Prompt Version** | CORTEX.prompt.md semantic version (v1.0.0) |
| **Service Discovery** | Automatic MCP endpoint lookup (env var → config) |
| **LSP** | Language Server Protocol (IDE integration) |
| **IPC** | Inter-Process Communication (local MCP transport) |
| **WAL Mode** | SQLite Write-Ahead Logging (concurrent access) |
| **Audit Trail** | Append-only log of all changes (hash-chained) |

---

## APPENDIX B: References

**GitHub Issues:**
- [#7 Deployment gaps](https://github.com/asifhussain60/CORTEX/issues/7)

**CORTEX Documentation:**
- `docs/cortex-builder.prompt.md` (instructions for builders)
- `_workspaces/roadmap/cortex-master.yaml` (phase tracker)
- `cortex_brain/tier0/governance/core-rules.yaml` (SKULL rules)

**Code References:**
- `src/mcp/server.py` (MCP server implementation)
- `cortex/api/orchestrators/` (orchestrator registry)
- `cortex/core/governance/` (governance engine)
- `tests/integration/` (integration tests)

**Standards:**
- [MCP Protocol Spec](https://modelcontextprotocol.io/)
- [LSP Specification](https://microsoft.github.io/language-server-protocol/)
- [SQLite WAL](https://sqlite.org/wal.html)

---

**Document Status:** ✅ READY FOR REVIEW & APPROVAL
**Next: Week 1 Implementation Kickoff (January 20-24, 2026)**
