"""TDD tests for context assembly + ContextValidator integration."""

from pathlib import Path

from cortex.orchestrators.support.context_assembly_orchestrator import ContextAssemblyOrchestrator


def test_context_assembly_includes_validation_metadata(tmp_path: Path) -> None:
    file_path = tmp_path / "example.py"
    file_path.write_text("print('ok')", encoding="utf-8")

    orchestrator = ContextAssemblyOrchestrator()
    result = orchestrator.assemble([str(file_path)])

    assert "context_validation" in result
    validation = result["context_validation"]
    assert validation["is_valid"] is True
    assert validation["errors"] == []


def test_context_assembly_marks_stale_file_refs_invalid(tmp_path: Path) -> None:
    missing_file = tmp_path / "missing.py"

    orchestrator = ContextAssemblyOrchestrator()
    result = orchestrator.assemble([str(missing_file)])

    validation = result["context_validation"]
    assert validation["is_valid"] is False
    assert any("Stale file references" in err for err in validation["errors"])
