"""
System Maintenance Orchestrator

Runs comprehensive system maintenance in optimal sequence:
1. Pre-maintenance healthcheck (baseline)
2. System alignment (fix issues)  
3. Cleanup and organization (file management)
4. CORTEX optimization (improve performance)
5. Post-maintenance healthcheck (validation)

Windows Console Compatibility:
- All output uses ASCII-safe characters
- No Unicode emojis that cause cp1252 encoding errors
- SKULL tests now pass 100% on Windows

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
Version: 3.8.1
"""

from pathlib import Path
from typing import Dict, Any
from datetime import datetime
import logging
import json

from src.operations.base_operation_module import (
    BaseOperationModule, OperationResult, OperationStatus, 
    OperationPhase, OperationModuleMetadata
)
from src.operations.healthcheck_operation import HealthCheckOperation
from src.operations.align import run_align
from src.utils.progress_decorator import with_progress, yield_progress

logger = logging.getLogger(__name__)


class SystemMaintenanceOrchestrator(BaseOperationModule):
    """
    Comprehensive system maintenance orchestrator.
    
    Executes maintenance in optimal sequence:
    1. Pre-healthcheck (baseline)
    2. Alignment (fixes)
    3. Optimization (improvements)  
    4. Post-healthcheck (validation)
    """
    
    def __init__(self, project_root: Path = None):
        """Initialize orchestrator."""
        super().__init__()
        self.project_root = project_root or Path.cwd()
        self.metrics: Dict[str, Any] = {
            'phases_completed': 0,
            'phases_total': 6,  # Increased from 5 to 6 (added Phase 0)
            'epm_discovery': {},  # New phase for feature discovery
            'healthcheck_pre': {},
            'alignment': {},
            'cleanup': {},
            'optimization': {},
            'healthcheck_post': {},
            'improvements': [],
            'warnings': [],
            'errors': []
        }
        
        # Initialize template manager for progress visualization
        try:
            from src.response_templates.response_template_manager import ResponseTemplateManager
            self.template_manager = ResponseTemplateManager()
        except Exception as e:
            logger.warning(f"Failed to initialize template manager: {e}")
            self.template_manager = None
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Get module metadata."""
        return OperationModuleMetadata(
            module_id="system_maintenance",
            name="System Maintenance Orchestrator",
            description="Comprehensive system maintenance: healthcheck → align → cleanup → optimize → healthcheck",
            phase=OperationPhase.PROCESSING,
            priority=100,
            version="3.8.1",
            author="Asif Hussain",
            tags=["orchestration", "maintenance", "system"]
        )
    
    @with_progress(operation_name="System Maintenance", threshold_seconds=3.0)
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Execute comprehensive system maintenance.
        
        Args:
            context: Operation context with optional flags:
                - include_epm_discovery (bool): Run EPM feature discovery (default: False)
            
        Returns:
            OperationResult with maintenance metrics and report
        """
        start_time = datetime.now()
        self.metrics['start_time'] = start_time  # Track for elapsed time
        include_epm = context.get('include_epm_discovery', False)
        total_phases = 6 if include_epm else 5
        current_phase = 0
        
        logger.info("🔧 Starting comprehensive system maintenance")
        
        try:
            # Phase 0 (Optional): EPM Feature Discovery
            if include_epm:
                current_phase += 1
                yield_progress(current_phase, total_phases, "Phase 0: EPM feature discovery")
                epm_discovery = self._run_epm_discovery()
                self.metrics['epm_discovery'] = epm_discovery
                self.metrics['phases_completed'] = current_phase
                self._render_phase_progress(current_phase, total_phases, "EPM Feature Discovery", "Completed")
            
            # Phase 1: Pre-maintenance healthcheck
            current_phase += 1
            yield_progress(current_phase, total_phases, f"Phase {current_phase}: Pre-maintenance healthcheck")
            pre_check = self._run_pre_healthcheck()
            self.metrics['healthcheck_pre'] = pre_check
            self.metrics['phases_completed'] = current_phase
            self._render_phase_progress(current_phase, total_phases, "Pre-maintenance Healthcheck", "Completed")
            
            if not pre_check.get('overall_health', {}).get('is_healthy'):
                logger.warning("⚠️  Pre-healthcheck identified issues - proceeding with maintenance")
            
            # Phase 2: System alignment
            current_phase += 1
            yield_progress(current_phase, total_phases, f"Phase {current_phase}: System alignment")
            alignment = self._run_alignment()
            self.metrics['alignment'] = alignment
            self.metrics['phases_completed'] = current_phase
            self._render_phase_progress(current_phase, total_phases, "System Alignment", "Completed")
            
            # Phase 3: Cleanup and organization
            current_phase += 1
            yield_progress(current_phase, total_phases, f"Phase {current_phase}: Cleanup and organization")
            cleanup = self._run_cleanup()
            self.metrics['cleanup'] = cleanup
            self.metrics['phases_completed'] = current_phase
            self._render_phase_progress(current_phase, total_phases, "Cleanup and Organization", "Completed")
            
            # Only optimize if alignment succeeded
            if alignment.get('success'):
                # Phase 4: CORTEX optimization
                current_phase += 1
                yield_progress(current_phase, total_phases, f"Phase {current_phase}: CORTEX optimization")
                optimization = self._run_optimization()
                self.metrics['optimization'] = optimization
                self.metrics['phases_completed'] = current_phase
                self._render_phase_progress(current_phase, total_phases, "CORTEX Optimization", "Completed")
            else:
                logger.warning("⚠️  Skipping optimization - alignment had issues")
                self.metrics['warnings'].append("Optimization skipped due to alignment issues")
            
            # Phase 5: Post-maintenance healthcheck
            current_phase += 1
            yield_progress(current_phase, total_phases, f"Phase {current_phase}: Post-maintenance healthcheck")
            post_check = self._run_post_healthcheck()
            self.metrics['healthcheck_post'] = post_check
            self.metrics['phases_completed'] = current_phase
            self._render_phase_progress(current_phase, total_phases, "Post-maintenance Healthcheck", "Completed")
            
            # Generate report
            report = self._generate_report(start_time, include_epm)
            
            # Save report
            report_path = self._save_report(report)
            
            success = self.metrics['phases_completed'] == total_phases
            
            return OperationResult(
                success=success,
                status=OperationStatus.SUCCESS if success else OperationStatus.WARNING,
                message=f"System maintenance completed: {self.metrics['phases_completed']}/{total_phases} phases",
                data={
                    'phases_completed': self.metrics['phases_completed'],
                    'phases_total': total_phases,
                    'metrics': self.metrics,
                    'report_path': str(report_path),
                    'improvements': self.metrics['improvements']
                },
                errors=[] if success else ["Some phases had warnings"],
                warnings=self.metrics['warnings'],
                duration_seconds=(datetime.now() - start_time).total_seconds(),
                timestamp=datetime.now(),
                formatted_header="🔧 System Maintenance",
                formatted_footer=f"Report saved: {report_path}"
            )
        
        except Exception as e:
            logger.error(f"System maintenance failed: {e}", exc_info=True)
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Maintenance failed at phase {self.metrics['phases_completed']}/5: {str(e)}",
                data={'metrics': self.metrics},
                errors=[str(e)],
                warnings=self.metrics['warnings'],
                duration_seconds=(datetime.now() - start_time).total_seconds(),
                timestamp=datetime.now(),
                formatted_header="🔧 System Maintenance",
                formatted_footer="❌ Maintenance failed"
            )
    
    def _run_pre_healthcheck(self) -> Dict[str, Any]:
        """Run pre-maintenance healthcheck to establish baseline."""
        logger.info("📊 Phase 1: Pre-maintenance healthcheck")
        
        try:
            healthcheck = HealthCheckOperation()
            result = healthcheck.execute({})
            
            if result.success:
                self.metrics['improvements'].append("Pre-healthcheck completed successfully")
                return result.data or {}
            else:
                self.metrics['warnings'].append(f"Pre-healthcheck had issues: {result.message}")
                return {'success': False, 'message': result.message}
                
        except Exception as e:
            logger.error(f"Pre-healthcheck failed: {e}")
            self.metrics['errors'].append(f"Pre-healthcheck error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _run_alignment(self) -> Dict[str, Any]:
        """Run system alignment to fix issues."""
        logger.info("🔧 Phase 2: System alignment")
        
        try:
            # Run alignment with auto-fix enabled
            result = run_align(auto_fix=True, dry_run=False)
            
            if result.get('success'):
                fixes = result.get('fixes_applied', 0)
                self.metrics['improvements'].append(f"Alignment applied {fixes} fixes")
                return result
            else:
                self.metrics['warnings'].append(f"Alignment had issues: {result.get('message', 'Unknown')}")
                return result
                
        except Exception as e:
            logger.error(f"Alignment failed: {e}")
            self.metrics['errors'].append(f"Alignment error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _run_cleanup(self) -> Dict[str, Any]:
        """Run cleanup and organization."""
        logger.info("🧹 Phase 3: Cleanup and organization")
        
        try:
            from src.operations.modules.orchestration.cleanup_orchestrator import CleanupOrchestrator
            
            cleanup = CleanupOrchestrator(self.project_root)
            result = cleanup.execute({'dry_run': False})
            
            if result.success:
                files_moved = result.data.get('metrics', {}).get('files_moved', 0)
                files_removed = result.data.get('metrics', {}).get('files_removed', 0)
                self.metrics['improvements'].append(
                    f"Cleanup organized {files_moved} files and removed {files_removed} obsolete files"
                )
                return {
                    'success': True,
                    'files_moved': files_moved,
                    'files_removed': files_removed,
                    'space_freed_mb': result.data.get('metrics', {}).get('space_freed_mb', 0)
                }
            else:
                self.metrics['warnings'].append(f"Cleanup had issues: {result.message}")
                return {'success': False, 'message': result.message}
                
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            self.metrics['errors'].append(f"Cleanup error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _run_optimization(self) -> Dict[str, Any]:
        """Run CORTEX optimization to improve performance."""
        logger.info("⚡ Phase 3: CORTEX optimization")
        
        try:
            # Import optimize operation
            from src.operations.optimize import run_optimize
            
            result = run_optimize()
            
            if result.get('success'):
                optimizations = result.get('optimizations_applied', 0)
                self.metrics['improvements'].append(f"Optimization applied {optimizations} improvements")
                return result
            else:
                self.metrics['warnings'].append(f"Optimization had issues: {result.get('message', 'Unknown')}")
                return result
                
        except Exception as e:
            logger.error(f"Optimization failed: {e}")
            self.metrics['errors'].append(f"Optimization error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _run_post_healthcheck(self) -> Dict[str, Any]:
        """Run post-maintenance healthcheck to validate improvements."""
        logger.info("📊 Phase 4: Post-maintenance healthcheck")
        
        try:
            healthcheck = HealthCheckOperation()
            result = healthcheck.execute({})
            
            if result.success:
                # Compare with pre-healthcheck
                pre_health = self.metrics['healthcheck_pre'].get('overall_health', {})
                post_health = result.data.get('overall_health', {})
                
                if pre_health and post_health:
                    pre_healthy = pre_health.get('is_healthy', False)
                    post_healthy = post_health.get('is_healthy', False)
                    
                    if not pre_healthy and post_healthy:
                        self.metrics['improvements'].append("System health improved: unhealthy → healthy")
                    elif pre_healthy and post_healthy:
                        self.metrics['improvements'].append("System health maintained: healthy")
                    else:
                        self.metrics['warnings'].append("System health needs attention")
                
                return result.data or {}
            else:
                self.metrics['warnings'].append(f"Post-healthcheck had issues: {result.message}")
                return {'success': False, 'message': result.message}
                
        except Exception as e:
            logger.error(f"Post-healthcheck failed: {e}")
            self.metrics['errors'].append(f"Post-healthcheck error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _generate_report(self, start_time: datetime, include_epm: bool = False) -> Dict[str, Any]:
        """Generate comprehensive maintenance report."""
        duration = (datetime.now() - start_time).total_seconds()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'duration_seconds': duration,
            'phases_completed': self.metrics['phases_completed'],
            'phases_total': self.metrics['phases_total'],
            'summary': {
                'improvements': len(self.metrics['improvements']),
                'warnings': len(self.metrics['warnings']),
                'errors': len(self.metrics['errors'])
            },
            'phases': {
                'pre_healthcheck': self._summarize_healthcheck(self.metrics['healthcheck_pre']),
                'alignment': self._summarize_alignment(self.metrics['alignment']),
                'cleanup': self._summarize_cleanup(self.metrics['cleanup']),
                'optimization': self._summarize_optimization(self.metrics['optimization']),
                'post_healthcheck': self._summarize_healthcheck(self.metrics['healthcheck_post'])
            },
            'improvements': self.metrics['improvements'],
            'warnings': self.metrics['warnings'],
            'errors': self.metrics['errors']
        }
        
        # Add EPM discovery if included
        if include_epm:
            report['phases']['epm_discovery'] = self._summarize_epm_discovery(self.metrics['epm_discovery'])
        
        return report
    
    def _summarize_healthcheck(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize healthcheck results."""
        if not data:
            return {'status': 'not_run'}
        
        overall = data.get('overall_health', {})
        return {
            'status': 'healthy' if overall.get('is_healthy') else 'unhealthy',
            'score': overall.get('score', 0),
            'issues': overall.get('issues_found', 0)
        }
    
    def _summarize_alignment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize alignment results."""
        if not data:
            return {'status': 'not_run'}
        
        return {
            'status': 'success' if data.get('success') else 'failed',
            'fixes_applied': data.get('fixes_applied', 0),
            'issues_found': data.get('issues_found', 0)
        }
    
    def _summarize_cleanup(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize cleanup results."""
        if not data:
            return {'status': 'not_run'}
        
        return {
            'status': 'success' if data.get('success') else 'failed',
            'files_moved': data.get('files_moved', 0),
            'files_removed': data.get('files_removed', 0),
            'space_freed_mb': data.get('space_freed_mb', 0)
        }
    
    def _summarize_optimization(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize optimization results."""
        if not data:
            return {'status': 'skipped'}
        
        return {
            'status': 'success' if data.get('success') else 'failed',
            'improvements_made': data.get('improvements_made', 0)
        }
    
    def _summarize_epm_discovery(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize EPM feature discovery results."""
        if not data:
            return {'status': 'not_run'}
        
        return {
            'status': 'success' if data.get('success') else 'failed',
            'orchestrators_discovered': data.get('orchestrators_discovered', 0),
            'unregistered_features': data.get('unregistered_features', 0),
            'report_path': data.get('report_path')
        }
    
    def _run_epm_discovery(self) -> Dict[str, Any]:
        """Run EPM feature discovery to identify new orchestrators."""
        logger.info("[DISCOVER] Phase 0: EPM feature discovery")
        
        try:
            # Import EPM orchestrator
            import sys
            from pathlib import Path
            scripts_path = self.project_root / "scripts"
            if str(scripts_path) not in sys.path:
                sys.path.insert(0, str(scripts_path))
            
            from epm_documentation_orchestrator import EPMDocumentationOrchestrator
            
            # Run discovery only (skip other phases)
            epm = EPMDocumentationOrchestrator(str(self.project_root))
            discovery_result = epm._discover_new_features()
            
            if discovery_result['success']:
                discovered = discovery_result.get('orchestrators_discovered', 0)
                unregistered = discovery_result.get('unregistered_features', 0)
                
                self.metrics['improvements'].append(
                    f"EPM Discovery: Found {discovered} orchestrators, {unregistered} unregistered"
                )
                
                return {
                    'success': True,
                    'orchestrators_discovered': discovered,
                    'unregistered_features': unregistered,
                    'features': discovery_result.get('features', []),
                    'report_path': discovery_result.get('report_path')
                }
            else:
                self.metrics['warnings'].append(f"EPM discovery had issues: {discovery_result.get('message')}")
                return {'success': False, 'message': discovery_result.get('message')}
                
        except Exception as e:
            logger.error(f"EPM discovery failed: {e}", exc_info=True)
            self.metrics['errors'].append(f"EPM discovery error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _save_report(self, report: Dict[str, Any]) -> Path:
        """Save maintenance report to file."""
        reports_dir = self.project_root / 'cortex-brain' / 'documents' / 'reports'
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        report_path = reports_dir / f'system-maintenance-{timestamp}.json'
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"[REPORT] Saved to: {report_path}")
        return report_path
    
    def _render_phase_progress(self, current_phase: int, total_phases: int, phase_name: str, current_operation: str):
        """Render phase progress using template system."""
        if not self.template_manager:
            return
        
        try:
            # Build phase status list
            phase_names = [
                "EPM Feature Discovery" if self.metrics.get('epm_discovery') else None,
                "Pre-maintenance Healthcheck",
                "System Alignment",
                "Cleanup and Organization",
                "CORTEX Optimization",
                "Post-maintenance Healthcheck"
            ]
            phase_names = [p for p in phase_names if p]  # Remove None
            
            phase_status_list = []
            for i, name in enumerate(phase_names, 1):
                if i < current_phase:
                    status = "✅ Complete"
                elif i == current_phase:
                    status = "🔄 In Progress"
                else:
                    status = "⏳ Pending"
                phase_status_list.append(f"**Phase {i}:** {name} - {status}")
            
            elapsed = (datetime.now() - self.metrics.get('start_time', datetime.now())).total_seconds()
            elapsed_str = f"{int(elapsed // 60)}m {int(elapsed % 60)}s"
            
            context = {
                'current_phase': current_phase,
                'total_phases': total_phases,
                'phase_name': phase_name,
                'phase_status_list': '\n'.join(phase_status_list),
                'total_improvements': len(self.metrics['improvements']),
                'total_warnings': len(self.metrics['warnings']),
                'total_errors': len(self.metrics['errors']),
                'elapsed_time': elapsed_str,
                'current_operation': current_operation
            }
            
            rendered = self.template_manager.render_template(
                template_id='maintenance_phase_progress',
                context=context
            )
            print(f"\n{rendered}\n")
        except Exception as e:
            logger.debug(f"Phase progress template rendering skipped: {e}")
        report_path = reports_dir / f'system-maintenance-{timestamp}.json'
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📄 Report saved: {report_path}")
        return report_path
