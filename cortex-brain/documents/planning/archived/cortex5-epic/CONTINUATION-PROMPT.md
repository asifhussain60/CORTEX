Restructure cortex5-epic to strict design per analysis/restructuring-requirements.yaml

Plan: cortex5-epic | Action: Epic Restructuring | Priority: P0_CRITICAL

Context: analysis/restructuring-requirements.yaml, analysis/planner.md design doc

**✅ BACKUP ARCHIVED:** cortex5-epic-backup-20260107-083422 → cortex-brain/archives/cortex5-epic/  
**✅ PLAN VIEWER GENERATED:** plan-viewer.html (31KB, zero validation errors, WCAG AA compliant)

Python Orchestrator Implementation Required:
- Update src/orchestrators/planning_orchestrator.py
- Implement migrate_epic_structure() method
- Implement generate_plan_viewer_html() with auto-detection
- Implement generate_continuation_prompt() 
- Add validation checks

Invocation: python3 -m src.main "restructure cortex5-epic to strict design" --format markdown

Post-execution: Verify root has 3 files, features/ has 10 folders, epic-progress-tracker.json exists

**Plan Viewer:** Open `plan-viewer.html` in browser for interactive navigation of all 68 epic files.


