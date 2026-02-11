"""
MCP Tool Wrappers for Security Analysis (Phase 8.2-8.4).

Provides MCP-compatible tool interfaces for:
- SecurityThreatAnalyzer (Phase 8.2)
- RecommendationEngine (Phase 8.4)

Authority: AC-SECURITY-FRAMEWORK-001
"""

import logging
from dataclasses import asdict
from typing import Any, Dict, List, Optional

from cortex.brain.analysis.security_threat_analyzer import (
    SecurityThreatAnalyzer,
    get_security_threat_analyzer,
)
from cortex.orchestrators.support.recommendation_engine import (
    RecommendationEngine,
    get_recommendation_engine,
)

logger = logging.getLogger(__name__)


class SecurityThreatAnalyzerTool:
    """MCP wrapper for SecurityThreatAnalyzer."""

    def __init__(self):
        """Initialize tool."""
        self.analyzer = get_security_threat_analyzer()

    def analyze_code_for_threats(
        self,
        code: str,
        file_path: str = "code.py"
    ) -> Dict[str, Any]:
        """
        Analyze code for security threats.

        Args:
            code: Python source code to analyze
            file_path: Path to file (for context)

        Returns:
            Dict with threat findings
        """
        result = self.analyzer.analyze_code(code, file_path)

        return {
            "success": result.success,
            "file_path": result.file_path,
            "analysis_time_ms": result.analysis_time_ms,
            "patterns_checked": result.patterns_checked,
            "threat_count": len(result.threat_findings),
            "threats": [
                {
                    "cwe_id": t.cwe_id,
                    "severity": t.severity.name,
                    "line_number": t.line_number,
                    "pattern_name": t.pattern_name,
                    "description": t.description,
                    "recommendation": t.recommendation,
                    "code_snippet": t.code_snippet,
                }
                for t in result.threat_findings
            ],
            "error": result.error,
        }


class RecommendationEngineTool:
    """MCP wrapper for RecommendationEngine."""

    def __init__(self):
        """Initialize tool."""
        self.engine = get_recommendation_engine()

    def recommend_security_fix(
        self,
        cwe_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get security recommendations for a CWE.

        Args:
            cwe_id: CWE identifier (e.g., "CWE-94")
            context: Additional context

        Returns:
            Dict with recommendations
        """
        result = self.engine.recommend_for_security(cwe_id, context or {})

        return {
            "success": result.success,
            "summary": result.summary,
            "recommendation_count": len(result.recommendations),
            "recommendations": [
                {
                    "advisor_type": rec.advisor_type.value,
                    "pattern_id": rec.pattern_id,
                    "title": rec.title,
                    "description": rec.description,
                    "severity": rec.severity,
                    "code_example": rec.code_example,
                    "rationale": rec.rationale,
                }
                for rec in result.recommendations
            ],
            "error": result.error,
        }

    def recommend_solid_fix(
        self,
        violation_type: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get SOLID principle recommendations.

        Args:
            violation_type: Type of violation (SRP, OCP, etc.)
            context: Additional context

        Returns:
            Dict with recommendations
        """
        result = self.engine.recommend_for_solid(violation_type, context or {})

        return {
            "success": result.success,
            "summary": result.summary,
            "recommendation_count": len(result.recommendations),
            "recommendations": [
                {
                    "advisor_type": rec.advisor_type.value,
                    "pattern_id": rec.pattern_id,
                    "title": rec.title,
                    "description": rec.description,
                }
                for rec in result.recommendations
            ],
            "error": result.error,
        }


# Tool instances for MCP registry
_security_analyzer_tool = None
_recommendation_tool = None


def get_security_threat_analyzer_tool() -> SecurityThreatAnalyzerTool:
    """Factory for SecurityThreatAnalyzerTool."""
    global _security_analyzer_tool
    if _security_analyzer_tool is None:
        _security_analyzer_tool = SecurityThreatAnalyzerTool()
    return _security_analyzer_tool


def get_recommendation_engine_tool() -> RecommendationEngineTool:
    """Factory for RecommendationEngineTool."""
    global _recommendation_tool
    if _recommendation_tool is None:
        _recommendation_tool = RecommendationEngineTool()
    return _recommendation_tool


# Tool registry entries for MCP discovery
SECURITY_TOOLS = [
    {
        "name": "analyze_code_for_threats",
        "module": "cortex.mcp.tools.security",
        "function": "analyze_code_for_threats_mcp",
        "description": "Analyze Python code for security threats (CWE vulnerabilities)",
        "category": "security",
        "parameters": {
            "code": "str (Python source code)",
            "file_path": "str (optional, defaults to 'code.py')",
        },
        "returns": "Dict with threat findings and CWE details",
        "phase": "8.2",
        "authority": "AC-SECURITY-FRAMEWORK-001",
    },
    {
        "name": "recommend_security_fix",
        "module": "cortex.mcp.tools.security",
        "function": "recommend_security_fix_mcp",
        "description": "Get security recommendations for a CWE vulnerability",
        "category": "recommendations",
        "parameters": {
            "cwe_id": "str (e.g., 'CWE-94')",
            "context": "dict (optional, additional context)",
        },
        "returns": "Dict with best practice recommendations",
        "phase": "8.4",
        "authority": "AC-SECURITY-FRAMEWORK-001",
    },
    {
        "name": "recommend_solid_fix",
        "module": "cortex.mcp.tools.security",
        "function": "recommend_solid_fix_mcp",
        "description": "Get SOLID principle recommendations",
        "category": "recommendations",
        "parameters": {
            "violation_type": "str (SRP, OCP, LSP, ISP, DIP)",
            "context": "dict (optional, additional context)",
        },
        "returns": "Dict with SOLID recommendations",
        "phase": "8.4",
        "authority": "AC-SECURITY-FRAMEWORK-001",
    },
]


# MCP Tool Functions (exported for registry)

def analyze_code_for_threats_mcp(code: str, file_path: str = "code.py") -> Dict[str, Any]:
    """MCP endpoint for code threat analysis."""
    tool = get_security_threat_analyzer_tool()
    return tool.analyze_code_for_threats(code, file_path)


def recommend_security_fix_mcp(cwe_id: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """MCP endpoint for security fix recommendations."""
    tool = get_recommendation_engine_tool()
    return tool.recommend_security_fix(cwe_id, context)


def recommend_solid_fix_mcp(violation_type: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """MCP endpoint for SOLID fix recommendations."""
    tool = get_recommendation_engine_tool()
    return tool.recommend_solid_fix(violation_type, context)
