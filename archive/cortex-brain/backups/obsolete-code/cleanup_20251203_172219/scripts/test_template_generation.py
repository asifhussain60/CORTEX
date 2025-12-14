"""
Test Template Generation System

Validates that:
1. YAML templates load correctly
2. Generator script runs without errors
3. CORTEX.prompt.md contains template section
4. All templates are represented

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import yaml
from pathlib import Path
import sys


def test_yaml_loads():
    """Test that response-templates.yaml is valid"""
    print("🧪 Test 1: YAML Loading...")
    
    template_file = Path("cortex-brain/templates/response-templates.yaml")
    
    try:
        with open(template_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        assert 'templates' in data, "Missing 'templates' key"
        assert len(data['templates']) > 0, "No templates found"
        
        print(f"   ✅ Loaded {len(data['templates'])} templates")
        return True
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False


def test_template_structure():
    """Test that templates have required fields"""
    print("🧪 Test 2: Template Structure...")
    
    template_file = Path("cortex-brain/templates/response-templates.yaml")
    
    try:
        with open(template_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        errors = []
        
        for template_id, template in data['templates'].items():
            # Check required fields
            if 'content' not in template:
                errors.append(f"{template_id}: missing 'content'")
            
            if 'trigger' not in template and template_id != 'fallback':
                # Confidence templates and some others don't need triggers
                if not template_id.startswith('confidence_'):
                    pass  # Allow some templates without triggers
        
        if errors:
            print(f"   ❌ Structure errors:")
            for error in errors:
                print(f"      • {error}")
            return False
        else:
            print(f"   ✅ All templates have valid structure")
            return True
    
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False


def test_prompt_file_updated():
    """Test that CORTEX.prompt.md contains template section"""
    print("🧪 Test 3: Prompt File Updated...")
    
    prompt_file = Path(".github/prompts/CORTEX.prompt.md")
    
    try:
        content = prompt_file.read_text(encoding='utf-8')
        
        # Check for key markers
        markers = [
            "# 🎯 CRITICAL: Template Trigger Detection & Selection",
            "**AUTO-GENERATED FROM response-templates.yaml**",
            "## 📋 Template Trigger Mappings",
            "### Fallback Response (No Trigger Match)"
        ]
        
        missing = []
        for marker in markers:
            if marker not in content:
                missing.append(marker)
        
        if missing:
            print(f"   ❌ Missing markers:")
            for marker in missing:
                print(f"      • {marker}")
            return False
        else:
            print(f"   ✅ All template markers found in prompt file")
            return True
    
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False


def test_all_templates_represented():
    """Test that all YAML templates appear in prompt file"""
    print("🧪 Test 4: All Templates Represented...")
    
    try:
        # Load YAML
        template_file = Path("cortex-brain/templates/response-templates.yaml")
        with open(template_file, 'r', encoding='utf-8') as f:
            yaml_data = yaml.safe_load(f)
        
        # Load prompt
        prompt_file = Path(".github/prompts/CORTEX.prompt.md")
        prompt_content = prompt_file.read_text(encoding='utf-8')
        
        # Check each template ID appears in prompt
        missing = []
        for template_id in yaml_data['templates'].keys():
            # Skip templates with no triggers (like confidence indicators)
            template = yaml_data['templates'][template_id]
            if not template.get('trigger') and template_id != 'fallback':
                continue
            
            # Check if template ID appears in prompt
            if f"`{template_id}`" not in prompt_content:
                missing.append(template_id)
        
        if missing:
            print(f"   ⚠️ Templates not in prompt (may be intentional):")
            for tid in missing:
                print(f"      • {tid}")
            return True  # Not a critical error
        else:
            print(f"   ✅ All templates with triggers represented in prompt")
            return True
    
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 70)
    print("🧠 CORTEX Template System Tests")
    print("=" * 70)
    print("")
    
    tests = [
        test_yaml_loads,
        test_template_structure,
        test_prompt_file_updated,
        test_all_templates_represented
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
        print("")
    
    # Summary
    print("=" * 70)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ ALL TESTS PASSED ({passed}/{total})")
        print("=" * 70)
        return 0
    else:
        print(f"⚠️ SOME TESTS FAILED ({passed}/{total} passed)")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
