# CORTEX Known Limitations & Status

## Operations in Development

### Design Sync (design_sync)
- **Status:** ✅ PRODUCTION READY
- **Purpose:** Resolves design-implementation drift
- **Capabilities:**
  - Live implementation discovery (modules, tests, plugins, operations)
  - Design-implementation gap analysis
  - Optimization integration (runs optimize_cortex automatically)
  - MD-to-YAML conversion (structured schemas from verbose docs)
  - Status file consolidation (ONE source of truth)
  - Git tracking (all changes committed with audit trail)
- **Profiles:**
  - quick: Analysis only (no changes)
  - standard: Safe updates + consolidation
  - comprehensive: Full sync with YAML conversion
- **Why It Matters:** Sometimes design and implementation diverge during rapid development. This operation resynchronizes everything automatically.
- **Use When:** Design docs show incorrect counts, multiple status files exist, implementation reality differs from documentation

### Story Refresh (refresh_cortex_story)
- **Status:** ❌ ADMIN-ONLY (not included in user deployment)
- **Deployment Tier:** Admin operation - updates CORTEX's own story documentation
- **Deprecated:** Use `document_cortex` for documentation updates
- **Current Behavior:** Validates story structure and read time, copies to docs folder
- **Why Admin-Only:** This operation updates CORTEX's internal documentation, not user application docs
- **User Alternative:** Users can use `document_cortex` for their own documentation needs
- **SKULL-005:** Module explicitly marked as validation-only to prevent false success claims

### Vision API
- **Status:** 🟡 MOCK IMPLEMENTATION (optional feature)
- **Current Behavior:** Returns mock data for image analysis
- **Enable:** Set `vision_api.enabled = true` in config
- **Requires:** GitHub Copilot API access (not yet available)
- **Fallback Chain:** Copilot → OpenAI → local models → mock

## Two-Tier Status System

CORTEX distinguishes between **architecture completion** and **implementation completion**:

| Symbol | Architecture | Implementation | Meaning |
|--------|-------------|----------------|---------|
| ✅ READY | Complete | Complete | **Production-ready** with real logic |
| 🟢 NEARLY | Complete | 80%+ | **Almost ready** - minor gaps only |
| 🟡 VALIDATION | Complete | Validation-only | **Works but doesn't transform** |
| 🟡 PARTIAL | Complete | 40-60% | **Architecture solid, logic incomplete** |
| 🟠 IN PROGRESS | Partial | Partial | **Active development** |
| ⏸️ PENDING | Designed | Not started | **Architecture ready, awaiting implementation** |

**Example:** `refresh_cortex_story` is **🟡 VALIDATION** because:
- ✅ Architecture: 6/6 modules orchestrate correctly
- 🟡 Implementation: Validation-only (no transformation logic yet)

This honest reporting prevents status inflation and maintains user trust.
