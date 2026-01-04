"""
Unit tests for Knowledge Library (Phase -1 Discovery)

Tests:
1. AST scanning extracts classes, functions, imports
2. Duplicate detection identifies same-name entities
3. Architectural pattern detection finds orchestrators/agents
4. Knowledge graph integration queries historical risks
5. Report generation creates markdown output

Coverage Goal: 100%
"""

import pytest
import tempfile
from pathlib import Path
from cortex_agents.knowledge_library import (
    KnowledgeLibrary,
    KnowledgeDiscovery,
    CodeEntity,
    Pattern,
    quick_scan,
)


# Fixtures


@pytest.fixture
def temp_workspace():
    """Create temporary workspace with sample Python files"""
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir)

        # Create sample files
        (workspace / "module1.py").write_text(
            '''
class UserAuth:
    """User authentication class"""
    def __init__(self):
        pass
    
    def login(self, username, password):
        """Login user"""
        pass

def validate_email(email):
    """Validate email format"""
    return "@" in email
'''
        )

        (workspace / "module2.py").write_text(
            '''
class UserAuth:
    """Duplicate user authentication"""
    def __init__(self):
        pass

class DataOrchestrator:
    """Data processing orchestrator"""
    pass

def validate_email(email):
    """Duplicate email validation"""
    return "@" in email
'''
        )

        (workspace / "module3.py").write_text(
            '''
import os
from pathlib import Path

class ConfigAgent:
    """Configuration agent"""
    pass
'''
        )

        yield workspace


@pytest.fixture
def knowledge_library(temp_workspace):
    """Create KnowledgeLibrary instance"""
    return KnowledgeLibrary(str(temp_workspace))


# Tests


def test_knowledge_library_initialization(temp_workspace):
    """Test: KnowledgeLibrary initializes with workspace path"""
    library = KnowledgeLibrary(str(temp_workspace))
    assert library.workspace_path == temp_workspace
    assert isinstance(library.discovered_entities, list)
    assert len(library.discovered_entities) == 0


def test_find_python_files(knowledge_library, temp_workspace):
    """Test: _find_python_files discovers all Python files"""
    python_files = knowledge_library._find_python_files()

    assert len(python_files) == 3
    assert all(f.suffix == ".py" for f in python_files)
    assert any("module1.py" in str(f) for f in python_files)
    assert any("module2.py" in str(f) for f in python_files)
    assert any("module3.py" in str(f) for f in python_files)


def test_scan_file_extracts_classes(knowledge_library, temp_workspace):
    """Test: _scan_file extracts class definitions"""
    file_path = temp_workspace / "module1.py"
    knowledge_library._scan_file(file_path)

    classes = [e for e in knowledge_library.discovered_entities if e.type == "class"]
    assert len(classes) == 1
    assert classes[0].name == "UserAuth"
    assert classes[0].docstring == "User authentication class"


def test_scan_file_extracts_functions(knowledge_library, temp_workspace):
    """Test: _scan_file extracts function definitions"""
    file_path = temp_workspace / "module1.py"
    knowledge_library._scan_file(file_path)

    functions = [e for e in knowledge_library.discovered_entities if e.type == "function"]
    assert len(functions) >= 2  # validate_email + methods

    # Find validate_email
    validate_email = next(f for f in functions if f.name == "validate_email")
    assert "email" in validate_email.signature


def test_scan_file_extracts_imports(knowledge_library, temp_workspace):
    """Test: _scan_file extracts import statements"""
    file_path = temp_workspace / "module3.py"
    knowledge_library._scan_file(file_path)

    imports = [e for e in knowledge_library.discovered_entities if e.type == "import"]
    assert len(imports) == 2

    import_names = [i.name for i in imports]
    assert "os" in import_names
    assert "pathlib.Path" in import_names


def test_detect_duplicates_finds_same_name_classes(knowledge_library):
    """Test: _detect_duplicates finds duplicate class names"""
    discovery = knowledge_library.scan_workspace()

    # Should find UserAuth duplicate
    user_auth_dup = next((d for d in discovery.duplicate_code if "UserAuth" in d.description), None)
    assert user_auth_dup is not None
    assert user_auth_dup.severity == "high"
    assert len(user_auth_dup.locations) == 2


def test_detect_duplicates_finds_same_name_functions(knowledge_library):
    """Test: _detect_duplicates finds duplicate function names"""
    discovery = knowledge_library.scan_workspace()

    # Should find validate_email duplicate
    email_dup = next(
        (d for d in discovery.duplicate_code if "validate_email" in d.description), None
    )
    assert email_dup is not None
    assert email_dup.severity == "high"


def test_detect_architectural_patterns_finds_orchestrators(knowledge_library):
    """Test: _detect_architectural_patterns finds orchestrator pattern"""
    discovery = knowledge_library.scan_workspace()

    orchestrator_pattern = next(
        (p for p in discovery.architectural_patterns if "Orchestrator" in p.description), None
    )
    assert orchestrator_pattern is not None
    assert orchestrator_pattern.pattern_type == "architectural"


