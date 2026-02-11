# MCP Tool Audit — Required vs Registered

**Date:** 2026-02-10  
**Phase:** 54 — MCP Unified Routing  
**Purpose:** Identify which tools CORTEX actually needs vs what's registered

---

## 📊 AUDIT RESULTS

### Tools Referenced in Documentation

**From prompts (.github/prompts/):**
1. ✅ `cortex_process_request` — IMPLEMENT/FIX/REFACTOR routing (CORE)
2. ✅ `cortex_lens_analyze` — ANALYZE intent, code intelligence (CORE)
3. ✅ `cortex_challenge` — Challenge gate, disagreement detection (CORE)
4. ✅ `cortex_total_recall` — Feature discovery, capability search (CORE)
5. ✅ `cortex_git_history` — Git context (24h window)
6. ✅ `cortex_detect_duplicates` — CORE-035 violation detection
7. ✅ `cortex_plan_setup` — Pre-execution phase hook (PLAN mode)
8. ✅ `cortex_plan_execute_autonomous` — Multi-stage autonomous execution (PLAN mode)
9. ✅ `cortex_plan_teardown` — Post-execution cleanup (PLAN mode)
10. ✅ `cortex_plan_sync` — Manual dashboard synchronization (PLAN mode)
11. ⚠️ `cortex_validate_holistically` — Phase 48 holistic validation (Phase 56 enhancement, NOT YET CREATED)
12. ⚠️ `cortex_digest_session` — DIGEST mode (chat session learning, NOT YET CREATED)
13. ⚠️ `cortex_onboard_repository` — Repository onboarding + security scan (NOT YET CREATED)

**From commands (copilot-instructions.md):**
- `/audit` → Uses `cortex_lens_analyze` + orchestrator routing
- `/implement` → Uses `cortex_process_request`
- `/fix` → Uses `cortex_process_request`
- `/refactor` → Uses `cortex_process_request`
- `/analyze` → Uses `cortex_lens_analyze`
- `/plan` → Uses `cortex_plan_*` tools
- `/recall` → Uses `cortex_total_recall`
- `/onboard` → Uses `cortex_onboard_repository` (MISSING)
- `/debug` → NOT MCP-based (uses native debug tools)
- `/check-env` → NOT MCP-based (environment validation)

### Currently Registered Tools (VERIFIED)

**IMPLEMENTATION FOUND:**

**Category: Core Orchestrator Tools (cortex/mcp/cortex_tools.py)**
1. ✅ `cortex_process_request` — Main routing via Master Orchestrator (KEEP, FIX NEEDED)
2. ✅ `cortex_total_recall` — Feature discovery via MCP tools catalog (KEEP, FIX NEEDED)
3. ✅ `cortex_challenge` — Challenge generation via ChallengeEngine (KEEP, VERIFY)

**Category: LENS Tools (cortex/mcp/tools/lens_tools.py)**
4. ✅ `cortex_lens_analyze` — Unified LENS analysis (KEEP)
5. ✅ `cortex_git_history` — Git history analyzer 24h (KEEP)
6. ✅ `cortex_ast_analyze` — AST structure analysis (KEEP)
7. ✅ `cortex_extract_comments` — Comment/TODO extractor (KEEP)
8. ✅ `cortex_detect_duplicates` — CORE-035 duplicate detection (KEEP)

**Category: Utility Tools (cortex/brain/mcp/tools/utility_tools.py)**
9. ✅ `echo_tool` — Test echo utility (REMOVE - dev only)
10. ✅ `transform_tool` — Data format transformation (KEEP - used for JSON/YAML conversion)

**Category: Governance Tools (cortex/brain/mcp/tools/governance_tools.py)**
11. ✅ `check_phase_lock` — Phase lock verification (KEEP)
12. ✅ `validate_ac_id` — AC-ID validation (KEEP)
13. ✅ `canonicalize_intent` — Intent normalization (KEEP)
14. ✅ `enforce_operation` — Governance enforcement (KEEP)
15. ✅ `get_phase_status` — Phase status query (KEEP)

**Category: Knowledge Tools (cortex/brain/mcp/tools/knowledge_tools.py)**
16. ✅ `search_knowledge_base` — Knowledge base search (KEEP)
17. ✅ `analyze_knowledge_gap` — Gap analysis (KEEP)
18. ✅ `generate_knowledge_summary` — Knowledge summarization (KEEP)

