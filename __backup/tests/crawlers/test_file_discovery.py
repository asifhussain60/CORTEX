"""
Tests for AC-CRAWLER-005: File Discovery and Filtering
"""
import pytest
import tempfile
import os
from pathlib import Path
from src.crawlers.file_discovery import FileDiscovery, GitignoreParser, FileStats


class TestGitignoredParser:
    """Test .gitignore pattern parsing"""

    def test_gitignore_parser_loads_patterns(self):
        """Test parser loads patterns from .gitignore"""
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".gitignore",
            delete=False,
        ) as f:
            f.write("*.pyc\n__pycache__\n.env\n")
            f.flush()

            parser = GitignoreParser(f.name)

            assert "*.pyc" in parser.patterns
            assert "__pycache__" in parser.patterns
            assert ".env" in parser.patterns

        Path(f.name).unlink()

    def test_gitignore_parser_ignores_comments(self):
        """Test parser ignores comment lines"""
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".gitignore",
            delete=False,
        ) as f:
            f.write("# Comment\n*.pyc\n# Another comment\n.env\n")
            f.flush()

            parser = GitignoreParser(f.name)

            assert len(parser.patterns) == 2
            assert "*.pyc" in parser.patterns
            assert ".env" in parser.patterns

        Path(f.name).unlink()

    def test_gitignore_parser_handles_negation(self):
        """Test parser handles negation patterns"""
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".gitignore",
            delete=False,
        ) as f:
            f.write("*.log\n!important.log\n")
            f.flush()

            parser = GitignoreParser(f.name)

            assert "*.log" in parser.patterns
            assert "important.log" in parser.negation_patterns

        Path(f.name).unlink()

    def test_gitignore_parser_should_ignore(self):
        """Test pattern matching for should_ignore"""
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".gitignore",
            delete=False,
        ) as f:
            f.write("*.pyc\n__pycache__\n")
            f.flush()

            parser = GitignoreParser(f.name)

            assert parser.should_ignore("test.pyc")
            assert parser.should_ignore("__pycache__")
            assert not parser.should_ignore("test.py")

        Path(f.name).unlink()

    def test_gitignore_parser_negation_overrides(self):
        """Test negation patterns override ignore patterns"""
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".gitignore",
            delete=False,
        ) as f:
            f.write("*.log\n!important.log\n")
            f.flush()

            parser = GitignoreParser(f.name)

            assert parser.should_ignore("debug.log")
            assert not parser.should_ignore("important.log")

        Path(f.name).unlink()


