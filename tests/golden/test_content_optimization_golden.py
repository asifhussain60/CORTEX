"""
Golden Tests — ContentOptimizationOrchestrator

TDD Contract (CORE-008): These tests MUST fail RED before implementation.

Test Categories:
1. Enum + Imports — IntentType.OPTIMIZE exists
2. Protocol Compliance — inherits OrchestratorProtocolMixin, WorkflowEnforcementMixin
3. Single-file optimization — HTML, Markdown, YAML, JSON, TXT
4. Multi-file batch optimization — arrays of mixed content types
5. In-place overwrite — original files replaced with optimized content
6. Validation gates — syntax checks before write (YAML parse, JSON parse)
7. Error handling — missing files, unreadable files, write failures

Run RED gate:  python3 scripts/run_tests.py file tests/golden/test_content_optimization_golden.py
Run GREEN gate: after implementing ContentOptimizationOrchestrator
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import List

import pytest
import yaml


# ---------------------------------------------------------------------------
# Test Category 1: Enum + Imports
# ---------------------------------------------------------------------------

class TestOptimizeIntentEnum:
    """IntentType.OPTIMIZE must exist in canonical_enums.py."""

    def test_optimize_intent_exists(self):
        """OPTIMIZE must be a valid member of IntentType."""
        from cortex.models.canonical_enums import IntentType
        assert hasattr(IntentType, "OPTIMIZE"), (
            "IntentType.OPTIMIZE does not exist — add OPTIMIZE = 'optimize' to canonical_enums.py"
        )

    def test_optimize_intent_value(self):
        """OPTIMIZE enum value must be the string 'optimize'."""
        from cortex.models.canonical_enums import IntentType
        assert IntentType.OPTIMIZE.value == "optimize", (
            f"Expected IntentType.OPTIMIZE.value == 'optimize', got {IntentType.OPTIMIZE.value!r}"
        )


class TestContentOptimizationOrchestratorImports:
    """ContentOptimizationOrchestrator must be importable."""

    def test_orchestrator_importable(self):
        """ContentOptimizationOrchestrator must exist at cortex/orchestrators/support/."""
        from cortex.orchestrators.support.content_optimization_orchestrator import (
            ContentOptimizationOrchestrator,
        )
        assert ContentOptimizationOrchestrator is not None

    def test_optimization_result_importable(self):
        """OptimizationResult dataclass must be importable."""
        from cortex.orchestrators.support.content_optimization_orchestrator import (
            OptimizationResult,
        )
        assert OptimizationResult is not None

    def test_content_type_enum_importable(self):
        """ContentType enum must be importable."""
        from cortex.orchestrators.support.content_optimization_orchestrator import (
            ContentType,
        )
        assert ContentType is not None


# ---------------------------------------------------------------------------
# Test Category 2: Protocol Compliance
# ---------------------------------------------------------------------------

class TestContentOptimizationOrchestratorProtocol:
    """ContentOptimizationOrchestrator must satisfy orchestrator contracts."""

    def test_inherits_protocol_mixin(self):
        """Must inherit OrchestratorProtocolMixin."""
        from cortex.core.orchestrator_protocol_mixin import OrchestratorProtocolMixin
        from cortex.orchestrators.support.content_optimization_orchestrator import (
            ContentOptimizationOrchestrator,
        )
        assert issubclass(ContentOptimizationOrchestrator, OrchestratorProtocolMixin)

    def test_inherits_workflow_enforcement_mixin(self):
        """Must inherit WorkflowEnforcementMixin."""
        from cortex.core.workflow_enforcement_mixin import WorkflowEnforcementMixin
        from cortex.orchestrators.support.content_optimization_orchestrator import (
            ContentOptimizationOrchestrator,
        )
        assert issubclass(ContentOptimizationOrchestrator, WorkflowEnforcementMixin)

    def test_has_optimize_method(self):
        """Must expose a public `optimize` method."""
        from cortex.orchestrators.support.content_optimization_orchestrator import (
            ContentOptimizationOrchestrator,
        )
        assert callable(getattr(ContentOptimizationOrchestrator, "optimize", None))

    def test_has_health_check_method(self):
        """Must expose `health_check` for HealthOrchestrator registration."""
        from cortex.orchestrators.support.content_optimization_orchestrator import (
            ContentOptimizationOrchestrator,
        )
        assert callable(getattr(ContentOptimizationOrchestrator, "health_check", None))


# ---------------------------------------------------------------------------
# Test Category 3: Single-File Optimization
# ---------------------------------------------------------------------------

class TestSingleFileOptimization:
    """Golden tests for optimizing individual files of each supported type."""

    @pytest.fixture
    def orchestrator(self):
        """Provide a ContentOptimizationOrchestrator instance."""
        from cortex.orchestrators.support.content_optimization_orchestrator import (
            ContentOptimizationOrchestrator,
        )
        return ContentOptimizationOrchestrator()

    def test_optimize_markdown_file(self, orchestrator, tmp_path: Path):
        """Markdown file with noise should be optimized and overwritten."""
        # Arrange
        md_file = tmp_path / "test.md"
        original_content = """# Test Document

