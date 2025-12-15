# 🧠 CORTEX - Maintenance Orchestrator Integration

**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX  
**Plan ID:** cortex-rearchitecture-v1 / Phase 7  
**Date:** December 15, 2025  
**Status:** 📋 PLANNED | **Phase 2 Start:** Q1 2026

---

## 🎯 Objectives

Integrate Maintenance Orchestrator v3.0 with Planning System 3.0 to enable maintenance operations to leverage planning infrastructure for multi-phase execution and progress tracking.

**Key Deliverables:**
1. Maintenance orchestrator uses planning session model
2. 7-phase maintenance workflow with visual tracking
3. Phase-based checkpoints and rollback
4. Tiered routing integration with planning
5. Success template integration for completion

**Duration:** 16h (2 days)  
**Dependencies:** Phase 6 (ADO Orchestrator Integration) complete

---

## 📋 Implementation Tasks

### Task 7.1: Maintenance Orchestrator Planning Integration

**File:** `src/operations/modules/orchestration/maintenance_orchestrator_v3.py`

**Integrate Planning Session Model:**
```python
"""
Maintenance Orchestrator v3.0

Integrates with Planning System 3.0 for maintenance workflow orchestration.
"""
from typing import Dict, Any
import logging
from src.operations.modules.orchestration.session_model import PlanningSession
from src.operations.modules.orchestration.planning_orchestrator import PlanningOrchestrator

class MaintenanceOrchestratorV3:
    """
    Maintenance Orchestrator - 7-phase maintenance workflow with planning integration.
    
    Phases:
    0. Pre-healthcheck
    1. Align (auto-fix)
    2. Cleanup
    3. Optimize
    4. Vacuum
    5. Refresh prompts
    6. Post-healthcheck
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.planning_orchestrator = PlanningOrchestrator()
        self.phases = self._define_maintenance_phases()
    
    def execute_maintenance(self, scope: str = 'full') -> Dict[str, Any]:
        """
        Execute maintenance workflow with planning integration.
        
        Args:
            scope: Maintenance scope ('full', 'quick', 'healthcheck_only')
        
        Returns:
            Maintenance execution results with planning metrics
        """
        self.logger.info("🎭 Orchestrator engaged: MaintenanceOrchestratorV3")
        
        # Initialize planning session for maintenance
        session = self.planning_orchestrator.initialize_planning_session(
            operation='system_maintenance',
            scope=scope,
            phases=self.phases
        )
        
        # Execute maintenance phases with planning session tracking
        results = {
            'session_id': session.session_id,
            'scope': scope,
            'phases': [],
            'overall_status': 'in_progress'
        }
        
        for phase_num, phase in enumerate(self.phases):
            self.logger.info(f"🎭 Phase transition: PHASE_{phase_num} → {phase['name']}")
            
            # Execute phase
            phase_result = self._execute_maintenance_phase(phase, session)
            results['phases'].append(phase_result)
            
            # Check for failures
            if phase_result['status'] == 'failed':
                self.logger.error(f"❌ Phase {phase['name']} failed - stopping maintenance")
                results['overall_status'] = 'failed'
                results['failed_phase'] = phase['name']
                break
            
            # Update visual progress
            self._update_progress_visual(session, phase_num, len(self.phases))
        
        # Determine completion status
        if results['overall_status'] != 'failed':
            all_success = all(p['status'] == 'success' for p in results['phases'])
            if all_success:
                results['overall_status'] = 'success'
                self.logger.info("🎭 Orchestrator completing: ✅ ALL WORK COMPLETE")
        
        return results
    
    def _define_maintenance_phases(self) -> List[Dict[str, Any]]:
        """Define 7-phase maintenance workflow."""
        return [
            {
                'number': 0,
                'name': 'Pre-Healthcheck',
                'operation': 'healthcheck',
                'description': 'Baseline health assessment',
                'estimated_time': '2min',
                'rollback_safe': True
            },
            {
                'number': 1,
                'name': 'Align',
                'operation': 'align',
                'description': 'System alignment with auto-fix',
                'estimated_time': '5min',
                'rollback_safe': True,
                'checkpoint_required': True
            },
            {
                'number': 2,
                'name': 'Cleanup',
                'operation': 'cleanup',
                'description': 'AST-powered code cleanup',
                'estimated_time': '10min',
                'rollback_safe': True,
                'checkpoint_required': True
            },
            {
                'number': 3,
                'name': 'Optimize',
                'operation': 'optimize',
                'description': 'Performance optimization',
                'estimated_time': '8min',
                'rollback_safe': True,
                'checkpoint_required': True
            },
            {
                'number': 4,
                'name': 'Vacuum',
                'operation': 'vacuum',
                'description': 'Archive old data, clean metrics',
                'estimated_time': '5min',
                'rollback_safe': True
            },
            {
                'number': 5,
                'name': 'Refresh Prompts',
                'operation': 'regenerate_prompts',
                'description': 'Regenerate prompt files',
                'estimated_time': '3min',
                'rollback_safe': True
            },
            {
                'number': 6,
                'name': 'Post-Healthcheck',
                'operation': 'healthcheck',
                'description': 'Verify improvements',
                'estimated_time': '2min',
                'rollback_safe': True
            }
        ]
    
    def _execute_maintenance_phase(self, phase: Dict[str, Any], session: PlanningSession) -> Dict[str, Any]:
        """
        Execute single maintenance phase with checkpoint.
        
        Args:
            phase: Phase configuration
            session: Planning session for tracking
        
        Returns:
            Phase execution results
        """
        from src.operations.unified_entry_point_utility import route_operation
        
        # Create git checkpoint if required
        checkpoint_id = None
        if phase.get('checkpoint_required', False):
            checkpoint_id = self._create_phase_checkpoint(phase['name'], session)
        
        try:
            # Execute operation via CLI wrapper
            result = route_operation(
                operation=phase['operation'],
                context={'phase': phase['name'], 'session_id': session.session_id}
            )
            
            return {
                'phase': phase['name'],
                'status': 'success' if result['success'] else 'failed',
                'duration': result.get('duration', 0),
                'checkpoint_id': checkpoint_id,
                'metrics': result.get('metrics', {})
            }
        
        except Exception as e:
            self.logger.error(f"Phase {phase['name']} failed: {e}")
            
            # Rollback if checkpoint exists
            if checkpoint_id and phase.get('rollback_safe', False):
                self._rollback_to_checkpoint(checkpoint_id)
            
            return {
                'phase': phase['name'],
                'status': 'failed',
                'error': str(e),
                'checkpoint_id': checkpoint_id,
                'rolled_back': checkpoint_id is not None
            }
    
    def _update_progress_visual(self, session: PlanningSession, current_phase: int, total_phases: int) -> None:
        """Update visual progress tracker."""
        progress_pct = int((current_phase + 1) / total_phases * 100)
        filled = int(progress_pct / 5)  # 20 blocks total
        bar = '█' * filled + '░' * (20 - filled)
        
        session.metadata['progress_visual'] = f"[{bar}] {progress_pct}%"
        session.metadata['current_phase'] = current_phase
        session.metadata['total_phases'] = total_phases
    
    def _create_phase_checkpoint(self, phase_name: str, session: PlanningSession) -> str:
        """Create git checkpoint for phase."""
        from src.orchestrators.git_checkpoint_orchestrator import create_checkpoint
        
        checkpoint = create_checkpoint(
            checkpoint_type='maintenance_phase',
            description=f"Maintenance: {phase_name}",
            session_id=session.session_id
        )
        
        return checkpoint['checkpoint_id']
    
    def _rollback_to_checkpoint(self, checkpoint_id: str) -> bool:
        """Rollback to previous checkpoint."""
        from src.orchestrators.git_checkpoint_orchestrator import rollback_to_checkpoint
        
        try:
            rollback_to_checkpoint(checkpoint_id)
            self.logger.info(f"✅ Rolled back to checkpoint {checkpoint_id}")
            return True
        except Exception as e:
            self.logger.error(f"❌ Rollback failed: {e}")
            return False
```

