import os
from pathlib import Path

import pytest

from src.epmo.documentation import generate_documentation


def create_sample_epmo(tmp_path: Path) -> Path:
    epmo = tmp_path / "sample_epmo"
    epmo.mkdir(parents=True, exist_ok=True)
    # package init
    (epmo / "__init__.py").write_text("\n\n", encoding="utf-8")
    # module A
    (epmo / "module_a.py").write_text(
        """
class Foo:
    def bar(self, x, y):
        'Add two numbers'
        return x + y
"""
        , encoding="utf-8")
    # module B
    (epmo / "module_b.py").write_text(
        """
from .module_a import Foo

def baz(n):
    'Return doubled n'
    return n * 2
"""
        , encoding="utf-8")
    return epmo


@pytest.mark.unit
def test_generate_documentation_multimodal(tmp_path, monkeypatch):
    # Arrange
    epmo_path = create_sample_epmo(tmp_path)
    project_root = tmp_path
    # Avoid writing prompts into repo by chdir to tmp
    monkeypatch.chdir(tmp_path)

    # Act
    result = generate_documentation(epmo_path, project_root)

    # Assert
    assert result["status"] == "success"
    assert result["epmo_name"] == epmo_path.name
    content = result.get("markdown_content", "")
    assert isinstance(content, str) and len(content) > 0
    assert f"# {epmo_path.name} Documentation" in content

    visual = result.get("visual_stats", {})
    assert isinstance(visual, dict)
    # At least one diagram (architecture) should be generated for non-empty module
    assert visual.get("total_diagrams", 0) >= 1

    # Image prompts should be generated and saved as files under tmp docs
    prompts = result.get("image_prompts", [])
    assert isinstance(prompts, list)
    assert len(prompts) >= 1
    prompt_files = result.get("prompt_files", {})
    assert isinstance(prompt_files, dict)
    # Ensure prompt files saved under tmp docs/diagrams/prompts
    for _, path in prompt_files.items():
        assert Path(path).exists(), f"Prompt file does not exist: {path}"
        assert Path(path).is_file()
