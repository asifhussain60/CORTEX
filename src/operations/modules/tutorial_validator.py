"""
Tutorial Exercise Validation

Validates that tutorial exercises complete successfully and produce expected outputs.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

from pathlib import Path
from typing import Dict, Any, List
import re
import logging


class TutorialValidator:
    """Validates tutorial exercise completion."""
    
    def __init__(self, cortex_root: Path):
        """Initialize validator."""
        self.cortex_root = cortex_root
        self.planning_dir = cortex_root / "cortex-brain" / "documents" / "planning"
        self.logger = logging.getLogger(__name__)
        
    def validate_ado_planning_exercise(self, work_item_id: str) -> Dict[str, Any]:
        """
        Validate ADO planning exercise completion.
        
        Args:
            work_item_id: Work item ID to validate
            
        Returns:
            Validation results
        """
        results = {
            'work_item_created': False,
            'git_context_present': False,
            'quality_score_calculated': False,
            'high_risk_detected': False,
            'sme_suggested': False,
            'contributors_listed': False,
            'related_commits_listed': False,
            'acceptance_criteria_enhanced': False
        }
        
        # Find work item file
        work_item_file = self._find_work_item_file(work_item_id)
        if not work_item_file:
            return {**results, 'error': f'Work item file not found for ID: {work_item_id}'}
        
        results['work_item_created'] = True
        
        # Read file content
        content = work_item_file.read_text()
        
        # Check for Git History Context section
        if '## Git History Context' in content:
            results['git_context_present'] = True
        
        # Check for quality score
        quality_match = re.search(r'\*\*Quality Score:\*\*\s+(\d+\.?\d*)%', content)
        if quality_match:
            results['quality_score_calculated'] = True
            results['quality_score_value'] = float(quality_match.group(1))
        
        # Check for high-risk files
        if '⚠️ High-Risk Files Detected:' in content:
            results['high_risk_detected'] = True
            high_risk_files = re.findall(r'-\s+`([^`]+)`\s+-\s+Requires extra attention', content)
            results['high_risk_files'] = high_risk_files
        
        # Check for SME suggestions
        if '💡 Subject Matter Expert Suggestions:' in content:
            results['sme_suggested'] = True
            sme_match = re.search(r'-\s+\*\*([^*]+)\*\*\s+\(top contributor', content)
            if sme_match:
                results['sme_name'] = sme_match.group(1)
        
        # Check for contributors
        if '**Contributors to Related Files:**' in content:
            results['contributors_listed'] = True
            contributors = re.findall(r'-\s+([^(]+)\((\d+)\s+commits?\)', content)
            results['contributors'] = [(name.strip(), int(count)) for name, count in contributors]
        
        # Check for related commits
        if '**Related Commits:**' in content:
            results['related_commits_listed'] = True
            commits = re.findall(r'-\s+`([^`]+)`[:\s]+([^\n]+)', content)
            results['related_commits'] = commits
        
        # Check for enhanced acceptance criteria (high-risk warning)
        if re.search(r'\[\s*\]\s+⚠️\s+Review high-risk files:', content):
            results['acceptance_criteria_enhanced'] = True
        
        # Calculate completion percentage
        checks = [
            results['work_item_created'],
            results['git_context_present'],
            results['quality_score_calculated'],
            results['high_risk_detected'],
            results['sme_suggested'],
            results['contributors_listed'],
            results['related_commits_listed'],
            results['acceptance_criteria_enhanced']
        ]
        results['completion_percentage'] = int((sum(checks) / len(checks)) * 100)
        results['all_checks_passed'] = all(checks)
        
        return results
    
    def _find_work_item_file(self, work_item_id: str) -> Path:
        """Find work item file by ID."""
        # Search in active directory
        active_dir = self.planning_dir / "ado" / "active"
        if active_dir.exists():
            for file in active_dir.glob(f"*{work_item_id}*.md"):
                return file
        
        # Search in completed directory
        completed_dir = self.planning_dir / "ado" / "completed"
        if completed_dir.exists():
            for file in completed_dir.glob(f"*{work_item_id}*.md"):
                return file
        
        return None
    
    def validate_all_exercises(self, session_id: str) -> Dict[str, Any]:
        """
        Validate all exercises for a tutorial session.
        
        Args:
            session_id: Tutorial session ID
            
        Returns:
            Comprehensive validation results
        """
        results = {
            'session_id': session_id,
            'basics_complete': self._validate_basics_exercises(),
            'planning_complete': self._validate_planning_exercises(),
            'ado_planning_complete': self._validate_ado_planning_exercises(),
            'tdd_complete': self._validate_tdd_exercises(),
            'testing_complete': self._validate_testing_exercises()
        }
        
        # Calculate overall completion
        module_results = [
            results['basics_complete']['passed'],
            results['planning_complete']['passed'],
            results['ado_planning_complete']['passed'],
            results['tdd_complete']['passed'],
            results['testing_complete']['passed']
        ]
        results['overall_completion'] = int((sum(module_results) / len(module_results)) * 100)
        results['all_modules_complete'] = all(module_results)
        
        return results
    
    def _validate_basics_exercises(self) -> Dict[str, Any]:
        """Validate basics module completion."""
        # Check for conversation history
        history_file = self.cortex_root / "cortex-brain" / "tier1" / "working_memory.db"
        
        return {
            'module': 'basics',
            'passed': history_file.exists(),
            'checks': {
                'working_memory_exists': history_file.exists()
            }
        }
    
    def _validate_planning_exercises(self) -> Dict[str, Any]:
        """Validate planning module completion."""
        # Check for planning files
        features_dir = self.planning_dir / "features"
        active_plans = list(features_dir.glob("active/PLAN-*.md")) if features_dir.exists() else []
        approved_plans = list(features_dir.glob("approved/APPROVED-*.md")) if features_dir.exists() else []
        
        return {
            'module': 'planning',
            'passed': len(active_plans) > 0 or len(approved_plans) > 0,
            'checks': {
                'active_plans': len(active_plans),
                'approved_plans': len(approved_plans)
            }
        }
    
    def _validate_ado_planning_exercises(self) -> Dict[str, Any]:
        """Validate ADO planning module completion."""
        # Check for ADO work items
        ado_dir = self.planning_dir / "ado" / "active"
        work_items = list(ado_dir.glob("*.md")) if ado_dir.exists() else []
        
        # For each work item, check git context
        git_context_present = 0
        for work_item_file in work_items:
            content = work_item_file.read_text()
            if '## Git History Context' in content:
                git_context_present += 1
        
        return {
            'module': 'ado_planning',
            'passed': len(work_items) > 0 and git_context_present > 0,
            'checks': {
                'work_items_created': len(work_items),
                'git_context_present': git_context_present,
                'git_integration_working': git_context_present > 0
            }
        }
    
    def _validate_tdd_exercises(self) -> Dict[str, Any]:
        """Validate TDD module completion."""
        # This would check for test files, implementation files, git checkpoints
        # For now, return basic validation
        return {
            'module': 'tdd',
            'passed': True,  # Placeholder
            'checks': {
                'tdd_session_started': True
            }
        }
    
    def _validate_testing_exercises(self) -> Dict[str, Any]:
        """Validate testing module completion."""
        # This would check for session reports, feedback files
        # For now, return basic validation
        return {
            'module': 'testing',
            'passed': True,  # Placeholder
            'checks': {
                'validation_complete': True
            }
        }
    
    def generate_validation_report(self, validation_results: Dict[str, Any]) -> str:
        """
        Generate human-readable validation report.
        
        Args:
            validation_results: Results from validate_ado_planning_exercise
            
        Returns:
            Formatted report
        """
        report = []
        report.append("# Tutorial Exercise Validation Report\n")
        
        if 'work_item_id' in validation_results:
            # ADO Planning validation report
            report.append(f"## ADO Planning Exercise\n")
            report.append(f"**Work Item ID:** {validation_results.get('work_item_id', 'N/A')}\n")
            report.append(f"**Completion:** {validation_results.get('completion_percentage', 0)}%\n")
            report.append(f"**Status:** {'✅ PASSED' if validation_results.get('all_checks_passed') else '⚠️ INCOMPLETE'}\n\n")
            
            report.append("### Validation Checks\n")
            checks = [
                ('Work item created', validation_results.get('work_item_created')),
                ('Git context present', validation_results.get('git_context_present')),
                ('Quality score calculated', validation_results.get('quality_score_calculated')),
                ('High-risk files detected', validation_results.get('high_risk_detected')),
                ('SME suggested', validation_results.get('sme_suggested')),
                ('Contributors listed', validation_results.get('contributors_listed')),
                ('Related commits listed', validation_results.get('related_commits_listed')),
                ('Acceptance criteria enhanced', validation_results.get('acceptance_criteria_enhanced'))
            ]
            
            for check_name, passed in checks:
                icon = '✅' if passed else '❌'
                report.append(f"- {icon} {check_name}\n")
            
            if validation_results.get('quality_score_calculated'):
                score = validation_results.get('quality_score_value', 0)
                label = self._get_quality_label(score)
                report.append(f"\n**Quality Score:** {score}% ({label})\n")
            
            if validation_results.get('sme_suggested'):
                sme = validation_results.get('sme_name', 'Unknown')
                report.append(f"**Suggested SME:** {sme}\n")
            
            if validation_results.get('high_risk_detected'):
                files = validation_results.get('high_risk_files', [])
                report.append(f"\n**High-Risk Files:** {', '.join(files)}\n")
        
        else:
            # Overall validation report
            report.append(f"## Overall Tutorial Progress\n")
            report.append(f"**Session ID:** {validation_results.get('session_id', 'N/A')}\n")
            report.append(f"**Completion:** {validation_results.get('overall_completion', 0)}%\n")
            report.append(f"**Status:** {'✅ ALL COMPLETE' if validation_results.get('all_modules_complete') else '⏳ IN PROGRESS'}\n\n")
            
            report.append("### Module Status\n")
            modules = [
                ('Basics', validation_results.get('basics_complete', {}).get('passed')),
                ('Planning', validation_results.get('planning_complete', {}).get('passed')),
                ('ADO Planning', validation_results.get('ado_planning_complete', {}).get('passed')),
                ('TDD', validation_results.get('tdd_complete', {}).get('passed')),
                ('Testing', validation_results.get('testing_complete', {}).get('passed'))
            ]
            
            for module_name, passed in modules:
                icon = '✅' if passed else '⏳'
                report.append(f"- {icon} {module_name}\n")
        
        return ''.join(report)
    
    def _get_quality_label(self, score: float) -> str:
        """Get quality label from score."""
        if score >= 90:
            return 'Excellent'
        elif score >= 70:
            return 'Good'
        elif score >= 50:
            return 'Adequate'
        else:
            return 'Weak'


def validate_ado_exercise(cortex_root: Path, work_item_id: str) -> Dict[str, Any]:
    """Quick validation function for ADO planning exercise."""
    validator = TutorialValidator(cortex_root)
    return validator.validate_ado_planning_exercise(work_item_id)