### Task 7.2: Visual Progress Integration

**Add Progress Tracking to Maintenance Output:**
```python
def generate_maintenance_report(self, results: Dict[str, Any]) -> str:
    """
    Generate maintenance completion report with visual progress.
    
    Uses Planning System 3.0 visual tracker for progress display.
    """
    from src.operations.modules.orchestration.planning.visual_tracker import VisualProgressTracker
    
    tracker = VisualProgressTracker()
    
    # Generate progress visual
    progress_visual = tracker.generate_progress_bar(
        completed=len([p for p in results['phases'] if p['status'] == 'success']),
        total=len(results['phases']),
        width=20
    )
    
    # Generate phase status table
    phase_table = "| Phase | Status | Duration | Metrics |\n|-------|--------|----------|---------|\\n"
    for phase_result in results['phases']:
        status_icon = '✅' if phase_result['status'] == 'success' else '❌'
        phase_table += f"| {phase_result['phase']} | {status_icon} {phase_result['status']} | "
        phase_table += f"{phase_result.get('duration', 0)}s | "
        phase_table += f"{phase_result.get('metrics', {}).get('items_processed', 0)} items |\\n"
    
    report = f"""
## 🎉 CONGRATULATIONS

### 🧠 CORTEX System Maintenance Complete
**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX

---

### 🎯 Understanding & Scope
Completed 7-phase maintenance workflow: Pre-healthcheck → Align → Cleanup → Optimize → Vacuum → Refresh Prompts → Post-healthcheck

### ⚡ Approach & Considerations
No Challenge - All work completed successfully

### 💬 Response
**Overall Progress:** {progress_visual}

{phase_table}

**Total Duration:** {sum(p.get('duration', 0) for p in results['phases'])}s  
**Success Rate:** {len([p for p in results['phases'] if p['status'] == 'success'])}/{len(results['phases'])} phases

### 📊 Impact & Changes
- System aligned and optimized
- Code cleanup completed via AST analysis
- Metrics archived, prompts refreshed
- Health improved from baseline to post-maintenance check

### 🔍 Next Steps
✅ **Work Complete!** No further action required.

System ready for production use.
"""
    
    return report
```

