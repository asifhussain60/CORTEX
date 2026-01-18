# CORTEX Universal Architecture - Quick Reference (2026-01-18)

## TL;DR - What Changed?

| Aspect | Before | After |
|--------|--------|-------|
| **Location** | Mixed in repo | Isolated in `CORTEX/` folder |
| **Dashboard** | CORTEX metrics only | Any repo metrics + MCP tools |
| **Installation** | Complex setup | `git clone + cortex init` |
| **Upgrades** | Manual | `cortex upgrade` (1 command) |
| **Parent Repo** | Modified extensively | Unchanged (except `CORTEX/` folder) |
| **Multi-repo** | Not supported | Built-in context switching |
| **MCP Tools** | Limited access | Universal via `CORTEX.prompt.md` |

---

## Installation (For Any Repo)

```bash
# 1. Clone CORTEX
cd company-repo
git clone https://github.com/cortex-ai/cortex.git CORTEX

# 2. Initialize
cd CORTEX
./cortex init

# 3. Use immediately
cortex dashboard              # Opens dashboard
cortex tools list            # See MCP tools
cortex plan <project>        # Start planning
```

**Time**: <5 minutes from clone to ready  
**User action**: None required after init  

---

## Directory Structure (Post-Install)

```
company-repo/
├── .git/                          ← Parent repo git
├── src/                           ← User's code (UNCHANGED)
├── tests/                         ← User's tests (UNCHANGED)
├── README.md                      ← User's docs (UNCHANGED)
│
└── CORTEX/                        ← NEW: Self-contained CORTEX
    ├── .git/                      ← CORTEX's own git history
    ├── cortex                     ← CLI entry point (executable)
    ├── dashboard/
    │   ├── index.html             ← Universal dashboard (single file)
    │   └── [embedded JS/CSS]
    ├── cortex-brain/
    │   ├── state/
    │   │   └── governance.db      ← Audit trail (isolated)
    │   ├── api/
    │   │   └── main.py            ← FastAPI backend
    │   └── [CORTEX internals]
    ├── .github/prompts/
    │   ├── CORTEX.prompt.md       ← MCP tool exposure
    │   └── cortex-builder.prompt.md
    ├── .env.example               ← Configuration template
    ├── scripts/
    │   ├── init.sh                ← Bootstrap script
    │   └── upgrade.sh             ← Upgrade script
    └── requirements.txt           ← Dependencies
```

---

## Two New Phases (Implementation Ready)

### PHASE-15-DASHBOARD-UNIVERSAL (16 ACs)

**Purpose**: Universal dashboard for ANY repo using CORTEX

| Section | ACs | Deliverable |
|---------|-----|-------------|
| **A: Foundation** | 4 | Shell, auto-detect, metrics, context switch |
| **B: Visualization** | 4 | Health, CORTEX ops, MCP tools, compliance |
| **C: Real-Time** | 4 | WebSocket, audit stream, test track, alerts |
| **D: UX** | 4 | Theme, export, layouts, search |

**Timeline**: 4 weeks  
**Key Feature**: Works immediately, zero config  

### PHASE-DEPLOYMENT (10 ACs)

**Purpose**: Single-command deployment & upgrade infrastructure

| Section | ACs | Deliverable |
|---------|-----|-------------|
| **A: Bootstrap** | 3 | Init command, detection, MCP registration |
| **B: Multi-Repo** | 3 | Path isolation, context switch, shared state |
| **C: Upgrade** | 2 | Upgrade command, backward compatibility |
| **D: Production** | 2 | Security, performance |

**Timeline**: 4 weeks (starts after PHASE-15 locked)  
**Key Feature**: `cortex upgrade` with zero breaking changes  

---

## Gating Logic (When to Implement)

### Enhancement Phase Conditions

```python
# ONLY implement when ALL true:
if (ONLY ONE phase with locked: false):
    if (that phase has implement_when_ready: true):
        if (ALL other phases have locked: true):
            if (audit trail verified):
                # ✅ READY FOR IMPLEMENTATION
                implement_phase()
            else:
                # ⏳ WAIT: Audit trail not verified
                continue_with_mandatory_phases()
        else:
            # ⏳ WAIT: Other phases still unlocked
            continue_with_mandatory_phases()
    else:
        # Mandatory phase - implement immediately
        implement_phase()
else:
    # ⏳ WAIT: Multiple unlocked phases
    continue_with_mandatory_phases()
```