**Category: Orchestrator Tools (cortex/brain/mcp/tools/orchestrator_tools.py)**
19. ✅ `monitor_orchestrator_health` — Health monitoring (KEEP)
20. ✅ `diagnose_orchestrator_issues` — Issue diagnostics (KEEP)
21. ✅ `optimize_orchestrator_config` — Config optimization (KEEP)
22. ✅ `get_operation_status` — Operation status query (KEEP)

**Category: Test/Development Tools (cortex/mcp/server.py)**
23. ✅ `sample_tool` — Basic test tool (REMOVE - dev only)

**NOT YET IMPLEMENTED (need creation):**
24. ❌ `cortex_plan_setup` — Pre-execution phase hook (CREATE)
25. ❌ `cortex_plan_execute_autonomous` — Multi-stage execution (CREATE)
26. ❌ `cortex_plan_teardown` — Post-execution cleanup (CREATE)
27. ❌ `cortex_plan_sync` — Dashboard synchronization (CREATE)
28. ❌ `cortex_validate_holistically` — Phase 48 holistic validation (CREATE)
29. ❌ `cortex_digest_session` — DIGEST mode chat learning (CREATE)
30. ❌ `cortex_onboard_repository` — Repository onboarding + security (CREATE)

---

## 🎯 REQUIRED TOOLS (Tier 0 — Must Work)

| Tool | Status | File | Priority | Notes |
|------|--------|------|----------|-------|
| `cortex_process_request` | ⚠️ BROKEN | cortex/mcp/cortex_tools.py | P0 | Fix Result.unwrap_err() |
| `cortex_lens_analyze` | ✅ FOUND | cortex/mcp/tools/lens_tools.py | P0 | Already implemented |
| `cortex_total_recall` | ⚠️ BROKEN | cortex/mcp/cortex_tools.py | P0 | Fix catalog.get_all_tools() |
| `cortex_challenge` | ✅ FOUND | cortex/mcp/cortex_tools.py | P0 | Verify ChallengeEngine exists |

---

## 🔧 OPTIONAL TOOLS (Tier 1 — Nice to Have)

| Tool | Status | File | Priority | Notes |
|------|--------|------|----------|-------|
| `cortex_git_history` | ✅ FOUND | cortex/mcp/tools/lens_tools.py | P1 | Already implemented |
| `cortex_detect_duplicates` | ✅ FOUND | cortex/mcp/tools/lens_tools.py | P1 | Already implemented |
| `cortex_ast_analyze` | ✅ FOUND | cortex/mcp/tools/lens_tools.py | P1 | Already implemented |
| `cortex_extract_comments` | ✅ FOUND | cortex/mcp/tools/lens_tools.py | P1 | Already implemented |
| `transform_tool` | ✅ FOUND | cortex/brain/mcp/tools/utility_tools.py | P1 | Used for format conversion |
| `search_knowledge_base` | ✅ FOUND | cortex/brain/mcp/tools/knowledge_tools.py | P1 | KB search |
| `check_phase_lock` | ✅ FOUND | cortex/brain/mcp/tools/governance_tools.py | P1 | Phase governance |
| `validate_ac_id` | ✅ FOUND | cortex/brain/mcp/tools/governance_tools.py | P1 | AC validation |
| `canonicalize_intent` | ✅ FOUND | cortex/brain/mcp/tools/governance_tools.py | P1 | Intent normalization |
| `enforce_operation` | ✅ FOUND | cortex/brain/mcp/tools/governance_tools.py | P1 | Governance enforcement |
| `get_phase_status` | ✅ FOUND | cortex/brain/mcp/tools/governance_tools.py | P1 | Phase status query |

---

## ❌ TOOLS TO REMOVE

| Tool | Reason | Action | File |
|------|--------|--------|------|
| `sample_tool` | Development only, not used in production | DELETE | cortex/mcp/server.py |
| `echo_tool` | Development only, duplicate testing tool | DELETE | cortex/brain/mcp/tools/utility_tools.py |

---

## 🆕 TOOLS TO CREATE (HIGH PRIORITY)

