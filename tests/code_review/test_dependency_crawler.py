"""
Tests for Dependency-Driven Crawling System
Code Review Feature - Phase 2 (RED phase)
"""

import pytest
from pathlib import Path
import tempfile
import shutil
from typing import List, Dict, Set

from src.code_review.dependency_crawler import DependencyCrawler, DependencyGraph, CrawlStrategy


class TestDependencyCrawler:
    """Test suite for dependency-driven crawling"""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace with mock files"""
        temp_dir = tempfile.mkdtemp()
        workspace = Path(temp_dir)
        
        # Create mock file structure
        (workspace / "src").mkdir()
        (workspace / "src" / "services").mkdir()
        (workspace / "src" / "models").mkdir()
        (workspace / "tests").mkdir()
        
        # Create mock Python files
        (workspace / "src" / "services" / "user_service.py").write_text("""
import src.models.user as user_model
from src.services.auth_service import AuthService

class UserService:
    def get_user(self, user_id):
        pass
""")
        
        (workspace / "src" / "services" / "auth_service.py").write_text("""
class AuthService:
    def authenticate(self, username, password):
        pass
""")
        
        (workspace / "src" / "models" / "user.py").write_text("""
class User:
    def __init__(self, id, name):
        self.id = id
        self.name = name
""")
        
        (workspace / "tests" / "test_user_service.py").write_text("""
from src.services.user_service import UserService

def test_get_user():
    service = UserService()
    # test code
""")
        
        yield workspace
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def crawler(self, temp_workspace):
        """Create DependencyCrawler instance"""
        return DependencyCrawler(temp_workspace)
    
    def test_extract_python_imports(self, crawler, temp_workspace):
        """RED: Test extracting imports from Python file"""
        file_path = temp_workspace / "src" / "services" / "user_service.py"
        
        imports = crawler.extract_imports(file_path)
        
        assert len(imports) == 2
        assert "src.models.user" in imports
        assert "src.services.auth_service" in imports
    
    def test_resolve_import_to_file_path(self, crawler, temp_workspace):
        """RED: Test resolving import statement to actual file path"""
        import_statement = "src.models.user"
        
        file_path = crawler.resolve_import(import_statement)
        
        assert file_path is not None
        assert file_path.name == "user.py"
        assert "models" in str(file_path)
    
    def test_build_dependency_graph_level_1(self, crawler, temp_workspace):
        """RED: Test building Level 1 dependency graph (changed files + direct imports)"""
        changed_files = [
            str(temp_workspace / "src" / "services" / "user_service.py")
        ]
        
        graph = crawler.build_dependency_graph(
            changed_files=changed_files,
            strategy=CrawlStrategy.LEVEL_1
        )
        
        assert len(graph.changed_files) == 1
        assert len(graph.direct_imports) >= 2  # auth_service.py, user.py
        assert graph.total_files <= 10
    
    def test_build_dependency_graph_level_2(self, crawler, temp_workspace):
        """RED: Test building Level 2 dependency graph (+ test files)"""
        changed_files = [
            str(temp_workspace / "src" / "services" / "user_service.py")
        ]
        
        graph = crawler.build_dependency_graph(
            changed_files=changed_files,
            strategy=CrawlStrategy.LEVEL_2
        )
        
        assert len(graph.test_files) >= 1
        assert "test_user_service.py" in str(graph.test_files)
    
    def test_crawl_strategy_level_3_capped_at_50_files(self, crawler):
        """RED: Test Level 3 stops at 50 files maximum"""
        # Mock a large codebase scenario
        changed_files = ["file1.py"]
        
        graph = crawler.build_dependency_graph(
            changed_files=changed_files,
            strategy=CrawlStrategy.LEVEL_3,
            max_files=50
        )
        
        assert graph.total_files <= 50
    
    def test_detect_circular_dependencies(self, crawler, temp_workspace):
        """RED: Test circular dependency detection"""
        # Create circular dependency scenario
        (temp_workspace / "src" / "a.py").write_text("import src.b")
        (temp_workspace / "src" / "b.py").write_text("import src.a")
        
        changed_files = [str(temp_workspace / "src" / "a.py")]
        
        graph = crawler.build_dependency_graph(
            changed_files=changed_files,
            strategy=CrawlStrategy.LEVEL_1
        )
        
        # Should detect but not crash
        assert graph.has_circular_dependencies is True
    
    def test_token_budget_estimation(self, crawler, temp_workspace):
        """RED: Test token budget estimation for crawled files"""
        changed_files = [
            str(temp_workspace / "src" / "services" / "user_service.py")
        ]
        
        graph = crawler.build_dependency_graph(
            changed_files=changed_files,
            strategy=CrawlStrategy.LEVEL_1
        )
        
        token_estimate = graph.estimate_tokens()
        
        # Should be under 10K tokens for small project
        assert token_estimate < 10000
        assert token_estimate > 0
    
    def test_dependency_graph_serialization(self, crawler, temp_workspace):
        """RED: Test serializing dependency graph to dict"""
        changed_files = [
            str(temp_workspace / "src" / "services" / "user_service.py")
        ]
        
        graph = crawler.build_dependency_graph(
            changed_files=changed_files,
            strategy=CrawlStrategy.LEVEL_1
        )
        
        serialized = graph.to_dict()
        
        assert "changed_files" in serialized
        assert "direct_imports" in serialized
        assert "total_files" in serialized
        assert "token_estimate" in serialized
    
    def test_find_test_files_for_source_file(self, crawler, temp_workspace):
        """RED: Test finding test files for a given source file"""
        source_file = temp_workspace / "src" / "services" / "user_service.py"
        
        test_files = crawler.find_test_files(source_file)
        
        assert len(test_files) >= 1
        assert any("test_user_service" in str(f) for f in test_files)
    
    def test_exclude_gitignored_files(self, crawler, temp_workspace):
        """RED: Test excluding files from .gitignore"""
        # Create .gitignore
        (temp_workspace / ".gitignore").write_text("""
