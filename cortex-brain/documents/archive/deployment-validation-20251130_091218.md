# Deployment Validation Report

**Timestamp:** 2025-11-30 09:12:18
**Version:** 3.3.0
**Overall Status:** ❌ FAILED

## Summary

- **Total Gates:** 16
- **Passed:** 14
- **Failed:** 2
- **Errors:** 1
- **Warnings:** 1

## Gate Results

### Gate 1: Integration Scores (ERROR)

**Status:** ❌ FAILED

**Message:** 12 features below 80% integration threshold

**Details:**

```json
[
  {
    "feature": "CleanupOrchestrator",
    "score": 70,
    "issues": []
  },
  {
    "feature": "DesignSyncOrchestrator",
    "score": 70,
    "issues": []
  },
  {
    "feature": "OptimizeCortexOrchestrator",
    "score": 70,
    "issues": []
  },
  {
    "feature": "WorkflowOrchestrator",
    "score": 70,
    "issues": []
  },
  {
    "feature": "ApplicationHealthOrchestrator",
    "score": 70,
    "issues": []
  },
  {
    "feature": "MasterSetupOrchestrator",
    "score": 70,
    "issues": []
  },
  {
    "feature": "RealignmentOrchestrator",
    "score": 70,
    "issues": []
  },
  {
    "feature": "SWAGGEREntryPointOrchestrator",
    "score": 70,
    "issues": []
  },
  {
    "feature": "ComplianceDashboardAgent",
    "score": 60,
    "issues": []
  },
  {
    "feature": "LearningCaptureAgent",
    "score": 70,
    "issues": []
  },
  {
    "feature": "ProfileAgent",
    "score": 70,
    "issues": []
  },
  {
    "feature": "WelcomeBannerAgent",
    "score": 70,
    "issues": []
  }
]
```

### Gate 2: Test Coverage (ERROR)

**Status:** ✅ PASSED

**Message:** All tests passing (validation placeholder)

**Details:**

```json
{
  "status": "assumed_passing"
}
```

### Gate 3: No Mocks in Production (ERROR)

**Status:** ✅ PASSED

**Message:** No production mocks found. 11 safe mock patterns detected (test helpers, introspection, templates).

**Details:**

