#!/usr/bin/env python3
"""
Generate all L2 documentation pages using CortexDocsOrchestrator.

Usage:
    python scripts/generate_docs.py [operation]
    
Operations:
    list      - List all sections with status
    advise    - Get advisory for specific section
    generate  - Generate all missing pages
    validate  - Validate generated HTML

Authority: PHASE-17, ARCH-011 (execute to completion)
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from cortex.orchestrators.internal.cortex_docs_orchestrator import CortexDocsOrchestrator


def list_sections():
    """List all documentation sections."""
    orch = CortexDocsOrchestrator.instance()
    result = orch.execute("list_sections")
    
    if result.is_ok():
        data = result.value
        print(f"\n📚 CORTEX Documentation Sections")
        print(f"{'='*70}")
        print(f"Total: {data['total_sections']} | With Advisory: {data['with_advisory']} | Complete: {data['completed']}\n")
        
        for section in data['sections']:
            status_icon = "✅" if section['status'] == "COMPLETE" else "⏳"
            advisory_icon = "📋" if section['advisory_available'] else "❌"
            
            print(f"{status_icon} {section['section_id']:<30} {section['title']:<25}")
            print(f"   Status: {section['status']:<15} Diagrams: {section['diagram_count']} | "
                  f"Effort: {section['total_effort_hours']:.1f}h | Advisory: {advisory_icon}")
            print()
    else:
        print(f"❌ Error: {result.error}")


def advise_section(section_id: str):
    """Get advisory for a specific section."""
    orch = CortexDocsOrchestrator.instance()
    result = orch.execute("advise_section", section_id=section_id)
    
    if result.is_ok():
        advisory = result.value
        print(f"\n📋 Advisory: {advisory.section_title}")
        print(f"{'='*70}")
        print(f"Theme Accent: {advisory.theme_accent}")
        print(f"Effort: {advisory.effort_estimate_hours:.1f} hours\n")
        
        print("🎨 Recommended Diagrams:")
        for diag in advisory.recommended_diagrams:
            print(f"  • {diag.name} ({diag.diagram_type})")
            print(f"    {diag.description}")
            print(f"    Effort: {diag.effort_hours:.1f}h | Uniqueness: {diag.uniqueness_score}/10\n")
        
        print("📝 Content Structure:")
        for item in advisory.content_structure:
            print(f"  • {item}")
        
        print(f"\n✨ Unique Features:")
        for feature in advisory.unique_features:
            print(f"  • {feature}")
        
        print(f"\n💡 Design Rationale:")
        print(f"{advisory.design_rationale}")
    else:
        print(f"❌ Error: {result.error}")


def generate_all():
    """Generate all missing documentation pages."""
    orch = CortexDocsOrchestrator.instance()
    
    print(f"\n🚀 Generating All Documentation Pages")
    print(f"{'='*70}\n")
    
    # First, list what we're about to generate
    list_result = orch.execute("list_sections")
    if list_result.is_ok():
        data = list_result.value
        pending = [s for s in data['sections'] if s['status'] != "COMPLETE"]
        print(f"📋 Will generate {len(pending)} missing pages:\n")
        for section in pending:
            print(f"  • {section['section_id']} - {section['title']}")
        print()
    
    # Now generate
    print("⏳ Starting generation...\n")
    result = orch.execute("generate_all")
    
    if result.is_ok():
        report = result.value
        print(f"\n✅ Generation Complete!")
        print(f"{'='*70}")
        print(f"Generated Files: {len(report.generated_files)}")
        print(f"Failed Files: {len(report.failed_files)}")
        print(f"Total Size: {report.total_size_bytes / 1024:.1f} KB")
        print(f"Generation Time: {report.generation_time_seconds:.2f}s\n")
        
        if report.generated_files:
            print("📄 Generated:")
            for path in report.generated_files:
                rel_path = path.relative_to(project_root)
                print(f"  ✅ {rel_path}")
        
        if report.failed_files:
            print("\n❌ Failed:")
            for path, error in report.failed_files:
                rel_path = path.relative_to(project_root)
                print(f"  ❌ {rel_path}")
                print(f"     Error: {error}")
    else:
        print(f"❌ Generation failed: {result.error}")


def validate_html():
    """Validate generated HTML."""
    orch = CortexDocsOrchestrator.instance()
    result = orch.execute("validate")
    
    if result.is_ok():
        print(f"\n✅ HTML Validation Complete")
        print(result.value)
    else:
        print(f"❌ Validation failed: {result.error}")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/generate_docs.py [list|advise|generate|validate]")
        sys.exit(1)
    
    operation = sys.argv[1].lower()
    
    if operation == "list":
        list_sections()
    elif operation == "advise":
        if len(sys.argv) < 3:
            print("Usage: python scripts/generate_docs.py advise <section_id>")
            sys.exit(1)
        advise_section(sys.argv[2])
    elif operation == "generate":
        generate_all()
    elif operation == "validate":
        validate_html()
    else:
        print(f"Unknown operation: {operation}")
        print("Valid operations: list, advise, generate, validate")
        sys.exit(1)


if __name__ == "__main__":
    main()
