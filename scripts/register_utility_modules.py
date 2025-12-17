"""
Register Utility Modules to cortex-operations.yaml

Registers the 32 utility modules that are missing from cortex-operations.yaml.
These are internal helper utilities under src/operations/modules/*.
"""

import yaml
from pathlib import Path
from datetime import datetime

# List of 32 utility modules to register
UTILITY_MODULES = [
    {'category': 'admin', 'module': 'align_utility', 'path': 'admin/align_utility'},
    {'category': 'admin', 'module': 'healthcheck_utility', 'path': 'admin/healthcheck_utility'},
    {'category': 'ado', 'module': 'ado_utility', 'path': 'ado/ado_utility'},
    {'category': 'analysis', 'module': 'analysis_utility', 'path': 'analysis/analysis_utility'},
    {'category': 'checkpoints', 'module': 'checkpoint_utility', 'path': 'checkpoints/checkpoint_utility'},
    {'category': 'cleanup', 'module': 'cleanup_utility', 'path': 'cleanup/cleanup_utility'},
    {'category': 'deploy', 'module': 'deploy_utility', 'path': 'deploy/deploy_utility'},
    {'category': 'epm', 'module': 'setup_epm_utility', 'path': 'epm/setup_epm_utility'},
    {'category': 'estimation', 'module': 'swagger_estimation_utility', 'path': 'estimation/swagger_estimation_utility'},
    {'category': 'git', 'module': 'commit_utility', 'path': 'git/commit_utility'},
    {'category': 'git', 'module': 'git_checkpoint_utility', 'path': 'git/git_checkpoint_utility'},
    {'category': 'git', 'module': 'rollback_utility', 'path': 'git/rollback_utility'},
    {'category': 'health', 'module': 'health_utility', 'path': 'health/health_utility'},
    {'category': 'incremental', 'module': 'base_incremental_utility', 'path': 'incremental/base_incremental_utility'},
    {'category': 'lint', 'module': 'lint_utility', 'path': 'lint/lint_utility'},
    {'category': 'metrics', 'module': 'metrics_utility', 'path': 'metrics/metrics_utility'},
    {'category': 'onboarding', 'module': 'onboarding_utility', 'path': 'onboarding/onboarding_utility'},
    {'category': 'phase8', 'module': 'phase8_utility', 'path': 'phase8/phase8_utility'},
    {'category': 'planning', 'module': 'migration_utility', 'path': 'planning/migration_utility'},
    {'category': 'planning', 'module': 'planning_utility', 'path': 'planning/planning_utility'},
    {'category': 'pr', 'module': 'pr_context_utility', 'path': 'pr/pr_context_utility'},
    {'category': 'rca', 'module': 'rca_utility', 'path': 'rca/rca_utility'},
    {'category': 'realignment', 'module': 'realignment_utility', 'path': 'realignment/realignment_utility'},
    {'category': 'reporting', 'module': 'dashboard_utility', 'path': 'reporting/dashboard_utility'},
    {'category': 'review', 'module': 'review_utility', 'path': 'review/review_utility'},
    {'category': 'routing', 'module': 'unified_entry_point_utility', 'path': 'routing/unified_entry_point_utility'},
    {'category': 'setup', 'module': 'master_setup_utility', 'path': 'setup/master_setup_utility'},
    {'category': 'setup', 'module': 'setup_utility', 'path': 'setup/setup_utility'},
    {'category': 'tdd', 'module': 'tdd_utility', 'path': 'tdd/tdd_utility'},
    {'category': 'upgrade', 'module': 'upgrade_utility', 'path': 'upgrade/upgrade_utility'},
    {'category': 'ux_enhancement', 'module': 'ux_enhancement_utility', 'path': 'ux_enhancement/ux_enhancement_utility'},
    {'category': 'validation', 'module': 'session_utility', 'path': 'validation/session_utility'},
]


def register_utility_modules():
    """Register all utility modules to cortex-operations.yaml."""
    
    cortex_root = Path(__file__).resolve().parents[1]
    operations_yaml_path = cortex_root / "cortex-brain" / "manifests" / "operations" / "cortex-operations.yaml"
    
    print(f"Loading: {operations_yaml_path}")
    
    # Load existing operations.yaml
    with open(operations_yaml_path, 'r', encoding='utf-8') as f:
        operations_data = yaml.safe_load(f) or {}
    
    if 'operations' not in operations_data:
        operations_data['operations'] = {}
    
    # Register each utility module
    registered_count = 0
    skipped_count = 0
    
    for util in UTILITY_MODULES:
        module_name = util['module']
        
        # Check if already registered
        if module_name in operations_data['operations']:
            print(f"⏭️  Skipped: {module_name} (already registered)")
            skipped_count += 1
            continue
        
        # Create registration entry
        operations_data['operations'][module_name] = {
            'display_name': module_name.replace('_', ' ').title(),
            'description': f"Internal utility module for {util['category']} operations",
            'deployment_tier': 'admin_only',
            'natural_language': [f"internal {util['category']} utility"],
            'category': util['category'],
            'version': '1.0.0',
            'author': 'Asif Hussain',
            'modules': [f"src.operations.modules.{util['path']}"]
        }
        
        print(f"✅ Registered: {module_name}")
        registered_count += 1
    
    # Save updated operations.yaml
    with open(operations_yaml_path, 'w', encoding='utf-8') as f:
        yaml.dump(operations_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print(f"\n{'='*70}")
    print(f"✅ Registration Complete!")
    print(f"   Registered: {registered_count}")
    print(f"   Skipped: {skipped_count}")
    print(f"   Total: {len(UTILITY_MODULES)}")
    print(f"{'='*70}")


if __name__ == "__main__":
    register_utility_modules()
