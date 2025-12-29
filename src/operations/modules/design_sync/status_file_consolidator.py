"""
Status File Consolidator

Consolidates multiple status files into one authoritative document.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0
"""

import logging
import re
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any, Callable
from src.operations.modules.design_sync.design_sync_models import (
    ImplementationState,
    DesignState,
    GapAnalysis,
    SyncMetrics
)

logger = logging.getLogger(__name__)


class StatusFileConsolidator:
    """
    Consolidates multiple status files into ONE authoritative document.
    
    Responsibilities:
    - Select primary status file (CORTEX2-STATUS.MD preferred)
    - Update counts from implementation state
    - Insert/update recent updates from git history
    - Regenerate visual progress bars
    - Add sync timestamp with contextual suffix
    """
    
    def __init__(
        self,
        generate_recent_updates_callback: Callable[[Path, int], List[str]],
        calculate_phase_progress_callback: Callable[[str], tuple[Dict[str, int], List[str]]],
        generate_progress_bar_callback: Callable[[int], str],
        add_sync_context_callback: Callable[[List[str], ImplementationState, Dict[str, Any]], str]
    ):
        """
        Initialize StatusFileConsolidator.
        
        Args:
            generate_recent_updates_callback: Function to generate recent updates from git
            calculate_phase_progress_callback: Function to calculate phase progress percentages
            generate_progress_bar_callback: Function to generate ASCII progress bars
            add_sync_context_callback: Function to add contextual suffix to sync timestamp
        """
        self.generate_recent_updates = generate_recent_updates_callback
        self.calculate_phase_progress = calculate_phase_progress_callback
        self.generate_progress_bar = generate_progress_bar_callback
        self.add_sync_context = add_sync_context_callback
    
    def consolidate(
        self,
        status_files: List[Path],
        impl_state: ImplementationState,
        design_state: DesignState,
        gaps: GapAnalysis,
        project_root: Path,
        metrics: SyncMetrics
    ) -> Optional[Path]:
        """
        Consolidate multiple status files into ONE authoritative document.
        
        Returns:
            Path to consolidated status file
        """
        # Use CORTEX2-STATUS.MD as primary (it has the visual bars)
        primary = None
        for status_file in status_files:
            if 'CORTEX2-STATUS' in status_file.name:
                primary = status_file
                break
        
        if not primary and status_files:
            primary = status_files[0]
        
        if not primary:
            return None
        
        # Read current content with proper encoding
        try:
            content = primary.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            logger.error(f"Failed to read {primary.name}: {e}")
            return None
        
        # Update with accurate counts
        updates = []
        
        # Update total modules
        content = re.sub(
            r'Total Modules:\*\* \d+',
            f'Total Modules:** {impl_state.total_modules}',
            content
        )
        updates.append(f"Updated total modules: {impl_state.total_modules}")
        
        # Update implemented modules
        content = re.sub(
            r'Implemented:\*\* \d+ modules',
            f'Implemented:** {impl_state.implemented_modules} modules',
            content
        )
        updates.append(f"Updated implemented modules: {impl_state.implemented_modules}")
        
        # Update test count
        total_tests = sum(impl_state.tests.values())
        content = re.sub(
            r'Tests:\*\* \d+ tests',
            f'Tests:** {total_tests} tests',
            content
        )
        updates.append(f"Updated test count: {total_tests}")
        
        # Update plugins count
        content = re.sub(
            r'Plugins:\*\* \d+ operational',
            f'Plugins:** {len(impl_state.plugins)} operational',
            content
        )
        updates.append(f"Updated plugins: {len(impl_state.plugins)}")
        
        # Generate recent updates from git history
        recent_updates = self.generate_recent_updates(project_root, 1)  # lookback_days=1
        
        # Insert "Recent Updates" section if not present
        if recent_updates and '**Recent Updates' not in content:
            # Find where to insert (after first header section)
            insert_pattern = r'(\*\*Last Synchronized:.*?\*\n)'
            recent_section = f"\n**Recent Updates ({datetime.now().strftime('%Y-%m-%d %H:%M')}):**\n"
            for update in recent_updates[:10]:  # Limit to 10 most recent
                recent_section += f"- {update}\n"
            recent_section += "\n"
            
            content = re.sub(
                insert_pattern,
                r'\1' + recent_section,
                content,
                count=1
            )
            updates.append(f"Added recent updates section ({len(recent_updates)} updates)")
        elif recent_updates and '**Recent Updates' in content:
            # Update existing Recent Updates section
            recent_section = f"**Recent Updates ({datetime.now().strftime('%Y-%m-%d %H:%M')}):**\n"
            for update in recent_updates[:10]:
                recent_section += f"- {update}\n"
            
            # Replace entire Recent Updates block
            pattern = r'\*\*Recent Updates.*?\n(?:- .*?\n)*'
            content = re.sub(
                pattern,
                recent_section,
                content,
                count=1
            )
            updates.append(f"Updated recent updates section ({len(recent_updates)} updates)")
        
        # Update visual progress bars (with user-specified execution order)
        phase_progress, execution_order = self.calculate_phase_progress(content)
        progress_section_lines = []
        progress_section_lines.append("```")
        
        # Display phases in execution order (not numerical order)
        for phase_name in execution_order:
            percentage = phase_progress[phase_name]
            bar = self.generate_progress_bar(percentage)
            # Pad phase name to align bars
            padded_name = phase_name.ljust(40)
            progress_section_lines.append(f"{padded_name}{bar} {percentage:3d}%")
        progress_section_lines.append("```")
        
        new_progress_section = "\n".join(progress_section_lines)
        
        # Replace the entire progress bars code block
        # Match from opening ``` to closing ``` after the last phase line
        progress_pattern = r'```\nPhase 0.*?```'
        if re.search(progress_pattern, content, re.DOTALL):
            content = re.sub(
                progress_pattern,
                new_progress_section,
                content,
                flags=re.DOTALL,
                count=1
            )
            updates.append(f"Updated visual progress bars for {len(phase_progress)} phases")
        
        # Add sync timestamp with contextual suffix
        transformations_context = {
            'md_to_yaml_converted': metrics.md_to_yaml_converted,
            'status_files_consolidated': metrics.status_files_consolidated
        }
        context_suffix = self.add_sync_context(recent_updates, impl_state, transformations_context)
        sync_note = f"*Last Synchronized: {datetime.now().strftime('%Y-%m-%d %H:%M')} {context_suffix}*\n"
        
        if '*Last Synchronized:' not in content:
            content += f"\n\n{sync_note}"
        else:
            # ✅ FIXED: Only match timestamp line, not surrounding content
            # Bug was: r'\*Last Synchronized:.*?\*' matched too much (greedy through next asterisk)
            # Fix: Only match to newline, use count=1 to avoid multiple replacements
            content = re.sub(
                r'\*Last Synchronized:.*?\n',
                sync_note,
                content,
                count=1
            )
        updates.append(f"Added sync timestamp with context: {context_suffix}")
        
        # Write back with proper encoding
        try:
            primary.write_text(content, encoding='utf-8')
        except Exception as e:
            logger.error(f"Failed to write {primary.name}: {e}")
            return None
        
        metrics.improvements['status_consolidation'] = updates
        return primary
