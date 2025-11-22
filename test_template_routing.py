"""
Test script to verify that different requests trigger different response templates.

This tests the template routing system to ensure it's not always falling back to the default template.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from response_templates.template_loader import TemplateLoader
from response_templates.template_renderer import TemplateRenderer
from entry_point.response_formatter import ResponseFormatter

def test_template_routing():
    """Test that different triggers route to different templates."""
    
    # Initialize components
    template_file = Path(__file__).parent / "cortex-brain" / "response-templates.yaml"
    
    if not template_file.exists():
        print(f"❌ Template file not found: {template_file}")
        return False
    
    print(f"✓ Template file found: {template_file}")
    
    loader = TemplateLoader(template_file)
    renderer = TemplateRenderer()
    formatter = ResponseFormatter(verbosity="concise")
    formatter.template_loader = loader
    formatter.template_renderer = renderer
    
    # Load templates
    loader.load_templates()
    all_templates = loader.list_templates()
    print(f"✓ Loaded {len(all_templates)} templates\n")
    
    # Test cases: request text -> expected template
    test_cases = [
        {
            "request": "help",
            "expected_template": "help_table",
            "should_contain": "CORTEX"
        },
        {
            "request": "status",
            "expected_template": "status_check",
            "should_contain": "CORTEX"
        },
        {
            "request": "plan a feature",
            "expected_template": "work_planner_success",
            "should_contain": "Feature Planning"
        },
        {
            "request": "export brain",
            "expected_template": "brain_export_guide",
            "should_contain": "Brain Implants - Export"
        },
        {
            "request": "import brain",
            "expected_template": "brain_import_guide",
            "should_contain": "Brain Implants - Import"
        },
        {
            "request": "enhance existing",
            "expected_template": "enhance_existing",
            "should_contain": "Enhancement Analysis"
        },
        {
            "request": "something random",
            "expected_template": "fallback",
            "should_contain": "CORTEX Response"
        }
    ]
    
    results = []
    
    print("=" * 80)
    print("TEMPLATE ROUTING TESTS")
    print("=" * 80)
    print()
    
    for i, test in enumerate(test_cases, 1):
        request = test["request"]
        expected_template = test["expected_template"]
        should_contain = test["should_contain"]
        
        print(f"Test {i}: '{request}'")
        print(f"  Expected template: {expected_template}")
        
        # Find template by trigger
        found_template = loader.find_by_trigger(request)
        
        if found_template:
            template_id = found_template.template_id
            print(f"  ✓ Found template: {template_id}")
            
            # Render template
            rendered = renderer.render(found_template, {}, "concise")
            
            # Check if expected content is present
            if should_contain in rendered:
                print(f"  ✓ Contains expected content: '{should_contain}'")
                status = "✓ PASS"
            else:
                print(f"  ✗ Missing expected content: '{should_contain}'")
                print(f"    First 200 chars: {rendered[:200]}")
                status = "✗ FAIL (wrong content)"
            
            # Check if correct template was used
            if template_id == expected_template:
                print(f"  {status} - Correct template used")
                results.append(True)
            else:
                print(f"  ✗ FAIL - Wrong template (got {template_id}, expected {expected_template})")
                results.append(False)
        else:
            print(f"  ✗ No template found - using fallback")
            # Try fallback
            fallback_template = loader.load_template("fallback")
            if fallback_template:
                rendered = renderer.render(fallback_template, {}, "concise")
                if should_contain in rendered:
                    if expected_template == "fallback":
                        print(f"  ✓ PASS - Correctly using fallback")
                        results.append(True)
                    else:
                        print(f"  ✗ FAIL - Should not use fallback for '{request}'")
                        results.append(False)
                else:
                    print(f"  ✗ FAIL - Fallback missing expected content")
                    results.append(False)
            else:
                print(f"  ✗ FAIL - No fallback template found")
                results.append(False)
        
        print()
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    total = len(results)
    passed = sum(results)
    failed = total - passed
    
    print(f"Total tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Pass rate: {(passed/total)*100:.1f}%")
    
    if failed == 0:
        print("\n✓ All tests passed! Template routing is working correctly.")
        return True
    else:
        print(f"\n✗ {failed} test(s) failed. Template routing needs attention.")
        return False

def inspect_triggers():
    """Inspect what triggers are registered in the template file."""
    
    template_file = Path(__file__).parent / "cortex-brain" / "response-templates.yaml"
    loader = TemplateLoader(template_file)
    loader.load_templates()
    
    print("=" * 80)
    print("REGISTERED TRIGGERS")
    print("=" * 80)
    print()
    
    all_templates = loader.list_templates()
    
    for template in sorted(all_templates, key=lambda t: t.template_id):
        print(f"Template: {template.template_id}")
        if template.triggers:
            for trigger in template.triggers:
                print(f"  - {trigger}")
        else:
            print(f"  (no triggers)")
        print()

if __name__ == "__main__":
    print("CORTEX Template Routing Test")
    print("=" * 80)
    print()
    
    # First, inspect what triggers are available
    inspect_triggers()
    
    print()
    print()
    
    # Then run the routing tests
    success = test_template_routing()
    
    sys.exit(0 if success else 1)
