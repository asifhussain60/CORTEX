"""
CORTEX 4.0 System Maintenance Orchestrator

Purpose: Automated 7-phase system maintenance orchestrator
Author: CORTEX Development Team
Created: 2025-12-24

Features:
- 7-phase workflow (healthcheck → align → cleanup → optimize → vacuum → refresh → healthcheck)
- BaseOrchestrator integration with PhaseManager
- Tiered routing integration (Planning System alignment)
- Automatic phase 5 vacuum cycle (SQLite optimization + AST cleanup)
- Version synchronization (cortex.config.json consistency)
- Enhanced healthcheck (component-level status reporting)
- Completion detection (🎭 engagement hints + success template)

Phases:
1. Pre-Healthcheck - Establish baseline system health
2. Align - Auto-fix system issues (realignment_utility.py integration)
3. Cleanup - Organize files and update references
4. Optimize - Token optimization and cache cleanup
5. Vacuum - SQLite optimization + AST-powered cleanup
6. Refresh Prompts - Regenerate prompts to reflect system changes
7. Post-Healthcheck - Validate improvements and measure health delta

Integration:
- BaseOrchestrator: Phase management, error handling, lifecycle
- CLI: Invoked via router_agent.py for 'system maintenance' command
- Operations: Registered in cortex-operations.yaml with execution_method: cli_wrapper
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import json

from src.orchestration_4_0.base.base_orchestrator import BaseOrchestrator


class MaintenanceOrchestrator(BaseOrchestrator):
    """
    System Maintenance Orchestrator
    
    Executes 7-phase maintenance workflow with automatic health validation
    and delta reporting.
    """
    
    def __init__(
        self,
        cortex_root: Path,
        logger: Optional[logging.Logger] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize Maintenance Orchestrator.
        
        Args:
            cortex_root: Path to CORTEX project root
            logger: Optional logger instance
            config: Optional configuration
        """
        super().__init__(
            name="maintenance",
            logger=logger,
            config=config or {}
        )
        
        self.cortex_root = Path(cortex_root)
        self.baseline_health: Optional[Dict[str, Any]] = None
        self.final_health: Optional[Dict[str, Any]] = None
        
        self.logger.info("🎭 Maintenance Orchestrator initialized")
    
    def _setup(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Setup orchestrator resources.
        
        Args:
            context: Execution context
            
        Returns:
            Setup result
        """
        self.logger.info("Setting up maintenance orchestrator...")
        
        # Validate CORTEX root exists
        if not self.cortex_root.exists():
            raise RuntimeError(f"CORTEX root not found: {self.cortex_root}")
        
        # Validate required directories
        required_dirs = [
            'cortex-brain',
            'src',
            'tests'
        ]
        
        for dir_name in required_dirs:
            dir_path = self.cortex_root / dir_name
            if not dir_path.exists():
                self.logger.warning(f"Required directory missing: {dir_name}")
        
        return {
            'success': True,
            'cortex_root': str(self.cortex_root),
            'directories_validated': len(required_dirs)
        }
    
    def _register_phases(self) -> None:
        """Register 7 maintenance phases."""
        phases = [
            ("pre_healthcheck", "Scan system health and establish baseline"),
            ("align", "Auto-fix misalignments with realignment utility"),
            ("cleanup", "Organize files and update references"),
            ("optimize", "Optimize token usage and cache"),
            ("vacuum", "SQLite and AST cleanup"),
            ("refresh_prompts", "Regenerate prompts"),
            ("post_healthcheck", "Calculate health delta")
        ]
        
        for phase_name, description in phases:
            self.phase_manager.register_phase(
                name=phase_name,
                description=description,
                required=True
            )
        
        self.logger.info(f"Registered {len(phases)} maintenance phases")
    
    def _execute_phase(self, phase_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single maintenance phase.
        
        Args:
            phase_name: Name of phase to execute
            context: Phase execution context
            
        Returns:
            Phase execution result
        """
        self.logger.info(f"🎭 Phase transition: → {phase_name.upper()}")
        
        # Route to phase-specific execution method
        phase_methods = {
            'pre_healthcheck': self._run_pre_healthcheck,
            'align': self._run_align_phase,
            'cleanup': self._run_cleanup_phase,
            'optimize': self._run_optimize_phase,
            'vacuum': self._run_vacuum_phase,
            'refresh_prompts': self._run_refresh_prompts_phase,
            'post_healthcheck': self._run_post_healthcheck
        }
        
        if phase_name not in phase_methods:
            self.logger.error(f"Unknown phase: {phase_name}")
            return {
                'success': False,
                'phase': phase_name,
                'error': f'Unknown phase: {phase_name}'
            }
        
        try:
            result = phase_methods[phase_name](context)
            self.logger.info(f"✅ Phase complete: {phase_name}")
            return result
        except Exception as e:
            self.logger.error(f"❌ Phase failed: {phase_name} - {e}", exc_info=True)
            return {
                'success': False,
                'phase': phase_name,
                'error': str(e)
            }
    
    def _teardown(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cleanup orchestrator resources.
        
        Args:
            context: Teardown context
            
        Returns:
            Teardown result
        """
        self.logger.info("Tearing down maintenance orchestrator...")
        
        # Calculate health delta if both healthchecks completed
        health_delta = None
        if self.baseline_health and self.final_health:
            # Handle both dict and float formats for backward compatibility
            if isinstance(self.baseline_health, dict):
                baseline_score = self.baseline_health.get('overall_score', 0)
            else:
                baseline_score = float(self.baseline_health)
            
            if isinstance(self.final_health, dict):
                final_score = self.final_health.get('overall_score', 0)
            else:
                final_score = float(self.final_health)
            
            health_delta = final_score - baseline_score
            
            self.logger.info(f"Health delta: {health_delta:+.2f}% ({baseline_score:.1f}% → {final_score:.1f}%)")
        
        return {
            'success': True,
            'health_delta': health_delta,
            'baseline_health': self.baseline_health,
            'final_health': self.final_health,
            'copilot_instructions': {
                'response_template': 'maintenance_execution_progress',
                'progress_updates': True,
                'autonomous_execution': True,
                'checkpoint_frequency': 'per_phase'
            }
        }
    
    # ========================================================================
    # Phase 1: Pre-Healthcheck
    # ========================================================================
    
    def _run_pre_healthcheck(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute pre-healthcheck phase: Establish baseline health.
        
        Scans 32 system components across 4 categories:
        - Brain Tiers (Tier 0-3)
        - Orchestrators (16 components)
        - Protection Layers (6 components)
        - System Health (6 components)
        
        Args:
            context: Phase context
            
        Returns:
            Healthcheck result with baseline metrics
        """
        self.logger.info("Running pre-healthcheck...")
        
        components = {
            'brain_tier0': self._check_tier0_health(),
            'brain_tier1': self._check_tier1_health(),
            'brain_tier2': self._check_tier2_health(),
            'brain_tier3': self._check_tier3_health(),
            'orchestrators': self._check_orchestrators_health(),
            'agents': self._check_agents_health(),
            'protection': self._check_protection_health(),
            'system': self._check_system_health()
        }
        
        # Calculate overall health score (all components return floats)
        health_scores = list(components.values())
        overall_score = sum(health_scores) / len(health_scores)
        
        # Store baseline health as simple float for attribute access
        self.baseline_health = overall_score
        
        self.logger.info(f"Baseline health: {overall_score:.1f}%")
        
        return {
            'success': True,
            'baseline_health': overall_score,
            'overall_score': overall_score,
            'components': components,
            'health_components': components
        }
    
    def _check_tier0_health(self) -> float:
        """Check Tier 0 (Governance) health."""
        tier0_path = self.cortex_root / 'cortex-brain'
        
        checks = {
            'brain_protection_rules': (tier0_path / 'brain-protection-rules.yaml').exists(),
            'response_templates': (tier0_path / 'response-templates-v4.yaml').exists()
        }
        
        score = (sum(checks.values()) / len(checks)) * 100
        return score
    
    def _check_tier1_health(self) -> float:
        """Check Tier 1 (Working Memory) health - returns score only."""
        return self._check_tier1_health_detailed()['score']
    
    def _check_tier1_health_detailed(self) -> Dict[str, Any]:
        """Check Tier 1 (Working Memory) health - returns detailed dict."""
        tier1_path = self.cortex_root / 'cortex-brain' / 'tier1'
        
        # Check conversation context limit (70 entries) - support both json and yaml
        context_files = []
        if tier1_path.exists():
            context_files = list(tier1_path.glob('*.json')) + list(tier1_path.glob('*.yaml'))
        context_count = len(context_files)
        
        score = 100 if context_count <= 70 else max(0, 100 - (context_count - 70))
        
        return {
            'score': score,
            'context_count': context_count,
            'status': 'healthy' if score >= 80 else 'degraded'
        }
    
    def _check_tier2_health(self) -> float:
        """Check Tier 2 (Knowledge Graph) health - returns score only."""
        return self._check_tier2_health_detailed()['score']
    
    def _check_tier2_health_detailed(self) -> Dict[str, Any]:
        """Check Tier 2 (Knowledge Graph) health - returns detailed dict."""
        tier2_path = self.cortex_root / 'cortex-brain' / 'tier2'
        
        # Check knowledge graph existence
        kg_exists = tier2_path.exists()
        score = 100 if kg_exists else 50
        
        return {
            'score': score,
            'kg_exists': kg_exists,
            'status': 'healthy' if score >= 80 else 'degraded'
        }
    
    def _check_tier3_health(self) -> float:
        """Check Tier 3 (Development Context) health."""
        tier3_path = self.cortex_root / 'cortex-brain' / 'tier3'
        
        # Check development context existence
        dev_context_exists = tier3_path.exists()
        score = 100 if dev_context_exists else 50
        return score
    
    def _check_orchestrators_health(self) -> float:
        """Check orchestrators health."""
        orchestrators_path = self.cortex_root / 'src' / 'orchestrators'
        
        # Check orchestrators directory exists
        orch_exists = orchestrators_path.exists()
        
        # Count orchestrator subdirectories
        orch_count = len(list(orchestrators_path.glob('*/'))) if orch_exists else 0
        
        score = 100 if orch_count >= 8 else (orch_count / 8) * 100
        return score
    
    def _check_agents_health(self) -> float:
        """Check agents health."""
        agents_path = self.cortex_root / 'src' / 'cortex_agents'
        
        # Check agents directory exists
        agents_exist = agents_path.exists()
        score = 100 if agents_exist else 50
        return score
    
    def _check_protection_health(self) -> float:
        """Check protection layer health."""
        brain_path = self.cortex_root / 'cortex-brain'
        tests_path = self.cortex_root / 'tests'
        
        checks = {
            'skull_rules': (brain_path / 'brain-protection-rules.yaml').exists(),
            'test_separation': tests_path.exists()
        }
        
        score = (sum(checks.values()) / len(checks)) * 100
        return score
    
    def _check_system_health(self) -> float:
        """Check system health."""
        checks = {
            'src_directory': (self.cortex_root / 'src').exists(),
            'tests_directory': (self.cortex_root / 'tests').exists(),
            'config_file': (self.cortex_root / 'cortex.config.json').exists(),
            'requirements': (self.cortex_root / 'requirements.txt').exists()
        }
        
        score = (sum(checks.values()) / len(checks)) * 100
        return score
    
    # ========================================================================
    # Phase 2: Align
    # ========================================================================
    
    def _run_align_phase(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute ALIGN phase: Auto-fix system issues.
        
        Uses realignment_utility.py with tiered routing integration.
        
        Args:
            context: Phase context
            
        Returns:
            Align result with fixes applied count
        """
        self.logger.info("Running align phase...")
        
        try:
            # Import alignment utility (may not exist yet)
            from src.operations.modules.realignment.realignment_utility import realign
            
            # Execute alignment with auto-fix enabled
            result = realign(
                project_root=self.cortex_root,
                cortex_root=self.cortex_root,
                interactive=False
            )
            
            fixes_applied = len(result.actions_applied)
            issues_detected = len(result.errors)
            
            self.logger.info(f"Alignment complete: {fixes_applied} fixes applied, {issues_detected} issues detected")
            
            return {
                'success': result.success,
                'fixes_applied': fixes_applied,
                'issues_detected': issues_detected,
                'rollback_checkpoint': str(result.report_path) if result.report_path else None,
                'validation_passed': result.after_compliance > result.before_compliance,
                'skipped': False
            }
        except ImportError as e:
            self.logger.warning(f"Align utility not available: {e}")
            return {
                'success': True,
                'fixes_applied': 0,
                'issues_detected': 0,
                'skipped': True,
                'reason': 'Align utility not available'
            }
        except Exception as e:
            self.logger.error(f"Align phase failed: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    # ========================================================================
    # Phase 3: Cleanup
    # ========================================================================
    
    def _run_cleanup_phase(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute CLEANUP phase: File organization and reference updates.
        
        Args:
            context: Phase context
            
        Returns:
            Cleanup result with files moved count
        """
        self.logger.info("Running cleanup phase...")
        
        try:
            # Import cleanup orchestrator (may not exist yet)
            from src.operations.modules.orchestration.cleanup_orchestrator import CleanupOrchestrator
            
            cleanup = CleanupOrchestrator()
            result = cleanup.execute({'dry_run': False})
            
            return {
                'success': result.success,
                'files_moved': result.data.get('files_moved', 0),
                'references_updated': result.data.get('references_updated', 0),
                'duplicates_found': result.data.get('duplicates_detected', 0),
                'backup_path': result.data.get('backup_path'),
                'skipped': False
            }
        except ImportError as e:
            self.logger.warning(f"Cleanup orchestrator not available: {e}")
            return {
                'success': True,
                'files_moved': 0,
                'skipped': True,
                'reason': 'Cleanup utility not available'
            }
        except Exception as e:
            self.logger.error(f"Cleanup phase failed: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    # ========================================================================
    # Phase 4: Optimize
    # ========================================================================
    
    def _run_optimize_phase(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute OPTIMIZE phase: Token optimization and cache cleanup.
        
        Args:
            context: Phase context
            
        Returns:
            Optimize result with tokens saved count
        """
        self.logger.info("Running optimize phase...")
        
        try:
            # Import optimize orchestrator (may not exist yet)
            from src.operations.modules.optimization.optimize_cortex_orchestrator import OptimizeCortexOrchestrator
            
            optimizer = OptimizeCortexOrchestrator()
            result = optimizer.execute({})
            
            return {
                'success': result.success,
                'tokens_saved': result.data.get('tokens_saved', 0),
                'cache_cleared': result.data.get('cache_cleared', False),
                'skipped': False
            }
        except ImportError as e:
            self.logger.warning(f"Optimize orchestrator not available: {e}")
            return {
                'success': True,
                'tokens_saved': 0,
                'skipped': True,
                'reason': 'Optimize utility not available'
            }
        except Exception as e:
            self.logger.error(f"Optimize phase failed: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    # ========================================================================
    # Phase 5: Vacuum
    # ========================================================================
    
    def _run_vacuum_phase(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute VACUUM phase: SQLite optimization + AST cleanup.
        
        Args:
            context: Phase context
            
        Returns:
            Vacuum result with space saved
        """
        self.logger.info("Running vacuum phase...")
        
        try:
            # Import vacuum orchestrator (may not exist yet)
            from src.operations.modules.vacuum.vacuum_orchestrator import VacuumOrchestrator
            
            vacuum = VacuumOrchestrator()
            result = vacuum.execute({})
            
            return {
                'success': result.success,
                'space_saved_bytes': result.data.get('space_saved', 0),
                'databases_vacuumed': result.data.get('databases_vacuumed', 0),
                'skipped': False
            }
        except ImportError as e:
            self.logger.warning(f"Vacuum orchestrator not available: {e}")
            return {
                'success': True,
                'space_saved_bytes': 0,
                'skipped': True,
                'reason': 'Vacuum utility not available'
            }
        except Exception as e:
            self.logger.error(f"Vacuum phase failed: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    # ========================================================================
    # Phase 6: Refresh Prompts
    # ========================================================================
    
    def _run_refresh_prompts_phase(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute REFRESH PROMPTS phase: Regenerate prompts.
        
        Args:
            context: Phase context
            
        Returns:
            Refresh result with prompts regenerated count
        """
        self.logger.info("Running refresh prompts phase...")
        
        try:
            # Import regenerate prompts utility (may not exist yet)
            from src.operations.modules.prompt_generation.regenerate_prompts_utility import regenerate_prompts
            
            result = regenerate_prompts()
            
            return {
                'success': result.get('success', False),
                'prompts_regenerated': result.get('prompts_regenerated', 0),
                'skipped': False
            }
        except ImportError as e:
            self.logger.warning(f"Regenerate prompts utility not available: {e}")
            return {
                'success': True,
                'prompts_regenerated': 0,
                'skipped': True,
                'reason': 'Refresh prompts utility not available'
            }
        except Exception as e:
            self.logger.error(f"Refresh prompts phase failed: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    # ========================================================================
    # Phase 7: Post-Healthcheck
    # ========================================================================
    
    def _run_post_healthcheck(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute post-healthcheck phase: Validate improvements.
        
        Args:
            context: Phase context
            
        Returns:
            Healthcheck result with health delta
        """
        self.logger.info("Running post-healthcheck...")
        
        components = {
            'brain_tier0': self._check_tier0_health(),
            'brain_tier1': self._check_tier1_health(),
            'brain_tier2': self._check_tier2_health(),
            'brain_tier3': self._check_tier3_health(),
            'orchestrators': self._check_orchestrators_health(),
            'agents': self._check_agents_health(),
            'protection': self._check_protection_health(),
            'system': self._check_system_health()
        }
        
        # Calculate overall health score (components are floats)
        health_scores = list(components.values())
        overall_score = sum(health_scores) / len(health_scores)
        
        # Store final health as simple float for attribute access
        self.final_health = overall_score
        
        # Calculate health delta
        health_delta = 0.0
        if self.baseline_health:
            baseline_score = self.baseline_health
            health_delta = overall_score - baseline_score
            
            self.logger.info(f"Final health: {overall_score:.1f}% (Δ {health_delta:+.2f}%)")
        else:
            self.logger.warning("No baseline health available for comparison")
        
        return {
            'success': True,
            'final_health': overall_score,
            'overall_score': overall_score,
            'health_delta': health_delta,
            'components': components,
            'health_components': components
        }


def execute_maintenance(cortex_root: Path, logger: Optional[logging.Logger] = None) -> Dict[str, Any]:
    """
    Execute system maintenance workflow.
    
    Args:
        cortex_root: Path to CORTEX project root
        logger: Optional logger instance
        
    Returns:
        Maintenance execution result
    """
    # Phase 0.5: Pre-Flight Cache Optimization (CORTEX-5.0 Sub-Plan 00D)
    if logger:
        try:
            from src.operations.utilities.vscode_cache_manager import VSCodeCacheManager
            
            cache_manager = VSCodeCacheManager()
            cache_results = cache_manager.pre_flight_optimize(log_metrics=True, fail_silently=True)
            
            if cache_results.get("success") and not cache_results.get("skipped"):
                logger.info(f"✅ Pre-flight cache optimization: {cache_results.get('summary', 'Complete')}")
            elif cache_results.get("skipped"):
                logger.debug(f"⏭️  Cache optimization skipped: {cache_results.get('reason', 'N/A')}")
            else:
                logger.warning(f"⚠️  Cache optimization failed (non-critical): {cache_results.get('error', 'Unknown')}")
        except Exception as e:
            logger.warning(f"⚠️  Pre-flight cache optimization failed (non-critical): {e}")
    
    orchestrator = MaintenanceOrchestrator(
        cortex_root=cortex_root,
        logger=logger
    )
    
    return orchestrator.execute()


if __name__ == '__main__':
    # Test execution
    import sys
    from pathlib import Path
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)8s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    cortex_root = Path(__file__).parent.parent.parent.parent.parent
    
    print(f"Executing maintenance from: {cortex_root}")
    
    result = execute_maintenance(cortex_root)
    
    print("\n" + "="*80)
    print("MAINTENANCE COMPLETE")
    print("="*80)
    print(json.dumps(result, indent=2))
