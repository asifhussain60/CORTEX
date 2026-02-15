# DEFERRED: Documentation & Site Infrastructure

**Status:** DEFERRED (Low Priority)  
**Date Archived:** 2026-02-15  
**Reason:** Focus on core production readiness (Phases 21-25) first

---

## ARCHIVED PLANS

### 1. Documentation Portal (doc-portal-001)
**Original Location:** `cortex-registry/planning/documentation/doc-portal-001/`  
**Purpose:** Interactive documentation portal for CORTEX (GitHub Pages hosted)  
**Status:** Planned but not started  
**Archived To:** `_cortex-master/archive/deferred/documentation-sites/doc-portal-001/`

**Scope:**
- Interactive documentation site
- 4 persona views (developer, architect, operator, user)
- GitHub Pages deployment
- MkDocs-based generation

**Why Deferred:**
- P2 priority (not blocking production readiness)
- Core functionality (Phases 21-25) takes precedence
- Documentation can be generated after core is stable

---

### 2. Multi-Site Infrastructure (site-infrastructure-001)
**Original Location:** `cortex-registry/master/site-infrastructure-001.yaml`  
**Purpose:** Infrastructure for hosting multiple documentation versions  
**Status:** Planned but not started  
**Archived To:** `_cortex-master/archive/deferred/documentation-sites/site-infrastructure-001.yaml`

**Scope:**
- Multi-version documentation hosting
- Archive management (v4.0, v5.0, v5.5+)
- Port management (8000-8003)
- MasterOrchestrator integration

**Why Deferred:**
- Infrastructure overkill for current needs
- No active documentation versions to host
- Can be revisited post-Phase 25

---

## RESTORATION PLAN (If Needed Later)

**When to Restore:**
- After Phase 25 complete (stabilization done)
- After Phase 21 complete (intelligence core stable)
- When external developer documentation becomes priority

**How to Restore:**
```bash
# Move back to active planning
git mv cortex-registry/_cortex-master/archive/deferred/documentation-sites/doc-portal-001 \
       cortex-registry/planning/documentation/

git mv cortex-registry/_cortex-master/archive/deferred/documentation-sites/site-infrastructure-001.yaml \
       cortex-registry/master/
```

**Estimated Effort:** 2-3 weeks (after core complete)  
**ROI:** Medium (helpful for external developers, not critical for production)

---

## ALTERNATIVE APPROACH (Recommended)

**Instead of full documentation portal:**

1. **Simple README.md updates** in key folders
2. **Inline docstrings** in code (already enforced by CORE-012)
3. **MCP tool catalog** (auto-generated from decorators)
4. **Phase YAMLs** as living documentation

**Why Better:**
- ✅ Zero maintenance overhead
- ✅ Always in sync with code
- ✅ No separate site to maintain
- ✅ CORE-002 compliant (no markdown sprawl)

---

**Decision:** Documentation sites deferred until post-production readiness (Phase 25+)