```json
{
  "safe_mocks": [
    {
      "file": "src\\agents\\feature_completion_orchestrator.py",
      "line": 704,
      "pattern": "unittest_mock_import",
      "context": "main_block",
      "snippet": " 702:         FCO with mock implementations for all sub-agents\n 703:     \"\"\"\n 704:     from unittest.mock import AsyncMock\n 705:     \n 706:     fco = FeatureCompletionOrchestrator()"
    },
    {
      "file": "src\\agents\\feature_completion_orchestrator.py",
      "line": 709,
      "pattern": "mock_call",
      "context": "main_block",
      "snippet": " 707:     \n 708:     # Mock all sub-agents for testing\n 709:     fco.brain_ingestion_agent = AsyncMock()\n 710:     fco.discovery_engine = AsyncMock()\n 711:     fco.doc_intelligence = AsyncMock()"
    },
    {
      "file": "src\\agents\\feature_completion_orchestrator.py",
      "line": 710,
      "pattern": "mock_call",
      "context": "main_block",
      "snippet": " 708:     # Mock all sub-agents for testing\n 709:     fco.brain_ingestion_agent = AsyncMock()\n 710:     fco.discovery_engine = AsyncMock()\n 711:     fco.doc_intelligence = AsyncMock()\n 712:     fco.visual_generator = AsyncMock()"
    },
    {
      "file": "src\\agents\\feature_completion_orchestrator.py",
      "line": 711,
      "pattern": "mock_call",
      "context": "main_block",
      "snippet": " 709:     fco.brain_ingestion_agent = AsyncMock()\n 710:     fco.discovery_engine = AsyncMock()\n 711:     fco.doc_intelligence = AsyncMock()\n 712:     fco.visual_generator = AsyncMock()\n 713:     fco.optimization_monitor = AsyncMock()"
    },
    {
      "file": "src\\agents\\feature_completion_orchestrator.py",
      "line": 712,
      "pattern": "mock_call",
      "context": "main_block",
      "snippet": " 710:     fco.discovery_engine = AsyncMock()\n 711:     fco.doc_intelligence = AsyncMock()\n 712:     fco.visual_generator = AsyncMock()\n 713:     fco.optimization_monitor = AsyncMock()\n 714:     "
    },
    {
      "file": "src\\agents\\feature_completion_orchestrator.py",
      "line": 713,
      "pattern": "mock_call",
      "context": "main_block",
      "snippet": " 711:     fco.doc_intelligence = AsyncMock()\n 712:     fco.visual_generator = AsyncMock()\n 713:     fco.optimization_monitor = AsyncMock()\n 714:     \n 715:     return fco"
    },
    {
      "file": "src\\agents\\feature_completion_orchestrator_concrete.py",
      "line": 320,
      "pattern": "mock_class",
      "context": "main_block",
      "snippet": " 318: # ====================================================================================\n 319: \n 320: class MockFeatureCompletionOrchestrator(FeatureCompletionOrchestrator):\n 321:     \"\"\"Mock implementation for testing and development\"\"\"\n 322:     "
    },
    {
      "file": "src\\deployment\\deployment_gates.py",
      "line": 413,
      "pattern": "unittest_mock_import",
      "context": "main_block",
      "snippet": " 411:         \n 412:         # Check if the mock import is inside a string literal (template string)\n 413:         # Pattern: 'from unittest.mock import...' or \"from unittest.mock import...\"\n 414:         if match_line.strip().startswith((\"'from unittest\", '\"from unittest')):\n 415:             # This is a string containing the mock import, not actual import"
    },
    {
      "file": "src\\deployment\\deployment_gates.py",
      "line": 413,
      "pattern": "unittest_mock_import",
      "context": "main_block",
      "snippet": " 411:         \n 412:         # Check if the mock import is inside a string literal (template string)\n 413:         # Pattern: 'from unittest.mock import...' or \"from unittest.mock import...\"\n 414:         if match_line.strip().startswith((\"'from unittest\", '\"from unittest')):\n 415:             # This is a string containing the mock import, not actual import"
    },
    {
      "file": "src\\cortex_agents\\test_generator\\templates\\template_manager.py",
      "line": 75,
      "pattern": "unittest_mock_import",
      "context": "template_gen",
      "snippet": "  73:             '',\n  74:             'import pytest',\n  75:             'from unittest.mock import Mock, patch, MagicMock'\n  76:         ]\n  77:         "
    },
    {
      "file": "src\\application\\validation\\validator_extensions.py",
      "line": 84,
      "pattern": "mock_class",
      "context": "introspection",
      "snippet": "  82:         # If we can't extract the name, try calling the selector with a mock object\n  83:         try:\n  84:             class MockObject:\n  85:                 def __getattribute__(self, name):\n  86:                     if not name.startswith('_'):"
    }
  ]
}
```

### Gate 4: Documentation Sync (WARNING)

**Status:** ✅ PASSED

**Message:** Documentation appears synchronized

### Gate 5: Version Consistency (ERROR)

**Status:** ✅ PASSED

**Message:** Version consistent: 3.4.0

**Details:**

```json
{
  "package.json": "3.4.0"
}
```

### Gate 6: Template Format Validation (ERROR)

**Status:** ✅ PASSED

**Message:** All templates use new format v3.2 (100.0% compliant, 3 base templates)

**Details:**

```json
{
  "schema_version": "3.2",
  "score": 100.0,
  "compliant_templates": 12,
  "total_templates": 12,
  "base_templates_count": 3,
  "critical_violations": 0,
  "warning_violations": 0
}
```

### Gate 7: Git Checkpoint System (ERROR)

**Status:** ✅ PASSED

**Message:** Git Checkpoint System fully operational

**Details:**

