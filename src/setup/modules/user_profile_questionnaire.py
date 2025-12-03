"""
User Profile Questionnaire Module (Task 2.2)
Interactive questionnaire to collect user profile information
"""
import subprocess
from typing import Optional
from src.setup.models.user_profile import UserProfile, SUPPORTED_LANGUAGES


class UserProfileQuestionnaire:
    """Interactive questionnaire for collecting user profile data"""
    
    def __init__(self):
        """Initialize the questionnaire"""
        self.profile_data = {}
    
    def _get_git_user_name(self) -> Optional[str]:
        """Get user name from git config as default"""
        try:
            result = subprocess.run(
                ['git', 'config', '--global', 'user.name'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None
    
    def ask_name(self) -> str:
        """Ask for user's name with git config fallback"""
        git_name = self._get_git_user_name()
        default_text = f" (default: {git_name})" if git_name else ""
        
        print(f"\n👤 What's your name?{default_text}")
        name = input("   Name: ").strip()
        
        if not name and git_name:
            return git_name
        elif not name:
            return "User"
        return name
    
    def ask_preference(self) -> str:
        """Ask for response preference"""
        print("\n💬 How detailed should responses be?")
        print("   1. Concise - Brief, to the point")
        print("   2. Balanced - Mix of detail and brevity")
        print("   3. Verbose - Detailed explanations")
        
        while True:
            choice = input("   Choice (1-3, default: 3): ").strip()
            
            if not choice:
                return 'verbose'
            
            if choice == '1':
                return 'concise'
            elif choice == '2':
                return 'balanced'
            elif choice == '3':
                return 'verbose'
            else:
                print("   ⚠️  Invalid choice. Please enter 1, 2, or 3.")
    
    def ask_role(self) -> str:
        """Ask for user's technical role/expertise level"""
        print("\n🎯 What's your technical expertise level?")
        print("   1. Beginner - New to programming")
        print("   2. Intermediate - Comfortable with coding")
        print("   3. Expert - Advanced developer")
        
        while True:
            choice = input("   Choice (1-3, default: 2): ").strip()
            
            if not choice:
                return 'intermediate'
            
            if choice == '1':
                return 'beginner'
            elif choice == '2':
                return 'intermediate'
            elif choice == '3':
                return 'expert'
            else:
                print("   ⚠️  Invalid choice. Please enter 1, 2, or 3.")
    
    def ask_work_area(self) -> str:
        """Ask for user's primary work area"""
        print("\n💼 What's your primary work area?")
        print("   1. Web Development (Full Stack)")
        print("   2. Backend Development")
        print("   3. Frontend Development")
        print("   4. Mobile Development")
        print("   5. Data Science")
        print("   6. AI/Machine Learning")
        print("   7. DevOps")
        print("   8. General Development")
        
        while True:
            choice = input("   Choice (1-8, default: 8): ").strip()
            
            if not choice:
                return 'general'
            
            work_areas = {
                '1': 'fullstack',
                '2': 'backend',
                '3': 'frontend',
                '4': 'mobile',
                '5': 'data_science',
                '6': 'ai_ml',
                '7': 'devops',
                '8': 'general'
            }
            
            if choice in work_areas:
                return work_areas[choice]
            else:
                print("   ⚠️  Invalid choice. Please enter 1-8.")
    
    def ask_language(self) -> str:
        """Ask for preferred language with native names"""
        print("\n🌍 What's your preferred language?")
        
        # Display languages with native names
        languages = []
        for code, lang_info in SUPPORTED_LANGUAGES.items():
            languages.append((code, f"{lang_info['name']} ({lang_info['native']})"))
        
        for idx, (code, display) in enumerate(languages, 1):
            print(f"   {idx:2d}. {display}")
        
        while True:
            choice = input(f"   Choice (1-{len(languages)}, default: 1): ").strip()
            
            if not choice:
                return 'en'
            
            try:
                idx = int(choice)
                if 1 <= idx <= len(languages):
                    return languages[idx - 1][0]
                else:
                    print(f"   ⚠️  Invalid choice. Please enter 1-{len(languages)}.")
            except ValueError:
                print("   ⚠️  Please enter a number.")
    
    def run(self) -> UserProfile:
        """Run the complete questionnaire and return UserProfile"""
        print("\n" + "=" * 60)
        print("🧠 CORTEX User Profile Setup")
        print("=" * 60)
        print("\nLet's personalize your CORTEX experience!")
        print("Press Enter to use default values.")
        
        # Collect all profile data
        name = self.ask_name()
        preference = self.ask_preference()
        role = self.ask_role()
        work_area = self.ask_work_area()
        language = self.ask_language()
        
        # Create UserProfile
        profile = UserProfile(
            name=name,
            preference=preference,
            role=role,
            work_area=work_area,
            language=language
        )
        
        # Display summary
        print("\n" + "=" * 60)
        print("✅ Profile Created Successfully!")
        print("=" * 60)
        print(f"\n   Name:           {profile.name}")
        print(f"   Response Style: {profile.preference}")
        print(f"   Expertise:      {profile.role}")
        print(f"   Work Area:      {profile.work_area.replace('_', ' ').title()}")
        print(f"   Language:       {SUPPORTED_LANGUAGES[profile.language]['name']} ({SUPPORTED_LANGUAGES[profile.language]['native']})")
        print("\n" + "=" * 60)
        
        return profile
