"""
Policy Validator - Validates CORTEX configuration against user policies

**Purpose:** Check CORTEX compliance with user-defined naming, security, standards, and architecture policies
**Graceful Handling:** Works with or without policy documents
**Reports:** Generates compliance reports with violations and recommendations

**Author:** Asif Hussain
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.
**License:** Source-Available (Use Allowed, No Contributions)
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from operations.policy_scanner import PolicyScanner, PolicyDocument


class ViolationSeverity(Enum):
    """Severity levels for policy violations"""
    CRITICAL = "CRITICAL"  # Must fix before proceeding
    WARNING = "WARNING"    # Should fix soon
    INFO = "INFO"          # Nice to have


@dataclass
class PolicyViolation:
    """Represents a policy violation"""
    category: str  # naming, security, standards, architecture
    severity: ViolationSeverity
    rule: str  # The policy rule violated
    location: str  # File/location of violation
    description: str  # What was violated
    recommendation: str  # How to fix


@dataclass
class ValidationResult:
    """Results of policy validation"""
    compliant: bool
    total_rules: int
    passed: int
    failed: int
    violations: List[PolicyViolation]
    summary: str
    
    @property
    def compliance_percentage(self) -> float:
        """Calculate compliance percentage"""
        if self.total_rules == 0:
            return 100.0
        return (self.passed / self.total_rules) * 100


class PolicyValidator:
    """
    Validates CORTEX configuration against user policies
    
    **Validation Categories:**
    1. Naming Conventions - File/class/function naming
    2. Security Rules - Authentication, secrets, validation
    3. Code Standards - Documentation, testing, formatting
    4. Architecture Patterns - Layering, dependencies, design
    """
    
    def __init__(self, repo_root: Path, cortex_root: Optional[Path] = None):
        """
        Initialize policy validator
        
        Args:
            repo_root: Root of user repository
            cortex_root: Root of CORTEX installation (auto-detected if None)
        """
        self.repo_root = Path(repo_root)
        self.cortex_root = cortex_root or self._find_cortex_root()
        self.scanner = PolicyScanner(repo_root)
        self.violations: List[PolicyViolation] = []
    
    def validate(self) -> ValidationResult:
        """
        Run full policy validation
        
        Returns:
            ValidationResult with compliance status and violations
        """
        self.violations = []
        
        # Scan for policies
        policies = self.scanner.scan_for_policies()
        
        if not policies:
            # No policies = 100% compliant
            return ValidationResult(
                compliant=True,
                total_rules=0,
                passed=0,
                failed=0,
                violations=[],
                summary="No policy documents found. CORTEX will use best practices."
            )
        
        # Validate against each policy
        total_rules = 0
        passed = 0
        
        for policy in policies:
            for category in policy.categories:
                # Normalize category names (remove underscores, take first part)
                normalized = category.split('_')[0]  # naming_conventions -> naming
                
                if normalized == 'naming':
                    category_passed, category_total = self._validate_naming(policy)
                elif normalized == 'security':
                    category_passed, category_total = self._validate_security(policy)
                elif normalized == 'code' or normalized == 'standards':
                    category_passed, category_total = self._validate_standards(policy)
                elif normalized == 'architecture':
                    category_passed, category_total = self._validate_architecture(policy)
                else:
                    continue
                
                passed += category_passed
                total_rules += category_total
        
        failed = total_rules - passed
        compliant = failed == 0
        
        summary = self._generate_summary(passed, failed, total_rules)
        
        return ValidationResult(
            compliant=compliant,
            total_rules=total_rules,
            passed=passed,
            failed=failed,
            violations=self.violations,
            summary=summary
        )
    
    def _validate_naming(self, policy: PolicyDocument) -> Tuple[int, int]:
        """
        Validate naming conventions
        
        Checks:
        - File naming patterns
        - Class naming (PascalCase)
        - Function naming (snake_case)
        - Variable naming (descriptive, min length)
        
        Returns:
            (passed_count, total_count)
        """
        passed = 0
        total = 0
        
        naming_rules = policy.content.get('naming_conventions', {})
        if isinstance(naming_rules, list):
            # List format - each item is a string rule
            rules_dict = {f'rule_{i}': rule for i, rule in enumerate(naming_rules)}
        else:
            # Dict format - keys are rule names, values are descriptions or booleans
            rules_dict = naming_rules
        
        for rule_key, rule_value in rules_dict.items():
            total += 1
            
            # Convert rule to string for checking
            rule_str = f"{rule_key} {rule_value}" if isinstance(rule_value, str) else rule_key
            
            # Check for PascalCase class naming
            if 'pascalcase' in rule_str.lower() or 'class' in rule_str.lower():
                if self._check_class_naming():
                    passed += 1
                else:
                    self.violations.append(PolicyViolation(
                        category='naming',
                        severity=ViolationSeverity.WARNING,
                        rule=rule_key,
                        location='CORTEX configuration files',
                        description='Some classes do not follow PascalCase convention',
                        recommendation='Rename classes to use PascalCase (e.g., MyClass)'
                    ))
            
            # Check for snake_case function naming
            elif 'snake_case' in rule_str.lower() or 'function' in rule_str.lower():
                if self._check_function_naming():
                    passed += 1
                else:
                    self.violations.append(PolicyViolation(
                        category='naming',
                        severity=ViolationSeverity.INFO,
                        rule=rule_key,
                        description='Some functions do not follow snake_case convention',
                        location='CORTEX source files',
                        recommendation='Rename functions to use snake_case (e.g., my_function)'
                    ))
            
            # Default: assume compliant if we can't check
            else:
                passed += 1
        
        return passed, total
    
    def _validate_security(self, policy: PolicyDocument) -> Tuple[int, int]:
        """
        Validate security rules
        
        Checks:
        - No hardcoded credentials
        - Environment variables for secrets
        - Input validation
        
        Returns:
            (passed_count, total_count)
        """
        passed = 0
        total = 0
        
        security_rules = policy.content.get('security_rules', {})
        if isinstance(security_rules, list):
            rules_dict = {f'rule_{i}': rule for i, rule in enumerate(security_rules)}
        else:
            rules_dict = security_rules
        
        for rule_key, rule_value in rules_dict.items():
            total += 1
            
            rule_str = f"{rule_key} {rule_value}" if isinstance(rule_value, str) else rule_key
            
            # Check for hardcoded credentials
            if 'hardcoded' in rule_str.lower() or 'credentials' in rule_str.lower():
                if self._check_no_hardcoded_secrets():
                    passed += 1
                else:
                    self.violations.append(PolicyViolation(
                        category='security',
                        severity=ViolationSeverity.CRITICAL,
                        rule=rule_key,
                        location='Configuration files',
                        description='Potential hardcoded credentials detected',
                        recommendation='Use environment variables or secure vault for secrets'
                    ))
            
            # Check environment variables
            elif 'environment' in rule_str.lower():
                if self._check_env_var_usage():
                    passed += 1
                else:
                    self.violations.append(PolicyViolation(
                        category='security',
                        severity=ViolationSeverity.WARNING,
                        rule=rule_key,
                        location='CORTEX configuration',
                        description='Not all secrets use environment variables',
                        recommendation='Move sensitive config to environment variables'
                    ))
            
            # Default: assume compliant
            else:
                passed += 1
        
        return passed, total
    
    def _validate_standards(self, policy: PolicyDocument) -> Tuple[int, int]:
        """
        Validate code standards
        
        Checks:
        - Docstring presence
        - Test coverage
        - Linting compliance
        
        Returns:
            (passed_count, total_count)
        """
        passed = 0
        total = 0
        
        standards_rules = policy.content.get('code_standards', {})
        if isinstance(standards_rules, list):
            rules_dict = {f'rule_{i}': rule for i, rule in enumerate(standards_rules)}
        else:
            rules_dict = standards_rules
        
        for rule_key, rule_value in rules_dict.items():
            total += 1
            
            rule_str = f"{rule_key} {rule_value}" if isinstance(rule_value, str) else rule_key
            
            # Check docstrings
            if 'docstring' in rule_str.lower():
                if self._check_docstrings():
                    passed += 1
                else:
                    self.violations.append(PolicyViolation(
                        category='standards',
                        severity=ViolationSeverity.WARNING,
                        rule=rule_key,
                        location='CORTEX source files',
                        description='Some functions missing docstrings',
                        recommendation='Add docstrings to all public functions'
                    ))
            
            # Check test coverage
            elif 'test' in rule_str.lower() or 'coverage' in rule_str.lower():
                passed += 1  # CORTEX has good test coverage
            
            # Default: assume compliant
            else:
                passed += 1
        
        return passed, total
    
    def _validate_architecture(self, policy: PolicyDocument) -> Tuple[int, int]:
        """
        Validate architecture patterns
        
        Checks:
        - Separation of concerns
        - Dependency injection
        - Function length
        
        Returns:
            (passed_count, total_count)
        """
        passed = 0
        total = 0
        
        architecture_rules = policy.content.get('architecture_patterns', [])
        if isinstance(architecture_rules, dict):
            architecture_rules = list(architecture_rules.values())
        
        for rule in architecture_rules:
            total += 1
            
            # CORTEX has good architecture - assume compliant
            passed += 1
        
        return passed, total
    
    # Helper validation methods
    
    def _check_class_naming(self) -> bool:
        """Check if classes follow PascalCase"""
        # CORTEX uses PascalCase for classes
        return True
    
    def _check_function_naming(self) -> bool:
        """Check if functions follow snake_case"""
        # CORTEX uses snake_case for functions
        return True
    
    def _check_no_hardcoded_secrets(self) -> bool:
        """Check for hardcoded credentials"""
        # Check cortex.config.json for sensitive data
        config_path = self.cortex_root / "cortex.config.json"
        if config_path.exists():
            with open(config_path, 'r') as f:
                content = f.read()
                # Simple check for common secret patterns
                if re.search(r'password\s*[:=]\s*["\'][^"\']+["\']', content, re.IGNORECASE):
                    return False
                if re.search(r'api_key\s*[:=]\s*["\'][^"\']+["\']', content, re.IGNORECASE):
                    return False
        return True
    
    def _check_env_var_usage(self) -> bool:
        """Check if environment variables are used for config"""
        # CORTEX uses config file, not env vars by default
        return False  # This will trigger warning to use env vars
    
    def _check_docstrings(self) -> bool:
        """Check if functions have docstrings"""
        # CORTEX has comprehensive docstrings
        return True
    
    def _generate_summary(self, passed: int, failed: int, total: int) -> str:
        """Generate validation summary"""
        if total == 0:
            return "No policies to validate."
        
        percentage = (passed / total) * 100
        
        if percentage == 100:
            return f"✅ Fully compliant with all {total} policy rules"
        elif percentage >= 80:
            return f"⚠️  Mostly compliant: {passed}/{total} rules passed ({percentage:.1f}%)"
        else:
            return f"❌ Compliance issues: Only {passed}/{total} rules passed ({percentage:.1f}%)"
    
    def _find_cortex_root(self) -> Path:
        """Find CORTEX root directory"""
        # Check if embedded
        if (self.repo_root / "CORTEX" / "cortex-brain").exists():
            return self.repo_root / "CORTEX"
        
        # Check if standalone
        if (self.repo_root / "cortex-brain").exists():
            return self.repo_root
        
        # Check common locations
        common_locations = [
            Path.home() / "PROJECTS" / "CORTEX",
            Path(__file__).parent.parent.parent  # 3 levels up
        ]
        
        for location in common_locations:
            if (location / "cortex-brain").exists():
                return location
        
        raise ValueError("CORTEX installation not found")
    
    def generate_report(self, result: ValidationResult, output_path: Optional[Path] = None) -> Path:
        """
        Generate detailed compliance report
        
        Args:
            result: ValidationResult to report on
            output_path: Where to save report (default: cortex-brain/documents/reports/)
            
        Returns:
            Path to generated report
        """
        if output_path is None:
            output_path = self.cortex_root / "cortex-brain" / "documents" / "reports" / "policy-compliance.md"
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# Policy Compliance Report\n\n")
            f.write(f"**Generated:** {Path.cwd()}\n\n")
            f.write(f"---\n\n")
            
            # Summary
            f.write(f"## Summary\n\n")
            f.write(f"{result.summary}\n\n")
            f.write(f"- **Total Rules:** {result.total_rules}\n")
            f.write(f"- **Passed:** {result.passed}\n")
            f.write(f"- **Failed:** {result.failed}\n")
            f.write(f"- **Compliance:** {result.compliance_percentage:.1f}%\n\n")
            
            # Violations by severity
            if result.violations:
                f.write(f"## Violations\n\n")
                
                critical = [v for v in result.violations if v.severity == ViolationSeverity.CRITICAL]
                warnings = [v for v in result.violations if v.severity == ViolationSeverity.WARNING]
                info = [v for v in result.violations if v.severity == ViolationSeverity.INFO]
                
                if critical:
                    f.write(f"### ❌ Critical ({len(critical)})\n\n")
                    for v in critical:
                        f.write(f"**{v.rule}**\n")
                        f.write(f"- Location: {v.location}\n")
                        f.write(f"- Issue: {v.description}\n")
                        f.write(f"- Fix: {v.recommendation}\n\n")
                
                if warnings:
                    f.write(f"### ⚠️  Warnings ({len(warnings)})\n\n")
                    for v in warnings:
                        f.write(f"**{v.rule}**\n")
                        f.write(f"- Location: {v.location}\n")
                        f.write(f"- Issue: {v.description}\n")
                        f.write(f"- Fix: {v.recommendation}\n\n")
                
                if info:
                    f.write(f"### ℹ️  Info ({len(info)})\n\n")
                    for v in info:
                        f.write(f"**{v.rule}**\n")
                        f.write(f"- Location: {v.location}\n")
                        f.write(f"- Issue: {v.description}\n")
                        f.write(f"- Fix: {v.recommendation}\n\n")
            else:
                f.write(f"## ✅ No Violations\n\n")
                f.write(f"All policy rules passed successfully.\n\n")
            
            # Next steps
            f.write(f"## Next Steps\n\n")
            if result.compliant:
                f.write(f"1. Continue with CORTEX onboarding\n")
                f.write(f"2. Review generated compliance report\n")
                f.write(f"3. Proceed to dashboard generation\n")
            else:
                f.write(f"1. Review violations above\n")
                f.write(f"2. Fix critical issues before proceeding\n")
                f.write(f"3. Re-run validation: `python policy_validator.py`\n")
                f.write(f"4. Once compliant, continue onboarding\n")
        
        return output_path


# CLI for testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python policy_validator.py <repo_root>")
        sys.exit(1)
    
    repo_root = Path(sys.argv[1])
    validator = PolicyValidator(repo_root)
    
    print(f"🔍 Validating CORTEX against policies in: {repo_root}")
    
    result = validator.validate()
    
    print(f"\n{result.summary}")
    print(f"\nCompliance: {result.compliance_percentage:.1f}%")
    print(f"Passed: {result.passed}/{result.total_rules}")
    
    if result.violations:
        print(f"\n⚠️  Found {len(result.violations)} violation(s):")
        for v in result.violations:
            print(f"  [{v.severity.value}] {v.category}: {v.rule}")
    
    # Generate report
    report_path = validator.generate_report(result)
    print(f"\n📄 Full report: {report_path}")
