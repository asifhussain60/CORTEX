"""
Debug script to test documentation validation logic in isolation.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Test the exact logic from system_alignment_orchestrator
project_root = Path(__file__).parent

def check_guide_file_exists(feature_name: str, feature_type: str) -> bool:
    """
    Check if guide file exists for a feature.
    """
    import re
    
    # Remove common suffixes
    name_base = feature_name.replace("Orchestrator", "").replace("Agent", "").replace("Module", "")
    
    # Convert CamelCase to kebab-case (handle acronyms specially)
    name_base = name_base.replace("TDD", "Tdd").replace("API", "Api").replace("HTTP", "Http")
    kebab_name = re.sub(r'(?<!^)(?=[A-Z])', '-', name_base).lower()
    
    # Construct guide filename
    guide_name = f"{kebab_name}-{feature_type}-guide.md"
    guide_path = project_root / ".github" / "prompts" / "modules" / guide_name
    
    exists = guide_path.exists()
    
    print(f"\nChecking: {feature_name}")
    print(f"  Name base: {name_base}")
    print(f"  Kebab name: {kebab_name}")
    print(f"  Guide name: {guide_name}")
    print(f"  Guide path: {guide_path}")
    print(f"  Exists: {exists}")
    
    # Check if it's not just a stub (has substantial content)
    if exists:
        try:
            content = guide_path.read_text(encoding='utf-8')
            is_substantial = len(content) > 1000 and '[Feature 1]' not in content
            print(f"  Content length: {len(content)}")
            print(f"  Is substantial: {is_substantial}")
            return is_substantial
        except Exception as e:
            print(f"  Error reading: {e}")
            return False
    
    return False

# Now test with actual orchestrator discovery
from src.discovery.orchestrator_scanner import OrchestratorScanner

scanner = OrchestratorScanner(project_root)
orchestrators = scanner.discover()

print(f"\n=== Discovered {len(orchestrators)} orchestrators ===\n")

# Focus on TDDWorkflowOrchestrator
if "TDDWorkflowOrchestrator" in orchestrators:
    metadata = orchestrators["TDDWorkflowOrchestrator"]
    print(f"TDDWorkflowOrchestrator metadata:")
    print(f"  has_docstring: {metadata.get('has_docstring')}")
    print(f"  docstring: {metadata.get('docstring')[:100] if metadata.get('docstring') else None}...")
    
    # Test guide file check
    has_guide = check_guide_file_exists("TDDWorkflowOrchestrator", "orchestrator")
    print(f"\n  Guide file check result: {has_guide}")
    print(f"  Final documented status: {metadata.get('has_docstring')} AND {has_guide} = {metadata.get('has_docstring') and has_guide}")
else:
    print("TDDWorkflowOrchestrator NOT FOUND in discovered orchestrators!")

# Also test a few others
for name in ["LintValidationOrchestrator", "SessionCompletionOrchestrator", "GitCheckpointOrchestrator"]:
    if name in orchestrators:
        metadata = orchestrators[name]
        has_guide = check_guide_file_exists(name, "orchestrator")
        print(f"\n{name}: has_docstring={metadata.get('has_docstring')}, has_guide={has_guide}, documented={metadata.get('has_docstring') and has_guide}")
