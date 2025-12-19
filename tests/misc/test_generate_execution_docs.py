"""
Integration test: Generate documentation for ExecutionOrchestrator
"""
import pytest
from pathlib import Path
import shutil

from src.orchestration_4_0.orchestrators.documentation.documentation_orchestrator import (
    DocumentationOrchestrator,
    DocumentationConfig
)


def test_generate_execution_orchestrator_docs(tmp_path):
    """Test generating documentation for ExecutionOrchestrator"""
    
    # Configure documentation generation
    output_dir = tmp_path / "execution_orchestrator_docs"
    config = DocumentationConfig(
        source_paths=[
            Path("src/orchestration_4_0/orchestrators/execution"),
            Path("src/orchestration_4_0/base"),
        ],
        output_dir=output_dir,
        include_private=False,
        generate_diagrams=True,
        diagram_types=["class_hierarchy", "phase_flow"]
    )
    
    # Create orchestrator
    orchestrator = DocumentationOrchestrator()
    
    # Execute documentation generation
    context = {"config": config}
    result = orchestrator.execute(context)
    
    # Assertions
    assert result is not None
    assert result.get("is_complete"), f"Documentation generation failed: {result.get('errors')}"
    
    doc_result = result.get("result")
    assert doc_result is not None
    
    # Verify documentation was generated
    assert doc_result.modules_analyzed > 0, "No modules were analyzed"
    assert doc_result.classes_documented > 0, "No classes were documented"
    assert len(doc_result.output_files) > 0, "No output files were generated"
    
    # Verify output files exist
    for file_path in doc_result.output_files:
        assert file_path.exists(), f"Output file not found: {file_path}"
    
    # Print summary
    print(f"\n✅ Documentation generated successfully!")
    print(f"  - Modules analyzed: {doc_result.modules_analyzed}")
    print(f"  - Classes documented: {doc_result.classes_documented}")
    print(f"  - Functions documented: {doc_result.functions_documented}")
    print(f"  - Diagrams generated: {doc_result.diagrams_generated}")
    print(f"  - Output files: {len(doc_result.output_files)}")
    
    # Copy to actual docs directory for inspection
    actual_docs_dir = Path("docs/orchestration_4_0/execution_orchestrator")
    if actual_docs_dir.exists():
        shutil.rmtree(actual_docs_dir)
    shutil.copytree(output_dir, actual_docs_dir)
    print(f"\n📁 Documentation copied to: {actual_docs_dir}")
    
    for file_path in sorted(doc_result.output_files):
        rel_path = file_path.relative_to(output_dir)
        actual_path = actual_docs_dir / rel_path
        print(f"  - {actual_path}")


if __name__ == "__main__":
    # Run as standalone script
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        test_generate_execution_orchestrator_docs(Path(tmpdir))