def test_detect_architectural_patterns_finds_agents(knowledge_library):
    """Test: _detect_architectural_patterns finds agent pattern"""
    discovery = knowledge_library.scan_workspace()

    agent_pattern = next(
        (p for p in discovery.architectural_patterns if "Agent" in p.description), None
    )
    assert agent_pattern is not None
    assert agent_pattern.pattern_type == "architectural"


def test_scan_workspace_returns_knowledge_discovery(knowledge_library):
    """Test: scan_workspace returns complete KnowledgeDiscovery"""
    discovery = knowledge_library.scan_workspace()

    assert isinstance(discovery, KnowledgeDiscovery)
    assert discovery.timestamp is not None
    assert discovery.workspace_path == str(knowledge_library.workspace_path)
    assert discovery.target_feature == "FULL_SCAN"
    assert len(discovery.existing_implementations) > 0
    assert "files_scanned" in discovery.scan_statistics


def test_scan_workspace_with_target_feature_filters_results(knowledge_library):
    """Test: scan_workspace with target_feature filters relevant entities"""
    discovery = knowledge_library.scan_workspace(target_feature="orchestrator")

    assert discovery.target_feature == "orchestrator"
    # Should only include entities related to orchestrator
    for entity in discovery.existing_implementations:
        entity_text = f"{entity.name} {entity.docstring or ''}".lower()
        assert "orchestrator" in entity_text


def test_generate_report_creates_markdown(knowledge_library, temp_workspace):
    """Test: generate_report creates markdown report"""
    discovery = knowledge_library.scan_workspace()
    report = knowledge_library.generate_report(discovery)

    assert "# 🔍 Knowledge Library Discovery Report" in report
    assert "## 📊 Scan Statistics" in report
    assert "## 🔁 Duplicate Code Detected" in report
    assert "## 🏗️ Architectural Patterns" in report
    assert str(discovery.scan_statistics["files_scanned"]) in report


def test_generate_report_saves_to_file(knowledge_library, temp_workspace):
    """Test: generate_report saves report to file"""
    discovery = knowledge_library.scan_workspace()
    output_path = temp_workspace / "report.md"

    report = knowledge_library.generate_report(discovery, output_path)

    assert output_path.exists()
    assert output_path.read_text() == report


def test_quick_scan_convenience_function(temp_workspace):
    """Test: quick_scan convenience function works"""
    discovery = quick_scan(str(temp_workspace))

    assert isinstance(discovery, KnowledgeDiscovery)
    assert discovery.workspace_path == str(temp_workspace)


def test_scan_ignores_syntax_errors(knowledge_library, temp_workspace):
    """Test: _scan_file handles files with syntax errors gracefully"""
    bad_file = temp_workspace / "bad_syntax.py"
    bad_file.write_text("def invalid syntax here")

    # Should not raise exception
    knowledge_library._scan_file(bad_file)
    # Should still process other files
    discovery = knowledge_library.scan_workspace()
    assert discovery.scan_statistics["files_scanned"] >= 3


def test_knowledge_discovery_scan_statistics_complete(knowledge_library):
    """Test: scan_statistics includes all required fields"""
    discovery = knowledge_library.scan_workspace()
    stats = discovery.scan_statistics

    assert "files_scanned" in stats
    assert "entities_discovered" in stats
    assert "duplicates_found" in stats
    assert "duration_seconds" in stats
    assert isinstance(stats["duration_seconds"], float)


def test_code_entity_dataclass():
    """Test: CodeEntity dataclass has correct fields"""
    entity = CodeEntity(
        name="TestClass",
        type="class",
        file_path="/path/to/file.py",
        line_number=10,
        signature=None,
        docstring="Test class docstring",
        dependencies=["BaseClass"],
    )

    assert entity.name == "TestClass"
    assert entity.type == "class"
    assert entity.line_number == 10
    assert entity.dependencies == ["BaseClass"]


def test_pattern_dataclass():
    """Test: Pattern dataclass has correct fields"""
    pattern = Pattern(
        pattern_type="duplicate",
        severity="high",
        description="Duplicate code detected",
        locations=[("/path/file1.py", 10), ("/path/file2.py", 20)],
        recommendation="Consolidate duplicate code",
    )

    assert pattern.pattern_type == "duplicate"
    assert pattern.severity == "high"
    assert len(pattern.locations) == 2


def test_load_config_returns_default_if_missing(temp_workspace):
    """Test: _load_config returns default config if cortex.config.json missing"""
    library = KnowledgeLibrary(str(temp_workspace))
    config = library._load_config()

    assert "scanning" in config
    assert "exclude_patterns" in config["scanning"]
    assert "*/tests/*" in config["scanning"]["exclude_patterns"]


# Integration Tests


def test_full_workflow_scan_and_report(temp_workspace):
    """Integration Test: Full scan → report workflow"""
    library = KnowledgeLibrary(str(temp_workspace))
    discovery = library.scan_workspace(target_feature="auth")
    report_path = temp_workspace / "discovery-report.md"

    report = library.generate_report(discovery, report_path)

    # Verify workflow completed
    assert discovery.scan_statistics["files_scanned"] > 0
    assert len(discovery.duplicate_code) > 0
    assert report_path.exists()
    assert "# 🔍 Knowledge Library Discovery Report" in report


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
