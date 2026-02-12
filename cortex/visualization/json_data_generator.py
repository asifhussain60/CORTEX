"""
JSON Data Generator - Transforms LENS analysis into dashboard JSON
Author: Asif Hussain
Date: 2026-02-04
Authority: CORE-008, CORE-030 (Implementation Truth)
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class JSONDataGenerator:
    """
    Generates dashboard.json from LENS analysis output.

    Transforms LENS data structure into dashboard JSON schema:
    - Input: LENS repository analysis (from cortex_lens_analyze)
    - Output: Structured dashboard JSON (for SPA rendering)

    Architecture:
    - Single SSOT: cortex/models/dashboard_schema_v3.py
    - Data transformation: LENS → Dashboard schema
    - Validation: Pydantic schema enforcement
    """

    def __init__(self):
        """Initialize generator"""
        self.schema_version = "3.0"
        logger.debug(f"JSONDataGenerator initialized (schema v{self.schema_version})")

    def generate(self, lens_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate dashboard JSON from LENS analysis.

        Args:
            lens_data: Raw LENS analysis output from cortex_lens_analyze

        Returns:
            Structured dashboard data dictionary
        """
        try:
            # Extract input sections (with defaults)
            repo_info = lens_data.get("repo", {})
            files = lens_data.get("files", [])
            metrics = lens_data.get("metrics", {})

            # Build dashboard structure
            dashboard = {
                "repo": self._build_repo_section(repo_info),
                "overview": self._build_overview_section(repo_info, files, metrics),
                "metrics": self._build_metrics_section(metrics, files),
                "files": self._build_files_section(files),
                "generated_at": datetime.utcnow().isoformat() + "Z"
            }

            logger.debug(f"Generated dashboard for {repo_info.get('name', 'unknown')}")
            return dashboard

        except Exception as e:
            logger.error(f"Error generating dashboard: {e}")
            # Return minimal valid structure
            return self._get_empty_dashboard()

    def _build_repo_section(self, repo_info: Dict[str, Any]) -> Dict[str, Any]:
        """Build 'repo' section from input"""
        name = repo_info.get("name", "Unknown Repository")
        return {
            "display_name": name,
            "slug": self._slugify(name),
            "path": repo_info.get("path", ""),
            "primary_language": repo_info.get("primary_language", "Unknown"),
            "description": repo_info.get("description", ""),
            "version": repo_info.get("version", ""),
            "last_analyzed_at": datetime.utcnow().isoformat() + "Z"
        }

    def _build_overview_section(self, repo_info: Dict[str, Any],
                               files: List[Dict],
                               metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Build 'overview' section with summary statistics"""
        return {
            "summary": repo_info.get("description", f"Repository: {repo_info.get('name', 'Unknown')}"),
            "file_count": len(files),
            "total_lines": sum(f.get("lines", 0) for f in files),
            "primary_language": repo_info.get("primary_language", "Unknown"),
            "last_updated": repo_info.get("last_updated", datetime.utcnow().isoformat() + "Z")
        }

    def _build_metrics_section(self, metrics: Dict[str, Any],
                              files: List[Dict]) -> Dict[str, Any]:
        """Build 'metrics' section with quality scores"""
        return {
            "health_score": metrics.get("health_score", 75),
            "total_files": len(files),
            "total_lines": metrics.get("total_lines", sum(f.get("lines", 0) for f in files)),
            "languages": self._extract_languages(files),
            "code_quality": metrics.get("code_quality", {}),
            "security_score": metrics.get("security_score", 70),
            "test_coverage": metrics.get("test_coverage", 0),
            "maintainability_index": metrics.get("maintainability_index", 50)
        }

    def _build_files_section(self, files: List[Dict]) -> List[Dict[str, Any]]:
        """Build 'files' section with file-level data"""
        return [
            {
                "path": f.get("path", ""),
                "language": f.get("language", "Unknown"),
                "lines": f.get("lines", 0),
                "complexity": f.get("complexity", 0),
                "coverage": f.get("coverage", 0)
            }
            for f in files[:100]  # Limit to first 100 for JSON size
        ]

    def _extract_languages(self, files: List[Dict]) -> Dict[str, int]:
        """Extract language distribution from files"""
        languages = {}
        for file in files:
            lang = file.get("language", "Other")
            languages[lang] = languages.get(lang, 0) + 1
        return languages

    def _slugify(self, name: str) -> str:
        """Convert repo name to URL-safe slug"""
        return name.lower().replace(" ", "-").replace("_", "-")

    def _get_empty_dashboard(self) -> Dict[str, Any]:
        """Return minimal valid dashboard structure"""
        return {
            "repo": {
                "display_name": "Unknown",
                "slug": "unknown",
                "path": "",
                "primary_language": "Unknown",
                "description": ""
            },
            "overview": {
                "summary": "Repository data unavailable",
                "file_count": 0,
                "total_lines": 0
            },
            "metrics": {
                "health_score": 0,
                "total_files": 0,
                "total_lines": 0,
                "languages": {},
                "security_score": 0
            },
            "files": [],
            "generated_at": datetime.utcnow().isoformat() + "Z"
        }

    def validate_schema(self, dashboard: Dict[str, Any]) -> bool:
        """
        Validate dashboard JSON against schema.

        Args:
            dashboard: Dashboard data to validate

        Returns:
            True if valid, False otherwise

        Note:
            Full Pydantic validation in downstream tools.
            This is a quick structural check.
        """
        required_keys = ["repo", "overview", "metrics"]
        return all(key in dashboard for key in required_keys)
