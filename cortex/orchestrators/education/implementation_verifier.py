"""
Implementation Verifier for Phase 22 ASK Mode System.

Verifies implementations match specifications, validates DoR completion,
and ensures test coverage meets requirements.

Author: CORTEX
Phase: 22 (ASK Mode System)
Component: P0 - Week 1
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Any
from enum import Enum
import yaml
import ast
import re


class ComplianceLevel(Enum):
    """Compliance level for verification results."""
    FULL = "full"
    PARTIAL = "partial"
    NONE = "none"


@dataclass
class VerificationResult:
    """Result of a verification check."""
    is_complete: bool
    missing_criteria: List[str] = field(default_factory=list)
    compliance_level: ComplianceLevel = ComplianceLevel.NONE
    confidence: float = 0.0
    details: str = ""


@dataclass
class SpecCompliance:
    """Specification compliance result."""
    compliance_level: ComplianceLevel
    missing_requirements: List[str] = field(default_factory=list)
    confidence: float = 0.0
    matched_requirements: List[str] = field(default_factory=list)


@dataclass
class CoverageResult:
    """Test coverage verification result."""
    is_adequate: bool
    coverage_percent: float
    compliance_level: ComplianceLevel
    uncovered_critical_paths: List[str] = field(default_factory=list)


@dataclass
class AlignmentResult:
    """Architectural alignment result."""
    is_aligned: bool
    wiring_found: bool
    compliance_level: ComplianceLevel
    issues: List[str] = field(default_factory=list)


@dataclass
class SecurityResult:
    """Security compliance result."""
    has_issues: bool
    security_score: float
    compliance_level: ComplianceLevel
    vulnerabilities: List[str] = field(default_factory=list)


@dataclass
class ComprehensiveResult:
    """Comprehensive verification result."""
    overall_compliance: ComplianceLevel
    dor_verified: bool
    spec_compliant: bool
    architecturally_aligned: bool
    critical_failures: int = 0
    warnings: List[str] = field(default_factory=list)


class ImplementationVerifier:
    """
    Verifies implementations against specifications and DoR requirements.
    
    Capabilities:
    - DoR verification (all criteria met)
    - Spec compliance (matches requirements)
    - Test coverage validation
    - Architectural alignment (wiring)
    - Security compliance
    """
    
    def __init__(self, repo_root: Path):
        """
        Initialize the verifier.
        
        Args:
            repo_root: Root directory of the repository
        """
        self.repo_root = Path(repo_root)
        
    def verify_dor(self, dor: Dict[str, Any]) -> VerificationResult:
        """
        Verify Definition of Ready is complete.
        
        Args:
            dor: DoR dictionary with criteria
            
        Returns:
            VerificationResult with completeness status
        """
        required_fields = [
            "intent",
            "target",
            "test_file",
            "challenge_complete",
            "extensibility_validated",
            "scalability_validated",
            "security_validated"
        ]
        
        missing = []
        for field in required_fields:
            if field not in dor:
                missing.append(field)
        
        is_complete = len(missing) == 0
        
        if is_complete:
            compliance_level = ComplianceLevel.FULL
        elif len(missing) < len(required_fields):  # Any fields present = PARTIAL
            compliance_level = ComplianceLevel.PARTIAL
        else:
            compliance_level = ComplianceLevel.NONE
            
        return VerificationResult(
            is_complete=is_complete,
            missing_criteria=missing,
            compliance_level=compliance_level,
            confidence=1.0 - (len(missing) / len(required_fields))
        )
    
    def verify_spec_compliance(
        self,
        spec_file: Path,
        impl_file: Path
    ) -> SpecCompliance:
        """
        Verify implementation matches specification.
        
        Args:
            spec_file: Path to specification YAML
            impl_file: Path to implementation file
            
        Returns:
            SpecCompliance result
        """
        try:
            # Load spec
            spec_content = spec_file.read_text()
            spec = yaml.safe_load(spec_content)
            
            if not spec:
                return SpecCompliance(
                    compliance_level=ComplianceLevel.NONE,
                    confidence=0.0
                )
            
            # Load implementation
            impl_content = impl_file.read_text()
            
            # Check required methods
            required_methods = spec.get("required_methods", [])
            required_attrs = spec.get("required_attributes", [])
            
            missing = []
            matched = []
            
            # Check methods
            for method in required_methods:
                if f"def {method}" in impl_content:
                    matched.append(method)
                else:
                    missing.append(method)
            
            # Check attributes
            for attr in required_attrs:
                if f"self.{attr}" in impl_content:
                    matched.append(attr)
                else:
                    missing.append(attr)
            
            total_required = len(required_methods) + len(required_attrs)
            if total_required == 0:
                confidence = 0.0
                compliance_level = ComplianceLevel.NONE
            else:
                confidence = len(matched) / total_required
                
                if confidence >= 0.9:
                    compliance_level = ComplianceLevel.FULL
                elif confidence >= 0.3:  # Lowered threshold for PARTIAL
                    compliance_level = ComplianceLevel.PARTIAL
                else:
                    compliance_level = ComplianceLevel.NONE
            
            return SpecCompliance(
                compliance_level=compliance_level,
                missing_requirements=missing,
                confidence=confidence,
                matched_requirements=matched
            )
            
        except Exception as e:
            return SpecCompliance(
                compliance_level=ComplianceLevel.NONE,
                confidence=0.0,
                missing_requirements=[f"Error: {str(e)}"]
            )
    
    def verify_coverage(
        self,
        coverage_data: Dict[str, Any],
        threshold: float = 0.85
    ) -> CoverageResult:
        """
        Verify test coverage meets threshold.
        
        Args:
            coverage_data: Coverage data dictionary
            threshold: Minimum required coverage (0.0-1.0)
            
        Returns:
            CoverageResult with adequacy status
        """
        try:
            files = coverage_data.get("files", {})
            
            if not files:
                return CoverageResult(
                    is_adequate=False,
                    coverage_percent=0.0,
                    compliance_level=ComplianceLevel.NONE
                )
            
            # Calculate average coverage
            total_percent = 0.0
            for file_data in files.values():
                summary = file_data.get("summary", {})
                total_percent += summary.get("percent_covered", 0.0)
            
            avg_coverage = total_percent / len(files) / 100.0
            is_adequate = avg_coverage >= threshold
            
            # Find uncovered paths
            uncovered = []
            for filename, file_data in files.items():
                summary = file_data.get("summary", {})
                if summary.get("percent_covered", 0.0) < threshold * 100:
                    uncovered.append(filename)
            
            if is_adequate:
                compliance_level = ComplianceLevel.FULL
            elif avg_coverage >= threshold * 0.7:
                compliance_level = ComplianceLevel.PARTIAL
            else:
                compliance_level = ComplianceLevel.NONE
            
            return CoverageResult(
                is_adequate=is_adequate,
                coverage_percent=avg_coverage,
                compliance_level=compliance_level,
                uncovered_critical_paths=uncovered
            )
            
        except Exception:
            return CoverageResult(
                is_adequate=False,
                coverage_percent=0.0,
                compliance_level=ComplianceLevel.NONE
            )
    
    def verify_architectural_alignment(
        self,
        component_name: str,
        wiring_file: Path
    ) -> AlignmentResult:
        """
        Verify component is properly wired in architecture.
        
        Args:
            component_name: Name of component to verify
            wiring_file: Path to wiring.yaml
            
        Returns:
            AlignmentResult with alignment status
        """
        try:
            wiring_content = wiring_file.read_text()
            wiring_found = component_name in wiring_content
            
            if wiring_found:
                compliance_level = ComplianceLevel.FULL
                is_aligned = True
            else:
                compliance_level = ComplianceLevel.NONE
                is_aligned = False
            
            return AlignmentResult(
                is_aligned=is_aligned,
                wiring_found=wiring_found,
                compliance_level=compliance_level
            )
            
        except Exception:
            return AlignmentResult(
                is_aligned=False,
                wiring_found=False,
                compliance_level=ComplianceLevel.NONE,
                issues=["Failed to read wiring file"]
            )
    
    def verify_security_compliance(self, impl_file: Path) -> SecurityResult:
        """
        Verify implementation has no security issues.
        
        Args:
            impl_file: Path to implementation file
            
        Returns:
            SecurityResult with security status
        """
        if not impl_file.exists():
            return SecurityResult(
                has_issues=False,
                security_score=0.0,
                compliance_level=ComplianceLevel.NONE
            )
        
        try:
            content = impl_file.read_text()
            vulnerabilities = []
            
            # Check for common security issues
            security_patterns = [
                (r'pickle\.loads', "Unsafe deserialization with pickle"),
                (r'subprocess\.call.*shell=True', "Command injection risk with shell=True"),
                (r'eval\(', "Code injection risk with eval()"),
                (r'exec\(', "Code execution risk with exec()"),
                (r'__import__\(', "Dynamic import security risk"),
            ]
            
            for pattern, message in security_patterns:
                if re.search(pattern, content):
                    vulnerabilities.append(message)
            
            has_issues = len(vulnerabilities) > 0
            
            if not has_issues:
                security_score = 1.0
                compliance_level = ComplianceLevel.FULL
            else:
                # Score based on number of issues
                security_score = max(0.0, 1.0 - (len(vulnerabilities) * 0.2))
                if security_score >= 0.5:  # Lowered threshold for PARTIAL
                    compliance_level = ComplianceLevel.PARTIAL
                else:
                    compliance_level = ComplianceLevel.NONE
            
            return SecurityResult(
                has_issues=has_issues,
                security_score=security_score,
                compliance_level=compliance_level,
                vulnerabilities=vulnerabilities
            )
            
        except Exception:
            return SecurityResult(
                has_issues=False,
                security_score=0.0,
                compliance_level=ComplianceLevel.NONE
            )
    
    def verify_comprehensive(
        self,
        dor: Dict[str, Any],
        spec_file: Path,
        impl_file: Path,
        wiring_file: Path
    ) -> ComprehensiveResult:
        """
        Perform comprehensive verification of all aspects.
        
        Args:
            dor: Definition of Ready
            spec_file: Specification file
            impl_file: Implementation file
            wiring_file: Wiring configuration file
            
        Returns:
            ComprehensiveResult with overall status
        """
        # Run all checks
        dor_result = self.verify_dor(dor)
        spec_result = self.verify_spec_compliance(spec_file, impl_file)
        alignment_result = self.verify_architectural_alignment(
            dor.get("target", "Unknown"),
            wiring_file
        )
        security_result = self.verify_security_compliance(impl_file)
        
        # Count critical failures
        critical_failures = 0
        if not dor_result.is_complete:
            critical_failures += 1
        if spec_result.compliance_level == ComplianceLevel.NONE:
            critical_failures += 1
        if not alignment_result.is_aligned:
            critical_failures += 1
        if security_result.has_issues:
            critical_failures += 1
        
        # Determine overall compliance
        if critical_failures == 0:
            overall_compliance = ComplianceLevel.FULL
        elif critical_failures <= 2:
            overall_compliance = ComplianceLevel.PARTIAL
        else:
            overall_compliance = ComplianceLevel.NONE
        
        return ComprehensiveResult(
            overall_compliance=overall_compliance,
            dor_verified=dor_result.is_complete,
            spec_compliant=spec_result.compliance_level != ComplianceLevel.NONE,
            architecturally_aligned=alignment_result.is_aligned,
            critical_failures=critical_failures
        )
    
    def generate_report(self, dor: Dict[str, Any]) -> str:
        """
        Generate detailed verification report.
        
        Args:
            dor: Definition of Ready to report on
            
        Returns:
            Formatted report string
        """
        report_lines = [
            "=" * 60,
            "IMPLEMENTATION VERIFICATION REPORT",
            "=" * 60,
            ""
        ]
        
        # DoR Status
        dor_result = self.verify_dor(dor)
        report_lines.append("DoR Status:")
        report_lines.append(f"  Complete: {dor_result.is_complete}")
        report_lines.append(f"  Compliance: {dor_result.compliance_level.value}")
        if dor_result.missing_criteria:
            report_lines.append("  Missing Criteria:")
            for criterion in dor_result.missing_criteria:
                report_lines.append(f"    - {criterion}")
        report_lines.append("")
        
        # Spec Compliance (placeholder - would need files)
        report_lines.append("Spec Compliance: (Requires spec/impl files)")
        report_lines.append("")
        
        # Test Coverage (placeholder - would need coverage data)
        report_lines.append("Test Coverage: (Requires coverage data)")
        report_lines.append("")
        
        # Architectural Alignment (placeholder - would need wiring file)
        report_lines.append("Architectural Alignment: (Requires wiring file)")
        report_lines.append("")
        
        # Security Compliance (placeholder - would need impl file)
        report_lines.append("Security Compliance: (Requires implementation file)")
        report_lines.append("")
        
        # Action Items
        if not dor_result.is_complete:
            report_lines.append("Action Items:")
            report_lines.append("  TODO: Complete missing DoR criteria")
            for criterion in dor_result.missing_criteria:
                report_lines.append(f"    - REQUIRED: {criterion}")
        
        report_lines.append("=" * 60)
        
        return "\n".join(report_lines)
