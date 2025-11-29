"""
Regenerate All CORTEX Documentation using Enterprise Doc Generator

This script regenerates all documentation components including:
- Enhanced image prompts and narratives
- Standard image prompts (via diagrams component)
- Feature lists
- Executive summaries
- Story chapters
- Rulebook

Usage:
    python scripts/regenerate_all_docs.py [component1] [component2] ...
    python scripts/regenerate_all_docs.py --all
    python scripts/regenerate_all_docs.py diagrams
    python scripts/regenerate_all_docs.py narratives executive_summary

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sys
import argparse
from pathlib import Path
import logging

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.operations.enterprise_documentation_orchestrator import (
    EnterpriseDocumentationOrchestrator,
    execute_enterprise_documentation
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


AVAILABLE_COMPONENTS = {
    "diagrams": "Image Prompts & Mermaid Diagrams",
    "feature_list": "CORTEX Feature List",
    "executive_summary": "Executive Summary",
    "rulebook": "THE RULEBOOK - CORTEX Bible",
    "narratives": "The Intern with Amnesia Story",
    "mkdocs": "MkDocs Site",
    "all": "All Components"
}


def print_banner():
    """Print application banner"""
    print("=" * 80)
    print("CORTEX Enterprise Documentation Regeneration")
    print("=" * 80)
    print()


def print_available_components():
    """Print available components"""
    print("Available Components:")
    print()
    for comp_id, comp_name in AVAILABLE_COMPONENTS.items():
        print(f"  • {comp_id:20} - {comp_name}")
    print()


def regenerate_components(component_ids: list, profile: str = "standard", dry_run: bool = False):
    """
    Regenerate specific documentation components
    
    Args:
        component_ids: List of component IDs to regenerate
        profile: Generation profile (quick, standard, comprehensive)
        dry_run: If True, preview what would be generated
    """
    print_banner()
    
    if "all" in component_ids:
        component_ids = ["diagrams", "feature_list", "executive_summary", "rulebook", "narratives"]
        print("Regenerating ALL documentation components...")
    else:
        print(f"Regenerating components: {', '.join(component_ids)}")
    
    print()
    print(f"Profile: {profile}")
    print(f"Dry Run: {dry_run}")
    print()
    print("-" * 80)
    print()
    
    try:
        # Execute through enterprise documentation orchestrator
        result = execute_enterprise_documentation(
            workspace_root=PROJECT_ROOT,
            profile=profile,
            dry_run=dry_run,
            stage=None,  # Full pipeline
            components=component_ids  # Pass components list
        )
        
        print()
        print("=" * 80)
        print("Generation Results")
        print("=" * 80)
        print()
        
        if result.success:
            print("✅ SUCCESS - Documentation regenerated successfully!")
            print()
            
            # Display summary
            if result.data:
                exec_summary = result.data.get("execution_summary", {})
                print(f"Duration: {exec_summary.get('duration_seconds', 0):.2f} seconds")
                print(f"Timestamp: {exec_summary.get('timestamp', 'N/A')}")
                print()
                
                # Display file counts
                file_gen = result.data.get("file_generation", {})
                if file_gen:
                    print(f"Files Generated: {file_gen.get('total', 0)}")
                    by_category = file_gen.get("by_category", {})
                    if by_category:
                        print()
                        print("By Category:")
                        for category, count in by_category.items():
                            print(f"  • {category}: {count} files")
                    print()
                
                # Display component results
                registry_exec = result.data.get("registry_execution", {})
                if registry_exec:
                    components = registry_exec.get("components", [])
                    if components:
                        print("Component Status:")
                        for comp in components:
                            comp_id = comp.get("id", "unknown")
                            success = comp.get("success", False)
                            status_icon = "✅" if success else "❌"
                            comp_name = AVAILABLE_COMPONENTS.get(comp_id, comp_id)
                            print(f"  {status_icon} {comp_name}")
                        print()
            
            print("=" * 80)
            print("Next Steps")
            print("=" * 80)
            print()
            print("1. Review generated files in docs/ directory")
            print("2. For image prompts: Use DALL-E 3 or Gemini to generate images")
            print("3. For narratives: Review story chapters for accuracy")
            print("4. Build documentation: python scripts/build_docs.py")
            print()
            
        else:
            print("❌ FAILED - Documentation generation encountered errors")
            print()
            if result.errors:
                print("Errors:")
                for error in result.errors:
                    print(f"  • {error}")
                print()
        
        return 0 if result.success else 1
        
    except Exception as e:
        print()
        print("❌ Error during regeneration:")
        print(f"   {str(e)}")
        print()
        import traceback
        print(traceback.format_exc())
        return 1


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description="Regenerate CORTEX documentation components",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "components",
        nargs="*",
        help="Component IDs to regenerate (or --all for all components)"
    )
    
    parser.add_argument(
        "--all",
        action="store_true",
        help="Regenerate all documentation components"
    )
    
    parser.add_argument(
        "--profile",
        choices=["quick", "standard", "comprehensive"],
        default="standard",
        help="Generation profile (default: standard)"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be generated without actual generation"
    )
    
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available components"
    )
    
    args = parser.parse_args()
    
    # List components if requested
    if args.list:
        print_banner()
        print_available_components()
        return 0
    
    # Determine which components to regenerate
    components = args.components if args.components else []
    
    if args.all:
        components = ["all"]
    
    if not components:
        print_banner()
        print("Error: No components specified")
        print()
        print_available_components()
        print("Usage:")
        print("  python scripts/regenerate_all_docs.py diagrams")
        print("  python scripts/regenerate_all_docs.py --all")
        print("  python scripts/regenerate_all_docs.py diagrams narratives")
        print()
        return 1
    
    # Validate components
    valid_components = set(AVAILABLE_COMPONENTS.keys())
    invalid = [c for c in components if c not in valid_components]
    if invalid and "all" not in components:
        print_banner()
        print(f"Error: Invalid components: {', '.join(invalid)}")
        print()
        print_available_components()
        return 1
    
    # Execute regeneration
    return regenerate_components(
        component_ids=components,
        profile=args.profile,
        dry_run=args.dry_run
    )


if __name__ == "__main__":
    sys.exit(main())
