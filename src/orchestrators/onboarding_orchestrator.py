"""
Onboarding Orchestrator (CORTEX 3.2.2)

Handles first-time user onboarding with 2-question micro-survey to establish
user profile preferences. Integrates with Tier 1 for profile storage and
response templates for consistent formatting.

Features:
- 10-second onboarding (2 questions only)
- Interactive choice presentation
- Input validation with user-friendly errors
- Profile creation in Tier 1 with FIFO exemption
- Resumable (can update profile anytime)
- Progress notifications for long-running setup

Author: Asif Hussain
Version: 3.2.2
"""

from typing import Dict, Any, Optional
from pathlib import Path
import json
import re

from src.utils.progress_decorator import (
    with_progress,
    yield_progress,
    generate_initial_notification
)
from src.tier1.working_memory import WorkingMemory

class OnboardingOrchestrator:
    """
    Orchestrates user onboarding and profile creation.
    
    Presents 2-question micro-survey to establish user preferences:
    1. Experience level (junior/mid/senior/expert)
    2. Interaction mode (autonomous/guided/educational/pair)
    
    Stores profile in Tier 1 with FIFO exemption for permanent retention.
    """
    
    def __init__(self, tier1_api=None):
        """
        Initialize onboarding orchestrator.
        
        Args:
            tier1_api: Tier 1 API instance for profile storage
        """
        self.tier1 = tier1_api
        self.working_memory = WorkingMemory()
        
        # Experience level choices
        self.experience_levels = {
            "1": {"value": "junior", "label": "Junior - Learning the ropes, need guidance"},
            "2": {"value": "mid", "label": "Mid - Solid fundamentals, occasional help needed"},
            "3": {"value": "senior", "label": "Senior - Experienced, confident in most areas"},
            "4": {"value": "expert", "label": "Expert - Deep expertise, minimal hand-holding"}
        }
        
        # Interaction mode choices
        self.interaction_modes = {
            "1": {"value": "autonomous", "label": "Autonomous - Just do it, show me results"},
            "2": {"value": "guided", "label": "Guided - Explain what you're doing (recommended)"},
            "3": {"value": "educational", "label": "Educational - Teach me why and show alternatives"},
            "4": {"value": "pair", "label": "Pair Programming - Ask clarifying questions first"}
        }
        
        # Tech stack presets (context for deployment, NOT constraint on recommendations)
        self.tech_stack_presets = {
            "1": {
                "value": None,
                "label": "No preference - CORTEX decides based on best practice"
            },
            "2": {
                "value": "azure",
                "label": "Azure stack (Azure DevOps, AKS, ARM/Terraform)",
                "preset": {
                    "cloud_provider": "azure",
                    "container_platform": "kubernetes",
                    "architecture": "microservices",
                    "ci_cd": "azure_devops",
                    "iac": "terraform"
                }
            },
            "3": {
                "value": "aws",
                "label": "AWS stack (ECS/EKS, CodePipeline, CloudFormation/Terraform)",
                "preset": {
                    "cloud_provider": "aws",
                    "container_platform": "kubernetes",
                    "architecture": "microservices",
                    "ci_cd": "github_actions",
                    "iac": "terraform"
                }
            },
            "4": {
                "value": "gcp",
                "label": "GCP stack (GKE, Cloud Build, Terraform)",
                "preset": {
                    "cloud_provider": "gcp",
                    "container_platform": "kubernetes",
                    "architecture": "microservices",
                    "ci_cd": "github_actions",
                    "iac": "terraform"
                }
            },
            "5": {
                "value": "custom",
                "label": "Custom (I'll configure later with 'update profile')"
            }
        }
    
    def start_onboarding(self, original_message: str) -> Dict[str, Any]:
        """
        Start onboarding flow.
        
        Args:
            original_message: User's original message that triggered onboarding
        
        Returns:
            Dict with onboarding content and status
        """
        return {
            "status": "onboarding_started",
            "content": self._generate_welcome_message(),
            "original_message": original_message,
            "step": "experience_level"
        }
    
    def _generate_welcome_message(self) -> str:
        """Generate welcome message with first question."""
        
        # Build experience level choices
        experience_choices = "\n".join([
            f"{key}. {data['label']}" 
            for key, data in self.experience_levels.items()
        ])
        
        message = f"""## 🧠 CORTEX Welcome
**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX

---

Welcome to CORTEX! Before we start, two quick questions to personalize your experience (10 seconds):

### Question 1: Experience Level

How would you describe your development experience?

{experience_choices}

**Your choice (1-4):**"""
        
        return message
    
    def process_experience_choice(self, choice: str) -> Dict[str, Any]:
        """
        Process experience level choice and move to interaction mode question.
        
        Args:
            choice: User's choice (1-4)
        
        Returns:
            Dict with next question or error
        """
        if choice not in self.experience_levels:
            return {
                "status": "error",
                "message": f"Invalid choice '{choice}'. Please enter 1, 2, 3, or 4.",
                "step": "experience_level"
            }
        
        # Store choice temporarily (will be saved after mode selection)
        selected_level = self.experience_levels[choice]
        
        # Build interaction mode choices
        mode_choices = "\n".join([
            f"{key}. {data['label']}" 
            for key, data in self.interaction_modes.items()
        ])
        
        message = f"""### Question 2: Interaction Mode

How do you prefer to work with AI assistants?

{mode_choices}

**Your choice (1-4):**"""
        
        return {
            "status": "awaiting_mode",
            "content": message,
            "experience_level": selected_level["value"],
            "step": "interaction_mode"
        }
    
    def process_mode_choice(
        self,
        choice: str,
        experience_level: str
    ) -> Dict[str, Any]:
        """
        Process interaction mode choice and present Question 3 (tech stack).
        
        Args:
            choice: User's choice (1-4)
            experience_level: Previously selected experience level
        
        Returns:
            Dict with Question 3 or error
        """
        if choice not in self.interaction_modes:
            return {
                "status": "error",
                "message": f"Invalid choice '{choice}'. Please enter 1, 2, 3, or 4.",
                "step": "interaction_mode"
            }
        
        selected_mode = self.interaction_modes[choice]
        
        # Store selections for next step (tech stack)
        self._pending_profile = {
            "interaction_mode": selected_mode["value"],
            "experience_level": experience_level
        }
        
        # Build tech stack choices
        tech_choices = "\n".join([
            f"{key}. {data['label']}" 
            for key, data in self.tech_stack_presets.items()
        ])
        
        # Generate Question 3: Tech Stack Preference
        question_3 = f"""### ✅ Selected: {selected_mode['label']}

## Question 3: Tech Stack Preference (Optional)

**IMPORTANT:** This is context for deployment recommendations, NOT a constraint.  
CORTEX will always recommend the best technical solution first, then show how to deploy with your stack if applicable.

**What's your company/project tech stack?**

{tech_choices}

**Your choice (1-5):**"""
        
        return {
            "status": "awaiting_tech_stack",
            "content": question_3,
            "step": "tech_stack"
        }
    
    def process_tech_stack_choice(
        self,
        choice: str
    ) -> Dict[str, Any]:
        """
        Process tech stack choice and create profile with all selections.
        
        Args:
            choice: User's choice (1-5)
        
        Returns:
            Dict with confirmation message or error
        """
        if choice not in self.tech_stack_presets:
            return {
                "status": "error",
                "message": f"Invalid choice '{choice}'. Please enter 1, 2, 3, 4, or 5.",
                "step": "tech_stack"
            }
        
        selected_preset = self.tech_stack_presets[choice]
        
        # Get pending profile selections (from previous steps)
        if not hasattr(self, '_pending_profile'):
            return {
                "status": "error",
                "message": "Onboarding state lost. Please restart onboarding.",
                "step": "tech_stack"
            }
        
        # Determine tech_stack_preference value
        tech_stack_preference = None
        if selected_preset["value"] and selected_preset["value"] != "custom":
            # Use preset (Azure/AWS/GCP)
            tech_stack_preference = selected_preset.get("preset")
        elif selected_preset["value"] == "custom":
            # User will configure later - store None
            tech_stack_preference = None
        # else: selected_preset["value"] is None (no preference)
        
        if self.tier1:
            success = self.tier1.create_profile(
                interaction_mode=self._pending_profile["interaction_mode"],
                experience_level=self._pending_profile["experience_level"],
                tech_stack_preference=tech_stack_preference
            )
            
            if not success:
                return {
                    "status": "error",
                    "message": "Failed to create profile. Please try again.",
                    "step": "tech_stack"
                }
        
        # Generate confirmation message
        tech_stack_display = selected_preset["label"]
        if tech_stack_preference:
            # Show preset details
            tech_stack_display = f"{selected_preset['label']}\n  - Cloud: {tech_stack_preference['cloud_provider']}\n  - Containers: {tech_stack_preference['container_platform']}\n  - CI/CD: {tech_stack_preference['ci_cd']}\n  - IaC: {tech_stack_preference['iac']}"
        
        # Save values before cleaning up pending state
        saved_interaction_mode = self._pending_profile["interaction_mode"]
        saved_experience_level = self._pending_profile["experience_level"]
        
        confirmation = f"""### ✅ Profile Created

**Experience Level:** {saved_experience_level.capitalize()}  
**Interaction Mode:** {saved_interaction_mode.capitalize()}  
**Tech Stack:** {tech_stack_display}

**Remember:** Tech stack is context for deployment, NOT a constraint.  
CORTEX will always recommend the best solution first.

You can change these anytime with `update profile`.

Now, let's tackle your request!"""
        
        # Clean up pending state
        delattr(self, '_pending_profile')
        
        return {
            "status": "completed",
            "content": confirmation,
            "profile": {
                "interaction_mode": saved_interaction_mode,
                "experience_level": saved_experience_level,
                "tech_stack_preference": tech_stack_preference
            }
        }
    
    def show_update_options(self) -> str:
        """
        Show options for updating existing profile.
        
        Returns:
            Formatted message with update options
        """
        current_profile = self.tier1.get_profile() if self.tier1 else None
        
        if not current_profile:
            return "No profile found. Run onboarding first."
        
        message = f"""## 🧠 CORTEX Profile Update

**Current Profile:**
- Experience: {current_profile['experience_level'].capitalize()}
- Mode: {current_profile['interaction_mode'].capitalize()}

**What would you like to update?**
1. Experience level
2. Interaction mode
3. Tech stack preference
4. All settings

**Your choice (1-4):**"""
        
        return message
    
    def update_experience_level(self, choice: str) -> Dict[str, Any]:
        """
        Update experience level only.
        
        Args:
            choice: User's choice (1-4 from experience_levels)
        
        Returns:
            Dict with update result
        """
        if choice not in self.experience_levels:
            return {
                "status": "error",
                "message": f"Invalid choice '{choice}'. Please enter 1, 2, 3, or 4."
            }
        
        selected_level = self.experience_levels[choice]
        
        if self.tier1:
            success = self.tier1.update_profile(
                experience_level=selected_level["value"]
            )
            
            if success:
                return {
                    "status": "success",
                    "message": f"Experience level updated to: {selected_level['value'].capitalize()}"
                }
            else:
                return {
                    "status": "error",
                    "message": "Failed to update profile."
                }
        
        return {
            "status": "error",
            "message": "Tier 1 API not available."
        }
    
    def update_interaction_mode(self, choice: str) -> Dict[str, Any]:
        """
        Update interaction mode only.
        
        Args:
            choice: User's choice (1-4 from interaction_modes)
        
        Returns:
            Dict with update result
        """
        if choice not in self.interaction_modes:
            return {
                "status": "error",
                "message": f"Invalid choice '{choice}'. Please enter 1, 2, 3, or 4."
            }
        
        selected_mode = self.interaction_modes[choice]
        
        if self.tier1:
            success = self.tier1.update_profile(
                interaction_mode=selected_mode["value"]
            )
            
            if success:
                return {
                    "status": "success",
                    "message": f"Interaction mode updated to: {selected_mode['value'].capitalize()}"
                }
            else:
                return {
                    "status": "error",
                    "message": "Failed to update profile."
                }
        
        return {
            "status": "error",
            "message": "Tier 1 API not available."
        }
    
    def update_tech_stack(self, choice: str) -> Dict[str, Any]:
        """
        Update tech stack preference only.
        
        Args:
            choice: User's choice (1-5 from tech_stack_presets)
        
        Returns:
            Dict with update result
        """
        if choice not in self.tech_stack_presets:
            return {
                "status": "error",
                "message": f"Invalid choice '{choice}'. Please enter 1, 2, 3, 4, or 5."
            }
        
        selected_preset = self.tech_stack_presets[choice]
        
        # Determine tech_stack_preference value
        tech_stack_preference = None
        if selected_preset["value"] and selected_preset["value"] != "custom":
            # Use preset (Azure/AWS/GCP)
            tech_stack_preference = selected_preset.get("preset")
        elif selected_preset["value"] == "custom":
            # User will configure later - store None for now
            tech_stack_preference = None
        # else: selected_preset["value"] is None (no preference)
        
        if self.tier1:
            success = self.tier1.update_profile(
                tech_stack_preference=tech_stack_preference
            )
            
            if success:
                tech_label = selected_preset["label"]
                return {
                    "status": "success",
                    "message": f"Tech stack updated to: {tech_label}\n\n**Remember:** This is context for deployment, NOT a constraint.\nCORTEX will always recommend the best solution first."
                }
            else:
                return {
                    "status": "error",
                    "message": "Failed to update profile."
                }
        
        return {
            "status": "error",
            "message": "Tier 1 API not available."
        }
    
    def show_tech_stack_options(self) -> str:
        """
        Show tech stack update options.
        
        Returns:
            Formatted message with tech stack options
        """
        current_profile = self.tier1.get_profile() if self.tier1 else None
        
        if not current_profile:
            return "No profile found. Run onboarding first."
        
        tech_stack = current_profile.get('tech_stack_preference', None)
        tech_display = "None (CORTEX decides)"
        if tech_stack and isinstance(tech_stack, dict):
            cloud = tech_stack.get('cloud_provider', 'unknown')
            tech_display = f"{cloud.upper()} stack"
        
        # Build tech stack choices
        tech_choices = "\n".join([
            f"{key}. {data['label']}" 
            for key, data in self.tech_stack_presets.items()
        ])
        
        message = f"""## 🧠 CORTEX Tech Stack Update

**Current Tech Stack:** {tech_display}

**IMPORTANT:** Tech stack is context for deployment, NOT a constraint.  
CORTEX will always recommend the best solution first.

**What's your company/project tech stack?**

{tech_choices}

**Your choice (1-5):**"""
        
        return message
    
    def get_profile_summary(self) -> str:
        """
        Get formatted summary of current profile.
        
        Returns:
            Formatted profile summary
        """
        if not self.tier1:
            return "Tier 1 API not available."
        
        profile = self.tier1.get_profile()
        
        if not profile:
            return "No profile found. Run onboarding first."
        
        return f"""## 🧠 CORTEX Profile

**Experience Level:** {profile['experience_level'].capitalize()}  
**Interaction Mode:** {profile['interaction_mode'].capitalize()}  
**Created:** {profile['created_at'][:10]}  
**Last Updated:** {profile['last_updated'][:10]}

**Mode Behavior:**
{self._get_mode_description(profile['interaction_mode'])}

To update: `update profile`"""
    
    def _get_mode_description(self, mode: str) -> str:
        """Get description for interaction mode."""
        descriptions = {
            "autonomous": "- Compact responses with minimal explanation\n- Action-focused, results-first approach\n- Best for experienced users who just want code",
            "guided": "- Full 5-part response structure\n- Balanced understanding + execution\n- Collaborative approach (recommended for most users)",
            "educational": "- Detailed explanations with rationale\n- Shows alternatives and trade-offs\n- Best for learning and understanding why",
            "pair": "- Asks clarifying questions before execution\n- Validates understanding at each step\n- Best for ambiguous requirements"
        }
        
        return descriptions.get(mode, "Unknown mode")
    
    def start_onboarding(self, command: str) -> str:
        """
        Start onboarding process, requiring --app-name parameter.
        
        Args:
            command: User command string (must include --app-name)
        
        Returns:
            Response message confirming onboarding started
        
        Raises:
            ValueError: If --app-name is missing or invalid
        """
        # Extract app name from command
        app_name = self._extract_app_name(command)
        
        if not app_name:
            raise ValueError(
                "--app-name parameter is required for onboarding.\n"
                "Usage: onboard application --app-name <name>\n"
                "Example: onboard application --app-name MyProject"
            )
        
        # Validate app name
        if not self._validate_app_name(app_name):
            raise ValueError(
                f"Invalid application name '{app_name}'. "
                "Application name must be at least 3 characters long."
            )
        
        # Store application name in Tier 1
        self.working_memory.store_application_name(app_name)
        
        # Return confirmation
        return f"Onboarding started for application '{app_name}'. Profile configuration in progress..."
    
    def _extract_app_name(self, command: str) -> Optional[str]:
        """
        Extract application name from command string.
        
        Args:
            command: Command string potentially containing --app-name
        
        Returns:
            Extracted app name or None if not found
        
        Raises:
            ValueError: If multiple --app-name parameters provided
        """
        # Pattern matches: --app-name value, --app-name 'value', --app-name "value"
        pattern = r'--app-name\s+(?:(["\'](.*?)["\'])|(\S+))'
        matches = list(re.finditer(pattern, command))
        
        if not matches:
            return None
        
        if len(matches) > 1:
            raise ValueError(
                "Multiple --app-name parameters detected. Please provide only one application name."
            )
        
        # Extract from match groups (quoted or unquoted)
        match = matches[0]
        groups = match.groups()
        app_name = groups[1] if groups[1] else groups[2]
        
        return app_name.strip() if app_name else None
    
    def _validate_app_name(self, name: str) -> bool:
        """
        Validate application name meets requirements.
        
        Args:
            name: Application name to validate
        
        Returns:
            True if valid, False otherwise
        """
        if not name or not name.strip():
            return False
        
        # Must be at least 3 characters (excluding whitespace)
        if len(name.strip()) < 3:
            return False
        
        return True
    
    def get_application_name(self) -> Optional[str]:
        """
        Get the stored application name from Tier 1.
        
        Returns:
            Application name or None if not set
        """
        return self.working_memory.get_application_name()
    
    def update_application_name(self, new_name: str) -> bool:
        """
        Update the application name after initial onboarding.
        
        Args:
            new_name: New application name
        
        Returns:
            True if updated successfully, False otherwise
        """
        if not self._validate_app_name(new_name):
            return False
        
        self.working_memory.store_application_name(new_name)
        return True
    
    def generate_welcome_message(self) -> str:
        """
        Generate personalized welcome message using stored application name.
        
        Returns:
            Welcome message with application name
        """
        app_name = self.get_application_name()
        
        if app_name:
            return (
                f"Welcome to CORTEX! I'm ready to assist with {app_name}.\n"
                f"I'll help you build, test, and deploy features for {app_name} "
                "with AI-powered intelligence."
            )
        else:
            return (
                "Welcome to CORTEX! I'm ready to assist with your project.\n"
                "I'll help you build, test, and deploy features with AI-powered intelligence."
            )


# Convenience function for CLI/API usage
def run_onboarding(tier1_api=None) -> Dict[str, Any]:
    """
    Run onboarding flow (convenience function).
    
    Args:
        tier1_api: Tier 1 API instance
    
    Returns:
        Onboarding result
    """
    orchestrator = OnboardingOrchestrator(tier1_api)
    return orchestrator.start_onboarding("User initiated onboarding")
