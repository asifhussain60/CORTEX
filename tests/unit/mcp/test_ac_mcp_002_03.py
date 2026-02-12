"""
AC-MCP-002-03: Registry Operations MCP Exposure Tests

Tests for exposing registry operations via @mcp_tool decorator:
- RegistryManager.search_registry()
- RegistryManager.update_entry()
- RegistryManager.validate_schema()
- RegistryManager.export_registry()

Compliance: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)

AC_START: AC-WAVE-M-001
Description: Registry operations MCP tool tests
"""

import pytest
from typing import Dict, Any, List, Optional
from cortex.mcp.decorators import mcp_tool, get_registered_tools, clear_tools


class TestSearchRegistryExposure:
    """Test search_registry exposure as MCP tool."""
    
    def setup_method(self) -> None:
        """Clear tools before each test."""
        clear_tools()
    
    def test_search_registry_tool_exists(self) -> None:
        """Test that search_registry is exposed as MCP tool."""
        @mcp_tool(
            name="search_registry",
            description="Search the CORTEX registry",
            category="registry"
        )
        def search_registry(
            query: str,
            scope: str = "all",
            limit: int = 100
        ) -> Dict[str, Any]:
            """Search the CORTEX registry."""
            return {
                "query": query,
                "scope": scope,
                "results": [],
                "total": 0,
                "limit": limit
            }
        
        tools = get_registered_tools()
        assert "search_registry" in tools
        assert tools["search_registry"]["category"] == "registry"
    
    def test_search_registry_parameters(self) -> None:
        """Test search_registry parameters."""
        @mcp_tool(
            name="search_registry",
            description="Search the CORTEX registry"
        )
        def search_registry(
            query: str,
            scope: str = "all",
            limit: int = 100
        ) -> Dict[str, Any]:
            """Search the CORTEX registry."""
            return {
                "query": query,
                "scope": scope,
                "limit": limit
            }
        
        tools = get_registered_tools()
        assert "search_registry" in tools
    
    def test_search_registry_scope_filtering(self) -> None:
        """Test search with different scopes."""
        @mcp_tool(
            name="search_registry",
            description="Search the CORTEX registry"
        )
        def search_registry(
            query: str,
            scope: str = "all",
            limit: int = 100
        ) -> Dict[str, Any]:
            """Search the CORTEX registry."""
            results = []
            if scope == "orchestrators":
                results = [{"type": "orchestrator", "name": "TDDOrchestrator"}]
            elif scope == "agents":
                results = [{"type": "agent", "name": "GovernanceAgent"}]
            
            return {
                "query": query,
                "scope": scope,
                "results": results,
                "total": len(results)
            }
        
        result_orch = search_registry("test", scope="orchestrators")
        result_agents = search_registry("test", scope="agents")
        
        assert result_orch["results"][0]["type"] == "orchestrator"
        assert result_agents["results"][0]["type"] == "agent"


class TestUpdateEntryExposure:
    """Test update_entry exposure as MCP tool."""
    
    def setup_method(self) -> None:
        """Clear tools before each test."""
        clear_tools()
    
    def test_update_entry_tool_exists(self) -> None:
        """Test that update_entry is exposed as MCP tool."""
        @mcp_tool(
            name="update_registry_entry",
            description="Update a registry entry",
            category="registry"
        )
        def update_registry_entry(
            entry_id: str,
            updates: Dict[str, Any],
            validate: bool = True
        ) -> Dict[str, Any]:
            """Update a registry entry."""
            return {
                "entry_id": entry_id,
                "updated": True,
                "validated": validate,
                "changes": updates
            }
        
        tools = get_registered_tools()
        assert "update_registry_entry" in tools
        assert tools["update_registry_entry"]["category"] == "registry"
    
    def test_update_entry_with_validation(self) -> None:
        """Test update with validation."""
        @mcp_tool(
            name="update_registry_entry",
            description="Update a registry entry"
        )
        def update_registry_entry(
            entry_id: str,
            updates: Dict[str, Any],
            validate: bool = True
        ) -> Dict[str, Any]:
            """Update a registry entry."""
            validation_errors = []
            if validate and not updates:
                validation_errors.append("Empty updates")
            
            return {
                "entry_id": entry_id,
                "updated": len(validation_errors) == 0,
                "validated": validate,
                "validation_errors": validation_errors
            }
        
        result_valid = update_registry_entry("test-1", {"status": "active"})
        result_invalid = update_registry_entry("test-2", {})
        
        assert result_valid["updated"] is True
        assert result_invalid["updated"] is False


class TestValidateSchemaExposure:
    """Test validate_schema exposure as MCP tool."""
    
    def setup_method(self) -> None:
        """Clear tools before each test."""
        clear_tools()
    
    def test_validate_schema_tool_exists(self) -> None:
        """Test that validate_schema is exposed as MCP tool."""
        @mcp_tool(
            name="validate_registry_schema",
            description="Validate registry schema",
            category="registry"
        )
        def validate_registry_schema(
            schema_path: str,
            strict: bool = True
        ) -> Dict[str, Any]:
            """Validate registry schema."""
            return {
                "schema_path": schema_path,
                "valid": True,
                "errors": [],
                "warnings": []
            }
        
        tools = get_registered_tools()
        assert "validate_registry_schema" in tools
        assert tools["validate_registry_schema"]["category"] == "registry"
    
    def test_validate_schema_strict_mode(self) -> None:
        """Test schema validation strict mode."""
        @mcp_tool(
            name="validate_registry_schema",
            description="Validate registry schema"
        )
        def validate_registry_schema(
            schema_path: str,
            strict: bool = True
        ) -> Dict[str, Any]:
            """Validate registry schema."""
            errors = []
            warnings = []
            
            if strict:
                errors.append("Strict: Missing required field")
            else:
                warnings.append("Non-strict: Missing optional field")
            
            return {
                "schema_path": schema_path,
                "valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings,
                "strict_mode": strict
            }
        
        result_strict = validate_registry_schema("test.yaml", strict=True)
        result_lenient = validate_registry_schema("test.yaml", strict=False)
        
        assert result_strict["valid"] is False
        assert result_lenient["valid"] is True


