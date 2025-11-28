"""
User Profile Manager - Tech Stack Preference System
CORTEX 3.2.1 Phase 1: User Profile System Enhancements

Manages user profile preferences including tech stack configurations.
Provides preset configurations for common cloud platforms and custom options.
"""

from enum import Enum
from pathlib import Path
from typing import Optional, Dict, Any
import sqlite3
import json


class TechStackPreset(Enum):
    """
    Predefined tech stack configurations for common platforms.
    
    Each preset represents a complete, opinionated stack for a specific cloud provider.
    NO_PREFERENCE allows CORTEX to recommend best practices without bias.
    CUSTOM allows users to mix and match individual tools.
    """
    
    AZURE_STACK = "azure_stack"
    AWS_STACK = "aws_stack"
    GCP_STACK = "gcp_stack"
    NO_PREFERENCE = "no_preference"
    CUSTOM = "custom"
    
    @classmethod
    def get_configuration(cls, preset: 'TechStackPreset') -> Optional[Dict[str, str]]:
        """
        Get the full configuration dictionary for a preset.
        
        Args:
            preset: TechStackPreset enum value
            
        Returns:
            Dict with cloud_provider, container_platform, ci_cd, iac, architecture
            None if preset is NO_PREFERENCE
        """
        configurations = {
            cls.AZURE_STACK: {
                "cloud_provider": "azure",
                "container_platform": "aks",
                "ci_cd": "azure_devops",
                "iac": "arm",
                "architecture": "microservices"
            },
            cls.AWS_STACK: {
                "cloud_provider": "aws",
                "container_platform": "eks",
                "ci_cd": "github_actions",
                "iac": "terraform",
                "architecture": "microservices"
            },
            cls.GCP_STACK: {
                "cloud_provider": "gcp",
                "container_platform": "gke",
                "ci_cd": "cloud_build",
                "iac": "terraform",
                "architecture": "microservices"
            },
            cls.NO_PREFERENCE: None,  # CORTEX decides based on best practice
            cls.CUSTOM: None  # User provides their own configuration
        }
        
        return configurations.get(preset)