**In Plain English**: 
- Don't start PHASE-15 or PHASE-DEPLOYMENT until all other phases are locked
- Only ONE enhancement phase can be in progress at a time
- System must be in stable state before enhancement work

---

## Daily Development Workflow

### For Dashboard Development (PHASE-15)

**Day 1: AC-DASH-001-01**
```bash
# 1. Write test (RED)
cd CORTEX
pytest tests/test_dashboard_foundation.py::test_dashboard_loads -v
# → FAILS

# 2. Implement (GREEN)
# Create: CORTEX/dashboard/index.html
# Add: @app.get("/dashboard") endpoint

# 3. Test passes
pytest tests/test_dashboard_foundation.py::test_dashboard_loads -v
# → PASSES ✅

# 4. Commit checkpoint
git add .
git commit -m "AC-DASH-001-01: Universal dashboard shell ✅"
```

**Repeat for each AC** (16 total)

### For Deployment Development (PHASE-DEPLOYMENT)

Similar pattern - RED → GREEN → COMMIT for each AC (10 total)

---

## MCP Tool Access

### Before (Limited)
```
User in: company-repo/
CORTEX in: company-repo/
MCP tools: Only what's in company-repo/
```

### After (Universal)
```
User in: company-repo/
CORTEX in: company-repo/CORTEX/
MCP tools: CORTEX.prompt.md from CORTEX/ folder
Access: From ANY repo - universal!
```

**Example Usage**:
```bash
# User is in: /company/project-a/
# CORTEX is in: /company/project-a/CORTEX/

# User can access:
cortex tools list              # Lists all MCP tools from CORTEX
cortex plan <file>            # Uses CORTEX planning on project-a files

# Tools operate on: project-a (user's repo)
# CORTEX logic runs from: project-a/CORTEX/ (isolated)
```

---

## Testing Strategy (CORE-008)

**For EVERY AC-ID**:

```bash
# 1. RED Phase - Write test that fails
pytest tests/test_dashboard.py::test_ac_dash_001_01 -v
# ❌ FAIL (test doesn't exist yet)

# 2. GREEN Phase - Implement to pass test
# Write the code...

# 3. Test passes
pytest tests/test_dashboard.py::test_ac_dash_001_01 -v
# ✅ PASS

# 4. REFACTOR Phase - Improve code quality
# Add type hints (CORE-011)
# Add docstrings (CORE-012)
# Improve error handling (CORE-013)

# 5. Test still passes
pytest tests/test_dashboard.py::test_ac_dash_001_01 -v
# ✅ PASS

# 6. Commit with AC-ID reference
git commit -m "AC-DASH-001-01: Dashboard shell with tests ✅"
```

**Coverage Target**: >85% for all ACs, >95% for critical functions

---

## Git Workflow

```bash
# During development
git commit -m "AC-DASH-001-01: Feature X in progress"

# When AC completes
git commit -m "AC-DASH-001-01: Feature X complete ✅"

# When Section (4 ACs) completes
git commit -m "Section A (AC-DASH-001-*): Foundation complete ✅"

# When Phase completes
git commit -m "PHASE-15-DASHBOARD-UNIVERSAL: All 16 ACs complete ✅"
git tag -a "PHASE-15-DASHBOARD-UNIVERSAL-COMPLETE" \
    -m "Production ready dashboard for universal deployment"
```

**Key Rule**: Git checkpoint after EVERY AC (CORE-026)

---

## Success Checklist

### PHASE-15-DASHBOARD-UNIVERSAL
- [ ] All 16 ACs passing tests
- [ ] Dashboard loads in <2 seconds
- [ ] Works in 5+ different repo structures
- [ ] MCP tools visible in dashboard
- [ ] Multi-repo context switching works
- [ ] Dark/light theme functional
- [ ] Export working (PDF/CSV/JSON)
- [ ] Search/filter fast (<100ms)
- [ ] Zero hardcoded paths
- [ ] All CORE-008 through CORE-028 rules followed

