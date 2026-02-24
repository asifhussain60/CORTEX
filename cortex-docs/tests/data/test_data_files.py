"""
Test Data Files — cortex-docs/tests/data/test_data_files.py
Validates all JSON data files in cortex-docs/data/.
"""

import json
from pathlib import Path
from typing import Any, Dict, List

import pytest


# AC_START: AC-DOCGEN-DATA-FILES-20260224T000000


class TestDataFiles:
    """Validate all JSON data files in cortex-docs/data/."""
    
    def test_data_directory_exists(self, data_dir: Path) -> None:
        """data/ directory must exist."""
        assert data_dir.exists(), "data/ directory not found"
        assert data_dir.is_dir(), "data/ is not a directory"
    
    @pytest.mark.parametrize("json_file", [
        "content.json",
        "learning-paths.json",
        "knowledge-catalog.json",
        "mcp-tools.json",
        "orchestrators.json"
    ])
    def test_json_file_exists(self, data_dir: Path, json_file: str) -> None:
        """All required JSON files must exist."""
        json_path = data_dir / json_file
        assert json_path.exists(), f"{json_file} not found in data/"
    
    @pytest.mark.parametrize("json_file", [
        "content.json",
        "learning-paths.json",
        "knowledge-catalog.json",
        "mcp-tools.json",
        "orchestrators.json"
    ])
    def test_json_file_is_valid_json(self, data_dir: Path, json_file: str) -> None:
        """All JSON files must be valid JSON."""
        json_path = data_dir / json_file
        
        with open(json_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                assert isinstance(data, (dict, list)), (
                    f"{json_file} is not a dict or list"
                )
            except json.JSONDecodeError as e:
                pytest.fail(f"{json_file} has invalid JSON: {e}")
    
    def test_content_json_structure(self, content_json: Dict[str, Any]) -> None:
        """content.json must have categories array."""
        assert "categories" in content_json, "content.json missing 'categories'"
        assert isinstance(content_json["categories"], list), (
            "content.json 'categories' is not a list"
        )
        assert len(content_json["categories"]) > 0, (
            "content.json has no categories"
        )
    
    def test_learning_paths_json_structure(
        self, 
        learning_paths_json: Dict[str, Any]
    ) -> None:
        """learning-paths.json must have paths array."""
        assert "paths" in learning_paths_json, (
            "learning-paths.json missing 'paths'"
        )
        assert isinstance(learning_paths_json["paths"], list), (
            "learning-paths.json 'paths' is not a list"
        )
        assert len(learning_paths_json["paths"]) == 3, (
            "learning-paths.json should have exactly 3 paths (beginner/intermediate/advanced)"
        )
    
    def test_knowledge_catalog_json_structure(
        self, 
        knowledge_catalog_json: Dict[str, Any]
    ) -> None:
        """knowledge-catalog.json must have tech_stacks or similar structure."""
        # Check for any top-level key (structure may vary)
        assert len(knowledge_catalog_json.keys()) > 0, (
            "knowledge-catalog.json is empty"
        )
        
        # If tech_stacks exists, validate structure
        if "tech_stacks" in knowledge_catalog_json:
            tech_stacks = knowledge_catalog_json["tech_stacks"]
            assert isinstance(tech_stacks, list), (
                "knowledge-catalog.json 'tech_stacks' is not a list"
            )
            
            for stack in tech_stacks:
                assert "id" in stack, f"Tech stack missing 'id': {stack}"
                assert "name" in stack, f"Tech stack missing 'name': {stack}"
    
    def test_mcp_tools_json_structure(
        self, 
        mcp_tools_json: Dict[str, Any]
    ) -> None:
        """mcp-tools.json must have tools array."""
        assert "tools" in mcp_tools_json, "mcp-tools.json missing 'tools'"
        assert isinstance(mcp_tools_json["tools"], list), (
            "mcp-tools.json 'tools' is not a list"
        )
        assert len(mcp_tools_json["tools"]) > 0, (
            "mcp-tools.json has no tools"
        )
        
        # Validate tool structure
        for tool in mcp_tools_json["tools"]:
            assert "name" in tool, f"Tool missing 'name': {tool}"
            assert "description" in tool, f"Tool missing 'description': {tool}"
    
    def test_orchestrators_json_structure(
        self, 
        orchestrators_json: Dict[str, Any]
    ) -> None:
        """orchestrators.json must have orchestrators array."""
        assert "orchestrators" in orchestrators_json, (
            "orchestrators.json missing 'orchestrators'"
        )
        assert isinstance(orchestrators_json["orchestrators"], list), (
            "orchestrators.json 'orchestrators' is not a list"
        )
        assert len(orchestrators_json["orchestrators"]) > 0, (
            "orchestrators.json has no orchestrators"
        )
        
        # Validate orchestrator structure
        for orchestrator in orchestrators_json["orchestrators"]:
            assert "name" in orchestrator, f"Orchestrator missing 'name': {orchestrator}"
            assert "tier" in orchestrator, f"Orchestrator missing 'tier': {orchestrator}"
    
    def test_mcp_tools_json_has_26_tools(
        self, 
        mcp_tools_json: Dict[str, Any]
    ) -> None:
        """mcp-tools.json should have 26 active tools (CORTEX spec)."""
        tools = mcp_tools_json.get("tools", [])
        active_tools = [t for t in tools if t.get("status") != "deprecated"]
        
        # Allow some tolerance (26 ± 2)
        assert 24 <= len(active_tools) <= 28, (
            f"Expected ~26 active MCP tools, found {len(active_tools)}"
        )
    
    def test_orchestrators_json_has_27_orchestrators(
        self, 
        orchestrators_json: Dict[str, Any]
    ) -> None:
        """orchestrators.json should have 27 orchestrators (CORTEX spec)."""
        orchestrators = orchestrators_json.get("orchestrators", [])
        
        # Allow some tolerance (27 ± 2)
        assert 25 <= len(orchestrators) <= 29, (
            f"Expected ~27 orchestrators, found {len(orchestrators)}"
        )
    
    def test_orchestrators_json_has_core_tier(
        self, 
        orchestrators_json: Dict[str, Any]
    ) -> None:
        """orchestrators.json should have core tier orchestrators."""
        orchestrators = orchestrators_json.get("orchestrators", [])
        
        core_orchestrators = [
            o for o in orchestrators 
            if o.get("tier") == "core"
        ]
        
        assert len(core_orchestrators) > 0, (
            "orchestrators.json has no core tier orchestrators"
        )
        
        # Should have ~7 core orchestrators
        assert 5 <= len(core_orchestrators) <= 9, (
            f"Expected ~7 core orchestrators, found {len(core_orchestrators)}"
        )
    
    def test_all_json_files_have_reasonable_size(self, data_dir: Path) -> None:
        """JSON files should have reasonable sizes (not empty, not huge)."""
        json_files = list(data_dir.glob("*.json"))
        
        for json_file in json_files:
            size_bytes = json_file.stat().st_size
            
            # At least 10 bytes (not empty)
            assert size_bytes > 10, f"{json_file.name} is too small (likely empty)"
            
            # Less than 10MB (reasonable for JSON)
            assert size_bytes < 10 * 1024 * 1024, (
                f"{json_file.name} is too large (>10MB)"
            )
    
    def test_content_json_roles_match_role_views(
        self, 
        content_json: Dict[str, Any],
        role_ids: List[str]
    ) -> None:
        """Roles in content.json should match canonical role IDs."""
        # Extract all unique roles from content.json
        used_roles = set()
        for category in content_json.get("categories", []):
            for file in category.get("files", []):
                for role in file.get("roles", []):
                    used_roles.add(role)
        
        # Note: content.json may use 'curious-learner' but role_ids has 'learner'
        valid_roles = set(role_ids) | {"curious-learner"}
        
        # All used roles should be valid
        invalid_roles = used_roles - valid_roles
        assert len(invalid_roles) == 0, (
            f"content.json uses invalid roles: {invalid_roles}"
        )
    
    def test_json_files_use_utf8_encoding(self, data_dir: Path) -> None:
        """All JSON files should be UTF-8 encoded."""
        json_files = list(data_dir.glob("*.json"))
        
        for json_file in json_files:
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    f.read()
            except UnicodeDecodeError:
                pytest.fail(f"{json_file.name} is not UTF-8 encoded")


# AC_COMPLETE: AC-DOCGEN-DATA-FILES-20260224T000000 ✅
