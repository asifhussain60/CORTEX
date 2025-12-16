"""
Phase Lifecycle Manager for CORTEX

Unified phase lifecycle management across all orchestrators.
Handles phase transitions: PENDING → IN PROGRESS → COMPLETE
Auto-completes plans when final phase is done.

Author: Asif Hussain
Version: 2.0.0 - Added automatic plan completion and folder movement
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import re
import shutil

from .unified_plan_generator import UnifiedPlanGenerator

logger = logging.getLogger(__name__)


class PhaseLifecycleManager:
    """
    Unified phase lifecycle management.
    
    Used by all orchestrators for consistent phase transitions.
    """
    
    def __init__(self, plan_generator: UnifiedPlanGenerator):
        """
        Initialize phase lifecycle manager.
        
        Args:
            plan_generator: Unified plan generator instance
        """
        self.plan_generator = plan_generator
        logger.info("✅ PhaseLifecycleManager initialized")
    
    def start_phase(
        self,
        master_plan_path: Path,
        phase_number: int
    ) -> Dict[str, Any]:
        """
        Transition phase: PENDING → IN PROGRESS
        
        Args:
            master_plan_path: Path to master plan file
            phase_number: Phase number to start
        
        Returns:
            Result dictionary with success status
        """
        try:
            # Read current master plan
            if not master_plan_path.exists():
                return {
                    "success": False,
                    "error": f"Master plan not found: {master_plan_path}"
                }
            
            with open(master_plan_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Update phase status
            started_at = datetime.now()
            updated_content = self.plan_generator.update_phase_status(
                master_plan_content=content,
                phase_number=phase_number,
                new_status="IN PROGRESS"
            )
            
            # Write back
            with open(master_plan_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            logger.info(f"🚀 Phase {phase_number} started: {master_plan_path.name}")
            
            return {
                "success": True,
                "phase_number": phase_number,
                "status": "IN PROGRESS",
                "started_at": started_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to start phase {phase_number}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def complete_phase(
        self,
        master_plan_path: Path,
        phase_number: int,
        duration: timedelta,
        tokens_saved: int = 0,
        metrics: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Transition phase: IN PROGRESS → COMPLETE
        
        Args:
            master_plan_path: Path to master plan file
            phase_number: Phase number to complete
            duration: Actual duration (timedelta)
            tokens_saved: Tokens saved in this phase
            metrics: Additional metrics (tests, coverage, etc.)
        
        Returns:
            Result dictionary with success status
        """
        try:
            # Read current master plan
            if not master_plan_path.exists():
                return {
                    "success": False,
                    "error": f"Master plan not found: {master_plan_path}"
                }
            
            with open(master_plan_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Format duration
            duration_str = self._format_duration(duration)
            
            # Update phase status
            updated_content = self.plan_generator.update_phase_status(
                master_plan_content=content,
                phase_number=phase_number,
                new_status="COMPLETE",
                actual_time=duration_str,
                tokens_saved=tokens_saved
            )
            
            # Update continuation prompt
            updated_content = self._update_continuation_prompt(updated_content)
            
            # Write back
            with open(master_plan_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            logger.info(f"✅ Phase {phase_number} completed: {duration_str}, {tokens_saved} tokens saved")
            
            # Check if this was the final phase
            is_final_phase = self._is_final_phase(updated_content, phase_number)
            
            result = {
                "success": True,
                "phase_number": phase_number,
                "status": "COMPLETE",
                "duration": duration_str,
                "tokens_saved": tokens_saved,
                "metrics": metrics or {},
                "is_final_phase": is_final_phase
            }
            
            # Auto-complete plan if final phase
            if is_final_phase:
                completion_result = self._auto_complete_plan(master_plan_path)
                result["plan_completed"] = completion_result
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to complete phase {phase_number}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_next_phase(self, master_plan_path: Path) -> Optional[int]:
        """
        Find next PENDING phase.
        
        Args:
            master_plan_path: Path to master plan file
        
        Returns:
            Next phase number or None if all complete
        """
        try:
            if not master_plan_path.exists():
                return None
            
            with open(master_plan_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find first PENDING phase in table
            pattern = r"\| (\d+) \| ([^|]+) \| .*?⏸️ PENDING"
            match = re.search(pattern, content)
            
            if match:
                return int(match.group(1))
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to find next phase: {e}")
            return None
    
    # ===== Private Helper Methods =====
    
    def _format_duration(self, duration: timedelta) -> str:
        """
        Format timedelta as readable string.
        
        Args:
            duration: Time duration
        
        Returns:
            Formatted string (e.g., "2h 15m", "45m", "3h")
        """
        total_seconds = int(duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        
        if hours > 0 and minutes > 0:
            return f"{hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h"
        elif minutes > 0:
            return f"{minutes}m"
        else:
            return "< 1m"
    
    def _update_continuation_prompt(self, content: str) -> str:
        """
        Update continuation prompt with new progress.
        
        Args:
            content: Master plan content
        
        Returns:
            Updated content
        """
        # Extract current progress from visual tracker
        progress_match = re.search(r"\*\*Overall Progress:\*\*.*?(\d+)/(\d+) Phases Complete", content)
        if not progress_match:
            return content
        
        completed = int(progress_match.group(1))
        total = int(progress_match.group(2))
        percentage = int((completed / total) * 100) if total > 0 else 0
        
        # Find next pending phase
        next_phase_match = re.search(r"\| (\d+) \| ([^|]+) \| .*?⏸️ PENDING", content)
        
        if next_phase_match:
            next_num = next_phase_match.group(1)
            next_name = next_phase_match.group(2).strip()
            new_prompt = f"Current status: {completed}/{total} phases ({percentage}%). Phase {next_num} ({next_name}) ready to start."
        else:
            new_prompt = f"Current status: {completed}/{total} phases ({percentage}%). All phases complete!"
        
        # Replace in continuation prompt section
        prompt_pattern = r"(Current status:.*?(?:ready to start|complete!)\.)"
        updated = re.sub(prompt_pattern, new_prompt, content)
        
        return updated
    
    def _is_final_phase(self, content: str, phase_number: int) -> bool:
        """
        Check if this is the final phase (no more PENDING phases).
        
        Args:
            content: Master plan content
            phase_number: Current phase number
        
        Returns:
            True if this is the final phase, False otherwise
        """
        # Look for any PENDING phases
        pending_pattern = r"\| \d+ \| [^|]+ \| .*?⏳ PENDING"
        has_pending = re.search(pending_pattern, content) is not None
        
        return not has_pending
    
    def _auto_complete_plan(self, master_plan_path: Path) -> Dict[str, Any]:
        """
        Automatically complete the plan and move to completed folder.
        
        Steps:
        1. Update plan status to COMPLETE in master plan
        2. Update completion timestamp
        3. Move plan folder from active/ to completed/
        
        Args:
            master_plan_path: Path to master plan file
        
        Returns:
            Result dictionary with success status and new path
        """
        try:
            logger.info(f"🎉 Final phase complete - auto-completing plan: {master_plan_path.name}")
            
            # Read current content
            with open(master_plan_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Update status to COMPLETE
            content = re.sub(
                r'\*\*Status:\*\* 🟡 In Progress',
                '**Status:** ✅ Complete',
                content
            )
            content = re.sub(
                r'\*\*Status:\*\* ⏳ Pending',
                '**Status:** ✅ Complete',
                content
            )
            
            # Update completed timestamp
            completed_timestamp = datetime.now().strftime("%Y-%m-%d %I:%M %p")
            content = re.sub(
                r'\*\*Completed:\*\* TBD',
                f'**Completed:** {completed_timestamp}',
                content
            )
            
            # Update continuation prompt to show completion
            content = re.sub(
                r'## 🔄 Continuation Prompt.*?---',
                '## 🔄 Continuation Prompt\n\n✅ **PLAN COMPLETE** - All phases finished successfully.\n\n---',
                content,
                flags=re.DOTALL
            )
            
            # Write back updated content
            with open(master_plan_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Determine plan folder structure
            plan_folder = master_plan_path.parent
            
            # Check if this is a folder-based plan (has parent folder with plan name)
            if plan_folder.name.startswith(('PLAN-', 'TEMP-PLAN-', 'template-naming-enhancement')):
                # Move entire folder from active/ to completed/
                active_base = plan_folder.parent
                completed_base = active_base.parent / "completed"
                completed_base.mkdir(parents=True, exist_ok=True)
                
                new_location = completed_base / plan_folder.name
                
                # Move folder
                shutil.move(str(plan_folder), str(new_location))
                
                logger.info(f"📁 Moved plan folder: {plan_folder} → {new_location}")
                
                return {
                    "success": True,
                    "moved": True,
                    "old_path": str(master_plan_path),
                    "new_path": str(new_location / master_plan_path.name),
                    "folder_moved": True
                }
            else:
                # Legacy flat structure - just update the file in place
                logger.info(f"✅ Plan marked complete (flat structure, no folder move)")
                
                return {
                    "success": True,
                    "moved": False,
                    "path": str(master_plan_path),
                    "folder_moved": False
                }
            
        except Exception as e:
            logger.error(f"Failed to auto-complete plan: {e}")
            return {
                "success": False,
                "error": str(e)
            }

