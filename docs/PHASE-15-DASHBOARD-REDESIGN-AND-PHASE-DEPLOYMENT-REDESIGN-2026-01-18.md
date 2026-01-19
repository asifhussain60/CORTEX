# PHASE-15-DASHBOARD-REDESIGN & PHASE-DEPLOYMENT-REDESIGN
## Universal CORTEX Multi-Repository Architecture (2026-01-18)

## Executive Overview

**New Architecture:**
CORTEX operates as a **universal command center** that can be cloned into any company repo folder, exposing MCP tools globally while operating entirely from the CORTEX folder but making changes in the user's current repo.

**Key Features:**
- Single-command installation: `git clone https://github.com/company/cortex.git && cortex init`
- MCP tools exposed from `CORTEX.prompt.md` usable in ANY repo
- All CORTEX logic executes from `./CORTEX/` but reads/modifies user's repo
- One-command upgrade: `cortex upgrade` pulls from main branch
- Production-ready from clone without additional setup

---

## PHASE-15: CORTEX Dashboard (REDESIGNED)

### Purpose
Production-grade dashboard for visualizing CORTEX operations across ANY repo utilizing the system, with single-click setup and universal tool access.

### Architecture Changes (from baseline)

**OLD (Baseline - PHASE-15):**
- Dashboard hosted in `src/dashboard/`
- Served from CORTEX repo only
- Tied to CORTEX internal metrics
- Complex multi-file setup

**NEW (Redesigned - PHASE-15-UNIVERSAL):**
- Dashboard runs from `CORTEX/dashboard/`
- Operates on ANY repo that has cloned CORTEX
- Reads repo-agnostic metrics (file count, test coverage, etc.)
- Single HTML file + embedded JavaScript (no build step)
- Responsive, works everywhere

### Scope (16 AC-IDs)

#### A. Dashboard Foundation (4 ACs)
- **AC-DASH-001-01**: Universal dashboard shell (HTML + embedded JS)
- **AC-DASH-001-02**: Repo detection & configuration auto-discovery
- **AC-DASH-001-03**: Real-time metrics collection interface
- **AC-DASH-001-04**: Multi-repo context switching

#### B. Visualization Layers (4 ACs)
- **AC-DASH-002-01**: Repository health overview (files, tests, commits)
- **AC-DASH-002-02**: CORTEX operation dashboard (last 100 AI operations)
- **AC-DASH-002-03**: MCP tool status & usage statistics
- **AC-DASH-002-04**: Governance compliance heatmap (SKULL rules)

#### C. Real-Time Features (4 ACs)
- **AC-DASH-003-01**: WebSocket connection to CORTEX backend
- **AC-DASH-003-02**: Live audit trail streaming
- **AC-DASH-003-03**: Real-time test execution tracking
- **AC-DASH-003-04**: Alert & notification system

#### D. User Experience (4 ACs)
- **AC-DASH-004-01**: Dark/light theme toggle with persistence
- **AC-DASH-004-02**: Export reports (PDF, JSON, CSV)
- **AC-DASH-004-03**: Custom dashboard layouts
- **AC-DASH-004-04**: Search & filter across all metrics

### File Structure

```
CORTEX/
├── dashboard/
│   ├── index.html                    # Universal dashboard (single file)
│   ├── assets/
│   │   ├── cortex-logo.svg
│   │   ├── light-theme.css           # Embedded in HTML
│   │   └── dark-theme.css            # Embedded in HTML
│   ├── js/
│   │   └── app.js                    # Embedded in HTML
│   ├── server.py                     # Optional: local dev server
│   └── README.md                     # Setup instructions
```

### Key Features

**Universal Design:**
- Works in ANY repo that cloned CORTEX
- Zero dependencies (uses CDN libraries only)
- No build process
- Single `cortex dashboard` command

**Repo-Agnostic Metrics:**
- File tree overview
- Test coverage (if tests exist)
- Git commit timeline
- CORTEX operation history
- Governance compliance

**MCP Tool Visibility:**
- See all exposed tools from current repo
- View tool usage statistics
- Track successful/failed operations
- Audit trail by tool

### Implementation Timeline

**Week 1: Foundation (AC-DASH-001-01 to 004)**
- Universal HTML shell with responsive design
- Repo detection and auto-config
- Metrics collection interface

**Week 2: Visualization (AC-DASH-002-01 to 004)**
- Health dashboard
- CORTEX operations dashboard
- MCP tools status
- Compliance heatmap

**Week 3: Real-Time (AC-DASH-003-01 to 004)**
- WebSocket integration
- Audit streaming
- Test tracking
- Alerts

**Week 4: Polish (AC-DASH-004-01 to 004)**
- Theming
- Export capabilities
- Custom layouts
- Search & filter

### Success Criteria

- ✅ Dashboard loads in <2 seconds
- ✅ Works in any repo without setup
- ✅ All 16 ACs with passing tests
- ✅ Zero hardcoded paths (all relative)
- ✅ No external dependencies required
- ✅ Responsive on mobile/tablet/desktop
- ✅ Dark/light mode functional
- ✅ Export works for all report types

