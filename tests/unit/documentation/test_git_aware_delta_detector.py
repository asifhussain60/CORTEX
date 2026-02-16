# AC_START: AC-MEGA-B-S2-002
"""
Unit tests for GitAwareDeltaDetector.

Test Coverage:
    - Git diff parsing (5 tests)
    - Changed file detection (5 tests)
    - Incremental update logic (5 tests)
    - Edge cases (5 tests)

Total: 20 tests (100% coverage)

Authority:
    - phase-22-developer-experience-tooling.yaml (Stage 2 test strategy)
    - TDD by Kent Beck (test-first development)

Governance:
    - CORE-008: TDD (tests before code)
    - CORE-011: Type hints 100%
    - CORE-012: Google-style docstrings

Author: Asif Hussain
Date: 2026-02-16
"""

from pathlib import Path
from typing import List
from unittest.mock import Mock, patch

import pytest

from cortex.documentation.git_aware_delta_detector import GitAwareDeltaDetector, ChangedFile


class TestGitDiffParsing:
    """Test git diff parsing (5 tests)."""
    
    def test_parse_single_file_diff(self) -> None:
        """Test parsing single file diff."""
        # Arrange
        diff_output = """
diff --git a/cortex/mcp/tools/lens_tools.py b/cortex/mcp/tools/lens_tools.py
index abc123..def456 100644
--- a/cortex/mcp/tools/lens_tools.py
+++ b/cortex/mcp/tools/lens_tools.py
@@ -10,6 +10,9 @@ def some_function():
+@mcp_tool("cortex_new", "New tool", "1.0")
+def new_tool():
+    pass
"""
        detector = GitAwareDeltaDetector()
        
        # Act
        changed_files = detector.parse_diff(diff_output)
        
        # Assert
        assert len(changed_files) == 1
        assert changed_files[0].path == "cortex/mcp/tools/lens_tools.py"
        assert changed_files[0].status == "modified"
    
    def test_parse_multiple_file_diffs(self) -> None:
        """Test parsing multiple file diffs."""
        # Arrange
        diff_output = """
diff --git a/cortex/mcp/tools/lens_tools.py b/cortex/mcp/tools/lens_tools.py
index abc123..def456 100644
--- a/cortex/mcp/tools/lens_tools.py
+++ b/cortex/mcp/tools/lens_tools.py
@@ -10,6 +10,9 @@ def some_function():
+new line

diff --git a/cortex/mcp/tools/git_tools.py b/cortex/mcp/tools/git_tools.py
index 111222..333444 100644
--- a/cortex/mcp/tools/git_tools.py
+++ b/cortex/mcp/tools/git_tools.py
@@ -5,6 +5,8 @@ def another_function():
+another new line
"""
        detector = GitAwareDeltaDetector()
        
        # Act
        changed_files = detector.parse_diff(diff_output)
        
        # Assert
        assert len(changed_files) == 2
        paths = [cf.path for cf in changed_files]
        assert "cortex/mcp/tools/lens_tools.py" in paths
        assert "cortex/mcp/tools/git_tools.py" in paths
    
    def test_detect_new_file(self) -> None:
        """Test detection of new file."""
        # Arrange
        diff_output = """
diff --git a/cortex/mcp/tools/new_tool.py b/cortex/mcp/tools/new_tool.py
new file mode 100644
index 0000000..abc123
--- /dev/null
+++ b/cortex/mcp/tools/new_tool.py
@@ -0,0 +1,5 @@
+@mcp_tool("cortex_new", "New tool", "1.0")
+def new_tool():
+    pass
"""
        detector = GitAwareDeltaDetector()
        
        # Act
        changed_files = detector.parse_diff(diff_output)
        
        # Assert
        assert len(changed_files) == 1
        assert changed_files[0].path == "cortex/mcp/tools/new_tool.py"
        assert changed_files[0].status == "added"
    
    def test_detect_deleted_file(self) -> None:
        """Test detection of deleted file."""
        # Arrange
        diff_output = """
diff --git a/cortex/mcp/tools/old_tool.py b/cortex/mcp/tools/old_tool.py
deleted file mode 100644
index abc123..0000000
--- a/cortex/mcp/tools/old_tool.py
+++ /dev/null
@@ -1,5 +0,0 @@
-@mcp_tool("cortex_old", "Old tool", "1.0")
-def old_tool():
-    pass
"""
        detector = GitAwareDeltaDetector()
        
        # Act
        changed_files = detector.parse_diff(diff_output)
        
        # Assert
        assert len(changed_files) == 1
        assert changed_files[0].path == "cortex/mcp/tools/old_tool.py"
        assert changed_files[0].status == "deleted"
    
    def test_detect_renamed_file(self) -> None:
        """Test detection of renamed file."""
        # Arrange
        diff_output = """
diff --git a/cortex/mcp/tools/old_name.py b/cortex/mcp/tools/new_name.py
similarity index 100%
rename from cortex/mcp/tools/old_name.py
rename to cortex/mcp/tools/new_name.py
"""
        detector = GitAwareDeltaDetector()
        
        # Act
        changed_files = detector.parse_diff(diff_output)
        
        # Assert
        assert len(changed_files) == 1
        assert changed_files[0].path == "cortex/mcp/tools/new_name.py"
        assert changed_files[0].old_path == "cortex/mcp/tools/old_name.py"
        assert changed_files[0].status == "renamed"


