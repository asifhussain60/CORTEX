"""
Template Manager v4.0 - Orchestrates adaptive response generation

Key responsibilities:
- Load response-templates-v4.yaml
- Coordinate tier selection, section selection, rendering
- Cache template configuration
- Provide high-level API for orchestrators
"""

import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional

from src.config import get_config_manager
from src.logging import setup_logger
from src.templates.types import ResponseTier, TemplateContext
from src.templates.tier_selector import TierSelector
from src.templates.section_selector import SectionSelector
from src.templates.template_renderer import TemplateRenderer


class TemplateManager:
    """
    Main orchestrator for Response Templates v4.0
    
    Responsibilities:
    - Load template configuration from YAML
    - Coordinate tier selection
    - Coordinate section selection
    - Coordinate rendering
    - Cache configuration data
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize the template manager.
        
        Args:
            config_path: Optional path to response-templates-v4.yaml
        """
        self.logger = setup_logger(__name__)
        self.config_manager = get_config_manager()
        
        # Load template configuration
        if config_path is None:
            brain_path = Path(self.config_manager.get("brain.base_path", "cortex-brain"))
            config_path = brain_path / "response-templates-v4.yaml"
        
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self._load_config()
        
        # Initialize subsystems
        self.tier_selector = TierSelector(self.config)
        self.section_selector = SectionSelector(self.config)
        self.renderer = TemplateRenderer(self.config)
        
        self.logger.info(f"TemplateManager v4.0 initialized with {config_path}")
    
    def _load_config(self) -> None:
        """Load the template configuration from YAML"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            
            self.logger.info(
                f"Loaded template config: {self.config.get('schema_version', 'unknown')} "
                f"({len(str(self.config))} bytes)"
            )
        except FileNotFoundError:
            self.logger.error(f"Template config not found: {self.config_path}")
            self.config = {}
        except yaml.YAMLError as e:
            self.logger.error(f"Failed to parse template config: {e}")
            self.config = {}
    
    def generate_response(
        self,
        context: TemplateContext,
        content: Dict[str, str]
    ) -> str:
        """
        Generate a response using the adaptive template system.
        
        Args:
            context: Template context with operation details
            content: Section content keyed by section ID
        
        Returns:
            Formatted markdown response
        """
        # Step 1: Select tier
        tier = self.tier_selector.select_tier(context)
        self.logger.debug(f"Selected tier: {tier.value}")
        
        # Step 2: Select sections for this tier
        sections = self.section_selector.select_sections(tier, context)
        self.logger.debug(f"Selected {len(sections)} sections: {sections}")
        
        # Step 3: Render the response
        response = self.renderer.render(tier, sections, content, context)
        
        # Step 4: Log token estimate
        token_estimate = len(response.split())  # Rough approximation
        self.logger.info(
            f"Generated {tier.value} response: ~{token_estimate} tokens, "
            f"{len(sections)} sections"
        )
        
        return response
    
    def generate_success_response(
        self,
        operation: str,
        completion_summary: str,
        changes: str,
        optional_next_actions: str = ""
    ) -> str:
        """
        Generate a success/completion response (🎉 CONGRATULATIONS).
        
        Args:
            operation: Name of the completed operation
            completion_summary: Summary with metrics
            changes: Files modified and outcomes
            optional_next_actions: Optional next actions
        
        Returns:
            Formatted success response
        """
        context = TemplateContext(
            operation=operation,
            request="completion",
            all_work_complete=True,
            no_errors=True,
            no_user_action_required=True,
            has_modifications=True
        )
        
        content = {
            "understanding_scope": f"Completed {operation}",
            "approach_considerations": "No Challenge - All work completed successfully",
            "response": completion_summary,
            "impact_changes": changes,
            "next_steps": "✅ **Work Complete!** No further action required.\n\n" + optional_next_actions
        }
        
        return self.renderer.render_success(content, context)
    
    def get_tier_info(self) -> Dict[str, Any]:
        """
        Get information about available tiers.
        
        Returns:
            Dictionary with tier definitions and token limits
        """
        return {
            "tiers": [tier.value for tier in ResponseTier],
            "token_budgets": self.config.get("token_budget", {}),
            "routing": self.config.get("routing", {})
        }
    
    def get_section_library(self) -> List[Dict[str, Any]]:
        """
        Get the available sections from the section library.
        
        Returns:
            List of section definitions
        """
        return self.config.get("section_library", [])
    
    def reload_config(self) -> None:
        """Reload the template configuration from disk"""
        self._load_config()
        self.tier_selector = TierSelector(self.config)
        self.section_selector = SectionSelector(self.config)
        self.renderer = TemplateRenderer(self.config)
        self.logger.info("Template configuration reloaded")
