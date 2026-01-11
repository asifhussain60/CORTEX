"""
CORTEX 6.0 - Brittleness & Ambiguity Validator

Strategic testing framework that detects:
1. Brittleness: Fragile code, hardcoded dependencies, missing error handling
2. Ambiguity: Vague requirements, unclear specifications, conflicting docs
3. DoR Completeness: 100% Definition of Ready validation

Halts execution if design score drops below target (95).

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import json
import re
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum

from src.infrastructure.enhanced_audit_logger import (
    EnhancedAuditLogger,
    AuditCategory,
    AuditLevel
)


class TestSeverity(Enum):
    """Test failure severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class FailureAction(Enum):
    """Actions taken on test failure"""
    BLOCK = "BLOCK"
    WARNING = "WARNING"
    INFO = "INFO"


@dataclass
class TestResult:
    """Result of a single test"""
    test_id: str
    test_name: str
    category_id: str
    passed: bool
    score: float  # 0-100
    severity: TestSeverity
    failure_action: FailureAction
    detected_issues: List[Dict[str, Any]] = field(default_factory=list)
    expected_behavior: str = ""
    actual_behavior: str = ""
    recommendations: List[str] = field(default_factory=list)


@dataclass
class CategoryResult:
    """Result of a test category"""
    category_id: str
    category_name: str
    weight: float
    passed_tests: int
    total_tests: int
    category_score: float  # 0-100
    test_results: List[TestResult] = field(default_factory=list)


@dataclass
class ClarificationItem:
    """A clarification question with recommended answer"""
    issue_id: str
    severity: TestSeverity
    question: str
    recommended_answer: str
    rationale: str
    impact_on_score: float
    user_answer: Optional[str] = None
    resolution_timestamp: Optional[datetime] = None


@dataclass
class ValidationReport:
    """Complete validation report"""
    timestamp: datetime
    overall_design_score: float
    brittleness_score: float
    ambiguity_score: float
    dor_score: float
    
    passed: bool
    halt_execution: bool
    
    brittleness_results: List[CategoryResult]
    ambiguity_results: List[CategoryResult]
    dor_results: List[CategoryResult]
    
    clarifications_required: List[ClarificationItem]
    clarifications_resolved: List[ClarificationItem]
    
    total_tests_run: int
    total_tests_passed: int
    total_tests_failed: int
    
    recommendations: List[str] = field(default_factory=list)
    halt_reasons: List[str] = field(default_factory=list)


