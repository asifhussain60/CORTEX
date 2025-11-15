# Archived Scripts

This directory contains scripts that have been integrated into CORTEX orchestrators and are no longer needed as standalone files.

## Migration History

### check_brain_health.py → optimize_cortex_orchestrator.py
- **Date:** 2025-11-15
- **Reason:** Integrated into optimize orchestrator as Phase 6 (Brain Health Diagnostics)
- **Pattern Applied:** `architecture_level_integration` from knowledge graph
- **New Usage:** Run `optimize cortex` command instead of standalone script
- **Benefits:**
  - Unified health reporting (all diagnostics in one place)
  - No separate script maintenance
  - Consistent with CORTEX architecture principles
- **Archived File:** `check_brain_health.py.archived`

### check_conversations.py
- **Date:** 2025-11-15
- **Reason:** Functionality fully covered by Tier 1 diagnostics in optimize orchestrator Phase 6
- **Pattern Applied:** `architecture_level_integration` from knowledge graph
- **New Usage:** Run `optimize cortex` command to see conversation database stats
- **Benefits:** Same as check_brain_health.py migration
- **Archived File:** `check_conversations.py.archived`

### fix_response_headers.py
- **Status:** One-time migration script - removed completely
- **Note:** No longer needed after response header format standardization complete

## Using Archived Scripts

If you need to reference the original implementation:
1. Files are preserved with `.archived` extension
2. Do NOT execute these files - use the integrated orchestrator instead
3. Review the code for historical context only

## Preventing Future Standalone Scripts

**CORTEX Architecture Principle:** Integrate diagnostic features into orchestrators, not standalone scripts.

**Why?**
- ✅ Single point of execution (`optimize cortex`, `cleanup workspace`, etc.)
- ✅ Unified reporting and health tracking
- ✅ Easier maintenance (one codebase, not scattered scripts)
- ✅ Better user experience (consistent commands)

**When creating new diagnostics:**
1. Add as a phase in appropriate orchestrator (optimize, validate, cleanup, etc.)
2. Update orchestrator metadata and natural language triggers
3. Test with existing orchestrator infrastructure
4. Document in orchestrator's docstring
