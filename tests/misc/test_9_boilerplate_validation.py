"""
Test 9: Boilerplate Validation - FastAPI Controller
Verifies FastAPI controller boilerplate generated correctly.
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


def test_scaffold_boilerplate_fastapi_controller(temp_output_path):
    """Verify FastAPI controller boilerplate generated correctly."""
    assessment = {
        "recommended_pattern": "clean_architecture",
        "tech_stack": {"framework": "FastAPI", "orm": "SQLAlchemy"},
        "service_candidates": [
            {"name": "PaymentService", "files": ["payment.py"], "confidence": 0.85}
        ]
    }
    
    generator = ScaffoldGenerator(output_path=temp_output_path)
    result = generator.generate(assessment)
    
    # Check main app file
    main_file = temp_output_path / "presentation" / "main.py"
    assert main_file.exists()
    
    content = main_file.read_text()
    assert "from fastapi import FastAPI" in content
    assert "app = FastAPI" in content
    assert "@app.get" in content or "health" in content
    
    # Check controller files created
    payment_controller = temp_output_path / "presentation" / "api" / "payment_controller.py"
    assert payment_controller.exists()
    
    controller_content = payment_controller.read_text()
    assert "from fastapi import APIRouter" in controller_content
    assert "router = APIRouter" in controller_content
    assert "@router.post" in controller_content or "@router.get" in controller_content


def test_scaffold_boilerplate_base_classes(temp_output_path):
    """Verify base classes generated correctly."""
    assessment = {
        "recommended_pattern": "clean_architecture",
        "tech_stack": {"framework": "FastAPI"},
        "service_candidates": []
    }
    
    generator = ScaffoldGenerator(output_path=temp_output_path)
    result = generator.generate(assessment)
    
    # Check base entity
    base_entity = temp_output_path / "domain" / "entities" / "base_entity.py"
    assert base_entity.exists()
    
    entity_content = base_entity.read_text()
    assert "class BaseEntity" in entity_content
    assert "dataclass" in entity_content or "BaseModel" in entity_content
    
    # Check base repository
    base_repo = temp_output_path / "domain" / "repositories" / "base_repository.py"
    assert base_repo.exists()
    
    repo_content = base_repo.read_text()
    assert "class BaseRepository" in repo_content
    assert "ABC" in repo_content or "abstractmethod" in repo_content


def test_scaffold_boilerplate_config_files(temp_output_path):
    """Verify configuration files generated."""
    assessment = {
        "recommended_pattern": "clean_architecture",
        "tech_stack": {"framework": "FastAPI", "orm": "SQLAlchemy"},
        "service_candidates": []
    }
    
    generator = ScaffoldGenerator(output_path=temp_output_path)
    result = generator.generate(assessment)
    
    # Check pyproject.toml
    pyproject = temp_output_path / "pyproject.toml"
    assert pyproject.exists()
    
    pyproject_content = pyproject.read_text()
    assert "FastAPI" in pyproject_content or "fastapi" in pyproject_content
    
    # Check pytest.ini
    pytest_ini = temp_output_path / "pytest.ini"
    assert pytest_ini.exists()
    
    # Check .env.example
    env_example = temp_output_path / ".env.example"
    assert env_example.exists()
    
    # Check Dockerfile
    dockerfile = temp_output_path / "Dockerfile"
    assert dockerfile.exists()
    
    dockerfile_content = dockerfile.read_text()
    assert "FROM python" in dockerfile_content
    
    # Check README.md
    readme = temp_output_path / "README.md"
    assert readme.exists()
    
    readme_content = readme.read_text()
    assert "Architecture" in readme_content or "Getting Started" in readme_content