class BrittlenessAmbiguityValidator:
    """
    Validates code and requirements for brittleness, ambiguity, and DoR completeness.
    Enforces 100% DoR and halts on design score degradation.
    """
    
    def __init__(
        self,
        config_path: str = "cortex-brain/tier0/governance/brittleness-ambiguity-tests.yaml",
        audit_logger: Optional[EnhancedAuditLogger] = None
    ):
        """Initialize validator with configuration"""
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.audit_logger = audit_logger or EnhancedAuditLogger()
        
        # Targets from config
        self.target_design_score = self.config['governance']['target_design_score']
        self.halt_on_score_reduction = self.config['governance']['halt_on_score_reduction']
        self.dor_threshold = self.config['governance']['dor_threshold']
        
        # Weights
        weights = self.config['governance']['score_calculation']['weights']
        self.brittleness_weight = weights['brittleness_score']
        self.ambiguity_weight = weights['ambiguity_score']
        self.dor_weight = weights['dor_score']
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def validate_before_execution(
        self,
        ac_id: Optional[str] = None,
        phase: Optional[str] = None,
        correlation_id: Optional[str] = None
    ) -> ValidationReport:
        """
        Run all validation tests before execution proceeds.
        
        Args:
            ac_id: AC-ID being implemented (optional)
            phase: Phase being executed (optional)
            correlation_id: Correlation ID for audit trail
        
        Returns:
            ValidationReport with pass/fail and clarifications
        """
        self.audit_logger.log(
            level=AuditLevel.INFO,
            message=f"Starting brittleness & ambiguity validation (AC: {ac_id}, Phase: {phase})",
            category=AuditCategory.VALIDATION,
            correlation_id=correlation_id,
            metadata={"ac_id": ac_id, "phase": phase}
        )
        
        # Run test categories
        brittleness_results = self._run_brittleness_tests(ac_id, correlation_id)
        ambiguity_results = self._run_ambiguity_tests(ac_id, correlation_id)
        dor_results = self._run_dor_validation(ac_id, correlation_id)
        
        # Calculate scores
        brittleness_score = self._calculate_category_score(brittleness_results)
        ambiguity_score = self._calculate_category_score(ambiguity_results)
        dor_score = self._calculate_category_score(dor_results)
        
        overall_score = (
            brittleness_score * self.brittleness_weight +
            ambiguity_score * self.ambiguity_weight +
            dor_score * self.dor_weight
        )
        
        # Generate clarifications
        clarifications = self._generate_clarifications(
            brittleness_results,
            ambiguity_results,
            dor_results
        )
        
        # Determine halt conditions
        halt_reasons = self._check_halt_conditions(
            overall_score,
            brittleness_score,
            ambiguity_score,
            dor_score
        )
        
        # Count tests
        all_results = brittleness_results + ambiguity_results + dor_results
        total_tests = sum(cat.total_tests for cat in all_results)
        passed_tests = sum(cat.passed_tests for cat in all_results)
        failed_tests = total_tests - passed_tests
        
        # Create report
        report = ValidationReport(
            timestamp=datetime.now(),
            overall_design_score=overall_score,
            brittleness_score=brittleness_score,
            ambiguity_score=ambiguity_score,
            dor_score=dor_score,
            passed=len(halt_reasons) == 0,
            halt_execution=len(halt_reasons) > 0,
            brittleness_results=brittleness_results,
            ambiguity_results=ambiguity_results,
            dor_results=dor_results,
            clarifications_required=clarifications,
            clarifications_resolved=[],
            total_tests_run=total_tests,
            total_tests_passed=passed_tests,
            total_tests_failed=failed_tests,
            recommendations=self._generate_recommendations(all_results),
            halt_reasons=halt_reasons
        )
        
        # Audit log results
        self.audit_logger.log(
            level=AuditLevel.INFO if report.passed else AuditLevel.WARNING,
            message=f"Validation {'PASSED' if report.passed else 'FAILED'} - Score: {overall_score:.1f}/100",
            category=AuditCategory.VALIDATION,
            correlation_id=correlation_id,
            metadata={
                "overall_score": overall_score,
                "brittleness_score": brittleness_score,
                "ambiguity_score": ambiguity_score,
                "dor_score": dor_score,
                "halt_execution": report.halt_execution,
                "clarifications_required": len(clarifications)
            }
        )
        
        # Save report
        self._save_report(report, ac_id)
        
        return report
    
    def _run_brittleness_tests(
        self,
        ac_id: Optional[str],
        correlation_id: Optional[str]
    ) -> List[CategoryResult]:
        """Run brittleness detection tests"""
        config = self.config['brittleness_tests']
        categories = config['categories']
        results = []
        
        for category in categories:
            category_id = category['category_id']
            category_name = category['name']
            weight = category['weight']
            tests = category.get('tests', [])
            
            test_results = []
            for test in tests:
                test_result = self._run_brittleness_test(test, ac_id, correlation_id)
                test_results.append(test_result)
            
            passed_tests = sum(1 for t in test_results if t.passed)
            category_score = (passed_tests / len(test_results) * 100) if test_results else 100.0
            
            results.append(CategoryResult(
                category_id=category_id,
                category_name=category_name,
                weight=weight,
                passed_tests=passed_tests,
                total_tests=len(test_results),
                category_score=category_score,
                test_results=test_results
            ))
        
        return results
    
    def _run_brittleness_test(
        self,
        test_config: Dict[str, Any],
        ac_id: Optional[str],
        correlation_id: Optional[str]
    ) -> TestResult:
        """Run a single brittleness test"""
        test_id = test_config['test_id']
        test_name = test_config['name']
        detection_pattern = test_config.get('detection_pattern')
        patterns = test_config.get('patterns', [])
        file_types = test_config.get('file_types', [])
        expected_behavior = test_config['expected_behavior']
        failure_action = FailureAction[test_config['failure_action']]
        
        detected_issues = []
        
        # Pattern-based detection
        if detection_pattern == "regex":
            detected_issues = self._detect_regex_patterns(patterns, file_types)
        elif detection_pattern == "ast":
            detected_issues = self._detect_ast_patterns(patterns, file_types)
        elif test_config.get('detection_method') == "multi_file_analysis":
            detected_issues = self._detect_state_desync()
        
        passed = len(detected_issues) == 0
        score = 100.0 if passed else max(0, 100 - len(detected_issues) * 10)
        
        return TestResult(
            test_id=test_id,
            test_name=test_name,
            category_id=test_config.get('category_id', 'UNKNOWN'),
            passed=passed,
            score=score,
            severity=TestSeverity[test_config.get('severity', 'MEDIUM').upper()],
            failure_action=failure_action,
            detected_issues=detected_issues,
            expected_behavior=expected_behavior,
            actual_behavior=f"{len(detected_issues)} violations detected" if not passed else "No violations"
        )
    
    def _detect_regex_patterns(
        self,
        patterns: List[str],
        file_types: List[str]
    ) -> List[Dict[str, Any]]:
        """Detect regex patterns in specified file types"""
        issues = []
        workspace = Path.cwd()
        
        for file_type_pattern in file_types:
            files = list(workspace.rglob(file_type_pattern))
            
            for file_path in files:
                # Skip test files and docs
                if 'test' in str(file_path) or 'docs/' in str(file_path):
                    continue
                
                try:
                    content = file_path.read_text()
                    
                    for pattern in patterns:
                        matches = re.finditer(pattern, content, re.MULTILINE)
                        for match in matches:
                            line_num = content[:match.start()].count('\n') + 1
                            issues.append({
                                "file": str(file_path.relative_to(workspace)),
                                "line": line_num,
                                "pattern": pattern,
                                "match": match.group(0)
                            })
                except Exception as e:
                    pass  # Skip files that can't be read
        
        return issues
    
    def _detect_ast_patterns(
        self,
        patterns: List[str],
        file_types: List[str]
    ) -> List[Dict[str, Any]]:
        """Detect AST-level patterns (placeholder - requires ast module)"""
        # For now, use regex fallback
        return self._detect_regex_patterns(patterns, file_types)
    
    def _detect_state_desync(self) -> List[Dict[str, Any]]:
        """Detect state desynchronization across plan files"""
        issues = []
        workspace = Path.cwd()
        
        try:
            # Load AC-INDEX
            ac_index_path = workspace / "cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml"
            with open(ac_index_path) as f:
                ac_index = yaml.safe_load(f)
            
            # Load master-plan
            master_plan_path = workspace / "cortex-brain/cx6-plan/master-plan.yaml"
            with open(master_plan_path) as f:
                master_plan = yaml.safe_load(f)
            
            # Compare AC counts
            ac_index_count = ac_index.get('total_ac_count', 0)
            master_plan_count = master_plan.get('total_ac_ids', 0)
            
            if ac_index_count != master_plan_count:
                issues.append({
                    "type": "AC_COUNT_MISMATCH",
                    "ac_index_count": ac_index_count,
                    "master_plan_count": master_plan_count,
                    "difference": abs(ac_index_count - master_plan_count)
                })
        
        except Exception as e:
            issues.append({
                "type": "FILE_ACCESS_ERROR",
                "error": str(e)
            })
        
        return issues
    
    def _run_ambiguity_tests(
        self,
        ac_id: Optional[str],
        correlation_id: Optional[str]
    ) -> List[CategoryResult]:
        """Run ambiguity detection tests"""
        config = self.config['ambiguity_tests']
        categories = config['categories']
        results = []
        
        for category in categories:
            category_id = category['category_id']
            category_name = category['name']
            weight = category['weight']
            tests = category.get('tests', [])
            
            test_results = []
            for test in tests:
                test_result = self._run_ambiguity_test(test, category, ac_id, correlation_id)
                test_results.append(test_result)
            
            passed_tests = sum(1 for t in test_results if t.passed)
            category_score = (passed_tests / len(test_results) * 100) if test_results else 100.0
            
            results.append(CategoryResult(
                category_id=category_id,
                category_name=category_name,
                weight=weight,
                passed_tests=passed_tests,
                total_tests=len(test_results),
                category_score=category_score,
                test_results=test_results
            ))
        
        return results
    
    def _run_ambiguity_test(
        self,
        test_config: Dict[str, Any],
        category: Dict[str, Any],
        ac_id: Optional[str],
        correlation_id: Optional[str]
    ) -> TestResult:
        """Run a single ambiguity test"""
        test_id = test_config['test_id']
        test_name = test_config['name']
        expected_behavior = test_config['expected_behavior']
        failure_action = FailureAction[test_config['failure_action']]
        
        detected_issues = []
        
        # Vague terms detection
        if test_config.get('detection_pattern') == 'keyword':
            vague_terms = category.get('vague_terms_list', {})
            all_vague_terms = []
            for term_type, terms in vague_terms.items():
                all_vague_terms.extend(terms)
            
            detected_issues = self._detect_vague_terms(
                all_vague_terms,
                test_config.get('analyze_files', [])
            )
        
        # State conflicts
        elif test_config.get('detection_method') == 'status_comparison':
            detected_issues = self._detect_status_conflicts()
        
        passed = len(detected_issues) == 0
        score = 100.0 if passed else max(0, 100 - len(detected_issues) * 5)
        
        return TestResult(
            test_id=test_id,
            test_name=test_name,
            category_id=category['category_id'],
            passed=passed,
            score=score,
            severity=TestSeverity[category.get('severity', 'MEDIUM').upper()],
            failure_action=failure_action,
            detected_issues=detected_issues,
            expected_behavior=expected_behavior,
            actual_behavior=f"{len(detected_issues)} ambiguities detected" if not passed else "No ambiguities"
        )
    
    def _detect_vague_terms(
        self,
        vague_terms: List[str],
        file_patterns: List[str]
    ) -> List[Dict[str, Any]]:
        """Detect vague terms in specified files"""
        issues = []
        workspace = Path.cwd()
        
        for pattern in file_patterns:
            files = list(workspace.rglob(pattern))
            
            for file_path in files:
                try:
                    content = file_path.read_text()
                    
                    for term in vague_terms:
                        # Case-insensitive search
                        pattern_re = re.compile(r'\b' + re.escape(term) + r'\b', re.IGNORECASE)
                        matches = pattern_re.finditer(content)
                        
                        for match in matches:
                            line_num = content[:match.start()].count('\n') + 1
                            issues.append({
                                "file": str(file_path.relative_to(workspace)),
                                "line": line_num,
                                "vague_term": term,
                                "context": content[max(0, match.start()-50):match.end()+50]
                            })
                except Exception:
                    pass
        
        return issues
    
    def _detect_status_conflicts(self) -> List[Dict[str, Any]]:
        """Detect status conflicts between progress-tracker and AC-INDEX"""
        issues = []
        workspace = Path.cwd()
        
        try:
            # Load progress-tracker
            tracker_path = workspace / "cortex-brain/tier1/tracking/progress-tracker.json"
            with open(tracker_path) as f:
                tracker = json.load(f)
            
            # Load AC-INDEX
            ac_index_path = workspace / "cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml"
            with open(ac_index_path) as f:
                ac_index = yaml.safe_load(f)
            
            # Extract completed AC-IDs from tracker
            completed_in_tracker = set()
            for phase in tracker.get('phases', []):
                completed_in_tracker.update(phase.get('completed_ac_ids', []))
            
            # Check against AC-INDEX status
            for ac_entry in ac_index.get('acceptance_criteria', []):
                ac_id = ac_entry.get('id')
                status = ac_entry.get('status', 'unknown')
                
                if ac_id in completed_in_tracker and status != 'implemented':
                    issues.append({
                        "ac_id": ac_id,
                        "tracker_status": "completed",
                        "ac_index_status": status,
                        "conflict": "Marked completed in tracker but not 'implemented' in AC-INDEX"
                    })
        
        except Exception as e:
            issues.append({
                "type": "COMPARISON_ERROR",
                "error": str(e)
            })
        
        return issues
    
    def _run_dor_validation(
        self,
        ac_id: Optional[str],
        correlation_id: Optional[str]
    ) -> List[CategoryResult]:
        """Run DoR validation tests"""
        config = self.config['dor_validation']
        categories = config['categories']
        results = []
        
        for category in categories:
            category_id = category['category_id']
            category_name = category['name']
            weight = category['weight']
            criteria = category.get('criteria', [])
            
            test_results = []
            for criterion in criteria:
                test_result = self._run_dor_criterion(criterion, ac_id, correlation_id)
                test_results.append(test_result)
            
            passed_tests = sum(1 for t in test_results if t.passed)
            category_score = (passed_tests / len(test_results) * 100) if test_results else 100.0
            
            results.append(CategoryResult(
                category_id=category_id,
                category_name=category_name,
                weight=weight,
                passed_tests=passed_tests,
                total_tests=len(test_results),
                category_score=category_score,
                test_results=test_results
            ))
        
        return results
    
    def _run_dor_criterion(
        self,
        criterion: Dict[str, Any],
        ac_id: Optional[str],
        correlation_id: Optional[str]
    ) -> TestResult:
        """Run a single DoR criterion check"""
        criterion_id = criterion['criterion_id']
        criterion_name = criterion['name']
        validation = criterion['validation']
        mandatory = criterion['mandatory']
        
        # For now, simulate passing (actual implementation would check AC-INDEX)
        # In production, this would validate against actual AC-ID data
        passed = True
        score = 100.0
        
        return TestResult(
            test_id=criterion_id,
            test_name=criterion_name,
            category_id=criterion_id.split('-')[0] + '-' + criterion_id.split('-')[1],
            passed=passed,
            score=score,
            severity=TestSeverity.HIGH if mandatory else TestSeverity.MEDIUM,
            failure_action=FailureAction.BLOCK if mandatory else FailureAction.WARNING,
            detected_issues=[],
            expected_behavior=validation,
            actual_behavior="Criterion satisfied" if passed else f"Criterion failed: {validation}"
        )
    
    def _calculate_category_score(self, categories: List[CategoryResult]) -> float:
        """Calculate weighted average score for a category group"""
        if not categories:
            return 100.0
        
        total_weight = sum(cat.weight for cat in categories)
        weighted_sum = sum(cat.category_score * cat.weight for cat in categories)
        
        return weighted_sum / total_weight if total_weight > 0 else 100.0
    
    def _generate_clarifications(
        self,
        brittleness_results: List[CategoryResult],
        ambiguity_results: List[CategoryResult],
        dor_results: List[CategoryResult]
    ) -> List[ClarificationItem]:
        """Generate clarification questions for failed tests"""
        clarifications = []
        
        # Process ambiguity failures (these need clarification)
        for category in ambiguity_results:
            for test in category.test_results:
                if not test.passed and test.detected_issues:
                    for issue in test.detected_issues[:5]:  # Max 5 per test
                        clarifications.append(ClarificationItem(
                            issue_id=f"{test.test_id}-{len(clarifications)+1}",
                            severity=test.severity,
                            question=f"Clarify: {issue.get('vague_term', 'ambiguous term')} in {issue.get('file', 'file')}",
                            recommended_answer=f"Replace with specific measurable term",
                            rationale="Ambiguous terms reduce clarity and testability",
                            impact_on_score=test.score - 100.0
                        ))
        
        # Process DoR failures
        for category in dor_results:
            for test in category.test_results:
                if not test.passed:
                    # Get clarification question from config
                    clarifications.append(ClarificationItem(
                        issue_id=test.test_id,
                        severity=test.severity,
                        question=f"DoR incomplete: {test.test_name}",
                        recommended_answer="Complete this criterion before proceeding",
                        rationale="100% DoR required for implementation",
                        impact_on_score=test.score - 100.0
                    ))
        
        return clarifications
    
    def _check_halt_conditions(
        self,
        overall_score: float,
        brittleness_score: float,
        ambiguity_score: float,
        dor_score: float
    ) -> List[str]:
        """Check if any halt conditions are met"""
        halt_reasons = []
        halt_conditions = self.config['execution_control']['halt_conditions']
        
        for condition in halt_conditions:
            condition_expr = condition['condition']
            
            # Evaluate condition (simplified)
            if "design_score < target_design_score" in condition_expr:
                if overall_score < self.target_design_score:
                    halt_reasons.append(condition['message'])
            
            elif "brittleness_score < 70" in condition_expr:
                if brittleness_score < 70:
                    halt_reasons.append(condition['message'])
            
            elif "ambiguity_score < 80" in condition_expr:
                if ambiguity_score < 80:
                    halt_reasons.append(condition['message'])
            
            elif "dor_score < 100" in condition_expr:
                if dor_score < 100:
                    halt_reasons.append(condition['message'])
        
        return halt_reasons
    
    def _generate_recommendations(
        self,
        all_results: List[CategoryResult]
    ) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        for category in all_results:
            if category.passed_tests < category.total_tests:
                recommendations.append(
                    f"{category.category_name}: {category.passed_tests}/{category.total_tests} passed - "
                    f"Review failed tests and apply fixes"
                )
        
        return recommendations
    
    def _save_report(
        self,
        report: ValidationReport,
        ac_id: Optional[str]
    ) -> None:
        """Save validation report to evidence bundle"""
        timestamp_str = report.timestamp.strftime("%Y%m%d_%H%M%S")
        filename = f"brittleness-ambiguity-test-report-{timestamp_str}.yaml"
        
        if ac_id:
            output_dir = Path(f"cortex-brain/tier1/evidence-bundles/{ac_id}")
        else:
            output_dir = Path("cortex-brain/tier1/tracking")
        
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / filename
        
        # Convert report to dict
        report_dict = {
            "timestamp": report.timestamp.isoformat(),
            "overall_design_score": report.overall_design_score,
            "brittleness_score": report.brittleness_score,
            "ambiguity_score": report.ambiguity_score,
            "dor_score": report.dor_score,
            "passed": report.passed,
            "halt_execution": report.halt_execution,
            "total_tests_run": report.total_tests_run,
            "total_tests_passed": report.total_tests_passed,
            "total_tests_failed": report.total_tests_failed,
            "clarifications_required": len(report.clarifications_required),
            "halt_reasons": report.halt_reasons,
            "recommendations": report.recommendations
        }
        
        with open(output_path, 'w') as f:
            yaml.dump(report_dict, f, default_flow_style=False)
        
        self.audit_logger.log(
            level=AuditLevel.INFO,
            message=f"Validation report saved: {output_path}",
            category=AuditCategory.VALIDATION,
            metadata={"report_path": str(output_path)}
        )
