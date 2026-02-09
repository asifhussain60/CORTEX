"""
Phase 63: LENS Tiered MCP API - Orchestrator Integration

MCP tool definitions and orchestrator wiring for all LENS tiers.

AC_START: AC-PHASE63-ORCHESTRATOR-001
"""

from typing import List, Optional, Dict
from pathlib import Path
import json
from dataclasses import asdict

from cortex.lens.lens_tiered_mcp_api import (
    LensOrchestratorIntegration,
    LensAnalysisResult,
)


class LensMCPTools:
    """MCP Tool definitions for LENS Tiered API"""
    
    @staticmethod
    def cortex_lens_quick_tool_definition() -> Dict:
        """
        MCP Tool: cortex_lens_quick
        
        Tier 2 quick analysis (<200ms) for fast feedback loops.
        Used by InteractionOrchestrator for real-time analysis.
        
        Parameters:
            - file_path (required): Path to file for analysis
            - cache (optional): Use cached results (default: true)
        
        Returns:
            LensAnalysisResult (Tier 2) with high-priority findings
        """
        return {
            "name": "cortex_lens_quick",
            "description": "Tier 2 Quick Analysis (<200ms) - Fast feedback for InteractionOrchestrator",
            "tier": "tier_2_quick",
            "latency_sla_ms": 200,
            "parameters": {
                "file_path": {
                    "type": "string",
                    "required": True,
                    "description": "Path to file for analysis",
                },
                "cache": {
                    "type": "boolean",
                    "required": False,
                    "default": True,
                    "description": "Use cached results if available",
                },
            },
            "output_schema": {
                "tier": "tier_2_quick",
                "file_path": "string",
                "timestamp": "string",
                "findings": "list[dict]",
                "capabilities_used": "list[string]",
                "analysis_time_ms": "float",
            },
        }
    
    @staticmethod
    def cortex_lens_targeted_tool_definition() -> Dict:
        """
        MCP Tool: cortex_lens_targeted
        
        Tier 3 targeted analysis with custom capabilities.
        Used by PlanOrchestrator for selective validation.
        
        Parameters:
            - file_path (required): Path to file for analysis
            - capabilities (optional): List of capability names to execute
        
        Returns:
            LensAnalysisResult (Tier 3) with targeted findings
        """
        return {
            "name": "cortex_lens_targeted",
            "description": "Tier 3 Targeted Analysis - Custom capabilities for selective analysis",
            "tier": "tier_3_targeted",
            "latency_sla_ms": 2000,
            "parameters": {
                "file_path": {
                    "type": "string",
                    "required": True,
                    "description": "Path to file for analysis",
                },
                "capabilities": {
                    "type": "list[string]",
                    "required": False,
                    "description": "Custom capabilities to execute (defaults to medium-priority)",
                },
            },
            "output_schema": {
                "tier": "tier_3_targeted",
                "file_path": "string",
                "timestamp": "string",
                "findings": "list[dict]",
                "capabilities_used": "list[string]",
                "analysis_time_ms": "float",
            },
        }
    
    @staticmethod
    def cortex_lens_stream_tool_definition() -> Dict:
        """
        MCP Tool: cortex_lens_stream
        
        Tier 3 streaming analysis for large repositories.
        Emits progressive results without blocking.
        
        Parameters:
            - repo_path (required): Repository path to analyze
            - batch_size (optional): Files per batch (default: 10)
            - capabilities (optional): Custom capabilities to execute
        
        Yields:
            StreamEvent objects (progress, result, complete, error)
        """
        return {
            "name": "cortex_lens_stream",
            "description": "Tier 3 Streaming Analysis - Progressive results for large repositories",
            "tier": "tier_3_stream",
            "streaming": True,
            "parameters": {
                "repo_path": {
                    "type": "string",
                    "required": True,
                    "description": "Repository path to analyze",
                },
                "batch_size": {
                    "type": "integer",
                    "required": False,
                    "default": 10,
                    "description": "Files to analyze per batch",
                },
                "capabilities": {
                    "type": "list[string]",
                    "required": False,
                    "description": "Custom capabilities to execute",
                },
            },
            "stream_events": [
                "progress",  # Analysis progress
                "result",    # Batch results
                "error",     # Analysis errors
                "complete",  # Streaming complete
            ],
        }
    
    @staticmethod
    def cortex_lens_analyze_tool_definition() -> Dict:
        """
        MCP Tool: cortex_lens_analyze (UNCHANGED)
        
        Tier 4 full analysis - comprehensive, unchanged from Phase 62.
        Used by RepositoryOnboardingOrchestrator for complete analysis.
        
        Parameters:
            - file_path (required): Path to file for analysis
        
        Returns:
            LensAnalysisResult (Tier 4) with all findings
        """
        return {
            "name": "cortex_lens_analyze",
            "description": "Tier 4 Full Analysis - Comprehensive analysis (unchanged, backward compatible)",
            "tier": "tier_4_full",
            "latency_sla_ms": 10000,
            "backward_compatible": True,
            "parameters": {
                "file_path": {
                    "type": "string",
                    "required": True,
                    "description": "Path to file for analysis",
                },
            },
            "output_schema": {
                "tier": "tier_4_full",
                "file_path": "string",
                "timestamp": "string",
                "findings": "list[dict]",
                "capabilities_used": "list[string]",
                "analysis_time_ms": "float",
            },
        }


