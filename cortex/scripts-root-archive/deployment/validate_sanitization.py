"""Sanitization validation for pre-commit hooks.

This module provides the SanitizationValidator class that validates
the sanitization state of governance.db and tier rules for pre-commit hooks.

PHASE-DEPLOYMENT-001: AC-DEP-001-03
"""

import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from cortex.common.validators import ValidationResult


@dataclass
class FullValidationResult:
    """Result of full validation (db + tier1 + tier2).
    
    Attributes:
        is_valid: Overall validation passed.
        db_valid: Database validation passed.
        tier1_valid: Tier1 rules validation passed.
        tier2_valid: Tier2 rules validation passed.
        reason: Combined reason if any validation failed.
    """
    is_valid: bool = True
    db_valid: bool = True
    tier1_valid: bool = True
    tier2_valid: bool = True
    reason: str = ""


class SanitizationValidator:
    """Validates sanitization state for pre-commit hooks.
    
    Checks governance.db for dev entries and tier1/tier2 for non-template
    rules to ensure the repository is in a clean state for production.
    
    Attributes:
        db_path: Path to governance.db.
        tier1_path: Path to tier1 rules directory.
        tier2_path: Path to tier2 rules directory.
    """
    
    # Patterns that indicate dev entries
    DEV_PATTERNS = [
        r"^TEST",
        r"^DEV",
        r"^DEBUG",
        r"^TEMP",
        r"^MOCK",
    ]
    
    # Release tag pattern (semver)
    RELEASE_TAG_PATTERN = r"^v\d+\.\d+\.\d+(-[a-zA-Z0-9]+)?$"
    
    def __init__(
        self,
        db_path: Optional[Path] = None,
        tier1_path: Optional[Path] = None,
        tier2_path: Optional[Path] = None,
    ) -> None:
        """Initialize the validator.
        
        Args:
            db_path: Path to governance.db file.
            tier1_path: Path to tier1 rules directory.
            tier2_path: Path to tier2 rules directory.
        """
        self.db_path = Path(db_path) if db_path else None
        self.tier1_path = Path(tier1_path) if tier1_path else None
        self.tier2_path = Path(tier2_path) if tier2_path else None
    
    def validate(self) -> ValidationResult:
        """Validate governance.db for dev entries.
        
        Returns:
            ValidationResult indicating if db is clean.
        """
        result = ValidationResult()
        
        if not self.db_path or not self.db_path.exists():
            # No db is considered clean
            return result
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Check if audit_log table exists
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='audit_log'"
            )
            if not cursor.fetchone():
                return result  # No table, considered clean
            
            # Check for dev entries
            cursor.execute("SELECT ac_id FROM audit_log WHERE is_production = 0")
            non_prod_entries = cursor.fetchall()
            
            dev_entries = []
            for (ac_id,) in non_prod_entries:
                for pattern in self.DEV_PATTERNS:
                    if re.match(pattern, ac_id, re.IGNORECASE):
                        dev_entries.append(ac_id)
                        break
            
            if dev_entries:
                result.is_valid = False
                result.reason = f"Dev entries found in governance.db: {', '.join(dev_entries[:5])}"
                if len(dev_entries) > 5:
                    result.reason += f" ... and {len(dev_entries) - 5} more"
            
        finally:
            conn.close()
        
        return result
    
    def validate_tier_rules(self) -> ValidationResult:
        """Validate tier1 and tier2 for non-template rules.
        
        Returns:
            ValidationResult indicating if tier rules are clean.
        """
        result = ValidationResult()
        
        non_template_files: List[str] = []
        
        # Check tier1
        if self.tier1_path and self.tier1_path.exists():
            for file in self.tier1_path.glob("*.yaml"):
                # Skip if in templates directory
                if "templates" in str(file.parent):
                    continue
                # Skip __init__.py and similar
                if file.name.startswith("_"):
                    continue
                non_template_files.append(str(file.relative_to(self.tier1_path.parent.parent)))
        
        # Check tier2
        if self.tier2_path and self.tier2_path.exists():
            for file in self.tier2_path.glob("*.yaml"):
                if "templates" in str(file.parent):
                    continue
                if file.name.startswith("_"):
                    continue
                non_template_files.append(str(file.relative_to(self.tier2_path.parent.parent)))
        
        if non_template_files:
            result.is_valid = False
            result.reason = f"Non-template rules found: {', '.join(non_template_files[:3])}"
            if len(non_template_files) > 3:
                result.reason += f" ... and {len(non_template_files) - 3} more"
        
        return result
    
    def validate_all(self) -> FullValidationResult:
        """Validate governance.db, tier1, and tier2.
        
        Returns:
            FullValidationResult with all validation results.
        """
        result = FullValidationResult()
        
        # Validate database
        db_result = self.validate()
        result.db_valid = db_result.is_valid
        
        # Validate tier rules
        tier_result = self.validate_tier_rules()
        result.tier1_valid = tier_result.is_valid
        result.tier2_valid = tier_result.is_valid
        
        # Overall result
        result.is_valid = result.db_valid and result.tier1_valid and result.tier2_valid
        
        if not result.is_valid:
            reasons = []
            if not result.db_valid:
                reasons.append(f"DB: {db_result.reason}")
            if not result.tier1_valid or not result.tier2_valid:
                reasons.append(f"Tier: {tier_result.reason}")
            result.reason = "; ".join(reasons)
        
        return result
    
    def check_release_tag(self, tag: str) -> bool:
        """Check if a tag is a release tag that should trigger sanitization.
        
        Args:
            tag: The git tag to check.
            
        Returns:
            True if this is a release tag (v1.0.0 format).
        """
        return bool(re.match(self.RELEASE_TAG_PATTERN, tag))
    
    def get_precommit_exit_code(self) -> int:
        """Get the exit code for pre-commit hook.
        
        Returns:
            0 if validation passes, 1 if it fails.
        """
        result = self.validate()
        return 0 if result.is_valid else 1


def main() -> int:
    """CLI entry point for validation.
    
    Returns:
        Exit code (0 for clean, 1 for dirty).
    """
    import sys
    
    # Default paths
    db_path = Path("cortex_brain/state/governance.db")
    tier1_path = Path("cortex_brain/tier1")
    tier2_path = Path("cortex_brain/tier2")
    
    # Parse command line args
    if "--db" in sys.argv:
        idx = sys.argv.index("--db")
        if idx + 1 < len(sys.argv):
            db_path = Path(sys.argv[idx + 1])
    
    validator = SanitizationValidator(
        db_path=db_path,
        tier1_path=tier1_path,
        tier2_path=tier2_path
    )
    
    result = validator.validate_all()
    
    if result.is_valid:
        print("✅ Sanitization validation passed")
        return 0
    else:
        print(f"❌ Sanitization validation failed: {result.reason}")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
