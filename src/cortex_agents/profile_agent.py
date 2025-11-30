"""
ProfileAgent - User Profile Update Handler

Handles user profile updates including interaction mode, experience level,
and tech stack preferences. Routes profile update requests to UserProfileManager.

CORTEX 3.2.1 Phase 1: User Profile System Enhancements
"""

from typing import Optional, Dict, Any
import re

from src.cortex_agents.base_agent import BaseAgent, AgentRequest, AgentResponse
from src.cortex_agents.agent_types import IntentType
from src.tier1.user_profile_manager import UserProfileManager, TechStackPreset


class ProfileAgent(BaseAgent):
    """
    Agent for handling user profile updates.
    
    Recognizes profile update intents and routes to UserProfileManager.
    Supports:
    - Tech stack preference updates (Azure/AWS/GCP/No Preference/Custom)
    - Interaction mode changes (autonomous/guided/educational/pair)
    - Experience level updates (junior/mid/senior/expert)
    - Multiple field updates in single request
    """
    
    def __init__(self, name: str = "ProfileAgent", db_path: Optional[str] = None, 
                 tier1_api=None, tier2_kg=None, tier3_context=None):
        """
        Initialize ProfileAgent.
        
        Args:
            name: Agent name
            db_path: Path to database (used for UserProfileManager)
            tier1_api: Tier 1 API (optional)
            tier2_kg: Tier 2 knowledge graph (optional)
            tier3_context: Tier 3 context (optional)
        """
        super().__init__(name, tier1_api, tier2_kg, tier3_context)
        self.profile_manager = UserProfileManager(db_path if db_path else None)
        
        # Keyword mappings for natural language parsing
        self.tech_stack_keywords = {
            "azure": TechStackPreset.AZURE_STACK,
            "aws": TechStackPreset.AWS_STACK,
            "gcp": TechStackPreset.GCP_STACK,
            "google": TechStackPreset.GCP_STACK,
            "no preference": TechStackPreset.NO_PREFERENCE,
            "none": TechStackPreset.NO_PREFERENCE,
            "custom": TechStackPreset.CUSTOM
        }
        
        self.interaction_modes = ["autonomous", "guided", "educational", "pair"]
        self.experience_levels = ["junior", "mid", "senior", "expert"]
    
    def can_handle(self, request: AgentRequest) -> bool:
        """
        Check if this agent can handle the request.
        
        Args:
            request: Agent request
            
        Returns:
            True if intent is UPDATE_PROFILE, False otherwise
        """
        return request.intent == IntentType.UPDATE_PROFILE
    
    def execute(self, request: AgentRequest) -> AgentResponse:
        """
        Execute profile update request.
        
        Args:
            request: Agent request with user message containing profile updates
            
        Returns:
            AgentResponse with success status and updated profile info
        """
        self.log_request(request)
        
        try:
            user_message = request.user_message.lower()
            
            # Parse user message to extract update fields
            updates = self._parse_update_request(user_message)
            
            if not updates:
                return AgentResponse(
                    success=False,
                    result={},
                    message="Could not identify what to update. Please specify: tech stack, mode, or experience level.",
                    agent_name=self.name
                )
            
            # Apply updates
            success = True
            result = {}
            
            # Handle tech stack update
            if "tech_stack" in updates:
                tech_stack = updates["tech_stack"]
                
                if tech_stack == "custom" and "tech_stack_config" in updates:
                    success = self.profile_manager.set_tech_stack_custom(updates["tech_stack_config"])
                    result["tech_stack"] = "custom"
                    result["tech_stack_config"] = updates["tech_stack_config"]
                else:
                    preset = self.tech_stack_keywords.get(tech_stack)
                    if preset:
                        success = self.profile_manager.set_tech_stack_preset(preset)
                        result["tech_stack"] = tech_stack + "_stack" if tech_stack != "no preference" else "no_preference"
            
            # Handle interaction mode and experience level
            update_fields = {}
            if "interaction_mode" in updates:
                update_fields["interaction_mode"] = updates["interaction_mode"]
                result["interaction_mode"] = updates["interaction_mode"]
            
            if "experience_level" in updates:
                update_fields["experience_level"] = updates["experience_level"]
                result["experience_level"] = updates["experience_level"]
            
            if update_fields:
                # Use WorkingMemory's update_profile if we're updating mode/experience
                # (UserProfileManager wraps this)
                from src.tier1.working_memory import WorkingMemory
                wm = WorkingMemory(self.profile_manager.db_path)
                success = success and wm.update_profile(**update_fields)
            
            if success:
                # Get updated profile
                profile = self.profile_manager.get_profile()
                
                message = self._format_success_message(result, profile)
                
                return AgentResponse(
                    success=True,
                    result=result,
                    message=message,
                    agent_name=self.name,
                    metadata={"profile": profile}
                )
            else:
                return AgentResponse(
                    success=False,
                    result=result,
                    message="Failed to update profile. Please check your input values.",
                    agent_name=self.name
                )
        
        except ValueError as e:
            # Validation error
            return AgentResponse(
                success=False,
                result={},
                message=f"Invalid profile value: {str(e)}",
                agent_name=self.name
            )
        
        except Exception as e:
            self.logger.error(f"Profile update failed: {str(e)}")
            return AgentResponse(
                success=False,
                result={},
                message=f"Profile update error: {str(e)}",
                agent_name=self.name
            )
    
    def _parse_update_request(self, user_message: str) -> Dict[str, Any]:
        """
        Parse user message to extract profile update fields.
        
        Args:
            user_message: User's natural language update request
            
        Returns:
            Dict with fields to update
        """
        updates = {}
        
        # Check for "custom tech stack:" pattern FIRST (highest priority)
        if "custom tech stack:" in user_message or "custom tech stack " in user_message:
            config = self._parse_custom_tech_stack(user_message)
            if config:
                updates["tech_stack"] = "custom"
                updates["tech_stack_config"] = config
        
        # Parse structured format (e.g., "mode=guided, experience=expert, tech_stack=aws")
        # Use word boundaries to avoid matching partial words
        if "interaction_mode" not in updates:
            structured_match = re.search(r"\bmode[=:]\s*(\w+)", user_message)
            if structured_match:
                mode_value = structured_match.group(1)
                if mode_value in self.interaction_modes:
                    updates["interaction_mode"] = mode_value
        
        if "experience_level" not in updates:
            structured_match = re.search(r"\bexperience[=:]\s*(\w+)", user_message)
            if structured_match:
                exp_value = structured_match.group(1)
                if exp_value in self.experience_levels:
                    updates["experience_level"] = exp_value
        
        if "tech_stack" not in updates:
            structured_match = re.search(r"\btech[_\s-]?stack[=:]\s*(\w+)", user_message)
            if structured_match:
                tech_value = structured_match.group(1)
                if tech_value in ["azure", "aws", "gcp", "custom", "none"]:
                    if tech_value == "none":
                        updates["tech_stack"] = "no preference"
                    else:
                        updates["tech_stack"] = tech_value
        
        # Check for tech stack keywords (if not already found)
        if "tech_stack" not in updates:
            # Special handling for "no preference" (two words)
            if "no preference" in user_message or "no tech preference" in user_message:
                updates["tech_stack"] = "no preference"
            else:
                # Check single-word tech stack keywords (but skip "custom" since we checked that above)
                for keyword, preset in self.tech_stack_keywords.items():
                    if keyword in ["no preference", "custom"]:  # Skip - already handled
                        continue
                    if keyword in user_message:
                        updates["tech_stack"] = keyword
                        break
        
        # Check for interaction mode (if not already found)
        if "interaction_mode" not in updates:
            # Match pattern "to [mode]" or "mode to [mode]" or just "[mode]"
            for mode in self.interaction_modes:
                # Look for "to <mode>" or "mode to <mode>" or "<mode> mode" or just "<mode>"
                pattern = rf"\b(?:(?:mode|change)\s+to\s+)?{mode}(?:\s+mode)?\b"
                if re.search(pattern, user_message):
                    updates["interaction_mode"] = mode
                    break
            
            # If still not found, check for invalid mode patterns
            if "interaction_mode" not in updates:
                invalid_match = re.search(r"\b(?:mode|change)\s+to\s+(\w+)", user_message)
                if invalid_match:
                    # Found a mode change request but mode not in valid list
                    updates["interaction_mode"] = invalid_match.group(1)  # Will be rejected in execute()
        
        # Check for experience level (if not already found)
        if "experience_level" not in updates:
            # Match pattern "to [level]" or "experience to [level]" or just "[level]"
            for level in self.experience_levels:
                # Look for "to <level>" or "experience to <level>" or "<level> level" or just "<level>"
                pattern = rf"\b(?:(?:experience|update|change)\s+to\s+)?{level}(?:\s+(?:level|developer|engineer))?\b"
                if re.search(pattern, user_message):
                    updates["experience_level"] = level
                    break
            
            # If still not found, check for invalid level patterns
            if "experience_level" not in updates:
                invalid_match = re.search(r"\b(?:experience|update|change)\s+to\s+(\w+)", user_message)
                if invalid_match and invalid_match.group(1) not in self.experience_levels:
                    # Found an experience change request but level not in valid list
                    updates["experience_level"] = invalid_match.group(1)  # Will be rejected in execute()
        
        return updates
    
    def _parse_custom_tech_stack(self, user_message: str) -> Optional[Dict[str, str]]:
        """
        Parse custom tech stack configuration from user message.
        
        Args:
            user_message: User message with custom tech stack
            
        Returns:
            Dict with custom configuration or None
        """
        config = {}
        
        # Cloud provider patterns
        if "azure" in user_message and "cloud" in user_message:
            config["cloud_provider"] = "azure"
        elif "aws" in user_message and "cloud" in user_message:
            config["cloud_provider"] = "aws"
        elif "gcp" in user_message or "google" in user_message:
            config["cloud_provider"] = "gcp"
        
        # Container platform patterns
        if "docker" in user_message:
            config["container_platform"] = "docker"
        elif "kubernetes" in user_message or "k8s" in user_message:
            config["container_platform"] = "kubernetes"
        elif "aks" in user_message:
            config["container_platform"] = "aks"
        elif "eks" in user_message:
            config["container_platform"] = "eks"
        elif "gke" in user_message:
            config["container_platform"] = "gke"
        
        # CI/CD patterns
        if "jenkins" in user_message:
            config["ci_cd"] = "jenkins"
        elif "github actions" in user_message:
            config["ci_cd"] = "github_actions"
        elif "azure devops" in user_message:
            config["ci_cd"] = "azure_devops"
        elif "cloud build" in user_message:
            config["ci_cd"] = "cloud_build"
        
        # IaC patterns
        if "terraform" in user_message:
            config["iac"] = "terraform"
        elif "arm" in user_message and ("template" in user_message or "iac" in user_message):
            config["iac"] = "arm"
        elif "cloudformation" in user_message:
            config["iac"] = "cloudformation"
        
        # Architecture
        if "microservice" in user_message:
            config["architecture"] = "microservices"
        elif "monolithic" in user_message:
            config["architecture"] = "monolithic"
        elif "hybrid" in user_message:
            config["architecture"] = "hybrid"
        
        return config if config else None
    
    def _format_success_message(self, updates: Dict[str, Any], profile: Dict[str, Any]) -> str:
        """
        Format success message with update details.
        
        Args:
            updates: Fields that were updated
            profile: Current profile after updates
            
        Returns:
            Formatted success message
        """
        messages = ["✅ Profile updated successfully:"]
        
        if "tech_stack" in updates:
            tech_stack = updates["tech_stack"]
            if tech_stack == "custom":
                messages.append(f"  - Tech Stack: Custom ({', '.join(updates['tech_stack_config'].keys())})")
            elif tech_stack == "no preference":
                messages.append("  - Tech Stack: No Preference (CORTEX will recommend best practices)")
            else:
                messages.append(f"  - Tech Stack: {tech_stack.upper()} Stack")
        
        if "interaction_mode" in updates:
            messages.append(f"  - Interaction Mode: {updates['interaction_mode'].title()}")
        
        if "experience_level" in updates:
            messages.append(f"  - Experience Level: {updates['experience_level'].title()}")
        
        messages.append("")
        messages.append("💡 Your preferences will be applied to all future CORTEX responses.")
        
        return "\n".join(messages)