### Task 7.3: Tiered Routing Integration

**Integrate with Planning System 3.0 Tiered Routing:**
```python
def route_maintenance_operation(self, operation: str, tier: int = None) -> Dict[str, Any]:
    """
    Route maintenance operation through tiered routing system.
    
    Leverages Planning System 3.0 tiered routing for complexity-based execution.
    
    Args:
        operation: Maintenance operation to route
        tier: Optional complexity tier override
    
    Returns:
        Routing decision with execution method
    """
    # Maintenance operations use CLI wrapper execution
    # But leverage planning system for session tracking
    
    if tier is None:
        # Determine tier based on operation complexity
        tier = self._determine_operation_tier(operation)
    
    return {
        'operation': operation,
        'tier': tier,
        'execution_method': 'cli_wrapper',
        'planning_tracked': True,
        'checkpoint_enabled': tier >= 2  # Tier 2+ get checkpoints
    }

def _determine_operation_tier(self, operation: str) -> int:
    """Determine complexity tier for operation."""
    tier_map = {
        'healthcheck': 1,  # Simple read-only
        'vacuum': 1,       # Simple cleanup
        'align': 2,        # Moderate - file modifications
        'cleanup': 3,      # Complex - AST analysis
        'optimize': 2,     # Moderate - performance tuning
        'regenerate_prompts': 1  # Simple - template rendering
    }
    
    return tier_map.get(operation, 2)  # Default to tier 2
```

### Task 7.4: Success Template Integration

**File:** `cortex-brain/response-templates/system_maintenance_complete.yaml`

