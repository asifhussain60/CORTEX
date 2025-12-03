"""
User Profile Validator Module (Task 2.4)
Provides validation logic and smart defaults for user profiles
"""
import subprocess
import re
from typing import Optional, Tuple, List, Dict, Any
from pydantic import ValidationError
from src.setup.models.user_profile import UserProfile


class UserProfileValidator:
    """Validates user profiles and provides smart defaults"""
    
    def __init__(self):
        """Initialize validator"""
        pass
    
    def get_git_user_name(self) -> Optional[str]:
        """
        Get user name from git config.
        
        Returns:
            Git user.name if configured, None otherwise
        """
        try:
            result = subprocess.run(
                ['git', 'config', '--global', 'user.name'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except Exception:
            pass
        return None
    
    def get_git_user_email(self) -> Optional[str]:
        """
        Get user email from git config.
        
        Returns:
            Git user.email if configured, None otherwise
        """
        try:
            result = subprocess.run(
                ['git', 'config', '--global', 'user.email'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except Exception:
            pass
        return None
    
    def validate_profile(self, profile: UserProfile) -> Tuple[bool, List[str]]:
        """
        Validate a UserProfile instance.
        
        Args:
            profile: UserProfile instance to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        # Pydantic already validates on instantiation
        # This method is here for consistency and future custom validation
        return True, []
    
    def validate_profile_data(self, profile_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate profile data dictionary before creating UserProfile.
        
        Args:
            profile_data: Dictionary with profile fields
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        try:
            # Try to create UserProfile (Pydantic will validate)
            UserProfile(**profile_data)
            return True, []
        except ValidationError as e:
            # Extract error messages
            for error in e.errors():
                field = error['loc'][0] if error['loc'] else 'unknown'
                msg = error['msg']
                errors.append(f"{field}: {msg}")
            return False, errors
        except Exception as e:
            errors.append(f"Validation error: {str(e)}")
            return False, errors
    
    def create_default_profile(self) -> UserProfile:
        """
        Create a default profile with smart defaults.
        
        Returns:
            UserProfile with default values
        """
        git_name = self.get_git_user_name()
        name = git_name if git_name else "User"
        
        return UserProfile(
            name=name,
            preference="verbose",
            role="intermediate",
            work_area="general",
            language="en"
        )
    
    def apply_smart_defaults(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply smart defaults to incomplete profile data.
        
        Args:
            profile_data: Partial profile data
            
        Returns:
            Complete profile data with defaults filled in
        """
        defaults = {
            "name": self.get_git_user_name() or "User",
            "preference": "verbose",
            "role": "intermediate",
            "work_area": "general",
            "language": "en"
        }
        
        # Merge with defaults (profile_data takes precedence)
        complete_data = {**defaults, **profile_data}
        
        return complete_data
    
    def sanitize_name(self, name: str) -> Optional[str]:
        """
        Sanitize user name by removing extra whitespace.
        
        Args:
            name: Raw name input
            
        Returns:
            Sanitized name or None if empty
        """
        if not name:
            return None
        
        # Remove extra whitespace and normalize
        sanitized = re.sub(r'\s+', ' ', name.strip())
        
        return sanitized if sanitized else None
