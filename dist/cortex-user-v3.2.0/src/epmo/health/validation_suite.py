"""
CORTEX 3.0 - EPMO Health Validation Suite
=========================================

Phase 3 - Track A: EPMO Health A3 Implementation
Comprehensive validation framework for Entry Point Module (EPMO) health assessment.

This module implements the validation suite that evaluates EPMO health across multiple dimensions:
- Code quality metrics
- Documentation completeness  
- Test coverage and quality
- Performance characteristics
- Architecture compliance

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Phase: 3 - Validation & Completion
Timeline: Week 9 (A3: Health Validation Suite)
Effort: 16 hours
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import logging
import time

logger = logging.getLogger(__name__)


class HealthDimension(Enum):
    """Health assessment dimensions for EPMOs."""
    CODE_QUALITY = "code_quality"
    DOCUMENTATION = "documentation"
    TEST_COVERAGE = "test_coverage"
    PERFORMANCE = "performance"
    ARCHITECTURE = "architecture"
    MAINTAINABILITY = "maintainability"


class ValidationSeverity(Enum):
    """Validation issue severity levels."""
    CRITICAL = "critical"      # Blocks production deployment
    HIGH = "high"             # Significant impact on maintainability
    MEDIUM = "medium"         # Should be addressed in next cycle
    LOW = "low"               # Technical debt, address when convenient
    INFO = "info"             # Informational, no action required


@dataclass
class ValidationResult:
    """Result of a single validation check."""
    dimension: HealthDimension
    check_name: str
    severity: ValidationSeverity
    score: float  # 0.0 to 1.0
    max_score: float = 1.0
    message: str = ""
    details: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        """Initialize metadata if not provided."""
        if self.metadata is None:
            self.metadata = {'dimension': self.dimension, 'check_id': self.check_name}
    
    @property
    def check_id(self) -> str:
        """Get check_id as alias for check_name."""
        return self.check_name
    
    @property
    def percentage(self) -> float:
        """Get score as percentage."""
        return (self.score / self.max_score) * 100.0 if self.max_score > 0 else 0.0
    
    @property
    def is_passing(self) -> bool:
        """Check if validation passes minimum threshold."""
        return self.percentage >= 70.0  # 70% minimum passing score


@dataclass
class EPMOHealthReport:
    """Comprehensive health report for an EPMO."""
    epmo_name: str
    module_path: Path
    validation_results: List[ValidationResult]
    overall_score: float
    overall_grade: str  # A, B, C, D, F
    timestamp: str
    
    @property
    def dimension_scores(self) -> Dict[HealthDimension, float]:
        """Get average scores by dimension."""
        dimension_totals = {}
        dimension_counts = {}
        
        for result in self.validation_results:
            dim = result.dimension
            if dim not in dimension_totals:
                dimension_totals[dim] = 0.0
                dimension_counts[dim] = 0
            
            dimension_totals[dim] += result.percentage
            dimension_counts[dim] += 1
        
        return {
            dim: dimension_totals[dim] / dimension_counts[dim]
            for dim in dimension_totals
        }
    
    @property
    def critical_issues(self) -> List[ValidationResult]:
        """Get all critical validation issues."""
        return [r for r in self.validation_results if r.severity == ValidationSeverity.CRITICAL]
    
    @property
    def is_healthy(self) -> bool:
        """Check if EPMO meets health threshold (≥85/100)."""
        return self.overall_score >= 85.0


class EPMOHealthValidator:
    """
    Comprehensive EPMO health validation engine.
    
    Evaluates Entry Point Modules across 6 dimensions using 30+ validation tests.
    Provides detailed reporting and actionable remediation guidance.
    """
    
    def __init__(self, project_root: Path = None):
        """
        Initialize validator with project context.
        
        Args:
            project_root: Root path of the CORTEX project (defaults to current directory)
        """
        self.project_root = project_root or Path('.')
        self.validation_cache = {}
        self._load_validators()
    
    def _load_validators(self) -> None:
        """Load all validation modules."""
        from .validators.code_quality_validator import CodeQualityValidator
        from .validators.documentation_validator import DocumentationValidator
        from .validators.test_coverage_validator import TestCoverageValidator
        from .validators.performance_validator import PerformanceValidator
        from .validators.architecture_validator import ArchitectureValidator
        from .validators.maintainability_validator import MaintainabilityValidator
        
        self.validators = {
            HealthDimension.CODE_QUALITY: CodeQualityValidator(),
            HealthDimension.DOCUMENTATION: DocumentationValidator(),
            HealthDimension.TEST_COVERAGE: TestCoverageValidator(),
            HealthDimension.PERFORMANCE: PerformanceValidator(),
            HealthDimension.ARCHITECTURE: ArchitectureValidator(),
            HealthDimension.MAINTAINABILITY: MaintainabilityValidator()
        }
        
        logger.info(f"Loaded {len(self.validators)} validation dimensions")
    
    def validate_epmo(self, epmo_path: Path) -> EPMOHealthReport:
        """
        Perform comprehensive validation of an EPMO.
        
        Args:
            epmo_path: Path to EPMO module
            
        Returns:
            Complete health report with scores and recommendations
        """
        start_time = time.time()
        epmo_name = epmo_path.name
        
        logger.info(f"Starting validation of EPMO: {epmo_name}")
        
        # Run validation across all dimensions
        all_results = []
        dimension_scores = {}
        
        for dimension, validator in self.validators.items():
            try:
                results = validator.validate(epmo_path, self.project_root)
                all_results.extend(results)
                
                # Calculate dimension score
                dim_score = sum(r.percentage for r in results) / len(results) if results else 0.0
                dimension_scores[dimension] = dim_score
                
                logger.debug(f"{dimension.value}: {dim_score:.1f}% ({len(results)} checks)")
                
            except Exception as e:
                logger.error(f"Validation failed for {dimension.value}: {e}")
                # Add error result
                error_result = ValidationResult(
                    dimension=dimension,
                    check_name="validation_error",
                    severity=ValidationSeverity.CRITICAL,
                    score=0.0,
                    message=f"Validation failed: {str(e)}"
                )
                all_results.append(error_result)
                dimension_scores[dimension] = 0.0
        
        # Calculate overall score (weighted average)
        weights = {
            HealthDimension.CODE_QUALITY: 0.25,      # 25%
            HealthDimension.DOCUMENTATION: 0.15,     # 15%
            HealthDimension.TEST_COVERAGE: 0.20,     # 20%
            HealthDimension.PERFORMANCE: 0.10,       # 10%
            HealthDimension.ARCHITECTURE: 0.20,      # 20%
            HealthDimension.MAINTAINABILITY: 0.10    # 10%
        }
        
        overall_score = sum(
            dimension_scores.get(dim, 0.0) * weight
            for dim, weight in weights.items()
        )
        
        # Calculate grade
        overall_grade = self._calculate_grade(overall_score)
        
        # Create report
        report = EPMOHealthReport(
            epmo_name=epmo_name,
            module_path=epmo_path,
            validation_results=all_results,
            overall_score=overall_score,
            overall_grade=overall_grade,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
        )
        
        validation_time = time.time() - start_time
        logger.info(f"Completed validation of {epmo_name} in {validation_time:.2f}s - Score: {overall_score:.1f}% (Grade: {overall_grade})")
        
        return report
    
    def validate_all_epmos(self) -> Dict[str, EPMOHealthReport]:
        """
        Validate all EPMOs in the project.
        
        Returns:
            Dictionary mapping EPMO names to their health reports
        """
        logger.info("Starting validation of all EPMOs")
        
        # Discover all EPMOs
        epmo_paths = self._discover_epmos()
        logger.info(f"Found {len(epmo_paths)} EPMOs to validate")
        
        # Validate each EPMO
        reports = {}
        for epmo_path in epmo_paths:
            try:
                report = self.validate_epmo(epmo_path)
                reports[report.epmo_name] = report
            except Exception as e:
                logger.error(f"Failed to validate EPMO {epmo_path.name}: {e}")
        
        # Generate summary statistics
        if reports:
            avg_score = sum(r.overall_score for r in reports.values()) / len(reports)
            healthy_count = sum(1 for r in reports.values() if r.is_healthy)
            
            logger.info(f"Validation complete - Average score: {avg_score:.1f}%, Healthy: {healthy_count}/{len(reports)}")
        
        return reports
    
    def _discover_epmos(self) -> List[Path]:
        """
        Discover all Entry Point Modules in the project.
        
        EPMOs are identified as Python modules in src/ that contain entry point logic.
        """
        epmo_paths = []
        
        # Search for entry point modules
        src_path = self.project_root / "src"
        if not src_path.exists():
            logger.warning(f"Source directory not found: {src_path}")
            return []
        
        # Look for common EPMO patterns
        epmo_patterns = [
            "entry_point",
            "operations",
            "**/cortex_*.py",
            "**/main.py",
            "**/cli.py",
            "**/*_entry.py"
        ]
        
        for pattern in epmo_patterns:
            matches = list(src_path.glob(pattern))
            for match in matches:
                if match.is_file() and match.suffix == ".py":
                    epmo_paths.append(match)
                elif match.is_dir():
                    # Check if directory contains __init__.py or main module
                    init_file = match / "__init__.py"
                    if init_file.exists():
                        epmo_paths.append(match)
        
        # Remove duplicates and sort
        unique_paths = sorted(set(epmo_paths))
        
        logger.debug(f"Discovered EPMO paths: {[p.name for p in unique_paths]}")
        return unique_paths
    
    def _calculate_grade(self, score: float) -> str:
        """Calculate letter grade from numeric score."""
        if score >= 90.0:
            return "A"
        elif score >= 80.0:
            return "B"
        elif score >= 70.0:
            return "C"
        elif score >= 60.0:
            return "D"
        else:
            return "F"
    
    def get_health_summary(self, reports: Dict[str, EPMOHealthReport]) -> Dict[str, Any]:
        """
        Generate project-wide health summary.
        
        Args:
            reports: Dictionary of EPMO health reports
            
        Returns:
            Summary statistics and recommendations
        """
        if not reports:
            return {"error": "No EPMO reports available"}
        
        # Calculate summary statistics
        scores = [r.overall_score for r in reports.values()]
        avg_score = sum(scores) / len(scores)
        min_score = min(scores)
        max_score = max(scores)
        
        # Count by grade
        grade_counts = {}
        for report in reports.values():
            grade = report.overall_grade
            grade_counts[grade] = grade_counts.get(grade, 0) + 1
        
        # Count healthy vs unhealthy
        healthy_count = sum(1 for r in reports.values() if r.is_healthy)
        unhealthy_count = len(reports) - healthy_count
        
        # Identify critical issues
        critical_issues = []
        for report in reports.values():
            critical_issues.extend(report.critical_issues)
        
        # Generate recommendations
        recommendations = []
        if avg_score < 85.0:
            recommendations.append(f"Average health score ({avg_score:.1f}%) is below target (85%). Focus on lowest-scoring EPMOs.")
        
        if critical_issues:
            recommendations.append(f"Address {len(critical_issues)} critical issues immediately.")
        
        if unhealthy_count > 0:
            recommendations.append(f"Remediate {unhealthy_count} unhealthy EPMOs to meet compliance standards.")
        
        return {
            "total_epmos": len(reports),
            "average_score": round(avg_score, 1),
            "min_score": round(min_score, 1),
            "max_score": round(max_score, 1),
            "healthy_epmos": healthy_count,
            "unhealthy_epmos": unhealthy_count,
            "grade_distribution": grade_counts,
            "critical_issues": len(critical_issues),
            "meets_target": avg_score >= 85.0,
            "recommendations": recommendations
        }
    
    def validate_epmo_health(self, epmo_path: Path, project_root: Path = None) -> Dict[str, Any]:
        """
        Validate EPMO health and return structured report.
        
        Args:
            epmo_path: Path to EPMO module
            project_root: Project root path (optional, defaults to self.project_root)
            
        Returns:
            Structured health report dictionary
        """
        if project_root:
            original_root = self.project_root
            self.project_root = project_root
        
        try:
            # Get the full health report
            report = self.validate_epmo(epmo_path)
            
            # Convert to structured dictionary format expected by integration layer
            dimension_scores = {}
            all_results_by_dimension = {}
            
            # Group results by dimension
            for result in report.validation_results:
                dim = result.dimension
                if dim not in all_results_by_dimension:
                    all_results_by_dimension[dim] = []
                all_results_by_dimension[dim].append(result)
            
            # Calculate dimension scores and weights
            weights = {
                HealthDimension.CODE_QUALITY: 0.25,      # 25%
                HealthDimension.DOCUMENTATION: 0.15,     # 15%
                HealthDimension.TEST_COVERAGE: 0.20,     # 20%
                HealthDimension.PERFORMANCE: 0.10,       # 10%
                HealthDimension.ARCHITECTURE: 0.20,      # 20%
                HealthDimension.MAINTAINABILITY: 0.10    # 10%
            }
            
            for dimension, results in all_results_by_dimension.items():
                if results:
                    dim_score = sum(r.percentage for r in results) / len(results)
                else:
                    dim_score = 0.0
                
                # Serialize ValidationResult objects for JSON compatibility
                serialized_results = []
                for result in results:
                    serialized_results.append({
                        'dimension': result.dimension.value,
                        'check_name': result.check_name,
                        'severity': result.severity.value,
                        'score': result.score,
                        'max_score': result.max_score,
                        'message': result.message,
                        'details': result.details,
                        'metadata': result.metadata
                    })
                
                dimension_scores[dimension.value] = {  # Convert enum to string
                    'score': dim_score,
                    'weight': weights.get(dimension, 0.1),
                    'weighted_score': dim_score * weights.get(dimension, 0.1),
                    'results': serialized_results,
                    'original_results': results  # Keep original objects for remediation engine
                }
            
            return {
                'epmo_name': report.epmo_name,
                'epmo_path': str(report.module_path),
                'overall_score': report.overall_score,
                'overall_grade': report.overall_grade,
                'dimension_scores': dimension_scores,
                'timestamp': report.timestamp,
                'is_healthy': report.is_healthy,
                'critical_issues': report.critical_issues
            }
            
        finally:
            if project_root:
                self.project_root = original_root


# Factory function for easy access
def create_validator(project_root: Optional[Path] = None) -> EPMOHealthValidator:
    """
    Create EPMO health validator with auto-detected project root.
    
    Args:
        project_root: Optional project root path. If None, auto-detects.
        
    Returns:
        Configured validator instance
    """
    if project_root is None:
        # Auto-detect project root by looking for cortex.config.json
        current_path = Path(__file__).parent
        while current_path != current_path.parent:
            if (current_path / "cortex.config.json").exists():
                project_root = current_path
                break
            current_path = current_path.parent
        
        if project_root is None:
            raise ValueError("Could not auto-detect CORTEX project root. Please specify project_root parameter.")
    
    return EPMOHealthValidator(project_root)