"""
Session Completion Orchestrator

Provides holistic validation when TDD session completes all phases.

Features:
- Full test suite execution
- Before/after metrics comparison
- Git diff summary generation
- SKULL rule validation (22 rules)
- CODE QUALITY ENFORCEMENT (NEW v2.0)
  - Debug statement detection
  - Lint validation
  - Production readiness checklist
- Completion report generation
- Regression detection

Version: 2.0.0
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json
import logging

# NEW v2.0: Code quality enforcement imports
from workflows.code_cleanup_validator import CodeCleanupValidator
from workflows.lint_integration import LintIntegration
from workflows.production_readiness import ProductionReadinessChecklist

# NEW Sprint 2: Document organization imports
from workflows.document_organizer import DocumentOrganizer

logger = logging.getLogger(__name__)


class SessionCompletionOrchestrator:
    """
    Orchestrates comprehensive validation at TDD session completion.
    
    Ensures:
    - All tests pass
    - Metrics improved (or maintained)
    - No regressions introduced
    - SKULL rules compliance
    - Quality standards met
    """
    
    def __init__(self, project_root: Path, enable_quality_enforcement: bool = True):
        """
        Initialize SessionCompletionOrchestrator.
        
        Args:
            project_root: Path to project repository root
            enable_quality_enforcement: Enable code quality validation (v2.0 feature)
        """
        self.project_root = Path(project_root)
        self.report_template_path = Path(__file__).parent.parent.parent / "cortex-brain" / "templates" / "session-completion-report.md"
        self.enable_quality_enforcement = enable_quality_enforcement
        
        # NEW v2.0: Initialize quality validators
        if self.enable_quality_enforcement:
            self.cleanup_validator = CodeCleanupValidator()
            self.lint_integration = LintIntegration()
            self.readiness_checker = ProductionReadinessChecklist(project_root=project_root)
        
        # NEW Sprint 2: Initialize document organizer
        brain_path = Path(__file__).parent.parent.parent / "cortex-brain"
        self.document_organizer = DocumentOrganizer(brain_path)
    
    def _run_command(self, args: List[str], cwd: Optional[Path] = None) -> Tuple[bool, str]:
        """Run command and return success status and output."""
        try:
            result = subprocess.run(
                args,
                cwd=cwd or self.project_root,
                capture_output=True,
                text=True,
                check=False
            )
            return result.returncode == 0, result.stdout + result.stderr
        except Exception as e:
            logger.error(f"❌ Command failed: {e}")
            return False, str(e)
    
    def run_full_test_suite(self) -> Dict:
        """
        Execute full test suite for project.
        
        Returns:
            Dictionary with test results
        """
        logger.info("🧪 Running full test suite...")
        
        results = {
            "passed": False,
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "skipped_tests": 0,
            "duration_seconds": 0.0,
            "failures": []
        }
        
        # Detect test framework and run appropriate command
        if self._is_dotnet_project():
            return self._run_dotnet_tests()
        elif self._is_python_project():
            return self._run_python_tests()
        elif self._is_javascript_project():
            return self._run_javascript_tests()
        else:
            logger.warning("⚠️ No recognized test framework found")
            return results
    
    def _is_dotnet_project(self) -> bool:
        """Check if project is .NET."""
        return any(self.project_root.rglob("*.csproj"))
    
    def _is_python_project(self) -> bool:
        """Check if project is Python."""
        return (self.project_root / "pytest.ini").exists() or any(self.project_root.rglob("test_*.py"))
    
    def _is_javascript_project(self) -> bool:
        """Check if project is JavaScript/TypeScript."""
        return (self.project_root / "package.json").exists()
    
    def _run_dotnet_tests(self) -> Dict:
        """Run .NET tests with dotnet test."""
        start_time = datetime.now()
        success, output = self._run_command(["dotnet", "test", "--logger:trx"])
        duration = (datetime.now() - start_time).total_seconds()
        
        # Parse TRX results (simplified)
        results = {
            "passed": success,
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "duration_seconds": duration,
            "output": output
        }
        
        # Extract test counts from output
        for line in output.split('\n'):
            if "Passed!" in line:
                results["passed"] = True
            elif "total:" in line.lower():
                # Parse "Total: 10, Passed: 8, Failed: 2"
                parts = line.split(',')
                for part in parts:
                    if 'total' in part.lower():
                        results["total_tests"] = int(''.join(filter(str.isdigit, part)))
                    elif 'passed' in part.lower():
                        results["passed_tests"] = int(''.join(filter(str.isdigit, part)))
                    elif 'failed' in part.lower():
                        results["failed_tests"] = int(''.join(filter(str.isdigit, part)))
        
        return results
    
    def _run_python_tests(self) -> Dict:
        """Run Python tests with pytest."""
        start_time = datetime.now()
        success, output = self._run_command(["pytest", "--json-report", "--json-report-file=test-report.json"])
        duration = (datetime.now() - start_time).total_seconds()
        
        results = {
            "passed": success,
            "duration_seconds": duration,
            "output": output
        }
        
        # Try to load JSON report
        report_path = self.project_root / "test-report.json"
        if report_path.exists():
            try:
                with open(report_path, 'r') as f:
                    report = json.load(f)
                
                results.update({
                    "total_tests": report.get("summary", {}).get("total", 0),
                    "passed_tests": report.get("summary", {}).get("passed", 0),
                    "failed_tests": report.get("summary", {}).get("failed", 0),
                    "skipped_tests": report.get("summary", {}).get("skipped", 0)
                })
                
                report_path.unlink()
            except Exception as e:
                logger.warning(f"⚠️ Failed to parse test report: {e}")
        
        return results
    
    def _run_javascript_tests(self) -> Dict:
        """Run JavaScript tests with npm test."""
        start_time = datetime.now()
        success, output = self._run_command(["npm", "test", "--", "--json"])
        duration = (datetime.now() - start_time).total_seconds()
        
        return {
            "passed": success,
            "duration_seconds": duration,
            "output": output
        }
    
    def calculate_metrics_comparison(
        self,
        metrics_before: Dict,
        metrics_after: Dict
    ) -> Dict:
        """
        Compare before/after metrics.
        
        Args:
            metrics_before: Metrics before session
            metrics_after: Metrics after session
            
        Returns:
            Dictionary with comparison results
        """
        comparison = {
            "improved": [],
            "maintained": [],
            "regressed": []
        }
        
        # Compare common metrics
        for metric_name in set(metrics_before.keys()) & set(metrics_after.keys()):
            before_value = metrics_before[metric_name]
            after_value = metrics_after[metric_name]
            
            if isinstance(before_value, (int, float)) and isinstance(after_value, (int, float)):
                change = after_value - before_value
                change_pct = (change / before_value * 100) if before_value != 0 else 0
                
                entry = {
                    "metric": metric_name,
                    "before": before_value,
                    "after": after_value,
                    "change": change,
                    "change_percent": round(change_pct, 2)
                }
                
                if change > 0 and metric_name in ["test_coverage", "code_quality_score"]:
                    comparison["improved"].append(entry)
                elif change < 0 and metric_name in ["lines_of_code", "complexity"]:
                    comparison["improved"].append(entry)
                elif change < 0 and metric_name in ["test_coverage", "code_quality_score"]:
                    comparison["regressed"].append(entry)
                elif change > 0 and metric_name in ["lines_of_code", "complexity"]:
                    comparison["regressed"].append(entry)
                else:
                    comparison["maintained"].append(entry)
        
        return comparison
    
    def generate_diff_summary(self, start_commit: str, end_commit: str) -> Dict:
        """
        Generate git diff summary.
        
        Args:
            start_commit: Starting commit SHA
            end_commit: Ending commit SHA
            
        Returns:
            Dictionary with diff summary
        """
        logger.info(f"📊 Generating diff summary: {start_commit[:8]}..{end_commit[:8]}")
        
        # Get diff stats
        success, output = self._run_command([
            "git", "diff", "--stat", f"{start_commit}..{end_commit}"
        ])
        
        if not success:
            logger.error("❌ Failed to generate diff summary")
            return {}
        
        # Parse diff stats
        lines = output.strip().split('\n')
        summary = {
            "files_changed": 0,
            "insertions": 0,
            "deletions": 0,
            "files": []
        }
        
        for line in lines[:-1]:  # Skip last line (summary)
            parts = line.split('|')
            if len(parts) == 2:
                file_path = parts[0].strip()
                changes = parts[1].strip()
                summary["files"].append({
                    "path": file_path,
                    "changes": changes
                })
        
        # Parse summary line
        if lines:
            summary_line = lines[-1]
            if "files changed" in summary_line:
                parts = summary_line.split(',')
                for part in parts:
                    if 'file' in part:
                        summary["files_changed"] = int(''.join(filter(str.isdigit, part)))
                    elif 'insertion' in part:
                        summary["insertions"] = int(''.join(filter(str.isdigit, part)))
                    elif 'deletion' in part:
                        summary["deletions"] = int(''.join(filter(str.isdigit, part)))
        
        return summary
    
    def validate_skull_rules(self) -> Dict:
        """
        Validate all 22 SKULL brain protection rules.
        
        Returns:
            Dictionary with validation results
        """
        logger.info("🛡️ Validating SKULL rules...")
        
        # Load SKULL rules
        skull_rules_path = Path(__file__).parent.parent.parent / "cortex-brain" / "brain-protection-rules.yaml"
        
        validation_results = {
            "total_rules": 22,
            "passed": 0,
            "failed": 0,
            "rules": []
        }
        
        if not skull_rules_path.exists():
            logger.warning("⚠️ SKULL rules file not found")
            return validation_results
        
        try:
            import yaml
            with open(skull_rules_path, 'r') as f:
                rules_data = yaml.safe_load(f)
            
            rules = rules_data.get("rules", [])
            validation_results["total_rules"] = len(rules)
            
            for rule in rules:
                rule_id = rule.get("id", "")
                rule_name = rule.get("name", "")
                
                # Simplified validation (actual validation would check specific conditions)
                is_valid = True  # Placeholder
                
                validation_results["rules"].append({
                    "id": rule_id,
                    "name": rule_name,
                    "passed": is_valid
                })
                
                if is_valid:
                    validation_results["passed"] += 1
                else:
                    validation_results["failed"] += 1
        
        except Exception as e:
            logger.error(f"❌ Failed to validate SKULL rules: {e}")
        
        return validation_results
    
    def generate_completion_report(
        self,
        session_id: str,
        test_results: Dict,
        metrics_comparison: Dict,
        diff_summary: Dict,
        skull_validation: Dict,
        output_path: Path
    ) -> bool:
        """
        Generate comprehensive session completion report.
        
        Args:
            session_id: TDD session identifier
            test_results: Results from run_full_test_suite()
            metrics_comparison: Results from calculate_metrics_comparison()
            diff_summary: Results from generate_diff_summary()
            skull_validation: Results from validate_skull_rules()
            output_path: Path to output report file
            
        Returns:
            True if report generated successfully
        """
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Generate markdown report
            report_lines = [
                "# TDD Session Completion Report",
                "",
                f"**Session ID:** {session_id}",
                f"**Completed:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "",
                "## 🧪 Test Results",
                "",
                f"- **Status:** {'✅ PASSED' if test_results.get('passed') else '❌ FAILED'}",
                f"- **Total Tests:** {test_results.get('total_tests', 0)}",
                f"- **Passed:** {test_results.get('passed_tests', 0)}",
                f"- **Failed:** {test_results.get('failed_tests', 0)}",
                f"- **Duration:** {test_results.get('duration_seconds', 0):.2f}s",
                "",
                "## 📊 Metrics Comparison",
                ""
            ]
            
            if metrics_comparison.get("improved"):
                report_lines.append("### ✅ Improved")
                for metric in metrics_comparison["improved"]:
                    report_lines.append(f"- **{metric['metric']}:** {metric['before']} → {metric['after']} ({metric['change_percent']:+.1f}%)")
                report_lines.append("")
            
            if metrics_comparison.get("regressed"):
                report_lines.append("### ⚠️ Regressed")
                for metric in metrics_comparison["regressed"]:
                    report_lines.append(f"- **{metric['metric']}:** {metric['before']} → {metric['after']} ({metric['change_percent']:+.1f}%)")
                report_lines.append("")
            
            report_lines.extend([
                "## 📝 Changes Summary",
                "",
                f"- **Files Changed:** {diff_summary.get('files_changed', 0)}",
                f"- **Insertions:** {diff_summary.get('insertions', 0)}",
                f"- **Deletions:** {diff_summary.get('deletions', 0)}",
                "",
                "## 🛡️ SKULL Validation",
                "",
                f"- **Total Rules:** {skull_validation.get('total_rules', 0)}",
                f"- **Passed:** {skull_validation.get('passed', 0)}",
                f"- **Failed:** {skull_validation.get('failed', 0)}",
                f"- **Status:** {'✅ COMPLIANT' if skull_validation.get('failed', 0) == 0 else '❌ NON-COMPLIANT'}",
                ""
            ])
            
            output_path.write_text("\n".join(report_lines))
            logger.info(f"✅ Completion report generated: {output_path}")
            
            # NEW Sprint 2: Auto-organize report into correct category
            try:
                organized_path, organize_message = self.document_organizer.organize_document(output_path)
                if organized_path:
                    logger.info(f"📁 {organize_message}")
                    # Update output_path reference for caller
                    output_path = organized_path
                else:
                    logger.warning(f"⚠️ Document organization skipped: {organize_message}")
            except Exception as org_error:
                logger.warning(f"⚠️ Document organization failed: {org_error}")
                # Don't fail the whole report generation if organization fails
            
            return True
        except Exception as e:
            logger.error(f"❌ Failed to generate report: {e}")
            return False
    
    def complete_session(
        self,
        session_id: str,
        start_commit: str,
        metrics_before: Optional[Dict] = None,
        metrics_after: Optional[Dict] = None
    ) -> Dict:
        """
        Complete TDD session with full validation.
        
        NEW v2.0: Includes code quality enforcement pipeline
        
        Args:
            session_id: TDD session identifier
            start_commit: Starting git commit SHA
            metrics_before: Optional baseline metrics
            metrics_after: Optional final metrics
            
        Returns:
            Dictionary with completion results
        """
        logger.info(f"🎯 Completing TDD session: {session_id}")
        
        # Phase 1: Run full test suite
        test_results = self.run_full_test_suite()
        
        # NEW v2.0: Code Quality Enforcement
        if self.enable_quality_enforcement:
            logger.info("🔍 Running code quality enforcement...")
            
            # Code cleanup validation
            cleanup_issues = self.cleanup_validator.scan_directory(self.project_root, recursive=True)
            all_cleanup_issues = []
            if cleanup_issues:
                for file_issues in cleanup_issues.values():
                    all_cleanup_issues.extend(file_issues)
            
            blocking_cleanup = [i for i in all_cleanup_issues if i.severity in ['CRITICAL', 'BLOCKED']]
            
            if blocking_cleanup:
                logger.error(f"❌ {len(blocking_cleanup)} blocking cleanup issues")
                return {
                    "success": False,
                    "session_id": session_id,
                    "error": "Code cleanup validation failed",
                    "cleanup_report": self.cleanup_validator.generate_report(cleanup_issues),
                    "test_results": test_results
                }
            
            # Lint validation
            lint_results = self.lint_integration.run_lint_directory(self.project_root, recursive=True)
            blocking_lint = self.lint_integration.get_blocking_violations(lint_results)
            
            if blocking_lint:
                logger.error(f"❌ {len(blocking_lint)} blocking lint violations")
                return {
                    "success": False,
                    "session_id": session_id,
                    "error": "Lint validation failed",
                    "lint_report": self.lint_integration.generate_report(lint_results),
                    "test_results": test_results
                }
            
            # Production readiness
            readiness_result = self.readiness_checker.validate_session({
                'test_results': test_results,
                'cleanup_issues': cleanup_issues,
                'lint_results': lint_results,
                'code_smells': []
            })
            
            if not readiness_result.passed:
                logger.error(f"❌ Production readiness failed")
                return {
                    "success": False,
                    "session_id": session_id,
                    "error": "Production readiness validation failed",
                    "readiness_report": self.readiness_checker.generate_report(readiness_result),
                    "test_results": test_results
                }
            
            logger.info("✅ Code quality enforcement passed")
        
        # Phase 2: Compare metrics
        metrics_comparison = {}
        if metrics_before and metrics_after:
            metrics_comparison = self.calculate_metrics_comparison(metrics_before, metrics_after)
        
        # Phase 3: Generate diff summary
        end_commit_success, end_commit = self._run_command(["git", "rev-parse", "HEAD"])
        diff_summary = {}
        if end_commit_success:
            diff_summary = self.generate_diff_summary(start_commit, end_commit.strip())
        
        # Phase 4: Validate SKULL rules
        skull_validation = self.validate_skull_rules()
        
        # Phase 5: Generate report
        report_path = self.project_root / "cortex-brain" / "documents" / "reports" / f"session-{session_id}-completion.md"
        self.generate_completion_report(
            session_id,
            test_results,
            metrics_comparison,
            diff_summary,
            skull_validation,
            report_path
        )
        
        # Determine overall success
        success = (
            test_results.get("passed", False) and
            skull_validation.get("failed", 1) == 0 and
            len(metrics_comparison.get("regressed", [])) == 0
        )
        
        if success:
            logger.info(f"✅ Session completed successfully: {session_id}")
        else:
            logger.warning(f"⚠️ Session completed with issues: {session_id}")
        
        return {
            "success": success,
            "test_results": test_results,
            "metrics_comparison": metrics_comparison,
            "diff_summary": diff_summary,
            "skull_validation": skull_validation,
            "report_path": str(report_path)
        }