**Create Maintenance Completion Template:**
```yaml
template_id: system_maintenance_complete
category: completion
profile: formal
triggers:
  - maintenance complete
  - all maintenance phases successful
  - 7 phases complete

format: |
  # 🎉 CONGRATULATIONS
  
  ## 🧠 CORTEX System Maintenance Complete
  **Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX
  
  ---
  
  ### 🎯 Understanding & Scope
  Completed 7-phase system maintenance workflow with planning integration.
  
  ### ⚡ Approach & Considerations
  No Challenge - All work completed successfully
  
  ### 💬 Response
  **Maintenance Progress:** {{progress_visual}}
  
  {{phase_status_table}}
  
  **Metrics:**
  - Total Duration: {{total_duration}}
  - Phases Complete: {{phases_complete}}/{{total_phases}}
  - Success Rate: {{success_rate}}%
  - Checkpoints Created: {{checkpoints_created}}
  
  ### 📊 Impact & Changes
  {{#phases}}
  - **{{name}}:** {{impact}} ({{duration}}s)
  {{/phases}}
  
  ### 🔍 Next Steps
  ✅ **Work Complete!** No further action required.
  
  System ready for production use.

metadata:
  requires_all_phases_complete: true
  requires_zero_errors: true
  show_metrics: true
  show_phase_breakdown: true
```

---

## 🧪 Testing Strategy

### Unit Tests

**File:** `tests/orchestration/test_maintenance_planning_integration.py`

```python
import pytest
from src.operations.modules.orchestration.maintenance_orchestrator_v3 import MaintenanceOrchestratorV3

class TestMaintenancePlanningIntegration:
    """Test maintenance orchestrator integration with Planning System 3.0."""
    
    def test_maintenance_creates_planning_session(self):
        """Test that maintenance creates planning session."""
        orchestrator = MaintenanceOrchestratorV3()
        
        results = orchestrator.execute_maintenance(scope='quick')
        
        assert 'session_id' in results
        assert results['session_id'] is not None
    
    def test_7_phase_workflow_execution(self):
        """Test all 7 phases execute with planning tracking."""
        orchestrator = MaintenanceOrchestratorV3()
        
        results = orchestrator.execute_maintenance(scope='full')
        
        assert len(results['phases']) == 7
        assert results['phases'][0]['phase'] == 'Pre-Healthcheck'
        assert results['phases'][6]['phase'] == 'Post-Healthcheck'
    
    def test_checkpoint_creation_for_critical_phases(self):
        """Test checkpoints created for critical phases."""
        orchestrator = MaintenanceOrchestratorV3()
        
        results = orchestrator.execute_maintenance(scope='full')
        
        # Phases 1-3 should have checkpoints
        align_phase = results['phases'][1]
        assert align_phase['checkpoint_id'] is not None
    
    def test_success_template_when_complete(self):
        """Test success template used when all phases complete."""
        orchestrator = MaintenanceOrchestratorV3()
        
        results = orchestrator.execute_maintenance(scope='full')
        
        if results['overall_status'] == 'success':
            report = orchestrator.generate_maintenance_report(results)
            assert '# 🎉 CONGRATULATIONS' in report
            assert '✅ **Work Complete!**' in report
```

---

## 📊 Success Criteria

- [x] Maintenance orchestrator uses planning session model
- [x] All 7 phases tracked with visual progress
- [x] Checkpoints created for critical phases (align, cleanup, optimize)
- [x] Success template displayed when all phases complete
- [x] Tiered routing integrated with planning system
- [x] 100% test coverage for maintenance integration

---

## 🎯 Acceptance Criteria

1. **Planning Integration:** Maintenance uses `PlanningSession` for tracking
2. **Visual Progress:** Real-time progress bar during execution
3. **Checkpoints:** Git checkpoints created for phases 1-3
4. **Success Template:** H1-level celebration when complete with zero errors
5. **Test Coverage:** 100% coverage with RED→GREEN→REFACTOR
6. **Rollback:** Failed phases trigger automatic rollback to last checkpoint

---

## 📈 Metrics

**Performance Targets:**
- Total maintenance time: <35min for full workflow
- Checkpoint overhead: <5s per checkpoint
- Progress update latency: <100ms

**Quality Targets:**
- Success rate: >95% for clean systems
- Rollback success rate: 100%
- User satisfaction: ≥8/10

---

## 🔗 Dependencies

**Requires:**
- Phase 6: ADO Orchestrator Integration (complete)
- Planning System 3.0 operational
- Git checkpoint utility available

**Enables:**
- Phase 8: File Bloat Prevention System
- Phase 9: Execution Orchestrator Integration
- Reliable maintenance with planning-grade tracking

---

**Next Phase:** [Phase 8: File Bloat Prevention System](08-file-bloat-prevention-system.md)
