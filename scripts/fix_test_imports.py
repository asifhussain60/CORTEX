#!/usr/bin/env python3
"""
Fix Test Imports After Redirect Stub Removal

Updates test imports to point to correct cortex_intelligence submodules
after redirect stubs were deleted.

Author: CORTEX Framework
Phase: 91.8 - Production Readiness
"""

from pathlib import Path
import re

# Mapping of classes/functions to their correct module paths
IMPORT_MAPPINGS = {
    # Hallucination Prevention
    "HallucinationDetector": "cortex_intelligence.memory.tier2_adaptive.hallucination_prevention.detection_recovery",
    "VisionMutation": "cortex_intelligence.memory.tier2_adaptive.hallucination_prevention.mutation_tracking",
    "ConfidenceScoring": "cortex_intelligence.memory.tier2_adaptive.hallucination_prevention.confidence_scoring",
    "BehavioralBoundary": "cortex_intelligence.memory.tier2_adaptive.hallucination_prevention.boundary_rules",
    "ExecutionSandbox": "cortex_intelligence.memory.tier2_adaptive.hallucination_prevention.execution_sandbox",
    "IntentCanonicalizer": "cortex_intelligence.memory.tier2_adaptive.hallucination_prevention.canonicalization_engine",
    
    # Governance
    "PIIDetector": "cortex_intelligence.memory.tier2_adaptive.governance.pii_detection",
    "ReasoningTrace": "cortex_intelligence.memory.tier2_adaptive.governance.reasoning_trace",
    "AuditPerformanceSLA": "cortex_intelligence.memory.tier2_adaptive.governance.audit_performance_sla",
    "SLAStatus": "cortex_intelligence.memory.tier2_adaptive.governance.audit_performance_sla",
    "CostTracker": "cortex_intelligence.memory.tier2_adaptive.governance.cost_tracking",
    "ScopeCreepDetector": "cortex_intelligence.memory.tier2_adaptive.governance.scope_creep",
    "AuditImmutability": "cortex_intelligence.memory.tier2_adaptive.governance.audit_immutability",
    "SLATracker": "cortex_intelligence.memory.tier2_adaptive.governance.sla_tracking",
    "SLAComplianceStatus": "cortex_intelligence.memory.tier2_adaptive.governance.sla_tracking",
    "PromptInjectionSanitizer": "cortex_intelligence.memory.tier2_adaptive.governance.prompt_injection_sanitizer",
    "RuntimeResilience": "cortex_intelligence.memory.tier2_adaptive.governance.runtime_resilience",
    "OutputDeterminism": "cortex_intelligence.memory.tier2_adaptive.governance.output_determinism",
    "ToolDescriptionValidator": "cortex_intelligence.memory.tier2_adaptive.governance.tool_description_validator",
    "CoreBaselineValidator": "cortex_intelligence.memory.tier2_adaptive.governance.core_030_baselines",
    "DataRetentionManager": "cortex_intelligence.memory.tier2_adaptive.governance.data_retention",
    "StakeholderNotifier": "cortex_intelligence.memory.tier2_adaptive.governance.stakeholder_notification",
}


def fix_test_imports(test_file: Path) -> bool:
    """Fix imports in a single test file.
    
    Args:
        test_file: Path to test file
        
    Returns:
        True if file was modified
    """
    try:
        content = test_file.read_text()
        original_content = content
        
        # Find import blocks that import from cortex_intelligence.memory.tier2_adaptive
        pattern = r'from cortex_intelligence\.tier2 import \(([\s\S]*?)\)'
        matches = list(re.finditer(pattern, content))
        
        if not matches:
            # Try single-line imports
            pattern = r'from cortex_intelligence\.tier2 import (.+)'
            matches = list(re.finditer(pattern, content))
        
        for match in matches:
            old_import = match.group(0)
            imports_str = match.group(1)
            
            # Parse imported names
            imported_names = [
                name.strip().rstrip(',')
                for name in imports_str.split('\n')
                if name.strip() and not name.strip().startswith('#')
            ]
            imported_names = [n for n in imported_names if n]
            
            # Group by target module
            module_imports = {}
            for name in imported_names:
                if name in IMPORT_MAPPINGS:
                    target_module = IMPORT_MAPPINGS[name]
                    if target_module not in module_imports:
                        module_imports[target_module] = []
                    module_imports[target_module].append(name)
            
            # Generate new import statements
            new_imports = []
            for module, names in sorted(module_imports.items()):
                if len(names) == 1:
                    new_imports.append(f"from {module} import {names[0]}")
                else:
                    names_str = ', '.join(names)
                    new_imports.append(f"from {module} import {names_str}")
            
            if new_imports:
                new_import_block = '\n'.join(new_imports)
                content = content.replace(old_import, new_import_block)
        
        if content != original_content:
            test_file.write_text(content)
            return True
        
        return False
        
    except Exception as e:
        print(f"  Error processing {test_file}: {e}")
        return False


def main() -> None:
    """Main execution function."""
    workspace = Path.cwd()
    
    print("🔧 Fixing test imports after redirect stub removal\n")
    
    files_fixed = 0
    files_skipped = 0
    
    for test_file in workspace.rglob('tests/**/*.py'):
        if test_file.name.startswith('test_'):
            if fix_test_imports(test_file):
                files_fixed += 1
                print(f"✓ Fixed {test_file.relative_to(workspace)}")
            else:
                files_skipped += 1
    
    print(f"\n✅ Complete!")
    print(f"  Fixed: {files_fixed} files")
    print(f"  Skipped: {files_skipped} files (no changes needed)")


if __name__ == "__main__":
    main()
