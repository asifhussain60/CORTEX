"""
Discovery Package - Convention-Based Feature Detection

Auto-discovers CORTEX features without hardcoded lists:
- Orchestrators (operations, workflows)
- Agents (specialists, integrations)
- Entry points (response templates)
- Documentation (prompts, modules)
- Tests (coverage, validation)

Enhancement Discovery:
- Git history scanning
- YAML configuration parsing
- Codebase module detection
- Response template cataloging

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from src.discovery.orchestrator_scanner import OrchestratorScanner
from src.discovery.agent_scanner import AgentScanner
from src.discovery.entry_point_scanner import EntryPointScanner
from src.discovery.documentation_scanner import DocumentationScanner
from src.discovery.enhancement_discovery import EnhancementDiscoveryEngine, DiscoveredFeature

__all__ = [
    "OrchestratorScanner",
    "AgentScanner",
    "EntryPointScanner",
    "DocumentationScanner",
    "EnhancementDiscoveryEngine",
    "DiscoveredFeature",
]
