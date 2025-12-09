"""
Fix all test issues in test_dashboard_integration.py
Updates container IDs and tab names to match actual HTML
"""

import re

def fix_test_file():
    filepath = r"c:\PROJECTS\CORTEX\tests\dashboard\e2e\test_dashboard_integration.py"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix parametrize decorator
    old_param = '''@pytest.mark.parametrize("tab_index,container_id,tab_name", [
        (0, "executive-container", "Executive Summary"),
        (1, "overview-container", "Overview"),
        (2, "tech-stack-container", "Tech Stack"),
        (3, "security-container", "Security Assessment"),
        (4, "use-cases-container", "Use Cases"),
        (5, "recommendations-container", "Recommendations"),
        (6, "architecture-container", "Architecture"),
        (7, "code-organization-container", "Code Organization"),
        (8, "vendors-container", "Dependencies"),
        (9, "engineering-container", "Engineering Onboarding")
    ])'''
    
    new_param = '''@pytest.mark.parametrize("tab_index,container_id,tab_name", [
        (0, "executive-container", "Executive Summary"),
        (1, "overview-container", "System Overview"),
        (2, "tech-stack-container", "Tech Stack"),
        (3, "security-container", "Security"),
        (4, "use-cases-container", "Use Cases"),
        (5, "recommendations-container", "Recommendations"),
        (6, "architecture-container", "Architecture"),
        (7, "code-org-container", "Code Organization"),
        (8, "vendors-container", "Dependencies"),
        (9, "engineering-container", "Onboarding")
    ])'''
    
    content = content.replace(old_param, new_param)
    
    # Fix all other occurrences of code-organization-container
    content = content.replace('"code-organization-container"', '"code-org-container"')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fixed container IDs and tab names")

if __name__ == "__main__":
    fix_test_file()