```json
{
  "checks": {
    "orchestrator_exists": true,
    "orchestrator_imports": true,
    "config_exists": true,
    "config_valid": true,
    "brain_rule_active": true,
    "can_instantiate": true
  },
  "issues": [],
  "passed_checks": 6,
  "total_checks": 6
}
```

### Gate 8: Swagger/OpenAPI Documentation (ERROR)

**Status:** ✅ PASSED

**Message:** Swagger/OpenAPI documentation valid (4/4 checks passed)

**Details:**

```json
{
  "checks": {
    "api_file_exists": true,
    "valid_openapi_structure": true,
    "in_capabilities": true,
    "documented_in_prompt": true
  },
  "issues": [],
  "passed_checks": 4,
  "total_checks": 4,
  "api_doc_file": "docs\\api\\openapi.yaml"
}
```

### Gate 9: Timeframe Estimator Module (WARNING)

**Status:** ✅ PASSED

**Message:** Timeframe Estimator fully integrated (7/7 checks passed)

**Details:**

```json
{
  "checks": {
    "module_exists": true,
    "module_imports": true,
    "required_methods": true,
    "has_tests": true,
    "tests_pass": true,
    "documented": true,
    "entry_point_wired": true
  },
  "issues": [],
  "passed_checks": 7,
  "total_checks": 7
}
```

### Gate 10: Production File Validation (WARNING)

**Status:** ✅ PASSED

**Message:** Production validation passed with warnings: 28 items will be excluded by deploy_cortex.py

**Details:**

```json
{
  "blocked_found": {
    "directories": [
      "docs",
      "dist",
      "cortex-brain/admin",
      "scripts/admin",
      "test_merge",
      "workflow_checkpoints",
      ".vscode",
      ".pytest_cache"
    ],
    "files": [
      "cortex-brain/mkdocs-refresh-config.yaml",
      "mkdocs.yml"
    ],
    "patterns": [
      ".coverage",
      "cortex_alerts.db",
      "cortex_metrics.db",
      "cortex_status.db",
      "mkdocs.yml",
      "test_alignment_fix.py",
      "test_align_unified_workflow.py",
      "test_checkpoint_enforcement.py",
      "test_cross_platform_paths.py",
      "test_diagnostic.py",
      "test_enhanced_flow.py",
      "test_gate8_swagger.py",
      "test_git_checkpoint_system.py",
      "test_guide_check.py",
      "test_incremental_generation.py",
      "test_master_setup_integration.py",
      "test_tdd_validation.py",
      "test_tdd_validation_simple.py"
    ]
  },
  "issues": [
    "BLOCKED DIR: docs/ exists and would be included in production",
    "BLOCKED DIR: dist/ exists and would be included in production",
    "BLOCKED DIR: cortex-brain/admin/ exists and would be included in production",
    "BLOCKED DIR: scripts/admin/ exists and would be included in production",
    "BLOCKED DIR: test_merge/ exists and would be included in production",
    "BLOCKED DIR: workflow_checkpoints/ exists and would be included in production",
    "BLOCKED DIR: .vscode/ exists and would be included in production",
    "BLOCKED DIR: .pytest_cache/ exists and would be included in production",
    "BLOCKED FILE: .coverage matches blocked pattern '.coverage'",
    "BLOCKED FILE: cortex_alerts.db matches blocked pattern '*.db'",
    "BLOCKED FILE: cortex_metrics.db matches blocked pattern '*.db'",
    "BLOCKED FILE: cortex_status.db matches blocked pattern '*.db'",
    "BLOCKED FILE: mkdocs.yml matches blocked pattern 'mkdocs.yml'",
    "BLOCKED FILE: test_alignment_fix.py matches blocked pattern 'test_*.py'",
    "BLOCKED FILE: test_align_unified_workflow.py matches blocked pattern 'test_*.py'",
    "BLOCKED FILE: test_checkpoint_enforcement.py matches blocked pattern 'test_*.py'",
    "BLOCKED FILE: test_cross_platform_paths.py matches blocked pattern 'test_*.py'",
    "BLOCKED FILE: test_diagnostic.py matches blocked pattern 'test_*.py'",
    "BLOCKED FILE: test_enhanced_flow.py matches blocked pattern 'test_*.py'",
    "BLOCKED FILE: test_gate8_swagger.py matches blocked pattern 'test_*.py'",
    "BLOCKED FILE: test_git_checkpoint_system.py matches blocked pattern 'test_*.py'",
    "BLOCKED FILE: test_guide_check.py matches blocked pattern 'test_*.py'",
    "BLOCKED FILE: test_incremental_generation.py matches blocked pattern 'test_*.py'",
    "BLOCKED FILE: test_master_setup_integration.py matches blocked pattern 'test_*.py'",
    "BLOCKED FILE: test_tdd_validation.py matches blocked pattern 'test_*.py'",
    "BLOCKED FILE: test_tdd_validation_simple.py matches blocked pattern 'test_*.py'",
    "BLOCKED FILE: cortex-brain/mkdocs-refresh-config.yaml must be excluded from production"
  ],
  "total_blocked_dirs": 8,
  "total_blocked_files": 20
}
```

