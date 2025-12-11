"""
Tests for OrchestrationDocsGenerator

TDD RED Phase - Tests written BEFORE implementation.
These tests MUST fail until GREEN phase implements the generator.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import tempfile
import shutil
import sys


def load_generator_module():
    """Helper to load generator with proper sys.path setup"""
    # Add cortex-brain/admin/documentation/generators to path
    generators_path = Path("/Users/asifhussain/PROJECTS/CORTEX/cortex-brain/admin/documentation/generators")
    if str(generators_path) not in sys.path:
        sys.path.insert(0, str(generators_path))
    
    # Now import will work
    from orchestration_docs_generator import OrchestrationDocsGenerator
    from base_generator import GenerationConfig, GenerationProfile
    
    return OrchestrationDocsGenerator, GenerationConfig, GenerationProfile


@pytest.fixture
def temp_workspace():
    """Create temporary CORTEX workspace structure for testing"""
    temp_dir = Path(tempfile.mkdtemp())
    
    # Create directory structure
    (temp_dir / "src" / "orchestrators").mkdir(parents=True)
    (temp_dir / "docs" / "orchestration").mkdir(parents=True)
    (temp_dir / "docs" / "diagrams" / "orchestration").mkdir(parents=True)
    (temp_dir / "cortex-brain" / "admin" / "documentation" / "generators").mkdir(parents=True)
    
    # Create sample orchestrator file
    orchestrator_content = '''"""
Test Orchestrator

Simple orchestrator for testing documentation generation.

