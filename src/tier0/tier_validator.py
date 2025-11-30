"""
CORTEX Tier Validator - Validates Brain Tier Integrity

Ensures data is stored in the correct tier and validates tier boundaries:
- Tier 0: Immutable governance rules (brain-protection-rules.yaml)
- Tier 1: Conversation history and working memory (SQLite)
- Tier 2: Knowledge graph and learned patterns (YAML)
- Tier 3: Development context and project health (YAML)

Part of Brain Protection Layer
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Created: 2025-11-11
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Dict, Any, Optional
import yaml
import sqlite3


class TierLevel(Enum):
    """CORTEX tier levels."""
    TIER_0 = "tier0"  # Immutable governance
    TIER_1 = "tier1"  # Working memory
    TIER_2 = "tier2"  # Knowledge graph
    TIER_3 = "tier3"  # Development context


class ValidationSeverity(Enum):
    """Validation result severity levels."""
    OK = "ok"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class TierViolation:
    """A tier boundary violation."""
    tier: TierLevel
    violation_type: str
    severity: ValidationSeverity
    message: str
    affected_file: Optional[str] = None
    suggestion: Optional[str] = None


@dataclass
class TierValidationResult:
    """Result of tier validation."""
    passed: bool
    tier: TierLevel
    violations: List[TierViolation]
    warnings: List[TierViolation]
    metadata: Dict[str, Any]


class TierValidator:
    """
    Validates CORTEX brain tier integrity.
    
    Ensures:
    1. Tier 0 contains only immutable governance rules
    2. Tier 1 contains only conversation data
    3. Tier 2 contains only aggregated patterns
    4. Tier 3 contains only development context
    5. No cross-tier data leakage
    """
    
    def __init__(self, brain_root: Optional[Path] = None):
        """
        Initialize Tier Validator.
        
        Args:
            brain_root: Path to cortex-brain directory
        """
        if brain_root is None:
            project_root = Path(__file__).parent.parent.parent
            brain_root = project_root / "cortex-brain"
        
        self.brain_root = Path(brain_root)
        
        # Define tier paths
        self.tier_paths = {
            TierLevel.TIER_0: self.brain_root / "brain-protection-rules.yaml",
            TierLevel.TIER_1: self.brain_root / "conversation-history.jsonl",
            TierLevel.TIER_2: self.brain_root / "knowledge-graph.yaml",
            TierLevel.TIER_3: self.brain_root / "development-context.yaml"
        }
        
        # Define tier content rules
        self.tier_rules = {
            TierLevel.TIER_0: {
                "allowed_extensions": [".yaml", ".yml"],
                "forbidden_keywords": ["conversation", "chat", "session", "user_input"],
                "description": "Immutable governance rules only"
            },
            TierLevel.TIER_1: {
                "allowed_extensions": [".jsonl", ".db", ".sqlite"],
                "required_schema": ["timestamp", "conversation_id"],
                "description": "Conversation history and working memory"
            },
            TierLevel.TIER_2: {
                "allowed_extensions": [".yaml", ".yml"],
                "required_keys": ["patterns", "confidence"],
                "forbidden_keywords": ["raw_conversation", "user_message"],
                "description": "Aggregated patterns and knowledge graph"
            },
            TierLevel.TIER_3: {
                "allowed_extensions": [".yaml", ".yml"],
                "required_keys": ["git_status", "test_coverage"],
                "description": "Development context and project health"
            }
        }
    
    def validate_all_tiers(self) -> Dict[TierLevel, TierValidationResult]:
        """
        Validate all tiers for integrity.
        
        Returns:
            Dictionary mapping tier to validation result
        """
        results = {}
        
        for tier in TierLevel:
            results[tier] = self.validate_tier(tier)
        
        return results
    
    def validate_tier(self, tier: TierLevel) -> TierValidationResult:
        """
        Validate a specific tier.
        
        Args:
            tier: Tier to validate
        
        Returns:
            TierValidationResult with violations and warnings
        """
        violations = []
        warnings = []
        metadata = {
            "tier": tier.value,
            "path": str(self.tier_paths.get(tier, "N/A"))
        }
        
        # Check if tier exists
        tier_path = self.tier_paths.get(tier)
        if not tier_path or not tier_path.exists():
            warnings.append(TierViolation(
                tier=tier,
                violation_type="missing_tier",
                severity=ValidationSeverity.WARNING,
                message=f"Tier {tier.value} file not found at {tier_path}",
                affected_file=str(tier_path) if tier_path else None,
                suggestion="Initialize tier with default structure"
            ))
            return TierValidationResult(
                passed=True,  # Missing is not a failure, just a warning
                tier=tier,
                violations=[],
                warnings=warnings,
                metadata=metadata
            )
        
        # Validate tier content
        if tier == TierLevel.TIER_0:
            violations.extend(self._validate_tier0(tier_path))
        elif tier == TierLevel.TIER_1:
            violations.extend(self._validate_tier1(tier_path))
        elif tier == TierLevel.TIER_2:
            violations.extend(self._validate_tier2(tier_path))
        elif tier == TierLevel.TIER_3:
            violations.extend(self._validate_tier3(tier_path))
        
        # Separate violations by severity
        critical_violations = [v for v in violations if v.severity == ValidationSeverity.CRITICAL]
        error_violations = [v for v in violations if v.severity == ValidationSeverity.ERROR]
        warning_violations = [v for v in violations if v.severity == ValidationSeverity.WARNING]
        
        # Determine overall pass/fail
        passed = len(critical_violations) == 0 and len(error_violations) == 0
        
        metadata["critical_count"] = len(critical_violations)
        metadata["error_count"] = len(error_violations)
        metadata["warning_count"] = len(warning_violations)
        
        return TierValidationResult(
            passed=passed,
            tier=tier,
            violations=critical_violations + error_violations,
            warnings=warning_violations,
            metadata=metadata
        )
    
    def _validate_tier0(self, tier_path: Path) -> List[TierViolation]:
        """Validate Tier 0 (Immutable Governance)."""
        violations = []
        rules = self.tier_rules[TierLevel.TIER_0]
        
        # Check file extension
        if tier_path.suffix not in rules["allowed_extensions"]:
            violations.append(TierViolation(
                tier=TierLevel.TIER_0,
                violation_type="invalid_format",
                severity=ValidationSeverity.ERROR,
                message=f"Tier 0 must use YAML format, found {tier_path.suffix}",
                affected_file=str(tier_path),
                suggestion="Convert to YAML format"
            ))
            return violations
        
        # Load and validate YAML content
        try:
            with open(tier_path, 'r', encoding='utf-8') as f:
                content = f.read()
                data = yaml.safe_load(content)
            
            # Check for forbidden keywords (application-specific data)
            content_lower = content.lower()
            for keyword in rules["forbidden_keywords"]:
                if keyword in content_lower:
                    violations.append(TierViolation(
                        tier=TierLevel.TIER_0,
                        violation_type="application_data_in_tier0",
                        severity=ValidationSeverity.CRITICAL,
                        message=f"Application-specific keyword '{keyword}' found in Tier 0",
                        affected_file=str(tier_path),
                        suggestion="Move application data to Tier 2 with scope='application'"
                    ))
            
            # Validate structure
            if not isinstance(data, dict):
                violations.append(TierViolation(
                    tier=TierLevel.TIER_0,
                    violation_type="invalid_structure",
                    severity=ValidationSeverity.ERROR,
                    message="Tier 0 YAML must be a dictionary at root level",
                    affected_file=str(tier_path)
                ))
            
            # Check for immutability markers
            if data and not data.get('version'):
                violations.append(TierViolation(
                    tier=TierLevel.TIER_0,
                    violation_type="missing_version",
                    severity=ValidationSeverity.WARNING,
                    message="Tier 0 should include version field for immutability tracking",
                    affected_file=str(tier_path),
                    suggestion="Add 'version' field to YAML"
                ))
        
        except yaml.YAMLError as e:
            violations.append(TierViolation(
                tier=TierLevel.TIER_0,
                violation_type="yaml_parse_error",
                severity=ValidationSeverity.CRITICAL,
                message=f"Failed to parse Tier 0 YAML: {e}",
                affected_file=str(tier_path),
                suggestion="Fix YAML syntax errors"
            ))
        except Exception as e:
            violations.append(TierViolation(
                tier=TierLevel.TIER_0,
                violation_type="read_error",
                severity=ValidationSeverity.ERROR,
                message=f"Failed to read Tier 0 file: {e}",
                affected_file=str(tier_path)
            ))
        
        return violations
    
    def _validate_tier1(self, tier_path: Path) -> List[TierViolation]:
        """Validate Tier 1 (Working Memory)."""
        violations = []
        rules = self.tier_rules[TierLevel.TIER_1]
        
        # Check file extension
        if tier_path.suffix not in rules["allowed_extensions"]:
            violations.append(TierViolation(
                tier=TierLevel.TIER_1,
                violation_type="invalid_format",
                severity=ValidationSeverity.ERROR,
                message=f"Tier 1 must use JSONL or SQLite, found {tier_path.suffix}",
                affected_file=str(tier_path),
                suggestion="Use .jsonl or .db format"
            ))
            return violations
        
        # Validate based on format
        if tier_path.suffix in ['.db', '.sqlite']:
            violations.extend(self._validate_tier1_db(tier_path, rules))
        elif tier_path.suffix == '.jsonl':
            violations.extend(self._validate_tier1_jsonl(tier_path, rules))
        
        return violations
    
    def _validate_tier1_db(self, tier_path: Path, rules: Dict) -> List[TierViolation]:
        """Validate Tier 1 SQLite database."""
        violations = []
        
        try:
            conn = sqlite3.connect(tier_path)
            cursor = conn.cursor()
            
            # Check for required schema
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            
            if not tables:
                violations.append(TierViolation(
                    tier=TierLevel.TIER_1,
                    violation_type="empty_database",
                    severity=ValidationSeverity.WARNING,
                    message="Tier 1 database has no tables",
                    affected_file=str(tier_path),
                    suggestion="Initialize with conversation schema"
                ))
            else:
                # Check for required columns in main table
                main_table = tables[0]
                cursor.execute(f"PRAGMA table_info({main_table});")
                columns = [row[1] for row in cursor.fetchall()]
                
                for required_field in rules.get("required_schema", []):
                    if required_field not in columns:
                        violations.append(TierViolation(
                            tier=TierLevel.TIER_1,
                            violation_type="missing_schema_field",
                            severity=ValidationSeverity.ERROR,
                            message=f"Required field '{required_field}' missing from Tier 1 schema",
                            affected_file=str(tier_path),
                            suggestion=f"Add '{required_field}' column to conversation table"
                        ))
            
            conn.close()
        
        except sqlite3.Error as e:
            violations.append(TierViolation(
                tier=TierLevel.TIER_1,
                violation_type="database_error",
                severity=ValidationSeverity.CRITICAL,
                message=f"Failed to validate Tier 1 database: {e}",
                affected_file=str(tier_path),
                suggestion="Check database file integrity"
            ))
        
        return violations
    
    def _validate_tier1_jsonl(self, tier_path: Path, rules: Dict) -> List[TierViolation]:
        """Validate Tier 1 JSONL file."""
        violations = []
        
        try:
            import json
            
            with open(tier_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if not lines:
                violations.append(TierViolation(
                    tier=TierLevel.TIER_1,
                    violation_type="empty_file",
                    severity=ValidationSeverity.WARNING,
                    message="Tier 1 JSONL file is empty",
                    affected_file=str(tier_path)
                ))
                return violations
            
            # Validate first few lines
            for i, line in enumerate(lines[:5], 1):
                if not line.strip():
                    continue
                
                try:
                    entry = json.loads(line)
                    
                    # Check for required fields
                    for required_field in rules.get("required_schema", []):
                        if required_field not in entry:
                            violations.append(TierViolation(
                                tier=TierLevel.TIER_1,
                                violation_type="missing_required_field",
                                severity=ValidationSeverity.ERROR,
                                message=f"Line {i} missing required field '{required_field}'",
                                affected_file=str(tier_path),
                                suggestion=f"Ensure all entries have '{required_field}' field"
                            ))
                
                except json.JSONDecodeError as e:
                    violations.append(TierViolation(
                        tier=TierLevel.TIER_1,
                        violation_type="json_parse_error",
                        severity=ValidationSeverity.ERROR,
                        message=f"Line {i} is not valid JSON: {e}",
                        affected_file=str(tier_path),
                        suggestion="Fix JSON syntax"
                    ))
        
        except Exception as e:
            violations.append(TierViolation(
                tier=TierLevel.TIER_1,
                violation_type="read_error",
                severity=ValidationSeverity.ERROR,
                message=f"Failed to read Tier 1 file: {e}",
                affected_file=str(tier_path)
            ))
        
        return violations
    
    def _validate_tier2(self, tier_path: Path) -> List[TierViolation]:
        """Validate Tier 2 (Knowledge Graph)."""
        violations = []
        rules = self.tier_rules[TierLevel.TIER_2]
        
        # Check file extension
        if tier_path.suffix not in rules["allowed_extensions"]:
            violations.append(TierViolation(
                tier=TierLevel.TIER_2,
                violation_type="invalid_format",
                severity=ValidationSeverity.ERROR,
                message=f"Tier 2 must use YAML format, found {tier_path.suffix}",
                affected_file=str(tier_path),
                suggestion="Convert to YAML format"
            ))
            return violations
        
        # Load and validate YAML content
        try:
            with open(tier_path, 'r', encoding='utf-8') as f:
                content = f.read()
                data = yaml.safe_load(content)
            
            # Check for forbidden keywords (raw conversation data)
            content_lower = content.lower()
            for keyword in rules.get("forbidden_keywords", []):
                if keyword in content_lower:
                    violations.append(TierViolation(
                        tier=TierLevel.TIER_2,
                        violation_type="raw_conversation_in_tier2",
                        severity=ValidationSeverity.CRITICAL,
                        message=f"Raw conversation keyword '{keyword}' found in Tier 2",
                        affected_file=str(tier_path),
                        suggestion="Move raw conversations to Tier 1, keep only patterns"
                    ))
            
            # Check for required keys
            if data:
                for required_key in rules.get("required_keys", []):
                    if required_key not in data:
                        violations.append(TierViolation(
                            tier=TierLevel.TIER_2,
                            violation_type="missing_required_key",
                            severity=ValidationSeverity.WARNING,
                            message=f"Tier 2 missing recommended key '{required_key}'",
                            affected_file=str(tier_path),
                            suggestion=f"Add '{required_key}' section to knowledge graph"
                        ))
        
        except yaml.YAMLError as e:
            violations.append(TierViolation(
                tier=TierLevel.TIER_2,
                violation_type="yaml_parse_error",
                severity=ValidationSeverity.CRITICAL,
                message=f"Failed to parse Tier 2 YAML: {e}",
                affected_file=str(tier_path),
                suggestion="Fix YAML syntax errors"
            ))
        except Exception as e:
            violations.append(TierViolation(
                tier=TierLevel.TIER_2,
                violation_type="read_error",
                severity=ValidationSeverity.ERROR,
                message=f"Failed to read Tier 2 file: {e}",
                affected_file=str(tier_path)
            ))
        
        return violations
    
    def _validate_tier3(self, tier_path: Path) -> List[TierViolation]:
        """Validate Tier 3 (Development Context)."""
        violations = []
        rules = self.tier_rules[TierLevel.TIER_3]
        
        # Check file extension
        if tier_path.suffix not in rules["allowed_extensions"]:
            violations.append(TierViolation(
                tier=TierLevel.TIER_3,
                violation_type="invalid_format",
                severity=ValidationSeverity.ERROR,
                message=f"Tier 3 must use YAML format, found {tier_path.suffix}",
                affected_file=str(tier_path),
                suggestion="Convert to YAML format"
            ))
            return violations
        
        # Load and validate YAML content
        try:
            with open(tier_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            # Check for required keys
            if data:
                for required_key in rules.get("required_keys", []):
                    if required_key not in data:
                        violations.append(TierViolation(
                            tier=TierLevel.TIER_3,
                            violation_type="missing_required_key",
                            severity=ValidationSeverity.WARNING,
                            message=f"Tier 3 missing recommended key '{required_key}'",
                            affected_file=str(tier_path),
                            suggestion=f"Add '{required_key}' section to development context"
                        ))
        
        except yaml.YAMLError as e:
            violations.append(TierViolation(
                tier=TierLevel.TIER_3,
                violation_type="yaml_parse_error",
                severity=ValidationSeverity.CRITICAL,
                message=f"Failed to parse Tier 3 YAML: {e}",
                affected_file=str(tier_path),
                suggestion="Fix YAML syntax errors"
            ))
        except Exception as e:
            violations.append(TierViolation(
                tier=TierLevel.TIER_3,
                violation_type="read_error",
                severity=ValidationSeverity.ERROR,
                message=f"Failed to read Tier 3 file: {e}",
                affected_file=str(tier_path)
            ))
        
        return violations
    
    def generate_report(self, results: Dict[TierLevel, TierValidationResult]) -> str:
        """
        Generate human-readable validation report.
        
        Args:
            results: Validation results for all tiers
        
        Returns:
            Formatted report string
        """
        report = []
        report.append("=" * 70)
        report.append("CORTEX TIER VALIDATION REPORT")
        report.append("=" * 70)
        report.append("")
        
        # Summary
        all_passed = all(r.passed for r in results.values())
        total_violations = sum(len(r.violations) for r in results.values())
        total_warnings = sum(len(r.warnings) for r in results.values())
        
        if all_passed:
            report.append("✅ All tiers passed validation")
        else:
            report.append(f"❌ Validation failed: {total_violations} violations, {total_warnings} warnings")
        
        report.append("")
        report.append("=" * 70)
        report.append("")
        
        # Per-tier details
        for tier, result in results.items():
            status = "✅ PASS" if result.passed else "❌ FAIL"
            report.append(f"{status} {tier.value.upper()}: {result.metadata.get('path', 'N/A')}")
            
            if result.violations:
                report.append(f"  Violations: {len(result.violations)}")
                for v in result.violations:
                    report.append(f"    • [{v.severity.value.upper()}] {v.message}")
                    if v.suggestion:
                        report.append(f"      → {v.suggestion}")
            
            if result.warnings:
                report.append(f"  Warnings: {len(result.warnings)}")
                for w in result.warnings[:3]:  # Show first 3
                    report.append(f"    • [{w.severity.value.upper()}] {w.message}")
                if len(result.warnings) > 3:
                    report.append(f"    ... and {len(result.warnings) - 3} more warnings")
            
            if result.passed and not result.warnings:
                report.append("  ✓ No issues found")
            
            report.append("")
        
        report.append("=" * 70)
        
        return "\n".join(report)


def validate_brain_tiers() -> bool:
    """
    Convenience function to validate all brain tiers.
    
    Returns:
        True if all tiers passed validation
    """
    validator = TierValidator()
    results = validator.validate_all_tiers()
    print(validator.generate_report(results))
    return all(r.passed for r in results.values())


if __name__ == "__main__":
    import sys
    passed = validate_brain_tiers()
    sys.exit(0 if passed else 1)
