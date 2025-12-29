"""
Execution Mode Integration for Documentation Orchestrator

Provides context-aware formatting and mode selection for adaptive documentation generation.

Author: Asif Hussain
Version: 1.0
Created: December 21, 2025

Features:
- Context-aware formatting based on execution mode
- Integration with ExecutionModeManager from Phase 5
- Mode selection logic for documentation operations
- Adaptive output formatting (verbose vs concise)
"""

import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from logging import Logger

from ...execution.execution_mode import ExecutionMode
from ...execution.execution_mode_manager import (
    ExecutionModeManager, Operation, UserProfile, User
)


class OutputFormat(Enum):
    """Documentation output format"""
    VERBOSE = "verbose"  # Full details, all sections
    STANDARD = "standard"  # Normal level of detail
    CONCISE = "concise"  # Minimal, essential only
    SUMMARY = "summary"  # High-level overview only


@dataclass
class FormattingConfig:
    """Configuration for context-aware formatting"""
    include_examples: bool = True
    include_warnings: bool = True
    include_diagrams: bool = True
    include_quick_ref: bool = True
    detail_level: OutputFormat = OutputFormat.STANDARD
    max_description_length: int = 500  # Characters
    max_examples_per_item: int = 3


class ExecutionModeIntegration:
    """
    Integrates ExecutionModeManager with DocumentationOrchestrator
    
    Provides:
    - Context-aware formatting based on execution mode
    - Mode selection logic for documentation operations
    - Adaptive behavior (autonomous vs supervised vs human-in-loop)
    
    Usage:
        integration = ExecutionModeIntegration(logger, config, user_id="dev123")
        mode = integration.select_mode_for_operation("generate_api_docs")
        formatting = integration.get_formatting_config(mode)
    """
    
    def __init__(
        self,
        logger: Optional["Logger"] = None,
        config: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ):
        """
        Initialize execution mode integration
        
        Args:
            logger: Logger instance
            config: Configuration dictionary
            user_id: User identifier for mode selection
        """
        self.logger = logger or logging.getLogger(__name__)
        self.config = config or {}
        self.user_id = user_id or "default_user"
        
        # Initialize ExecutionModeManager
        self.user_profile = UserProfile(self.user_id)
        self.mode_manager = ExecutionModeManager(self.config, self.user_profile)
        
        # Mode-to-format mapping
        self._format_mappings = {
            ExecutionMode.AUTONOMOUS: OutputFormat.CONCISE,
            ExecutionMode.SUPERVISED: OutputFormat.STANDARD,
            ExecutionMode.HUMAN_IN_LOOP: OutputFormat.VERBOSE
        }
        
        self.logger.info(f"🎭 ExecutionModeIntegration initialized for user: {self.user_id}")
    
    def select_mode_for_operation(
        self,
        operation_name: str,
        estimated_duration: int = 60,
        override_mode: Optional[str] = None
    ) -> ExecutionMode:
        """
        Select appropriate execution mode for documentation operation
        
        Args:
            operation_name: Name of the documentation operation
            estimated_duration: Estimated duration in seconds
            override_mode: Optional mode override
            
        Returns:
            ExecutionMode: Selected execution mode
        """
        # Check for override
        if override_mode:
            try:
                mode = ExecutionMode(override_mode)
                self.logger.info(f"🎯 Mode override: {mode.value}")
                return mode
            except ValueError:
                self.logger.warning(f"⚠️  Invalid mode override: {override_mode}, using auto-select")
        
        # Create operation
        operation = Operation(
            name=operation_name,
            category="documentation",
            estimated_duration=estimated_duration
        )
        
        # Get mode from ExecutionModeManager
        mode = self.mode_manager.get_mode_for_operation(operation)
        
        self.logger.info(f"🎭 Selected mode for '{operation_name}': {mode.value}")
        return mode
    
    def get_formatting_config(self, mode: ExecutionMode) -> FormattingConfig:
        """
        Get formatting configuration based on execution mode
        
        Args:
            mode: Execution mode
            
        Returns:
            FormattingConfig: Context-aware formatting configuration
        """
        output_format = self._format_mappings.get(mode, OutputFormat.STANDARD)
        
        # Mode-specific formatting
        if mode == ExecutionMode.AUTONOMOUS:
            # Autonomous: Minimal output, fast generation
            config = FormattingConfig(
                include_examples=False,
                include_warnings=False,
                include_diagrams=False,
                include_quick_ref=True,
                detail_level=OutputFormat.CONCISE,
                max_description_length=200,
                max_examples_per_item=1
            )
        elif mode == ExecutionMode.SUPERVISED:
            # Supervised: Standard output with key details
            config = FormattingConfig(
                include_examples=True,
                include_warnings=True,
                include_diagrams=True,
                include_quick_ref=True,
                detail_level=OutputFormat.STANDARD,
                max_description_length=500,
                max_examples_per_item=2
            )
        else:  # HUMAN_IN_LOOP
            # Human-in-loop: Full verbosity, all details
            config = FormattingConfig(
                include_examples=True,
                include_warnings=True,
                include_diagrams=True,
                include_quick_ref=True,
                detail_level=OutputFormat.VERBOSE,
                max_description_length=1000,
                max_examples_per_item=3
            )
        
        self.logger.info(
            f"📝 Formatting config for {mode.value}: "
            f"detail={config.detail_level.value}, "
            f"diagrams={config.include_diagrams}, "
            f"examples={config.include_examples}"
        )
        
        return config
    
    def should_include_section(self, section_name: str, mode: ExecutionMode) -> bool:
        """
        Determine if a documentation section should be included based on mode
        
        Args:
            section_name: Name of the documentation section
            mode: Execution mode
            
        Returns:
            bool: True if section should be included
        """
        # Essential sections (always included)
        essential_sections = {
            "description",
            "parameters",
            "returns",
            "class_signature"
        }
        
        # Optional sections (mode-dependent)
        optional_sections = {
            "examples",
            "warnings",
            "notes",
            "see_also",
            "source_code"
        }
        
        # Verbose-only sections
        verbose_sections = {
            "implementation_details",
            "performance_notes",
            "history"
        }
        
        if section_name in essential_sections:
            return True
        
        if section_name in optional_sections:
            return mode in [ExecutionMode.SUPERVISED, ExecutionMode.HUMAN_IN_LOOP]
        
        if section_name in verbose_sections:
            return mode == ExecutionMode.HUMAN_IN_LOOP
        
        # Unknown section - include for supervised and human-in-loop
        return mode != ExecutionMode.AUTONOMOUS
    
    def format_description(self, text: str, mode: ExecutionMode) -> str:
        """
        Format description text based on execution mode
        
        Args:
            text: Original description text
            mode: Execution mode
            
        Returns:
            str: Formatted description
        """
        config = self.get_formatting_config(mode)
        max_length = config.max_description_length
        
        if len(text) <= max_length:
            return text
        
        # Truncate and add ellipsis
        truncated = text[:max_length].rsplit(' ', 1)[0]
        return f"{truncated}..."
    
    def get_execution_summary(self, mode: ExecutionMode) -> Dict[str, Any]:
        """
        Get execution summary for the selected mode
        
        Args:
            mode: Execution mode
            
        Returns:
            Dict with execution summary
        """
        return {
            "mode": mode.value,
            "description": mode.description,
            "risk_tolerance": mode.risk_tolerance,
            "speed_multiplier": mode.speed_multiplier,
            "formatting": self._format_mappings[mode].value,
            "user_action_required": mode == ExecutionMode.HUMAN_IN_LOOP
        }
    
    def update_user_stats(self, operation_name: str, success: bool) -> None:
        """
        Update user statistics after operation completion
        
        Args:
            operation_name: Name of the completed operation
            success: Whether operation succeeded
        """
        user = self.user_profile.get_user()
        user.completed_operations += 1
        
        if success:
            user.successful_operations += 1
        
        self.logger.info(
            f"📊 Updated user stats: "
            f"completed={user.completed_operations}, "
            f"successful={user.successful_operations}, "
            f"rate={user.success_rate:.1%}"
        )
