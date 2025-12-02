from pathlib import Path

import pytest

from src.epmo.documentation.cli import EPMDocumentationCLI


def create_sample_epmo(tmp_path: Path) -> Path:
    epmo = tmp_path / "sample_epmo_cli"
    epmo.mkdir(parents=True, exist_ok=True)
    (epmo / "__init__.py").write_text("\n\n", encoding="utf-8")
    (epmo / "core.py").write_text(
        """
class Core:
    def ping(self):
        'pong'
        return 'pong'
""",
        encoding="utf-8",
    )
    return epmo


@pytest.mark.unit
def test_cli_generate_documentation_for_epmo(tmp_path, monkeypatch):
    # Arrange
    epmo_path = create_sample_epmo(tmp_path)
    output_dir = tmp_path / "out_docs"
    cli = EPMDocumentationCLI()
    parser = cli.create_parser()
    args = parser.parse_args([
        str(epmo_path),
        "-o",
        str(output_dir),
        "--format",
        "markdown",
        "--template",
        "comprehensive",
        "--health-analysis",
        "--include-diagrams",
        "--include-image-prompts",
        "--dry-run",
    ])

    # Act
    config = cli.create_generation_config(args)
    diagram_config = cli.create_diagram_config(args)
    result = cli.generate_documentation_for_epmo(
        epmo_path, tmp_path, config, diagram_config, args
    )

    # Assert
    assert result["status"] == "success"
    stats = result.get("summary_stats", {})
    assert stats.get("total_files", 0) >= 1
    visual = result.get("visual_stats", {})
    assert isinstance(visual, dict)
    # Should have at least one diagram in visual stats
    assert visual.get("total_diagrams", 0) >= 1
    # Dry run should not write main markdown file
    out_file = output_dir / f"{epmo_path.name}_documentation.md"
    assert not out_file.exists()
