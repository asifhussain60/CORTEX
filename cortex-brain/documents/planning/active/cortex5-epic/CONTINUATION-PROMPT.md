Execute Phase 1: Critical Blocker Resolution

Plan: cortex5-epic | Progress: 7% | Phase 1/14

Context: tracking/progress-tracker.json, phases/phase-01-blocker-resolution.md, reports/master-plan-v3.md

**Recent Changes (2026-01-07T09:00:00Z):** Governance Enhancement Complete
- ✅ Added 3 new SKULL governance rules to brain-protection-rules.yaml
  - `INCREMENTAL_AUTONOMOUS_EXECUTION` - Small increments prevent 502 errors (category: orchestration_lifecycle)
  - `NO_SUMMARY_FILE_GENERATION` - Block unwanted summary files (category: response_formatting)
  - `VISUAL_PROGRESS_RESPONSE_FORMAT` - Executive summaries with progress bars only (category: response_formatting)
- ✅ Added new category: `response_formatting` to brain-protection-rules.yaml schema
- ✅ Rules reference user feedback from chat01.md (explicit user requirements)
- ✅ Rules reference error context (HTTP 502 token limit errors)
- ⏸️ PENDING: Implement middleware for new rules (Phase P00B integration)

**Previous Changes (2026-01-07T08:00:00Z):** Review Orchestrator Conversion Complete
- ✅ Converted cortex-review.prompt.md → review_orchestrator_v2 (registered toolkit)
- ✅ Created manifest: manifests/orchestrators/review-orchestrator-v2.yaml
- ✅ Implemented core: src/orchestrators/review/review_orchestrator_v2.py (700+ lines)
- ✅ Created stubs: analyzers/__init__.py, validators/__init__.py, reporters/__init__.py
- ✅ Generated plan: analysis/review-orchestrator-conversion-plan.md
- ⏸️ PENDING: Delete .github/prompts/cortex-review.prompt.md (after testing)
- ⏸️ PENDING: Progressive analyzer implementation (15 hours, Phase 4 integration)

**Governance Rules Integration Context:**
These rules address critical user pain points:
1. **Brittleness Issue:** Orchestrators failing with 502 errors due to large operations
2. **Summary File Bloat:** Unwanted *-summary.md files cluttering workspace (explicit user request to stop)
3. **Response Format:** Users want executive summaries with progress bars, NOT code snippets

Requirements from tracking/progress-tracker.json phases[1].deliverables
Success criteria from tracking/progress-tracker.json phases[1].success_criteria

Post-execution: 
1. Update tracking/progress-tracker.json phases[1].status="COMPLETE"
2. Increment overall_progress.phases_completed
3. Set overall_progress.current_phase=2
4. Execute vacuum cleanup (MANDATORY): `python3 -m src.main "vacuum cortex-brain/documents/planning/active/cortex5-epic"`
5. Regenerate plan-viewer.html from latest progress-tracker.json
