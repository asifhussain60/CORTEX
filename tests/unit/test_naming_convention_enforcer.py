"""
Naming convention enforcer tests.

Tests file type detection and automatic rule application for different file types.
"""

import pytest
from pathlib import Path


class TestNamingConventionEnforcer:
    """Test naming convention enforcement."""
    
    def test_enforces_snake_case_for_python(self):
        """Should enforce snake_case for Python files."""
        from src.governance.naming_convention_enforcer import NamingConventionEnforcer
        
        enforcer = NamingConventionEnforcer()
        
        # Valid Python files
        assert enforcer.check("user_service.py") is True
        assert enforcer.check("test_user_service.py") is True
        
        # Invalid Python files (camelCase)
        assert enforcer.check("userService.py") is False
        assert enforcer.check("UserService.py") is False
    
    def test_enforces_kebab_case_for_markdown(self):
        """Should enforce kebab-case for markdown files."""
        from src.governance.naming_convention_enforcer import NamingConventionEnforcer
        
        enforcer = NamingConventionEnforcer()
        
        # Valid markdown files
        assert enforcer.check("user-guide.md") is True
        assert enforcer.check("api-documentation.md") is True
        
        # Invalid markdown files (snake_case)
        assert enforcer.check("user_guide.md") is False
        assert enforcer.check("api_documentation.md") is False
    
    def test_enforces_kebab_case_for_yaml(self):
        """Should enforce kebab-case for YAML files."""
        from src.governance.naming_convention_enforcer import NamingConventionEnforcer
        
        enforcer = NamingConventionEnforcer()
        
        # Valid YAML files
        assert enforcer.check("docker-compose.yaml") is True
        assert enforcer.check("ci-config.yml") is True
        
        # Invalid YAML files (snake_case)
        assert enforcer.check("docker_compose.yaml") is False
        assert enforcer.check("ci_config.yml") is False
    
    def test_enforces_kebab_case_for_json(self):
        """Should enforce kebab-case for JSON files."""
        from src.governance.naming_convention_enforcer import NamingConventionEnforcer
        
        enforcer = NamingConventionEnforcer()
        
        # Valid JSON files
        assert enforcer.check("package-lock.json") is True
        assert enforcer.check("tsconfig.json") is True
        
        # Invalid JSON files (snake_case)
        assert enforcer.check("package_lock.json") is False
    
    def test_detects_file_type_correctly(self):
        """Should detect file type from extension."""
        from src.governance.naming_convention_enforcer import NamingConventionEnforcer
        
        enforcer = NamingConventionEnforcer()
        
        assert enforcer.get_file_type("script.py") == "python"
        assert enforcer.get_file_type("readme.md") == "markdown"
        assert enforcer.get_file_type("config.yaml") == "config"
        assert enforcer.get_file_type("config.yml") == "config"
        assert enforcer.get_file_type("data.json") == "config"
        assert enforcer.get_file_type("notes.txt") == "text"
    
    def test_get_expected_convention_by_type(self):
        """Should return expected naming convention for file type."""
        from src.governance.naming_convention_enforcer import NamingConventionEnforcer
        
        enforcer = NamingConventionEnforcer()
        
        assert enforcer.get_expected_convention("script.py") == "snake_case"
        assert enforcer.get_expected_convention("guide.md") == "kebab-case"
        assert enforcer.get_expected_convention("config.yaml") == "kebab-case"
        assert enforcer.get_expected_convention("data.json") == "kebab-case"
    
    def test_suggests_correct_name(self):
        """Should suggest correct name for invalid files."""
        from src.governance.naming_convention_enforcer import NamingConventionEnforcer
        
        enforcer = NamingConventionEnforcer()
        
        # Python: camelCase → snake_case
        assert enforcer.suggest_name("userService.py") == "user_service.py"
        assert enforcer.suggest_name("TestUser.py") == "test_user.py"
        
        # Markdown: snake_case → kebab-case
        assert enforcer.suggest_name("user_guide.md") == "user-guide.md"
        assert enforcer.suggest_name("api_docs.md") == "api-docs.md"
    
    def test_batch_check_multiple_files(self):
        """Should check multiple files at once."""
        from src.governance.naming_convention_enforcer import NamingConventionEnforcer
        
        enforcer = NamingConventionEnforcer()
        
        files = [
            "user_service.py",  # valid
            "userService.py",   # invalid
            "user-guide.md",    # valid
            "user_guide.md",    # invalid
        ]
        
        results = enforcer.check_batch(files)
        
        assert results["user_service.py"]["valid"] is True
        assert results["userService.py"]["valid"] is False
        assert results["user-guide.md"]["valid"] is True
        assert results["user_guide.md"]["valid"] is False
    
    def test_respects_exception_list(self):
        """Should allow exception files regardless of convention."""
        from src.governance.naming_convention_enforcer import NamingConventionEnforcer
        
        enforcer = NamingConventionEnforcer()
        
        # These should pass despite not following convention
        exceptions = ["LICENSE", "VERSION", "README.md", "Makefile"]
        
        for filename in exceptions:
            assert enforcer.check(filename) is True
    
    def test_handles_path_objects(self):
        """Should handle Path objects in addition to strings."""
        from src.governance.naming_convention_enforcer import NamingConventionEnforcer
        
        enforcer = NamingConventionEnforcer()
        
        # Test with Path
        path = Path("user_service.py")
        assert enforcer.check(path) is True
        
        # Test with string
        assert enforcer.check("user_service.py") is True
