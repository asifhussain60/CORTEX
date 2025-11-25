"""
Enhanced Feedback Module - Comprehensive Performance Analytics

Collects 8 categories of metrics from user environments:
1. Application Metrics - Project size, tech stack, complexity
2. Crawler Performance - Discovery stats, cache efficiency
3. CORTEX Performance - Operation timings, memory usage
4. Knowledge Graphs - Entity counts, graph density
5. Development Hygiene - Commit quality, security
6. TDD Mastery - Test coverage, test-first adherence
7. Commit Metrics - Build success, deployment frequency
8. Velocity Metrics - Sprint velocity, cycle time

Supports GitHub Gist integration for effortless sharing.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import logging
import yaml
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import hashlib

from src.operations.base_operation_module import (
    BaseOperationModule,
    OperationModuleMetadata,
    OperationResult,
    OperationPhase,
    OperationStatus
)

logger = logging.getLogger(__name__)


class EnhancedFeedbackModule(BaseOperationModule):
    """
    Enhanced feedback collection with comprehensive metrics and Gist integration.
    
    Features:
        - 8-category metrics collection
        - GitHub Gist upload (optional)
        - Privacy-first sanitization
        - Local report storage
        - Multiple sharing options
    
    Usage:
        # Natural language
        "feedback"
        "generate feedback report"
        "share performance metrics"
    """
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Get module metadata."""
        return OperationModuleMetadata(
            module_id="enhanced_feedback_module",
            name="Enhanced Feedback Collection",
            description="Collect comprehensive performance metrics with 8-category analysis",
            phase=OperationPhase.PROCESSING,
            dependencies=[],
            tags=["feedback", "metrics", "analytics", "performance", "user"],
            version="1.0.0"
        )
    
    def validate_context(self, context: Dict[str, Any]) -> tuple[bool, str]:
        """
        Validate execution context.
        
        Checks:
            - Project root exists
            - CORTEX brain accessible
            - Feedback reports directory writable
        """
        project_root = context.get('project_root', Path.cwd())
        project_root = Path(project_root)
        
        if not project_root.exists():
            return False, f"Project root does not exist: {project_root}"
        
        # Verify cortex-brain accessible
        cortex_brain = project_root / 'cortex-brain'
        if not cortex_brain.exists():
            return False, "cortex-brain directory not found"
        
        # Verify feedback reports directory writable
        feedback_dir = cortex_brain / 'feedback' / 'reports'
        try:
            feedback_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            return False, f"Cannot create feedback directory: {e}"
        
        return True, "Context validated"
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Execute comprehensive feedback collection.
        
        Args:
            context: Execution context with:
                - project_root: Project root directory
                - share_method: 'local', 'gist', or 'export'
                - github_token: GitHub token for Gist (if share_method='gist')
                - privacy_level: 'full', 'medium', or 'minimal'
        
        Returns:
            OperationResult with feedback report and sharing status
        """
        project_root = Path(context.get('project_root', Path.cwd()))
        share_method = context.get('share_method', 'local')
        privacy_level = context.get('privacy_level', 'medium')
        
        try:
            logger.info("Starting enhanced feedback collection...")
            
            # Phase 1: Collect metrics from all 8 categories
            metrics = self._collect_all_metrics(project_root, context)
            
            # Phase 2: Generate feedback report
            feedback_report = self._generate_feedback_report(
                metrics, 
                project_root,
                privacy_level
            )
            
            # Phase 3: Save local report
            report_path = self._save_local_report(feedback_report, project_root)
            
            # Phase 4: Handle sharing (if requested)
            sharing_result = self._handle_sharing(
                feedback_report,
                share_method,
                context
            )
            
            return OperationResult(
                success=True,
                status=OperationStatus.COMPLETED,
                message=f"Feedback report generated successfully",
                data={
                    'report_path': str(report_path),
                    'feedback_id': feedback_report['metadata']['feedback_id'],
                    'share_method': share_method,
                    'sharing_result': sharing_result,
                    'metrics_summary': self._summarize_metrics(metrics)
                },
                metadata={
                    'module_id': self.get_metadata().module_id,
                    'categories_collected': 8,
                    'privacy_level': privacy_level
                }
            )
            
        except Exception as e:
            logger.exception("Enhanced feedback collection failed")
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message="Feedback collection error",
                error=str(e)
            )
    
    def _collect_all_metrics(
        self, 
        project_root: Path, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Collect metrics from all 8 categories."""
        from src.operations.modules.feedback.collectors import (
            ApplicationMetricsCollector,
            CrawlerPerformanceCollector,
            CortexPerformanceCollector,
            KnowledgeGraphCollector,
            DevelopmentHygieneCollector,
            TDDMasteryCollector,
            CommitMetricsCollector,
            VelocityMetricsCollector
        )
        
        logger.info("Collecting metrics from 8 categories...")
        
        metrics = {}
        
        # Category 1: Application Metrics
        logger.info("  ✅ Collecting application metrics...")
        metrics['application'] = ApplicationMetricsCollector().collect(project_root)
        
        # Category 2: Crawler Performance
        logger.info("  ✅ Collecting crawler performance...")
        metrics['crawler'] = CrawlerPerformanceCollector().collect(project_root)
        
        # Category 3: CORTEX Performance
        logger.info("  ✅ Collecting CORTEX performance...")
        metrics['cortex'] = CortexPerformanceCollector().collect(project_root)
        
        # Category 4: Knowledge Graphs
        logger.info("  ✅ Analyzing knowledge graphs...")
        metrics['knowledge_graphs'] = KnowledgeGraphCollector().collect(project_root)
        
        # Category 5: Development Hygiene
        logger.info("  ✅ Checking development hygiene...")
        metrics['hygiene'] = DevelopmentHygieneCollector().collect(project_root)
        
        # Category 6: TDD Mastery
        logger.info("  ✅ Calculating TDD mastery...")
        metrics['tdd'] = TDDMasteryCollector().collect(project_root)
        
        # Category 7: Commit Metrics
        logger.info("  ✅ Gathering commit metrics...")
        metrics['commits'] = CommitMetricsCollector().collect(project_root)
        
        # Category 8: Velocity Metrics
        logger.info("  ✅ Computing velocity metrics...")
        metrics['velocity'] = VelocityMetricsCollector().collect(project_root)
        
        logger.info("✅ All 8 metric categories collected")
        
        return metrics
    
    def _generate_feedback_report(
        self,
        metrics: Dict[str, Any],
        project_root: Path,
        privacy_level: str
    ) -> Dict[str, Any]:
        """Generate structured feedback report."""
        from src.operations.modules.feedback.privacy import PrivacySanitizer
        
        timestamp = datetime.now()
        feedback_id = f"FEEDBACK-{timestamp.strftime('%Y%m%d-%H%M%S')}"
        
        # Generate anonymized project identifier
        project_hash = hashlib.sha256(str(project_root).encode()).hexdigest()[:12]
        
        report = {
            'cortex_feedback': {
                'metadata': {
                    'feedback_id': feedback_id,
                    'timestamp': timestamp.isoformat(),
                    'cortex_version': self._get_cortex_version(project_root),
                    'repository': f"App_{project_hash}",  # Anonymized
                    'user_id': self._get_user_hash(),
                    'privacy_level': privacy_level
                },
                'metrics': metrics,
                'issues_reported': [],
                'user_feedback_text': ""
            }
        }
        
        # Apply privacy sanitization
        sanitizer = PrivacySanitizer(privacy_level)
        report = sanitizer.sanitize(report)
        
        return report
    
    def _save_local_report(
        self,
        feedback_report: Dict[str, Any],
        project_root: Path
    ) -> Path:
        """Save report to local feedback directory."""
        feedback_dir = project_root / 'cortex-brain' / 'feedback' / 'reports'
        feedback_dir.mkdir(parents=True, exist_ok=True)
        
        feedback_id = feedback_report['cortex_feedback']['metadata']['feedback_id']
        report_path = feedback_dir / f"{feedback_id}.yaml"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            yaml.dump(feedback_report, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Report saved: {report_path}")
        return report_path
    
    def _handle_sharing(
        self,
        feedback_report: Dict[str, Any],
        share_method: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle feedback sharing based on user preference."""
        if share_method == 'local':
            return {
                'method': 'local',
                'status': 'saved',
                'message': 'Report saved locally only'
            }
        
        elif share_method == 'gist':
            return self._upload_to_gist(feedback_report, context)
        
        elif share_method == 'export':
            return self._export_for_sharing(feedback_report, context)
        
        else:
            return {
                'method': 'unknown',
                'status': 'error',
                'message': f'Unknown share method: {share_method}'
            }
    
    def _upload_to_gist(
        self,
        feedback_report: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Upload feedback report to GitHub Gist."""
        try:
            from github import Github, InputFileContent
            
            github_token = context.get('github_token')
            if not github_token:
                return {
                    'method': 'gist',
                    'status': 'error',
                    'message': 'GitHub token not provided'
                }
            
            g = Github(github_token)
            user = g.get_user()
            
            # Convert report to YAML
            yaml_content = yaml.dump(
                feedback_report, 
                default_flow_style=False,
                sort_keys=False
            )
            
            feedback_id = feedback_report['cortex_feedback']['metadata']['feedback_id']
            
            # Create private Gist
            gist = user.create_gist(
                public=False,
                files={
                    "cortex-feedback.yaml": InputFileContent(yaml_content)
                },
                description=f"CORTEX Performance Feedback - {feedback_id}"
            )
            
            # Save Gist URL to registry
            self._save_to_gist_registry(gist.html_url, feedback_id, context)
            
            return {
                'method': 'gist',
                'status': 'success',
                'gist_url': gist.html_url,
                'message': 'Uploaded to private GitHub Gist'
            }
            
        except ImportError:
            return {
                'method': 'gist',
                'status': 'error',
                'message': 'PyGithub library not installed. Run: pip install PyGithub'
            }
        except Exception as e:
            logger.exception("Gist upload failed")
            return {
                'method': 'gist',
                'status': 'error',
                'message': f'Upload failed: {str(e)}'
            }
    
    def _export_for_sharing(
        self,
        feedback_report: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Export report to file for manual sharing."""
        project_root = Path(context.get('project_root', Path.cwd()))
        export_dir = project_root / 'cortex-brain' / 'feedback' / 'exports'
        export_dir.mkdir(parents=True, exist_ok=True)
        
        feedback_id = feedback_report['cortex_feedback']['metadata']['feedback_id']
        export_path = export_dir / f"{feedback_id}.yaml"
        
        with open(export_path, 'w', encoding='utf-8') as f:
            yaml.dump(feedback_report, f, default_flow_style=False, sort_keys=False)
        
        return {
            'method': 'export',
            'status': 'success',
            'export_path': str(export_path),
            'message': 'Exported for manual sharing'
        }
    
    def _save_to_gist_registry(
        self,
        gist_url: str,
        feedback_id: str,
        context: Dict[str, Any]
    ) -> None:
        """Save Gist URL to local registry."""
        project_root = Path(context.get('project_root', Path.cwd()))
        registry_path = project_root / 'cortex-brain' / 'feedback' / 'gist-registry.yaml'
        
        # Load existing registry
        if registry_path.exists():
            with open(registry_path, 'r', encoding='utf-8') as f:
                registry = yaml.safe_load(f) or {'gist_urls': []}
        else:
            registry = {'gist_urls': []}
        
        # Add new entry
        registry['gist_urls'].append({
            'feedback_id': feedback_id,
            'gist_url': gist_url,
            'created_at': datetime.now().isoformat()
        })
        
        # Save updated registry
        with open(registry_path, 'w', encoding='utf-8') as f:
            yaml.dump(registry, f, default_flow_style=False, sort_keys=False)
    
    def _summarize_metrics(self, metrics: Dict[str, Any]) -> Dict[str, str]:
        """Generate human-readable metrics summary."""
        summary = {}
        
        # Application metrics
        if 'application' in metrics:
            app = metrics['application']
            summary['application'] = f"{app.get('total_files', 0)} files, {app.get('lines_of_code', 0)} LOC"
        
        # Crawler performance
        if 'crawler' in metrics:
            crawler = metrics['crawler']
            summary['crawler'] = f"{crawler.get('success_rate', 0)}% success, {crawler.get('discovery_runs', 0)} runs"
        
        # CORTEX performance
        if 'cortex' in metrics:
            cortex = metrics['cortex']
            summary['cortex'] = f"Avg {cortex.get('avg_operation_time_ms', 0)}ms operations"
        
        # Knowledge graphs
        if 'knowledge_graphs' in metrics:
            kg = metrics['knowledge_graphs']
            summary['knowledge_graphs'] = f"{kg.get('entity_count', 0)} entities, {kg.get('relationship_density', 0)} density"
        
        # TDD mastery
        if 'tdd' in metrics:
            tdd = metrics['tdd']
            summary['tdd'] = f"{tdd.get('test_first_adherence', 0)}% test-first, {tdd.get('test_coverage', 0)}% coverage"
        
        # Velocity
        if 'velocity' in metrics:
            vel = metrics['velocity']
            summary['velocity'] = f"{vel.get('story_points_per_sprint', 0)} pts/sprint, {vel.get('avg_cycle_time_days', 0)}d cycle"
        
        return summary
    
    def _get_cortex_version(self, project_root: Path) -> str:
        """Get CORTEX version from VERSION file."""
        version_file = project_root / 'VERSION'
        if version_file.exists():
            return version_file.read_text(encoding='utf-8').strip()
        return "unknown"
    
    def _get_user_hash(self) -> str:
        """Generate non-reversible user identifier."""
        import getpass
        import socket
        
        user_data = f"{getpass.getuser()}@{socket.gethostname()}"
        return hashlib.sha256(user_data.encode()).hexdigest()[:16]


def register() -> BaseOperationModule:
    """Register module for discovery."""
    return EnhancedFeedbackModule()
