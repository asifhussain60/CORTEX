"""Generate OrchestratorSpec batch from wiring.yaml.

AC_START: AC-WAVE2-S2-001
Description: Extract specs for 60 orchestrators from GitBackedRegistry
Authority: WAVE-2 Stage 2
"""

import yaml
from pathlib import Path
from typing import List, Dict, Any

def load_wiring_spec() -> Dict[str, Any]:
    """Load wiring.yaml specification."""
    wiring_file = Path("cortex/wiring/specifications/wiring.yaml")
    with open(wiring_file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def extract_orchestrator_specs(spec: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract orchestrator specifications from wiring.yaml.
    
    Returns:
        List of OrchestratorSpec-compatible dicts
    """
    specs = []
    orchestrators = spec.get('orchestrators', {})
    
    for category in ['core', 'domain', 'support']:
        category_orchs = orchestrators.get(category, [])
        for orch in category_orchs:
            spec_dict = {
                'name': orch['name'],
                'module': orch['module'],
                'class_name': orch['class'],
                'tier': orch.get('tier', 'unknown'),
                'category': category,
                'capabilities': orch.get('capabilities', []),
                'dependencies': orch.get('dependencies', []),
                'integration_points': orch.get('integration_points', {}),
                'stages': orch.get('stages', []),
                'hooks': orch.get('hooks', {}),
            }
            specs.append(spec_dict)
    
    return specs

def main():
    """Generate orchestrator specs and save to JSON."""
    spec = load_wiring_spec()
    specs = extract_orchestrator_specs(spec)
    
    print(f"Extracted {len(specs)} orchestrator specifications")
    print(f"\nCategories:")
    print(f"  Core: {len([s for s in specs if s['category'] == 'core'])}")
    print(f"  Domain: {len([s for s in specs if s['category'] == 'domain'])}")
    print(f"  Support: {len([s for s in specs if s['category'] == 'support'])}")
    
    # Save to JSON for adapter consumption
    import json
    output_file = Path("cortex-registry/_cortex-master/orchestrator_specs.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(specs, f, indent=2)
    
    print(f"\n✅ Saved specs to {output_file}")
    
    return specs

if __name__ == "__main__":
    specs = main()

# AC_COMPLETE: AC-WAVE2-S2-001 ✅