class UserProfileManager:
    """
    Manages user profile preferences with focus on tech stack configurations.
    
    Provides high-level interface for tech stack preference management,
    wrapping WorkingMemory's user_profile table operations.
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize UserProfileManager.
        
        Args:
            db_path: Path to SQLite database. If None, uses default location.
        """
        if db_path is None:
            db_path = Path("cortex-brain/tier1/working_memory.db")
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Ensure database schema exists
        self._init_database()
    
    def _init_database(self):
        """Initialize user_profile table if it doesn't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_profile (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                interaction_mode TEXT NOT NULL CHECK(interaction_mode IN ('autonomous', 'guided', 'educational', 'pair')) DEFAULT 'guided',
                experience_level TEXT NOT NULL CHECK(experience_level IN ('junior', 'mid', 'senior', 'expert')) DEFAULT 'mid',
                tech_stack_preference TEXT DEFAULT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                persistent_flag BOOLEAN NOT NULL DEFAULT 1
            )
        """)
        
        cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_single_profile ON user_profile(id)
        """)
        
        conn.commit()
        conn.close()
    
    def set_tech_stack_preset(self, preset: TechStackPreset) -> bool:
        """
        Set tech stack preference using a predefined preset.
        
        Args:
            preset: TechStackPreset enum value
            
        Returns:
            True if successful, False otherwise
        """
        config = TechStackPreset.get_configuration(preset)
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Serialize config to JSON (None for NO_PREFERENCE)
            config_json = json.dumps(config) if config else None
            
            # Check if profile exists
            cursor.execute("SELECT COUNT(*) FROM user_profile WHERE id = 1")
            exists = cursor.fetchone()[0] > 0
            
            if exists:
                # Update existing profile
                cursor.execute("""
                    UPDATE user_profile 
                    SET tech_stack_preference = ?, last_updated = CURRENT_TIMESTAMP 
                    WHERE id = 1
                """, (config_json,))
            else:
                # Create new profile with defaults
                cursor.execute("""
                    INSERT INTO user_profile (id, interaction_mode, experience_level, tech_stack_preference)
                    VALUES (1, 'guided', 'mid', ?)
                """, (config_json,))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"Failed to set tech stack preset: {e}")
            return False
    
    def set_tech_stack_custom(self, config: Dict[str, str]) -> bool:
        """
        Set custom tech stack configuration.
        
        Args:
            config: Dict with cloud_provider, container_platform, ci_cd, iac, architecture
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            ValueError: If configuration contains invalid values
        """
        # Validate configuration
        self._validate_tech_stack_config(config)
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            config_json = json.dumps(config)
            
            # Check if profile exists
            cursor.execute("SELECT COUNT(*) FROM user_profile WHERE id = 1")
            exists = cursor.fetchone()[0] > 0
            
            if exists:
                # Update existing profile
                cursor.execute("""
                    UPDATE user_profile 
                    SET tech_stack_preference = ?, last_updated = CURRENT_TIMESTAMP 
                    WHERE id = 1
                """, (config_json,))
            else:
                # Create new profile with defaults
                cursor.execute("""
                    INSERT INTO user_profile (id, interaction_mode, experience_level, tech_stack_preference)
                    VALUES (1, 'guided', 'mid', ?)
                """, (config_json,))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"Failed to set custom tech stack: {e}")
            return False
    
    def get_tech_stack_preference(self) -> Optional[Dict[str, str]]:
        """
        Get current tech stack preference.
        
        Returns:
            Dict with tech stack configuration, or None if not set/NO_PREFERENCE
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT tech_stack_preference 
                FROM user_profile 
                WHERE id = 1
            """)
            
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0]:
                return json.loads(result[0])
            
            return None
            
        except Exception as e:
            print(f"Failed to get tech stack preference: {e}")
            return None
    
    def update_tech_stack_preset(self, preset: TechStackPreset) -> bool:
        """
        Update existing tech stack preference to a new preset.
        
        Alias for set_tech_stack_preset for clarity in update scenarios.
        
        Args:
            preset: New TechStackPreset enum value
            
        Returns:
            True if successful, False otherwise
        """
        return self.set_tech_stack_preset(preset)
    
    def clear_tech_stack_preference(self) -> bool:
        """
        Clear tech stack preference (equivalent to NO_PREFERENCE).
        
        Returns:
            True if successful, False otherwise
        """
        return self.set_tech_stack_preset(TechStackPreset.NO_PREFERENCE)
    
    def get_profile(self) -> Optional[Dict[str, Any]]:
        """
        Get complete user profile including tech stack preference.
        
        Returns:
            Dict with interaction_mode, experience_level, tech_stack_preference, timestamps
            None if profile doesn't exist
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT interaction_mode, experience_level, tech_stack_preference, 
                       created_at, last_updated
                FROM user_profile
                WHERE id = 1
            """)
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                tech_stack = json.loads(result[2]) if result[2] else None
                
                return {
                    "interaction_mode": result[0],
                    "experience_level": result[1],
                    "tech_stack_preference": tech_stack,
                    "created_at": result[3],
                    "last_updated": result[4]
                }
            
            return None
            
        except Exception as e:
            print(f"Failed to get profile: {e}")
            return None
    
    def _validate_tech_stack_config(self, config: Dict[str, str]):
        """
        Validate tech stack configuration values.
        
        Args:
            config: Configuration dict to validate
            
        Raises:
            ValueError: If any configuration value is invalid
        """
        valid_cloud = ["azure", "aws", "gcp", "none"]
        valid_container = ["kubernetes", "aks", "eks", "gke", "docker", "none"]
        valid_arch = ["microservices", "monolithic", "hybrid"]
        valid_cicd = ["azure_devops", "github_actions", "jenkins", "cloud_build", "none"]
        valid_iac = ["terraform", "arm", "cloudformation", "none"]
        
        if "cloud_provider" in config and config["cloud_provider"] not in valid_cloud:
            raise ValueError(f"Invalid cloud_provider. Must be one of: {', '.join(valid_cloud)}")
        
        if "container_platform" in config and config["container_platform"] not in valid_container:
            raise ValueError(f"Invalid container_platform. Must be one of: {', '.join(valid_container)}")
        
        if "architecture" in config and config["architecture"] not in valid_arch:
            raise ValueError(f"Invalid architecture. Must be one of: {', '.join(valid_arch)}")
        
        if "ci_cd" in config and config["ci_cd"] not in valid_cicd:
            raise ValueError(f"Invalid ci_cd. Must be one of: {', '.join(valid_cicd)}")
        
        if "iac" in config and config["iac"] not in valid_iac:
            raise ValueError(f"Invalid iac. Must be one of: {', '.join(valid_iac)}")
