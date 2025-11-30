#!/usr/bin/env python3
"""
Update cortex-operations.yaml with status fields for all modules.

This script adds implementation status tracking to all 70 modules:
- Implemented modules: status="implemented", tests count, date
- Pending modules: status="pending", estimated hours

Author: Asif Hussain
Date: 2025-11-10
Part of: CORTEX 2.0 Architecture Refinement
"""

import yaml
from pathlib import Path
from datetime import datetime

# Define status for all modules
STATUS_MAP = {
    # ========================================================================
    # IMPLEMENTED MODULES (10 total)
    # ========================================================================
    
    # Environment Setup (4 modules)
    "platform_detection": {
        "status": "implemented",
        "tests": 15,
        "implemented_date": "2025-11-09",
        "lines_of_code": 156
    },
    "vision_api": {
        "status": "implemented",
        "tests": 12,
        "implemented_date": "2025-11-09",
        "lines_of_code": 245
    },
    "python_dependencies": {
        "status": "implemented",
        "tests": 8,
        "implemented_date": "2025-11-09",
        "lines_of_code": 178
    },
    "brain_initialization": {
        "status": "implemented",
        "tests": 10,
        "implemented_date": "2025-11-09",
        "lines_of_code": 203
    },
    
    # Story Refresh (6 modules)
    "load_story_template": {
        "status": "implemented",
        "tests": 5,
        "implemented_date": "2025-11-09",
        "lines_of_code": 89
    },
    "apply_narrator_voice": {
        "status": "implemented",
        "tests": 8,
        "implemented_date": "2025-11-09",
        "lines_of_code": 156
    },
    "validate_story_structure": {
        "status": "implemented",
        "tests": 6,
        "implemented_date": "2025-11-09",
        "lines_of_code": 134
    },
    "save_story_markdown": {
        "status": "implemented",
        "tests": 5,
        "implemented_date": "2025-11-09",
        "lines_of_code": 98
    },
    "update_mkdocs_index": {
        "status": "implemented",
        "tests": 4,
        "implemented_date": "2025-11-09",
        "lines_of_code": 123
    },
    "build_story_preview": {
        "status": "implemented",
        "tests": 3,
        "implemented_date": "2025-11-09",
        "lines_of_code": 87
    },
    
    # ========================================================================
    # PENDING MODULES (60 total) - WITH ESTIMATES
    # ========================================================================
    
    # Environment Setup - Remaining (7 modules)
    "project_validation": {"status": "pending", "estimated_hours": 1.5, "priority": "high"},
    "git_sync": {"status": "pending", "estimated_hours": 2.0, "priority": "high"},
    "virtual_environment": {"status": "pending", "estimated_hours": 2.5, "priority": "high"},
    "conversation_tracking": {"status": "pending", "estimated_hours": 3.0, "priority": "high"},
    "brain_tests": {"status": "pending", "estimated_hours": 2.0, "priority": "high"},
    "tooling_verification": {"status": "pending", "estimated_hours": 1.5, "priority": "high"},
    "setup_completion": {"status": "pending", "estimated_hours": 1.0, "priority": "high"},
    
    # Workspace Cleanup (6 modules)
    "scan_temporary_files": {"status": "pending", "estimated_hours": 1.5, "priority": "medium"},
    "remove_old_logs": {"status": "pending", "estimated_hours": 1.0, "priority": "medium"},
    "clear_python_cache": {"status": "pending", "estimated_hours": 0.5, "priority": "medium"},
    "vacuum_sqlite_databases": {"status": "pending", "estimated_hours": 1.5, "priority": "medium"},
    "remove_orphaned_files": {"status": "pending", "estimated_hours": 2.0, "priority": "medium"},
    "generate_cleanup_report": {"status": "pending", "estimated_hours": 1.0, "priority": "medium"},
    
    # Documentation Update (6 modules)
    "scan_docstrings": {"status": "pending", "estimated_hours": 2.0, "priority": "medium"},
    "generate_api_docs": {"status": "pending", "estimated_hours": 2.5, "priority": "medium"},
    "refresh_design_docs": {"status": "pending", "estimated_hours": 2.0, "priority": "medium"},
    "build_mkdocs_site": {"status": "pending", "estimated_hours": 1.5, "priority": "medium"},
    "validate_doc_links": {"status": "pending", "estimated_hours": 1.0, "priority": "medium"},
    "deploy_docs_preview": {"status": "pending", "estimated_hours": 1.5, "priority": "medium"},
    
    # Brain Protection (6 modules)
    "load_protection_rules": {"status": "pending", "estimated_hours": 1.0, "priority": "low"},
    "validate_tier0_immutability": {"status": "pending", "estimated_hours": 1.5, "priority": "low"},
    "validate_tier1_structure": {"status": "pending", "estimated_hours": 1.5, "priority": "low"},
    "validate_tier2_schema": {"status": "pending", "estimated_hours": 1.5, "priority": "low"},
    "check_brain_integrity": {"status": "pending", "estimated_hours": 2.0, "priority": "low"},
    "generate_protection_report": {"status": "pending", "estimated_hours": 1.0, "priority": "low"},
    
    # Test Execution (5 modules)
    "discover_tests": {"status": "pending", "estimated_hours": 1.0, "priority": "low"},
    "run_unit_tests": {"status": "pending", "estimated_hours": 1.5, "priority": "low"},
    "run_integration_tests": {"status": "pending", "estimated_hours": 1.5, "priority": "low"},
    "generate_coverage_report": {"status": "pending", "estimated_hours": 1.5, "priority": "low"},
    "validate_test_quality": {"status": "pending", "estimated_hours": 1.0, "priority": "low"},
    
    # CORTEX 2.1 - Interactive Planning (8 modules)
    "detect_planning_ambiguity": {"status": "pending", "estimated_hours": 2.5, "priority": "medium", "cortex_version": "2.1"},
    "generate_clarifying_questions": {"status": "pending", "estimated_hours": 3.0, "priority": "medium", "cortex_version": "2.1"},
    "parse_user_answers": {"status": "pending", "estimated_hours": 2.5, "priority": "medium", "cortex_version": "2.1"},
    "filter_redundant_questions": {"status": "pending", "estimated_hours": 2.0, "priority": "medium", "cortex_version": "2.1"},
    "extract_implied_context": {"status": "pending", "estimated_hours": 2.5, "priority": "medium", "cortex_version": "2.1"},
    "synthesize_planning_context": {"status": "pending", "estimated_hours": 2.0, "priority": "medium", "cortex_version": "2.1"},
    "generate_implementation_plan": {"status": "pending", "estimated_hours": 2.5, "priority": "medium", "cortex_version": "2.1"},
    "generate_architecture_plan": {"status": "pending", "estimated_hours": 2.5, "priority": "medium", "cortex_version": "2.1"},
    "generate_refactoring_plan": {"status": "pending", "estimated_hours": 2.0, "priority": "medium", "cortex_version": "2.1"},
    "present_plan_for_approval": {"status": "pending", "estimated_hours": 1.5, "priority": "medium", "cortex_version": "2.1"},
    
    # CORTEX 2.1 - Command Discovery (9 modules)
    "analyze_user_context": {"status": "pending", "estimated_hours": 2.0, "priority": "medium", "cortex_version": "2.1"},
    "filter_relevant_commands": {"status": "pending", "estimated_hours": 1.5, "priority": "medium", "cortex_version": "2.1"},
    "categorize_commands": {"status": "pending", "estimated_hours": 1.0, "priority": "medium", "cortex_version": "2.1"},
    "generate_help_output": {"status": "pending", "estimated_hours": 1.5, "priority": "medium", "cortex_version": "2.1"},
    "suggest_next_actions": {"status": "pending", "estimated_hours": 2.0, "priority": "medium", "cortex_version": "2.1"},
    "parse_search_query": {"status": "pending", "estimated_hours": 1.0, "priority": "medium", "cortex_version": "2.1"},
    "search_command_index": {"status": "pending", "estimated_hours": 2.0, "priority": "medium", "cortex_version": "2.1"},
    "rank_search_results": {"status": "pending", "estimated_hours": 1.5, "priority": "medium", "cortex_version": "2.1"},
    "generate_search_output": {"status": "pending", "estimated_hours": 1.0, "priority": "medium", "cortex_version": "2.1"},
}


