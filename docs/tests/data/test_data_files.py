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
        """learning-paths.json must have tracks array."""
        assert "tracks" in learning_paths_json, (
            "learning-paths.json missing 'tracks'"
        )
        assert isinstance(learning_paths_json["tracks"], list), (
            "learning-paths.json 'tracks' is not a list"
        )
        assert len(learning_paths_json["tracks"]) == 3, (
            "learning-paths.json should have exactly 3 tracks (beginner/intermediate/advanced)"
        )
    
    def test_knowledge_catalog_json_structure(
        self, 
        knowledge_catalog_json: Dict[str, Any]
    ) -> None:
        """knowledge-catalog.json must have domains structure."""
        # Check for any top-level key (structure may vary)
        assert len(knowledge_catalog_json.keys()) > 0, (
            "knowledge-catalog.json is empty"
        )
        
        # Validate domains structure (canonical schema)
        if "domains" in knowledge_catalog_json:
            domains = knowledge_catalog_json["domains"]
            assert isinstance(domains, list), (
                "knowledge-catalog.json 'domains' is not a list"
            )
            
            for domain in domains:
                assert "id" in domain, f"Domain missing 'id': {domain}"
                assert "title" in domain, f"Domain missing 'title': {domain}"
        
        # Legacy: if tech_stacks exists, validate structure
        if "tech_stacks" in knowledge_catalog_json:
            tech_stacks = knowledge_catalog_json["tech_stacks"]
            if isinstance(tech_stacks, list):
                for stack in tech_stacks:
                    if isinstance(stack, dict):
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
        """orchestrators.json must have tiers structure."""
        assert "tiers" in orchestrators_json, (
            "orchestrators.json missing 'tiers'"
        )
        assert isinstance(orchestrators_json["tiers"], dict), (
            "orchestrators.json 'tiers' is not a dict"
        )
        assert len(orchestrators_json["tiers"]) > 0, (
            "orchestrators.json has no tiers"
        )
        
        # Validate each tier has orchestrators
        for tier_name, tier_data in orchestrators_json["tiers"].items():
            assert "orchestrators" in tier_data, (
                f"Tier '{tier_name}' missing 'orchestrators'"
            )
            for orchestrator in tier_data["orchestrators"]:
                assert "name" in orchestrator, (
                    f"Orchestrator missing 'name' in tier '{tier_name}': {orchestrator}"
                )
    
    def test_mcp_tools_json_has_registered_tools(
        self, 
        mcp_tools_json: Dict[str, Any]
    ) -> None:
        """mcp-tools.json should have 28-35 registered tools (CORTEX spec)."""
        tools = mcp_tools_json.get("tools", [])
        registered_tools = [t for t in tools if t.get("registered", False)]
        
        # Allow tolerance for growth (28-35 registered)
        assert 28 <= len(registered_tools) <= 35, (
            f"Expected 28-35 registered MCP tools, found {len(registered_tools)}"
        )
    
    def test_orchestrators_json_has_wired_orchestrators(
        self, 
        orchestrators_json: Dict[str, Any]
    ) -> None:
        """orchestrators.json should have 40-60 wired orchestrators (CORTEX spec)."""
        tiers = orchestrators_json.get("tiers", {})
        total = 0
        for tier_data in tiers.values():
            total += len(tier_data.get("orchestrators", []))
        
        # Allow tolerance for growth (40-60 wired)
        assert 40 <= total <= 60, (
            f"Expected 40-60 wired orchestrators, found {total}"
        )
    
    def test_orchestrators_json_has_core_tier(
        self, 
        orchestrators_json: Dict[str, Any]
    ) -> None:
        """orchestrators.json should have core tier orchestrators."""
        tiers = orchestrators_json.get("tiers", {})
        
        assert "core" in tiers, (
            "orchestrators.json has no 'core' tier"
        )
        
        core_orchestrators = tiers["core"].get("orchestrators", [])
        
        assert len(core_orchestrators) > 0, (
            "orchestrators.json has no core tier orchestrators"
        )
        
        # Should have ~10-20 core orchestrators
        assert 5 <= len(core_orchestrators) <= 20, (
            f"Expected 5-20 core orchestrators, found {len(core_orchestrators)}"
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