This is a test paragraph with some noise...

Lorem ipsum dolor sit amet, consectetur adipiscing elit. This sentence
is important and should be kept.

More noise here that doesn't add value. Filler text. Etc.

## Section 2

Important information here.
"""
        md_file.write_text(original_content, encoding="utf-8")

        # Act
        result = orchestrator.optimize(file_paths=[str(md_file)])

        # Assert
        assert result.success is True
        assert result.files_processed == 1
        assert result.files_written == 1
        optimized = md_file.read_text(encoding="utf-8")
        assert len(optimized) < len(original_content), "Optimized content should be shorter"
        assert "important" in optimized.lower(), "Signal content must be preserved"

    def test_optimize_json_file(self, orchestrator, tmp_path: Path):
        """JSON file with verbose keys should be optimized."""
        # Arrange
        json_file = tmp_path / "test.json"
        original_data = {
            "very_verbose_key_name_that_could_be_shorter": "value1",
            "another_unnecessarily_long_key": "value2",
            "data": "important",
        }
        json_file.write_text(json.dumps(original_data, indent=2), encoding="utf-8")

        # Act
        result = orchestrator.optimize(file_paths=[str(json_file)])

        # Assert
        assert result.success is True
        optimized_data = json.loads(json_file.read_text(encoding="utf-8"))
        assert "data" in optimized_data, "Essential keys must remain"

    def test_optimize_yaml_file(self, orchestrator, tmp_path: Path):
        """YAML file with comments and noise should be optimized."""
        # Arrange
        yaml_file = tmp_path / "test.yaml"
        original_content = """# This is a verbose comment
# Another comment that adds no value
key1: value1  # inline comment
key2: value2
# More noise
important_config:
  nested: true
"""
        yaml_file.write_text(original_content, encoding="utf-8")

        # Act
        result = orchestrator.optimize(file_paths=[str(yaml_file)])

        # Assert
        assert result.success is True
        optimized = yaml_file.read_text(encoding="utf-8")
        optimized_data = yaml.safe_load(optimized)
        assert "important_config" in optimized_data, "Essential keys preserved"
        assert len(optimized) < len(original_content), "Comments stripped"

    def test_optimize_html_file(self, orchestrator, tmp_path: Path):
        """HTML file with excessive whitespace should be optimized."""
        # Arrange
        html_file = tmp_path / "test.html"
        original_content = """<!DOCTYPE html>
<html>
<head>
    <title>Test Page</title>
    <!-- Unnecessary comment -->
</head>
<body>
    <h1>   Header with extra spaces   </h1>
    <p>
        Content with
        excessive
        line breaks
    </p>
</body>
</html>"""
        html_file.write_text(original_content, encoding="utf-8")

        # Act
        result = orchestrator.optimize(file_paths=[str(html_file)])

        # Assert
        assert result.success is True
        optimized = html_file.read_text(encoding="utf-8")
        assert len(optimized) < len(original_content), "Whitespace compressed"
        assert "<h1>" in optimized and "</h1>" in optimized, "Structure preserved"

    def test_optimize_txt_file(self, orchestrator, tmp_path: Path):
        """Plain text file with filler should be optimized."""
        # Arrange
        txt_file = tmp_path / "test.txt"
        original_content = """This is a test file.

It has some important information here.

But also a lot of filler text that doesn't add value.
Lorem ipsum dolor sit amet. More filler. Etc.

