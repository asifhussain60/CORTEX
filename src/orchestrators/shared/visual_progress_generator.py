"""Visual Progress Generator - Standardized progress bar rendering for CORTEX.

This module provides centralized, standardized visual progress generation
for all autonomous orchestrators with 10-character width standardization.

**CORTEX v5 Standardization (C50-06):**
- Default width: 10 characters
- ASCII block characters: █ (filled), ░ (empty)
- Percentage clamping: 0-100%
- Consistent formatting across all orchestrators

Author: Asif Hussain
Version: 1.0.0 (C50-06 Phase 2)
Created: 2026-01-04
"""

from typing import List, Dict, Any, Optional, Tuple


class VisualProgressGenerator:
    """Centralized visual progress bar generation for CORTEX orchestrators.
    
    **Standard Configuration:**
    - Width: 10 characters (CORTEX v5 standard)
    - Filled: █ (Unicode U+2588 - Full Block)
    - Empty: ░ (Unicode U+2591 - Light Shade)
    - Percentage: Clamped to 0-100
    
    **Usage:**
    ```python
    generator = VisualProgressGenerator()
    
    # Simple progress bar
    bar = generator.generate_bar(75)  # "███████░░░"
    
    # With label
    labeled = generator.generate_with_label("Phase 3", 60)  # "Phase 3: ██████░░░░ 60%"
    
    # Multi-phase display
    phases = [
        {"name": "Setup", "status": "complete", "progress": 100},
        {"name": "Execute", "status": "in_progress", "progress": 50},
        {"name": "Validate", "status": "pending", "progress": 0}
    ]
    multi = generator.generate_multi_phase(phases, current_phase=2)
    
    # Epic-level overview
    epic = generator.generate_epic_progress(5, 12)  # "Epic: █████░░░░░ 42% (5/12 complete)"
    ```
    """
    
    def __init__(
        self,
        width: int = 10,
        filled_char: str = '█',
        empty_char: str = '░'
    ):
        """Initialize visual progress generator.
        
        Args:
            width: Total width of progress bars (default: 10)
            filled_char: Character for filled portion (default: █)
            empty_char: Character for empty portion (default: ░)
        """
        self.width = width
        self.filled_char = filled_char
        self.empty_char = empty_char
        
        # Status emoji mapping
        self.status_emoji = {
            'complete': '✅',
            'in_progress': '🔄',
            'pending': '⏳',
            'blocked': '🔒',
            'failed': '❌',
            'skipped': '⏭️'
        }
    
    def generate_bar(
        self,
        percentage: float,
        width: Optional[int] = None
    ) -> str:
        """Generate a visual progress bar using Unicode block characters.
        
        Args:
            percentage: Progress percentage (0-100)
            width: Override default width (optional)
            
        Returns:
            Progress bar string like "████████░░" (10 chars at 80%)
            
        Example:
            >>> generator = VisualProgressGenerator()
            >>> generator.generate_bar(50)
            '█████░░░░░'
            >>> generator.generate_bar(100)
            '██████████'
            >>> generator.generate_bar(0)
            '░░░░░░░░░░'
        """
        width = width or self.width
        percentage = max(0, min(100, percentage))  # Clamp to 0-100
        filled_count = int(width * percentage / 100)
        empty_count = width - filled_count
        return f"{self.filled_char * filled_count}{self.empty_char * empty_count}"
    
    def generate_with_label(
        self,
        label: str,
        percentage: float,
        width: Optional[int] = None,
        show_percentage: bool = True
    ) -> str:
        """Generate labeled progress bar with optional percentage display.
        
        Args:
            label: Text label for the progress bar
            percentage: Progress percentage (0-100)
            width: Override default width (optional)
            show_percentage: Whether to show percentage value (default: True)
            
        Returns:
            Formatted string like "Phase 3: ██████░░░░ 60%"
            
        Example:
            >>> generator = VisualProgressGenerator()
            >>> generator.generate_with_label("Setup", 100)
            'Setup: ██████████ 100%'
            >>> generator.generate_with_label("Execute", 50, show_percentage=False)
            'Execute: █████░░░░░'
        """
        bar = self.generate_bar(percentage, width)
        
        if show_percentage:
            return f"{label}: {bar} {int(percentage)}%"
        else:
            return f"{label}: {bar}"
    
    def generate_multi_phase(
        self,
        phases: List[Dict[str, Any]],
        current_phase: int,
        width: Optional[int] = None,
        show_status_emoji: bool = True
    ) -> str:
        """Generate multi-phase progress display with status indicators.
        
        Args:
            phases: List of phase dictionaries with keys:
                - name (str): Phase name
                - status (str): Phase status (complete/in_progress/pending/blocked/failed/skipped)
                - progress (float): Phase progress percentage (0-100)
            current_phase: Current phase number (1-indexed)
            width: Override default width (optional)
            show_status_emoji: Whether to show status emoji (default: True)
            
        Returns:
            Multi-line formatted phase progress display
            
        Example:
            >>> generator = VisualProgressGenerator()
            >>> phases = [
            ...     {"name": "Setup", "status": "complete", "progress": 100},
            ...     {"name": "Execute", "status": "in_progress", "progress": 50},
            ...     {"name": "Validate", "status": "pending", "progress": 0}
            ... ]
            >>> print(generator.generate_multi_phase(phases, current_phase=2))
            ✅ Phase 1: Setup      ██████████ 100%
            🔄 Phase 2: Execute    █████░░░░░ 50%  [CURRENT]
            ⏳ Phase 3: Validate   ░░░░░░░░░░ 0%
        """
        width = width or self.width
        lines = []
        
        for idx, phase in enumerate(phases, start=1):
            name = phase.get('name', f'Phase {idx}')
            status = phase.get('status', 'pending')
            progress = phase.get('progress', 0)
            
            # Get status emoji
            emoji = self.status_emoji.get(status, '❓') if show_status_emoji else ''
            
            # Generate progress bar
            bar = self.generate_bar(progress, width)
            
            # Add current phase indicator
            current_marker = '  [CURRENT]' if idx == current_phase else ''
            
            # Format line (pad name to 12 characters for alignment)
            padded_name = f"{name:<12}"
            line = f"{emoji} Phase {idx}: {padded_name} {bar} {int(progress)}%{current_marker}"
            lines.append(line)
        
        return '\n'.join(lines)
    
    def generate_epic_progress(
        self,
        completed: int,
        total: int,
        epic_name: Optional[str] = None,
        width: Optional[int] = None
    ) -> str:
        """Generate epic-level progress overview.
        
        Args:
            completed: Number of completed child plans/phases
            total: Total number of child plans/phases
            epic_name: Optional epic name (default: "Epic")
            width: Override default width (optional)
            
        Returns:
            Formatted epic progress string
            
        Example:
            >>> generator = VisualProgressGenerator()
            >>> generator.generate_epic_progress(5, 12)
            'Epic: █████░░░░░ 42% (5/12 complete)'
            >>> generator.generate_epic_progress(8, 10, epic_name="CORTEX v5")
            'CORTEX v5: ████████░░ 80% (8/10 complete)'
        """
        width = width or self.width
        epic_name = epic_name or "Epic"
        
        # Calculate percentage
        percentage = (completed / total * 100) if total > 0 else 0
        
        # Generate bar
        bar = self.generate_bar(percentage, width)
        
        return f"{epic_name}: {bar} {int(percentage)}% ({completed}/{total} complete)"
    
    def get_status_emoji(self, status: str) -> str:
        """Get emoji for a given status.
        
        Args:
            status: Status string (complete/in_progress/pending/blocked/failed/skipped)
            
        Returns:
            Emoji character for the status
            
        Example:
            >>> generator = VisualProgressGenerator()
            >>> generator.get_status_emoji('complete')
            '✅'
            >>> generator.get_status_emoji('in_progress')
            '🔄'
        """
        return self.status_emoji.get(status, '❓')
    
    def calculate_percentage(self, completed: int, total: int) -> float:
        """Calculate percentage completion.
        
        Args:
            completed: Number of completed items
            total: Total number of items
            
        Returns:
            Percentage (0-100), clamped and rounded to 2 decimal places
            
        Example:
            >>> generator = VisualProgressGenerator()
            >>> generator.calculate_percentage(5, 10)
            50.0
            >>> generator.calculate_percentage(7, 10)
            70.0
            >>> generator.calculate_percentage(0, 0)
            0.0
        """
        if total == 0:
            return 0.0
        
        percentage = (completed / total) * 100
        return round(max(0, min(100, percentage)), 2)
