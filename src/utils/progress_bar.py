"""
Progress Bar Utility for Response Templates.

This module provides visual progress indicators for multi-step operations.
"""


class ProgressBar:
    """
    Visual progress bar using Unicode block characters.
    
    Renders progress as: ████████░░ 80%
    """
    
    def __init__(self, current: int, total: int, width: int = 20):
        """
        Initialize progress bar.
        
        Args:
            current: Current progress value
            total: Total target value
            width: Number of characters for the bar (default: 20)
        """
        self.current = max(0, current)  # Prevent negative values
        self.total = max(0, total)
        self.width = width
    
    def render(self) -> str:
        """
        Render progress bar with visual blocks and percentage.
        
        Returns:
            String with format: "████░░░ 50%"
        """
        if self.total == 0:
            return "░" * self.width + " 0%"
        
        # Calculate percentage (cap at 100%)
        percent = min(100, (self.current / self.total) * 100)
        
        # Calculate filled blocks
        filled = int((min(self.current, self.total) / self.total) * self.width)
        
        # Build visual bar
        bar = "█" * filled + "░" * (self.width - filled)
        
        return f"{bar} {percent:.0f}%"