### PHASE-DEPLOYMENT
- [ ] `cortex init` completes in <5 minutes
- [ ] Parent repo unchanged (except CORTEX/)
- [ ] MCP tools registered in user's client
- [ ] `cortex upgrade` works without breaking
- [ ] Context switching between repos works
- [ ] Performance: <1 second startup
- [ ] Security: no secrets in CORTEX/
- [ ] All 10 ACs passing tests
- [ ] Audit trail maintained through upgrades
- [ ] All CORE-008 through CORE-028 rules followed

---

## Common Tasks

### Switch Between Repos
```bash
cd ~/other-repo/CORTEX
cortex switch ../
cortex dashboard  # Now shows other-repo metrics
```

### Upgrade CORTEX
```bash
cd CORTEX
cortex upgrade
# → Pulls latest from main branch
# → Auto-merges non-breaking changes
# → Migrates state if needed
# → Verifies integrity
```

### View Dashboard
```bash
cd CORTEX
cortex dashboard
# → Opens http://localhost:8000/dashboard
# → Shows parent repo metrics
# → Shows MCP tool status
# → Shows audit trail
```

### List Available Tools
```bash
cortex tools list
# → Shows all MCP tools available in current context
# → Shows usage statistics
# → Shows recent invocations
```

---

## Key Files to Know

| File | Purpose |
|------|---------|
| `cortex` | CLI entry point (chmod +x) |
| `dashboard/index.html` | Universal dashboard (single file, embedded JS/CSS) |
| `cortex-brain/state/governance.db` | Audit trail for this CORTEX instance |
| `CORTEX.prompt.md` | MCP tool exposure definition |
| `cortex-builder.prompt.md` | Implementation guide |
| `.cortex-config.yaml` | Auto-detected repo configuration |
| `.env` | Runtime configuration (not in git) |

---

## Performance Targets

| Metric | Target |
|--------|--------|
| Dashboard load time | <2 seconds |
| Dashboard responsiveness | <100ms interactions |
| MCP tool invocation | <500ms average |
| Startup time | <1 second |
| Metrics update | <500ms |
| File operation | <100ms |
| Memory usage | <50MB baseline |

---

## Troubleshooting

### Dashboard Not Loading
```bash
# Check if backend is running
ps aux | grep cortex-brain/api

# Restart backend
cd CORTEX
python3 cortex-brain/api/main.py

# Check logs
tail -f CORTEX/logs/api.log
```

### MCP Tools Not Showing
```bash
# Re-register tools
cd CORTEX
python3 scripts/register_mcp.py

# Verify MCP client config
cat ~/.config/cortex/mcp-config.json
```

### Upgrade Failed
```bash
# Check git status
cd CORTEX
git status

# Resolve conflicts manually
git diff

# Try again
cortex upgrade
```

---

## Documentation References

| Document | Purpose |
|----------|---------|
| `PHASE-15-DASHBOARD-REDESIGN...` | Full phase specification (500 lines) |
| `CORTEX-UNIVERSAL-DEPLOYMENT-IMPLEMENTATION-GUIDE...` | Detailed implementation patterns |
| `cortex-builder.prompt.md` | Implementation patterns (Examples 1 & 2) |
| `cortex-master.yaml` | Phase definitions with AC-IDs |

---

## Contact & Support

For questions about:
- **Architecture**: See `PHASE-15-DASHBOARD-REDESIGN-...`
- **Implementation**: See `CORTEX-UNIVERSAL-DEPLOYMENT-IMPLEMENTATION-GUIDE-...`
- **Governance**: See `.github/prompts/cortex-builder.prompt.md`
- **Phases**: See `_workspaces/roadmap/cortex-master.yaml`

---

**Version**: 2.0 - Universal Multi-Repo Architecture  
**Status**: ✅ Ready for Implementation  
**First AC to Start**: AC-DASH-001-01 (Universal Dashboard Shell)  
**Timeline**: 8 weeks total (4 weeks dashboard + 4 weeks deployment)
