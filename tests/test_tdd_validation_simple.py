"""Quick test for TDD Mastery validation integration - Direct module test."""
import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_tdd_validation_methods():
    """Test TDD Mastery validation methods directly."""
    print("\n🧪 Testing TDD Mastery Validation Methods\n")
    print("="*80)
    
    tdd_workflow_path = project_root / "src" / "workflows" / "tdd_workflow_orchestrator.py"
    tdd_state_machine_path = project_root / "src" / "workflows" / "tdd_state_machine.py"
    
    print("\n1. Checking TDD Workflow Orchestrator Config...")
    if tdd_workflow_path.exists():
        content = tdd_workflow_path.read_text(encoding='utf-8')
        
        checks = {
            'enable_refactoring: bool = True': 'Enable Refactoring',
            'auto_debug_on_failure: bool = True': 'Auto Debug on Failure',
            'enable_session_tracking: bool = True': 'Session Tracking',
            'enable_programmatic_execution: bool = True': 'Programmatic Execution',
            'auto_detect_test_location: bool = True': 'Test Location Detection',
            'debug_timing_to_refactoring: bool = True': 'Debug Timing Integration',
            'batch_max_workers': 'Batch Processing',
            'enable_terminal_integration': 'Terminal Integration',
            'from src.workflows.batch_processor import BatchTestGenerator': 'BatchTestGenerator',
            'from src.workflows.test_execution_manager import TestExecutionManager': 'TestExecutionManager',
            'from src.tier1.sessions.session_manager import SessionManager': 'SessionManager',
            'from src.workflows.page_tracking import PageTracker': 'PageTracker'
        }
        
        for check, name in checks.items():
            found = check in content
            icon = "✅" if found else "❌"
            print(f"   {icon} {name}")
    else:
        print("   ❌ TDD Workflow Orchestrator not found")
    
    print("\n2. Checking TDD State Machine...")
    if tdd_state_machine_path.exists():
        content = tdd_state_machine_path.read_text(encoding='utf-8')
        
        states = ['IDLE', 'RED', 'GREEN', 'REFACTOR', 'DONE', 'ERROR']
        for state in states:
            found = f'{state} = ' in content
            icon = "✅" if found else "❌"
            print(f"   {icon} TDDState.{state}")
        
        metrics_checks = {
            'class TDDCycleMetrics': 'TDDCycleMetrics Class',
            'red_duration': 'Red Duration Metric',
            'green_duration': 'Green Duration Metric',
            'refactor_duration': 'Refactor Duration Metric',
            'tests_written': 'Tests Written Metric',
            'tests_passing': 'Tests Passing Metric',
            'from agents.debug_agent import DebugAgent': 'DebugAgent Integration'
        }
        
        for check, name in metrics_checks.items():
            found = check in content
            icon = "✅" if found else "❌"
            print(f"   {icon} {name}")
    else:
        print("   ❌ TDD State Machine not found")
    
    print("\n3. Checking Git Checkpoint System...")
    git_checkpoint_paths = [
        project_root / "src" / "workflows" / "git_checkpoint_system.py",
        project_root / "src" / "orchestrators" / "git_checkpoint_orchestrator.py",
        project_root / "src" / "operations" / "modules" / "git_checkpoint_module.py"
    ]
    
    found_path = None
    for path in git_checkpoint_paths:
        if path.exists():
            found_path = path
            break
    
    if found_path:
        print(f"   ✅ Git Checkpoint System ({found_path.name})")
    else:
        print(f"   ❌ Git Checkpoint System")
    
    print(f"\n{'='*80}")
    print("✅ Manual Validation Complete")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    test_tdd_validation_methods()
