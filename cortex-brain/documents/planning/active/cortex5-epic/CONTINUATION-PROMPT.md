Execute Phase 1: Critical Blocker Resolution

Plan: cortex5-epic | Progress: 7% | Phase 1/14

Context: tracking/progress-tracker.json, phases/phase-01-blocker-resolution.md, reports/master-plan-v3.md

**Recent Changes:** Root folder cleanup complete (PLAN_FILE_ORGANIZATION enforced)
- ✅ Moved 00-*.md files to reports/ (master-plan-v3.md, master-plan-v2-legacy.md)
- ✅ Moved README.md to reports/quick-start-guide.md
- ✅ Centralized cortex-logo.png in planning/assets/images/
- ✅ Updated vacuum rules to prevent future violations

Requirements from tracking/progress-tracker.json phases[1].deliverables
Success criteria from tracking/progress-tracker.json phases[1].success_criteria

Post-execution: 
1. Update tracking/progress-tracker.json phases[1].status="COMPLETE"
2. Increment overall_progress.phases_completed
3. Set overall_progress.current_phase=2
4. Execute vacuum cleanup (MANDATORY): `python3 -m src.main "vacuum cortex-brain/documents/planning/active/cortex5-epic"`
5. Regenerate plan-viewer.html from latest progress-tracker.json
