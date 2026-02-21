"""
Unit tests for ScaffoldWriter — disk-emission of workflow scaffold_files.

AC_START: AC-BADMONOLITH-G2-001
Description: RED tests for ScaffoldWriter that writes scaffold_files to disk
             after each WorkflowEngine step, enabling the next step's
             depends_on gate to find the files it expects.
Authority: CORE-008 (TDD-first), CORE-011 (type hints), CORE-012 (docstrings)

These tests must FAIL before ScaffoldWriter is implemented.
"""

import json
from pathlib import Path

import pytest

from cortex.core.scaffold_writer import ScaffoldFile, ScaffoldWriter


class TestScaffoldFile:
    """Test ScaffoldFile dataclass construction."""

    def test_scaffold_file_requires_path_and_content(self, tmp_path: Path) -> None:
        """ScaffoldFile must store path and content."""
        sf = ScaffoldFile(path=tmp_path / "ITaskRepository.cs", content="public interface ITaskRepository {}")
        assert sf.path == tmp_path / "ITaskRepository.cs"
        assert "ITaskRepository" in sf.content

    def test_scaffold_file_optional_overwrite_defaults_true(self, tmp_path: Path) -> None:
        """overwrite defaults to True — new files always written."""
        sf = ScaffoldFile(path=tmp_path / "Foo.cs", content="class Foo {}")
        assert sf.overwrite is True

    def test_scaffold_file_overwrite_false_skips_existing(self, tmp_path: Path) -> None:
        """overwrite=False: existing file must not be changed."""
        existing = tmp_path / "Existing.cs"
        existing.write_text("original content")

        sf = ScaffoldFile(path=existing, content="NEW content", overwrite=False)
        writer = ScaffoldWriter(root=tmp_path)
        written = writer.emit([sf])

        assert written == []  # nothing written
        assert existing.read_text() == "original content"


class TestScaffoldWriterEmit:
    """Test ScaffoldWriter.emit() — writes files to disk, returns written paths."""

    def test_emit_single_file(self, tmp_path: Path) -> None:
        """emit() writes a single ScaffoldFile to disk."""
        writer = ScaffoldWriter(root=tmp_path)
        sf = ScaffoldFile(
            path=tmp_path / "ITaskRepository.cs",
            content="public interface ITaskRepository { }",
        )
        written = writer.emit([sf])

        assert len(written) == 1
        assert written[0] == tmp_path / "ITaskRepository.cs"
        assert (tmp_path / "ITaskRepository.cs").read_text() == "public interface ITaskRepository { }"

    def test_emit_creates_parent_directories(self, tmp_path: Path) -> None:
        """emit() must create missing parent directories (mkdir -p)."""
        nested = tmp_path / "Repositories" / "Tasks" / "ITaskRepository.cs"
        writer = ScaffoldWriter(root=tmp_path)
        sf = ScaffoldFile(path=nested, content="public interface ITaskRepository { }")

        written = writer.emit([sf])

        assert nested.exists()
        assert len(written) == 1

    def test_emit_multiple_files_returns_all_written_paths(self, tmp_path: Path) -> None:
        """emit() writes all files and returns every written path."""
        writer = ScaffoldWriter(root=tmp_path)
        files = [
            ScaffoldFile(path=tmp_path / "ITaskRepository.cs", content="interface ITaskRepository {}"),
            ScaffoldFile(path=tmp_path / "TaskRepository.cs", content="class TaskRepository {}"),
            ScaffoldFile(path=tmp_path / "TaskDbContext.cs", content="class TaskDbContext {}"),
        ]

        written = writer.emit(files)

        assert len(written) == 3
        for sf in files:
            assert sf.path.exists()

    def test_emit_overwrites_existing_by_default(self, tmp_path: Path) -> None:
        """emit() replaces existing file content when overwrite=True (default)."""
        target = tmp_path / "Task.cs"
        target.write_text("OLD content")

        writer = ScaffoldWriter(root=tmp_path)
        sf = ScaffoldFile(path=target, content="NEW content")
        writer.emit([sf])

        assert target.read_text() == "NEW content"

    def test_emit_skips_existing_when_overwrite_false(self, tmp_path: Path) -> None:
        """emit() skips files that already exist when overwrite=False."""
        target = tmp_path / "Task.cs"
        target.write_text("KEEP ME")

        writer = ScaffoldWriter(root=tmp_path)
        sf = ScaffoldFile(path=target, content="DISCARD", overwrite=False)
        written = writer.emit([sf])

        assert written == []
        assert target.read_text() == "KEEP ME"

    def test_emit_empty_list_returns_empty(self, tmp_path: Path) -> None:
        """emit() with no files returns empty list without error."""
        writer = ScaffoldWriter(root=tmp_path)
        assert writer.emit([]) == []

    def test_emit_returns_only_actually_written_paths(self, tmp_path: Path) -> None:
        """emit() returns only paths that were actually written to disk."""
        existing = tmp_path / "Existing.cs"
        existing.write_text("original")
        new_file = tmp_path / "New.cs"

        writer = ScaffoldWriter(root=tmp_path)
        files = [
            ScaffoldFile(path=existing, content="skip me", overwrite=False),
            ScaffoldFile(path=new_file, content="write me"),
        ]
        written = writer.emit(files)

        assert written == [new_file]


