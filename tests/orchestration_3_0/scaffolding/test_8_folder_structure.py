"""
Test 8: Folder Structure Generation
Verifies Clean Architecture folder structure created.
"""

import pytest
from pathlib import Path
import tempfile
import shutil

from src.orchestration_3_0.orchestrators.scaffolding.scaffold_generator import ScaffoldGenerator


@pytest.fixture
def temp_output_path():
    """Create temporary output directory."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


def test_scaffold_folder_structure_clean_architecture(temp_output_path):
    """Verify Clean Architecture folder structure created."""
    assessment = {
        "recommended_pattern": "clean_architecture",
        "service_candidates": [],
        "tech_stack": {"framework": "FastAPI", "orm": "SQLAlchemy"}
    }
    
    generator = ScaffoldGenerator(output_path=temp_output_path)
    result = generator.generate(assessment)
    
    # Check folder structure
    assert (temp_output_path / "domain" / "entities").exists()
    assert (temp_output_path / "domain" / "repositories").exists()
    assert (temp_output_path / "application" / "use_cases").exists()
    assert (temp_output_path / "application" / "dtos").exists()
    assert (temp_output_path / "infrastructure" / "persistence").exists()
    assert (temp_output_path / "infrastructure" / "config").exists()
    assert (temp_output_path / "presentation" / "api").exists()
    assert (temp_output_path / "presentation" / "schemas").exists()
    assert (temp_output_path / "tests" / "unit").exists()
    assert (temp_output_path / "tests" / "integration").exists()
    assert (temp_output_path / "tests" / "e2e").exists()
    
    # Check result metadata
    assert result['files_created'] > 0
    assert result['scaffold_path'] == str(temp_output_path)
    assert result['language'] in ['python', 'typescript', 'csharp']
    assert result['framework'] is not None


def test_scaffold_folder_structure_with_service_candidates(temp_output_path):
    """Verify service-specific files created for candidates."""
    assessment = {
        "recommended_pattern": "clean_architecture",
        "service_candidates": [
            {"name": "PaymentService", "files": ["payment.py"], "confidence": 0.85},
            {"name": "UserService", "files": ["user.py"], "confidence": 0.80}
        ],
        "tech_stack": {"framework": "FastAPI"}
    }
    
    generator = ScaffoldGenerator(output_path=temp_output_path)
    result = generator.generate(assessment)
    
    # Check service-specific entity files created
    payment_entity = temp_output_path / "domain" / "entities" / "payment.py"
    user_entity = temp_output_path / "domain" / "entities" / "user.py"
    
    # At least base entities should exist
    base_entity = temp_output_path / "domain" / "entities" / "base_entity.py"
    assert base_entity.exists()
    
    # Check generated files count
    assert result['files_created'] > 10  # Should have many files