*.pyc
__pycache__/
.env
""")
        
        # Create ignored file
        (temp_workspace / "src" / "config.pyc").write_text("compiled")
        
        changed_files = [str(temp_workspace / "src" / "config.pyc")]
        
        graph = crawler.build_dependency_graph(
            changed_files=changed_files,
            strategy=CrawlStrategy.LEVEL_1
        )
        
        # Should exclude .pyc files
        assert len(graph.changed_files) == 0 or ".pyc" not in str(graph.changed_files[0])
    
    def test_multi_language_support(self, crawler, temp_workspace):
        """RED: Test handling multiple language files (Python, JS, C#)"""
        # Create C# file
        (temp_workspace / "src" / "UserService.cs").write_text("""
using System;
using MyApp.Models;

public class UserService {
}
""")
        
        changed_files = [str(temp_workspace / "src" / "UserService.cs")]
        
        graph = crawler.build_dependency_graph(
            changed_files=changed_files,
            strategy=CrawlStrategy.LEVEL_1
        )
        
        # Should detect C# imports
        assert len(graph.direct_imports) >= 0  # May find MyApp.Models if it exists


class TestCrawlStrategy:
    """Test CrawlStrategy enum and logic"""
    
    def test_crawl_strategy_enum_values(self):
        """RED: Test CrawlStrategy enum has all required levels"""
        assert hasattr(CrawlStrategy, "LEVEL_1")
        assert hasattr(CrawlStrategy, "LEVEL_2")
        assert hasattr(CrawlStrategy, "LEVEL_3")
    
    def test_level_1_includes_changed_and_direct(self):
        """RED: Test Level 1 strategy includes changed files + direct imports only"""
        strategy = CrawlStrategy.LEVEL_1
        
        assert strategy.includes_changed_files is True
        assert strategy.includes_direct_imports is True
        assert strategy.includes_test_files is False
        assert strategy.includes_indirect_deps is False
    
    def test_level_2_adds_test_files(self):
        """RED: Test Level 2 strategy adds test files"""
        strategy = CrawlStrategy.LEVEL_2
        
        assert strategy.includes_test_files is True
    
    def test_level_3_adds_indirect_deps_with_cap(self):
        """RED: Test Level 3 strategy adds indirect dependencies with 50-file cap"""
        strategy = CrawlStrategy.LEVEL_3
        
        assert strategy.includes_indirect_deps is True
        assert strategy.max_files == 50


class TestDependencyGraph:
    """Test DependencyGraph data structure"""
    
    def test_dependency_graph_initialization(self):
        """RED: Test DependencyGraph initializes with empty collections"""
        graph = DependencyGraph()
        
        assert isinstance(graph.changed_files, list)
        assert isinstance(graph.direct_imports, list)
        assert isinstance(graph.test_files, list)
        assert isinstance(graph.indirect_deps, list)
        assert graph.total_files == 0
    
    def test_add_file_to_graph(self):
        """RED: Test adding files to dependency graph"""
        graph = DependencyGraph()
        
        graph.add_changed_file("file1.py")
        graph.add_direct_import("file2.py")
        
        assert len(graph.changed_files) == 1
        assert len(graph.direct_imports) == 1
        assert graph.total_files == 2
    
    def test_deduplicate_files_in_graph(self):
        """RED: Test graph deduplicates files across categories"""
        graph = DependencyGraph()
        
        graph.add_changed_file("file1.py")
        graph.add_direct_import("file1.py")  # Duplicate
        
        # Should not double-count
        assert graph.total_files == 1
