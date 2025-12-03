"""
User Profile Setup Module (Task 2.6)
Integrates user profiling system into CORTEX setup orchestrator
"""
import time
from typing import Dict, Any, Tuple, List
from pathlib import Path

from src.setup.base_setup_module import (
    BaseSetupModule,
    SetupModuleMetadata,
    SetupResult,
    SetupStatus,
    SetupPhase
)
from src.setup.models.user_profile import UserProfile
from src.setup.modules.user_profile_questionnaire import UserProfileQuestionnaire
from src.setup.modules.user_profile_storage import UserProfileStorage
from src.setup.modules.user_profile_validator import UserProfileValidator
from src.setup.modules.user_profile_editor import UserProfileEditor


class UserProfileModule(BaseSetupModule):
    """
    Setup module for user profile creation and management.
    
    Features:
    - Detects existing profiles
    - Runs interactive questionnaire for new profiles
    - Offers to edit existing profiles
    - Stores profile in cortex.config.json
    - Optional module (can skip on failure)
    
    Context Keys:
    - config_path: Path to cortex.config.json (optional, defaults to CORTEX repo)
    """
    
    def get_metadata(self) -> SetupModuleMetadata:
        """Return module metadata."""
        return SetupModuleMetadata(
            module_id="user_profile",
            name="User Profile Setup",
            description="Create or update user profile for personalized experience",
            phase=SetupPhase.FEATURES,
            priority=100,  # Run early in features phase
            dependencies=[],
            optional=True,  # Don't block setup if this fails
            enabled_by_default=True
        )
    
    def validate_prerequisites(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate prerequisites for profile setup.
        
        Args:
            context: Setup context
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        # Profile setup has minimal prerequisites
        # Config file will be created if it doesn't exist
        return True, []
    
    def execute(self, context: Dict[str, Any]) -> SetupResult:
        """
        Execute user profile setup.
        
        Args:
            context: Setup context with optional 'config_path'
            
        Returns:
            SetupResult with profile creation status
        """
        start_time = time.time()
        
        try:
            # Get config path from context or use default
            config_path = context.get('config_path')
            storage = UserProfileStorage(config_path)
            
            # Check if profile already exists
            existing_profile = storage.load_profile()
            
            if existing_profile:
                self.logger.info(f"✓ Found existing profile: {existing_profile.name}")
                
                # Offer to edit existing profile
                print(f"\n👤 Found existing profile: {existing_profile.name}")
                edit_choice = input("   Would you like to edit your profile? (y/N): ").strip().lower()
                
                if edit_choice == 'y':
                    editor = UserProfileEditor(existing_profile)
                    updated_profile = editor.run()
                    
                    # Save updated profile
                    storage.save_profile(updated_profile)
                    
                    duration_ms = (time.time() - start_time) * 1000
                    
                    return SetupResult(
                        module_id=self.metadata.module_id,
                        status=SetupStatus.SUCCESS,
                        message=f"Profile updated: {updated_profile.name}",
                        details={'profile': updated_profile.model_dump()},
                        duration_ms=duration_ms
                    )
                else:
                    duration_ms = (time.time() - start_time) * 1000
                    
                    return SetupResult(
                        module_id=self.metadata.module_id,
                        status=SetupStatus.SKIPPED,
                        message=f"Using existing profile: {existing_profile.name}",
                        details={'profile': existing_profile.model_dump()},
                        duration_ms=duration_ms
                    )
            
            # No existing profile - run questionnaire
            self.logger.info("Creating new user profile...")
            
            questionnaire = UserProfileQuestionnaire()
            profile = questionnaire.run()
            
            # Save profile
            storage.save_profile(profile)
            
            duration_ms = (time.time() - start_time) * 1000
            
            return SetupResult(
                module_id=self.metadata.module_id,
                status=SetupStatus.SUCCESS,
                message=f"Profile created successfully: {profile.name}",
                details={'profile': profile.model_dump()},
                duration_ms=duration_ms
            )
            
        except KeyboardInterrupt:
            duration_ms = (time.time() - start_time) * 1000
            
            return SetupResult(
                module_id=self.metadata.module_id,
                status=SetupStatus.SKIPPED,
                message="Profile setup cancelled by user",
                warnings=["User cancelled profile creation"],
                duration_ms=duration_ms
            )
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            
            self.logger.error(f"Profile setup failed: {str(e)}")
            
            return SetupResult(
                module_id=self.metadata.module_id,
                status=SetupStatus.FAILED,
                message=f"Profile setup failed: {str(e)}",
                errors=[str(e)],
                duration_ms=duration_ms
            )
    
    def rollback(self, context: Dict[str, Any]) -> bool:
        """
        Rollback profile setup (remove profile from config).
        
        Args:
            context: Setup context
            
        Returns:
            True if rollback successful
        """
        try:
            config_path = context.get('config_path')
            storage = UserProfileStorage(config_path)
            
            # Check if profile exists
            if not storage.profile_exists():
                self.logger.info("No profile to rollback")
                return True
            
            # Read config
            import json
            with open(storage.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Remove user section
            if 'user' in config:
                del config['user']
                
                # Write back
                with open(storage.config_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                
                self.logger.info("✓ Profile removed from config")
                return True
            
            return True
            
        except Exception as e:
            self.logger.error(f"Rollback failed: {str(e)}")
            return False