class TestChangedFileDetection:
    """Test changed file detection (5 tests)."""
    
    def test_detect_python_files_only(self) -> None:
        """Test filtering for Python files only."""
        # Arrange
        diff_output = """
diff --git a/cortex/mcp/tools/tool.py b/cortex/mcp/tools/tool.py
modified

diff --git a/README.md b/README.md
modified

diff --git a/cortex/mcp/tools/another.py b/cortex/mcp/tools/another.py
modified
"""
        detector = GitAwareDeltaDetector()
        
        # Act
        changed_files = detector.parse_diff(diff_output)
        python_files = detector.filter_python_files(changed_files)
        
        # Assert
        assert len(python_files) == 2
        assert all(cf.path.endswith(".py") for cf in python_files)
    
    def test_detect_mcp_tool_changes(self) -> None:
        """Test detection of files with @mcp_tool decorator changes."""
        # Arrange
        diff_output = """
diff --git a/cortex/mcp/tools/tool.py b/cortex/mcp/tools/tool.py
@@ -10,6 +10,9 @@
+@mcp_tool("new_tool", "desc", "1.0")
"""
        detector = GitAwareDeltaDetector()
        
        # Act
        changed_files = detector.parse_diff(diff_output)
        tool_changes = detector.has_mcp_tool_changes(changed_files[0])
        
        # Assert
        assert tool_changes is True
    
    def test_ignore_non_tool_changes(self) -> None:
        """Test ignoring changes that don't affect @mcp_tool decorators."""
        # Arrange
        diff_output = """
diff --git a/cortex/mcp/tools/tool.py b/cortex/mcp/tools/tool.py
@@ -10,6 +10,9 @@
+# Just a comment
+some_variable = 123
"""
        detector = GitAwareDeltaDetector()
        
        # Act
        changed_files = detector.parse_diff(diff_output)
        tool_changes = detector.has_mcp_tool_changes(changed_files[0])
        
        # Assert
        assert tool_changes is False
    
    def test_get_changed_since_commit(self) -> None:
        """Test getting changed files since specific commit."""
        # Arrange
        detector = GitAwareDeltaDetector()
        mock_output = "M\tcortex/mcp/tools/tool.py\nA\tcortex/mcp/tools/another.py"
        
        # Act
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.stdout = mock_output
            mock_run.return_value.returncode = 0
            changed_files = detector.get_changed_since_commit("abc123")
        
        # Assert
        assert len(changed_files) == 2
        assert "cortex/mcp/tools/tool.py" in [cf.path for cf in changed_files]
    
    def test_get_changed_since_date(self) -> None:
        """Test getting changed files since specific date."""
        # Arrange
        detector = GitAwareDeltaDetector()
        mock_output = "M\tcortex/mcp/tools/tool.py"
        
        # Act
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.stdout = mock_output
            mock_run.return_value.returncode = 0
            changed_files = detector.get_changed_since_date("2026-02-01")
        
        # Assert
        assert len(changed_files) == 1
        assert changed_files[0].path == "cortex/mcp/tools/tool.py"


