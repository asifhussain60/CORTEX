# 🎯 11-Phase Optimized Maintenance Pipeline

**⚠️ EVERY PHASE = DIAGNOSE + AUTO-REPAIR + VERIFY**

---

## Pipeline Strategy: DISCOVER → CLEAN → PRESERVE → WIRE → TEST → VERIFY

| Phase | Focus Area | Diagnose | Auto-Repair | Verify |
|-------|-----------|----------|-------------|--------|
| **0** | **🧹 CLEANUP ORCHESTRATOR** | **Smart cleanup execution** | **Delete backups, clear caches** | **Zero bloat** |
| **1** | **🔍 DISCOVERY** | **Scan entire system for enhancements, gaps, bloat** | **Generate comprehensive action report** | **All issues cataloged** |
| **2** | **🗑️ TEMPLATE VALIDATION** | **Validate templates, remove legacy, resolve duplicates** | **Fix broken refs, delete duplicates** | **Valid templates** |
| **3** | **⛔ PRESERVATION** | **Validate protected data paths exist** | **Verify no critical data in cleanup targets** | **All user data safe** |
| **4** | **🔧 SCAFFOLDING** | **Check toolkit generators exist** | **Create missing generators** | **Test generation works** |
| **5** | **🔌 WIRING** | **Detect unwired components** | **Auto-wire orchestrators, agents** | **100% wiring coverage** |
| **6** | **🧪 TESTING** | **Run full test suite** | **Delete obsolete tests, fix bugs** | **100% pass rate** |
| **7** | **📚 KNOWLEDGE** | **Scan knowledge library, validate plan content** | **Fix broken refs, sync YAML↔MD, auto-repair plans** | **All guidelines accessible, plans conformant** |
| **8** | **🗂️ ORGANIZATION** | **Check report structure** | **Archive old, consolidate duplicates** | **Clean hierarchy** |
| **9** | **🔀 ROUTING** | **Validate intent router** | **Fix broken manifest paths** | **All routes functional** |
| **10** | **📝 PROMPTS** | **Measure prompt bloat** | **Regenerate lean prompts** | **Each <200 lines** |
| **11** | **✅ VERIFICATION** | **Run health diagnostics** | **Fix critical issues** | **Health score ≥95** |

---

## Phase Execution Order (Optimized for Efficiency)

```
Phase 0: CLEANUP ORCHESTRATOR (Smart Cleanup)
  ├─ Load cleanup rules: cortex-brain/cleanup-rules.yaml
  ├─ Execute cleanup orchestrator: src/plugins/cleanup_orchestrator.py
  ├─ Delete backups, archives, temp files
  ├─ Preserve protected data paths (brain DBs, lessons-learned, etc.)
  └─ Generate cleanup manifest
  
Phase 1: DISCOVERY (Holistic Scan)
  ├─ Identify all unwired components
  ├─ Detect duplicate reports
  ├─ Measure prompt bloat
  ├─ Check knowledge library sync
  ├─ Validate test suite health
  └─ Generate master action report
  
Phase 2: TEMPLATE VALIDATION (Quality Check)
  ├─ Validate all template references
  ├─ Check response-templates-v4.yaml integrity
  └─ Fix broken template paths
  
Phase 3: PRESERVATION (Validate Protected Data)
  └─ Verify critical data paths safe
  
Phase 4: SCAFFOLDING (Foundation)
  └─ Verify/create toolkit generators
  
Phase 5: WIRING (Connections)
  ├─ Auto-wire orchestrators
  ├─ Register agents
  └─ Update manifests
  
Phase 6: TESTING (Quality)
  ├─ Run test suite
  └─ Delete obsolete tests
  
Phase 7: KNOWLEDGE (Content)
  └─ Sync knowledge library
  
Phase 8: ORGANIZATION (Structure)
  └─ Organize reports
  
Phase 9: ROUTING (Navigation)
  └─ Fix intent router
  
Phase 10: PROMPTS (Templates)
  └─ Regenerate lean prompts (preserve ALL orchestrators + Vision API)
  
Phase 11: VERIFICATION (Final Health Check)
  └─ Confirm 100% system health
```

---

## 🤖 Autonomous Execution Block

**⚠️ EXECUTE ALL PHASES IN SEQUENCE WITHOUT STOPPING**

When `system maintenance` is invoked, execute this consolidated flow:

```python
# PSEUDO-CODE FOR AUTONOMOUS EXECUTION
# This is the EXACT behavior Copilot must follow

def execute_maintenance():
    """
    Autonomous 12-phase maintenance pipeline.
    NO USER INTERACTION between phases.
    """
    phases = [
        (0, "CLEANUP_ORCHESTRATOR", run_cleanup_orchestrator),
        (1, "DISCOVERY", discover_system),
        (2, "TEMPLATE_VALIDATION", validate_templates),
        (3, "PRESERVATION", validate_preservation),
        (4, "SCAFFOLDING", verify_scaffolds),
        (5, "WIRING", wire_components),
        (6, "TESTING", run_tests),
        (7, "KNOWLEDGE", sync_knowledge),
        (8, "ORGANIZATION", organize_reports),
        (9, "ROUTING", fix_routing),
        (10, "PROMPTS", optimize_prompts),
        (11, "VERIFICATION", verify_health),
    ]
    
    results = {}
    
    for phase_num, phase_name, phase_func in phases:
        # Show progress BEFORE phase
        render_progress_tracker(phase_num, "IN_PROGRESS")
        
        # Execute phase (NO CONFIRMATION)
        result = phase_func()
        
        # Auto-repair if issues found
        if result.issues:
            for issue in result.issues:
                auto_repair(issue)  # FIX IMMEDIATELY
        
        # Log completion (NO PAUSE)
        log(f"✅ Phase {phase_num} - {phase_name}: Complete")
        
        # Store result
        results[phase_num] = result
        
        # IMMEDIATELY proceed to next phase
        # ⛔ NO: "Ready for Phase N+1?"
        # ⛔ NO: "Should I continue?"
        # ✅ YES: Just start next phase
    
    # ONLY at end: Generate consolidated report
    generate_final_report(results)
    commit_all_changes()
    
    return "✅ All 11 phases complete!"
```

---

**For detailed phase instructions, see `phases/phase-{00-11}-*.prompt.md`**
