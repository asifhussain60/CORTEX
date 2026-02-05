# Shell Scripts Deprecation Plan

**Purpose:** Document migration path from shell scripts to Python/MCP tools  
**Status:** IN PROGRESS  
**Updated:** 2026-02-05

---

## 📋 Shell Scripts Inventory

| Script | Purpose | Lines | Status | Migration Path |
|--------|---------|-------|--------|----------------|
| consolidate-duplicates.sh | Duplicate file cleanup | ~50 | 🔴 DEPRECATED | VacuumOrchestrator (MCP) |
| execute-core-038-cleanup.sh | CORE-038 file placement enforcement | ~30 | 🔴 DEPRECATED | Manual (one-time operation) |
| phase-2-execute.sh | Phase 2 legacy removal | ~40 | ✅ ARCHIVED | One-time migration complete |
| phase-3-execute.sh | Phase 3 dependency resolution | ~35 | ✅ ARCHIVED | One-time migration complete |
| phase-4-execute.sh | Phase 4 Docker setup | ~45 | ✅ ARCHIVED | One-time migration complete |
| phase-6-cleanup.sh | Phase 6 validation | ~25 | ✅ ARCHIVED | One-time migration complete |
| refactor-file-names.sh | File naming migration | ~60 | 🔴 DEPRECATED | FileNamingEnforcementAgent |
| vacuum-audit-fix.sh | Markdown cleanup + audit | ~55 | 🔴 DEPRECATED | VacuumOrchestrator (MCP) |
| migrate-to-docker.sh | Docker migration helper | ~70 | ⚠️ REFERENCE | Docker guide (docs) |

**Total:** 9 scripts, ~410 lines of shell code

---

## 🎯 Migration Strategy

### Priority 1: Already Migrated (Archive Now)
**Scripts:** phase-{2,3,4,6}-execute.sh  
**Reason:** One-time phase executions, complete  
**Action:** Move to .archive/shell-scripts/

### Priority 2: Superseded by MCP Tools (Archive + Deprecate)
**Scripts:** consolidate-duplicates.sh, vacuum-audit-fix.sh  
**Replacement:** VacuumOrchestrator + `/vacuum` command (MCP)  
**Action:** 
1. Verify VacuumOrchestrator covers all use cases
2. Add deprecation notice to script headers
3. Move to .archive/shell-scripts/

### Priority 3: Superseded by Governance (Archive + Deprecate)
**Scripts:** execute-core-038-cleanup.sh, refactor-file-names.sh  
**Replacement:** FileNamingEnforcementAgent (pre-execution gate)  
**Action:**
1. Verify EnforcementOrchestrator prevents violations
2. Move to .archive/shell-scripts/

### Priority 4: Convert to Documentation (Reference)
**Scripts:** migrate-to-docker.sh  
**Reason:** Useful reference for Docker migration steps  
**Action:**
1. Extract steps to docs/14-deployment/docker-migration.md
2. Mark script as REFERENCE ONLY
3. Move to .archive/shell-scripts/ with README pointer

---

## 🔄 Migration Timeline

### Week 1 (2026-02-05)
- [x] Create deprecation plan
- [x] Archive phase-{2,3,4,6}-execute.sh (one-time complete)
- [ ] Verify VacuumOrchestrator functionality
- [ ] Archive vacuum-audit-fix.sh

### Week 2 (2026-02-12)
- [ ] Verify FileNamingEnforcementAgent coverage
- [ ] Archive execute-core-038-cleanup.sh
- [ ] Archive refactor-file-names.sh

### Week 3 (2026-02-19)
- [ ] Extract Docker migration docs from migrate-to-docker.sh
- [ ] Archive migrate-to-docker.sh with reference pointer
- [ ] Archive consolidate-duplicates.sh

---

## 📊 Migration Benefits

### Before (Shell Scripts)
- ❌ No test coverage
- ❌ Manual execution required
- ❌ Brittle (env-specific)
- ❌ No MCP integration
- ❌ Limited error handling

### After (Python/MCP)
- ✅ TDD with 85%+ coverage
- ✅ MCP tool invocation (automated)
- ✅ Cross-platform (Python)
- ✅ Production-ready (observability)
- ✅ Graceful error handling

**Estimated Effort Reduction:** 60% (manual → automated)

---

## 🧪 Testing Shell Script Equivalence

Before archiving any script, verify Python/MCP replacement:

```bash
# Example: Verify VacuumOrchestrator matches vacuum-audit-fix.sh behavior

# 1. Run shell script (dry-run)
./vacuum-audit-fix.sh --dry-run > shell-output.txt

# 2. Run MCP tool (dry-run)
cortex_vacuum --dry-run > mcp-output.txt

# 3. Compare outputs
diff shell-output.txt mcp-output.txt

# 4. Verify no regressions
```

---

## 📝 Deprecation Notice Template

Add to top of deprecated scripts:

```bash
#!/bin/bash
# ⚠️ DEPRECATED: This script has been superseded by [Replacement]
# Migration: [Date]
# Replacement: [Tool/Command]
# Reason: [Brief explanation]
# Reference: [Link to docs/MCP tool]
#
# This file is kept for historical reference only.
# DO NOT USE in production workflows.
```

---

## 🔗 Related Documents

- [VacuumOrchestrator](../../cortex/orchestrators/support/vacuum_orchestrator.py)
- [FileNamingEnforcementAgent](../../cortex/orchestrators/core/enforcement_orchestrator.py)
- [MCP Tools Catalog](../../docs/11-mcp-tools/)
- [CORE-038 File Placement](../../.github/copilot-instructions.md)

---

**Status Summary:** 4/9 scripts archived (44%), 5/9 pending migration (56%)

**Next Review:** 2026-02-12 (verify VacuumOrchestrator parity)
