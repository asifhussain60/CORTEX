# LENS Governance Integration

**Purpose:** How LENS integrates with CORTEX governance  
**Audience:** Architects, Security Teams  
**Last Updated:** 2026-02-10

---

## Table of Contents

- [Overview](#overview)
- [Governance Context Provision](#governance-context-provision)
- [Rule Validation Support](#rule-validation-support)
- [Security Analysis](#security-analysis)
- [Compliance Checking](#compliance-checking)
- [Related Documents](#related-documents)

---

## Overview

LENS provides contextual intelligence that powers governance enforcement. Without LENS context, governance rules would operate blindly. With LENS, enforcement agents have full visibility into code structure, history, and patterns.

```
┌─────────────────────────────────────────────────────────────────┐
│              LENS + GOVERNANCE INTEGRATION                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                        LENS                              │   │
│  │  Git │ AST │ Comments │ Patterns │ Config │ Security    │   │
│  └───────────────────────────┬─────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              UnifiedIntelligenceContext                  │   │
│  │  • File changes      • Anti-patterns                    │   │
│  │  • Code structure    • Security findings                │   │
│  │  • Dependencies      • Complexity metrics               │   │
│  └───────────────────────────┬─────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │            EnforcementOrchestrator                       │   │
│  │                                                          │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐       │   │
│  │  │Governance│ │Security │ │Compliance│ │ FileNaming│    │   │
│  │  │ Agent   │ │ Agent   │ │  Agent   │ │  Agent  │       │   │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘       │   │
│  │                                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Governance Context Provision

### Context Fields for Governance

| Context Field | Governance Use |
|---------------|----------------|
| `ast_analysis` | Type hints, docstrings validation |
| `git_insights` | Checkpoint verification |
| `detected_patterns` | Architecture compliance |
| `anti_patterns` | Code smell blocking |
| `comment_analysis` | TODO tracking, doc coverage |
| `complexity_hotspots` | Complexity threshold enforcement |

### Context Enrichment for Enforcement

```python
class GovernanceContextEnricher:
    """Enriches LENS context for governance use."""
    
    def enrich_for_governance(
        self,
        context: UnifiedIntelligenceContext
    ) -> GovernanceContext:
        """
        Transform LENS context for governance agents.
        """
        return GovernanceContext(
            # CORE-008: TDD Enforcement
            has_tests=self._check_test_presence(context),
            test_coverage=self._calculate_coverage(context),
            
            # CORE-011: Type Hints
            type_hint_coverage=self._type_hint_coverage(context),
            missing_type_hints=self._find_missing_hints(context),
            
            # CORE-012: Docstrings
            docstring_coverage=context.docstring_coverage,
            missing_docstrings=self._find_missing_docs(context),
            
            # CORE-026: Git Checkpoints
            recent_commits=context.recent_commits,
            has_checkpoint=self._check_checkpoint(context),
            
            # CORE-028: File Naming
            file_names=self._extract_file_names(context),
            naming_violations=self._check_naming(context),
            
            # CORE-035: Duplication
            duplicates=context.anti_patterns.get("duplicates", []),
            
            # Security
            security_findings=self._extract_security(context),
            
            # Complexity
            complexity_violations=self._check_complexity(context)
        )
```

---

## Rule Validation Support

### CORE-008: TDD Enforcement

```python
class TDDValidationSupport:
    """LENS support for TDD rule validation."""
    
    def validate_tdd(
        self,
        context: UnifiedIntelligenceContext,
        target_files: List[str]
    ) -> TDDValidationResult:
        """
        Validate TDD compliance using LENS context.
        """
        # Check for test files
        test_files = self._find_test_files(context, target_files)
        
        if not test_files:
            return TDDValidationResult(
                passed=False,
                reason="No test files found for implementation",
                missing_tests=target_files
            )
        
        # Check test-to-code ratio
        code_lines = sum(
            f.line_count for f in context.file_context.files
            if not f.is_test
        )
        test_lines = sum(
            f.line_count for f in context.file_context.files
            if f.is_test
        )
        
        ratio = test_lines / max(code_lines, 1)
        
        if ratio < 0.5:  # At least 50% test-to-code ratio
            return TDDValidationResult(
                passed=False,
                reason=f"Test ratio too low: {ratio:.2f}",
                current_ratio=ratio,
                required_ratio=0.5
            )
        
        return TDDValidationResult(passed=True)
```

### CORE-011: Type Hints

```python
class TypeHintValidationSupport:
    """LENS support for type hint validation."""
    
    def validate_type_hints(
        self,
        context: UnifiedIntelligenceContext
    ) -> TypeHintValidationResult:
        """
        Validate type hint presence using AST analysis.
        """
        functions = context.ast_analysis.functions
        
        missing = []
        for func in functions:
            if not func.return_type:
                missing.append({
                    "function": func.name,
                    "file": func.file,
                    "line": func.line_start,
                    "issue": "Missing return type"
                })
            
            for param in func.parameters:
                if not param.type_annotation:
                    missing.append({
                        "function": func.name,
                        "parameter": param.name,
                        "file": func.file,
                        "line": func.line_start,
                        "issue": "Missing parameter type"
                    })
        
        coverage = 1 - (len(missing) / max(len(functions) * 3, 1))
        
        return TypeHintValidationResult(
            passed=coverage >= 0.95,
            coverage=coverage,
            missing=missing
        )
```

### CORE-035: Duplication Detection

```python
class DuplicationValidationSupport:
    """LENS support for duplication detection."""
    
    def validate_duplication(
        self,
        context: UnifiedIntelligenceContext
    ) -> DuplicationValidationResult:
        """
        Check for code duplication using pattern analysis.
        """
        duplicates = [
            ap for ap in context.anti_patterns
            if ap.type == "duplicate_code"
        ]
        
        if not duplicates:
            return DuplicationValidationResult(passed=True)
        
        # Categorize by severity
        critical = [d for d in duplicates if d.lines > 50]
        warning = [d for d in duplicates if 20 <= d.lines <= 50]
        info = [d for d in duplicates if d.lines < 20]
        
        return DuplicationValidationResult(
            passed=len(critical) == 0,
            critical=critical,
            warning=warning,
            info=info,
            total_duplicate_lines=sum(d.lines for d in duplicates)
        )
```

---

## Security Analysis

### Security Context from LENS

```python
class SecurityContextProvider:
    """Provides security context from LENS analysis."""
    
    def get_security_context(
        self,
        context: UnifiedIntelligenceContext
    ) -> SecurityContext:
        """
        Extract security-relevant information.
        """
        return SecurityContext(
            # Secrets detection
            potential_secrets=self._find_secrets(context),
            
            # Dependency vulnerabilities
            vulnerable_deps=self._check_dependencies(context),
            
            # Injection risks
            injection_points=self._find_injection_points(context),
            
            # Auth patterns
            auth_patterns=self._analyze_auth(context),
            
            # OWASP findings
            owasp_findings=self._check_owasp(context)
        )
    
    def _find_secrets(
        self,
        context: UnifiedIntelligenceContext
    ) -> List[SecretFinding]:
        """Find potential hardcoded secrets."""
        findings = []
        
        SECRET_PATTERNS = [
            r"password\s*=\s*['\"].*['\"]",
            r"api_key\s*=\s*['\"].*['\"]",
            r"secret\s*=\s*['\"].*['\"]",
            r"-----BEGIN.*PRIVATE KEY-----",
        ]
        
        for file_info in context.file_context.files:
            for pattern in SECRET_PATTERNS:
                matches = re.findall(pattern, file_info.content, re.I)
                for match in matches:
                    findings.append(SecretFinding(
                        file=file_info.path,
                        pattern=pattern,
                        snippet=match[:50] + "..."
                    ))
        
        return findings
```

### Security Agent Integration

```python
class SecurityCheckpointAgent:
    """Uses LENS for security checkpoint validation."""
    
    def __init__(self, lens: LENSOrchestrator):
        self.lens = lens
        self.security_provider = SecurityContextProvider()
    
    async def validate(
        self,
        request: Request,
        context: UnifiedIntelligenceContext
    ) -> ValidationResult:
        """
        Validate security using LENS context.
        """
        security = self.security_provider.get_security_context(context)
        
        violations = []
        
        # Check for secrets
        if security.potential_secrets:
            violations.append(Violation(
                rule="CORE-025",
                severity="CRITICAL",
                message=f"Potential secrets detected: {len(security.potential_secrets)}",
                details=security.potential_secrets
            ))
        
        # Check for vulnerabilities
        if security.vulnerable_deps:
            violations.append(Violation(
                rule="ARCH-SECURITY",
                severity="HIGH",
                message=f"Vulnerable dependencies: {len(security.vulnerable_deps)}",
                details=security.vulnerable_deps
            ))
        
        return ValidationResult(
            passed=len(violations) == 0,
            violations=violations
        )
```

---

## Compliance Checking

### Standards Compliance

```python
class ComplianceChecker:
    """Uses LENS for standards compliance checking."""
    
    STANDARDS = {
        "12-factor": TwelveFactorChecker(),
        "solid": SOLIDChecker(),
        "clean-code": CleanCodeChecker(),
        "owasp": OWASPChecker(),
    }
    
    def check_compliance(
        self,
        context: UnifiedIntelligenceContext,
        standards: List[str]
    ) -> ComplianceReport:
        """
        Check compliance against specified standards.
        """
        results = {}
        
        for standard in standards:
            checker = self.STANDARDS.get(standard)
            if checker:
                results[standard] = checker.check(context)
        
        return ComplianceReport(
            results=results,
            overall_score=self._calculate_overall(results),
            recommendations=self._generate_recommendations(results)
        )
```

### Architecture Compliance

```python
class ArchitectureComplianceChecker:
    """Check architecture patterns using LENS."""
    
    def check_architecture(
        self,
        context: UnifiedIntelligenceContext
    ) -> ArchitectureComplianceResult:
        """
        Validate architecture patterns.
        """
        issues = []
        
        # Check for god classes
        god_classes = [
            ap for ap in context.anti_patterns
            if ap.type == "god_class"
        ]
        if god_classes:
            issues.append(ArchitectureIssue(
                type="god_class",
                severity="HIGH",
                classes=god_classes
            ))
        
        # Check for circular dependencies
        circular = self._find_circular_deps(
            context.dependency_graph
        )
        if circular:
            issues.append(ArchitectureIssue(
                type="circular_dependency",
                severity="CRITICAL",
                cycles=circular
            ))
        
        # Check layer violations
        layer_violations = self._check_layers(context)
        if layer_violations:
            issues.append(ArchitectureIssue(
                type="layer_violation",
                severity="HIGH",
                violations=layer_violations
            ))
        
        return ArchitectureComplianceResult(
            passed=len([i for i in issues if i.severity == "CRITICAL"]) == 0,
            issues=issues
        )
```

---

## Related Documents

- [Governance & Compliance](../capabilities/governance-compliance.md) — Governance overview
- [LENS Overview](overview.md) — LENS introduction
- [Analyzers](analyzers.md) — Analyzer details

---

*Part of CORTEX Architecture Documentation*