Author: Test Author
"""

from pathlib import Path
from typing import Dict, Any


class TestOrchestrator:
    """
    Test orchestrator for documentation generation.
    
    Orchestrates test workflows with validation.
    """
    
    def __init__(self, workspace_root: Path):
        """Initialize test orchestrator"""
        self.workspace_root = workspace_root
    
    def execute_workflow(self, task_id: str) -> Dict[str, Any]:
        """
        Execute test workflow.
        
        Args:
            task_id: Unique task identifier
            
        Returns:
            Dictionary with execution results
        """
        return {"status": "success", "task_id": task_id}
'''
    
    (temp_dir / "src" / "orchestrators" / "test_orchestrator.py").write_text(orchestrator_content)
    
    yield temp_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def generator_config(temp_workspace):
    """Create generator configuration"""
    OrchestrationDocsGenerator, GenerationConfig, GenerationProfile = load_generator_module()
    
    return GenerationConfig(
        output_path=temp_workspace / "docs",
        profile=GenerationProfile.STANDARD,
        force_regenerate=True,
        validate_output=True
    )


class TestOrchestrationDocsGenerator:
    """Test suite for OrchestrationDocsGenerator (TDD GREEN Phase)"""
    
    def test_generator_imports(self):
        """Test that generator module can be imported (GREEN phase)"""
        OrchestrationDocsGenerator, GenerationConfig, GenerationProfile = load_generator_module()
        
        assert OrchestrationDocsGenerator is not None, "Should load OrchestrationDocsGenerator class"
        assert GenerationConfig is not None, "Should load GenerationConfig"
        assert GenerationProfile is not None, "Should load GenerationProfile"
    
    def test_discover_orchestrators(self, temp_workspace, generator_config):
        """Test orchestrator file discovery in src/orchestrators/"""
        OrchestrationDocsGenerator, _, _ = load_generator_module()
        
        generator = OrchestrationDocsGenerator(generator_config, temp_workspace)
        orchestrators = generator._discover_orchestrators()
        
        assert len(orchestrators) > 0, "Should discover at least one orchestrator"
        assert any("test_orchestrator.py" in str(p) for p in orchestrators), "Should find test_orchestrator.py"
    
    def test_extract_metadata(self, temp_workspace, generator_config):
        """Test metadata extraction from orchestrator file using AST"""
        pytest.skip("Generator not implemented yet (RED phase)")
        
        # This test will be implemented in GREEN phase
        # Expected behavior:
        # 1. Parse Python file with AST
        # 2. Extract class names and docstrings
        # 3. Extract method signatures and docstrings
        # 4. Extract module-level docstring
        # 5. Return structured metadata dictionary
        
        from cortex_brain.admin.documentation.generators.orchestration_docs_generator import OrchestrationDocsGenerator
        
        generator = OrchestrationDocsGenerator(generator_config, temp_workspace)
        orchestrator_file = temp_workspace / "src" / "orchestrators" / "test_orchestrator.py"
        
        metadata = generator._extract_metadata(orchestrator_file)
        
        assert "module_docstring" in metadata, "Should extract module docstring"
        assert "classes" in metadata, "Should extract classes"
        assert len(metadata["classes"]) > 0, "Should find at least one class"
        
        test_class = metadata["classes"][0]
        assert test_class["name"] == "TestOrchestrator", "Should extract correct class name"
        assert test_class["docstring"] is not None, "Should extract class docstring"
        assert len(test_class["methods"]) > 0, "Should extract methods"
    
    def test_generate_workflow_diagram(self, temp_workspace, generator_config):
        """Test Mermaid workflow diagram generation"""
        pytest.skip("Generator not implemented yet (RED phase)")
        
        # This test will be implemented in GREEN phase
        # Expected behavior:
        # 1. Analyze orchestrator methods and workflow
        # 2. Generate Mermaid flowchart syntax
        # 3. Show method call flow
        # 4. Return diagram content as string
        
        from cortex_brain.admin.documentation.generators.orchestration_docs_generator import OrchestrationDocsGenerator
        
        generator = OrchestrationDocsGenerator(generator_config, temp_workspace)
        
        metadata = {
            "name": "TestOrchestrator",
            "methods": [
                {"name": "__init__", "params": ["workspace_root"]},
                {"name": "execute_workflow", "params": ["task_id"]}
            ]
        }
        
        diagram = generator._generate_workflow_diagram(metadata)
        
        assert "flowchart" in diagram or "graph" in diagram, "Should generate Mermaid flowchart"
        assert "TestOrchestrator" in diagram, "Should include orchestrator name"
        assert "execute_workflow" in diagram, "Should include method name"
    
    def test_generate_documentation_page(self, temp_workspace, generator_config):
        """Test markdown documentation page generation"""
        pytest.skip("Generator not implemented yet (RED phase)")
        
        # This test will be implemented in GREEN phase
        # Expected behavior:
        # 1. Create markdown file in docs/orchestration/
        # 2. Include metadata (title, author, description)
        # 3. Include usage examples
        # 4. Include method documentation
        # 5. Include workflow diagram reference
        
        from cortex_brain.admin.documentation.generators.orchestration_docs_generator import OrchestrationDocsGenerator
        
        generator = OrchestrationDocsGenerator(generator_config, temp_workspace)
        orchestrator_file = temp_workspace / "src" / "orchestrators" / "test_orchestrator.py"
        
        result = generator.generate()
        
        assert result.success, "Generation should succeed"
        assert len(result.files_generated) > 0, "Should generate at least one file"
        
        # Check output file exists
        output_file = temp_workspace / "docs" / "orchestration" / "test-orchestrator.md"
        assert output_file.exists(), "Should create documentation file"
        
        content = output_file.read_text()
        assert "# Test Orchestrator" in content, "Should include title"
        assert "execute_workflow" in content, "Should document methods"
    
    def test_get_component_name(self, temp_workspace, generator_config):
        """Test component name for registry"""
        pytest.skip("Generator not implemented yet (RED phase)")
        
        from cortex_brain.admin.documentation.generators.orchestration_docs_generator import OrchestrationDocsGenerator
        
        generator = OrchestrationDocsGenerator(generator_config, temp_workspace)
        
        assert generator.get_component_name() == "Orchestration Documentation", "Should return correct component name"
    
    def test_validation(self, temp_workspace, generator_config):
        """Test output validation"""
        pytest.skip("Generator not implemented yet (RED phase)")
        
        from cortex_brain.admin.documentation.generators.orchestration_docs_generator import OrchestrationDocsGenerator
        
        generator = OrchestrationDocsGenerator(generator_config, temp_workspace)
        generator.generate()
        
        is_valid = generator.validate()
        
        assert is_valid, "Generated documentation should pass validation"
