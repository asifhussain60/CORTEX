"""
Investigation Orchestrator v2 - Pure Autonomous Root Cause Analysis & Architectural Review.

Comprehensive investigation system with:
- Multi-source artifact discovery (plans, reports, brittleness analyses, code)
- Acceptance criteria validation framework
- Cross-plan brittleness correlation
- Root cause analysis engine
- Gap identification and remediation planning
- Comprehensive investigation report generation

Triggered by:
- User request: "investigate", "find root cause", "review", "analyze"
- Master Orchestrator routing pattern: ^(investigate|find root cause|review|holistic review)
- Priority: 60

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import json
import re

from src.orchestrators.base.base_orchestrator_v4_1 import (
    BaseOrchestratorV4_1,
    PhaseStatus,
    PhaseResult,
    OrchestratorResult,
    OrchestratorStatus
)
from src.database.planning_state_db import PlanningStateDB


logger = logging.getLogger(__name__)


class InvestigationOrchestratorV2(BaseOrchestratorV4_1):
    """
    Investigation Orchestrator v2 - Pure autonomous root cause analysis.
    
    Workflow (7 phases):
        1. DISCOVERY - Locate target artifacts (plans, acceptance criteria, brittleness reports)
        2. PARSING - Extract structured data from artifacts
        3. VALIDATION - Compare planned vs actual state against acceptance criteria
        4. CORRELATION - Cross-reference brittleness reports with plan claims
        5. ANALYSIS - Root cause identification and impact assessment
        6. REMEDIATION - Generate fix recommendations and implementation roadmap
        7. REPORTING - Create comprehensive investigation report
    
    Config: cortex-brain/manifests/orchestrators/investigation-orchestrator-v2.yaml
    """
    
    def __init__(
        self,
        config_path: str = "cortex-brain/manifests/orchestrators/investigation-orchestrator-v2.yaml",
        state_db: Optional[PlanningStateDB] = None,
        plan_id: Optional[str] = None
    ):
        """
        Initialize Investigation Orchestrator v2.
        
        Args:
            config_path: Path to investigation configuration manifest
            state_db: PlanningStateDB instance (creates new if None)
            plan_id: Optional existing plan ID to resume
        """
        # Initialize database if not provided
        if state_db is None:
            db_path = Path("cortex-brain/database/planning_state.db")
            state_db = PlanningStateDB(str(db_path))
        
        super().__init__(
            config_path=config_path,
            state_db=state_db,
            plan_id=plan_id
        )
        
        # Investigation state
        self.target_plan_id: Optional[str] = None
        self.artifacts: Dict[str, List[Path]] = {
            'plans': [],
            'acceptance_criteria': [],
            'brittleness_reports': [],
            'completion_certificates': [],
            'phase_reports': []
        }
        self.parsed_data: Dict[str, Any] = {}
        self.validation_results: Dict[str, Any] = {}
        self.correlations: List[Dict[str, Any]] = []
        self.root_causes: List[Dict[str, Any]] = []
        self.remediation_plan: Dict[str, Any] = {}
        
        self.logger.info("InvestigationOrchestratorV2 initialized")
    
    def execute(
        self,
        user_request: str,
        target_plan_id: Optional[str] = None,
        investigation_scope: List[str] = None,
        output_dir: Optional[str] = None,
        **kwargs
    ) -> OrchestratorResult:
        """
        Execute investigation workflow.
        
        Args:
            user_request: User's investigation request
            target_plan_id: Specific plan ID to investigate (e.g., "C150", "html-glassmorphism-alignment")
            investigation_scope: List of investigation types:
                - 'acceptance_criteria': Validate against acceptance criteria
                - 'brittleness': Cross-reference brittleness reports
                - 'implementation': Verify implementation completeness
                - 'deployment': Check deployment validation
                - 'root_cause': Perform root cause analysis
            output_dir: Output directory for investigation reports
            **kwargs: Additional parameters
        
        Returns:
            OrchestratorResult with investigation findings
        """
        try:
            # Default investigation scope (all types)
            if investigation_scope is None:
                investigation_scope = [
                    'acceptance_criteria',
                    'brittleness',
                    'implementation',
                    'deployment',
                    'root_cause'
                ]
            
            # Default output directory
            if output_dir is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_dir = f"cortex-brain/documents/investigations/investigation-{timestamp}"
            
            self.output_dir = Path(output_dir)
            self.investigation_scope = investigation_scope
            
            # Extract plan ID from user request if not provided
            if target_plan_id is None:
                target_plan_id = self._extract_plan_id(user_request)
            
            self.target_plan_id = target_plan_id
            
            self.logger.info(f"Starting investigation for plan: {target_plan_id}")
            self.logger.info(f"Investigation scope: {investigation_scope}")
            self.logger.info(f"Output directory: {output_dir}")
            
            # Execute phases
            result = self._execute_phases()
            
            return result
            
        except Exception as e:
            self.logger.error(f"Investigation failed: {e}", exc_info=True)
            return OrchestratorResult(
                status=OrchestratorStatus.FAILED,
                message=f"Investigation failed: {str(e)}",
                metadata={'error': str(e)}
            )
    
    def _execute_phases(self) -> OrchestratorResult:
        """Execute all investigation phases."""
        # Phase 1: DISCOVERY
        discovery_result = self._phase_1_discovery()
        if discovery_result.status == PhaseStatus.FAILED:
            return self._create_failure_result("Discovery phase failed", discovery_result)
        
        # Phase 2: PARSING
        parsing_result = self._phase_2_parsing()
        if parsing_result.status == PhaseStatus.FAILED:
            return self._create_failure_result("Parsing phase failed", parsing_result)
        
        # Phase 3: VALIDATION
        if 'acceptance_criteria' in self.investigation_scope:
            validation_result = self._phase_3_validation()
            if validation_result.status == PhaseStatus.FAILED:
                return self._create_failure_result("Validation phase failed", validation_result)
        
        # Phase 4: CORRELATION
        if 'brittleness' in self.investigation_scope:
            correlation_result = self._phase_4_correlation()
            if correlation_result.status == PhaseStatus.FAILED:
                return self._create_failure_result("Correlation phase failed", correlation_result)
        
        # Phase 5: ANALYSIS
        if 'root_cause' in self.investigation_scope:
            analysis_result = self._phase_5_analysis()
            if analysis_result.status == PhaseStatus.FAILED:
                return self._create_failure_result("Analysis phase failed", analysis_result)
        
        # Phase 6: REMEDIATION
        remediation_result = self._phase_6_remediation()
        if remediation_result.status == PhaseStatus.FAILED:
            return self._create_failure_result("Remediation phase failed", remediation_result)
        
        # Phase 7: REPORTING
        reporting_result = self._phase_7_reporting()
        if reporting_result.status == PhaseStatus.FAILED:
            return self._create_failure_result("Reporting phase failed", reporting_result)
        
        # Success
        return OrchestratorResult(
            status=OrchestratorStatus.SUCCESS,
            message=f"Investigation complete: {self.target_plan_id}",
            metadata={
                'target_plan': self.target_plan_id,
                'investigation_scope': self.investigation_scope,
                'output_dir': str(self.output_dir),
                'artifacts_found': sum(len(v) for v in self.artifacts.values()),
                'validation_results': self.validation_results,
                'root_causes_identified': len(self.root_causes),
                'report_path': str(self.output_dir / '00-executive-summary.md')
            }
        )
    
    def _phase_1_discovery(self) -> PhaseResult:
        """Phase 1: Discover investigation artifacts."""
        self.logger.info("Phase 1: DISCOVERY - Locating investigation artifacts")
        
        try:
            # Search for plan artifacts
            plan_patterns = [
                f"cortex-brain/documents/planning/**/*{self.target_plan_id}*",
                f"cortex-brain/documents/planning/**/*{self.target_plan_id.lower()}*"
            ]
            
            for pattern in plan_patterns:
                for path in Path(".").glob(pattern):
                    if path.is_file() and path.suffix == '.md':
                        if 'acceptance' in path.name.lower():
                            self.artifacts['acceptance_criteria'].append(path)
                        elif 'completion' in path.name.lower() or 'certificate' in path.name.lower():
                            self.artifacts['completion_certificates'].append(path)
                        elif 'phase-' in path.name.lower():
                            self.artifacts['phase_reports'].append(path)
                        else:
                            self.artifacts['plans'].append(path)
            
            # Search for brittleness reports
            brittleness_patterns = [
                "cortex-brain/documents/reports/*brittleness*.md",
                "cortex-brain/documents/analysis/*brittleness*.md"
            ]
            
            for pattern in brittleness_patterns:
                for path in Path(".").glob(pattern):
                    if path.is_file():
                        self.artifacts['brittleness_reports'].append(path)
            
            total_artifacts = sum(len(v) for v in self.artifacts.values())
            self.logger.info(f"Discovery complete: {total_artifacts} artifacts found")
            
            return PhaseResult(
                phase_id=1,
                status=PhaseStatus.COMPLETED,
                message=f"Discovery complete: {total_artifacts} artifacts found",
                metadata={'artifacts': {k: len(v) for k, v in self.artifacts.items()}}
            )
            
        except Exception as e:
            self.logger.error(f"Discovery failed: {e}", exc_info=True)
            return PhaseResult(
                phase_id=1,
                status=PhaseStatus.FAILED,
                message=f"Discovery failed: {str(e)}",
                metadata={'error': str(e)}
            )
    
    def _phase_2_parsing(self) -> PhaseResult:
        """Phase 2: Parse discovered artifacts."""
        self.logger.info("Phase 2: PARSING - Extracting structured data")
        
        try:
            # Parse completion certificates
            for cert_path in self.artifacts['completion_certificates']:
                cert_data = self._parse_completion_certificate(cert_path)
                self.parsed_data[f'certificate_{cert_path.stem}'] = cert_data
            
            # Parse acceptance criteria
            for criteria_path in self.artifacts['acceptance_criteria']:
                criteria_data = self._parse_acceptance_criteria(criteria_path)
                self.parsed_data[f'criteria_{criteria_path.stem}'] = criteria_data
            
            # Parse brittleness reports
            for report_path in self.artifacts['brittleness_reports']:
                report_data = self._parse_brittleness_report(report_path)
                self.parsed_data[f'brittleness_{report_path.stem}'] = report_data
            
            self.logger.info(f"Parsing complete: {len(self.parsed_data)} artifacts parsed")
            
            return PhaseResult(
                phase_id=2,
                status=PhaseStatus.COMPLETED,
                message=f"Parsing complete: {len(self.parsed_data)} artifacts parsed",
                metadata={'parsed_artifacts': list(self.parsed_data.keys())}
            )
            
        except Exception as e:
            self.logger.error(f"Parsing failed: {e}", exc_info=True)
            return PhaseResult(
                phase_id=2,
                status=PhaseStatus.FAILED,
                message=f"Parsing failed: {str(e)}",
                metadata={'error': str(e)}
            )
    
    def _phase_3_validation(self) -> PhaseResult:
        """Phase 3: Validate against acceptance criteria."""
        self.logger.info("Phase 3: VALIDATION - Comparing planned vs actual state")
        
        try:
            # Extract acceptance criteria
            criteria_list = []
            for key, data in self.parsed_data.items():
                if key.startswith('criteria_'):
                    criteria_list.extend(data.get('criteria', []))
            
            # Validate each criterion
            results = {
                'total': len(criteria_list),
                'passed': 0,
                'failed': 0,
                'partial': 0,
                'details': []
            }
            
            for criterion in criteria_list:
                status = self._validate_criterion(criterion)
                results['details'].append({
                    'criterion_id': criterion.get('id'),
                    'component': criterion.get('component'),
                    'status': status,
                    'requirement': criterion.get('requirement')
                })
                
                if status == 'pass':
                    results['passed'] += 1
                elif status == 'fail':
                    results['failed'] += 1
                else:
                    results['partial'] += 1
            
            self.validation_results = results
            
            pass_rate = (results['passed'] / results['total'] * 100) if results['total'] > 0 else 0
            self.logger.info(f"Validation complete: {pass_rate:.1f}% pass rate ({results['passed']}/{results['total']})")
            
            return PhaseResult(
                phase_id=3,
                status=PhaseStatus.COMPLETED,
                message=f"Validation complete: {pass_rate:.1f}% pass rate",
                metadata=results
            )
            
        except Exception as e:
            self.logger.error(f"Validation failed: {e}", exc_info=True)
            return PhaseResult(
                phase_id=3,
                status=PhaseStatus.FAILED,
                message=f"Validation failed: {str(e)}",
                metadata={'error': str(e)}
            )
    
    def _phase_4_correlation(self) -> PhaseResult:
        """Phase 4: Correlate brittleness reports with plan claims."""
        self.logger.info("Phase 4: CORRELATION - Cross-referencing brittleness reports")
        
        try:
            # Extract brittleness issues
            brittleness_issues = []
            for key, data in self.parsed_data.items():
                if key.startswith('brittleness_'):
                    brittleness_issues.extend(data.get('issues', []))
            
            # Extract plan claims
            plan_claims = []
            for key, data in self.parsed_data.items():
                if key.startswith('certificate_'):
                    plan_claims.extend(data.get('claims', []))
            
            # Find contradictions
            for claim in plan_claims:
                for issue in brittleness_issues:
                    if self._claims_contradict(claim, issue):
                        self.correlations.append({
                            'claim': claim,
                            'issue': issue,
                            'severity': 'critical',
                            'contradiction': True
                        })
            
            self.logger.info(f"Correlation complete: {len(self.correlations)} contradictions found")
            
            return PhaseResult(
                phase_id=4,
                status=PhaseStatus.COMPLETED,
                message=f"Correlation complete: {len(self.correlations)} contradictions found",
                metadata={'correlations': len(self.correlations)}
            )
            
        except Exception as e:
            self.logger.error(f"Correlation failed: {e}", exc_info=True)
            return PhaseResult(
                phase_id=4,
                status=PhaseStatus.FAILED,
                message=f"Correlation failed: {str(e)}",
                metadata={'error': str(e)}
            )
    
    def _phase_5_analysis(self) -> PhaseResult:
        """Phase 5: Root cause analysis."""
        self.logger.info("Phase 5: ANALYSIS - Identifying root causes")
        
        try:
            # Analyze validation failures
            for detail in self.validation_results.get('details', []):
                if detail['status'] == 'fail':
                    root_cause = self._analyze_failure(detail)
                    if root_cause:
                        self.root_causes.append(root_cause)
            
            # Analyze contradictions
            for correlation in self.correlations:
                root_cause = self._analyze_contradiction(correlation)
                if root_cause:
                    self.root_causes.append(root_cause)
            
            self.logger.info(f"Analysis complete: {len(self.root_causes)} root causes identified")
            
            return PhaseResult(
                phase_id=5,
                status=PhaseStatus.COMPLETED,
                message=f"Analysis complete: {len(self.root_causes)} root causes identified",
                metadata={'root_causes': len(self.root_causes)}
            )
            
        except Exception as e:
            self.logger.error(f"Analysis failed: {e}", exc_info=True)
            return PhaseResult(
                phase_id=5,
                status=PhaseStatus.FAILED,
                message=f"Analysis failed: {str(e)}",
                metadata={'error': str(e)}
            )
    
    def _phase_6_remediation(self) -> PhaseResult:
        """Phase 6: Generate remediation plan."""
        self.logger.info("Phase 6: REMEDIATION - Generating fix recommendations")
        
        try:
            # Group root causes by category
            categories = {}
            for root_cause in self.root_causes:
                category = root_cause.get('category', 'other')
                if category not in categories:
                    categories[category] = []
                categories[category].append(root_cause)
            
            # Generate recommendations for each category
            recommendations = []
            for category, causes in categories.items():
                recommendation = self._generate_recommendation(category, causes)
                recommendations.append(recommendation)
            
            self.remediation_plan = {
                'categories': list(categories.keys()),
                'total_issues': len(self.root_causes),
                'recommendations': recommendations,
                'estimated_time': self._estimate_remediation_time(recommendations)
            }
            
            self.logger.info(f"Remediation planning complete: {len(recommendations)} recommendations generated")
            
            return PhaseResult(
                phase_id=6,
                status=PhaseStatus.COMPLETED,
                message=f"Remediation planning complete: {len(recommendations)} recommendations",
                metadata=self.remediation_plan
            )
            
        except Exception as e:
            self.logger.error(f"Remediation planning failed: {e}", exc_info=True)
            return PhaseResult(
                phase_id=6,
                status=PhaseStatus.FAILED,
                message=f"Remediation planning failed: {str(e)}",
                metadata={'error': str(e)}
            )
    
    def _phase_7_reporting(self) -> PhaseResult:
        """Phase 7: Generate comprehensive investigation report."""
        self.logger.info("Phase 7: REPORTING - Creating investigation report")
        
        try:
            # Create output directory
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate executive summary
            summary_path = self.output_dir / '00-executive-summary.md'
            self._generate_executive_summary(summary_path)
            
            # Generate detailed reports
            self._generate_acceptance_criteria_comparison(self.output_dir / 'acceptance-criteria-comparison.md')
            self._generate_brittleness_cross_reference(self.output_dir / 'brittleness-cross-reference.md')
            self._generate_implementation_completeness_matrix(self.output_dir / 'implementation-completeness-matrix.md')
            self._generate_gap_analysis_summary(self.output_dir / 'gap-analysis-summary.md')
            self._generate_root_cause_analysis(self.output_dir / 'root-cause-analysis.md')
            
            self.logger.info(f"Reporting complete: Reports generated in {self.output_dir}")
            
            return PhaseResult(
                phase_id=7,
                status=PhaseStatus.COMPLETED,
                message=f"Reporting complete: {self.output_dir}",
                metadata={'report_path': str(summary_path)}
            )
            
        except Exception as e:
            self.logger.error(f"Reporting failed: {e}", exc_info=True)
            return PhaseResult(
                phase_id=7,
                status=PhaseStatus.FAILED,
                message=f"Reporting failed: {str(e)}",
                metadata={'error': str(e)}
            )
    
    # Helper methods
    
    def _extract_plan_id(self, user_request: str) -> str:
        """Extract plan ID from user request."""
        # Try to find C### pattern (e.g., C150)
        match = re.search(r'\bC\d+\b', user_request, re.IGNORECASE)
        if match:
            return match.group(0).upper()
        
        # Try to find plan name pattern (e.g., html-glassmorphism-alignment)
        match = re.search(r'[\w-]+(?:-v\d+)?(?:\s+plan)?', user_request.lower())
        if match:
            return match.group(0).strip()
        
        return "unknown-plan"
    
    def _parse_completion_certificate(self, path: Path) -> Dict[str, Any]:
        """Parse completion certificate file."""
        content = path.read_text()
        
        # Extract claims (lines starting with ✅)
        claims = []
        for line in content.split('\n'):
            if '✅' in line:
                claims.append(line.strip())
        
        # Extract completion percentage
        completion_match = re.search(r'(\d+)%.*complete', content, re.IGNORECASE)
        completion_pct = int(completion_match.group(1)) if completion_match else 0
        
        return {
            'path': str(path),
            'claims': claims,
            'completion_percentage': completion_pct
        }
    
    def _parse_acceptance_criteria(self, path: Path) -> Dict[str, Any]:
        """Parse acceptance criteria file."""
        content = path.read_text()
        
        # Extract criteria from tables (simplified)
        criteria = []
        in_table = False
        for line in content.split('\n'):
            if '|' in line and '---' not in line:
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 4 and parts[0] and parts[0] != '':
                    criteria.append({
                        'id': parts[1] if len(parts) > 1 else '',
                        'component': parts[2] if len(parts) > 2 else '',
                        'requirement': parts[3] if len(parts) > 3 else ''
                    })
        
        return {
            'path': str(path),
            'criteria': criteria
        }
    
    def _parse_brittleness_report(self, path: Path) -> Dict[str, Any]:
        """Parse brittleness report file."""
        content = path.read_text()
        
        # Extract issues (simplified - look for sections marked with 🔴, ⚠️, etc.)
        issues = []
        for line in content.split('\n'):
            if any(marker in line for marker in ['🔴', '⚠️', '❌']):
                issues.append(line.strip())
        
        return {
            'path': str(path),
            'issues': issues
        }
    
    def _validate_criterion(self, criterion: Dict[str, Any]) -> str:
        """Validate a single acceptance criterion."""
        # Simplified validation - check if artifacts exist
        requirement = criterion.get('requirement', '').lower()
        
        # Check for completion keywords
        if 'complete' in requirement or 'documented' in requirement:
            # Check if related artifacts exist
            component = criterion.get('component', '').lower()
            if any(component in str(path).lower() for paths in self.artifacts.values() for path in paths):
                return 'pass'
            return 'fail'
        
        return 'partial'
    
    def _claims_contradict(self, claim: str, issue: str) -> bool:
        """Check if a plan claim contradicts a brittleness issue."""
        # Simplified contradiction detection
        positive_keywords = ['100%', 'complete', 'success', 'all', 'zero']
        negative_keywords = ['fail', 'error', 'missing', 'broken', 'critical']
        
        claim_positive = any(kw in claim.lower() for kw in positive_keywords)
        issue_negative = any(kw in issue.lower() for kw in negative_keywords)
        
        return claim_positive and issue_negative
    
    def _analyze_failure(self, detail: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Analyze a validation failure to identify root cause."""
        return {
            'type': 'validation_failure',
            'category': 'implementation',
            'criterion_id': detail.get('criterion_id'),
            'component': detail.get('component'),
            'root_cause': f"Implementation incomplete for {detail.get('component')}",
            'severity': 'high'
        }
    
    def _analyze_contradiction(self, correlation: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Analyze a contradiction to identify root cause."""
        return {
            'type': 'contradiction',
            'category': 'false_claim',
            'claim': correlation.get('claim'),
            'issue': correlation.get('issue'),
            'root_cause': 'Plan claimed completion but brittleness issue exists',
            'severity': 'critical'
        }
    
    def _generate_recommendation(self, category: str, causes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate remediation recommendation for a category."""
        return {
            'category': category,
            'issue_count': len(causes),
            'priority': 'critical' if len(causes) > 5 else 'high',
            'recommendation': f"Address {len(causes)} {category} issues",
            'estimated_hours': len(causes) * 2  # 2 hours per issue (rough estimate)
        }
    
    def _estimate_remediation_time(self, recommendations: List[Dict[str, Any]]) -> str:
        """Estimate total remediation time."""
        total_hours = sum(r.get('estimated_hours', 0) for r in recommendations)
        if total_hours < 8:
            return f"{total_hours} hours"
        else:
            days = total_hours / 8
            return f"{total_hours} hours ({days:.1f} business days)"
    
    def _generate_executive_summary(self, path: Path):
        """Generate executive summary report."""
        # This would generate a comprehensive markdown report
        # For now, placeholder
        path.write_text(f"# Investigation Report: {self.target_plan_id}\n\nGenerated: {datetime.now()}\n")
    
    def _generate_acceptance_criteria_comparison(self, path: Path):
        """Generate acceptance criteria comparison report."""
        path.write_text("# Acceptance Criteria Comparison\n\n(Generated by Investigation Orchestrator)\n")
    
    def _generate_brittleness_cross_reference(self, path: Path):
        """Generate brittleness cross-reference report."""
        path.write_text("# Brittleness Cross-Reference\n\n(Generated by Investigation Orchestrator)\n")
    
    def _generate_implementation_completeness_matrix(self, path: Path):
        """Generate implementation completeness matrix."""
        path.write_text("# Implementation Completeness Matrix\n\n(Generated by Investigation Orchestrator)\n")
    
    def _generate_gap_analysis_summary(self, path: Path):
        """Generate gap analysis summary."""
        path.write_text("# Gap Analysis Summary\n\n(Generated by Investigation Orchestrator)\n")
    
    def _generate_root_cause_analysis(self, path: Path):
        """Generate root cause analysis report."""
        path.write_text("# Root Cause Analysis\n\n(Generated by Investigation Orchestrator)\n")
    
    def _create_failure_result(self, message: str, phase_result: PhaseResult) -> OrchestratorResult:
        """Create failure result from phase failure."""
        return OrchestratorResult(
            status=OrchestratorStatus.FAILED,
            message=message,
            metadata={
                'failed_phase': phase_result.phase_id,
                'error': phase_result.message
            }
        )
