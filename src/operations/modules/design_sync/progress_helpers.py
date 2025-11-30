"""
Progress Helpers

Helper functions for calculating and displaying phase progress.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0
"""

import re
from typing import Dict, List, Any
from src.operations.modules.design_sync.design_sync_models import ImplementationState


class PhaseProgressCalculator:
    """Calculates phase completion percentages from status document content."""
    
    def calculate(self, content: str) -> tuple[Dict[str, int], List[str]]:
        """
        Calculate phase completion percentages AND execution order by parsing Current Focus.
        
        Returns:
            Tuple of (phase_progress_dict, execution_order_list)
            - phase_progress_dict: Maps phase names to completion percentages (0-100)
            - execution_order_list: List of phase names in user-specified execution order
        """
        # Default percentages (fallback if parsing fails)
        phase_progress = {
            'Phase 0 - Quick Wins': 100,
            'Phase 1 - Core Modularization': 100,
            'Phase 2 - Ambient + Workflow': 100,
            'Phase 3 - Modular Entry Validation': 100,
            'Phase 4 - Advanced CLI & Integration': 100,
            'Phase 5 - Risk Mitigation & Testing': 85,
            'Phase 6 - Performance Optimization': 100,
            'Phase 7 - Documentation & Polish': 70,
            'Phase 8 - Migration & Deployment': 25,
            'Phase 9 - Advanced Capabilities': 0,
            'Phase 10 - Production Hardening': 0,
            'Phase 11 - Context Helper Plugin': 0,
        }
        
        # Track execution order (phases mentioned in Current Focus)
        execution_order = []
        
        # Try to extract percentages AND order from Current Focus section
        focus_match = re.search(r'## 🎯 Current Focus(.*?)(?=##|$)', content, re.DOTALL)
        if focus_match:
            focus_section = focus_match.group(1)
            
            # Look for "\*\*Phase X (YY% complete" patterns (must start a line with **)
            # This prevents matching "Phase 2 Reality Check:" style headers
            for match in re.finditer(r'\*\*Phase (\d+) \((\d+)%\s+complete', focus_section):
                phase_num = int(match.group(1))
                percentage = int(match.group(2))
                
                # Map phase number to full phase name
                for phase_name in phase_progress.keys():
                    if phase_name.startswith(f'Phase {phase_num} -'):
                        phase_progress[phase_name] = percentage
                        # Only add if not already in execution order (prevent duplicates)
                        if phase_name not in execution_order:
                            execution_order.append(phase_name)
                        break
        
        # If no execution order found, fall back to numerical order
        if not execution_order:
            execution_order = list(phase_progress.keys())
        else:
            # Add remaining phases (not in Current Focus) at the end in numerical order
            for phase_name in phase_progress.keys():
                if phase_name not in execution_order:
                    execution_order.append(phase_name)
        
        return phase_progress, execution_order


class ProgressBarGenerator:
    """Generates visual ASCII progress bars."""
    
    def generate(self, percentage: int, width: int = 32) -> str:
        """
        Generate visual progress bar with █ (complete) and ░ (remaining).
        
        Args:
            percentage: Completion percentage (0-100)
            width: Total width of progress bar in characters
            
        Returns:
            Progress bar string like "[████████████████████░░░░░░░░]"
        """
        filled = int(width * percentage / 100)
        remaining = width - filled
        return f"[{'█' * filled}{'░' * remaining}]"


class SyncContextGenerator:
    """Generates contextual suffix for sync timestamp."""
    
    def generate(
        self,
        updates: List[str],
        impl_state: ImplementationState,
        transformations: Dict[str, Any]
    ) -> str:
        """
        Add contextual suffix to sync timestamp based on what changed.
        
        Analyzes the updates and transformations to generate a meaningful
        description like "(design_sync + deployment updates)" instead of
        just generic "(design_sync)".
        
        Args:
            updates: Recent updates list
            impl_state: Implementation state
            transformations: Transformations applied
            
        Returns:
            Contextual suffix string
        """
        context_keywords = []
        
        # Analyze recent updates for themes
        update_text = ' '.join(updates).lower()
        
        if 'deploy' in update_text or 'package' in update_text:
            context_keywords.append('deployment updates')
        
        if 'build' in update_text or 'script' in update_text:
            context_keywords.append('build automation')
        
        if 'test' in update_text and 'fix' in update_text:
            context_keywords.append('test fixes')
        
        if 'doc' in update_text or 'documentation' in update_text:
            context_keywords.append('documentation')
        
        # Check transformations
        if transformations.get('md_to_yaml_converted', 0) > 0:
            context_keywords.append('YAML conversion')
        
        if transformations.get('status_files_consolidated', 0) > 1:
            context_keywords.append('status consolidation')
        
        # Build context string
        if context_keywords:
            # Use first 2 most relevant keywords
            context = ' + '.join(context_keywords[:2])
            return f"(design_sync + {context})"
        else:
            return "(design_sync)"
