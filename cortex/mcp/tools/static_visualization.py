"""
CORTEX Static Visualization MCP Tool - Phase 15 Implementation.

Exposes static repository visualization as MCP tool:
- cortex_visualize_portfolio: Multi-repo dashboard generation

AC-IDs: STATIC-VIZ-001 through STATIC-VIZ-007
Author: Asif Hussain
Date: 2026-01-31
"""

import json
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

from cortex.mcp.server import Tool, ToolDefinition, ToolParameter

logger = logging.getLogger(__name__)


class CORTEXVisualizePortfolioTool(Tool):
    """Multi-repository static visualization with domain aggregation."""

    @property
    def definition(self) -> ToolDefinition:
        """Get tool definition."""
        return ToolDefinition(
            name="cortex_visualize_portfolio",
            description="Generate static HTML dashboards for multi-repository portfolio analysis with domain aggregation",
            parameters=[
                ToolParameter(
                    name="output_dir",
                    type="string",
                    required=True,
                    description="Output directory for generated dashboard files"
                ),
                ToolParameter(
                    name="repository_paths",
                    type="array",
                    required=False,
                    description="Optional list of repository paths to analyze (defaults to current repo)"
                ),
                ToolParameter(
                    name="domain_mapping",
                    type="object",
                    required=False,
                    description="Optional domain mapping: {repo_name: domain_name}"
                ),
                ToolParameter(
                    name="personas",
                    type="array",
                    required=False,
                    description="Target personas: developers, managers, executives, regulatory, product (defaults to all)"
                ),
                ToolParameter(
                    name="include_entry_dashboard",
                    type="boolean",
                    required=False,
                    description="Whether to generate tabbed entry dashboard (default: true)"
                )
            ],
            metadata={
                "category": "visualization",
                "version": "1.0",
                "phase": "15",
                "ac_ids": ["STATIC-VIZ-001", "STATIC-VIZ-002", "STATIC-VIZ-003", 
                          "STATIC-VIZ-004", "STATIC-VIZ-005", "STATIC-VIZ-006", "STATIC-VIZ-007"]
            }
        )

    def execute(
        self,
        output_dir: str,
        repository_paths: Optional[List[str]] = None,
        domain_mapping: Optional[Dict[str, str]] = None,
        personas: Optional[List[str]] = None,
        include_entry_dashboard: bool = True,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Execute static visualization generation."""
        try:
            from cortex.visualization.static_visualization_orchestrator import StaticVisualizationOrchestrator
            from cortex.visualization.multi_persona_generator import MultiPersonaGenerator
            from cortex.visualization.domain_knowledge_accumulator import DomainKnowledgeAccumulator
            from cortex.visualization.three_tier_hierarchy import ThreeTierHierarchy

            # Step 1: Initialize orchestrator (AC-STATIC-VIZ-001)
            logger.info("AC-STATIC-VIZ-001: Initializing StaticVisualizationOrchestrator")
            orchestrator = StaticVisualizationOrchestrator(
                output_dir=Path(output_dir)
            )
            
            # Step 2: Generate multi-persona dashboards (AC-STATIC-VIZ-002)
            logger.info("AC-STATIC-VIZ-002: Generating multi-persona HTML")
            persona_generator = MultiPersonaGenerator()
            
            target_personas = personas or ["developers", "managers", "executives", "regulatory", "product"]
            
            # Step 3: Accumulate domain knowledge (AC-STATIC-VIZ-003)
            logger.info("AC-STATIC-VIZ-003: Accumulating domain knowledge")
            domain_accumulator = DomainKnowledgeAccumulator()
            
            repos = repository_paths or [str(Path.cwd())]
            domain_knowledge = domain_accumulator.accumulate(
                repository_paths=repos,
                domain_mapping=domain_mapping or {}
            )
            
            # Step 4: Generate 3-tier hierarchy (AC-STATIC-VIZ-004)
            logger.info("AC-STATIC-VIZ-004: Building 3-tier dashboard hierarchy")
            hierarchy = ThreeTierHierarchy()
            
            # Generate entry dashboard if requested
            if include_entry_dashboard:
                entry_dashboard = orchestrator.generate_entry_dashboard(
                    repositories=repos,
                    domain_knowledge=domain_knowledge
                )
            else:
                entry_dashboard = None
            
            # Generate individual repo dashboards
            repo_dashboards = []
            for repo_path in repos:
                dashboard = orchestrator.generate_repo_dashboard(
                    repo_path=Path(repo_path),
                    personas=target_personas
                )
                repo_dashboards.append(dashboard)
            
            # Generate domain dashboards
            domain_dashboards = []
            for domain_name in domain_knowledge.keys():
                dashboard = orchestrator.generate_domain_dashboard(
                    domain_name=domain_name,
                    domain_data=domain_knowledge[domain_name]
                )
                domain_dashboards.append(dashboard)
            
            return {
                "status": "success",
                "output_dir": output_dir,
                "generated_files": {
                    "entry_dashboard": entry_dashboard.get("path") if entry_dashboard else None,
                    "repo_dashboards": [d.get("path") for d in repo_dashboards],
                    "domain_dashboards": [d.get("path") for d in domain_dashboards],
                    "total_files": (1 if entry_dashboard else 0) + len(repo_dashboards) + len(domain_dashboards)
                },
                "statistics": {
                    "repositories_analyzed": len(repos),
                    "domains_detected": len(domain_knowledge),
                    "personas_generated": len(target_personas),
                    "total_dashboards": len(repo_dashboards) + len(domain_dashboards)
                },
                "domain_knowledge": {
                    domain: {
                        "repo_count": data.get("repo_count", 0),
                        "entity_count": data.get("entity_count", 0),
                        "tech_stack": data.get("tech_stack", [])
                    }
                    for domain, data in domain_knowledge.items()
                },
                "visualization": {
                    "d3_system": "bundled_locally",
                    "offline_first": True,
                    "glassmorphism_theme": True
                }
            }

        except ImportError as e:
            logger.error(f"Phase 15 visualization module import failed: {e}", exc_info=True)
            return {
                "status": "error",
                "error": f"Static visualization modules not available: {str(e)}",
                "hint": "Ensure Phase 15 implementation is complete"
            }
        except Exception as e:
            logger.error(f"Portfolio visualization failed: {e}", exc_info=True)
            return {
                "status": "error",
                "error": f"Failed to generate portfolio visualization: {str(e)}"
            }


# Register tool
CORTEX_VISUALIZATION_TOOLS = [
    CORTEXVisualizePortfolioTool()
]