class TestScaffoldWriterFromStepOutput:
    """Test ScaffoldWriter.from_step_output() — parses workflow step output_keys."""

    def test_from_step_output_parses_scaffold_files_key(self, tmp_path: Path) -> None:
        """from_step_output extracts ScaffoldFile list from step result dict."""
        step_output = {
            "status": "complete",
            "scaffold_files": [
                {"path": str(tmp_path / "ITaskRepository.cs"), "content": "public interface ITaskRepository {}"},
                {"path": str(tmp_path / "TaskRepository.cs"), "content": "public class TaskRepository {}"},
            ],
            "test_results": {"passed": 0, "failed": 0},
        }

        writer = ScaffoldWriter(root=tmp_path)
        files = writer.from_step_output(step_output)

        assert len(files) == 2
        assert all(isinstance(f, ScaffoldFile) for f in files)
        assert files[0].path == tmp_path / "ITaskRepository.cs"

    def test_from_step_output_empty_when_no_scaffold_files_key(self) -> None:
        """from_step_output returns empty list when scaffold_files key missing."""
        step_output = {"status": "complete", "test_results": {}}
        writer = ScaffoldWriter(root=Path("/tmp"))
        assert writer.from_step_output(step_output) == []

    def test_from_step_output_empty_when_scaffold_files_is_none(self) -> None:
        """from_step_output returns empty list when scaffold_files is None."""
        step_output = {"status": "complete", "scaffold_files": None}
        writer = ScaffoldWriter(root=Path("/tmp"))
        assert writer.from_step_output(step_output) == []

    def test_from_step_output_respects_overwrite_flag(self, tmp_path: Path) -> None:
        """from_step_output passes overwrite=False when scaffold entry says so."""
        step_output = {
            "scaffold_files": [
                {
                    "path": str(tmp_path / "Task.cs"),
                    "content": "class Task {}",
                    "overwrite": False,
                }
            ]
        }
        writer = ScaffoldWriter(root=tmp_path)
        files = writer.from_step_output(step_output)

        assert files[0].overwrite is False

    # ── BadMonolith scenario ─────────────────────────────────────────────────

    def test_badmonolith_data_layer_scaffold_emitted_to_disk(self, tmp_path: Path) -> None:
        """Simulate Step 2 (layer_data_access) scaffold_files landing on disk."""
        step_output = {
            "status": "complete",
            "scaffold_files": [
                {
                    "path": str(tmp_path / "Repositories" / "ITaskRepository.cs"),
                    "content": (
                        "namespace TaskManager.Repositories {\n"
                        "    public interface ITaskRepository {\n"
                        "        Task<IEnumerable<TaskEntity>> GetAllAsync(int skip, int take);\n"
                        "        Task<TaskEntity?> GetByIdAsync(int id);\n"
                        "        Task<TaskEntity> CreateAsync(CreateTaskDto dto);\n"
                        "        Task<TaskEntity> UpdateAsync(int id, UpdateTaskDto dto);\n"
                        "        Task DeleteAsync(int id);\n"
                        "    }\n"
                        "}"
                    ),
                },
                {
                    "path": str(tmp_path / "Repositories" / "TaskRepository.cs"),
                    "content": (
                        "namespace TaskManager.Repositories {\n"
                        "    public class TaskRepository : ITaskRepository { }\n"
                        "}"
                    ),
                },
                {
                    "path": str(tmp_path / "Data" / "TaskDbContext.cs"),
                    "content": (
                        "namespace TaskManager.Data {\n"
                        "    public class TaskDbContext : DbContext { }\n"
                        "}"
                    ),
                },
            ],
        }

        writer = ScaffoldWriter(root=tmp_path)
        files = writer.from_step_output(step_output)
        written = writer.emit(files)

        assert len(written) == 3
        assert (tmp_path / "Repositories" / "ITaskRepository.cs").exists()
        assert (tmp_path / "Repositories" / "TaskRepository.cs").exists()
        assert (tmp_path / "Data" / "TaskDbContext.cs").exists()
        content = (tmp_path / "Repositories" / "ITaskRepository.cs").read_text()
        assert "ITaskRepository" in content
        assert "GetAllAsync" in content


# AC_COMPLETE: AC-BADMONOLITH-G2-001 ✅ RED tests for ScaffoldWriter
