"""
BaseOrchestrator v4.1 - Config-Driven Autonomous Execution.

Enhanced base class for CORTEX v5.0 with:
- Pure config-driven execution (no natural language interpretation)
- Jinja2 template system integration
- PlanningStateDB integration for persistent state
- Progress tracking with visual indicators
- Session management and continuation prompts
- Checkpoint/rollback support
- Artifact registry

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import logging
import yaml
import json
import time
import hashlib
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field, asdict
from abc import ABC, abstractmethod
from enum import Enum
from jinja2 import Environment, FileSystemLoader, select_autoescape

# Import database layer
from src.database.planning_state_db import PlanningStateDB

# Import existing base
from src.orchestrators.base.base_orchestrator import (
    OrchestratorStatus,
    ValidationResult,
    OrchestratorResult,
    ErrorResult
)


class PhaseStatus(str, Enum):
    """Phase execution status."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class PhaseResult:
    """Result of phase execution."""
    phase_id: str
    phase_number: int
    name: str
    status: PhaseStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: float = 0.0
    artifacts: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        result = asdict(self)
        # Convert datetime to ISO format
        if self.started_at:
            result['started_at'] = self.started_at.isoformat()
        if self.completed_at:
            result['completed_at'] = self.completed_at.isoformat()
        result['status'] = self.status.value
        return result


@dataclass
class ArtifactMetadata:
    """Metadata for generated artifacts."""
    artifact_id: str
    path: str
    type: str  # e.g., 'plan', 'report', 'config', 'code'
    created_at: datetime
    checksum: str
    size_bytes: int
    phase_id: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            'artifact_id': self.artifact_id,
            'path': self.path,
            'type': self.type,
            'created_at': self.created_at.isoformat(),
            'checksum': self.checksum,
            'size_bytes': self.size_bytes,
            'phase_id': self.phase_id
        }


