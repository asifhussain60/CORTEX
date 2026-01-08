#!/usr/bin/env python3
"""
CORTEX 6.0 Build Epic - Autonomous Executor
============================================
Executes the CORTEX 6.0 Build Epic autonomously by reading the TODO tracker
and executing tasks with TDD enforcement, audit logging, and self-healing.

Author: Asif Hussain
Version: 1.0.0
Created: 2026-01-08
"""

import sys
import yaml
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

# Add src to path for imports
REPO_ROOT = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from orchestrators.audit_logger import get_audit_logger, AuditCategory, AuditLevel


class EpicExecutor:
    """Autonomous executor for CORTEX 6.0 Build Epic"""
    
    def __init__(self, tracker_path: Path):
        self.tracker_path = tracker_path
        self.source_of_truth_dir = tracker_path.parent.parent
        self.repo_root = REPO_ROOT
        self.logger = get_audit_logger()
        self.tracker_data: Dict[str, Any] = {}
        self.current_position: Dict[str, Any] = {}
        
    def load_tracker(self) -> bool:
        """Load TODO tracker YAML"""
        try:
            with open(self.tracker_path, 'r') as f:
                self.tracker_data = yaml.safe_load(f)
            self.current_position = self.tracker_data.get('current_position', {})
            
            self.logger.info(
                category=AuditCategory.EXECUTION,
                component='epic_executor',
                operation='load_tracker',
                message=f"Loaded tracker: {self.tracker_path}",
                context={
                    'feature': self.current_position.get('feature'),
                    'phase': self.current_position.get('phase'),
                    'task': self.current_position.get('task'),
                    'status': self.current_position.get('status'),
                    'completed_count': self.current_position.get('completed_count', 0)
                },
                correlation_id='EPIC-EXECUTOR'
            )
            return True
            
        except Exception as e:
            self.logger.error(
                category=AuditCategory.EXECUTION,
                component='epic_executor',
                operation='load_tracker',
                message=f"Failed to load tracker: {e}",
                correlation_id='EPIC-EXECUTOR'
            )
            return False
    
    def find_next_task(self) -> Optional[Dict[str, Any]]:
        """Find next NOT_STARTED or IN_PROGRESS task"""
        feature_id = self.current_position.get('feature')
        phase_id = self.current_position.get('phase')
        task_id = self.current_position.get('task')
        status = self.current_position.get('status')
        
        # If current task is IN_PROGRESS, continue it
        if status == 'IN_PROGRESS':
            return self._get_task_definition(feature_id, phase_id, task_id)
        
        # Find next NOT_STARTED task
        feature_data = self.tracker_data.get(feature_id)
        if not feature_data:
            self.logger.warning(
                category=AuditCategory.EXECUTION,
                component='epic_executor',
                operation='find_next_task',
                message=f"Feature not found: {feature_id}",
                correlation_id='EPIC-EXECUTOR'
            )
            return None
        
        phases = feature_data.get('phases', [])
        for phase in phases:
            if phase.get('phase_id') != phase_id:
                continue
                
            tasks = phase.get('tasks', [])
            for task in tasks:
                if task.get('status') == 'NOT_STARTED':
                    return task
        
        return None
    
    def _get_task_definition(self, feature_id: str, phase_id: int, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task definition from tracker"""
        feature_data = self.tracker_data.get(feature_id)
        if not feature_data:
            return None
        
        phases = feature_data.get('phases', [])
        for phase in phases:
            if phase.get('phase_id') == phase_id:
                tasks = phase.get('tasks', [])
                for task in tasks:
                    if task.get('task_id') == task_id:
                        return task
        return None
    
    def execute_task(self, task: Dict[str, Any]) -> bool:
        """Execute a single task with TDD and audit logging"""
        task_id = task.get('task_id')
        task_name = task.get('name')
        tdd_required = task.get('tdd_required', False)
        
        self.logger.info(
            category=AuditCategory.EXECUTION,
            component='epic_executor',
            operation='execute_task',
            message=f"Starting task: {task_id} - {task_name}",
            context={
                'task_id': task_id,
                'tdd_required': tdd_required,
                'estimated_minutes': task.get('estimated_minutes')
            },
            correlation_id=f"EPIC-{task_id}"
        )
        
        # Update task status to IN_PROGRESS
        self._update_task_status(task_id, 'IN_PROGRESS')
        
        try:
            # Execute based on task definition
            if tdd_required:
                success = self._execute_with_tdd(task)
            else:
                success = self._execute_direct(task)
            
            if success:
                self._update_task_status(task_id, 'COMPLETED')
                self._update_current_position_after_completion(task_id)
                return True
            else:
                self._update_task_status(task_id, 'FAILED')
                return False
                
        except Exception as e:
            self.logger.error(
                category=AuditCategory.EXECUTION,
                component='epic_executor',
                operation='execute_task',
                message=f"Task execution failed: {e}",
                context={'task_id': task_id},
                correlation_id=f"EPIC-{task_id}"
            )
            self._update_task_status(task_id, 'FAILED')
            return False
    
    def _execute_with_tdd(self, task: Dict[str, Any]) -> bool:
        """Execute task with RED-GREEN-REFACTOR TDD cycle"""
        task_id = task.get('task_id')
        
        # RED: Write failing test
        print(f"\n🔴 RED: Writing failing test for {task_id}...")
        test_file = task.get('test', {}).get('path')
        if not test_file:
            print(f"⚠️  No test file specified for {task_id}, skipping TDD")
            return self._execute_direct(task)
        
        # Check if test exists and fails
        if not self._run_tests(test_file, should_fail=True):
            print(f"❌ Test did not fail as expected")
            return False
        
        # GREEN: Implement minimal code
        print(f"\n🟢 GREEN: Implementing minimal code for {task_id}...")
        deliverable = task.get('deliverable')
        if deliverable:
            # Implementation would happen here
            # For now, we'll assume GitHub Copilot has done the implementation
            pass
        
        # Verify tests pass
        if not self._run_tests(test_file, should_fail=False):
            print(f"❌ Tests did not pass after implementation")
            return False
        
        # REFACTOR: Clean up
        print(f"\n🔵 REFACTOR: Cleaning up code for {task_id}...")
        # Refactoring logic would go here
        
        return True
    
    def _execute_direct(self, task: Dict[str, Any]) -> bool:
        """Execute task without TDD (design, documentation, etc.)"""
        task_id = task.get('task_id')
        deliverable = task.get('deliverable')
        
        print(f"\n⚙️  Executing {task_id}: {task.get('name')}")
        
        # For now, we'll prompt for manual completion
        print(f"📋 Deliverable: {deliverable}")
        print(f"⏱️  Estimated: {task.get('estimated_minutes')} minutes")
        
        response = input(f"\n✅ Task completed? (y/n): ")
        return response.lower() == 'y'
    
    def _run_tests(self, test_file: str, should_fail: bool = False) -> bool:
        """Run pytest on test file"""
        try:
            result = subprocess.run(
                ['pytest', test_file, '-v'],
                capture_output=True,
                text=True,
                cwd=self.repo_root
            )
            
            if should_fail:
                return result.returncode != 0
            else:
                return result.returncode == 0
                
        except Exception as e:
            print(f"❌ Test execution failed: {e}")
            return False
    
    def _update_task_status(self, task_id: str, status: str):
        """Update task status in tracker"""
        # This would update the YAML file
        # For now, just log it
        self.logger.info(
            category=AuditCategory.STATE_MANAGEMENT,
            component='epic_executor',
            operation='update_task_status',
            message=f"Task {task_id} status: {status}",
            context={'task_id': task_id, 'status': status},
            correlation_id=f"EPIC-{task_id}"
        )
    
    def _update_current_position_after_completion(self, task_id: str):
        """Update current_position after task completion"""
        self.current_position['last_completed'] = task_id
        self.current_position['completed_count'] = self.current_position.get('completed_count', 0) + 1
        self.current_position['status'] = 'COMPLETED'
        
        # Save updated tracker
        # For now, just log
        self.logger.info(
            category=AuditCategory.STATE_MANAGEMENT,
            component='epic_executor',
            operation='update_position',
            message=f"Updated position after {task_id}",
            context={'completed_count': self.current_position['completed_count']},
            correlation_id='EPIC-EXECUTOR'
        )
    
    def run(self, max_tasks: int = 1, auto_mode: bool = False):
        """
        Run the epic executor
        
        Args:
            max_tasks: Maximum number of tasks to execute (0 = unlimited)
            auto_mode: If True, execute without user prompts
        """
        print("\n" + "="*80)
        print("🚀 CORTEX 6.0 Build Epic - Autonomous Executor")
        print("="*80)
        
        if not self.load_tracker():
            print("❌ Failed to load tracker")
            return False
        
        print(f"\n📍 Current Position:")
        print(f"   Feature: {self.current_position.get('feature')}")
        print(f"   Phase: {self.current_position.get('phase')}")
        print(f"   Task: {self.current_position.get('task')}")
        print(f"   Status: {self.current_position.get('status')}")
        print(f"   Completed: {self.current_position.get('completed_count', 0)} tasks")
        
        tasks_executed = 0
        while max_tasks == 0 or tasks_executed < max_tasks:
            next_task = self.find_next_task()
            
            if not next_task:
                print("\n✅ No more tasks to execute")
                break
            
            print(f"\n{'='*80}")
            print(f"📋 Next Task: {next_task.get('task_id')} - {next_task.get('name')}")
            print(f"{'='*80}")
            
            if not auto_mode:
                response = input("\n▶️  Execute this task? (y/n/q): ")
                if response.lower() == 'q':
                    print("\n⏸️  Execution paused")
                    break
                elif response.lower() != 'y':
                    continue
            
            if self.execute_task(next_task):
                tasks_executed += 1
                print(f"\n✅ Task completed ({tasks_executed}/{max_tasks if max_tasks > 0 else '∞'})")
            else:
                print(f"\n❌ Task failed, stopping execution")
                break
        
        print(f"\n{'='*80}")
        print(f"🎉 Execution Summary:")
        print(f"   Tasks executed: {tasks_executed}")
        print(f"   Total completed: {self.current_position.get('completed_count', 0)}")
        print(f"{'='*80}\n")
        
        return True


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='CORTEX 6.0 Build Epic Autonomous Executor')
    parser.add_argument('--tasks', type=int, default=1, help='Number of tasks to execute (0 = unlimited)')
    parser.add_argument('--auto', action='store_true', help='Autonomous mode (no prompts)')
    parser.add_argument('--tracker', type=str, help='Path to tracker YAML')
    
    args = parser.parse_args()
    
    # Default tracker path
    if args.tracker:
        tracker_path = Path(args.tracker)
    else:
        tracker_path = Path(__file__).parent / 'todo' / '00-TODO-CONTINUITY-TRACKER.yaml'
    
    if not tracker_path.exists():
        print(f"❌ Tracker not found: {tracker_path}")
        return 1
    
    executor = EpicExecutor(tracker_path)
    success = executor.run(max_tasks=args.tasks, auto_mode=args.auto)
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
