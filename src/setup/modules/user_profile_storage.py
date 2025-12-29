"""
User Profile Storage Module (Task 2.3)
Handles saving/loading user profiles and path configurations to/from cortex.config.json
"""
import json
import os
from pathlib import Path
from typing import Optional
from src.setup.models.user_profile import UserProfile
from src.setup.models.user_path_config import UserPathConfig


class UserProfileStorage:
    """Manages user profile persistence in cortex.config.json"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize storage with config file path.
        
        Args:
            config_path: Path to cortex.config.json (defaults to CORTEX repo location)
        """
        if config_path:
            self.config_path = config_path
        else:
            # Default to CORTEX repo's cortex.config.json
            self.config_path = self._get_default_config_path()
    
    def _get_default_config_path(self) -> str:
        """Get default cortex.config.json path in CORTEX repo"""
        # Navigate from this file to repo root
        current_file = Path(__file__).resolve()
        repo_root = current_file.parent.parent.parent  # src/setup/modules -> CORTEX
        config_path = repo_root / "cortex.config.json"
        return str(config_path)
    
    def _read_config(self) -> dict:
        """Read existing config file or return empty config"""
        if not os.path.exists(self.config_path):
            return {
                "machines": {},
                "testing": {"enabled": False}
            }
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            # If file is corrupted, return minimal config
            return {
                "machines": {},
                "testing": {"enabled": False}
            }
    
    def _write_config(self, config: dict) -> None:
        """Write config to file with formatting"""
        # Ensure directory exists
        config_dir = os.path.dirname(self.config_path)
        if config_dir and not os.path.exists(config_dir):
            os.makedirs(config_dir, exist_ok=True)
        
        # Write with 2-space indentation for readability
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    def save_profile(self, profile: UserProfile) -> None:
        """
        Save user profile to config file.
        
        Args:
            profile: UserProfile instance to save
        """
        # Read existing config
        config = self._read_config()
        
        # Add/update user section
        config['user'] = profile.model_dump()
        
        # Write back to file
        self._write_config(config)
    
    def load_profile(self) -> Optional[UserProfile]:
        """
        Load user profile from config file.
        
        Returns:
            UserProfile instance if found, None otherwise
        """
        if not os.path.exists(self.config_path):
            return None
        
        config = self._read_config()
        
        if 'user' not in config:
            return None
        
        try:
            # Create UserProfile from config data
            return UserProfile(**config['user'])
        except Exception:
            # If profile data is invalid, return None
            return None
    
    def profile_exists(self) -> bool:
        """
        Check if user profile exists in config.
        
        Returns:
            True if profile exists, False otherwise
        """
        if not os.path.exists(self.config_path):
            return False
        
        config = self._read_config()
        return 'user' in config and isinstance(config['user'], dict)
    
    def save_path_config(self, path_config: UserPathConfig) -> None:
        """
        Save user path configuration to config file.
        
        Args:
            path_config: UserPathConfig instance to save
        """
        # Read existing config
        config = self._read_config()
        
        # Add/update user_paths section
        config['user_paths'] = path_config.to_dict()
        
        # Write back to file
        self._write_config(config)
    
    def load_path_config(self) -> Optional[UserPathConfig]:
        """
        Load user path configuration from config file.
        
        Returns:
            UserPathConfig instance if found, None otherwise
        """
        if not os.path.exists(self.config_path):
            return None
        
        config = self._read_config()
        
        if 'user_paths' not in config:
            return None
        
        try:
            # Create UserPathConfig from config data
            return UserPathConfig(**config['user_paths'])
        except Exception:
            # If path config data is invalid, return None
            return None
    
    def path_config_exists(self) -> bool:
        """
        Check if user path configuration exists in config.
        
        Returns:
            True if path config exists, False otherwise
        """
        if not os.path.exists(self.config_path):
            return False
        
        config = self._read_config()
        return 'user_paths' in config and isinstance(config['user_paths'], dict)
    
    def save_complete_config(self, profile: UserProfile, path_config: UserPathConfig) -> None:
        """
        Save both user profile and path configuration atomically.
        
        Args:
            profile: UserProfile instance
            path_config: UserPathConfig instance
        """
        # Read existing config
        config = self._read_config()
        
        # Update both sections
        config['user'] = profile.model_dump()
        config['user_paths'] = path_config.to_dict()
        
        # Write back to file
        self._write_config(config)

