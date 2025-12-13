"""
Git Checkpoint Utility

High-level wrapper for git checkpoint operations.
Provides simplified API for Planning Orchestrator integration.

Implements standardized commit message format per Orchestrator Enhancement Plan:
    feat(phase-N): [Phase Name] - [Key Deliverables]
    
    Phase: N/M
    Duration: X hours
    Test Coverage: XX%
    Files Changed: N files
    Key Deliverables:
    - Deliverable 1
    - Deliverable 2
    
    Compliance:
    - DoR: ✅ All criteria met
    - DoD: ✅ All criteria met
    - Tests: ✅ XX/XX passing

Author: Asif Hussain
Created: December 13, 2025
Feature: Orchestrator Enhancement Plan - Feature 2
"""

import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class GitCheckpointUtility:
    """
    Simplified git checkpoint utility for Planning Orchestrator.
    
    Provides easy-to-use methods for creating checkpoints at phase boundaries
    with standardized commit messages and automatic tagging.
    """
    
    def __init__(self, project_root: str):
        """
        Initialize git checkpoint utility.
        
        Args:
            project_root: Root directory of git repository
        """
        self.project_root = Path(project_root)
        
    def create_phase_checkpoint(
        self,
        phase_number: int,
        total_phases: int,
        phase_name: str,
        duration_hours: float,
        test_coverage: float,
        files_changed: int,
        deliverables: List[str],
        dor_met: bool = True,
        dod_met: bool = True,
        tests_passed: int = 0,
        tests_total: int = 0
    ) -> Dict[str, Any]:
        """
        Create a checkpoint for a completed phase with standardized format.
        
        Args:
            phase_number: Current phase number
            total_phases: Total number of phases
            phase_name: Name of the phase
            duration_hours: Time taken for phase
            test_coverage: Test coverage percentage (0-100)
            files_changed: Number of files modified
            deliverables: List of key deliverables
            dor_met: Definition of Ready satisfied
            dod_met: Definition of Done satisfied
            tests_passed: Number of tests passing
            tests_total: Total number of tests
            
        Returns:
            Dict with success status, checkpoint_id, commit_sha, tag_name
        """
        logger.info(f"🎭 Phase transition: Phase {phase_number} → Phase {phase_number + 1}")
        
        try:
            # Format deliverables list
            deliverables_text = "\n".join([f"- {d}" for d in deliverables])
            
            # Format commit message per spec
            commit_message = (
                f"feat(phase-{phase_number}): {phase_name} - Complete\n\n"
                f"Phase: {phase_number}/{total_phases}\n"
                f"Duration: {duration_hours:.1f} hours\n"
                f"Test Coverage: {test_coverage:.0f}%\n"
                f"Files Changed: {files_changed} files\n"
                f"Key Deliverables:\n{deliverables_text}\n\n"
                f"Compliance:\n"
                f"- DoR: {'✅' if dor_met else '❌'} {'All criteria met' if dor_met else 'Not satisfied'}\n"
                f"- DoD: {'✅' if dod_met else '❌'} {'All criteria met' if dod_met else 'Not satisfied'}\n"
                f"- Tests: {'✅' if tests_passed == tests_total else '⚠️'} {tests_passed}/{tests_total} passing"
            )
            
            # Stage all changes
            subprocess.run(
                ["git", "add", "-A"],
                cwd=self.project_root,
                check=True,
                capture_output=True
            )
            
            # Check if there are changes to commit
            status_result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if not status_result.stdout.strip():
                logger.warning("No changes to commit for phase checkpoint")
                return {
                    "success": True,
                    "message": "No changes to commit",
                    "checkpoint_id": None,
                    "commit_sha": None,
                    "tag_name": None
                }
            
            # Create commit
            subprocess.run(
                ["git", "commit", "-m", commit_message],
                cwd=self.project_root,
                check=True,
                capture_output=True,
                text=True
            )
            
            # Get commit SHA
            sha_result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.project_root,
                check=True,
                capture_output=True,
                text=True
            )
            commit_sha = sha_result.stdout.strip()
            
            # Create tag with format: phase-N-complete-YYYYMMDD-HHMMSS
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            tag_name = f"phase-{phase_number}-complete-{timestamp}"
            
            subprocess.run(
                ["git", "tag", "-a", tag_name, "-m", f"Phase {phase_number} complete: {phase_name}"],
                cwd=self.project_root,
                check=True,
                capture_output=True
            )
            
            logger.info(f"✅ Phase {phase_number} checkpoint created: {tag_name}")
            
            return {
                "success": True,
                "checkpoint_id": tag_name,
                "commit_sha": commit_sha,
                "tag_name": tag_name,
                "phase_number": phase_number,
                "phase_name": phase_name
            }
        
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode() if e.stderr else str(e)
            logger.error(f"Failed to create phase checkpoint: {error_msg}")
            return {
                "success": False,
                "error": error_msg
            }
    
    def rollback_to_phase(self, phase_number: int) -> Dict[str, Any]:
        """
        Rollback to a specific phase tag.
        
        Args:
            phase_number: Phase number to rollback to
            
        Returns:
            Dict with success status
        """
        try:
            # Find the most recent tag for the phase
            tags_result = subprocess.run(
                ["git", "tag", "-l", f"phase-{phase_number}-complete-*"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            tags = tags_result.stdout.strip().split("\n")
            if not tags or tags == ['']:
                return {
                    "success": False,
                    "error": f"No checkpoint found for phase {phase_number}"
                }
            
            # Use the most recent tag (last in sorted order)
            latest_tag = sorted(tags)[-1]
            
            # Checkout the tag
            subprocess.run(
                ["git", "checkout", latest_tag],
                cwd=self.project_root,
                check=True,
                capture_output=True
            )
            
            return {
                "success": True,
                "tag_name": latest_tag,
                "phase_number": phase_number
            }
        
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode() if e.stderr else str(e)
            return {
                "success": False,
                "error": error_msg
            }
    
    def list_phase_checkpoints(self) -> List[Dict[str, Any]]:
        """
        List all phase checkpoints.
        
        Returns:
            List of checkpoint dicts with tag_name, phase_number, timestamp
        """
        try:
            tags_result = subprocess.run(
                ["git", "tag", "-l", "phase-*-complete-*"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            tags = tags_result.stdout.strip().split("\n")
            if not tags or tags == ['']:
                return []
            
            checkpoints = []
            for tag in sorted(tags):
                # Parse tag: phase-N-complete-YYYYMMDD-HHMMSS
                parts = tag.split("-")
                if len(parts) >= 4:
                    phase_num = parts[1]
                    timestamp = "-".join(parts[3:])
                    
                    checkpoints.append({
                        "tag_name": tag,
                        "phase_number": int(phase_num),
                        "timestamp": timestamp
                    })
            
            return checkpoints
        
        except Exception as e:
            logger.error(f"Failed to list checkpoints: {e}")
            return []