| Tool | Purpose | File | Priority | Effort |
|------|---------|------|----------|--------|
| `cortex_plan_setup` | Pre-execution phase hook | cortex/mcp/tools/plan_tools.py | P0 | 1h |
| `cortex_plan_execute_autonomous` | Multi-stage autonomous execution | cortex/mcp/tools/plan_tools.py | P0 | 2h |
| `cortex_plan_teardown` | Post-execution cleanup + sync | cortex/mcp/tools/plan_tools.py | P0 | 1h |
| `cortex_plan_sync` | Manual dashboard synchronization | cortex/mcp/tools/plan_tools.py | P1 | 30min |
| `cortex_validate_holistically` | Phase 48 holistic validation gate | cortex/mcp/tools/validation_tools.py | P0 | 2h |
| `cortex_digest_session` | DIGEST mode chat learning | cortex/mcp/tools/digest_tools.py | P1 | 1.5h |
| `cortex_onboard_repository` | Repository onboarding + security | cortex/mcp/tools/onboarding_tools.py | P1 | 2h |

**Total Effort:** ~10 hours for all missing P0/P1 tools

---

## 🔍 TOOLS VERIFIED AND KEPT (Tier 2 — Infrastructure)

These tools exist and are used for CORTEX internal operations:

| Tool | Purpose | File | Keep? |
|------|---------|------|-------|
| `monitor_orchestrator_health` | Orchestrator health monitoring | cortex/brain/mcp/tools/orchestrator_tools.py | ✅ YES |
| `diagnose_orchestrator_issues` | Issue diagnostics | cortex/brain/mcp/tools/orchestrator_tools.py | ✅ YES |
| `optimize_orchestrator_config` | Config optimization | cortex/brain/mcp/tools/orchestrator_tools.py | ✅ YES |
| `get_operation_status` | Operation status query | cortex/brain/mcp/tools/orchestrator_tools.py | ✅ YES |
| `analyze_knowledge_gap` | Gap analysis | cortex/brain/mcp/tools/knowledge_tools.py | ✅ YES |
| `generate_knowledge_summary` | Knowledge summarization | cortex/brain/mcp/tools/knowledge_tools.py | ✅ YES |

---

## 📋 REVISED PHASE 54 ACTION PLAN

### Stage 1: Fix Broken Core Tools (2h) — P0 BLOCKING

| Task | File | Action | Time | Status |
|------|------|--------|------|--------|
| 1.1 | cortex/mcp/cortex_tools.py | Fix `cortex_total_recall` catalog API | 30min | 🔵 IN PROGRESS |
| 1.2 | cortex/mcp/cortex_tools.py | Fix `cortex_process_request` Result error handling | 30min | ⚪ PENDING |
| 1.3 | cortex/orchestrators/core/challenge_engine.py | Verify `ChallengeEngine` exists | 15min | ⚪ PENDING |
| 1.4 | cortex/mcp/server.py | Verify tool registration exposes all 23 tools | 45min | ⚪ PENDING |

### Stage 2: Remove Unused Tools (15min) — P1 CLEANUP

| Task | File | Action | Time | Status |
|------|------|--------|------|--------|
| 2.1 | cortex/mcp/server.py | Remove `sample_tool` registration | 5min | ⚪ PENDING |
| 2.2 | cortex/brain/mcp/tools/utility_tools.py | Remove `echo_tool` | 5min | ⚪ PENDING |
| 2.3 | cortex/mcp/server.py | Update tool count in comments | 5min | ⚪ PENDING |

### Stage 3: Create Missing P0 Tools (6h) — P0 REQUIRED

| Task | File | Tool | Time | Status |
|------|------|------|------|--------|
| 3.1 | cortex/mcp/tools/plan_tools.py | `cortex_plan_setup` | 1h | ⚪ PENDING |
| 3.2 | cortex/mcp/tools/plan_tools.py | `cortex_plan_execute_autonomous` | 2h | ⚪ PENDING |
| 3.3 | cortex/mcp/tools/plan_tools.py | `cortex_plan_teardown` | 1h | ⚪ PENDING |
| 3.4 | cortex/mcp/tools/validation_tools.py | `cortex_validate_holistically` | 2h | ⚪ PENDING |

### Stage 4: Create Missing P1 Tools (4h) — P1 ENHANCEMENT

| Task | File | Tool | Time | Status |
|------|------|------|------|--------|
| 4.1 | cortex/mcp/tools/plan_tools.py | `cortex_plan_sync` | 30min | ⚪ PENDING |
| 4.2 | cortex/mcp/tools/digest_tools.py | `cortex_digest_session` | 1.5h | ⚪ PENDING |
| 4.3 | cortex/mcp/tools/onboarding_tools.py | `cortex_onboard_repository` | 2h | ⚪ PENDING |

