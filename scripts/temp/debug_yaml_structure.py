"""Debug YAML loading and entry_points structure."""
import yaml
from pathlib import Path

cortex_root = Path(__file__).parent
response_templates_path = cortex_root / "cortex-brain" / "response-templates.yaml"

with open(response_templates_path, 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f)

templates = data.get('templates', {})

critical_templates = [
    'holistic_cleanup',
    'setup_epm',
    'ado_work_item',
    'demo_system',
    'unified_entry_point'
]

print("Checking template structure:\n")
for template_name in critical_templates:
    template = templates.get(template_name)
    if not template:
        print(f"❌ {template_name}: NOT FOUND")
        continue
    
    print(f"✓ {template_name}:")
    print(f"  name: {template.get('name')}")
    print(f"  expected_orchestrator: {template.get('expected_orchestrator')}")
    print(f"  triggers: {template.get('triggers', [])[:2]}...")
    print()

# Show how WiringValidator expects entry_points
print("\n" + "="*60)
print("How entry_points dict should look:")
print("="*60)

# The wiring validator expects:
# entry_points = {
#     "cleanup": {"expected_orchestrator": "HolisticCleanupOrchestrator", ...},
#     "clean up": {"expected_orchestrator": "HolisticCleanupOrchestrator", ...},
# }

print("\nBUT we have:")
print("templates = {")
print("    'holistic_cleanup': {")
print("        'expected_orchestrator': '...',")
print("        'triggers': ['cleanup', 'clean up', ...]")
print("    }")
print("}")

print("\nThe issue: WiringValidator expects trigger → metadata mapping")
print("We have: template_name → metadata mapping")
print("\nSolution: Transform templates dict to expand triggers into entry_points")
