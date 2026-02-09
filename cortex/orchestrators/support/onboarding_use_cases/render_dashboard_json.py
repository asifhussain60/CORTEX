"""
Render Dashboard JSON Use Case (Phase 54-A S1)

AC_START: AC-PHASE54A-S1-UC05
Description: Convert data models to dashboard JSON
Authority: phase-54-A-incremental-onboarding-refactor.yaml, S1 task 5
"""

from pathlib import Path
from typing import Dict, Any
from dataclasses import asdict
import json

from cortex.brain.core.result import Result, Ok, Err


class RenderDashboardJSONUseCase:
    """Render dashboard JSON (SOLID: Single Responsibility)."""
    
    def execute(
        self,
        repo_overview: Dict[str, Any],
        security_threats: list,
        business_narrative: Dict[str, Any],
        dependency_graph: Dict[str, Any],
    ) -> Result[Dict[str, Any]]:
        """
        Convert data models to dashboard JSON.
        
        Args:
            repo_overview: Repository overview data
            security_threats: List of security threats
            business_narrative: Business narrative data
            dependency_graph: Dependency graph data
            
        Returns:
            Result containing dashboard JSON or error
        """
        try:
            dashboard = {
                "version": "1.0",
                "generated_at": self._get_timestamp(),
                "sections": {
                    "overview": self._render_overview_section(repo_overview),
                    "security": self._render_security_section(security_threats),
                    "business": self._render_business_section(business_narrative),
                    "dependencies": self._render_dependencies_section(dependency_graph),
                },
                "metadata": {
                    "schema_version": "1.0",
                    "valid": True,
                },
            }
            
            return Ok(dashboard)
        
        except Exception as e:
            return Err(f"Failed to render dashboard JSON: {str(e)}")
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _render_overview_section(self, overview: Dict[str, Any]) -> Dict[str, Any]:
        """Render overview section."""
        return {
            "name": overview.get("name", "Unknown"),
            "path": overview.get("path", ""),
            "file_count": overview.get("file_count", 0),
            "languages": overview.get("language_distribution", {}),
            "has_tests": overview.get("has_tests", False),
            "test_framework": overview.get("test_framework"),
            "has_docs": overview.get("has_docs", False),
        }
    
    def _render_security_section(self, threats: list) -> Dict[str, Any]:
        """Render security section."""
        p0_threats = [t for t in threats if t.get("level") == "P0"]
        p1_threats = [t for t in threats if t.get("level") == "P1"]
        p2_threats = [t for t in threats if t.get("level") == "P2"]
        
        return {
            "total_threats": len(threats),
            "p0_count": len(p0_threats),
            "p1_count": len(p1_threats),
            "p2_count": len(p2_threats),
            "threats": threats,
        }
    
    def _render_business_section(self, narrative: Dict[str, Any]) -> Dict[str, Any]:
        """Render business section."""
        return {
            "title": narrative.get("title", ""),
            "description": narrative.get("description", ""),
            "value_proposition": narrative.get("value_proposition", ""),
            "target_audience": narrative.get("target_audience", ""),
            "capabilities": narrative.get("key_capabilities", []),
            "outcomes": narrative.get("business_outcomes", []),
            "confidence": narrative.get("confidence_score", 0.0),
        }
    
    def _render_dependencies_section(self, graph: Dict[str, Any]) -> Dict[str, Any]:
        """Render dependencies section."""
        return {
            "total_count": graph.get("dependency_count", 0),
            "runtime_count": graph.get("runtime_count", 0),
            "dev_count": graph.get("dev_count", 0),
            "dependencies": graph.get("dependencies", []),
        }
    
    def write_to_file(self, dashboard: Dict[str, Any], output_path: Path) -> Result[Path]:
        """
        Write dashboard JSON to file.
        
        Args:
            dashboard: Dashboard data
            output_path: Path to write JSON file
            
        Returns:
            Result containing output path or error
        """
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, "w") as f:
                json.dump(dashboard, f, indent=2, default=str)
            
            return Ok(output_path)
        
        except Exception as e:
            return Err(f"Failed to write dashboard JSON: {str(e)}")


# AC_COMPLETE: AC-PHASE54A-S1-UC05 ✅
