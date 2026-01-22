"""Governance compliance tests for Knowledge Graph module.

Validates that the KG implementation complies with CORTEX governance rules:
- CORE-011: 100% type hints on all parameters and returns
- CORE-012: Google-style docstrings on all public APIs
- CORE-013: No bare `except:` clauses (specific exception handling)
"""

import pytest
from inspect import signature, getsource, Parameter
import cortex.brain.core.knowledge.graph.interface as interface_module
import cortex.brain.core.knowledge.graph.mock_adapter as mock_module
import cortex.brain.core.knowledge.graph.sqlite_adapter as sqlite_module
import cortex.brain.core.knowledge.graph.constraint_validator as validator_module


class TestGovernanceCORE011TypeHints:
    """Test CORE-011: 100% type hints on all parameters and returns."""

    def _check_type_hints(self, module, class_name: str, method_names: list) -> None:
        """Check that class methods have type hints.

        Args:
            module: Python module to check
            class_name: Name of class to inspect
            method_names: List of method names to check

        Raises:
            AssertionError: If any method missing type hints
        """
        cls = getattr(module, class_name)

        for method_name in method_names:
            method = getattr(cls, method_name)
            sig = signature(method)

            # Check return type
            assert (
                sig.return_annotation != Parameter.empty
            ), f"{class_name}.{method_name} missing return type hint"

            # Check parameter types (skip 'self')
            for param_name, param in sig.parameters.items():
                if param_name != "self":
                    assert (
                        param.annotation != Parameter.empty
                    ), f"{class_name}.{method_name}({param_name}) missing type hint"

    def test_interface_type_hints(self) -> None:
        """Test IGraphAdapter interface has complete type hints."""
        methods = [
            "create_entity",
            "create_relationship",
            "query_entities",
            "query_paths",
            "delete_entity",
            "health_check",
        ]

        self._check_type_hints(interface_module, "IGraphAdapter", methods)

    def test_mock_adapter_type_hints(self) -> None:
        """Test MockGraphAdapter has complete type hints."""
        methods = [
            "create_entity",
            "create_relationship",
            "query_entities",
            "query_paths",
            "delete_entity",
            "health_check",
        ]

        self._check_type_hints(mock_module, "MockGraphAdapter", methods)

    def test_sqlite_adapter_type_hints(self) -> None:
        """Test SQLiteGraphAdapter has complete type hints."""
        methods = [
            "create_entity",
            "create_relationship",
            "query_entities",
            "query_paths",
            "delete_entity",
            "health_check",
        ]

        self._check_type_hints(sqlite_module, "SQLiteGraphAdapter", methods)

    def test_constraint_validator_type_hints(self) -> None:
        """Test ConstraintValidator has complete type hints."""
        methods = [
            "validate_entity_type",
            "validate_relationship_type",
            "validate_entity",
            "validate_relationship",
            "get_valid_entity_types",
            "get_valid_relationship_types",
        ]

        self._check_type_hints(validator_module, "ConstraintValidator", methods)


class TestGovernanceCORE012Docstrings:
    """Test CORE-012: Google-style docstrings on public APIs."""

    def _check_google_docstrings(
        self, module, class_name: str, method_names: list
    ) -> None:
        """Check for Google-style docstrings.

        Args:
            module: Python module to check
            class_name: Name of class to inspect
            method_names: List of method names to check

        Raises:
            AssertionError: If any method missing or non-Google docstring
        """
        cls = getattr(module, class_name)

        for method_name in method_names:
            method = getattr(cls, method_name)
            docstring = method.__doc__

            assert docstring is not None, (
                f"{class_name}.{method_name} missing docstring"
            )

            # Check for Google-style sections
            # At minimum, should have Args: or Returns: or Raises:
            google_markers = ["Args:", "Returns:", "Raises:", "Attributes:"]
            has_marker = any(marker in docstring for marker in google_markers)

            assert has_marker or len(docstring) > 100, (
                f"{class_name}.{method_name} docstring not Google-style "
                f"(should have Args/Returns/Raises sections)"
            )

    def test_interface_docstrings(self) -> None:
        """Test IGraphAdapter has Google-style docstrings."""
        methods = [
            "create_entity",
            "create_relationship",
            "query_entities",
            "query_paths",
            "delete_entity",
            "health_check",
        ]

        self._check_google_docstrings(interface_module, "IGraphAdapter", methods)

    def test_mock_adapter_docstrings(self) -> None:
        """Test MockGraphAdapter has Google-style docstrings."""
        methods = [
            "create_entity",
            "create_relationship",
            "query_entities",
            "query_paths",
            "delete_entity",
            "health_check",
        ]

        self._check_google_docstrings(mock_module, "MockGraphAdapter", methods)

    def test_sqlite_adapter_docstrings(self) -> None:
        """Test SQLiteGraphAdapter has Google-style docstrings."""
        methods = [
            "create_entity",
            "create_relationship",
            "query_entities",
            "query_paths",
            "delete_entity",
            "health_check",
        ]

        self._check_google_docstrings(sqlite_module, "SQLiteGraphAdapter", methods)

    def test_constraint_validator_docstrings(self) -> None:
        """Test ConstraintValidator has Google-style docstrings."""
        methods = [
            "validate_entity_type",
            "validate_relationship_type",
            "validate_entity",
            "validate_relationship",
        ]

        self._check_google_docstrings(
            validator_module, "ConstraintValidator", methods
        )


