# CORTEX Key Files Inventory

**Purpose:** Central registry of all files CORTEX references during planning, enhancement, and operations  
**Created:** December 1, 2025  
**Phase:** 2.2 - Architecture Synchronization  
**Status:** Active

---

## 📋 Overview

This document lists ALL files that CORTEX checks when:
- Planning features
- Validating architecture
- Generating documentation
- Executing deployments
- Performing system alignment

Each file is tagged with:
- **Update Frequency** - How often it should be refreshed
- **Last Updated** - Timestamp of last modification
- **Auto-Update** - Whether it's automatically synchronized
- **Owner** - Primary orchestrator/module responsible

---

## 🎯 Truth Sources (Tier 0 - Immutable References)

### Architecture & Design

| File | Purpose | Update Frequency | Auto-Update | Owner |
|------|---------|------------------|-------------|-------|
| `docs/ARCHITECTURE.md` | System architecture documentation | Deploy | ✅ Yes (architecture_sync.py) | deploy_cortex_simple.py |
| `cortex-brain/CORTEX-UNIFIED-ARCHITECTURE.yaml` | System design, component structure | Major design changes | ❌ Manual | System Architect |
| `cortex-brain/brain-protection-rules.yaml` | SKULL rules, protection layers | Feature addition | ❌ Manual | brain_protector.py |
| `cortex-brain/TRUTH-SOURCES.yaml` | Single source of truth registry | Quarterly | ❌ Manual | Documentation Team |

### Capabilities & Operations

| File | Purpose | Update Frequency | Auto-Update | Owner |
|------|---------|------------------|-------------|-------|
| `cortex-brain/capabilities.yaml` | Feature capabilities matrix | Feature completion | ❌ Manual | Feature Lead |
| `cortex-brain/operations-config.yaml` | Operation definitions, routing | New operation added | ❌ Manual | operations/ modules |
| `cortex-operations.yaml` | Module counts, implementation status | Module implementation | ❌ Manual | Module Lead |

### Configuration & Templates

| File | Purpose | Update Frequency | Auto-Update | Owner |
|------|---------|------------------|-------------|-------|
| `cortex-brain/response-templates.yaml` | AI response templates | Template changes | ❌ Manual | Template System |
| `cortex-brain/config/plan-schema.yaml` | Planning schema validation | Schema evolution | ❌ Manual | planning_orchestrator.py |
| `cortex.config.json` | Machine-specific paths | Setup/migration | ❌ Manual | setup_orchestrator.py |

---

## 📊 Status & Tracking (Tier 1 - Frequently Updated)

### Implementation Status

| File | Purpose | Update Frequency | Auto-Update | Owner |
|------|---------|------------------|-------------|-------|
| `cortex-brain/cortex-2.0-design/status-data.yaml` | Phase completion, task progress | Task completion | ✅ Yes (status script) | generate_status_docs.py |
| `cortex-brain/cortex-2.0-design/STATUS.md` | Detailed prose status | Task completion | ✅ Yes (derived) | generate_status_docs.py |
| `cortex-brain/cortex-2.0-design/CORTEX2-STATUS.MD` | Visual progress bars | Task completion | ✅ Yes (derived) | generate_status_docs.py |
| `VERSION` | Current version + health metrics | Deploy | ✅ Yes (deploy script) | deploy_cortex_simple.py |

### Planning & Documentation

| File | Purpose | Update Frequency | Auto-Update | Owner |
|------|---------|------------------|-------------|-------|
| `cortex-brain/documents/planning/features/*.yaml` | Feature plans | Planning session | ❌ Manual | planning_orchestrator.py |
| `cortex-brain/documents/planning/features/phases/*.yaml` | Phase breakdowns | Phase planning | ❌ Manual | planning_orchestrator.py |
| `CHANGELOG.md` | Breaking changes, version history | Deploy/breaking change | ❌ Manual | Developer |
| `README.md` | Project overview, quick start | Major feature addition | ❌ Manual | Documentation Team |

---

## 🧠 Brain State (Tier 2 - Runtime Updated)

### Memory Systems

| File | Purpose | Update Frequency | Auto-Update | Owner |
|------|---------|------------------|-------------|-------|
| `cortex-brain/tier1-working-memory.db` | Recent conversations (70-conv FIFO) | Real-time | ✅ Yes (runtime) | tier1/working_memory.py |
| `cortex-brain/tier2-knowledge-graph.db` | Patterns, validation insights | Post-session | ✅ Yes (runtime) | tier2/knowledge_graph.py |
| `cortex-brain/tier3-development-context.db` | Code metrics, hotspots | Post-session | ✅ Yes (runtime) | tier3/development_context.py |
| `cortex-brain/conversation-context.jsonl` | Full conversation history | Real-time | ✅ Yes (runtime) | tier1/conversation_memory.py |

### Cleanup & Maintenance

| File | Purpose | Update Frequency | Auto-Update | Owner |
|------|---------|------------------|-------------|-------|
| `cortex-brain/cleanup-rules.yaml` | Workspace cleanup patterns | Quarterly | ❌ Manual | cleanup orchestrator |
| `cortex-brain/obsolete-tests-manifest.json` | Deprecated test tracking | Test cleanup | ❌ Manual | test validator |
| `cortex-brain/refactoring-rules.yaml` | Code refactoring patterns | Best practice update | ❌ Manual | refactoring agent |

---

## 🔧 Development & Testing (Tier 3 - Developer Managed)

### Test Infrastructure

