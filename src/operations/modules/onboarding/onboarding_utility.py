"""
Onboarding Utility

Lightweight user profile management for CORTEX onboarding.
Replaces heavy orchestrator (843 lines) with focused utility (~350 lines).

Core Operations:
- Create user profile
- Load existing profile
- Update profile preferences
- Interactive onboarding survey
- Profile validation

Version: 3.0.0 (Utility Migration)
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import CORTEX config
try:
    from src.config import config
    CORTEX_ROOT = Path(config.root_path)
except ImportError:
    CORTEX_ROOT = Path(__file__).resolve().parents[4]


# ===== DATACLASSES =====

@dataclass
class UserProfile:
    """User profile with preferences."""
    user_id: str
    experience_level: str  # junior, mid, senior, expert
    interaction_mode: str  # autonomous, guided, educational, pair
    tech_stack: Optional[str] = None  # azure, aws, gcp, custom, none
    created_at: str = ""
    updated_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = datetime.now().isoformat()


@dataclass
class ProfileResult:
    """Result of profile operation."""
    success: bool
    message: str
    profile: Optional[UserProfile] = None
    errors: list = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []


# ===== CONSTANTS =====

EXPERIENCE_LEVELS = {
    "junior": "Learning the ropes, need guidance",
    "mid": "Solid fundamentals, occasional help needed",
    "senior": "Experienced, confident in most areas",
    "expert": "Deep expertise, minimal hand-holding"
}

INTERACTION_MODES = {
    "autonomous": "Just do it, show me results",
    "guided": "Explain what you're doing (recommended)",
    "educational": "Teach me why and show alternatives",
    "pair": "Ask clarifying questions first"
}

TECH_STACKS = {
    "azure": "Azure DevOps, AKS, ARM/Terraform",
    "aws": "ECS/EKS, CodePipeline, CloudFormation/Terraform",
    "gcp": "GKE, Cloud Build, Terraform",
    "custom": "Custom configuration",
    "none": "No preference"
}


# ===== HELPER FUNCTIONS =====

def _get_profile_path(user_id: str) -> Path:
    """Get path to user profile file."""
    profile_dir = CORTEX_ROOT / "cortex-brain" / "profiles"
    profile_dir.mkdir(parents=True, exist_ok=True)
    return profile_dir / f"{user_id}.json"


def _validate_experience(level: str) -> bool:
    """Validate experience level."""
    return level in EXPERIENCE_LEVELS


def _validate_mode(mode: str) -> bool:
    """Validate interaction mode."""
    return mode in INTERACTION_MODES


def _validate_tech_stack(stack: Optional[str]) -> bool:
    """Validate tech stack."""
    return stack is None or stack in TECH_STACKS


# ===== CORE OPERATION 1: CREATE PROFILE =====

def create_profile(
    user_id: str,
    experience_level: str,
    interaction_mode: str,
    tech_stack: Optional[str] = None
) -> ProfileResult:
    """
    Create new user profile.
    
    Args:
        user_id: User identifier
        experience_level: junior, mid, senior, expert
        interaction_mode: autonomous, guided, educational, pair
        tech_stack: azure, aws, gcp, custom, none (optional)
        
    Returns:
        ProfileResult with creation outcome
    """
    logger.info(f"👤 Creating profile for user: {user_id}")
    
    # Validate inputs
    errors = []
    if not _validate_experience(experience_level):
        errors.append(f"Invalid experience level: {experience_level}")
    if not _validate_mode(interaction_mode):
        errors.append(f"Invalid interaction mode: {interaction_mode}")
    if not _validate_tech_stack(tech_stack):
        errors.append(f"Invalid tech stack: {tech_stack}")
    
    if errors:
        return ProfileResult(
            success=False,
            message="Validation failed",
            errors=errors
        )
    
    try:
        # Create profile
        profile = UserProfile(
            user_id=user_id,
            experience_level=experience_level,
            interaction_mode=interaction_mode,
            tech_stack=tech_stack or "none"
        )
        
        # Save to file
        profile_path = _get_profile_path(user_id)
        with open(profile_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(profile), f, indent=2)
        
        return ProfileResult(
            success=True,
            message=f"Profile created for {user_id}",
            profile=profile
        )
        
    except Exception as e:
        return ProfileResult(
            success=False,
            message=f"Failed to create profile: {str(e)}",
            errors=[str(e)]
        )


# ===== CORE OPERATION 2: LOAD PROFILE =====

def load_profile(user_id: str) -> ProfileResult:
    """
    Load existing user profile.
    
    Args:
        user_id: User identifier
        
    Returns:
        ProfileResult with loaded profile
    """
    logger.info(f"📂 Loading profile for user: {user_id}")
    
    try:
        profile_path = _get_profile_path(user_id)
        
        if not profile_path.exists():
            return ProfileResult(
                success=False,
                message=f"Profile not found for user: {user_id}",
                errors=[f"No profile file at {profile_path}"]
            )
        
        # Load profile
        with open(profile_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        profile = UserProfile(**data)
        
        return ProfileResult(
            success=True,
            message=f"Profile loaded for {user_id}",
            profile=profile
        )
        
    except Exception as e:
        return ProfileResult(
            success=False,
            message=f"Failed to load profile: {str(e)}",
            errors=[str(e)]
        )


# ===== CORE OPERATION 3: UPDATE PROFILE =====

def update_profile(
    user_id: str,
    experience_level: Optional[str] = None,
    interaction_mode: Optional[str] = None,
    tech_stack: Optional[str] = None
) -> ProfileResult:
    """
    Update existing user profile.
    
    Args:
        user_id: User identifier
        experience_level: New experience level (optional)
        interaction_mode: New interaction mode (optional)
        tech_stack: New tech stack (optional)
        
    Returns:
        ProfileResult with update outcome
    """
    logger.info(f"✏️  Updating profile for user: {user_id}")
    
    # Load existing profile
    load_result = load_profile(user_id)
    if not load_result.success:
        return load_result
    
    profile = load_result.profile
    
    # Validate updates
    errors = []
    if experience_level and not _validate_experience(experience_level):
        errors.append(f"Invalid experience level: {experience_level}")
    if interaction_mode and not _validate_mode(interaction_mode):
        errors.append(f"Invalid interaction mode: {interaction_mode}")
    if tech_stack and not _validate_tech_stack(tech_stack):
        errors.append(f"Invalid tech stack: {tech_stack}")
    
    if errors:
        return ProfileResult(
            success=False,
            message="Validation failed",
            errors=errors
        )
    
    try:
        # Update fields
        if experience_level:
            profile.experience_level = experience_level
        if interaction_mode:
            profile.interaction_mode = interaction_mode
        if tech_stack:
            profile.tech_stack = tech_stack
        
        profile.updated_at = datetime.now().isoformat()
        
        # Save updated profile
        profile_path = _get_profile_path(user_id)
        with open(profile_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(profile), f, indent=2)
        
        return ProfileResult(
            success=True,
            message=f"Profile updated for {user_id}",
            profile=profile
        )
        
    except Exception as e:
        return ProfileResult(
            success=False,
            message=f"Failed to update profile: {str(e)}",
            errors=[str(e)]
        )


# ===== CORE OPERATION 4: RUN ONBOARDING =====

def run_onboarding(user_id: str) -> ProfileResult:
    """
    Run interactive onboarding survey (simplified for testing).
    In production, this would be interactive CLI.
    
    Args:
        user_id: User identifier
        
    Returns:
        ProfileResult with survey outcome
    """
    logger.info(f"🎓 Starting onboarding for user: {user_id}")
    
    try:
        # In real implementation, this would present interactive prompts
        # For testing, we'll create a default profile
        
        print("\n" + "=" * 60)
        print("CORTEX Onboarding Survey")
        print("=" * 60)
        print("\nWelcome! Let's personalize your CORTEX experience.\n")
        
        print("Experience Levels:")
        for level, desc in EXPERIENCE_LEVELS.items():
            print(f"  {level}: {desc}")
        
        print("\nInteraction Modes:")
        for mode, desc in INTERACTION_MODES.items():
            print(f"  {mode}: {desc}")
        
        print("\nTech Stacks:")
        for stack, desc in TECH_STACKS.items():
            print(f"  {stack}: {desc}")
        
        # For testing, create default guided/mid profile
        profile = UserProfile(
            user_id=user_id,
            experience_level="mid",
            interaction_mode="guided",
            tech_stack="none"
        )
        
        # Save profile
        profile_path = _get_profile_path(user_id)
        with open(profile_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(profile), f, indent=2)
        
        print(f"\n✅ Profile created for {user_id}")
        print(f"   Experience: {profile.experience_level}")
        print(f"   Mode: {profile.interaction_mode}")
        print(f"   Tech Stack: {profile.tech_stack}\n")
        
        return ProfileResult(
            success=True,
            message=f"Onboarding complete for {user_id}",
            profile=profile
        )
        
    except Exception as e:
        return ProfileResult(
            success=False,
            message=f"Onboarding failed: {str(e)}",
            errors=[str(e)]
        )


# ===== CORE OPERATION 5: VALIDATE PROFILE =====

def validate_profile(user_id: str) -> ProfileResult:
    """
    Validate user profile completeness.
    
    Args:
        user_id: User identifier
        
    Returns:
        ProfileResult with validation outcome
    """
    logger.info(f"✓ Validating profile for user: {user_id}")
    
    # Load profile
    load_result = load_profile(user_id)
    if not load_result.success:
        return load_result
    
    profile = load_result.profile
    
    # Check required fields
    issues = []
    if not profile.experience_level or profile.experience_level not in EXPERIENCE_LEVELS:
        issues.append("Invalid or missing experience level")
    if not profile.interaction_mode or profile.interaction_mode not in INTERACTION_MODES:
        issues.append("Invalid or missing interaction mode")
    if profile.tech_stack and profile.tech_stack not in TECH_STACKS:
        issues.append("Invalid tech stack")
    
    if issues:
        return ProfileResult(
            success=False,
            message="Profile validation failed",
            profile=profile,
            errors=issues
        )
    
    return ProfileResult(
        success=True,
        message=f"Profile valid for {user_id}",
        profile=profile
    )


# ===== CLI TEST EXECUTION =====

if __name__ == "__main__":
    print("=" * 60)
    print("Onboarding Utility - Direct Test")
    print("=" * 60)
    
    test_user = "test_user_123"
    
    # Test 1: Create profile
    print("\n[Test 1] Create profile...")
    result = create_profile(
        user_id=test_user,
        experience_level="mid",
        interaction_mode="guided",
        tech_stack="azure"
    )
    print(f"Success: {result.success}")
    print(f"Message: {result.message}")
    if result.profile:
        print(f"Profile: {result.profile.user_id} - {result.profile.experience_level}/{result.profile.interaction_mode}")
    
    # Test 2: Load profile
    print("\n" + "=" * 60)
    print("[Test 2] Load profile...")
    result = load_profile(test_user)
    print(f"Success: {result.success}")
    print(f"Message: {result.message}")
    if result.profile:
        print(f"Loaded: {result.profile.experience_level}/{result.profile.interaction_mode}/{result.profile.tech_stack}")
    
    # Test 3: Update profile
    print("\n" + "=" * 60)
    print("[Test 3] Update profile...")
    result = update_profile(
        user_id=test_user,
        experience_level="senior",
        tech_stack="aws"
    )
    print(f"Success: {result.success}")
    print(f"Message: {result.message}")
    if result.profile:
        print(f"Updated: {result.profile.experience_level}/{result.profile.tech_stack}")
    
    # Test 4: Validate profile
    print("\n" + "=" * 60)
    print("[Test 4] Validate profile...")
    result = validate_profile(test_user)
    print(f"Success: {result.success}")
    print(f"Message: {result.message}")
    
    # Cleanup
    print("\n" + "=" * 60)
    print("[Cleanup] Removing test profile...")
    profile_path = _get_profile_path(test_user)
    if profile_path.exists():
        profile_path.unlink()
        print("✅ Test profile removed")
    
    print("\n" + "=" * 60)
    print("✅ Utility tests complete")
    print("=" * 60)
