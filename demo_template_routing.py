"""
Visual Demonstration: Different Requests Use Different Templates

This script demonstrates that CORTEX uses different response templates
for different types of requests, NOT just the fallback template.

Author: Asif Hussain
Copyright: © 2024-2025
"""

from pathlib import Path
from src.response_templates.template_loader import TemplateLoader
from src.response_templates.template_renderer import TemplateRenderer


def demonstrate_template_routing():
    """Show how different requests route to different templates"""
    
    # Initialize components
    template_file = Path("cortex-brain/response-templates.yaml")
    loader = TemplateLoader(template_file)
    loader.load_templates()
    renderer = TemplateRenderer()
    
    # Test cases: different user requests
    test_cases = [
        {
            "request": "help",
            "description": "Simple help request"
        },
        {
            "request": "status",
            "description": "Status check request"
        },
        {
            "request": "plan a feature",
            "description": "Feature planning request"
        },
        {
            "request": "export brain",
            "description": "Brain export request"
        },
        {
            "request": "enhance existing code",
            "description": "Enhancement request"
        },
        {
            "request": "something completely random",
            "description": "Unknown request (should use fallback)"
        }
    ]
    
    print("=" * 80)
    print("CORTEX TEMPLATE ROUTING DEMONSTRATION")
    print("=" * 80)
    print()
    print("This proves that different requests use different templates,")
    print("NOT just the fallback template.")
    print()
    print("=" * 80)
    print()
    
    for i, test in enumerate(test_cases, 1):
        request = test["request"]
        description = test["description"]
        
        print(f"Test #{i}: {description}")
        print(f"User Request: \"{request}\"")
        print("-" * 80)
        
        # Find matching template
        template = loader.find_by_trigger(request)
        
        if template:
            print(f"✅ Template Found: {template.template_id}")
            print(f"   Triggers: {', '.join(template.triggers[:3])}{'...' if len(template.triggers) > 3 else ''}")
            print(f"   Response Type: {template.response_type}")
            
            # Show first 200 chars of content
            content_preview = template.content[:200].replace("\\n", " ")
            print(f"   Content Preview: {content_preview}...")
            
            # Render a snippet
            rendered = renderer.render(template, {}, "concise")
            first_line = rendered.split("\n")[0]
            print(f"   Rendered Header: {first_line}")
        else:
            print("❌ No template found (would use fallback)")
        
        print()
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    
    all_templates = loader.list_templates()
    print(f"Total templates loaded: {len(all_templates)}")
    print(f"Templates with triggers: {len([t for t in all_templates if t.triggers])}")
    
    # Count unique templates used
    templates_used = set()
    for test in test_cases:
        template = loader.find_by_trigger(test["request"])
        if template:
            templates_used.add(template.template_id)
    
    print(f"Unique templates matched in demo: {len(templates_used)}")
    print(f"Templates: {', '.join(sorted(templates_used))}")
    print()
    
    if len(templates_used) > 1:
        print("✅ PROOF: Different requests DO use different templates!")
    else:
        print("❌ WARNING: All requests using same template")
    
    print()


if __name__ == "__main__":
    demonstrate_template_routing()
