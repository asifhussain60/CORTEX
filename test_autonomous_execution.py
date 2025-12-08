"""
Test autonomous execution with progress templates
"""
import sys
import os
from pathlib import Path

# Set UTF-8 encoding for Windows console
if os.name == 'nt':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.orchestrators.planning_orchestrator import PlanningOrchestrator

def test_autonomous_execution():
    """Test autonomous execution with progress template rendering."""
    try:
        # First, check both approved and completed directories
        from pathlib import Path
        approved_path = Path('cortex-brain/documents/planning/approved/PLAN-2025-12-08-progress-template-test.yaml')
        completed_path = Path('cortex-brain/documents/planning/completed/PLAN-2025-12-08-progress-template-test.yaml')
        
        # Move from completed to approved if needed
        if completed_path.exists() and not approved_path.exists():
            print(f'Moving plan from completed to approved...')
            approved_path.parent.mkdir(parents=True, exist_ok=True)
            import shutil
            shutil.move(str(completed_path), str(approved_path))
        
        orchestrator = PlanningOrchestrator(cortex_root='D:/PROJECTS/CORTEX')
        print('\n' + '='*80)
        print('AUTONOMOUS EXECUTION TEST - Progress Template Integration')
        print('='*80 + '\n')
        
        print('Loading plan...')
        result = orchestrator.execute_plan_autonomously('PLAN-2025-12-08-template-test.yaml')
        
        print('\n' + '='*80)
        print('EXECUTION COMPLETE')
        print('='*80)
        print(f'\n✅ Success: {result.get("success")}')
        print(f'📝 Message: {result.get("message", "No message")}')
        print(f'📊 Total Phases: {result.get("total_phases")}')
        print(f'✅ Tasks Completed: {result.get("completed_tasks")}/{result.get("total_tasks")}')
        
        if result.get('rendered_output'):
            print('\n' + '-'*80)
            print('FINAL RENDERED OUTPUT')
            print('-'*80)
            print(result['rendered_output'])
        
        return 0 if result.get('success') else 1
        
    except Exception as e:
        print(f'\n❌ Error: {e}')
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(test_autonomous_execution())