def update_operations_yaml():
    """Update cortex-operations.yaml with status fields."""
    
    # Find the YAML file
    yaml_path = Path(__file__).parent.parent / "cortex-operations.yaml"
    
    if not yaml_path.exists():
        print(f"❌ Error: {yaml_path} not found")
        return False
    
    print(f"📂 Loading: {yaml_path}")
    
    # Load YAML
    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    
    if not data or "modules" not in data:
        print("❌ Error: Invalid YAML structure (no 'modules' key)")
        return False
    
    # Track statistics
    updated_count = 0
    implemented_count = 0
    pending_count = 0
    missing_count = 0
    
    # Update each module
    for module_id, module_info in data["modules"].items():
        if module_id in STATUS_MAP:
            # Merge status info
            status_info = STATUS_MAP[module_id]
            data["modules"][module_id].update(status_info)
            updated_count += 1
            
            if status_info["status"] == "implemented":
                implemented_count += 1
            else:
                pending_count += 1
        else:
            missing_count += 1
            print(f"⚠️  Warning: No status defined for module '{module_id}'")
    
    # Update metadata statistics
    if "metadata" in data and "statistics" in data["metadata"]:
        data["metadata"]["statistics"]["modules_implemented"] = implemented_count
        data["metadata"]["statistics"]["modules_pending"] = pending_count
        data["metadata"]["last_updated"] = datetime.now().strftime("%Y-%m-%d")
    
    # Save updated YAML
    print(f"\n💾 Saving changes to: {yaml_path}")
    
    with open(yaml_path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    # Print summary
    print("\n" + "="*60)
    print("✅ CORTEX Operations Status Update Complete")
    print("="*60)
    print(f"📊 Modules updated: {updated_count}/70")
    print(f"✅ Implemented: {implemented_count} modules")
    print(f"⏸️  Pending: {pending_count} modules")
    
    if missing_count > 0:
        print(f"⚠️  Missing status: {missing_count} modules")
    
    print("\n📈 Implementation Progress: {:.1f}%".format(
        (implemented_count / 70) * 100
    ))
    
    # Estimate total remaining work
    total_hours = sum(
        info.get("estimated_hours", 0) 
        for info in STATUS_MAP.values() 
        if info.get("status") == "pending"
    )
    print(f"⏱️  Estimated remaining work: {total_hours:.1f} hours")
    
    return True


def validate_update():
    """Validate that all modules have status field."""
    
    yaml_path = Path(__file__).parent.parent / "cortex-operations.yaml"
    
    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    
    modules_with_status = 0
    modules_without_status = []
    
    for module_id, module_info in data["modules"].items():
        if "status" in module_info:
            modules_with_status += 1
        else:
            modules_without_status.append(module_id)
    
    print("\n" + "="*60)
    print("🔍 Validation Results")
    print("="*60)
    print(f"✅ Modules with status: {modules_with_status}/70")
    
    if modules_without_status:
        print(f"❌ Modules missing status: {len(modules_without_status)}")
        for module_id in modules_without_status:
            print(f"   - {module_id}")
        return False
    
    print("✅ All modules have status field!")
    return True


if __name__ == "__main__":
    print("🚀 CORTEX Operations Status Updater")
    print("="*60)
    print("Purpose: Add implementation status to all 70 modules")
    print("Version: 1.0")
    print("Date: 2025-11-10")
    print("="*60 + "\n")
    
    # Update YAML
    success = update_operations_yaml()
    
    if success:
        # Validate update
        validate_update()
        print("\n✅ Status update complete!")
        print("📝 Next: Review cortex-operations.yaml for accuracy")
    else:
        print("\n❌ Status update failed!")
        exit(1)