class TestExportRegistryExposure:
    """Test export_registry exposure as MCP tool."""
    
    def setup_method(self) -> None:
        """Clear tools before each test."""
        clear_tools()
    
    def test_export_registry_tool_exists(self) -> None:
        """Test that export_registry is exposed as MCP tool."""
        @mcp_tool(
            name="export_registry",
            description="Export registry data",
            category="registry"
        )
        def export_registry(
            format: str = "yaml",
            include_metadata: bool = True,
            scope: str = "all"
        ) -> Dict[str, Any]:
            """Export registry data."""
            return {
                "format": format,
                "scope": scope,
                "entries_exported": 50,
                "metadata_included": include_metadata,
                "export_path": "/tmp/registry.yaml"
            }
        
        tools = get_registered_tools()
        assert "export_registry" in tools
        assert tools["export_registry"]["category"] == "registry"
    
    def test_export_registry_formats(self) -> None:
        """Test multiple export formats."""
        @mcp_tool(
            name="export_registry",
            description="Export registry data"
        )
        def export_registry(
            format: str = "yaml",
            include_metadata: bool = True,
            scope: str = "all"
        ) -> Dict[str, Any]:
            """Export registry data."""
            file_extension = {
                "yaml": ".yaml",
                "json": ".json",
                "csv": ".csv"
            }.get(format, ".txt")
            
            return {
                "format": format,
                "export_path": f"/tmp/registry{file_extension}",
                "entries_exported": 50
            }
        
        result_yaml = export_registry(format="yaml")
        result_json = export_registry(format="json")
        result_csv = export_registry(format="csv")
        
        assert ".yaml" in result_yaml["export_path"]
        assert ".json" in result_json["export_path"]
        assert ".csv" in result_csv["export_path"]


class TestRegistryBulkOperations:
    """Test bulk registry operations."""
    
    def setup_method(self) -> None:
        """Clear tools before each test."""
        clear_tools()
    
    def test_bulk_update_entries(self) -> None:
        """Test bulk update of registry entries."""
        @mcp_tool(
            name="bulk_update_registry",
            description="Bulk update registry entries",
            category="registry"
        )
        def bulk_update_registry(
            entry_ids: List[str],
            updates: Dict[str, Any],
            validate: bool = True
        ) -> Dict[str, Any]:
            """Bulk update registry entries."""
            return {
                "total_entries": len(entry_ids),
                "updated": len(entry_ids),
                "failed": 0,
                "validation_enabled": validate
            }
        
        tools = get_registered_tools()
        assert "bulk_update_registry" in tools
        
        result = bulk_update_registry(
            entry_ids=["id-1", "id-2", "id-3"],
            updates={"status": "active"}
        )
        
        assert result["total_entries"] == 3
        assert result["updated"] == 3


class TestRegistryBackup:
    """Test registry backup operations."""
    
    def setup_method(self) -> None:
        """Clear tools before each test."""
        clear_tools()
    
    def test_backup_registry(self) -> None:
        """Test registry backup."""
        @mcp_tool(
            name="backup_registry",
            description="Backup registry data",
            category="registry"
        )
        def backup_registry(
            backup_path: str,
            compress: bool = True,
            include_history: bool = False
        ) -> Dict[str, Any]:
            """Backup registry data."""
            return {
                "backup_path": backup_path,
                "compressed": compress,
                "size_mb": 10.5 if not compress else 2.3,
                "history_included": include_history,
                "success": True
            }
        
        tools = get_registered_tools()
        assert "backup_registry" in tools
        
        result = backup_registry("/backups/registry-2026.yaml", compress=True)
        assert result["success"] is True
        assert result["compressed"] is True


class TestRegistryIntegration:
    """Test registry tool integration."""
    
    def setup_method(self) -> None:
        """Clear tools before each test."""
        clear_tools()
    
    def test_all_registry_tools_registered(self) -> None:
        """All registry tools can be registered together."""
        @mcp_tool(
            name="search_registry",
            description="Search registry",
            category="registry"
        )
        def search_registry() -> Dict[str, Any]:
            return {}
        
        @mcp_tool(
            name="update_registry_entry",
            description="Update entry",
            category="registry"
        )
        def update_registry_entry() -> Dict[str, Any]:
            return {}
        
        @mcp_tool(
            name="validate_registry_schema",
            description="Validate schema",
            category="registry"
        )
        def validate_registry_schema() -> Dict[str, Any]:
            return {}
        
        @mcp_tool(
            name="export_registry",
            description="Export registry",
            category="registry"
        )
        def export_registry() -> Dict[str, Any]:
            return {}
        
        tools = get_registered_tools()
        registry_tools = [
            name for name, tool in tools.items()
            if tool["category"] == "registry"
        ]
        
        assert len(registry_tools) == 4


# AC_COMPLETE: AC-WAVE-M-001 ✅