---

## PHASE-DEPLOYMENT: CORTEX Production Deployment & Distribution (REDESIGNED)

### Purpose
Enable single-command installation, multi-repo deployment, upgrade capability, and production distribution of CORTEX as a universal development tool.

### New Deployment Model

**OLD (Baseline):**
- CORTEX deployed as isolated monolith
- Tied to specific repo
- Manual setup required
- No upgrade path

**NEW (Redesigned):**
- CORTEX as distributed command center
- Clones into any company repo folder
- Auto-discovers existing repos
- Single-command upgrade
- Backward-compatible patches

### Scope (10 AC-IDs)

#### A. Installation & Bootstrap (3 ACs)
- **AC-DEPLOY-001-01**: `cortex init` command - single-step setup
- **AC-DEPLOY-001-02**: Auto-detection of company repo structure
- **AC-DEPLOY-001-03**: MCP tool registration in user's MCP client

#### B. Multi-Repo Architecture (3 ACs)
- **AC-DEPLOY-002-01**: CORTEX operates from isolated folder but reads/modifies user repo
- **AC-DEPLOY-002-02**: Context switching between repos
- **AC-DEPLOY-002-03**: Shared state management (audit trail, cache)

#### C. Upgrade & Distribution (2 ACs)
- **AC-DEPLOY-003-01**: `cortex upgrade` - pull latest from main branch
- **AC-DEPLOY-003-02**: Backward-compatible versioning & migration

#### D. Production Readiness (2 ACs)
- **AC-DEPLOY-004-01**: Security hardening (no secrets in CORTEX folder)
- **AC-DEPLOY-004-02**: Performance optimization & resource limits

### File Structure Post-Deployment

```
company-repo/
├── .git/
├── src/
├── tests/
├── [user's existing files]
│
└── CORTEX/                               # User clones CORTEX here
    ├── .git/ (separate from parent)      # Independent git history
    ├── cortex                            # CLI entry point
    ├── dashboard/                        # Universal dashboard
    ├── .github/prompts/
    │   ├── CORTEX.prompt.md              # Master orchestrator
    │   ├── cortex-builder.prompt.md      # Implementation guide
    │   └── [other prompts]
    ├── cortex_brain/                     # Governance engine
    │   ├── tier0/governance/
    │   ├── state/governance.db           # Audit trail
    │   └── [core files]
    ├── scripts/
    ├── .env.example
    ├── requirements.txt
    └── README.md
```

**Key Points:**
- CORTEX has its own `.git` folder (separate from parent)
- Parent repo unchanged except for `CORTEX/` folder
- All CORTEX operations read from parent repo's `src/`, `tests/`, etc.
- Audit trail stays in `CORTEX/cortex_brain/state/governance.db`
- MCP tools can operate on parent repo files

### Installation Flow

```bash
# Step 1: Clone CORTEX into company repo
cd company-repo
git clone https://github.com/cortex-ai/cortex.git CORTEX
cd CORTEX

# Step 2: Initialize CORTEX for this repo
./cortex init

# Step 3: Register MCP tools (automated)
# cortex init auto-detects user's MCP client and registers tools

# Step 4: Start using CORTEX
cortex dashboard              # Open dashboard
cortex tools list            # See available MCP tools
cortex plan <project>        # Plan project improvements
```

### Key Capabilities

**Single-Repo Context:**
```bash
# Automatic - CORTEX knows parent repo structure
$ cortex dashboard
→ Opens dashboard showing parent repo metrics
→ Shows all MCP tools available for parent repo
→ Displays recent CORTEX operations on parent repo
```

**Multi-Repo Navigation:**
```bash
# If multiple repos with CORTEX installed
$ cortex switch ../another-repo/CORTEX
→ Switches context to another-repo
→ Dashboard shows that repo's metrics
→ All tools operate on that repo
```

**Upgrade Path:**
```bash
# Pull latest features from main branch
$ cortex upgrade
→ Checks for updates
→ Auto-merges non-breaking changes
→ Migrates state if needed
→ Verifies audit trail integrity
```

### Implementation Timeline

**Week 1: Bootstrap (AC-DEPLOY-001-01 to 003)**
- Installation script
- Auto-detection
- MCP registration

**Week 2: Architecture (AC-DEPLOY-002-01 to 003)**
- Path isolation (CORTEX folder reads/modifies parent)
- Context switching
- Shared state

**Week 3: Distribution (AC-DEPLOY-003-01 to 002)**
- Upgrade mechanism
- Versioning & migration

**Week 4: Hardening (AC-DEPLOY-004-01 to 002)**
- Security review
- Performance tuning

### Success Criteria

- ✅ Single `git clone + cortex init` works
- ✅ Dashboard accessible immediately after init
- ✅ MCP tools available in user's client
- ✅ Parent repo completely unchanged (except CORTEX/ folder)
- ✅ `cortex upgrade` pulls latest without breaking existing state
- ✅ All 10 ACs with passing tests
- ✅ No secrets stored in CORTEX folder
- ✅ Performance: all operations <1 second response time
- ✅ Audit trail maintains integrity through upgrades

