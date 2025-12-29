"""Quick fix for test file issues"""
import re

# Fix diagram tests
diagram_test_path = r"tests\test_diagram_regeneration_orchestrator.py"
with open(diagram_test_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix: partial completion should be 50% with 2/4 components
content = content.replace(
    'has_prompt=True, has_narrative=False,\n            has_mermaid=False, has_image=False\n        )\n        assert status.completion_percentage == 50\n        assert status.status == "partial"',
    'has_prompt=True, has_narrative=True,\n            has_mermaid=False, has_image=False\n        )\n        assert status.completion_percentage == 50\n        assert status.status == "partial"'
)

# Fix: statuses -> diagrams (multiple occurrences)
content = content.replace('statuses=', 'diagrams=')
content = content.replace('hasattr(report, \'statuses\')', 'hasattr(report, \'diagrams\')')
content = content.replace('report.complete_count', 'report.complete_diagrams')

with open(diagram_test_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed diagram tests")

# Fix onboarding tests
onboarding_test_path = r"tests\test_onboarding_orchestrator.py"
with open(onboarding_test_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix: process_mode_choice needs experience_level parameter
content = re.sub(
    r'orchestrator\.process_mode_choice\("(\d)"\)',
    r'orchestrator.process_mode_choice("\1", "junior")',
    content
)

# Fix: start_onboarding returns content not message/question
content = content.replace(
    'assert ("message" in result or "question" in result or "next_question" in result)',
    'assert "content" in result'
)

with open(onboarding_test_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed onboarding tests")
print("\nRun: pytest tests/test_diagram_regeneration_orchestrator.py tests/test_onboarding_orchestrator.py -v --cov")
