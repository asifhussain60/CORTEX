"""
Update wiring.yaml with generated adapter references (Phase 2B)

Adds mcp_adapter fields to 16 orchestrators.
"""

import yaml
import re

# Adapter mappings
ADAPTER_MAPPINGS = {
    'PhaseExecutor': 'PhaseExecutorAdapter',
    'AutonomousExecutionEngine': 'AutonomousExecutionEngineAdapter',
    'OrchestratorEventBus': 'OrchestratorEventBusAdapter',
    'InteractionOrchestratorEnhancement': 'InteractionOrchestratorEnhancementAdapter',
    'FuzzyIntentMatcher': 'FuzzyIntentMatcherAdapter',
    'ComprehensionSession': 'ComprehensionSessionAdapter',
    'DoRApprovalGate': 'DoRApprovalGateAdapter',
    'ChallengeEngine': 'ChallengeEngineAdapter',
    'EducationalOrchestrator': 'EducationalOrchestratorAdapter',
    'DuplicationDetector': 'DuplicationDetectorAdapter',
    'RecommendationGate': 'RecommendationGateAdapter',
    'VacuumOrchestrator': 'VacuumOrchestratorAdapter',
    'InstrumentationOrchestrator': 'InstrumentationOrchestratorAdapter',
    'DebuggingOrchestrator': 'DebuggingOrchestratorAdapter',
    'OrchestratorVisibility': 'OrchestratorVisibilityAdapter',
    'DigestEnhancementOrchestrator': 'DigestEnhancementOrchestratorAdapter',
}

def main():
    """Update wiring.yaml with adapter references."""
    wiring_path = 'cortex/wiring/specifications/wiring.yaml'
    
    # Read file
    with open(wiring_path, 'r') as f:
        content = f.read()
    
    # Load YAML to track structure
    spec = yaml.safe_load(content)
    
    # For each orchestrator, find and add mcp_adapter field
    updates_made = 0
    
    for orch_name, adapter_name in ADAPTER_MAPPINGS.items():
        # Pattern: find orchestrator entry and add mcp_adapter after health_check
        pattern = rf'(- name: "{orch_name}".*?health_check: ".*?")'
        
        def add_adapter(match):
            nonlocal updates_made
            original = match.group(1)
            if 'mcp_adapter:' not in original:
                updates_made += 1
                return f'{original}\n      mcp_adapter: "{adapter_name}"'
            return original
        
        content = re.sub(pattern, add_adapter, content, flags=re.DOTALL)
    
    # Write back
    with open(wiring_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Updated {updates_made} orchestrators in {wiring_path}")
    
    # Verify
    spec = yaml.safe_load(open(wiring_path))
    total_with_adapter = 0
    for category in ['core', 'domain', 'support']:
        if category in spec.get('orchestrators', {}):
            for orch in spec['orchestrators'][category]:
                if 'mcp_adapter' in orch:
                    total_with_adapter += 1
    
    print(f"✅ Verification: {total_with_adapter}/43 orchestrators now have mcp_adapter")
    print(f"✅ Coverage: {total_with_adapter/43*100:.1f}%")

if __name__ == "__main__":
    main()
