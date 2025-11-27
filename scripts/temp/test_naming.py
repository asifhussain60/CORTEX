import re
from pathlib import Path

def test_naming(feature_name, feature_type):
    name_base = feature_name.replace("Orchestrator", "").replace("Agent", "").replace("Module", "")
    print(f"Feature: {feature_name}")
    print(f"Name base: {name_base}")
    
    # Handle acronyms
    name_base = name_base.replace("TDD", "Tdd").replace("API", "Api").replace("HTTP", "Http")
    print(f"Acronym fix: {name_base}")
    
    # Convert CamelCase to kebab-case
    kebab_name = re.sub(r'(?<!^)(?=[A-Z])', '-', name_base).lower()
    print(f"Kebab: {kebab_name}")
    
    guide_name = f"{kebab_name}-{feature_type}-guide.md"
    print(f"Guide filename: {guide_name}")
    
    guide_path = Path("d:/PROJECTS/CORTEX/.github/prompts/modules") / guide_name
    print(f"Exists: {guide_path.exists()}")
    
    if guide_path.exists():
        content = guide_path.read_text(encoding='utf-8')
        print(f"Length: {len(content)}")
        print(f"Has placeholders: {'[Feature 1]' in content}")
    print()

# Test cases
test_naming("TDDWorkflowOrchestrator", "orchestrator")
test_naming("LintValidationOrchestrator", "orchestrator")
test_naming("SessionCompletionOrchestrator", "orchestrator")
test_naming("UpgradeOrchestrator", "orchestrator")
test_naming("GitCheckpointOrchestrator", "orchestrator")
