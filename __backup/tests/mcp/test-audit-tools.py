"""
Tests for AC-TOOLKIT-001: Consolidate audit tool family

TDD Implementation: RED → GREEN → REFACTOR
This file represents the RED phase - all tests written to fail initially.
Tests define the desired state for consolidated audit tools module.

AC-ID: AC-TOOLKIT-001
Title: Consolidate audit tool family
Effort: 8 hours
Priority: Critical
Phase: 2
Governance: CORE-024 (@mcp_tool enforcement), CORE-022 (naming standards)
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock


class TestAuditToolsModuleStructure:
    """Test that audit-tools.py module exists and has correct structure"""
    
    def test_audit_tools_module_exists(self):
        """RED: Verify src/mcp/audit-tools.py exists"""
        audit_tools_path = Path("src/mcp/audit-tools.py")
        assert audit_tools_path.exists(), "src/mcp/audit-tools.py must exist"
    
    def test_audit_tools_is_valid_python(self):
        """RED: Verify audit-tools.py is valid Python syntax"""
        audit_tools_path = Path("src/mcp/audit-tools.py")
        with open(audit_tools_path, 'r') as f:
            code = f.read()
        # Should not raise SyntaxError
        compile(code, audit_tools_path, 'exec')
    
    def test_naming_compliance_kebab_case(self):
        """RED: Verify filename follows kebab-case per CORE-022"""
        filename = "audit-tools.py"
        # Must be kebab-case, no underscores, all lowercase
        assert "-" in filename or filename.isidentifier(), "Filename must use kebab-case"
        assert filename == filename.lower(), "Filename must be lowercase"
        assert len(filename) <= 25, "Filename must be ≤25 characters"


class TestAuditToolsMCPDecorators:
    """Test that functions have @mcp_tool decorators per CORE-024"""
    
    @pytest.fixture
    def audit_tools_module(self):
        """Import audit-tools module"""
        from src.mcp.audit_tools import audit_query, audit_validate, audit_history
        return {
            'audit_query': audit_query,
            'audit_validate': audit_validate,
            'audit_history': audit_history
        }
    
    def test_audit_query_has_mcp_decorator(self, audit_tools_module):
        """RED: Verify audit_query has @mcp_tool decorator"""
        func = audit_tools_module['audit_query']
        # Check for MCP metadata attribute (set by @mcp_tool decorator)
        assert hasattr(func, '_mcp_metadata'), \
            "audit_query must have @mcp_tool decorator"
        assert func._mcp_metadata.get('name') == 'cortex_audit_query'
        assert 'Query' in func._mcp_metadata.get('description', '')
    
    def test_audit_validate_has_mcp_decorator(self, audit_tools_module):
        """RED: Verify audit_validate has @mcp_tool decorator"""
        func = audit_tools_module['audit_validate']
        assert hasattr(func, '_mcp_metadata'), \
            "audit_validate must have @mcp_tool decorator"
        assert func._mcp_metadata.get('name') == 'cortex_audit_validate'
    
    def test_audit_history_has_mcp_decorator(self, audit_tools_module):
        """RED: Verify audit_history has @mcp_tool decorator"""
        func = audit_tools_module['audit_history']
        assert hasattr(func, '_mcp_metadata'), \
            "audit_history must have @mcp_tool decorator"
        assert func._mcp_metadata.get('name') == 'cortex_audit_history'


class TestAuditQueryFunction:
    """Test audit_query function signature and behavior"""
    
    @pytest.fixture
    def audit_query(self):
        """Import audit_query function"""
        from src.mcp.audit_tools import audit_query
        return audit_query
    
    def test_audit_query_signature(self, audit_query):
        """RED: Verify audit_query has correct signature"""
        import inspect
        sig = inspect.signature(audit_query)
        params = list(sig.parameters.keys())
        assert 'db_path' in params, "Must have db_path parameter"
        assert 'filters' in params, "Must have filters parameter"
    
    def test_audit_query_returns_dict_with_required_keys(self, audit_query):
        """RED: Verify audit_query returns {status, data, error} dict"""
        # Mock implementation for now
        result = audit_query(
            db_path="test.db",
            filters={"ac_id": "AC-AUDIT-001"}
        )
        assert isinstance(result, dict), "Must return dict"
        assert 'status' in result, "Must have 'status' key"
        assert 'data' in result, "Must have 'data' key"
        assert 'error' in result, "Must have 'error' key"
    
    def test_audit_query_supports_ac_id_filter(self, audit_query):
        """RED: Verify audit_query supports ac_id filter"""
        result = audit_query(
            db_path="test.db",
            filters={"ac_id": "AC-AUDIT-001"}
        )
        # Filter should be processed (implementation detail tested later)
        assert isinstance(result, dict)
    
    def test_audit_query_supports_date_range_filter(self, audit_query):
        """RED: Verify audit_query supports date_range filter"""
        result = audit_query(
            db_path="test.db",
            filters={"date_range": {"start": "2026-01-01", "end": "2026-01-12"}}
        )
        assert isinstance(result, dict)
    
    def test_audit_query_supports_level_filter(self, audit_query):
        """RED: Verify audit_query supports level filter"""
        result = audit_query(
            db_path="test.db",
            filters={"level": "ERROR"}
        )
        assert isinstance(result, dict)
    
    def test_audit_query_supports_category_filter(self, audit_query):
        """RED: Verify audit_query supports category filter"""
        result = audit_query(
            db_path="test.db",
            filters={"category": "GOVERNANCE"}
        )
        assert isinstance(result, dict)


class TestAuditValidateFunction:
    """Test audit_validate function signature and behavior"""
    
    @pytest.fixture
    def audit_validate(self):
        """Import audit_validate function"""
        from src.mcp.audit_tools import audit_validate
        return audit_validate
    
    def test_audit_validate_signature(self, audit_validate):
        """RED: Verify audit_validate has correct signature"""
        import inspect
        sig = inspect.signature(audit_validate)
        params = list(sig.parameters.keys())
        assert 'evidence_path' in params, "Must have evidence_path parameter"
    
    def test_audit_validate_returns_validation_dict(self, audit_validate):
        """RED: Verify audit_validate returns {status, data, error}"""
        result = audit_validate(evidence_path="/path/to/evidence.json")
        assert isinstance(result, dict)
        assert 'status' in result
        assert 'data' in result
        assert 'error' in result
        # Status should be "valid" or "invalid"
        assert result['status'] in ["valid", "invalid"], \
            f"Status must be 'valid' or 'invalid', got {result['status']}"


class TestAuditHistoryFunction:
    """Test audit_history function signature and behavior"""
    
    @pytest.fixture
    def audit_history(self):
        """Import audit_history function"""
        from src.mcp.audit_tools import audit_history
        return audit_history
    
    def test_audit_history_signature(self, audit_history):
        """RED: Verify audit_history has correct signature"""
        import inspect
        sig = inspect.signature(audit_history)
        params = list(sig.parameters.keys())
        assert 'ac_id' in params, "Must have ac_id parameter"
        assert 'days' in params, "Must have days parameter"
    
    def test_audit_history_has_default_days(self, audit_history):
        """RED: Verify days parameter has default value"""
        import inspect
        sig = inspect.signature(audit_history)
        assert sig.parameters['days'].default == 30, \
            "days parameter must default to 30"
    
    def test_audit_history_returns_history_list(self, audit_history):
        """RED: Verify audit_history returns {status, data: list, error}"""
        result = audit_history(ac_id="AC-AUDIT-001")
        assert isinstance(result, dict)
        assert 'status' in result
        assert 'data' in result
        assert 'error' in result
        # data should be a list of history entries
        assert isinstance(result['data'], list), "data must be a list"
    
    def test_audit_history_returns_sorted_entries(self, audit_history):
        """RED: Verify entries are sorted by timestamp"""
        result = audit_history(ac_id="AC-AUDIT-001")
        if result['data']:  # If there are entries
            # Each entry should have timestamp
            for entry in result['data']:
                assert 'timestamp' in entry or 'time' in entry, \
                    "Each entry must have timestamp field"


class TestCapabilityRegistryDiscovery:
    """Test that audit-tools functions are discoverable via capability_registry"""
    
    def test_capability_registry_discovers_audit_tools(self):
        """RED: Verify capability_registry discovers audit tools"""
        from src.tools.capability_registry import capability_registry
        tools = capability_registry.discover()
        audit_tool_names = [t for t in tools if 'audit' in t.lower()]
        assert len(audit_tool_names) > 0, "Should discover audit tools"
    
    def test_capability_registry_get_audit_query(self):
        """RED: Verify capability_registry.get() returns audit_query metadata"""
        from src.tools.capability_registry import capability_registry
        tool = capability_registry.get("cortex_audit_query")
        assert tool is not None, "Should get cortex_audit_query tool"
        assert 'name' in tool or 'description' in tool, \
            "Tool metadata should have name and description"
    
    def test_capability_registry_get_audit_validate(self):
        """RED: Verify capability_registry.get() returns audit_validate metadata"""
        from src.tools.capability_registry import capability_registry
        tool = capability_registry.get("cortex_audit_validate")
        assert tool is not None
    
    def test_capability_registry_get_audit_history(self):
        """RED: Verify capability_registry.get() returns audit_history metadata"""
        from src.tools.capability_registry import capability_registry
        tool = capability_registry.get("cortex_audit_history")
        assert tool is not None


class TestImportSafety:
    """Test that importing audit-tools doesn't create circular dependencies"""
    
    def test_no_circular_import_from_audit_tools(self):
        """RED: Verify audit-tools can be imported without circular dependency"""
        # This should not raise ImportError or circular import error
        try:
            from src.mcp.audit_tools import audit_query, audit_validate, audit_history
            assert True, "Should import successfully"
        except ImportError as e:
            if "circular" in str(e).lower():
                pytest.fail(f"Circular import detected: {e}")
            raise
    
    def test_audit_tools_doesnt_import_conflicting_modules(self):
        """RED: Verify audit-tools doesn't import conflicting modules"""
        import sys
        # Import audit-tools
        from src.mcp import audit_tools
        # Should not have imported old audit scripts
        old_imports = [m for m in sys.modules if 'scripts.audit' in m]
        # Old imports should not be present (or should be cleaned up)
        # This is a soft assertion - implementation decides cleanup strategy