class LensOrchestratorWiring:
    """Orchestrator wiring for LENS Tiered API"""
    
    @staticmethod
    def get_wiring_configuration() -> Dict:
        """
        Get complete orchestrator wiring for LENS Tiered API.
        
        Returns:
            Wiring configuration dictionary for GitBackedRegistry
        """
        # AC_START: AC-PHASE63-WIRING-001 Orchestrator integration
        return {
            "interaction_orchestrator": {
                "tier": "tier_2_quick",
                "mcp_tool": "cortex_lens_quick",
                "purpose": "Real-time analysis for user interactions",
                "latency_requirement": "< 200ms",
                "use_cache": True,
            },
            "tdd_orchestrator": {
                "tier": "tier_2_quick",
                "mcp_tool": "cortex_lens_quick",
                "purpose": "Context enrichment during TDD cycles",
                "latency_requirement": "< 200ms",
                "use_case": "RED phase context, GREEN phase validation",
            },
            "plan_orchestrator": {
                "tier": "tier_3_targeted",
                "mcp_tool": "cortex_lens_targeted",
                "purpose": "Plan validation with custom capabilities",
                "latency_requirement": "< 2s",
                "default_capabilities": [
                    "syntax_check",
                    "type_hints_analysis",
                    "import_analysis",
                ],
            },
            "repository_onboarding_orchestrator": {
                "tier": "tier_4_full",
                "mcp_tool": "cortex_lens_analyze",
                "purpose": "Complete repository analysis",
                "latency_requirement": "< 10s",
                "use_case": "Initial onboarding, full audit",
                "backward_compatible": True,
            },
            "large_repository_support": {
                "tier": "tier_3_stream",
                "mcp_tool": "cortex_lens_stream",
                "purpose": "Progressive analysis for large codebases",
                "file_threshold": 500,
                "default_batch_size": 10,
            },
        }
        # AC_COMPLETE: AC-PHASE63-WIRING-001