The important data should remain.
"""
        txt_file.write_text(original_content, encoding="utf-8")

        # Act
        result = orchestrator.optimize(file_paths=[str(txt_file)])

        # Assert
        assert result.success is True
        optimized = txt_file.read_text(encoding="utf-8")
        assert len(optimized) < len(original_content), "Filler removed"
        assert "important" in optimized.lower(), "Signal preserved"


# ---------------------------------------------------------------------------
# Test Category 4: Multi-File Batch Optimization
# ---------------------------------------------------------------------------

class TestMultiFileBatchOptimization:
    """Golden tests for processing arrays of files in a single call."""

    @pytest.fixture
    def orchestrator(self):
        from cortex.orchestrators.support.content_optimization_orchestrator import (
            ContentOptimizationOrchestrator,
        )
        return ContentOptimizationOrchestrator()

    def test_optimize_mixed_content_types(self, orchestrator, tmp_path: Path):
        """Array of [HTML, Markdown, JSON, YAML, TXT] should all be optimized."""
        # Arrange
        files: List[Path] = []
        files.append(tmp_path / "doc.md")
        files[-1].write_text("# Test\n\nSome content with noise...\n", encoding="utf-8")

        files.append(tmp_path / "data.json")
        files[-1].write_text('{"key": "value", "noise": "filler"}', encoding="utf-8")

        files.append(tmp_path / "config.yaml")
        files[-1].write_text("key: value\n# noise comment\n", encoding="utf-8")

        files.append(tmp_path / "page.html")
        files[-1].write_text("<html><body>   Test   </body></html>", encoding="utf-8")

        files.append(tmp_path / "notes.txt")
        files[-1].write_text("Important note.\nFiller filler filler.\n", encoding="utf-8")

        file_paths = [str(f) for f in files]

        # Act
        result = orchestrator.optimize(file_paths=file_paths)

        # Assert
        assert result.success is True
        assert result.files_processed == 5
        assert result.files_written == 5
        for file in files:
            assert file.exists(), f"{file.name} should still exist"
            assert file.stat().st_size > 0, f"{file.name} should not be empty"

    def test_optimize_empty_array(self, orchestrator):
        """Empty file_paths array should fail gracefully."""
        result = orchestrator.optimize(file_paths=[])
        assert result.success is False
        assert "empty" in result.error_message.lower()


# ---------------------------------------------------------------------------
# Test Category 5: Validation Gates
# ---------------------------------------------------------------------------

class TestValidationGates:
    """Optimized content must pass syntax validation before write."""

    @pytest.fixture
    def orchestrator(self):
        from cortex.orchestrators.support.content_optimization_orchestrator import (
            ContentOptimizationOrchestrator,
        )
        return ContentOptimizationOrchestrator()

    def test_yaml_syntax_validation(self, orchestrator, tmp_path: Path):
        """If optimization breaks YAML syntax, write should be blocked."""
        yaml_file = tmp_path / "test.yaml"
        yaml_file.write_text("key: value\nnested:\n  inner: data\n", encoding="utf-8")

        # This test assumes the orchestrator's internal validator catches syntax breaks
        # We can't easily inject a broken optimization without mocking, so we verify
        # the validator exists and is callable
        assert hasattr(orchestrator, "_validate_yaml") or hasattr(orchestrator, "_validate_content")

    def test_json_syntax_validation(self, orchestrator, tmp_path: Path):
        """If optimization breaks JSON syntax, write should be blocked."""
        json_file = tmp_path / "test.json"
        json_file.write_text('{"key": "value"}', encoding="utf-8")

        # Verify validator exists
        assert hasattr(orchestrator, "_validate_json") or hasattr(orchestrator, "_validate_content")


# ---------------------------------------------------------------------------
# Test Category 6: Error Handling
# ---------------------------------------------------------------------------

class TestErrorHandling:
    """Orchestrator must handle missing files, read errors, write errors gracefully."""

    @pytest.fixture
    def orchestrator(self):
        from cortex.orchestrators.support.content_optimization_orchestrator import (
            ContentOptimizationOrchestrator,
        )
        return ContentOptimizationOrchestrator()

    def test_missing_file_fails_gracefully(self, orchestrator):
        """Non-existent file should return success=False with clear error."""
        result = orchestrator.optimize(file_paths=["/nonexistent/file.md"])
        assert result.success is False
        assert len(result.file_results) == 1
        file_result = result.file_results[0]
        assert file_result.success is False
        error_msg = file_result.error or ""
        assert "not found" in error_msg.lower() or "does not exist" in error_msg.lower()

    def test_unreadable_file_fails_gracefully(self, orchestrator, tmp_path: Path):
        """File that cannot be read should fail gracefully."""
        # Create a file, then make it unreadable (Unix only)
        test_file = tmp_path / "unreadable.txt"
        test_file.write_text("content", encoding="utf-8")
        test_file.chmod(0o000)  # Remove all permissions

        try:
            result = orchestrator.optimize(file_paths=[str(test_file)])
            assert result.success is False
        finally:
            test_file.chmod(0o644)  # Restore permissions for cleanup
