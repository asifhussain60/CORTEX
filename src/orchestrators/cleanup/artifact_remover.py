"""
Artifact Remover - Group 3 cleanup (build artifacts and generated files).

Handles:
- Backup archives (.backup-archive/)
- Story documentation backups (keep 5 most recent)
- Phase completion reports (keep 3 most recent)
- Workflow checkpoints (keep 5 most recent)
- Legacy agent backups
- Documentation backups
- Root clutter (misplaced files)
- Copilot chat transcripts
- Temporary historical documentation
- Root phase documentation (misplaced)
- Root validation scripts (temporary)
- Root backup files (.backup.*)
- Root test outputs
- Redundant alignment reports
- Generated doc patterns

Priority: MEDIUM (generated files, but may contain WIP)
Expected: ~60s execution, 2.5GB+ freed

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import logging
from pathlib import Path
from typing import Dict, Any

from src.orchestrators.cleanup.cleanup_engine import CleanupEngine


logger = logging.getLogger(__name__)


class ArtifactRemover:
    """
    Artifact removal (Group 3) - Backups, reports, build artifacts.
    
    Categories (15 total):
    - backup_archive: Nested backup directories
    - story_backups: Story documentation backups
    - phase_reports: Phase completion reports
    - workflow_checkpoints: Workflow state snapshots
    - legacy_agent_backups: Old agent backups
    - docs_awakening_backups: Documentation backups
    - root_clutter: Root-level generated files
    - copilot_chats_clutter: Copilot chat transcripts
    - temp_historical_docs: Temporary historical documentation
    - root_phase_documentation: Misplaced phase docs
    - root_validation_scripts: Temporary validation scripts
    - root_backup_files: Root-level backup files
    - root_test_outputs: Test output files in root
    - redundant_alignment_reports: Duplicate alignment reports
    - doc_pattern_cleanup: Generated doc patterns
    """
    
    CATEGORIES = [
        "backup_archive",
        "story_backups",
        "phase_reports",
        "workflow_checkpoints",
        "legacy_agent_backups",
        "docs_awakening_backups",
        "root_clutter",
        "copilot_chats_clutter",
        "temp_historical_docs",
        "root_phase_documentation",
        "root_validation_scripts",
        "root_backup_files",
        "root_test_outputs",
        "redundant_alignment_reports",
        "doc_pattern_cleanup"
    ]
    
    def __init__(
        self,
        workspace_root: Path,
        rules_path: Path,
        config: Dict[str, Any]
    ):
        """
        Initialize artifact remover.
        
        Args:
            workspace_root: Workspace root directory
            rules_path: Path to cleanup-rules.yaml
            config: Orchestrator configuration
        """
        self.workspace_root = workspace_root
        self.rules_path = rules_path
        self.config = config
        
        # Get retention days from config
        self.retention_days = config.get('modes', {}).get('artifacts', {}).get(
            'retention_days', 30
        )
        
        # Initialize cleanup engine
        self.cleanup_engine = CleanupEngine(workspace_root, rules_path)
        
        logger.info(f"ArtifactRemover initialized (retention: {self.retention_days} days)")
    
    def execute(self) -> Dict[str, Any]:
        """
        Execute artifact removal.
        
        Returns:
            Cleanup result dictionary
        """
        logger.info("Starting artifact removal (Group 3)")
        
        # Process artifact categories
        result = self.cleanup_engine.process_categories(self.CATEGORIES)
        
        logger.info(
            f"Artifact removal complete: {result['statistics']['files_deleted']} files, "
            f"{result['statistics']['space_freed_mb']:.2f} MB freed"
        )
        
        return result
