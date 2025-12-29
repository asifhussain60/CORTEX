#!/usr/bin/env python3
"""
Generate documentation for ExecutionOrchestrator using DocumentationOrchestrator.

This demonstrates the self-documenting capability of CORTEX 4.0.
"""
import sys
import os
from pathlib import Path

# Change to project root directory
project_root = Path(__file__).parent.parent
os.chdir(project_root)

# Add src to path if not already there
src_path = str(project_root / "src")
if src_path not in sys.path:
    sys.path.append(src_path)

from orchestration_4_0.orchestrators.documentation.documentation_orchestrator import (
    DocumentationOrchestrator,
    DocumentationConfig
)


def main():
    """Generate documentation for ExecutionOrchestrator"""
    
    # Configure documentation generation
    config = DocumentationConfig(
        source_paths=[
            Path("src/orchestration_4_0/orchestrators/execution"),
            Path("src/orchestration_4_0/base"),
        ],
        output_dir=Path("docs/orchestration_4_0/execution_orchestrator"),
        include_private=False,
        generate_diagrams=True,
        diagram_types=["class_hierarchy", "phase_flow"]
    )
    
    # Create orchestrator
    orchestrator = DocumentationOrchestrator(name="ExecutionOrchestrator Documentation")
    
    # Execute documentation generation
    print("🚀 Generating ExecutionOrchestrator documentation...")
    print(f"📁 Output: {config.output_dir}")
    print()
    
    context = {"config": config}
    result = orchestrator.execute(context)
    
    # Display results
    if result.get("is_complete"):
        print("\n✅ Documentation generation complete!")
        
        doc_result = result.get("result")
        if doc_result:
            print(f"\n📊 Summary:")
            print(f"  - Modules analyzed: {doc_result.modules_analyzed}")
            print(f"  - Classes documented: {doc_result.classes_documented}")
            print(f"  - Functions documented: {doc_result.functions_documented}")
            print(f"  - Diagrams generated: {doc_result.diagrams_generated}")
            print(f"  - Output files: {len(doc_result.output_files)}")
            
            if doc_result.output_files:
                print(f"\n📄 Generated files:")
                for file_path in sorted(doc_result.output_files):
                    print(f"  - {file_path}")
            
            if doc_result.warnings:
                print(f"\n⚠️  Warnings ({len(doc_result.warnings)}):")
                for warning in doc_result.warnings[:5]:  # Show first 5
                    print(f"  - {warning}")
                if len(doc_result.warnings) > 5:
                    print(f"  ... and {len(doc_result.warnings) - 5} more")
            
            if doc_result.errors:
                print(f"\n❌ Errors ({len(doc_result.errors)}):")
                for error in doc_result.errors[:5]:  # Show first 5
                    print(f"  - {error}")
                if len(doc_result.errors) > 5:
                    print(f"  ... and {len(doc_result.errors) - 5} more")
    else:
        print("\n❌ Documentation generation failed")
        errors = result.get("errors", {})
        print(f"Total errors: {errors.get('total_errors', 0)}")
    
    return 0 if result.get("is_complete") else 1


if __name__ == "__main__":
    sys.exit(main())
