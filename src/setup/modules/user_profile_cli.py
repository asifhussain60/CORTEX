"""
User Profile CLI Commands (Task 2.7)
Command-line interface for managing user profiles
"""
from enum import Enum
from typing import Optional
from src.setup.models.user_profile import UserProfile, SUPPORTED_LANGUAGES
from src.setup.modules.user_profile_storage import UserProfileStorage
from src.setup.modules.user_profile_questionnaire import UserProfileQuestionnaire
from src.setup.modules.user_profile_editor import UserProfileEditor


class ProfileCommands(Enum):
    """Available profile management commands"""
    SHOW = "show"
    EDIT = "edit"
    CREATE = "create"
    DELETE = "delete"


class UserProfileCLI:
    """
    Command-line interface for user profile management.
    
    Commands:
    - show: Display current profile
    - edit: Edit existing profile interactively
    - create: Create new profile (fails if exists)
    - delete: Remove profile from config
    
    Usage:
        cli = UserProfileCLI()
        
        # Show profile
        cli.show()
        
        # Edit profile
        cli.edit()
        
        # Create new profile
        cli.create()
        
        # Delete profile
        cli.delete()
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize CLI with config path.
        
        Args:
            config_path: Path to cortex.config.json (optional)
        """
        self.storage = UserProfileStorage(config_path)
        self.config_path = self.storage.config_path
    
    def show(self) -> int:
        """
        Display current user profile.
        
        Returns:
            Exit code (0 = success, 1 = error)
        """
        profile = self.storage.load_profile()
        
        if not profile:
            print("❌ No user profile found.")
            print("   Run 'profile create' to create one.")
            return 1
        
        print("\n" + "=" * 60)
        print("👤 CORTEX User Profile")
        print("=" * 60)
        print(f"\n   Name:           {profile.name}")
        print(f"   Response Style: {profile.preference.title()}")
        print(f"   Expertise:      {profile.role.title()}")
        print(f"   Work Area:      {profile.work_area.replace('_', ' ').title()}")
        
        lang_info = SUPPORTED_LANGUAGES[profile.language]
        print(f"   Language:       {lang_info['name']} ({lang_info['native']})")
        
        print("\n" + "=" * 60)
        
        return 0
    
    def edit(self) -> int:
        """
        Edit existing user profile interactively.
        
        Returns:
            Exit code (0 = success, 1 = error)
        """
        profile = self.storage.load_profile()
        
        if not profile:
            print("❌ No user profile found.")
            print("   Run 'profile create' to create one.")
            return 1
        
        # Open interactive editor
        editor = UserProfileEditor(profile)
        updated_profile = editor.run()
        
        # Save updated profile
        self.storage.save_profile(updated_profile)
        
        return 0
    
    def create(self) -> int:
        """
        Create new user profile via interactive questionnaire.
        
        Returns:
            Exit code (0 = success, 1 = error)
        """
        # Check if profile already exists
        if self.storage.profile_exists():
            print("❌ User profile already exists.")
            print("   Use 'profile edit' to modify it.")
            return 1
        
        # Run questionnaire
        questionnaire = UserProfileQuestionnaire()
        profile = questionnaire.run()
        
        # Save profile
        self.storage.save_profile(profile)
        
        return 0
    
    def delete(self) -> int:
        """
        Delete user profile from config.
        
        Returns:
            Exit code (0 = success, 1 = error)
        """
        profile = self.storage.load_profile()
        
        if not profile:
            print("❌ No user profile found.")
            return 1
        
        # Confirm deletion
        print(f"\n⚠️  Are you sure you want to delete profile for '{profile.name}'?")
        confirm = input("   Type 'y' to confirm: ").strip().lower()
        
        if confirm != 'y':
            print("   Deletion cancelled.")
            return 0
        
        # Remove profile from config
        import json
        with open(self.storage.config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        if 'user' in config:
            del config['user']
            
            with open(self.storage.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print("\n✅ Profile deleted successfully.")
            return 0
        
        return 1


def main():
    """
    Main entry point for CLI.
    
    Usage from command line:
        python -m src.setup.modules.user_profile_cli show
        python -m src.setup.modules.user_profile_cli edit
        python -m src.setup.modules.user_profile_cli create
        python -m src.setup.modules.user_profile_cli delete
    """
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m src.setup.modules.user_profile_cli <command>")
        print("\nCommands:")
        print("  show    - Display current profile")
        print("  edit    - Edit existing profile")
        print("  create  - Create new profile")
        print("  delete  - Delete profile")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    cli = UserProfileCLI()
    
    if command == 'show':
        sys.exit(cli.show())
    elif command == 'edit':
        sys.exit(cli.edit())
    elif command == 'create':
        sys.exit(cli.create())
    elif command == 'delete':
        sys.exit(cli.delete())
    else:
        print(f"❌ Unknown command: {command}")
        print("\nValid commands: show, edit, create, delete")
        sys.exit(1)


if __name__ == '__main__':
    main()
