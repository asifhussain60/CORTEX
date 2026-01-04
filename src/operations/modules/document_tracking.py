"""
Document Tracking Configuration Module

Manages user-configurable document tracking with whitelist/blacklist enforcement.
Ensures CORTEX brain and core files are NEVER trackable while allowing users
to selectively track planning documents, reports, and documentation.

SKULL Rules Enforced:
- GIT_ISOLATION_ENFORCEMENT: Brain/core always isolated
- USER_DOCUMENT_SELECTIVE_TRACKING: Safe user documents can be whitelisted

Author: Asif Hussain
Copyright © 2026 Asif Hussain. All rights reserved.
"""

import json
import fnmatch
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from enum import Enum


class TrackingMode(Enum):
    """Document tracking modes."""
    DISABLED = "disabled"
    WHITELIST = "whitelist"
    BLACKLIST = "blacklist"  # Not recommended, kept for completeness


class Severity(Enum):
    """Validation severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class ValidationViolation:
    """Represents a configuration validation violation."""
    pattern: str
    reason: str
    severity: Severity
    suggestion: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of configuration validation."""
    valid: bool
    violations: List[ValidationViolation] = None
    message: str = ""
    
    def __post_init__(self):
        if self.violations is None:
            self.violations = []


class DocumentTrackingConfig:
    """
    Manages document tracking configuration with safety enforcement.
    
    Ensures CORTEX brain and core files can NEVER be whitelisted,
    while allowing users to selectively track safe document types.
    """
    
    # PROTECTED PATTERNS - These can NEVER be tracked
    PROTECTED_PATTERNS = [
        "CORTEX/**",
        "cortex-brain/**",
        "src/**",
        "tests/**",
        "*.cortex-session.*",
        "*.cortex-state.*",
        ".cortex/config.json",
        ".cortex/sessions/**",
        ".cortex/.secrets/**",
    ]
    
    # SAFE USER PATTERNS - These CAN be whitelisted
    SAFE_USER_PATTERNS = [
        ".cortex/planning/**/*.md",
        ".cortex/planning/**/*.yaml",
        ".cortex/reports/**/*.md",
        ".cortex/reports/**/*.html",
        ".cortex/docs/**/*.md",
    ]
    
    # DEFAULT CONFIGURATION
    DEFAULT_CONFIG = {
        "version": "5.0",
        "user_preferences": {
            "document_tracking": {
                "enabled": False,
                "mode": "whitelist",
                "whitelist": {
                    "planning": {
                        "enabled": False,
                        "patterns": [
                            ".cortex/planning/**/*.md",
                            ".cortex/planning/**/*.yaml"
                        ],
                        "exclude_active": False,
                        "exclude_private": True
                    },
                    "reports": {
                        "enabled": False,
                        "patterns": [
                            ".cortex/reports/**/*.md",
                            ".cortex/reports/**/*.html"
                        ]
                    },
                    "documentation": {
                        "enabled": False,
                        "patterns": [
                            ".cortex/docs/**/*.md"
                        ]
                    }
                }
            },
            "sharing": {
                "team_plans": False,
                "public_docs": False,
                "sanitize_before_commit": True
            }
        },
        "brain_protection": {
            "enforce_isolation": True,
            "strict_mode": True,
            "never_track": [
                "CORTEX/**",
                "cortex-brain/**",
                ".cortex/config.json",
                ".cortex/sessions/**",
                ".cortex/.secrets/**",
                "*.cortex-session.*",
                "*.cortex-state.*"
            ],
            "validation": {
                "pre_commit_scan": True,
                "block_on_violation": True,
                "alert_user": True
            }
        },
        "safety": {
            "backup_before_migration": True,
            "rollback_enabled": True,
            "audit_log": ".cortex/.audit.log"
        }
    }
    
    def __init__(self, repo_path: Path):
        """
        Initialize document tracking configuration.
        
        Args:
            repo_path: Path to repository root
        """
        self.repo_path = repo_path
        self.config_path = repo_path / ".cortex" / "config.json"
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Load configuration from file or create default."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid config.json: {e}")
        else:
            # Create default config
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            self._save_config(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG.copy()
    
    def _save_config(self, config: Dict):
        """Save configuration to file."""
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
    
    def validate(self) -> ValidationResult:
        """
        Validate configuration for safety violations.
        
        Returns:
            ValidationResult with any violations found
        """
        violations = []
        
        # Get user whitelist patterns
        whitelist_config = self.config.get("user_preferences", {}).get(
            "document_tracking", {}
        ).get("whitelist", {})
        
        user_patterns = []
        for category, settings in whitelist_config.items():
            if isinstance(settings, dict) and settings.get("enabled"):
                user_patterns.extend(settings.get("patterns", []))
        
        # Check each user pattern against protected patterns
        for user_pattern in user_patterns:
            if self._matches_protected(user_pattern):
                violations.append(ValidationViolation(
                    pattern=user_pattern,
                    reason="Matches protected CORTEX brain/core pattern",
                    severity=Severity.CRITICAL,
                    suggestion="Remove this pattern from whitelist"
                ))
            elif not self._is_safe_pattern(user_pattern):
                violations.append(ValidationViolation(
                    pattern=user_pattern,
                    reason="Pattern not in approved safe list",
                    severity=Severity.WARNING,
                    suggestion=f"Use one of: {', '.join(self.SAFE_USER_PATTERNS)}"
                ))
        
        if violations:
            critical = [v for v in violations if v.severity == Severity.CRITICAL]
            if critical:
                return ValidationResult(
                    valid=False,
                    violations=violations,
                    message=f"Configuration violates GIT_ISOLATION_ENFORCEMENT "
                            f"({len(critical)} critical violations)"
                )
        
        return ValidationResult(valid=True, message="Configuration is safe")
    
    def _matches_protected(self, user_pattern: str) -> bool:
        """
        Check if user pattern overlaps with protected patterns.
        
        Args:
            user_pattern: User-specified pattern to check
            
        Returns:
            True if pattern matches any protected pattern
        """
        for protected in self.PROTECTED_PATTERNS:
            # Check both directions for overlap
            if self._patterns_overlap(user_pattern, protected):
                return True
        return False
    
    def _patterns_overlap(self, pattern1: str, pattern2: str) -> bool:
        """Check if two glob patterns overlap."""
        # Simple heuristic: check if one is a prefix of the other
        # or if they share common path segments
        
        # Normalize patterns
        p1 = pattern1.rstrip('*').rstrip('/')
        p2 = pattern2.rstrip('*').rstrip('/')
        
        # Check prefix overlap
        if p1.startswith(p2) or p2.startswith(p1):
            return True
        
        # Check if patterns would match the same files
        # (More sophisticated overlap detection could be added)
        return False
    
    def _is_safe_pattern(self, pattern: str) -> bool:
        """Check if pattern is in approved safe list."""
        for safe_pattern in self.SAFE_USER_PATTERNS:
            if fnmatch.fnmatch(pattern, safe_pattern):
                return True
        return False
    
    def get_trackable_patterns(self) -> List[str]:
        """
        Get list of patterns that should be trackable based on config.
        
        Returns:
            List of file patterns that can be tracked in git
        """
        if not self.config.get("user_preferences", {}).get(
            "document_tracking", {}
        ).get("enabled"):
            return []
        
        patterns = []
        whitelist_config = self.config.get("user_preferences", {}).get(
            "document_tracking", {}
        ).get("whitelist", {})
        
        for category, settings in whitelist_config.items():
            if isinstance(settings, dict) and settings.get("enabled"):
                patterns.extend(settings.get("patterns", []))
        
        return patterns
    
    def get_protected_patterns(self) -> List[str]:
        """
        Get list of patterns that are ALWAYS protected.
        
        Returns:
            List of patterns that can never be tracked
        """
        return self.config.get("brain_protection", {}).get(
            "never_track", self.PROTECTED_PATTERNS
        )
    
    def is_file_trackable(self, file_path: str) -> bool:
        """
        Check if a specific file can be tracked based on configuration.
        
        Args:
            file_path: Relative path to file from repo root
            
        Returns:
            True if file can be tracked, False if protected
        """
        # ALWAYS protect brain/core files
        for protected_pattern in self.get_protected_patterns():
            if fnmatch.fnmatch(file_path, protected_pattern):
                return False
        
        # If tracking disabled, nothing is trackable
        if not self.config.get("user_preferences", {}).get(
            "document_tracking", {}
        ).get("enabled"):
            return False
        
        # Check if file matches whitelisted patterns
        trackable_patterns = self.get_trackable_patterns()
        for pattern in trackable_patterns:
            if fnmatch.fnmatch(file_path, pattern):
                return True
        
        return False
    
    def enable_tracking(self, category: str) -> ValidationResult:
        """
        Enable tracking for a specific category.
        
        Args:
            category: Category to enable ('planning', 'reports', 'documentation')
            
        Returns:
            ValidationResult indicating success or failure
        """
        valid_categories = ['planning', 'reports', 'documentation']
        if category not in valid_categories:
            return ValidationResult(
                valid=False,
                message=f"Invalid category. Must be one of: {', '.join(valid_categories)}"
            )
        
        # Update config
        if "user_preferences" not in self.config:
            self.config["user_preferences"] = {}
        if "document_tracking" not in self.config["user_preferences"]:
            self.config["user_preferences"]["document_tracking"] = {}
        if "whitelist" not in self.config["user_preferences"]["document_tracking"]:
            self.config["user_preferences"]["document_tracking"]["whitelist"] = {}
        
        whitelist = self.config["user_preferences"]["document_tracking"]["whitelist"]
        
        if category not in whitelist:
            # Initialize with safe defaults
            whitelist[category] = self.DEFAULT_CONFIG["user_preferences"][
                "document_tracking"]["whitelist"][category].copy()
        
        whitelist[category]["enabled"] = True
        self.config["user_preferences"]["document_tracking"]["enabled"] = True
        
        # Validate before saving
        validation = self.validate()
        if not validation.valid:
            return validation
        
        # Save config
        self._save_config(self.config)
        
        return ValidationResult(
            valid=True,
            message=f"Tracking enabled for category: {category}"
        )
    
    def disable_tracking(self, category: Optional[str] = None) -> ValidationResult:
        """
        Disable tracking for a category or entirely.
        
        Args:
            category: Category to disable, or None to disable all tracking
            
        Returns:
            ValidationResult indicating success
        """
        if category is None:
            # Disable all tracking
            if "user_preferences" in self.config:
                if "document_tracking" in self.config["user_preferences"]:
                    self.config["user_preferences"]["document_tracking"]["enabled"] = False
            
            self._save_config(self.config)
            return ValidationResult(valid=True, message="All tracking disabled")
        
        # Disable specific category
        whitelist = self.config.get("user_preferences", {}).get(
            "document_tracking", {}
        ).get("whitelist", {})
        
        if category in whitelist:
            whitelist[category]["enabled"] = False
        
        self._save_config(self.config)
        return ValidationResult(
            valid=True,
            message=f"Tracking disabled for category: {category}"
        )
    
    def get_status(self) -> Dict:
        """
        Get current tracking status summary.
        
        Returns:
            Dictionary with tracking status information
        """
        tracking_enabled = self.config.get("user_preferences", {}).get(
            "document_tracking", {}
        ).get("enabled", False)
        
        whitelist = self.config.get("user_preferences", {}).get(
            "document_tracking", {}
        ).get("whitelist", {})
        
        enabled_categories = [
            cat for cat, settings in whitelist.items()
            if isinstance(settings, dict) and settings.get("enabled")
        ]
        
        return {
            "tracking_enabled": tracking_enabled,
            "enabled_categories": enabled_categories,
            "trackable_patterns": self.get_trackable_patterns(),
            "protected_patterns": self.get_protected_patterns(),
            "validation": self.validate().valid
        }


# Example usage
if __name__ == "__main__":
    from pathlib import Path
    
    # Example: Initialize config for repo
    repo_path = Path("/path/to/repo")
    config = DocumentTrackingConfig(repo_path)
    
    # Validate configuration
    result = config.validate()
    print(f"Valid: {result.valid}")
    if not result.valid:
        for violation in result.violations:
            print(f"  {violation.severity.value}: {violation.pattern} - {violation.reason}")
    
    # Enable planning tracking
    result = config.enable_tracking("planning")
    print(f"Enable result: {result.message}")
    
    # Check if file is trackable
    trackable = config.is_file_trackable(".cortex/planning/active/my-plan.md")
    print(f"Can track plan: {trackable}")
    
    # Get status
    status = config.get_status()
    print(f"Status: {json.dumps(status, indent=2)}")
