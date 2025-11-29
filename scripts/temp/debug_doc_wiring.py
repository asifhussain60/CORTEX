"""Debug documentation and wiring validation logic."""
import sys
from pathlib import Path

cortex_root = Path(__file__).parent
sys.path.insert(0, str(cortex_root / "src"))

from discovery.orchestrator_scanner import OrchestratorScanner
from validation.wiring_validator import WiringValidator

project_root = cortex_root

# Initialize
scanner = OrchestratorScanner(project_root)
wiring_validator = WiringValidator(project_root)
orchestrators_dict = scanner.discover()

critical = [
    "HolisticCleanupOrchestrator",
    "SetupEPMOrchestrator",
    "ADOWorkItemOrchestrator",
    "DemoOrchestrator",
    "UnifiedEntryPointOrchestrator"
]

# Get entry points from response templates
response_templates_path = project_root / "cortex-brain" / "response-templates.yaml"
print(f"Response templates path: {response_templates_path}")
print(f"Exists: {response_templates_path.exists()}\n")

for name in critical:
    print(f"\n{'='*60}")
    print(f"{name}")
    print('='*60)
    
    # Get orchestrator metadata
    orch_info = orchestrators_dict.get(name)
    if not orch_info:
        print(f"❌ Not found in discovered orchestrators")
        continue
    
    print(f"✓ Module: {orch_info['module_path']}")
    print(f"✓ File: {orch_info['path']}")
    
    # Check docstring
    has_docstring = bool(orch_info.get('docstring', '').strip())
    print(f"\n📄 Docstring:")
    print(f"  Has docstring: {has_docstring}")
    if has_docstring:
        docstring = orch_info.get('docstring', '')
        print(f"  Length: {len(docstring)} chars")
        print(f"  Preview: {docstring[:100]}...")
    
    # Check guide file
    # Convert to kebab-case: HolisticCleanupOrchestrator → holistic-cleanup-orchestrator
    def to_kebab_case(name):
        result = []
        for i, char in enumerate(name):
            if char.isupper():
                if i > 0:
                    prev_lower = name[i - 1].islower()
                    next_lower = i + 1 < len(name) and name[i + 1].islower()
                    if prev_lower or next_lower:
                        result.append('-')
                result.append(char.lower())
            else:
                result.append(char)
        return ''.join(result)
    
    kebab_name = to_kebab_case(name)
    guide_filename = f"{kebab_name}-guide.md"
    guide_path = project_root / ".github" / "prompts" / "modules" / guide_filename
    
    print(f"\n📚 Guide File:")
    print(f"  Expected: {guide_filename}")
    print(f"  Path: {guide_path.relative_to(project_root)}")
    print(f"  Exists: {guide_path.exists()}")
    
    if guide_path.exists():
        content = guide_path.read_text(encoding='utf-8')
        print(f"  Size: {len(content)} chars")
        print(f"  Has placeholder: {'TODO' in content or 'PLACEHOLDER' in content}")
    
    # Check wiring
    print(f"\n🔌 Wiring Validation:")
    
    # Load entry points
    if response_templates_path.exists():
        import yaml
        with open(response_templates_path, 'r', encoding='utf-8') as f:
            templates = yaml.safe_load(f)
        
        entry_points = templates.get('response_templates', {})
        
        # Check if orchestrator is wired
        is_wired = wiring_validator.check_orchestrator_wired(name, entry_points)
        print(f"  Is wired: {is_wired}")
        
        # Debug: Show what the validator is looking for
        # Check entry_point_scanner.py
        scanner_path = project_root / "src" / "discovery" / "entry_point_scanner.py"
        if scanner_path.exists():
            scanner_content = scanner_path.read_text(encoding='utf-8')
            has_mapping = name in scanner_content
            print(f"  In entry_point_scanner.py: {has_mapping}")
            
            # Show relevant lines
            if has_mapping:
                for i, line in enumerate(scanner_content.splitlines(), 1):
                    if name in line:
                        print(f"    Line {i}: {line.strip()}")
    else:
        print(f"  ❌ response-templates.yaml not found")
    
    # Combined documentation check
    print(f"\n✅ Documentation Layer Status:")
    print(f"  Has docstring: {has_docstring}")
    print(f"  Has guide: {guide_path.exists()}")
    print(f"  Both required: {has_docstring and guide_path.exists()}")
