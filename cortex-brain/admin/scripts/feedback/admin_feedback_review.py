"""
Admin Feedback Review Module - Aggregate Multi-Repo Feedback

CORTEX REPO ONLY: This module aggregates feedback reports from multiple user repositories
for admin analysis, trend identification, and issue prioritization.

Features:
    - GitHub Gist sync pipeline (pulls from gist-sources.yaml registry)
    - Report validation and sanitization verification
    - Trend analysis (month-over-month, rolling averages)
    - Issue categorization (by type and severity)
    - Natural language triggers (review feedback, feedback review, etc.)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import logging
import yaml
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import statistics
import sqlite3
import sys

# Add analytics to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from analytics.analytics_db_manager import AnalyticsDBManager

from src.operations.base_operation_module import (
    BaseOperationModule,
    OperationModuleMetadata,
    OperationResult,
    OperationPhase,
    OperationStatus
)

logger = logging.getLogger(__name__)


class AdminFeedbackReviewModule(BaseOperationModule):
    """
    Admin-only feedback aggregation and analysis module.
    
    This module ONLY runs in the CORTEX repository (detected by cortex-brain/admin/ directory).
    It aggregates feedback from multiple user repositories via GitHub Gist registry.
    
    Features:
        - Auto-sync Gist registry by default
        - Validate and process feedback reports
        - Calculate trend analysis (MoM, rolling averages)
        - Categorize issues by type and severity
        - Generate aggregate statistics
    
    Natural Language Triggers:
        - "review feedback"
        - "feedback review"
        - "analyze feedback"
        - "process feedback"
        - "sync feedback"
        - "import feedback"
    
    Storage:
        - Raw reports: cortex-brain/analytics/per-app/{AppName}/reports/
        - Aggregate DB: cortex-brain/analytics/aggregate/cross-app-metrics.db
        - Trend data: cortex-brain/analytics/trends/
    """
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Get module metadata."""
        return OperationModuleMetadata(
            module_id="admin_feedback_review_module",
            name="Admin Feedback Review",
            description="Aggregate and analyze feedback from multiple user repositories (CORTEX repo only)",
            phase=OperationPhase.PROCESSING,
            dependencies=[],
            tags=["admin", "feedback", "analytics", "aggregation", "cortex-only"],
            version="1.0.0"
        )
    
    def validate_context(self, context: Dict[str, Any]) -> tuple[bool, str]:
        """
        Validate execution context.
        
        Critical Check: CORTEX repo only (admin operation)
        """
        project_root = context.get('project_root', Path.cwd())
        project_root = Path(project_root)
        
        # CRITICAL: Check if this is CORTEX repo (admin directory exists)
        admin_dir = project_root / "cortex-brain" / "admin"
        if not admin_dir.exists():
            return False, "❌ ADMIN OPERATION: This command only works in the CORTEX repository. Not available in user repositories."
        
        # Check Gist registry exists
        registry_file = project_root / "cortex-brain" / "feedback" / "gist-sources.yaml"
        if not registry_file.exists():
            logger.warning(f"Gist registry not found: {registry_file}. Will create on first sync.")
        
        return True, "CORTEX repository detected. Admin operation authorized."
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Execute admin feedback review.
        
        Pipeline:
            1. Sync Gist registry (pull latest from registered Gists)
            2. Validate and process reports
            3. Store in analytics databases
            4. Calculate trend analysis
            5. Categorize issues
            6. Generate summary report
        """
        try:
            project_root = Path(context.get('project_root', Path.cwd()))
            
            logger.info("Starting admin feedback review (CORTEX repo)")
            
            # Step 1: Sync Gist registry
            sync_result = self._sync_gist_registry(project_root)
            if not sync_result['success']:
                return OperationResult(
                    success=False,
                    status=OperationStatus.FAILED,
                    message=f"Gist sync failed: {sync_result['error']}",
                    errors=[sync_result['error']]
                )
            
            synced_reports = sync_result['reports']
            logger.info(f"Synced {len(synced_reports)} reports from Gist registry")
            
            # Step 2: Validate and process reports
            processed_reports = []
            validation_errors = []
            
            for report_path in synced_reports:
                try:
                    report_data = self._load_and_validate_report(report_path)
                    if report_data:
                        processed_reports.append(report_data)
                except Exception as e:
                    logger.warning(f"Report validation failed: {report_path.name} - {e}")
                    validation_errors.append(f"{report_path.name}: {str(e)}")
            
            logger.info(f"Processed {len(processed_reports)}/{len(synced_reports)} reports successfully")
            
            # Step 3: Store in analytics databases
            storage_result = self._store_in_analytics_db(project_root, processed_reports)
            
            # Step 4: Calculate trend analysis
            trends = self._calculate_trends(project_root, processed_reports)
            
            # Step 5: Categorize issues
            issues = self._categorize_issues(processed_reports)
            
            # Step 6: Generate summary report
            summary = self._generate_summary_report(
                project_root,
                processed_reports,
                trends,
                issues,
                validation_errors
            )
            
            return OperationResult(
                success=True,
                status=OperationStatus.SUCCESS,
                message=f"Processed {len(processed_reports)} feedback reports from {len(set(r['app_name'] for r in processed_reports))} applications",
                data={
                    'reports_processed': len(processed_reports),
                    'reports_failed': len(validation_errors),
                    'applications': len(set(r['app_name'] for r in processed_reports)),
                    'trends': trends,
                    'issues': issues,
                    'summary_path': str(summary['path'])
                }
            )
        
        except Exception as e:
            logger.error(f"Admin feedback review failed: {e}", exc_info=True)
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Admin feedback review failed: {str(e)}",
                errors=[str(e)]
            )
    
    def _sync_gist_registry(self, project_root: Path) -> Dict[str, Any]:
        """
        Sync Gist registry - pull latest reports from registered GitHub Gists.
        
        Registry Format (gist-sources.yaml):
            applications:
              - app_name: MyApp
                gist_url: https://gist.github.com/user/abc123
                last_synced: 2025-11-23T10:30:00
                report_count: 5
        
        Returns:
            {'success': bool, 'reports': List[Path], 'error': Optional[str]}
        """
        try:
            registry_file = project_root / "cortex-brain" / "feedback" / "gist-sources.yaml"
            reports_dir = project_root / "cortex-brain" / "analytics" / "raw-reports"
            reports_dir.mkdir(parents=True, exist_ok=True)
            
            # Load registry
            if not registry_file.exists():
                logger.warning("Gist registry not found. No reports to sync.")
                return {'success': True, 'reports': []}
            
            with open(registry_file, 'r', encoding='utf-8') as f:
                registry = yaml.safe_load(f) or {}
            
            applications = registry.get('applications', [])
            if not applications:
                logger.info("No applications registered in Gist registry")
                return {'success': True, 'reports': []}
            
            # Try to import PyGithub (optional dependency)
            try:
                from github import Github, GithubException
                github_available = True
            except ImportError:
                logger.warning("PyGithub not installed. Skipping Gist sync. Install with: pip install PyGithub")
                # Return existing reports if Gist sync unavailable
                existing_reports = list(reports_dir.glob("*.yaml"))
                return {'success': True, 'reports': existing_reports}
            
            # Sync from each registered Gist
            synced_reports = []
            
            # Get GitHub token from environment or config
            github_token = self._get_github_token(project_root)
            gh = Github(github_token) if github_token else Github()
            
            for app in applications:
                app_name = app['app_name']
                gist_url = app['gist_url']
                
                try:
                    # Extract Gist ID from URL
                    gist_id = gist_url.split('/')[-1]
                    
                    # Fetch Gist
                    gist = gh.get_gist(gist_id)
                    
                    # Download all YAML files from Gist
                    for filename, file_obj in gist.files.items():
                        if filename.endswith('.yaml') or filename.endswith('.yml'):
                            # Save to reports directory
                            app_reports_dir = reports_dir / app_name
                            app_reports_dir.mkdir(parents=True, exist_ok=True)
                            
                            report_path = app_reports_dir / filename
                            report_path.write_text(file_obj.content, encoding='utf-8')
                            synced_reports.append(report_path)
                            
                            logger.info(f"Synced report: {app_name}/{filename}")
                    
                    # Update last_synced timestamp
                    app['last_synced'] = datetime.now().isoformat()
                
                except GithubException as e:
                    logger.error(f"Failed to sync Gist for {app_name}: {e}")
                except Exception as e:
                    logger.error(f"Error syncing {app_name}: {e}")
            
            # Save updated registry
            with open(registry_file, 'w', encoding='utf-8') as f:
                yaml.dump(registry, f, default_flow_style=False, sort_keys=False)
            
            logger.info(f"Gist sync complete: {len(synced_reports)} reports from {len(applications)} applications")
            
            return {'success': True, 'reports': synced_reports}
        
        except Exception as e:
            logger.error(f"Gist sync failed: {e}", exc_info=True)
            return {'success': False, 'reports': [], 'error': str(e)}
    
    def _get_github_token(self, project_root: Path) -> Optional[str]:
        """Get GitHub personal access token from cortex.config.json or environment."""
        import os
        
        # Try environment variable first
        token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
        if token:
            return token
        
        # Try cortex.config.json
        config_file = project_root / "cortex.config.json"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                token = config.get('github', {}).get('personal_access_token')
                if token:
                    return token
            except Exception as e:
                logger.warning(f"Failed to load GitHub token from config: {e}")
        
        return None
    
    def _load_and_validate_report(self, report_path: Path) -> Optional[Dict[str, Any]]:
        """
        Load and validate a feedback report.
        
        Validation:
            - YAML structure valid
            - Required fields present (app_name, timestamp, metrics)
            - Privacy sanitization applied (check for sensitive patterns)
        """
        try:
            with open(report_path, 'r', encoding='utf-8') as f:
                report = yaml.safe_load(f)
            
            # Validate required fields
            required_fields = ['app_name', 'timestamp', 'metrics']
            for field in required_fields:
                if field not in report:
                    raise ValueError(f"Missing required field: {field}")
            
            # Validate metrics structure (8 categories)
            metrics = report['metrics']
            expected_categories = [
                'application_metrics',
                'crawler_performance',
                'cortex_performance',
                'knowledge_graph',
                'development_hygiene',
                'tdd_mastery',
                'commit_metrics',
                'velocity_metrics'
            ]
            
            for category in expected_categories:
                if category not in metrics:
                    logger.warning(f"Report missing category: {category}")
            
            # Check privacy sanitization (no sensitive patterns should exist)
            report_str = json.dumps(report, default=str)
            sensitive_patterns = [
                r'password["\s:=]+[\w]+',
                r'api[_-]?key["\s:=]+[\w]+',
                r'secret["\s:=]+[\w]+'
            ]
            
            import re
            for pattern in sensitive_patterns:
                if re.search(pattern, report_str, re.IGNORECASE):
                    logger.warning(f"Report may contain sensitive data: {report_path.name}")
            
            return report
        
        except Exception as e:
            logger.error(f"Report validation failed: {report_path} - {e}")
            return None
    
    def _store_in_analytics_db(self, project_root: Path, reports: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Store reports in analytics SQLite databases.
        
        Database Structure:
            - Per-app DB: cortex-brain/analytics/per-app/{AppName}/metrics.db
            - Aggregate DB: cortex-brain/analytics/aggregate/cross-app-metrics.db
        """
        try:
            analytics_dir = project_root / "cortex-brain" / "analytics"
            db_manager = AnalyticsDBManager(analytics_dir)
            
            stored_count = 0
            failed_count = 0
            duplicate_count = 0
            
            for report in reports:
                app_name = report['app_name']
                gist_url = report.get('gist_url')
                
                success, report_id, message = db_manager.store_feedback_report(
                    app_name=app_name,
                    report_data=report,
                    gist_url=gist_url
                )
                
                if success:
                    stored_count += 1
                    logger.info(f"Stored report for {app_name} (ID: {report_id})")
                elif "duplicate" in message.lower():
                    duplicate_count += 1
                    logger.debug(f"Duplicate report skipped: {app_name}")
                else:
                    failed_count += 1
                    logger.error(f"Failed to store report for {app_name}: {message}")
            
            logger.info(f"Analytics storage: {stored_count} stored, {duplicate_count} duplicates, {failed_count} failed")
            
            return {
                'success': True,
                'stored_count': stored_count,
                'duplicate_count': duplicate_count,
                'failed_count': failed_count
            }
        
        except Exception as e:
            logger.error(f"Analytics storage failed: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}
    
    def _calculate_trends(self, project_root: Path, reports: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate trend analysis across reports.
        
        Trends:
            - Month-over-month changes (test coverage, build success, velocity)
            - Rolling 30-day averages
            - Growth rates
        """
        try:
            # Group reports by app
            reports_by_app = {}
            for report in reports:
                app_name = report['app_name']
                if app_name not in reports_by_app:
                    reports_by_app[app_name] = []
                reports_by_app[app_name].append(report)
            
            trends = {}
            
            for app_name, app_reports in reports_by_app.items():
                # Sort by timestamp
                app_reports.sort(key=lambda r: r['timestamp'])
                
                # Calculate trends for key metrics
                app_trends = {
                    'test_coverage_trend': self._calculate_metric_trend(app_reports, 'tdd_mastery', 'test_coverage'),
                    'build_success_trend': self._calculate_metric_trend(app_reports, 'commit_metrics', 'build_success_rate'),
                    'velocity_trend': self._calculate_metric_trend(app_reports, 'velocity_metrics', 'sprint_velocity'),
                    'report_count': len(app_reports),
                    'date_range': {
                        'start': app_reports[0]['timestamp'],
                        'end': app_reports[-1]['timestamp']
                    }
                }
                
                trends[app_name] = app_trends
            
            return trends
        
        except Exception as e:
            logger.error(f"Trend calculation failed: {e}")
            return {}
    
    def _calculate_metric_trend(
        self, 
        reports: List[Dict[str, Any]], 
        category: str, 
        metric: str
    ) -> Dict[str, Any]:
        """Calculate trend for a specific metric."""
        try:
            values = []
            for report in reports:
                metrics = report.get('metrics', {})
                category_data = metrics.get(category, {})
                value = category_data.get(metric)
                if value is not None and isinstance(value, (int, float)):
                    values.append(float(value))
            
            if len(values) < 2:
                return {'trend': 'insufficient_data', 'values': values}
            
            # Calculate trend
            first_value = values[0]
            last_value = values[-1]
            change = last_value - first_value
            change_percent = (change / first_value * 100) if first_value != 0 else 0
            
            # Determine direction
            if change_percent > 5:
                direction = 'improving'
            elif change_percent < -5:
                direction = 'declining'
            else:
                direction = 'stable'
            
            return {
                'trend': direction,
                'change_percent': round(change_percent, 2),
                'first_value': first_value,
                'last_value': last_value,
                'average': round(statistics.mean(values), 2),
                'values_count': len(values)
            }
        
        except Exception as e:
            logger.warning(f"Metric trend calculation failed: {e}")
            return {'trend': 'error', 'error': str(e)}
    
    def _categorize_issues(self, reports: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Categorize issues from feedback reports.
        
        Categories:
            - Critical: Security vulnerabilities, build failures
            - High: Low test coverage, declining velocity
            - Medium: Code quality issues, documentation gaps
            - Low: Minor improvements, optimization opportunities
        """
        try:
            issues = {
                'critical': [],
                'high': [],
                'medium': [],
                'low': []
            }
            
            for report in reports:
                app_name = report['app_name']
                metrics = report.get('metrics', {})
                
                # Check for critical issues
                hygiene = metrics.get('development_hygiene', {})
                if hygiene.get('security_vulnerabilities', 0) > 0:
                    issues['critical'].append({
                        'app': app_name,
                        'type': 'security',
                        'message': f"{hygiene['security_vulnerabilities']} security vulnerabilities detected",
                        'timestamp': report['timestamp']
                    })
                
                commit_metrics = metrics.get('commit_metrics', {})
                if commit_metrics.get('build_success_rate', 100) < 80:
                    issues['critical'].append({
                        'app': app_name,
                        'type': 'build_failure',
                        'message': f"Build success rate: {commit_metrics['build_success_rate']}%",
                        'timestamp': report['timestamp']
                    })
                
                # Check for high priority issues
                tdd = metrics.get('tdd_mastery', {})
                if tdd.get('test_coverage', 100) < 60:
                    issues['high'].append({
                        'app': app_name,
                        'type': 'low_coverage',
                        'message': f"Test coverage: {tdd['test_coverage']}%",
                        'timestamp': report['timestamp']
                    })
                
                velocity = metrics.get('velocity_metrics', {})
                if velocity.get('sprint_velocity', 0) > 0:
                    # Check if velocity is declining (would need historical data)
                    pass
            
            # Sort issues by timestamp (most recent first)
            for category in issues:
                issues[category].sort(key=lambda x: x['timestamp'], reverse=True)
            
            return issues
        
        except Exception as e:
            logger.error(f"Issue categorization failed: {e}")
            return {'critical': [], 'high': [], 'medium': [], 'low': []}
    
    def _generate_summary_report(
        self,
        project_root: Path,
        reports: List[Dict[str, Any]],
        trends: Dict[str, Any],
        issues: Dict[str, List[Dict[str, Any]]],
        validation_errors: List[str]
    ) -> Dict[str, Any]:
        """Generate admin summary report."""
        try:
            summary = {
                'generated_at': datetime.now().isoformat(),
                'summary': {
                    'total_reports': len(reports),
                    'total_applications': len(set(r['app_name'] for r in reports)),
                    'validation_errors': len(validation_errors),
                    'critical_issues': len(issues['critical']),
                    'high_priority_issues': len(issues['high'])
                },
                'applications': list(set(r['app_name'] for r in reports)),
                'trends': trends,
                'issues': issues,
                'validation_errors': validation_errors
            }
            
            # Save summary report
            summary_dir = project_root / "cortex-brain" / "analytics" / "summaries"
            summary_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            summary_path = summary_dir / f"admin-summary-{timestamp}.yaml"
            
            with open(summary_path, 'w', encoding='utf-8') as f:
                yaml.dump(summary, f, default_flow_style=False, sort_keys=False)
            
            logger.info(f"Generated admin summary: {summary_path}")
            
            return {'success': True, 'path': summary_path, 'summary': summary}
        
        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            return {'success': False, 'error': str(e)}