class BaseOrchestratorV4_1(ABC):
    """
    Enhanced base orchestrator for CORTEX v5.0.
    
    Features:
    - Config-driven execution (YAML manifest)
    - Template rendering (Jinja2)
    - Database state persistence (SQLite)
    - Progress tracking with visual bars
    - Session continuation prompts
    - Checkpoint/rollback support
    - Artifact registry
    
    Lifecycle:
        1. __init__() - Load config, connect to database
        2. load_config() - Parse and validate manifest
        3. execute() - Main autonomous execution (abstract)
        4. execute_phase() - Execute individual phase
        5. complete_phase() - Mark phase complete, update tracking
    
    Subclass Requirements:
        - Implement execute() method
        - Define config file path
        - Implement phase-specific logic
    """
    
    def __init__(
        self,
        config_path: str,
        state_db: PlanningStateDB,
        plan_id: Optional[str] = None,
        template_dir: Optional[str] = None
    ):
        """
        Initialize orchestrator with config and database.
        
        Args:
            config_path: Path to YAML configuration manifest
            state_db: PlanningStateDB instance for state persistence
            plan_id: Optional existing plan ID to resume
            template_dir: Optional template directory override
        """
        self.config_path = Path(config_path)
        self.state_db = state_db
        self.plan_id = plan_id
        
        # Setup logging
        self.logger = logging.getLogger(
            f"cortex.orchestrators.{self.__class__.__name__}"
        )
        
        # Load configuration
        self.config = self.load_config()
        self.name = self.config.get('orchestrator', {}).get('name', 'unknown')
        self.version = self.config.get('orchestrator', {}).get('version', '5.0')
        
        # Setup Jinja2 template environment
        template_path = Path(template_dir or self.config.get(
            'templates', {}).get('base_path', 'cortex-brain/templates')
        )
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(template_path)),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # State tracking
        self.current_phase_id: Optional[str] = None
        self.artifacts: List[ArtifactMetadata] = []
        
        self.logger.info(
            f"Initialized {self.name} v{self.version} "
            f"(config={config_path}, plan_id={plan_id})"
        )
    
    def load_config(self) -> dict:
        """
        Load and validate YAML configuration manifest.
        
        Returns:
            Parsed configuration dictionary
        
        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If config is invalid YAML
            ValueError: If config fails validation
        """
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config not found: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Validate required fields
        self._validate_config(config)
        
        self.logger.info(f"Loaded config from {self.config_path}")
        return config
    
    def _validate_config(self, config: dict) -> None:
        """
        Validate configuration structure.
        
        Args:
            config: Configuration dictionary to validate
        
        Raises:
            ValueError: If validation fails
        """
        required_sections = ['schema_version', 'orchestrator']
        for section in required_sections:
            if section not in config:
                raise ValueError(f"Missing required config section: {section}")
        
        # Validate orchestrator metadata
        orch_config = config['orchestrator']
        required_fields = ['name', 'version', 'type']
        for field in required_fields:
            if field not in orch_config:
                raise ValueError(
                    f"Missing required orchestrator field: {field}"
                )
        
        # Validate type
        valid_types = ['autonomous', 'guided']
        if orch_config['type'] not in valid_types:
            raise ValueError(
                f"Invalid orchestrator type: {orch_config['type']}. "
                f"Must be one of: {valid_types}"
            )
    
    @abstractmethod
    def execute(self, user_request: str, **kwargs) -> OrchestratorResult:
        """
        Execute orchestrator logic autonomously.
        
        This method MUST be implemented by subclasses to define
        orchestrator-specific execution logic.
        
        Args:
            user_request: User's natural language request
            **kwargs: Additional execution parameters
        
        Returns:
            OrchestratorResult with execution status and artifacts
        """
        pass
    
    def execute_phase(
        self,
        phase_number: int,
        phase_config: dict,
        **kwargs
    ) -> PhaseResult:
        """
        Execute a single phase of orchestrator workflow.
        
        Args:
            phase_number: Sequential phase number (0-indexed)
            phase_config: Phase configuration from manifest
            **kwargs: Additional phase parameters
        
        Returns:
            PhaseResult with phase execution details
        """
        phase_name = phase_config.get('name', f'Phase {phase_number}')
        
        self.logger.info(f"Starting Phase {phase_number}: {phase_name}")
        
        # Create phase in database
        phase_id = self.state_db.start_phase(
            plan_id=self.plan_id,
            phase_number=phase_number,
            config=phase_config
        )
        self.current_phase_id = phase_id
        
        started_at = datetime.now()
        phase_result = PhaseResult(
            phase_id=phase_id,
            phase_number=phase_number,
            name=phase_name,
            status=PhaseStatus.IN_PROGRESS,
            started_at=started_at
        )
        
        try:
            # Execute phase-specific logic
            # Subclasses should override _execute_phase_logic()
            artifacts = self._execute_phase_logic(
                phase_number,
                phase_config,
                **kwargs
            )
            
            # Mark phase complete
            completed_at = datetime.now()
            phase_result.status = PhaseStatus.COMPLETED
            phase_result.completed_at = completed_at
            phase_result.duration_seconds = (
                completed_at - started_at
            ).total_seconds()
            phase_result.artifacts = artifacts
            
            # Update database
            self.state_db.complete_phase(phase_id)
            
            # Update continuation prompt
            self.update_continuation_prompt(phase_id)
            
            self.logger.info(
                f"Completed Phase {phase_number}: {phase_name} "
                f"({phase_result.duration_seconds:.1f}s)"
            )
            
        except Exception as e:
            # Mark phase failed
            phase_result.status = PhaseStatus.FAILED
            phase_result.errors.append(str(e))
            phase_result.completed_at = datetime.now()
            phase_result.duration_seconds = (
                phase_result.completed_at - started_at
            ).total_seconds()
            
            # Update database
            self.state_db.fail_phase(phase_id, str(e))
            
            self.logger.error(
                f"Failed Phase {phase_number}: {phase_name} - {e}",
                exc_info=True
            )
            raise
        
        finally:
            self.current_phase_id = None
        
        return phase_result
    
    def _execute_phase_logic(
        self,
        phase_number: int,
        phase_config: dict,
        **kwargs
    ) -> List[str]:
        """
        Execute phase-specific logic. Override in subclasses.
        
        Args:
            phase_number: Sequential phase number
            phase_config: Phase configuration
            **kwargs: Additional parameters
        
        Returns:
            List of artifact paths created
        """
        # Default implementation does nothing
        return []
    
    def render_template(
        self,
        template_name: str,
        context: dict,
        **kwargs
    ) -> str:
        """
        Render Jinja2 template with context data.
        
        Args:
            template_name: Template file name (relative to template dir)
            context: Data dictionary for template rendering
            **kwargs: Additional Jinja2 render parameters
        
        Returns:
            Rendered template string
        
        Raises:
            jinja2.TemplateNotFound: If template doesn't exist
            jinja2.TemplateError: If rendering fails
        """
        template = self.jinja_env.get_template(template_name)
        rendered = template.render(**context, **kwargs)
        
        self.logger.debug(f"Rendered template: {template_name}")
        return rendered
    
    def create_artifact(
        self,
        path: str,
        content: str,
        artifact_type: str,
        phase_id: Optional[str] = None
    ) -> str:
        """
        Create artifact file and register in database.
        
        Args:
            path: File path (relative or absolute)
            content: File content
            artifact_type: Type classification (e.g., 'plan', 'report')
            phase_id: Optional phase ID for association
        
        Returns:
            Artifact ID (UUID)
        """
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write file
        file_path.write_text(content, encoding='utf-8')
        
        # Calculate checksum
        checksum = hashlib.sha256(content.encode('utf-8')).hexdigest()
        
        # Register in database
        artifact_id = self.state_db.register_artifact(
            plan_id=self.plan_id,
            path=str(file_path),
            artifact_type=artifact_type
        )
        
        # Track metadata
        metadata = ArtifactMetadata(
            artifact_id=artifact_id,
            path=str(file_path),
            type=artifact_type,
            created_at=datetime.now(),
            checksum=checksum,
            size_bytes=len(content.encode('utf-8')),
            phase_id=phase_id or self.current_phase_id
        )
        self.artifacts.append(metadata)
        
        self.logger.info(
            f"Created artifact: {file_path} "
            f"(type={artifact_type}, id={artifact_id})"
        )
        
        return artifact_id
    
    def create_checkpoint(self, phase_id: str, metadata: dict = None) -> str:
        """
        Create state snapshot for rollback support.
        
        Args:
            phase_id: Phase ID to checkpoint
            metadata: Optional additional metadata
        
        Returns:
            Snapshot ID
        """
        snapshot_data = {
            'phase_id': phase_id,
            'artifacts': [a.to_dict() for a in self.artifacts],
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        
        snapshot_id = self.state_db.create_snapshot(
            plan_id=self.plan_id,
            phase_id=phase_id,
            data=snapshot_data
        )
        
        self.logger.info(f"Created checkpoint: {snapshot_id}")
        return snapshot_id
    
    def rollback_to_checkpoint(self, snapshot_id: str) -> bool:
        """
        Rollback to previous checkpoint state.
        
        Args:
            snapshot_id: Snapshot ID to restore
        
        Returns:
            True if rollback successful
        """
        try:
            snapshot_data = self.state_db.resume_from_snapshot(snapshot_id)
            
            # Restore state
            self.artifacts = [
                ArtifactMetadata(**a) for a in snapshot_data.get('artifacts', [])
            ]
            
            self.logger.info(f"Rolled back to checkpoint: {snapshot_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Rollback failed: {e}", exc_info=True)
            return False
    
    def update_continuation_prompt(self, phase_id: str) -> None:
        """
        Update CONTINUATION-PROMPT.md after phase completion.
        
        This provides session handoff capability for token limit management.
        
        Args:
            phase_id: Completed phase ID
        """
        try:
            # Get current plan status
            plan_state = self.state_db.get_plan_status(self.plan_id)
            
            # Prepare context
            context = {
                'plan_name': plan_state.get('feature_name', 'unknown'),
                'plan_id': self.plan_id,
                'timestamp': datetime.now().isoformat(),
                'completed_phases': plan_state.get('completed_phases', 0),
                'total_phases': plan_state.get('total_phases', 0),
                'progress_percentage': plan_state.get('progress_percent', 0),
                'current_phase': plan_state.get('current_phase'),
                'next_phase': plan_state.get('next_phase'),
                'status': plan_state.get('status', 'unknown'),
                'last_checkpoint': self._get_last_checkpoint_commit()
            }
            
            # Render prompt template
            prompt_content = self.render_template(
                'continuation-prompt.jinja2',
                context
            )
            
            # Write to tracking folder
            plan_dir = Path(f"cortex-brain/documents/planning/active/{self.plan_id}")
            prompt_path = plan_dir / "tracking" / "CONTINUATION-PROMPT.md"
            prompt_path.parent.mkdir(parents=True, exist_ok=True)
            prompt_path.write_text(prompt_content, encoding='utf-8')
            
            self.logger.info(f"Updated continuation prompt: {prompt_path}")
            
        except Exception as e:
            # Non-fatal error - log and continue
            self.logger.warning(
                f"Failed to update continuation prompt: {e}"
            )
    
    def _get_last_checkpoint_commit(self) -> Optional[str]:
        """Get last git checkpoint commit hash."""
        try:
            import subprocess
            result = subprocess.run(
                ['git', 'rev-parse', '--short', 'HEAD'],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except Exception:
            return None
    
    def get_progress_status(self) -> dict:
        """
        Get current execution progress.
        
        Returns:
            Dictionary with progress metrics
        """
        plan_state = self.state_db.get_plan_status(self.plan_id)
        
        return {
            'plan_id': self.plan_id,
            'orchestrator': self.name,
            'version': self.version,
            'status': plan_state.get('status'),
            'progress_percent': plan_state.get('progress_percent', 0),
            'completed_phases': plan_state.get('completed_phases', 0),
            'total_phases': plan_state.get('total_phases', 0),
            'artifacts_created': len(self.artifacts),
            'current_phase': plan_state.get('current_phase')
        }
    
    def generate_progress_bar(
        self,
        current: int,
        total: int,
        width: int = 20,
        fill: str = '█',
        empty: str = '░'
    ) -> str:
        """
        Generate ASCII progress bar.
        
        Args:
            current: Current progress value
            total: Total value (100%)
            width: Bar width in characters
            fill: Character for filled portion
            empty: Character for empty portion
        
        Returns:
            Progress bar string (e.g., "████████░░")
        """
        if total == 0:
            return empty * width
        
        percent = min(current / total, 1.0)
        filled = int(width * percent)
        bar = fill * filled + empty * (width - filled)
        
        return bar
