"""Training Materials & Communication Plan System"""
from typing import List, Dict


class TrainingModule:
    """Training module with lessons.
    
    Args:
        name: Module name
    """
    def __init__(self, name: str):
        self.name = name
        self.lessons: List[str] = []
    
    def add_lesson(self, title: str) -> None:
        """Add lesson to module.
        
        Args:
            title: Lesson title
        """
        self.lessons.append(title)
    
    def get_lesson_count(self) -> int:
        """Get lesson count.
        
        Returns:
            Number of lessons
        """
        return len(self.lessons)


class CommunicationPlan:
    """Communication plan for training adoption."""
    
    def __init__(self):
        self.announcements: List[str] = []
        self.schedule: Dict[str, str] = {}
    
    def announce(self, message: str) -> None:
        """Send announcement.
        
        Args:
            message: Announcement message
        """
        self.announcements.append(message)
    
    def schedule_communication(self, date: str, message: str) -> None:
        """Schedule communication.
        
        Args:
            date: Date to send
            message: Message content
        """
        self.schedule[date] = message
    
    def get_announcement_count(self) -> int:
        """Get announcement count.
        
        Returns:
            Number of announcements
        """
        return len(self.announcements)
    
    def get_schedule_size(self) -> int:
        """Get schedule size.
        
        Returns:
            Number of scheduled items
        """
        return len(self.schedule)
