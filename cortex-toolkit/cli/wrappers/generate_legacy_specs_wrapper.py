#!/usr/bin/env python3
"""
CORTEX Toolkit - Legacy API Spec Generator CLI Wrapper
Generate business specifications and OpenAPI specs from legacy C# code.

Author: Asif Hussain
GitHub: github.com/asifhussain60/CORTEX
Version: 3.0.1 (with narrative validation)
"""

import sys
import argparse
from pathlib import Path

# Add CORTEX to path
TOOLKIT_ROOT = Path(__file__).parent.parent.parent
CORTEX_ROOT = TOOLKIT_ROOT.parent
sys.path.insert(0, str(CORTEX_ROOT))

from src.operations.modules.generators.legacy_spec_generator import LegacySpecGenerator


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Generate specifications from legacy C# API code (CORTEX Lens v3)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate with defaults (narrative validation enabled)
  python generate_legacy_specs_wrapper.py \\
    path/to/XUpdateFundingBatch.cs \\
    --output-dir ./specs/xupdatefundingbatch
  
  # Generate without narrative validation (legacy mode)
  python generate_legacy_specs_wrapper.py \\
    path/to/API.cs \\
    --output-dir ./specs/api-name \\
    --no-narrative-validation
  
  # Regenerate existing specs with corrections
  python generate_legacy_specs_wrapper.py \\
    path/to/Updater_CreateRAFundingInvoices.cs \\
    --output-dir ./specs/updater-createrafundinginvoices \\
    --force
        """
    )
    
    parser.add_argument(
        "legacy_file",
        help="Path to legacy C# file"
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Output directory for specifications"
    )
    parser.add_argument(
        "--no-narrative-validation",
        action="store_true",
        help="Disable narrative quality validation (legacy mode)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing output directory"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Validate legacy file
    legacy_file = Path(args.legacy_file)
    if not legacy_file.exists():
        print(f"❌ Error: Legacy file not found: {legacy_file}")
        return 1
    
    if not legacy_file.suffix == ".cs":
        print(f"⚠️  Warning: File does not have .cs extension: {legacy_file}")
    
    # Check output directory
    output_dir = Path(args.output_dir)
    if output_dir.exists() and not args.force:
        print(f"❌ Error: Output directory already exists: {output_dir}")
        print(f"   Use --force to overwrite")
        return 1
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize generator
    try:
        print(f"🚀 CORTEX Lens v3.0 - Legacy API Spec Generator")
        print(f"=" * 60)
        print(f"📄 Legacy File: {legacy_file.name}")
        print(f"📁 Output Dir: {output_dir}")
        print(f"✍️  Narrative Validation: {'Enabled ✅' if not args.no_narrative_validation else 'Disabled ⚠️ '}")
        print(f"=" * 60)
        print()
        
        generator = LegacySpecGenerator(
            legacy_file=legacy_file,
            output_dir=output_dir,
            enable_narrative_validation=not args.no_narrative_validation
        )
        
        # Phase 1: Analysis
        print(f"⚙️  Phase 1: Analyzing legacy code...")
        generator.analyze()
        print(f"✅ Phase 1 Complete")
        print()
        
        # Phase 2: Business Spec
        print(f"⚙️  Phase 2: Generating business specification...")
        business_spec = generator.generate_business_spec()
        business_spec_path = output_dir / "business-spec.md"
        business_spec_path.write_text(business_spec, encoding='utf-8')
        print(f"✅ Phase 2 Complete: {business_spec_path.name}")
        print()
        
        # Phase 3: OpenAPI Spec
        if generator.openapi_enabled:
            print(f"⚙️  Phase 3: Generating OpenAPI specification...")
            openapi_spec = generator.generate_openapi_spec()
            openapi_spec_path = output_dir / "openapi.yaml"
            openapi_spec_path.write_text(openapi_spec, encoding='utf-8')
            print(f"✅ Phase 3 Complete: {openapi_spec_path.name}")
            print()
        
        # Phase 4: Diagrams (optional - skip if methods don't exist)
        diagrams_generated = 0
        if hasattr(generator, 'generate_flow_diagram'):
            print(f"⚙️  Phase 4: Generating visual diagrams...")
            diagrams_dir = output_dir / "diagrams"
            diagrams_dir.mkdir(exist_ok=True)
            
            # Flow diagram
            if hasattr(generator, 'generate_flow_diagram'):
                flow = generator.generate_flow_diagram()
                (diagrams_dir / "flowchart.mmd").write_text(flow, encoding='utf-8')
                diagrams_generated += 1
            
            # Sequence diagram
            if hasattr(generator, 'generate_sequence_diagram'):
                sequence = generator.generate_sequence_diagram()
                (diagrams_dir / "sequence.mmd").write_text(sequence, encoding='utf-8')
                diagrams_generated += 1
            
            # Dependency diagram
            if hasattr(generator, 'generate_dependency_diagram'):
                deps = generator.generate_dependency_diagram()
                (diagrams_dir / "dependency.mmd").write_text(deps, encoding='utf-8')
                diagrams_generated += 1
            
            print(f"✅ Phase 4 Complete: {diagrams_generated} diagrams generated")
            print()
        
        # Phase 5: Traceability Matrix
        if hasattr(generator, 'generate_traceability_matrix'):
            print(f"⚙️  Phase 5: Generating traceability matrix...")
            matrix = generator.generate_traceability_matrix()
            matrix_path = output_dir / "traceability-matrix.md"
            matrix_path.write_text(matrix, encoding='utf-8')
            print(f"✅ Phase 5 Complete: {matrix_path.name}")
            print()
        
        # Summary
        print(f"=" * 60)
        print(f"🎉 Specification Generation Complete!")
        print(f"=" * 60)
        print()
        print(f"📊 Statistics:")
        print(f"   • Business Rules: {len(generator.business_rules)}")
        print(f"   • Validations: {len(generator.validations)}")
        print(f"   • DB Operations: {len(generator.db_operations)}")
        print(f"   • Methods: {len(generator.methods)}")
        print(f"   • Dependencies: {len(generator.dependencies)}")
        if generator.openapi_enabled:
            print(f"   • OpenAPI Endpoints: {len(generator.openapi_endpoints)}")
        print()
        
        print(f"📂 Generated Files:")
        print(f"   • business-spec.md")
        if generator.openapi_enabled:
            print(f"   • openapi.yaml")
        print(f"   • diagrams/flowchart.mmd")
        print(f"   • diagrams/sequence.mmd")
        print(f"   • diagrams/dependency.mmd")
        print(f"   • traceability-matrix.md")
        print()
        
        if not args.no_narrative_validation:
            print(f"✨ Quality Enhancements:")
            print(f"   ✅ Grammar and readability validated")
            print(f"   ✅ User stories use proper English")
            print(f"   ✅ Headings and descriptions corrected")
            print()
        
        print(f"✨ Next Steps:")
        print(f"   1. Review: {business_spec_path}")
        print(f"   2. Validate: PM/BA approval checklist at bottom")
        if generator.openapi_enabled:
            print(f"   3. Test: Import {openapi_spec_path.name} into Swagger UI")
        print(f"   4. Visualize: Open diagrams in VS Code with Mermaid extension")
        print()
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error during specification generation:")
        print(f"   {str(e)}")
        
        if args.verbose:
            import traceback
            print(f"\n📋 Stack trace:")
            traceback.print_exc()
        
        return 1


if __name__ == "__main__":
    sys.exit(main())
