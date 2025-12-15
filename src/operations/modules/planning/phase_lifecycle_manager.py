"""
Phase Lifecycle Manager for CORTEX

Unified phase lifecycle management across all orchestrators.
Handles phase transitions: PENDING → IN PROGRESS → COMPLETE

Author: Asif Hussain
Version: 1.0.0
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import re

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
            
            return {
                "success": True,
                "phase_number": phase_number,
                "status": "COMPLETE",
                "duration": duration_str,
                "tokens_saved": tokens_saved,
                "metrics": metrics or {}
            }
            
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