### Deployment Targets

**Phase 1: Internal Testing**
- Clone into sample company repos
- Verify dashboard works
- Test MCP tool exposure
- Validate audit trail

**Phase 2: Alpha Release**
- Release to internal teams
- Collect feedback
- Fix issues
- Document patterns

**Phase 3: Beta Release**
- Public beta
- Community feedback
- Hardening based on real usage
- Documentation

**Phase 4: GA Release**
- Production-ready
- SLA support
- Upgrade guarantees
- Long-term support plan

---

## Implementation Priority Matrix

### Critical Path Dependencies

```
AC-DEPLOY-001-01 (Init command)
    ↓
AC-DEPLOY-001-02 (Auto-detection)
    ↓
AC-DEPLOY-002-01 (Path isolation)
    ↓
AC-DASH-001-01 (Dashboard shell)
    ↓
AC-DEPLOY-001-03 (MCP registration)
```

### Implementation Order

1. **Weeks 1-2: Deployment Foundation** (AC-DEPLOY-001-01/02/03 + AC-DEPLOY-002-01)
   - Install CLI and bootstrap script
   - Test path isolation
   - Verify MCP tool registration

2. **Weeks 3-4: Dashboard Foundation** (AC-DASH-001-01/02/03/04)
   - Universal dashboard shell
   - Repo detection
   - Metrics collection

3. **Weeks 5-6: Multi-Repo Support** (AC-DEPLOY-002-02/03)
   - Context switching
   - Shared state
   - Dashboard multi-repo views

4. **Weeks 7-8: Visualization** (AC-DASH-002-01/02/03/04)
   - All dashboard metrics
   - Real-time features
   - Compliance views

5. **Weeks 9-10: Upgrade Path** (AC-DEPLOY-003-01/02)
   - Versioning
   - Migration logic
   - Rollback capability

6. **Weeks 11-12: Polish** (AC-DASH-004-01/02/03/04 + AC-DEPLOY-004-01/02)
   - Theming
   - Export
   - Security hardening

---

## File Updates Required

### cortex-master.yaml Phase Entries

**PHASE-15-DASHBOARD (REDESIGNED):**
```yaml
PHASE-15-DASHBOARD:
  title: "Universal CORTEX Dashboard - Multi-Repo Visualization"
  description: |
    Production-grade dashboard for visualizing CORTEX operations across 
    any repo utilizing the system. Universal design, zero setup required.
  
  status: "ENHANCEMENT_READY"
  locked: false
  
  enhancement_phase: true
  implement_when_ready: true
  
  ac_ids: 16
  completed_ac_ids: 0
  
  files_to_create:
    - "CORTEX/dashboard/index.html"
    - "CORTEX/dashboard/server.py"
    - "CORTEX/dashboard/README.md"
```

**PHASE-DEPLOYMENT (REDESIGNED):**
```yaml
PHASE-DEPLOYMENT:
  title: "CORTEX Universal Deployment & Distribution"
  description: |
    Single-command installation, multi-repo deployment, upgrade capability,
    and production distribution of CORTEX as universal development tool.
  
  status: "NOT_STARTED"
  locked: false
  
  enhancement_phase: true
  implement_when_ready: true
  
  ac_ids: 10
  completed_ac_ids: 0
  
  files_to_create:
    - "cortex"                          # CLI entry point
    - "scripts/init.sh"
    - "scripts/upgrade.sh"
    - ".env.example"
```

---

## Governance Integration

**All phases MUST enforce:**
- CORE-008: Tests first (RED → GREEN)
- CORE-011: Type hints mandatory
- CORE-012: Google-style docstrings
- CORE-026: Git checkpoints
- CORE-027: Audit logging (AC_START/EXECUTE/COMPLETE)
- CORE-028: Kebab-case naming, ≤25 chars

**Multi-Repo Specific:**
- No hardcoded paths (use `Path(__file__).parent`)
- All file operations relative to working repo
- Audit trail stored in CORTEX/cortex_brain/state/governance.db
- MCP tools must operate on parent repo context

---

## Success Metrics

### Dashboard (PHASE-15)
- Load time: <2 seconds
- Mobile responsive: 100%
- Test coverage: >85%
- Zero external dependencies
- Works in all repos

### Deployment (PHASE-DEPLOYMENT)
- Install time: <5 minutes
- Init success rate: >99%
- Upgrade success rate: >99%
- Breaking changes: 0
- Support queries: <5% of user base

---

## Next Steps

1. **Update cortex-master.yaml** with redesigned phases
2. **Create AC specifications** for each AC-ID
3. **Begin PHASE-DEPLOYMENT-001-01** (init command)
4. **Parallel track PHASE-15-DASHBOARD-001-01** (universal shell)
5. **Regular sync** with governance enforcement at each AC completion
