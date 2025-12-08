"""
Test autonomous execution with progress templates
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.orchestrators.planning_orchestrator import PlanningOrchestrator

def test_autonomous_execution():
    """Test autonomous execution with progress template rendering."""
    try:
        orchestrator = PlanningOrchestrator(cortex_root='D:/PROJECTS/CORTEX')
        print('\n' + '='*80)
        print('AUTONOMOUS EXECUTION TEST - Progress Template Integration')
        print('='*80 + '\n')
        
        result = orchestrator.execute_plan_autonomously('PLAN-2025-12-08-progress-template-test.yaml')
        
        print('\n' + '='*80)
        print('EXECUTION COMPLETE')
        print('='*80)
        print(f'\nSuccess: {result.get("success")}')
        print(f'Total Phases: {result.get("total_phases")}')
        print(f'Tasks Completed: {result.get("completed_tasks")}/{result.get("total_tasks")}')
        
        if result.get('rendered_output'):
            print('\n' + '-'*80)
            print('FINAL RENDERED OUTPUT')
            print('-'*80)
            print(result['rendered_output'])
        
        return 0 if result.get('success') else 1
        
    except Exception as e:
        print(f'\n❌ Error: {e}', file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(test_autonomous_execution())
