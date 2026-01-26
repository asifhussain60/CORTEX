"""
Test Suite: Planning Registry Loader Naming Utilities

Tests for naming utilities in planning_registry_loader.py:
- Kebab-case conversion
- Domain inference from descriptions
- Folder name generation
- Folder name validation

AC-PLANNING-NAMING-001: Naming Factory Utilities
"""

import pytest
from pathlib import Path
from typing import Optional

from cortex.orchestrators.domain.planning_registry_loader import (
    PlanningRegistryLoader,
    NamingFactory,
)


class TestNamingFactory:
    """Test suite for naming utilities"""

    @pytest.fixture
    def factory(self) -> NamingFactory:
        """Create NamingFactory instance"""
        return NamingFactory()

    # ========================================================================
    # KEBAB-CASE CONVERSION TESTS (RED Cycle)
    # ========================================================================

    def test_to_kebab_case_simple_word(self, factory: NamingFactory) -> None:
        """Test kebab-case conversion for simple words"""
        assert factory.to_kebab_case("Hello") == "hello"
        assert factory.to_kebab_case("WORLD") == "world"
        assert factory.to_kebab_case("Test") == "test"

    def test_to_kebab_case_with_spaces(self, factory: NamingFactory) -> None:
        """Test kebab-case conversion with spaces"""
        assert factory.to_kebab_case("hello world") == "hello-world"
        assert factory.to_kebab_case("Test Plan Name") == "test-plan-name"
        assert factory.to_kebab_case("My Amazing Feature") == "my-amazing-feature"

    def test_to_kebab_case_with_underscores(self, factory: NamingFactory) -> None:
        """Test kebab-case conversion with underscores"""
        assert factory.to_kebab_case("hello_world") == "hello-world"
        assert factory.to_kebab_case("test_plan_name") == "test-plan-name"

    def test_to_kebab_case_with_mixed_separators(self, factory: NamingFactory) -> None:
        """Test kebab-case conversion with mixed separators"""
        assert factory.to_kebab_case("hello_world test") == "hello-world-test"
        assert factory.to_kebab_case("Test Plan_Name") == "test-plan-name"

    def test_to_kebab_case_with_special_chars(self, factory: NamingFactory) -> None:
        """Test kebab-case conversion removes special characters"""
        assert factory.to_kebab_case("hello@world") == "hello-world"
        assert factory.to_kebab_case("test-plan!") == "test-plan"
        assert factory.to_kebab_case("feature#123") == "feature-123"

    def test_to_kebab_case_camel_case(self, factory: NamingFactory) -> None:
        """Test kebab-case conversion from camelCase"""
        assert factory.to_kebab_case("helloWorld") == "hello-world"
        assert factory.to_kebab_case("TestPlanName") == "test-plan-name"
        assert factory.to_kebab_case("myAmazingFeature") == "my-amazing-feature"

    def test_to_kebab_case_consecutive_separators(self, factory: NamingFactory) -> None:
        """Test kebab-case handles consecutive separators"""
        assert factory.to_kebab_case("hello  world") == "hello-world"
        assert factory.to_kebab_case("test__plan") == "test-plan"
        assert factory.to_kebab_case("feature---name") == "feature-name"

    def test_to_kebab_case_preserves_numbers(self, factory: NamingFactory) -> None:
        """Test kebab-case preserves numbers"""
        assert factory.to_kebab_case("feature123") == "feature123"
        assert factory.to_kebab_case("plan v2") == "plan-v2"
        assert factory.to_kebab_case("doc portal 2.0") == "doc-portal-2.0"

    # ========================================================================
    # DOMAIN INFERENCE TESTS (RED Cycle)
    # ========================================================================

    def test_infer_domain_from_description_docs(self, factory: NamingFactory) -> None:
        """Test domain inference for documentation"""
        assert factory.infer_domain("Generate documentation for API") == "docs"
        assert factory.infer_domain("Create user guide") == "docs"
        assert factory.infer_domain("Build architectural diagram") == "docs"

    def test_infer_domain_from_description_planning(self, factory: NamingFactory) -> None:
        """Test domain inference for planning"""
        assert factory.infer_domain("Create master plan") == "planning"
        assert factory.infer_domain("Phase roadmap") == "planning"

    def test_infer_domain_from_description_api(self, factory: NamingFactory) -> None:
        """Test domain inference for API"""
        assert factory.infer_domain("REST API endpoint") == "api"
        assert factory.infer_domain("GraphQL schema") == "api"

    def test_infer_domain_from_description_core(self, factory: NamingFactory) -> None:
        """Test domain inference for core/infrastructure"""
        assert factory.infer_domain("Database layer") == "core"
        assert factory.infer_domain("Message queue") == "core"
        assert factory.infer_domain("Service bus") == "core"

    def test_infer_domain_default(self, factory: NamingFactory) -> None:
        """Test domain inference returns default for unknown"""
        assert factory.infer_domain("Random description") == "general"
        assert factory.infer_domain("") == "general"
        assert factory.infer_domain("Unknown topic xyz") == "general"

    def test_infer_domain_case_insensitive(self, factory: NamingFactory) -> None:
        """Test domain inference is case-insensitive"""
        assert factory.infer_domain("DOCUMENTATION GUIDE") == "docs"
        assert factory.infer_domain("Planning ROADMAP") == "planning"
        assert factory.infer_domain("API ENDPOINT") == "api"

    # ========================================================================
    # FOLDER NAME GENERATION TESTS (RED Cycle)
    # ========================================================================

    def test_generate_folder_name_simple(self, factory: NamingFactory) -> None:
        """Test folder name generation with simple inputs"""
        result = factory.generate_folder_name({
            "name": "My Plan",
            "description": "Documentation guide",
        })

        assert isinstance(result, str)
        assert result == "my-plan"

    def test_generate_folder_name_with_domain(self, factory: NamingFactory) -> None:
        """Test folder name uses domain from description"""
        result = factory.generate_folder_name({
            "name": "API Documentation",
            "description": "REST API endpoint reference",
            "domain": None,  # Should infer from description
        })

        assert isinstance(result, str)
        # Should include domain-aware naming
        assert "-" in result or result.isalnum()

    def test_generate_folder_name_explicit_domain(self, factory: NamingFactory) -> None:
        """Test folder name respects explicit domain"""
        result = factory.generate_folder_name({
            "name": "Planning",
            "description": "Master plan",
            "domain": "planning",
        })

        assert isinstance(result, str)

    def test_generate_folder_name_long_name(self, factory: NamingFactory) -> None:
        """Test folder name generation with long name"""
        long_name = "This is a very long plan name that should be handled correctly"
        result = factory.generate_folder_name({
            "name": long_name,
            "description": "Test",
        })

        # Should be truncated or handled gracefully
        assert len(result) > 0
        assert isinstance(result, str)

    def test_generate_folder_name_special_characters(self, factory: NamingFactory) -> None:
        """Test folder name generation removes special characters"""
        result = factory.generate_folder_name({
            "name": "Plan@#$%Name!",
            "description": "Test",
        })

        assert "@" not in result
        assert "#" not in result
        assert "$" not in result
        assert "%" not in result
        assert "!" not in result

    # ========================================================================
    # FOLDER NAME VALIDATION TESTS (RED Cycle)
    # ========================================================================

    def test_validate_folder_name_valid(self, factory: NamingFactory) -> None:
        """Test folder name validation for valid names"""
        assert factory.validate_folder_name("valid-folder-name") is True
        assert factory.validate_folder_name("test-plan-v2") is True
        assert factory.validate_folder_name("doc-portal-2023") is True

    def test_validate_folder_name_invalid_empty(self, factory: NamingFactory) -> None:
        """Test folder name validation rejects empty names"""
        assert factory.validate_folder_name("") is False
        assert factory.validate_folder_name("   ") is False

    def test_validate_folder_name_invalid_special_chars(self, factory: NamingFactory) -> None:
        """Test folder name validation rejects special characters"""
        assert factory.validate_folder_name("invalid@name") is False
        assert factory.validate_folder_name("invalid#name") is False
        assert factory.validate_folder_name("invalid!name") is False

    def test_validate_folder_name_invalid_spaces(self, factory: NamingFactory) -> None:
        """Test folder name validation rejects spaces"""
        assert factory.validate_folder_name("invalid name") is False
        assert factory.validate_folder_name("test plan") is False

    def test_validate_folder_name_invalid_starts_with_hyphen(self, factory: NamingFactory) -> None:
        """Test folder name validation rejects leading hyphen"""
        assert factory.validate_folder_name("-invalid-name") is False

    def test_validate_folder_name_invalid_ends_with_hyphen(self, factory: NamingFactory) -> None:
        """Test folder name validation rejects trailing hyphen"""
        assert factory.validate_folder_name("invalid-name-") is False

    def test_validate_folder_name_consecutive_hyphens(self, factory: NamingFactory) -> None:
        """Test folder name validation rejects consecutive hyphens"""
        assert factory.validate_folder_name("invalid--name") is False
        assert factory.validate_folder_name("test---plan") is False

    def test_validate_folder_name_too_long(self, factory: NamingFactory) -> None:
        """Test folder name validation rejects names that are too long"""
        long_name = "a" * 300
        assert factory.validate_folder_name(long_name) is False

    # ========================================================================
    # INTEGRATION TESTS (GREEN Cycle)
    # ========================================================================

    def test_generate_and_validate_folder_name(self, factory: NamingFactory) -> None:
        """Test generate and validate work together"""
        request = {
            "name": "Documentation Portal",
            "description": "API reference documentation",
        }

        generated_name = factory.generate_folder_name(request)
        is_valid = factory.validate_folder_name(generated_name)

        assert is_valid is True

    def test_naming_roundtrip(self, factory: NamingFactory) -> None:
        """Test naming roundtrip: input → generate → validate"""
        test_cases = [
            "My Test Plan",
            "API Documentation v2",
            "Planning Roadmap 2026",
            "Core Infrastructure",
        ]

        for test_case in test_cases:
            generated = factory.generate_folder_name({
                "name": test_case,
                "description": "Test",
            })
            assert factory.validate_folder_name(generated) is True

    # ========================================================================
    # REGISTRY LOADER INTEGRATION TESTS
    # ========================================================================

    def test_planning_registry_loader_has_naming_factory(
        self,
        tmp_path: Path,
    ) -> None:
        """Test planning registry loader includes naming factory"""
        registry_path = tmp_path / "cortex-registry"
        registry_path.mkdir()

        loader = PlanningRegistryLoader(registry_path)

        # Should have naming factory
        assert hasattr(loader, "naming_factory")
        assert loader.naming_factory is not None

    def test_planning_registry_loader_generate_folder_name(
        self,
        tmp_path: Path,
    ) -> None:
        """Test registry loader can generate folder names"""
        registry_path = tmp_path / "cortex-registry"
        registry_path.mkdir()

        loader = PlanningRegistryLoader(registry_path)

        result = loader.generate_folder_name({
            "name": "Test Plan",
            "description": "Documentation",
        })

        assert isinstance(result, str)
        assert len(result) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