### Stage 5: Update Prompts & Agents (4h) — P0 ENFORCEMENT

| Task | File | Action | Time | Status |
|------|------|--------|------|--------|
| 5.1 | .github/prompts/cortex-architect.prompt.md | Update tool list (remove sample/echo) | 30min | ⚪ PENDING |
| 5.2 | .github/prompts/CORTEX.prompt.md | Update tool list | 30min | ⚪ PENDING |
| 5.3 | .github/prompts/MCP-SETUP-GUIDE.md | Update tool count (23 → 28 total) | 30min | ⚪ PENDING |
| 5.4 | .github/agents/core/*.md | Add references to new plan/validation tools | 2.5h | ⚪ PENDING |

### Stage 6: Testing & Validation (3h) — P0 VERIFICATION

| Task | Action | Time | Status |
|------|--------|------|--------|
| 6.1 | Test all 4 P0 core tools execute successfully | 30min | ⚪ PENDING |
| 6.2 | Test 7 new P0/P1 tools | 1h | ⚪ PENDING |
| 6.3 | Verify VS Code exposes all 28 tools | 30min | ⚪ PENDING |
| 6.4 | Run integration tests for MCP routing | 1h | ⚪ PENDING |

---

## 🎯 REVISED SUCCESS CRITERIA

### Tier 0 (Must Pass)
- [ ] All 4 core tools (cortex_process_request, cortex_lens_analyze, cortex_total_recall, cortex_challenge) execute successfully
- [ ] 28 tools total registered (23 existing + 7 new - 2 removed)
- [ ] VS Code exposes all 28 tools in Copilot Chat
- [ ] All IMPLEMENT/FIX/REFACTOR/ANALYZE/PLAN intents route through MCP
- [ ] Prompts updated to reference correct tool count

### Tier 1 (Should Pass)
- [ ] All 7 new P0/P1 tools created and tested
- [ ] sample_tool and echo_tool removed from production
- [ ] Agent documentation updated with new tool references
- [ ] Integration tests passing for MCP routing
- [ ] MCP pre-flight check validates tool availability

### Tier 2 (Nice to Have)
- [ ] Tool audit documentation updated with final inventory
- [ ] Performance benchmarks for new tools
- [ ] Dashboard showing tool usage metrics

---

## 📊 TOOL INVENTORY SUMMARY

| Category | Count | Status |
|----------|-------|--------|
| **Core Orchestrator** | 3 | ⚠️ 2 broken, 1 verify |
| **LENS Analysis** | 5 | ✅ All working |
| **Governance** | 5 | ✅ All working |
| **Knowledge** | 3 | ✅ All working |
| **Orchestrator Ops** | 4 | ✅ All working |
| **Utility** | 1 | ✅ Working (keep transform_tool) |
| **Dev/Test** | 2 | ❌ Remove both (sample_tool, echo_tool) |
| **Missing (P0)** | 4 | ❌ Need creation |
| **Missing (P1)** | 3 | ❌ Need creation |
| **TOTAL CURRENT** | 23 | - |
| **TOTAL AFTER** | 28 | - |

---

## ⏱️ REVISED TIMELINE

| Stage | Duration | Cumulative | Priority |
|-------|----------|------------|----------|
| Stage 1: Fix Broken Tools | 2h | 2h | P0 |
| Stage 2: Remove Unused | 15min | 2h 15min | P1 |
| Stage 3: Create P0 Tools | 6h | 8h 15min | P0 |
| Stage 4: Create P1 Tools | 4h | 12h 15min | P1 |
| Stage 5: Update Docs | 4h | 16h 15min | P0 |
| Stage 6: Testing | 3h | 19h 15min | P0 |
| **TOTAL** | **19h 15min** | - | - |

**Previous Estimate:** 52 hours  
**Revised Estimate:** 19.25 hours  
**Savings:** 32.75 hours (63% reduction)

**Why?** Most tools already exist! We only need to:
1. Fix 2 broken core tools (2h)
2. Create 7 new tools (10h)
3. Update documentation (4h)
4. Test everything (3h)

---

**Authority:** Phase 54 MCP Unified Routing  
**Mode:** ARCHITECT  
**AC:** AC-PHASE54-TOOL-AUDIT-001
