"""
System Maintenance Orchestrator

Runs comprehensive system maintenance in optimal sequence:
1. Pre-maintenance healthcheck (baseline)
2. System alignment (fix issues)  
3. CORTEX optimization (improve performance)
4. Post-maintenance healthcheck (validation)

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
            'phases_total': 4,
            'healthcheck_pre': {},
            'alignment': {},
            'optimization': {},
            'healthcheck_post': {},
            'improvements': [],
            'warnings': [],
            'errors': []
        }
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Get module metadata."""
        return OperationModuleMetadata(
            module_id="system_maintenance",
            name="System Maintenance Orchestrator",
            description="Comprehensive system maintenance: healthcheck → align → optimize → healthcheck",
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
            context: Operation context (unused, for interface compatibility)
            
        Returns:
            OperationResult with maintenance metrics and report
        """
        start_time = datetime.now()
        logger.info("🔧 Starting comprehensive system maintenance")
        
        try:
            # Phase 1: Pre-maintenance healthcheck
            yield_progress(1, 4, "Phase 1: Pre-maintenance healthcheck")
            pre_check = self._run_pre_healthcheck()
            self.metrics['healthcheck_pre'] = pre_check
            self.metrics['phases_completed'] = 1
            
            if not pre_check.get('overall_health', {}).get('is_healthy'):
                logger.warning("⚠️  Pre-healthcheck identified issues - proceeding with maintenance")
            
            # Phase 2: System alignment
            yield_progress(2, 4, "Phase 2: System alignment")
            alignment = self._run_alignment()
            self.metrics['alignment'] = alignment
            self.metrics['phases_completed'] = 2
            
            # Only optimize if alignment succeeded
            if alignment.get('success'):
                # Phase 3: CORTEX optimization
                yield_progress(3, 4, "Phase 3: CORTEX optimization")
                optimization = self._run_optimization()
                self.metrics['optimization'] = optimization
                self.metrics['phases_completed'] = 3
            else:
                logger.warning("⚠️  Skipping optimization - alignment had issues")
                self.metrics['warnings'].append("Optimization skipped due to alignment issues")
            
            # Phase 4: Post-maintenance healthcheck
            yield_progress(4, 4, "Phase 4: Post-maintenance healthcheck")
            post_check = self._run_post_healthcheck()
            self.metrics['healthcheck_post'] = post_check
            self.metrics['phases_completed'] = 4
            
            # Generate report
            report = self._generate_report(start_time)
            
            # Save report
            report_path = self._save_report(report)
            
            success = self.metrics['phases_completed'] == 4
            
            return OperationResult(
                success=success,
                status=OperationStatus.SUCCESS if success else OperationStatus.WARNING,
                message=f"System maintenance completed: {self.metrics['phases_completed']}/4 phases",
                data={
                    'phases_completed': self.metrics['phases_completed'],
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
                message=f"Maintenance failed at phase {self.metrics['phases_completed']}/4: {str(e)}",
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
    
    def _generate_report(self, start_time: datetime) -> Dict[str, Any]:
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
                'optimization': self._summarize_optimization(self.metrics['optimization']),
                'post_healthcheck': self._summarize_healthcheck(self.metrics['healthcheck_post'])
            },
            'improvements': self.metrics['improvements'],
            'warnings': self.metrics['warnings'],
            'errors': self.metrics['errors']
        }
        
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
    
    def _summarize_optimization(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize optimization results."""
        if not data:
            return {'status': 'skipped'}
        
        return {
            'status': 'success' if data.get('success') else 'failed',
            'optimizations_applied': data.get('optimizations_applied', 0),
            'performance_gain': data.get('performance_gain', '0%')
        }
    
    def _save_report(self, report: Dict[str, Any]) -> Path:
        """Save maintenance report to file."""
        reports_dir = self.project_root / 'cortex-brain' / 'documents' / 'reports'
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        report_path = reports_dir / f'system-maintenance-{timestamp}.json'
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📄 Report saved: {report_path}")
        return report_path
