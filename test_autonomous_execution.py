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
        
        print('Loading plan...')
        result = orchestrator.execute_plan_autonomously('PLAN-2025-12-08-progress-template-test.yaml')
        
        print(f'\nResult type: {type(result)}')
        print(f'Result keys: {result.keys() if isinstance(result, dict) else "not a dict"}')
        print(f'Result: {result}')
        
        print('\n' + '='*80)
        print('EXECUTION COMPLETE')
        print('='*80)
        print(f'\nSuccess: {result.get("success")}')
        print(f'Message: {result.get("message", "No message")}')
        print(f'Total Phases: {result.get("total_phases")}')
        print(f'Tasks Completed: {result.get("completed_tasks")}/{result.get("total_tasks")}')
        
        if result.get('rendered_output'):
            print('\n' + '-'*80)
            print('FINAL RENDERED OUTPUT')
            print('-'*80)
            # Handle unicode by encoding to utf-8
            try:
                print(result['rendered_output'])
            except UnicodeEncodeError:
                print(result['rendered_output'].encode('ascii', 'ignore').decode('ascii'))
        
        return 0 if result.get('success') else 1
        
    except Exception as e:
        print(f'\n❌ Error: {e}')
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(test_autonomous_execution())
