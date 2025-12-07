"""Test autonomous plan execution"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'd:/PROJECTS/CORTEX')
from src.orchestrators.planning_orchestrator import PlanningOrchestrator

orchestrator = PlanningOrchestrator('d:/PROJECTS/CORTEX')
print('🚀 CORTEX Autonomous Execution Starting...')
print('='*70)
print('Plan: Phase 2 Auto-Documentation Generation')
print('='*70 + '\n')

result = orchestrator.execute_plan_autonomously('PLAN-2025-12-06-auto-documentation-generation.yaml')

print('\n' + '='*70)
print('📊 EXECUTION RESULTS')
print('='*70)
print(f"✅ Success: {result.get('success')}")
print(f"📋 Total Phases: {result.get('total_phases')}")
print(f"📝 Total Tasks: {result.get('total_tasks')}")
print(f"✔️  Completed Tasks: {result.get('completed_tasks')}")
print(f"💬 Message: {result.get('message')}")

# Display rendered template output if available
if result.get('rendered_output'):
    print('\n' + '='*70)
    print('🎨 FORMATTED OUTPUT (Response Template)')
    print('='*70)
    print(result['rendered_output'])
elif result.get('execution_log'):
    print('\n📜 Execution Log (last 5 entries):')
    for entry in result['execution_log'][-5:]:
        print(f"  - {entry}")

if result.get('documentation_reminder'):
    print('\n📚 Documentation Reminder:')
    print(result['documentation_reminder'])
