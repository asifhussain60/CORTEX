"""Naming exception manager."""

from src.governance.file_naming_validator import FileNameValidator


class NamingExceptionManager:
    """Manages naming exceptions."""
    
    def __init__(self):
        self.validator = FileNameValidator()
    
    def is_exception(self, filename: str) -> bool:
        """Check if filename is an allowed exception."""
        return filename in self.validator.ALLOWED_EXCEPTIONS
