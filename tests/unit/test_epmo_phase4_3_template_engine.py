from pathlib import Path

import pytest

from src.epmo.documentation import (
    generate_documentation,
    create_epmo_model,
)
from src.epmo.documentation.models import GenerationConfig
from src.epmo.documentation.template_engine import render_documentation
from src.epmo.documentation.parser import analyze_epmo_structure
from src.epmo.documentation.dependency_mapper import analyze_epmo_dependencies


def create_sample_epmo(tmp_path: Path) -> Path:
    epmo = tmp_path / "sample_epmo_te"
    epmo.mkdir(parents=True, exist_ok=True)
    (epmo / "__init__.py").write_text("\n\n", encoding="utf-8")
    (epmo / "alpha.py").write_text(
        """
class Alpha:
    def run(self):
        'Do work'
        return True
""",
        encoding="utf-8",
    )
    return epmo


@pytest.mark.unit
def test_template_engine_minimal_renders(tmp_path, monkeypatch):
    # Arrange
    epmo_path = create_sample_epmo(tmp_path)
    project_root = tmp_path
    monkeypatch.chdir(tmp_path)

    # Build model
    ast_analysis = analyze_epmo_structure(epmo_path)
    deps = analyze_epmo_dependencies(epmo_path, project_root)
    model = create_epmo_model(epmo_path, ast_analysis, deps, health_data=None)

    # Act
    content = render_documentation(model, template_name="minimal.md.j2")

    # Assert
    assert isinstance(content, str)
    assert content.startswith(f"# {epmo_path.name}")
    assert "## Overview" in content