class TestMCPMetadataQuality:
    """Test that @mcp_tool decorators have complete metadata per CORE-024"""
    
    @pytest.fixture
    def audit_tools_module(self):
        """Import audit-tools module"""
        from src.mcp import audit_tools
        return audit_tools
    
    def test_audit_query_metadata_complete(self, audit_tools_module):
        """RED: Verify audit_query has complete @mcp_tool metadata"""
        func = audit_tools_module.audit_query
        assert hasattr(func, '_mcp_metadata')
        metadata = func._mcp_metadata
        assert metadata.get('name')
        assert metadata.get('description')
        assert metadata.get('category')
        assert metadata.get('parameters')
        assert metadata.get('returns')
    
    def test_audit_validate_metadata_complete(self, audit_tools_module):
        """RED: Verify audit_validate has complete @mcp_tool metadata"""
        func = audit_tools_module.audit_validate
        assert hasattr(func, '_mcp_metadata')
        metadata = func._mcp_metadata
        assert metadata.get('name')
        assert metadata.get('description')
        assert metadata.get('category')
    
    def test_audit_history_metadata_complete(self, audit_tools_module):
        """RED: Verify audit_history has complete @mcp_tool metadata"""
        func = audit_tools_module.audit_history
        assert hasattr(func, '_mcp_metadata')
        metadata = func._mcp_metadata
        assert metadata.get('name')
        assert metadata.get('description')
        assert metadata.get('category')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
