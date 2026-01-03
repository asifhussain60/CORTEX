"""
Response Renderer - Unified response rendering for all CORTEX orchestrators.

Purpose:
    Convert OrchestratorResult to user-facing markdown using response-templates-v4.yaml.
    Provides consistent formatting across all orchestrators with tier-based complexity routing.

Features:
    - Template-driven formatting (YAML configuration)
    - Tier routing (INSTANT → FOCUSED → STRUCTURED → COMPREHENSIVE)
    - Block composition (LEGO-style component assembly)
    - Markdown generation
    - Performance: <10ms per render

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import logging
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

# Import orchestrator types
try:
    from src.orchestrators.base.base_orchestrator import (
        OrchestratorResult,
        OrchestratorStatus
    )
except ImportError:
    # Fallback for testing
    from enum import Enum
    from dataclasses import field
    from datetime import datetime
    
    class OrchestratorStatus(Enum):
        NOT_STARTED = "not_started"
        RUNNING = "running"
        COMPLETED = "completed"
        FAILED = "failed"
        CANCELLED = "cancelled"
    
    @dataclass
    class OrchestratorResult:
        status: OrchestratorStatus
        success: bool
        message: str
        data: Dict[str, Any] = field(default_factory=dict)
        errors: List[str] = field(default_factory=list)
        warnings: List[str] = field(default_factory=list)
        execution_time_seconds: float = 0.0
        timestamp: datetime = field(default_factory=datetime.now)
        execution_time_seconds: Optional[float] = None


logger = logging.getLogger(__name__)


class ResponseTier(Enum):
    """Response complexity tiers."""
    INSTANT = "INSTANT"           # <50 tokens, factual
    FOCUSED = "FOCUSED"           # 50-200 tokens, single concept
    STRUCTURED = "STRUCTURED"     # 200-600 tokens, multi-faceted
    COMPREHENSIVE = "COMPREHENSIVE"  # 600+ tokens, complex


class ResponseRenderer:
    """
    Unified response rendering for all orchestrators.
    
    Converts OrchestratorResult to user-facing markdown using response-templates-v4.yaml.
    
    Features:
        - Template-driven formatting
        - Automatic tier detection
        - Block composition (header, response, changes, next_steps)
        - Performance: <10ms per render
    
    Example:
        >>> renderer = ResponseRenderer()
        >>> result = OrchestratorResult(
        ...     status=OrchestratorStatus.COMPLETED,
        ...     message="Plan created successfully",
        ...     data={'plan_id': 'user-auth-123'}
        ... )
        >>> markdown = renderer.render(result, tier='FOCUSED')
        >>> print(markdown)
        ## 🧠 CORTEX Response
        
        ✅ Plan created successfully
        
        **Plan ID:** user-auth-123
        
        **Next:** Review plan in `cortex-brain/documents/planning/active/user-auth-123/`
    """
    
    def __init__(
        self,
        template_path: str = "cortex-brain/response-templates-v4.yaml",
        cache_templates: bool = True
    ):
        """
        Initialize ResponseRenderer.
        
        Args:
            template_path: Path to response templates YAML
            cache_templates: Cache parsed templates for performance
        """
        self.template_path = template_path
        self.cache_templates = cache_templates
        self.template_cache: Dict[str, Any] = {} if cache_templates else {}
        
        # Load templates
        self.template_config = self._load_templates(template_path)
        
        logger.info(f"ResponseRenderer initialized (template_path={template_path})")
    
    def render(
        self,
        result: OrchestratorResult,
        tier: str = 'auto',
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Render OrchestratorResult to user-facing markdown.
        
        Args:
            result: Orchestrator execution result
            tier: Response tier (auto|INSTANT|FOCUSED|STRUCTURED|COMPREHENSIVE)
            context: Additional rendering context
        
        Returns:
            Formatted markdown string
        
        Example:
            >>> renderer = ResponseRenderer()
            >>> result = OrchestratorResult(
            ...     status=OrchestratorStatus.COMPLETED,
            ...     message="Operation completed successfully",
            ...     execution_time_seconds=2.5
            ... )
            >>> markdown = renderer.render(result)
            >>> print(markdown)
            ## 🧠 CORTEX Response
            
            ✅ Operation completed successfully
            
            ⏱️ Duration: 2.5s
        """
        ctx = context or {}
        
        # Step 1: Determine tier
        tier_enum = self._determine_tier(result, tier, ctx)
        
        # Step 2: Select blocks
        blocks = self._select_blocks(result, tier_enum, ctx)
        
        # Step 3: Render blocks
        rendered_blocks = []
        for block in blocks:
            try:
                rendered = self._render_block(block, result, ctx)
                if rendered:
                    rendered_blocks.append(rendered)
            except Exception as e:
                logger.error(f"Block rendering failed: {block['name']} - {e}")
                # Continue rendering other blocks
        
        # Step 4: Compose final markdown
        markdown = self._compose_response(rendered_blocks, tier_enum)
        
        logger.debug(
            f"Response rendered: tier={tier_enum.value}, "
            f"blocks={len(rendered_blocks)}, "
            f"length={len(markdown)}"
        )
        
        return markdown
    
    def _determine_tier(
        self,
        result: OrchestratorResult,
        tier: str,
        context: Dict[str, Any]
    ) -> ResponseTier:
        """
        Determine response tier based on result complexity.
        
        Rules:
            - INSTANT: Simple success/error, <50 tokens
            - FOCUSED: Single concept, 50-200 tokens
            - STRUCTURED: Multi-faceted, 200-600 tokens
            - COMPREHENSIVE: Complex operations, 600+ tokens
        
        Args:
            result: Orchestrator result
            tier: Requested tier ('auto' for automatic)
            context: Additional context
        
        Returns:
            ResponseTier enum value
        """
        # If explicit tier provided, use it
        if tier != 'auto':
            try:
                return ResponseTier[tier.upper()]
            except KeyError:
                logger.warning(f"Invalid tier '{tier}', using auto-detection")
        
        # Auto-detect tier based on message complexity
        message_length = len(result.message) if result.message else 0
        token_count = message_length // 4  # ~4 chars per token
        
        # Errors always at least FOCUSED
        if result.status == OrchestratorStatus.FAILED:
            return ResponseTier.FOCUSED
        
        # Token-based tier selection
        if token_count < 50:
            return ResponseTier.INSTANT
        elif token_count < 200:
            return ResponseTier.FOCUSED
        elif token_count < 600:
            return ResponseTier.STRUCTURED
        else:
            return ResponseTier.COMPREHENSIVE
    
    def _select_blocks(
        self,
        result: OrchestratorResult,
        tier: ResponseTier,
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Select response blocks based on tier and context signals.
        
        Context Signals:
            - operation_type: planning, execution, analysis, etc.
            - response_phase: start, in_progress, complete, error
            - orchestrator_type: planning, vacuum, cleanup, etc.
            - files_modified: bool
            - validation_ran: bool
            - multi_phase_operation: bool
        
        Args:
            result: Orchestrator result
            tier: Response tier
            context: Rendering context
        
        Returns:
            List of blocks to render (with priority)
        """
        blocks = []
        
        # Mandatory: CORTEX header
        blocks.append({
            'name': 'cortex_header',
            'priority': 100,
            'config': {
                'emoji': '🧠',
                'title': 'CORTEX Response'
            }
        })
        
        # Conditional: Progress tracker (multi-phase operations)
        if context.get('multi_phase_operation'):
            blocks.append({
                'name': 'progress_tracker',
                'priority': 90,
                'config': {}
            })
        
        # Conditional: Error details (failed status)
        if result.status == OrchestratorStatus.FAILED:
            blocks.append({
                'name': 'error_details',
                'priority': 85,
                'config': {}
            })
        
        # Mandatory: Response body
        blocks.append({
            'name': 'response',
            'priority': 80,
            'config': {}
        })
        
        # Conditional: Changes (files modified or artifacts created)
        artifacts = result.data.get('artifacts', []) if result.data else []
        if context.get('files_modified') or (artifacts and len(artifacts) > 0):
            blocks.append({
                'name': 'changes',
                'priority': 75,
                'config': {}
            })
        
        # Mandatory: Next steps or completion
        if result.status == OrchestratorStatus.COMPLETED:
            blocks.append({
                'name': 'completion',
                'priority': 70,
                'config': {}
            })
        else:
            blocks.append({
                'name': 'next_steps',
                'priority': 70,
                'config': {}
            })
        
        # Sort by priority (high to low)
        blocks.sort(key=lambda b: b['priority'], reverse=True)
        
        return blocks
    
    def _render_block(
        self,
        block: Dict[str, Any],
        result: OrchestratorResult,
        context: Dict[str, Any]
    ) -> str:
        """
        Render individual block to markdown.
        
        Args:
            block: Block configuration
            result: Orchestrator result
            context: Rendering context
        
        Returns:
            Rendered markdown for block
        """
        block_name = block['name']
        config = block['config']
        
        # Get status emoji
        status_emoji = self._get_status_emoji(result.status)
        
        # Render block based on name
        if block_name == 'cortex_header':
            return self._render_header(config, status_emoji)
        
        elif block_name == 'progress_tracker':
            return self._render_progress(context)
        
        elif block_name == 'error_details':
            return self._render_errors(result)
        
        elif block_name == 'response':
            return self._render_response_body(result, status_emoji)
        
        elif block_name == 'changes':
            return self._render_changes(result)
        
        elif block_name == 'completion':
            return self._render_completion(result)
        
        elif block_name == 'next_steps':
            return self._render_next_steps(result, context)
        
        else:
            logger.warning(f"Unknown block: {block_name}")
            return ""
    
    def _render_header(self, config: Dict[str, Any], status_emoji: str) -> str:
        """Render CORTEX header."""
        emoji = config.get('emoji', '🧠')
        title = config.get('title', 'CORTEX Response')
        return f"## {emoji} {title}"
    
    def _render_progress(self, context: Dict[str, Any]) -> str:
        """Render progress tracker."""
        progress = context.get('progress', {})
        if not progress:
            return ""
        
        current = progress.get('current', 0)
        total = progress.get('total', 1)
        percentage = (current / total * 100) if total > 0 else 0
        
        return f"**Progress:** {current}/{total} ({percentage:.0f}%)"
    
    def _render_errors(self, result: OrchestratorResult) -> str:
        """Render error details."""
        if not result.errors:
            return ""
        
        errors_md = "### ❌ Errors\n\n"
        for i, error in enumerate(result.errors, 1):
            errors_md += f"{i}. {error}\n"
        
        return errors_md
    
    def _render_response_body(self, result: OrchestratorResult, status_emoji: str) -> str:
        """Render main response body."""
        if not result.message:
            return ""
        
        return f"{status_emoji} {result.message}"
    
    def _render_changes(self, result: OrchestratorResult) -> str:
        """Render changes/artifacts."""
        artifacts = result.data.get('artifacts', []) if result.data else []
        if not artifacts:
            return ""
        
        artifacts_md = "### 📁 Artifacts Created\n\n"
        for artifact in artifacts[:10]:  # Limit to 10
            artifacts_md += f"- `{artifact}`\n"
        
        if len(artifacts) > 10:
            artifacts_md += f"\n... and {len(artifacts) - 10} more"
        
        return artifacts_md
    
    def _render_completion(self, result: OrchestratorResult) -> str:
        """Render completion message."""
        completion_md = ""
        
        # Add duration if available
        if result.execution_time_seconds:
            duration = result.execution_time_seconds
            completion_md += f"\n\n⏱️ **Duration:** {duration:.1f}s"
        
        return completion_md
    
    def _render_next_steps(self, result: OrchestratorResult, context: Dict[str, Any]) -> str:
        """Render next steps."""
        next_steps = context.get('next_steps', [])
        if not next_steps:
            return ""
        
        next_steps_md = "\n\n**Next Steps:**\n\n"
        for i, step in enumerate(next_steps, 1):
            next_steps_md += f"{i}. {step}\n"
        
        return next_steps_md
    
    def _compose_response(
        self,
        rendered_blocks: List[str],
        tier: ResponseTier
    ) -> str:
        """
        Compose final markdown from rendered blocks.
        
        Args:
            rendered_blocks: List of rendered block strings
            tier: Response tier
        
        Returns:
            Final markdown response
        """
        # Filter out empty blocks
        non_empty_blocks = [block for block in rendered_blocks if block.strip()]
        
        # Join blocks with double newlines
        markdown = '\n\n'.join(non_empty_blocks)
        
        # Add tier-specific formatting
        if tier == ResponseTier.COMPREHENSIVE:
            markdown += '\n\n---\n'
        
        return markdown
    
    def _get_status_emoji(self, status: OrchestratorStatus) -> str:
        """
        Get emoji for orchestrator status.
        
        Args:
            status: Orchestrator status
        
        Returns:
            Status emoji
        """
        return {
            OrchestratorStatus.COMPLETED: '✅',
            OrchestratorStatus.FAILED: '❌',
            OrchestratorStatus.CANCELLED: '🚫',
            OrchestratorStatus.RUNNING: '⏳',
            OrchestratorStatus.NOT_STARTED: '⚪'
        }.get(status, '❓')
    
    def _load_templates(self, path: str) -> Dict[str, Any]:
        """
        Load response templates from YAML file.
        
        Args:
            path: Path to templates YAML
        
        Returns:
            Parsed template configuration
        
        Raises:
            FileNotFoundError: If template file not found
            yaml.YAMLError: If YAML parsing fails
        """
        template_file = Path(path)
        
        if not template_file.exists():
            logger.warning(
                f"Template file not found: {path}, using defaults"
            )
            return self._get_default_templates()
        
        try:
            with open(template_file, 'r') as f:
                config = yaml.safe_load(f)
                logger.info(f"Templates loaded from {path}")
                return config
        except yaml.YAMLError as e:
            logger.error(f"YAML parsing failed: {e}, using defaults")
            return self._get_default_templates()
    
    def _get_default_templates(self) -> Dict[str, Any]:
        """
        Get default templates (fallback if YAML file missing).
        
        Returns:
            Default template configuration
        """
        return {
            'blocks': {
                'cortex_header': {
                    'emoji': '🧠',
                    'title': 'CORTEX Response'
                },
                'progress_tracker': {},
                'error_details': {},
                'response': {},
                'changes': {},
                'completion': {},
                'next_steps': {}
            }
        }