| File | Purpose | Update Frequency | Auto-Update | Owner |
|------|---------|------------------|-------------|-------|
| `pytest.ini` | Test discovery configuration | Test framework change | ❌ Manual | Test Lead |
| `requirements.txt` | Python dependencies | Dependency addition | ❌ Manual | Developer |
| `optional-requirements.txt` | Optional dependencies | Optional feature | ❌ Manual | Developer |

### Documentation Generation

| File | Purpose | Update Frequency | Auto-Update | Owner |
|------|---------|------------------|-------------|-------|
| `cortex-brain/doc-generation-rules.yaml` | Doc sync rules | Doc workflow change | ❌ Manual | documentation generator |
| `mkdocs.yml` | MkDocs configuration | Doc structure change | ❌ Manual | Documentation Team |
| `.github/prompts/CORTEX.prompt.md` | Universal entry point | Feature addition | ❌ Manual | Template System |

---

## ⚙️ Operational Files (Checked During Workflows)

### Planning Workflow

**Files Checked:**
1. `cortex-brain/config/plan-schema.yaml` - Validates plan structure
2. `cortex-brain/capabilities.yaml` - Checks feasibility
3. `cortex-brain/brain-protection-rules.yaml` - Applies DoR/DoD gates
4. `docs/ARCHITECTURE.md` - Validates architectural fit
5. `TRUTH-SOURCES.yaml` - Ensures single source of truth

**Automated Check:** ✅ Planning orchestrator validates before plan creation

---

### Deployment Workflow

**Files Checked:**
1. `VERSION` - Version bump validation
2. `CHANGELOG.md` - Breaking changes documented
3. `docs/ARCHITECTURE.md` - Architecture synchronized
4. `cortex-brain/capabilities.yaml` - Capabilities current
5. `README.md` - Quick start current

**Automated Check:** ✅ Deploy script runs architecture sync before deployment

---

### System Alignment Workflow

**Files Checked:**
1. `cortex-brain/CORTEX-UNIFIED-ARCHITECTURE.yaml` - Architecture definition
2. `cortex-brain/operations-config.yaml` - Operation alignment
3. `cortex-brain/brain-protection-rules.yaml` - Protection rules current
4. `cortex-brain/TRUTH-SOURCES.yaml` - Truth source registry
5. `cortex-operations.yaml` - Module counts match src/

**Automated Check:** ✅ Alignment orchestrator validates daily (if enabled)

---

## 🔍 Automated Freshness Checks

### 30-Day Staleness Monitor

**Critical Files (Must Update Within 30 Days):**
- `docs/ARCHITECTURE.md` - Architecture documentation
- `cortex-brain/capabilities.yaml` - Capabilities matrix
- `CHANGELOG.md` - Version history
- `VERSION` - Version + health metrics

**Check Command:**
```bash
python scripts/check_file_freshness.py --days 30
```

**Automated Trigger:** Deploy script fails if critical files >30 days stale

---

### Weekly Sync Checks

**Files Validated Weekly:**
- Status trinity (status-data.yaml, STATUS.md, CORTEX2-STATUS.MD)
- Test inventory (pytest collection vs docs claims)
- Module counts (cortex-operations.yaml vs src/)

**Check Command:**
```bash
python scripts/validate_truth_sources.py
```

**Automated Trigger:** Pre-commit hook for status files

---

## 📅 Update Schedule Recommendations

### Deploy-Triggered (Every Release)
✅ `docs/ARCHITECTURE.md` - Auto-updated by deploy script  
✅ `VERSION` - Auto-updated by deploy script  
⚠️ `CHANGELOG.md` - Manual (developer responsibility)  
⚠️ `README.md` - Manual if quick start changes

### Monthly Reviews
- `cortex-brain/capabilities.yaml` - Feature additions
- `cortex-brain/operations-config.yaml` - New operations
- `cortex-brain/brain-protection-rules.yaml` - Protection enhancements
- `cortex-brain/response-templates.yaml` - Template improvements

### Quarterly Reviews
- `cortex-brain/CORTEX-UNIFIED-ARCHITECTURE.yaml` - Major design changes
- `cortex-brain/TRUTH-SOURCES.yaml` - Truth source validation
- `cortex-brain/cleanup-rules.yaml` - Cleanup pattern review
- `cortex-brain/refactoring-rules.yaml` - Best practice updates

### Real-Time (Automated)
✅ `cortex-brain/tier1-working-memory.db` - Conversation tracking  
✅ `cortex-brain/tier2-knowledge-graph.db` - Pattern learning  
✅ `cortex-brain/tier3-development-context.db` - Code metrics  
✅ `cortex-brain/conversation-context.jsonl` - Full history

---

## 🚨 Drift Prevention

### Pre-Commit Hooks
1. **Status Trinity Check** - Ensures status files updated together
2. **Truth Source Validation** - Prevents duplicate authoritative sources
3. **Test Inventory Sync** - Validates test counts match docs
4. **File Freshness** - Warns if critical files >30 days stale

### CI/CD Checks
1. **Architecture Sync** - Fails if ARCHITECTURE.md not synchronized during deploy
2. **Module Count Validation** - Fails if operations-config.yaml module count doesn't match src/
3. **Capabilities Validation** - Fails if capabilities.yaml claims features with <95% test pass rate

---

## 📊 Current Status Summary

**Last Full Inventory:** December 1, 2025  
**Total Files Tracked:** 40  
**Auto-Updated:** 10 (25%)  
**Manual Update Required:** 30 (75%)  
**Files >30 Days Stale:** TBD (run freshness check)

**Next Review:** January 1, 2026 (Monthly)  
**Automated Freshness Check:** ✅ Enabled (deploy-triggered)

---

**Maintained By:** Architecture Synchronization System (Phase 2.2)  
**Last Updated:** December 1, 2025  
**Owner:** Mac Implementation Track
