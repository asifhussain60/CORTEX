"""
Unit tests for RoslynAdapter symbol-name resolution (by_name rename mode).

AC_START: AC-BADMONOLITH-G3-001
Description: RED tests for by_name rename — symbol_name param instead of byte offset.
Authority: CORE-008 (TDD-first), CORE-011 (type hints), CORE-012 (docstrings)

These tests must FAIL before the implementation is added.
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from cortex.orchestrators.domain.refactoring.adapters.roslyn_adapter import RoslynAdapter
from cortex.orchestrators.domain.refactoring.refactoring_models import (
    RefactoringLanguage,
    RefactoringRequest,
    RefactoringResult,
)
from cortex.core.result import Ok, Err


class TestRoslynAdapterByNameRename:
    """Test symbol-name resolution mode for rename (no byte offset required)."""

    # ── validation ────────────────────────────────────────────────────────────

    def test_validate_rename_by_name_passes_without_offset(self, tmp_path: Path) -> None:
        """Validation must accept rename when symbol_name given but no offset."""
        cs_file = tmp_path / "Task.cs"
        cs_file.write_text("namespace BadMonolith.Models { public class Task { } }")

        adapter = RoslynAdapter()
        request = RefactoringRequest(
            operation="rename",
            file_path=cs_file,
            language=RefactoringLanguage.CSHARP,
            parameters={"symbol_name": "Task", "new_name": "TaskEntity"},
        )

        with patch.object(adapter._process_manager, "is_available", return_value=True):
            result = adapter.validate_request(request)

        assert result.is_ok(), f"Expected Ok but got Err: {result}"

    def test_validate_rename_still_works_with_offset(self, tmp_path: Path) -> None:
        """Existing offset-based rename must still pass validation (no regression)."""
        cs_file = tmp_path / "Program.cs"
        cs_file.write_text("class Foo { }")

        adapter = RoslynAdapter()
        request = RefactoringRequest(
            operation="rename",
            file_path=cs_file,
            language=RefactoringLanguage.CSHARP,
            parameters={"offset": 6, "new_name": "Bar"},
        )

        with patch.object(adapter._process_manager, "is_available", return_value=True):
            result = adapter.validate_request(request)

        assert result.is_ok()

    def test_validate_rename_fails_without_offset_or_symbol_name(self, tmp_path: Path) -> None:
        """Validation must fail when neither offset nor symbol_name is provided."""
        cs_file = tmp_path / "Foo.cs"
        cs_file.write_text("class Foo { }")

        adapter = RoslynAdapter()
        request = RefactoringRequest(
            operation="rename",
            file_path=cs_file,
            language=RefactoringLanguage.CSHARP,
            parameters={"new_name": "Bar"},  # no offset, no symbol_name
        )

        with patch.object(adapter._process_manager, "is_available", return_value=True):
            result = adapter.validate_request(request)

        assert result.is_err()
        assert "offset" in str(result.unwrap_err()).lower() or "symbol_name" in str(result.unwrap_err()).lower()

    def test_validate_rename_fails_without_new_name(self, tmp_path: Path) -> None:
        """Validation must fail when new_name is missing regardless of lookup mode."""
        cs_file = tmp_path / "Foo.cs"
        cs_file.write_text("class Foo { }")

        adapter = RoslynAdapter()
        request = RefactoringRequest(
            operation="rename",
            file_path=cs_file,
            language=RefactoringLanguage.CSHARP,
            parameters={"symbol_name": "Foo"},  # no new_name
        )

        with patch.object(adapter._process_manager, "is_available", return_value=True):
            result = adapter.validate_request(request)

        assert result.is_err()
        assert "new_name" in str(result.unwrap_err()).lower()

    # ── command building ──────────────────────────────────────────────────────

    def test_by_name_command_includes_symbol_name_key(self, tmp_path: Path) -> None:
        """The Roslyn command sent over JSON-RPC must include symbol_name when provided."""
        cs_file = tmp_path / "Task.cs"
        cs_file.write_text("namespace N { public class Task { } }")

        adapter = RoslynAdapter()
        request = RefactoringRequest(
            operation="rename",
            file_path=cs_file,
            language=RefactoringLanguage.CSHARP,
            parameters={"symbol_name": "Task", "new_name": "TaskEntity"},
        )

        captured_commands: list[dict] = []

        def fake_send(cmd: dict):  # type: ignore[no-untyped-def]
            captured_commands.append(cmd)
            return Ok(
                {
                    "success": True,
                    "modified_files": [str(cs_file)],
                    "description": "Renamed Task → TaskEntity",
                    "warnings": [],
                    "metadata": {},
                }
            )

        with (
            patch.object(adapter._process_manager, "is_available", return_value=True),
            patch.object(adapter._process_manager, "is_running", return_value=True),
            patch.object(adapter._process_manager, "send_command", side_effect=fake_send),
        ):
            result = adapter.execute_refactoring(request)

        assert result.is_ok(), f"Expected Ok but got: {result}"
        assert len(captured_commands) == 1
        cmd = captured_commands[0]
        assert cmd["parameters"].get("symbol_name") == "Task"
        assert cmd["parameters"].get("new_name") == "TaskEntity"
        assert "offset" not in cmd["parameters"]

    # ── end-to-end with mock process ─────────────────────────────────────────

    def test_execute_rename_by_name_returns_ok_result(self, tmp_path: Path) -> None:
        """execute_refactoring with symbol_name must return Ok(RefactoringResult)."""
        cs_file = tmp_path / "Task.cs"
        cs_file.write_text("namespace BadMonolith { public class Task { } }")

        adapter = RoslynAdapter()
        request = RefactoringRequest(
            operation="rename",
            file_path=cs_file,
            language=RefactoringLanguage.CSHARP,
            parameters={"symbol_name": "Task", "new_name": "TaskEntity"},
        )

        mock_response = {
            "success": True,
            "modified_files": [str(cs_file)],
            "description": "Renamed 'Task' to 'TaskEntity'",
            "warnings": [],
            "metadata": {"symbol_kind": "class"},
        }

        with (
            patch.object(adapter._process_manager, "is_available", return_value=True),
            patch.object(adapter._process_manager, "is_running", return_value=True),
            patch.object(
                adapter._process_manager, "send_command", return_value=Ok(mock_response)
            ),
        ):
            result = adapter.execute_refactoring(request)

        assert result.is_ok()
        refactoring_result = result.unwrap()
        assert refactoring_result.success is True
        assert cs_file in refactoring_result.modified_files
        assert "TaskEntity" in refactoring_result.description

    def test_execute_rename_by_name_badmonolith_task_to_task_entity(
        self, tmp_path: Path
    ) -> None:
        """Smoke test: rename BadMonolith Task → TaskEntity, Task.cs file."""
        cs_file = tmp_path / "Task.cs"
        cs_file.write_text(
            "namespace BadMonolith.Models {\n"
            "    public class Task {\n"
            "        public int Id { get; set; }\n"
            "        public string Title { get; set; }\n"
            "        public bool IsCompleted { get; set; }\n"
            "    }\n"
            "}"
        )

        adapter = RoslynAdapter()
        request = RefactoringRequest(
            operation="rename",
            file_path=cs_file,
            language=RefactoringLanguage.CSHARP,
            parameters={"symbol_name": "Task", "new_name": "TaskEntity"},
        )

        with (
            patch.object(adapter._process_manager, "is_available", return_value=True),
            patch.object(adapter._process_manager, "is_running", return_value=True),
            patch.object(
                adapter._process_manager,
                "send_command",
                return_value=Ok(
                    {
                        "success": True,
                        "modified_files": [str(cs_file)],
                        "description": "Renamed class 'Task' to 'TaskEntity'",
                        "warnings": [],
                        "metadata": {},
                    }
                ),
            ),
        ):
            result = adapter.execute_refactoring(request)

        assert result.is_ok()
        r = result.unwrap()
        assert r.success is True
        assert "TaskEntity" in r.description


# AC_COMPLETE: AC-BADMONOLITH-G3-001 ✅ RED tests for by_name rename