class TestFileDiscovery:
    """AC-CRAWLER-005: File discovery tests"""

    def test_file_discovery_initialization(self):
        """Test file discovery initializes correctly"""
        with tempfile.TemporaryDirectory() as tmpdir:
            discovery = FileDiscovery(tmpdir)

            assert discovery.root_path == Path(tmpdir)
            assert discovery.max_file_size_bytes > 0

    def test_discover_python_files(self):
        """Test discovering Python files"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            Path(tmpdir, "test1.py").write_text("# python")
            Path(tmpdir, "test2.py").write_text("# python")
            Path(tmpdir, "test.txt").write_text("# text")

            discovery = FileDiscovery(tmpdir)
            files = discovery.discover()

            assert len(files) == 3  # All files discovered

    def test_discover_by_include_pattern(self):
        """Test discovery with include patterns"""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "test.py").write_text("# python")
            Path(tmpdir, "data.json").write_text("{}")

            discovery = FileDiscovery(
                tmpdir,
                include_patterns=["**/*.py"],
            )
            files = discovery.discover()

            assert len(files) == 1
            assert files[0].endswith(".py")

    def test_discover_by_exclude_pattern(self):
        """Test discovery with exclude patterns"""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "test.py").write_text("# python")
            Path(tmpdir, "test_backup.py").write_text("# backup")

            discovery = FileDiscovery(
                tmpdir,
                include_patterns=["**/*.py"],
                exclude_patterns=["**/test_backup.py"],
            )
            files = discovery.discover()

            assert len(files) == 1
            assert "test.py" in files[0]
            assert "test_backup.py" not in files[0]

    def test_discover_respects_gitignore(self):
        """Test discovery respects .gitignore"""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "test.py").write_text("# python")
            Path(tmpdir, "test.pyc").write_text("# compiled")
            Path(tmpdir, ".gitignore").write_text("*.pyc\n")

            discovery = FileDiscovery(tmpdir, respect_gitignore=True)
            files = discovery.discover()

            assert len(files) == 2  # .gitignore + test.py (test.pyc excluded)
            assert not any(f.endswith(".pyc") for f in files)

    def test_discover_by_language(self):
        """Test discovering files by language"""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "test.py").write_text("# python")
            Path(tmpdir, "script.js").write_text("// js")
            Path(tmpdir, "style.css").write_text("/* css */")

            discovery = FileDiscovery(tmpdir)
            python_files = discovery.discover_by_language("python")

            assert len(python_files) == 1
            assert python_files[0].endswith(".py")

    def test_discover_multiple_languages(self):
        """Test discovery for multiple language extensions"""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "app.ts").write_text("// ts")
            Path(tmpdir, "component.tsx").write_text("// tsx")

            discovery = FileDiscovery(tmpdir)
            ts_files = discovery.discover_by_language("typescript")

            assert len(ts_files) == 2

    def test_get_statistics(self):
        """Test getting discovery statistics"""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "test1.py").write_text("# python\n")
            Path(tmpdir, "test2.py").write_text("# python\n")
            Path(tmpdir, "data.json").write_text("{}\n")

            discovery = FileDiscovery(tmpdir)
            stats = discovery.get_statistics()

            assert stats.total_files >= 3
            assert ".py" in stats.by_extension
            assert ".json" in stats.by_extension
            assert stats.total_size_bytes > 0

    def test_discover_respects_file_size_limit(self):
        """Test discovery respects file size limits"""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "small.py").write_text("# small")
            large_file = Path(tmpdir, "large.py")
            large_file.write_text("x" * (100 * 1024 * 1024))  # 100MB

            discovery = FileDiscovery(tmpdir, max_file_size_mb=50)
            files = discovery.discover()

            # Should only find small.py
            assert len([f for f in files if f.endswith(".py")]) <= 1

        # Cleanup
        if large_file.exists():
            large_file.unlink()

    def test_file_discovery_empty_directory(self):
        """Test discovery on empty directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            discovery = FileDiscovery(tmpdir)
            files = discovery.discover()

            assert len(files) == 0

    def test_language_extension_mapping(self):
        """Test language to extension mapping"""
        discovery = FileDiscovery(".")

        python_exts = discovery.LANGUAGE_EXTENSIONS["python"]
        assert ".py" in python_exts

        csharp_exts = discovery.LANGUAGE_EXTENSIONS["csharp"]
        assert ".cs" in csharp_exts

        javascript_exts = discovery.LANGUAGE_EXTENSIONS["javascript"]
        assert ".js" in javascript_exts

    def test_discover_mixed_tech_stack(self):
        """Test discovery with mixed tech stack"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Mixed tech stack
            Path(tmpdir, "backend.py").write_text("# python")
            Path(tmpdir, "App.cs").write_text("// csharp")
            Path(tmpdir, "component.tsx").write_text("// react")
            Path(tmpdir, "query.sql").write_text("-- sql")
            Path(tmpdir, "config.yaml").write_text("# yaml")

            discovery = FileDiscovery(tmpdir)
            files = discovery.discover()

            assert len(files) == 5

            # Verify each language can be discovered
            assert len(discovery.discover_by_language("python")) == 1
            assert len(discovery.discover_by_language("csharp")) == 1
            assert len(discovery.discover_by_language("typescript")) == 1
            assert len(discovery.discover_by_language("sql")) == 1
            assert len(discovery.discover_by_language("yaml")) == 1