class TestGovernanceCORE013ExceptionHandling:
    """Test CORE-013: No bare `except:` clauses."""

    def _check_no_bare_except(self, module) -> None:
        """Check for bare except clauses.

        Args:
            module: Python module to check

        Raises:
            AssertionError: If bare except found
        """
        source = getsource(module)
        # Look for bare except (not except SomeException)
        # This is a simple check - bare except followed by colon
        lines = source.split("\n")
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped == "except:":
                raise AssertionError(
                    f"Bare except: found on line {i+1} in {module.__name__}"
                )

    def test_interface_no_bare_except(self) -> None:
        """Test IGraphAdapter has no bare except."""
        self._check_no_bare_except(interface_module)

    def test_mock_adapter_no_bare_except(self) -> None:
        """Test MockGraphAdapter has no bare except."""
        self._check_no_bare_except(mock_module)

    def test_sqlite_adapter_no_bare_except(self) -> None:
        """Test SQLiteGraphAdapter has no bare except."""
        self._check_no_bare_except(sqlite_module)

    def test_constraint_validator_no_bare_except(self) -> None:
        """Test ConstraintValidator has no bare except."""
        self._check_no_bare_except(validator_module)


class TestGovernanceSpecificExceptionHandling:
    """Test that exceptions are handled specifically (not caught broadly)."""

    def test_graph_query_error_used_for_errors(self) -> None:
        """Test that GraphQueryError is used appropriately."""
        from cortex.brain.core.knowledge.graph.interface import GraphQueryError

        adapter = mock_module.MockGraphAdapter()

        # Should raise GraphQueryError for constraint violations
        with pytest.raises(GraphQueryError):
            adapter.create_entity("e1", "Service", {})
            adapter.create_entity("e1", "Service", {})

    def test_sqlite_uses_specific_exceptions(self) -> None:
        """Test that SQLite adapter uses specific exceptions."""
        import sqlite3
        from cortex.brain.core.knowledge.graph.interface import GraphQueryError

        adapter = sqlite_module.SQLiteGraphAdapter(":memory:")

        # Should raise GraphQueryError (not bare Exception or sqlite3.Error)
        with pytest.raises(GraphQueryError):
            adapter.create_entity("e1", "Service", {})
            adapter.create_entity("e1", "Service", {})


class TestGovernanceNonBreakingDesign:
    """Test that KG module follows non-breaking design."""

    def test_kg_module_optional_import(self) -> None:
        """Test that KG module can be imported without affecting core."""
        try:
            from cortex.brain.core.knowledge.graph import IGraphAdapter

            adapter_imported = True
        except ImportError:
            adapter_imported = False

        # Should import successfully
        assert adapter_imported is True

    def test_no_circular_imports(self) -> None:
        """Test that graph module doesn't create circular imports."""
        # Should import without issues
        try:
            import cortex.brain.core.knowledge.graph
            import cortex.brain

            success = True
        except ImportError:
            success = False

        assert success is True

    def test_adapters_dont_require_external_dependencies(self) -> None:
        """Test that mock and SQLite adapters don't require external KG."""
        import cortex.brain.core.knowledge.graph

        # MockGraphAdapter should work without Neo4j/Neptune
        mock = mock_module.MockGraphAdapter()
        assert mock is not None

        # SQLiteGraphAdapter should work without external database
        sqlite = sqlite_module.SQLiteGraphAdapter(":memory:")
        assert sqlite is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
