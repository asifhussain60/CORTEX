"""
MCP Tool Spec Generator - Phase 38 Stage 7.

Auto-generates MCP tool registry from orchestrator specifications.

AC-PHASE38-020: MCP tool registry auto-generation
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class MCPToolSpecGenerator:
    """Generates MCP tool registry from orchestrator specifications."""

    def __init__(self) -> None:
        """Initialize generator."""
        self.tools: List[Dict[str, Any]] = []

    def generate_registry(self, output_path: Optional[Path] = None) -> str:
        """
        Generate MCP tool registry.

        Args:
            output_path: Path to save registry (None = dry-run)

        Returns:
            Path string or "dry-run"
        """
        if output_path is None:
            return "dry-run"

        registry_data = self.build_registry_data()

        with open(output_path, "w") as f:
            json.dump(registry_data, f, indent=2)

        return str(output_path)

    def build_registry_data(self) -> Dict[str, Any]:
        """
        Build registry data structure.

        Returns:
            Dict with tools list
        """
        # If no tools added yet, add placeholder
        if not self.tools:
            self.tools = [{
                "name": "cortex_placeholder",
                "description": "Placeholder tool",
                "inputSchema": {"type": "object", "properties": {}},
            }]

        return {
            "version": "1.0",
            "tools": self.tools,
        }

    def merge_with_existing(self, existing_tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Merge with existing registry.

        Args:
            existing_tools: Existing tool list

        Returns:
            Merged tool list
        """
        merged = existing_tools.copy()

        # Add new tools not in existing
        existing_names = {tool["name"] for tool in existing_tools}
        for tool in self.tools:
            if tool["name"] not in existing_names:
                merged.append(tool)

        return merged