### Gate 11: CORTEX Brain Operational (ERROR)

**Status:** ✅ PASSED

**Message:** CORTEX Brain fully operational: All 6 checks passed

**Details:**

```json
{
  "checks": {
    "entry_point": true,
    "brain_structure": true,
    "tier_databases": true,
    "response_templates": true,
    "brain_protection": true,
    "orchestrator_wiring": true
  },
  "issues": [],
  "passed_checks": 6,
  "total_checks": 6,
  "score": "100%"
}
```

### Gate 12: Next Steps Formatting (ERROR)

**Status:** ✅ PASSED

**Message:** All Next Steps sections comply with formatting rules. No violations detected.

**Details:**

```json
{
  "violations": [],
  "by_type": {},
  "high_priority_files": [],
  "scanned_files": 0
}
```

### Gate 13: TDD Mastery Integration (ERROR)

**Status:** ✅ PASSED

**Message:** TDD Mastery fully integrated with Git Checkpoint system. All checks passed.

**Details:**

```json
{
  "git_checkpoint_imported": true,
  "config_has_git_option": true,
  "checkpoints_in_state_transitions": true,
  "guide_documents_git": true,
  "issues": []
}
```

### Gate 14: User Feature Packaging (ERROR)

**Status:** ✅ PASSED

**Message:** All user features packaged successfully. 5 features validated.

**Details:**

```json
{
  "required_features": {
    "swagger_analyzer": true,
    "work_planner": true,
    "ado_epm": true,
    "view_discovery": true,
    "feedback_system": true
  },
  "missing_features": [],
  "packaging_manifest": "3.3.0"
}
```

### Gate 15: Admin/User Separation (ERROR)

**Status:** ✅ PASSED

**Message:** Admin/user separation validated. 8 admin patterns correctly excluded.

**Details:**

```json
{
  "admin_leaks": [],
  "manifest_path": "publish\\deployment-manifest.json",
  "validated_exclusions": [
    "admin/",
    "deployment_gates.py",
    "deploy_cortex.py",
    "system_alignment_orchestrator.py",
    "enterprise_documentation_orchestrator.py",
    "deployment/",
    "validate_deployment.py",
    "publish_branch_orchestrator.py"
  ]
}
```

### Gate 16: Align EPM User-Only (WARNING)

**Status:** ❌ FAILED

**Message:** Setup EPM exposes admin operations: deploy. EPM should only show user-facing operations. WARNING: Deployment allowed but admin operations should be hidden from EPM.

**Details:**

```json
{
  "admin_triggers_found": [
    "deploy"
  ],
  "user_triggers_validated": [
    "help",
    "plan",
    "feedback",
    "upgrade"
  ],
  "epm_orchestrator_path": "src\\orchestrators\\setup_epm_orchestrator.py"
}
```

## Blocking Errors

- 12 features below 80% integration threshold

## Warnings (Non-Blocking)

- Setup EPM exposes admin operations: deploy. EPM should only show user-facing operations. WARNING: Deployment allowed but admin operations should be hidden from EPM.

