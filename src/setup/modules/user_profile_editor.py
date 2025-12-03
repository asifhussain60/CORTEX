"""
User Profile Editor Module (Task 2.5)
Interactive editor for updating existing user profiles
"""
from typing import Optional
from src.setup.models.user_profile import UserProfile, SUPPORTED_LANGUAGES


class UserProfileEditor:
    """Interactive editor for modifying user profiles"""
    
    def __init__(self, profile: UserProfile):
        """
        Initialize editor with existing profile.
        
        Args:
            profile: UserProfile instance to edit
        """
        self.profile = profile
    
    def show_current_profile(self) -> None:
        """Display current profile values"""
        print("\n" + "=" * 60)
        print("📋 Current Profile")
        print("=" * 60)
        print(f"   Name:           {self.profile.name}")
        print(f"   Response Style: {self.profile.preference}")
        print(f"   Expertise:      {self.profile.role}")
        print(f"   Work Area:      {self.profile.work_area.replace('_', ' ').title()}")
        lang_info = SUPPORTED_LANGUAGES[self.profile.language]
        print(f"   Language:       {lang_info['name']} ({lang_info['native']})")
        print("=" * 60)
    
    def show_menu(self) -> None:
        """Display edit menu options"""
        print("\n🔧 What would you like to edit?")
        print("   1. Name")
        print("   2. Response Preference")
        print("   3. Role/Expertise")
        print("   4. Work Area")
        print("   5. Language")
        print("   6. Done (Save and Exit)")
    
    def edit_name(self) -> UserProfile:
        """
        Edit user name.
        
        Returns:
            Updated UserProfile
        """
        print(f"\n👤 Current name: {self.profile.name}")
        new_name = input("   New name (press Enter to keep current): ").strip()
        
        if new_name:
            return UserProfile(
                name=new_name,
                preference=self.profile.preference,
                role=self.profile.role,
                work_area=self.profile.work_area,
                language=self.profile.language
            )
        return self.profile
    
    def edit_preference(self) -> UserProfile:
        """
        Edit response preference.
        
        Returns:
            Updated UserProfile
        """
        print(f"\n💬 Current preference: {self.profile.preference}")
        print("   1. Concise - Brief, to the point")
        print("   2. Balanced - Mix of detail and brevity")
        print("   3. Verbose - Detailed explanations")
        
        while True:
            choice = input("   Choice (1-3, Enter to keep current): ").strip()
            
            if not choice:
                return self.profile
            
            preference_map = {'1': 'concise', '2': 'balanced', '3': 'verbose'}
            
            if choice in preference_map:
                return UserProfile(
                    name=self.profile.name,
                    preference=preference_map[choice],
                    role=self.profile.role,
                    work_area=self.profile.work_area,
                    language=self.profile.language
                )
            else:
                print("   ⚠️  Invalid choice. Please enter 1, 2, or 3.")
    
    def edit_role(self) -> UserProfile:
        """
        Edit user role/expertise.
        
        Returns:
            Updated UserProfile
        """
        print(f"\n🎯 Current role: {self.profile.role}")
        print("   1. Beginner - New to programming")
        print("   2. Intermediate - Comfortable with coding")
        print("   3. Expert - Advanced developer")
        
        while True:
            choice = input("   Choice (1-3, Enter to keep current): ").strip()
            
            if not choice:
                return self.profile
            
            role_map = {'1': 'beginner', '2': 'intermediate', '3': 'expert'}
            
            if choice in role_map:
                return UserProfile(
                    name=self.profile.name,
                    preference=self.profile.preference,
                    role=role_map[choice],
                    work_area=self.profile.work_area,
                    language=self.profile.language
                )
            else:
                print("   ⚠️  Invalid choice. Please enter 1, 2, or 3.")
    
    def edit_work_area(self) -> UserProfile:
        """
        Edit work area.
        
        Returns:
            Updated UserProfile
        """
        print(f"\n💼 Current work area: {self.profile.work_area.replace('_', ' ').title()}")
        print("   1. Web Development (Full Stack)")
        print("   2. Backend Development")
        print("   3. Frontend Development")
        print("   4. Mobile Development")
        print("   5. Data Science")
        print("   6. AI/Machine Learning")
        print("   7. DevOps")
        print("   8. General Development")
        
        while True:
            choice = input("   Choice (1-8, Enter to keep current): ").strip()
            
            if not choice:
                return self.profile
            
            work_area_map = {
                '1': 'fullstack',
                '2': 'backend',
                '3': 'frontend',
                '4': 'mobile',
                '5': 'data_science',
                '6': 'ai_ml',
                '7': 'devops',
                '8': 'general'
            }
            
            if choice in work_area_map:
                return UserProfile(
                    name=self.profile.name,
                    preference=self.profile.preference,
                    role=self.profile.role,
                    work_area=work_area_map[choice],
                    language=self.profile.language
                )
            else:
                print("   ⚠️  Invalid choice. Please enter 1-8.")
    
    def edit_language(self) -> UserProfile:
        """
        Edit preferred language.
        
        Returns:
            Updated UserProfile
        """
        current_lang = SUPPORTED_LANGUAGES[self.profile.language]
        print(f"\n🌍 Current language: {current_lang['name']} ({current_lang['native']})")
        
        # Display languages with native names
        languages = []
        for code, lang_info in SUPPORTED_LANGUAGES.items():
            languages.append((code, f"{lang_info['name']} ({lang_info['native']})"))
        
        for idx, (code, display) in enumerate(languages, 1):
            print(f"   {idx:2d}. {display}")
        
        while True:
            choice = input(f"   Choice (1-{len(languages)}, Enter to keep current): ").strip()
            
            if not choice:
                return self.profile
            
            try:
                idx = int(choice)
                if 1 <= idx <= len(languages):
                    return UserProfile(
                        name=self.profile.name,
                        preference=self.profile.preference,
                        role=self.profile.role,
                        work_area=self.profile.work_area,
                        language=languages[idx - 1][0]
                    )
                else:
                    print(f"   ⚠️  Invalid choice. Please enter 1-{len(languages)}.")
            except ValueError:
                print("   ⚠️  Please enter a number.")
    
    def run(self) -> UserProfile:
        """
        Run interactive profile editor.
        
        Returns:
            Updated UserProfile
        """
        print("\n" + "=" * 60)
        print("🔧 CORTEX Profile Editor")
        print("=" * 60)
        
        while True:
            self.show_current_profile()
            self.show_menu()
            
            choice = input("\n   Your choice: ").strip()
            
            if choice == '1':
                self.profile = self.edit_name()
            elif choice == '2':
                self.profile = self.edit_preference()
            elif choice == '3':
                self.profile = self.edit_role()
            elif choice == '4':
                self.profile = self.edit_work_area()
            elif choice == '5':
                self.profile = self.edit_language()
            elif choice == '6':
                print("\n✅ Profile updated successfully!")
                break
            else:
                print("\n⚠️  Invalid choice. Please select 1-6.")
        
        return self.profile