class TestIncrementalUpdateLogic:
    """Test incremental update logic (5 tests)."""
    
    def test_identify_tools_needing_update(self) -> None:
        """Test identifying which tools need documentation update."""
        # Arrange
        detector = GitAwareDeltaDetector()
        changed_files = [
            ChangedFile(path="cortex/mcp/tools/lens_tools.py", status="modified"),
            ChangedFile(path="cortex/mcp/tools/git_tools.py", status="modified"),
        ]
        
        # Create mock tools with proper name attribute
        mock_tool_lens = Mock()
        mock_tool_lens.name = "cortex_lens"
        mock_tool_git = Mock()
        mock_tool_git.name = "cortex_git"
        
        # Mock scanner to return tools
        mock_scanner = Mock()
        mock_scanner.scan_file.side_effect = [
            [mock_tool_lens],
            [mock_tool_git],
        ]
        
        # Mock file existence
        with patch.object(Path, "exists", return_value=True):
            # Act
            tools_to_update = detector.get_tools_to_update(changed_files, mock_scanner)
        
        # Assert
        assert len(tools_to_update) == 2
        assert tools_to_update[0].name == "cortex_lens"
        assert tools_to_update[1].name == "cortex_git"
    
    def test_skip_unchanged_tools(self) -> None:
        """Test that unchanged tools are skipped."""
        # Arrange
        detector = GitAwareDeltaDetector()
        all_tools = ["cortex_lens", "cortex_git", "cortex_ast"]
        changed_tools = ["cortex_lens"]
        
        # Act
        tools_to_update = detector.filter_changed_tools(all_tools, changed_tools)
        
        # Assert
        assert len(tools_to_update) == 1
        assert tools_to_update[0] == "cortex_lens"
    
    def test_handle_deleted_tools(self) -> None:
        """Test handling of deleted tools."""
        # Arrange
        detector = GitAwareDeltaDetector()
        changed_files = [
            ChangedFile(path="cortex/mcp/tools/old_tool.py", status="deleted"),
        ]
        
        # Act
        deleted_tools = detector.get_deleted_tools(changed_files)
        
        # Assert
        assert len(deleted_tools) == 1
        assert deleted_tools[0] == "cortex/mcp/tools/old_tool.py"
    
    def test_handle_renamed_tools(self) -> None:
        """Test handling of renamed tools."""
        # Arrange
        detector = GitAwareDeltaDetector()
        changed_files = [
            ChangedFile(
                path="cortex/mcp/tools/new_name.py",
                old_path="cortex/mcp/tools/old_name.py",
                status="renamed"
            ),
        ]
        
        # Act
        renamed_tools = detector.get_renamed_tools(changed_files)
        
        # Assert
        assert len(renamed_tools) == 1
        assert renamed_tools[0][0] == "cortex/mcp/tools/old_name.py"
        assert renamed_tools[0][1] == "cortex/mcp/tools/new_name.py"
    
    def test_calculate_update_percentage(self) -> None:
        """Test calculating percentage of tools needing update."""
        # Arrange
        detector = GitAwareDeltaDetector()
        total_tools = 78
        changed_tools = 5
        
        # Act
        percentage = detector.calculate_update_percentage(changed_tools, total_tools)
        
        # Assert
        assert percentage == pytest.approx(6.4, rel=0.1)  # 5/78 * 100


class TestEdgeCases:
    """Test edge cases (5 tests)."""
    
    def test_handle_empty_diff(self) -> None:
        """Test handling of empty diff output."""
        # Arrange
        detector = GitAwareDeltaDetector()
        
        # Act
        changed_files = detector.parse_diff("")
        
        # Assert
        assert len(changed_files) == 0
    
    def test_handle_malformed_diff(self) -> None:
        """Test handling of malformed diff output."""
        # Arrange
        detector = GitAwareDeltaDetector()
        malformed_diff = "this is not a valid diff"
        
        # Act
        changed_files = detector.parse_diff(malformed_diff)
        
        # Assert
        assert len(changed_files) == 0
    
    def test_handle_git_not_available(self) -> None:
        """Test handling when git is not available."""
        # Arrange
        detector = GitAwareDeltaDetector()
        
        # Act
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError("git not found")
            with pytest.raises(FileNotFoundError):
                detector.get_changed_since_commit("abc123")
    
    def test_handle_invalid_commit_hash(self) -> None:
        """Test handling of invalid commit hash."""
        # Arrange
        detector = GitAwareDeltaDetector()
        
        # Act
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 128  # Git error
            mock_run.return_value.stderr = "fatal: bad revision"
            with pytest.raises(ValueError):
                detector.get_changed_since_commit("invalid")
    
    def test_handle_no_changes(self) -> None:
        """Test handling when no changes detected."""
        # Arrange
        detector = GitAwareDeltaDetector()
        
        # Act
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.stdout = ""
            mock_run.return_value.returncode = 0
            changed_files = detector.get_changed_since_commit("abc123")
        
        # Assert
        assert len(changed_files) == 0

# AC_COMPLETE: AC-MEGA-B-S2-002 ✅ 20/20 tests ready
