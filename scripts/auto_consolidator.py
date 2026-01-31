#!/usr/bin/env python3
"""
Automated CORE-035 Consolidator
Fixes TRUE duplicates by updating imports to canonical locations.

Author: CORTEX Architect
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple

# Canonical locations for duplicated classes
CANONICAL_LOCATIONS = {
    # Enum duplicates -> canonical_enums.py
    "CircuitBreakerState": ("cortex.models.canonical_enums", "cortex/models/canonical_enums.py"),
    "HealthStatus": ("cortex.models.canonical_enums", "cortex/models/canonical_enums.py"),
    "RiskLevel": ("cortex.models.canonical_enums", "cortex/models/canonical_enums.py"),
    
    # Gateway duplicates -> canonical implementation
    "GateDecision": ("cortex.core.orchestrator.stage_2_5_gate", "cortex/core/orchestrator/stage_2_5_gate.py"),
    
    # Challenge duplicates -> challenge_engine.py (canonical)
    "DisagreementType": ("cortex.orchestrators.core.challenge_engine", "cortex/orchestrators/core/challenge_engine.py"),
    
    # Onboarding duplicates -> unified_onboarding.py (canonical)
    "JourneyState": ("cortex.config.unified_onboarding", "cortex/config/unified_onboarding.py"),
    
    # Response duplicates -> unified_response_composer.py (canonical)
    "FormattingProfile": ("cortex.orchestrators.response.unified_response_composer", "cortex/orchestrators/response/unified_response_composer.py"),
    "QualityMetricType": ("cortex.orchestrators.response.unified_response_composer", "cortex/orchestrators/response/unified_response_composer.py"),
    
    # Multimodal duplicates -> canonical
    "InputModality": ("cortex.intent_router.multimodal_processor", "cortex/intent_router/multimodal_processor.py"),
    
    # Scenario duplicates -> canonical
    "ScenarioStatus": ("cortex.devx.scenario_library", "cortex/devx/scenario_library.py"),
    
    # LENS duplicates -> canonical
    "ResponseFormat": ("cortex.brain.core.intent.lens_response_formatter", "cortex/brain/core/intent/lens_response_formatter.py"),
    "SeverityColor": ("cortex.brain.core.intent.lens_response_formatter", "cortex/brain/core/intent/lens_response_formatter.py"),
    
    # Execution duplicates -> canonical
    "ExecutionState": ("cortex.mcp.executor", "cortex/mcp/executor.py"),
    
    # MD Organizer duplicates -> canonical
    "MDFileCategory": ("cortex.brain.tier1.orchestrators.cleaners.md_organizer", "cortex/brain/tier1/orchestrators/cleaners/md_organizer.py"),
}

# Files to update (duplicates that should import from canonical)
DUPLICATE_FILES = {
    "CircuitBreakerState": [
        "cortex/brain/tier2/resilience/__init__.py",
    ],
    "HealthStatus": [
        "cortex/api/health_endpoints.py",
    ],
    "RiskLevel": [
        "cortex/visualization/renderers/impact_analysis_renderer.py",
        "cortex/orchestrators/core/git_analysis_engine.py",
        "cortex/orchestrators/domain/enhanced_planning_orchestrator.py",
        "cortex/brain/domain_orchestrators/business/base.py",
    ],
    "GateDecision": [
        "cortex/orchestrators/core/stage_2_5_gate.py",
    ],
    "JourneyState": [
        "cortex/orchestrators/onboarding/orchestrator.py",
    ],
    "FormattingProfile": [
        "_workspaces/dashboard/multi_mode_formatter.py",
    ],
    "QualityMetricType": [
        "cortex/orchestrators/response/ux_optimizer.py",
    ],
    "InputModality": [
        "cortex/brain/intent_router/multimodal_processor.py",
    ],
    "ScenarioStatus": [
        "cortex/brain/devx/scenario_library.py",
    ],
    "ResponseFormat": [
        "_workspaces/dashboard/enhancements_lens_response_formatter.py",
    ],
    "SeverityColor": [
        "_workspaces/dashboard/enhancements_lens_response_formatter.py",
    ],
    "ExecutionState": [
        "cortex_brain/tier2/hallucination_prevention/execution_sandbox.py",
    ],
    "MDFileCategory": [
        "cortex_brain/tier1/orchestrators/cleaners/md_organizer.py",
    ],
}


def fix_duplicate(root_path: Path, class_name: str, duplicate_file: str):
    """Fix a duplicate by adding import from canonical location."""
    canonical_module, canonical_file = CANONICAL_LOCATIONS[class_name]
    filepath = root_path / duplicate_file
    
    if not filepath.exists():
        print(f"⚠️  Skipping {duplicate_file} (not found)")
        return False
    
    content = filepath.read_text()
    
    # Check if duplicate class definition exists
    pattern = rf"class {class_name}\([^)]*\):"
    if not re.search(pattern, content):
        print(f"⚠️  {class_name} not found in {duplicate_file}")
        return False
    
    # Add import at top (after other imports)
    import_line = f"from {canonical_module} import {class_name}\n"
    
    # Remove class definition (keep docstring if complex, or delete whole block)
    # For safety, we'll comment it out rather than delete
    updated_content = re.sub(
        rf"(class {class_name}\([^)]*\):.*?)(\n\nclass |\n\n@|\Z)",
        rf"# CONSOLIDATED: Import from {canonical_module}\n# \1\2",
        content,
        flags=re.DOTALL,
        count=1
    )
    
    if updated_content != content:
        filepath.write_text(updated_content)
        print(f"✅ Fixed {class_name} in {duplicate_file}")
        return True
    
    return False


def main():
    root = Path("/Users/asifhussain/PROJECTS/CORTEX")
    fixed_count = 0
    
    print("🔧 Starting automated CORE-035 consolidation...")
    print()
    
    for class_name, duplicate_files in DUPLICATE_FILES.items():
        if class_name not in CANONICAL_LOCATIONS:
            print(f"⚠️  No canonical location defined for {class_name}")
            continue
        
        print(f"📌 Consolidating {class_name}...")
        for dup_file in duplicate_files:
            if fix_duplicate(root, class_name, dup_file):
                fixed_count += 1
        print()
    
    print(f"\n✅ Fixed {fixed_count} duplicates!")
    return 0


if __name__ == "__main__":
    exit(main())