class LensOrchestratorTierSelection:
    """Intelligent tier selection for orchestrators"""
    
    @staticmethod
    def select_tier_for_intent(intent: str, repo_size: int = 0) -> str:
        """
        Select appropriate LENS tier based on orchestrator intent.
        
        Args:
            intent: Orchestrator intent (interact, tdd, plan, onboard, stream)
            repo_size: Repository size in files (for stream selection)
        
        Returns:
            Tier name (tier_2_quick, tier_3_targeted, tier_3_stream, tier_4_full)
        """
        # AC_START: AC-PHASE63-SELECTION-001 Tier selection logic
        tier_map = {
            "interact": "tier_2_quick",
            "tdd": "tier_2_quick",
            "plan": "tier_3_targeted",
            "onboard": "tier_4_full",
            "stream": "tier_3_stream",
        }
        
        selected_tier = tier_map.get(intent, "tier_2_quick")
        
        # Override for large repositories
        if intent != "stream" and repo_size > 500:
            selected_tier = "tier_3_stream"
        
        return selected_tier
        # AC_COMPLETE: AC-PHASE63-SELECTION-001
    
    @staticmethod
    def get_tier_characteristics(tier: str) -> Dict:
        """Get characteristics of specified tier"""
        characteristics = {
            "tier_2_quick": {
                "latency_ms": 200,
                "throughput_rps": 100,
                "caching": True,
                "cache_hit_target": 0.7,
                "use_cases": ["interaction", "context_enrichment"],
            },
            "tier_3_targeted": {
                "latency_ms": 2000,
                "throughput_rps": 10,
                "caching": False,
                "custom_capabilities": True,
                "use_cases": ["validation", "planning"],
            },
            "tier_3_stream": {
                "latency_ms": 0,  # Progressive
                "throughput_rps": 1000,
                "streaming": True,
                "batch_processing": True,
                "use_cases": ["large_repositories"],
            },
            "tier_4_full": {
                "latency_ms": 10000,
                "throughput_rps": 1,
                "comprehensive": True,
                "use_cases": ["onboarding", "audit"],
            },
        }
        return characteristics.get(tier, {})
    
    @staticmethod
    def select_tier_with_escalation(
        initial_tier: str,
        tier_2_result: Optional[Dict] = None,
        context: Optional[Dict] = None,
    ) -> str:
        """
        AC-PHASE64-S2-001: Select tier with intelligent escalation.
        
        Escalation triggers:
        1. Critical findings detected → Escalate to Tier 3
        2. Ambiguous results (confidence < 0.7) → Escalate to Tier 3
        3. Clear results → Stay with default tier
        
        Args:
            initial_tier: Starting tier (usually tier_2_quick)
            tier_2_result: Results from Tier 2 analysis
            context: Orchestrator context
        
        Returns:
            Selected tier after escalation evaluation
        """
        if tier_2_result is None:
            return initial_tier
        
        # Check for critical findings (security, performance issues)
        findings = tier_2_result.get("findings", [])
        has_critical = any(
            f.get("severity", "info").lower() == "critical"
            for f in findings
        )
        
        if has_critical:
            # Critical findings found → escalate to Tier 3
            return "tier_3_targeted"
        
        # Check for ambiguous results (confidence < 0.7)
        avg_confidence = 0.0
        if findings:
            confidences = [f.get("confidence", 0.5) for f in findings]
            avg_confidence = sum(confidences) / len(confidences)
        
        if avg_confidence < 0.7:
            # Ambiguous results → escalate to Tier 3
            return "tier_3_targeted"
        
        # Clear results → stay with initial tier
        return initial_tier


class LensIntegrationOrchestrator:
    """Coordinates all LENS tier operations"""
    
    def __init__(self):
        """Initialize LENS integration orchestrator"""
        self.integration = LensOrchestratorIntegration()
        self.tools = LensMCPTools()
        self.wiring = LensOrchestratorWiring()
        self.selection = LensOrchestratorTierSelection()
    
    async def execute_interaction_analysis(self, file_path: Path) -> Dict:
        """Execute Tier 2 quick analysis for interactions"""
        result = await self.integration.interaction_orchestrator_quick_analysis(
            file_path
        )
        return result.to_dict()
    
    async def execute_tdd_enrichment(self, file_path: Path) -> Dict:
        """Execute Tier 2 context enrichment for TDD"""
        result = await self.integration.tdd_orchestrator_context_enrichment(
            file_path
        )
        return result.to_dict()
    
    async def execute_plan_validation(
        self,
        file_path: Path,
        capabilities: Optional[List[str]] = None,
    ) -> Dict:
        """Execute Tier 3 targeted validation for planning"""
        result = await self.integration.plan_orchestrator_validation(
            file_path,
            capabilities,
        )
        return result.to_dict()
    
    async def execute_onboarding_analysis(self, file_path: Path) -> Dict:
        """Execute Tier 4 full analysis for onboarding"""
        result = await self.integration.onboarding_orchestrator_full_analysis(
            file_path
        )
        return result.to_dict()
    
    def get_mcp_tools_manifest(self) -> Dict:
        """
        Get manifest of all available MCP tools.
        
        Returns:
            Dictionary of MCP tool definitions
        """
        return {
            "cortex_lens_quick": self.tools.cortex_lens_quick_tool_definition(),
            "cortex_lens_targeted": self.tools.cortex_lens_targeted_tool_definition(),
            "cortex_lens_stream": self.tools.cortex_lens_stream_tool_definition(),
            "cortex_lens_analyze": self.tools.cortex_lens_analyze_tool_definition(),
        }
    
    def get_orchestrator_wiring(self) -> Dict:
        """Get complete orchestrator wiring configuration"""
        return self.wiring.get_wiring_configuration()


# AC_COMPLETE: AC-PHASE63-ORCHESTRATOR-001 (EOF)
