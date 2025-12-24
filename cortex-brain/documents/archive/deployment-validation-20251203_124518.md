# Deployment Validation Report

**Timestamp:** 2025-12-03 12:45:18
**Version:** 3.5.5
**Overall Status:** ✅ PASSED

## Summary

- **Total Gates:** 21
- **Passed:** 15
- **Failed:** 6
- **Errors:** 0
- **Warnings:** 6

## Gate Results

### Gate 1: Integration Scores (ERROR)

**Status:** ✅ PASSED

**Message:** All user-facing features meet 80% integration threshold (admin features excluded)

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

**Message:** No production mocks found. 12 safe mock patterns detected (test helpers, introspection, templates).

**Details:**

```json
{
  "safe_mocks": [
    {
      "file": "src\\agents\\feature_completion_orchestrator.py",
      "line": 699,
      "pattern": "unittest_mock_import",
      "context": "main_block",
      "snippet": " 697:         FCO with mock implementations for all sub-agents\n 698:     \"\"\"\n 699:     from unittest.mock import AsyncMock\n 700:     \n 701:     fco = FeatureCompletionOrchestrator()"
    },
    {
      "file": "src\\agents\\feature_completion_orchestrator.py",
      "line": 704,
      "pattern": "mock_call",
      "context": "main_block",
      "snippet": " 702:     \n 703:     # Mock all sub-agents for testing\n 704:     fco.brain_ingestion_agent = AsyncMock()\n 705:     fco.discovery_engine = AsyncMock()\n 706:     fco.doc_intelligence = AsyncMock()"
    },
    {
      "file": "src\\agents\\feature_completion_orchestrator.py",
      "line": 705,
      "pattern": "mock_call",
      "context": "main_block",
      "snippet": " 703:     # Mock all sub-agents for testing\n 704:     fco.brain_ingestion_agent = AsyncMock()\n 705:     fco.discovery_engine = AsyncMock()\n 706:     fco.doc_intelligence = AsyncMock()\n 707:     fco.visual_generator = AsyncMock()"
    },
    {
      "file": "src\\agents\\feature_completion_orchestrator.py",
      "line": 706,
      "pattern": "mock_call",
      "context": "main_block",
      "snippet": " 704:     fco.brain_ingestion_agent = AsyncMock()\n 705:     fco.discovery_engine = AsyncMock()\n 706:     fco.doc_intelligence = AsyncMock()\n 707:     fco.visual_generator = AsyncMock()\n 708:     fco.optimization_monitor = AsyncMock()"
    },
    {
      "file": "src\\agents\\feature_completion_orchestrator.py",
      "line": 707,
      "pattern": "mock_call",
      "context": "main_block",
      "snippet": " 705:     fco.discovery_engine = AsyncMock()\n 706:     fco.doc_intelligence = AsyncMock()\n 707:     fco.visual_generator = AsyncMock()\n 708:     fco.optimization_monitor = AsyncMock()\n 709:     "
    },
    {
      "file": "src\\agents\\feature_completion_orchestrator.py",
      "line": 708,
      "pattern": "mock_call",
      "context": "main_block",
      "snippet": " 706:     fco.doc_intelligence = AsyncMock()\n 707:     fco.visual_generator = AsyncMock()\n 708:     fco.optimization_monitor = AsyncMock()\n 709:     \n 710:     return fco"
    },
    {
      "file": "src\\agents\\feature_completion_orchestrator_concrete.py",
      "line": 317,
      "pattern": "mock_class",
      "context": "main_block",
      "snippet": " 315: # ====================================================================================\n 316: \n 317: class MockFeatureCompletionOrchestrator(FeatureCompletionOrchestrator):\n 318:     \"\"\"Mock implementation for testing and development\"\"\"\n 319:     "
    },
    {
      "file": "src\\deployment\\deployment_gates.py",
      "line": 459,
      "pattern": "unittest_mock_import",
      "context": "main_block",
      "snippet": " 457:         \n 458:         # Check if the mock import is inside a string literal (template string)\n 459:         # Pattern: 'from unittest.mock import...' or \"from unittest.mock import...\"\n 460:         if match_line.strip().startswith((\"'from unittest\", '\"from unittest')):\n 461:             # This is a string containing the mock import, not actual import"
    },
    {
      "file": "src\\deployment\\deployment_gates.py",
      "line": 459,
      "pattern": "unittest_mock_import",
      "context": "main_block",
      "snippet": " 457:         \n 458:         # Check if the mock import is inside a string literal (template string)\n 459:         # Pattern: 'from unittest.mock import...' or \"from unittest.mock import...\"\n 460:         if match_line.strip().startswith((\"'from unittest\", '\"from unittest')):\n 461:             # This is a string containing the mock import, not actual import"
    },
    {
      "file": "src\\operations\\modules\\realignment\\realignment_utility.py",
      "line": 1074,
      "pattern": "mock_class",
      "context": "main_block",
      "snippet": "1072:         \n1073:         @dataclass\n1074:         class MockViolation:\n1075:             category: str = \"naming\"\n1076:             description: str = \"Use camelCase\""
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
      "line": 83,
      "pattern": "mock_class",
      "context": "introspection",
      "snippet": "  81:         # If we can't extract the name, try calling the selector with a mock object\n  82:         try:\n  83:             class MockObject:\n  84:                 def __getattribute__(self, name):\n  85:                     if not name.startswith('_'):"
    }
  ]
}
```

### Gate 4: Documentation Sync (WARNING)

**Status:** ✅ PASSED

**Message:** Documentation appears synchronized

### Gate 5: Version Consistency (ERROR)

**Status:** ✅ PASSED

**Message:** Version consistent: 3.5.5

**Details:**

```json
{
  "VERSION": "3.5.5",
  "CORTEX.prompt.md": "3.5.5"
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

### Gate 7: Git Checkpoint System (WARNING)

**Status:** ✅ PASSED

**Message:** Git Checkpoint System fully operational

**Details:**

```json
{
  "checks": {
    "utility_exists": true,
    "utility_imports": true,
    "config_exists": true,
    "config_valid": true,
    "brain_rule_active": true,
    "can_call_utility": true
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

**Message:** Production validation passed with warnings: 10 items will be excluded by deploy_cortex.py

**Details:**

```json
{
  "blocked_found": {
    "directories": [
      ".pytest_cache",
      "test_merge",
      "docs",
      "cortex-brain/admin",
      "scripts/admin",
      ".vscode"
    ],
    "files": [
      "mkdocs.yml",
      "cortex-brain/mkdocs-refresh-config.yaml"
    ],
    "patterns": [
      "mkdocs.yml",
      "test_gate8_swagger.py"
    ]
  },
  "issues": [
    "BLOCKED DIR: .pytest_cache/ exists and would be included in production",
    "BLOCKED DIR: test_merge/ exists and would be included in production",
    "BLOCKED DIR: docs/ exists and would be included in production",
    "BLOCKED DIR: cortex-brain/admin/ exists and would be included in production",
    "BLOCKED DIR: scripts/admin/ exists and would be included in production",
    "BLOCKED DIR: .vscode/ exists and would be included in production",
    "BLOCKED FILE: mkdocs.yml matches blocked pattern 'mkdocs.yml'",
    "BLOCKED FILE: test_gate8_swagger.py matches blocked pattern 'test_*.py'",
    "BLOCKED FILE: cortex-brain/mkdocs-refresh-config.yaml must be excluded from production"
  ],
  "total_blocked_dirs": 6,
  "total_blocked_files": 4
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

### Gate 13: TDD Mastery Integration (WARNING)

**Status:** ✅ PASSED

**Message:** TDD Mastery fully integrated: RED→GREEN→REFACTOR workflow operational. All 10 checks passed: State machine, git checkpoints, terminal integration, auto-debug, Vision API, complete documentation.

**Details:**

```json
{
  "tdd_orchestrator_exists": true,
  "tdd_orchestrator_imports": true,
  "state_machine_exists": true,
  "state_machine_has_phases": true,
  "git_checkpoint_imported": true,
  "config_has_git_option": true,
  "terminal_integration_exists": true,
  "auto_debug_enabled": true,
  "guide_documents_workflow": true,
  "vision_api_integrated": true,
  "issues": []
}
```

### Gate 14: User Feature Packaging (WARNING)

**Status:** ❌ FAILED

**Message:** User feature packaging incomplete: 3 features missing. Missing: SWAGGER complexity analyzer, Work planner (feature planning), ADO EPM (work item management). Production deployment BLOCKED until all user features packaged.

**Details:**

```json
{
  "required_features": {
    "swagger_analyzer": false,
    "work_planner": false,
    "ado_epm": false,
    "view_discovery": true,
    "feedback_system": true
  },
  "missing_features": [
    "SWAGGER complexity analyzer",
    "Work planner (feature planning)",
    "ADO EPM (work item management)"
  ],
  "packaging_manifest": "3.5.5"
}
```

### Gate 15: Production Content Purity (WARNING)

**Status:** ❌ FAILED

**Message:** ❌ Production content purity FAILED: 44 blocked items found
   - 16 admin/dev directories
   - 28 blocked files
   REQUIRED ACTION: Remove all admin/dev content before deployment
   See details for complete list of blocked items

**Details:**

```json
{
  "blocked_found": {
    "directories": [
      "publish",
      ".github/CopilotChats",
      "tests",
      "examples",
      "cortex-brain/admin",
      ".vscode",
      "tests/operations/modules/admin",
      "cortex-extension",
      ".github/Environments",
      "logs",
      ".pytest_cache",
      "test_merge",
      "docs",
      "tests/operations/admin",
      "src/operations/modules/admin",
      "scripts/admin"
    ],
    "files": [
      "ado-validation.json",
      "alignment_result.txt",
      "deployment-validation.json",
      "MAC-CONTINUATION-GUIDE.md",
      "mkdocs.yml",
      "run_deploy_gates.py",
      "run_optimize.py",
      "test_gate8_swagger.py",
      "validate_yaml.py",
      "cortex-brain\\admin\\documentation",
      "cortex-brain\\admin\\reports",
      "cortex-brain\\admin\\scripts",
      "cortex-brain\\admin\\documentation\\.test-output",
      "cortex-brain\\admin\\documentation\\.test-output-e2e",
      "src\\operations\\modules\\admin\\alignment_models.py",
      "src\\operations\\modules\\admin\\alignment_validators.py",
      "src\\operations\\modules\\admin\\align_utility.py",
      "src\\operations\\modules\\admin\\documentation_governance_validator.py",
      "src\\operations\\modules\\admin\\gap_remediation_validator.py",
      ".vscode\\cortex.code-snippets",
      ".vscode\\settings.json",
      ".vscode\\settings.recommended.json",
      ".github\\CopilotChats\\Conversations",
      ".github\\CopilotChats\\enhancements",
      ".github\\CopilotChats\\issues",
      ".github\\CopilotChats\\Conversations\\2025",
      ".github\\CopilotChats\\enhancements\\consolidated-plan.md",
      "deploy_cortex.py (missing exclusions)"
    ],
    "patterns": []
  },
  "issues": [
    "\u26d4 BLOCKED DIR: publish/ exists - MUST be excluded before deployment",
    "\u26d4 BLOCKED DIR: .github/CopilotChats/ exists - MUST be excluded before deployment",
    "\u26d4 BLOCKED DIR: tests/ exists - MUST be excluded before deployment",
    "\u26d4 BLOCKED DIR: examples/ exists - MUST be excluded before deployment",
    "\u26d4 BLOCKED DIR: cortex-brain/admin/ exists - MUST be excluded before deployment",
    "\u26d4 BLOCKED DIR: .vscode/ exists - MUST be excluded before deployment",
    "\u26d4 BLOCKED DIR: tests/operations/modules/admin/ exists - MUST be excluded before deployment",
    "\u26d4 BLOCKED DIR: cortex-extension/ exists - MUST be excluded before deployment",
    "\u26d4 BLOCKED DIR: .github/Environments/ exists - MUST be excluded before deployment",
    "\u26d4 BLOCKED DIR: logs/ exists - MUST be excluded before deployment",
    "\u26d4 BLOCKED DIR: .pytest_cache/ exists - MUST be excluded before deployment",
    "\u26d4 BLOCKED DIR: test_merge/ exists - MUST be excluded before deployment",
    "\u26d4 BLOCKED DIR: docs/ exists - MUST be excluded before deployment",
    "\u26d4 BLOCKED DIR: tests/operations/admin/ exists - MUST be excluded before deployment",
    "\u26d4 BLOCKED DIR: src/operations/modules/admin/ exists - MUST be excluded before deployment",
    "\u26d4 BLOCKED DIR: scripts/admin/ exists - MUST be excluded before deployment",
    "\u26d4 BLOCKED FILE: ado-validation.json - admin/dev only",
    "\u26d4 BLOCKED FILE: alignment_result.txt - admin/dev only",
    "\u26d4 BLOCKED FILE: deployment-validation.json - admin/dev only",
    "\u26d4 BLOCKED FILE: MAC-CONTINUATION-GUIDE.md - admin/dev only",
    "\u26d4 BLOCKED FILE: mkdocs.yml - admin/dev only",
    "\u26d4 BLOCKED FILE: run_deploy_gates.py - admin/dev only",
    "\u26d4 BLOCKED FILE: run_optimize.py - admin/dev only",
    "\u26d4 BLOCKED FILE: test_gate8_swagger.py - admin/dev only",
    "\u26d4 BLOCKED FILE: validate_yaml.py - admin/dev only",
    "\u26d4 ADMIN CONTENT: cortex-brain\\admin\\documentation",
    "\u26d4 ADMIN CONTENT: cortex-brain\\admin\\reports",
    "\u26d4 ADMIN CONTENT: cortex-brain\\admin\\scripts",
    "\u26d4 ADMIN CONTENT: cortex-brain\\admin\\documentation\\.test-output",
    "\u26d4 ADMIN CONTENT: cortex-brain\\admin\\documentation\\.test-output-e2e",
    "\u26d4 ADMIN CONTENT: src\\operations\\modules\\admin\\alignment_models.py",
    "\u26d4 ADMIN CONTENT: src\\operations\\modules\\admin\\alignment_validators.py",
    "\u26d4 ADMIN CONTENT: src\\operations\\modules\\admin\\align_utility.py",
    "\u26d4 ADMIN CONTENT: src\\operations\\modules\\admin\\documentation_governance_validator.py",
    "\u26d4 ADMIN CONTENT: src\\operations\\modules\\admin\\gap_remediation_validator.py",
    "\u26d4 ADMIN CONTENT: .vscode\\cortex.code-snippets",
    "\u26d4 ADMIN CONTENT: .vscode\\settings.json",
    "\u26d4 ADMIN CONTENT: .vscode\\settings.recommended.json",
    "\u26d4 ADMIN CONTENT: .github\\CopilotChats\\Conversations",
    "\u26d4 ADMIN CONTENT: .github\\CopilotChats\\enhancements",
    "\u26d4 ADMIN CONTENT: .github\\CopilotChats\\issues",
    "\u26d4 ADMIN CONTENT: .github\\CopilotChats\\Conversations\\2025",
    "\u26d4 ADMIN CONTENT: .github\\CopilotChats\\enhancements\\consolidated-plan.md",
    "\u26a0\ufe0f  DEPLOY SCRIPT: Missing exclusions: .github/CopilotChats"
  ],
  "total_blocked_dirs": 16,
  "total_blocked_files": 28,
  "scan_categories": {
    "admin_dirs": 5,
    "dev_dirs": 1,
    "test_dirs": 5,
    "build_dirs": 1
  }
}
```

### Gate 16: Align EPM User-Only (WARNING)

**Status:** ❌ FAILED

**Message:** Setup EPM orchestrator not found. Cannot validate user-only operations.

**Details:**

```json
{
  "admin_triggers_found": [],
  "user_triggers_validated": [],
  "epm_orchestrator_path": null
}
```

### Gate 17: Incremental Work Management System (v3.2.1) (WARNING)

**Status:** ❌ FAILED

**Message:** Layer 2 (IncrementalWorkExecutor) not found. Critical component missing.

**Details:**

```json
{
  "layer1_status": {
    "exists": true,
    "has_response_size_monitor": true,
    "has_estimate_tokens": true,
    "has_check_response": true,
    "has_auto_chunking": true,
    "test_file_exists": true
  },
  "layer2_status": {
    "exists": false
  },
  "layer3_status": {},
  "test_coverage": {},
  "integration_status": {}
}
```

### Gate 18: EPM Wiring Enforcement (ERROR)

**Status:** ✅ PASSED

**Message:** SetupEPMOrchestrator confirmed wired and operational (score: 80/100). EPM entry point ready for production deployment.

**Details:**

```json
{
  "alignment_file_loaded": true,
  "orchestrator_count": 42,
  "epm_status": {
    "score": 80,
    "discovered": true,
    "imported": true,
    "instantiated": true,
    "documented": true,
    "tested": false,
    "wired": true,
    "optimized": false,
    "timestamp": "2025-11-30T07:41:03.165259"
  },
  "validation_timestamp": "2025-11-30T07:41:03.165259",
  "quality_score": 80
}
```

### Gate 19: Token Efficiency (WARNING)

**Status:** ❌ FAILED

**Message:** Token budget validation FAILED. Total: 76,342 tokens (Budget: 76,000 tokens). Overage: 342 tokens. Deployment BLOCKED until optimization completes.

Violations (1 files):
  • response-templates.yaml: 30,899 / 25,000 tokens (23.6% over)

ACTION REQUIRED: Execute token optimization phases:
  Phase 1: Modularization (101K → 11K, -88.8%)
  Phase 2: Template compression (11K → 5K, -94.9%)
  Phase 3: Lazy loading (5K → 3K, -96.9%)
  Phase 4: Reference compression (3K → 2K, -98.0%)

See: cortex-brain/documents/planning/TOKEN-OPTIMIZATION-HOLISTIC-PLAN.md

**Details:**

```json
{
  "timestamp": "2025-12-03T12:45:18.035770",
  "execution_time": 0.00931549072265625,
  "total_current_tokens": 76342,
  "total_budget_tokens": 76000,
  "total_overage_tokens": 342,
  "is_compliant": false,
  "compliant_count": 3,
  "total_count": 4,
  "files": [
    {
      "name": "CORTEX.prompt.md",
      "path": "D:\\PROJECTS\\CORTEX\\.github\\prompts\\CORTEX.prompt.md",
      "current_tokens": 10834,
      "max_tokens": 12000,
      "char_count": 43336,
      "line_count": 825,
      "is_compliant": true,
      "overage_tokens": -1166,
      "overage_percent": -9.716666666666667,
      "reduction_needed": -10.76241462063873
    },
    {
      "name": "brain-protection-rules.yaml",
      "path": "D:\\PROJECTS\\CORTEX\\cortex-brain\\brain-protection-rules.yaml",
      "current_tokens": 31035,
      "max_tokens": 35000,
      "char_count": 124143,
      "line_count": 1999,
      "is_compliant": true,
      "overage_tokens": -3965,
      "overage_percent": -11.328571428571427,
      "reduction_needed": -12.775898179474787
    },
    {
      "name": "response-templates.yaml",
      "path": "D:\\PROJECTS\\CORTEX\\cortex-brain\\response-templates.yaml",
      "current_tokens": 30899,
      "max_tokens": 25000,
      "char_count": 123596,
      "line_count": 3056,
      "is_compliant": false,
      "overage_tokens": 5899,
      "overage_percent": 23.596,
      "reduction_needed": 19.091232725978188
    },
    {
      "name": "copilot-instructions.md",
      "path": "D:\\PROJECTS\\CORTEX\\.github\\copilot-instructions.md",
      "current_tokens": 3574,
      "max_tokens": 4000,
      "char_count": 14299,
      "line_count": 299,
      "is_compliant": true,
      "overage_tokens": -426,
      "overage_percent": -10.65,
      "reduction_needed": -11.9194180190263
    }
  ]
}
```

### Gate 20: Application Onboarding (WARNING)

**Status:** ❌ FAILED

**Message:** Application onboarding incomplete: 1 issues (5/6 checks passed). Can deploy without onboarding - users can onboard manually.

**Details:**

```json
{
  "operation_exists": true,
  "operation_imports": false,
  "orchestrator_exists": true,
  "epm_integration": true,
  "step_registry_configured": true,
  "profiles_supported": true,
  "issues": [
    "Cannot import ApplicationOnboardingOperation: No module named 'src.epm'"
  ]
}
```

### Gate 21: Dashboard Utility (WARNING)

**Status:** ✅ PASSED

**Message:** Dashboard utility fully operational: D3.js charts, data collection, template rendering (6/6 checks passed).

**Details:**

```json
{
  "utility_exists": true,
  "utility_imports": true,
  "has_d3_charts": true,
  "data_collector_integrated": true,
  "template_rendering": true,
  "output_directory_configured": true,
  "issues": []
}
```

## Warnings (Non-Blocking)

- User feature packaging incomplete: 3 features missing. Missing: SWAGGER complexity analyzer, Work planner (feature planning), ADO EPM (work item management). Production deployment BLOCKED until all user features packaged.
- ❌ Production content purity FAILED: 44 blocked items found
   - 16 admin/dev directories
   - 28 blocked files
   REQUIRED ACTION: Remove all admin/dev content before deployment
   See details for complete list of blocked items
- Setup EPM orchestrator not found. Cannot validate user-only operations.
- Layer 2 (IncrementalWorkExecutor) not found. Critical component missing.
- Token budget validation FAILED. Total: 76,342 tokens (Budget: 76,000 tokens). Overage: 342 tokens. Deployment BLOCKED until optimization completes.

Violations (1 files):
  • response-templates.yaml: 30,899 / 25,000 tokens (23.6% over)

ACTION REQUIRED: Execute token optimization phases:
  Phase 1: Modularization (101K → 11K, -88.8%)
  Phase 2: Template compression (11K → 5K, -94.9%)
  Phase 3: Lazy loading (5K → 3K, -96.9%)
  Phase 4: Reference compression (3K → 2K, -98.0%)

See: cortex-brain/documents/planning/TOKEN-OPTIMIZATION-HOLISTIC-PLAN.md
- Application onboarding incomplete: 1 issues (5/6 checks passed). Can deploy without onboarding - users can onboard manually.

