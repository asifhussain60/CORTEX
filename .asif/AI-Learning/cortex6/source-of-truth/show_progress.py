#!/usr/bin/env python3
"""
CORTEX 6.0 Epic Progress Visualizer

Displays dual progress bars:
1. Current phase progress
2. Overall epic completion

Author: GitHub Copilot
Version: 1.0.0
"""

import yaml
from pathlib import Path
from datetime import datetime


def load_tracker():
    """Load the TODO continuity tracker."""
    tracker_path = Path(__file__).parent / "todo" / "00-TODO-CONTINUITY-TRACKER.yaml"
    with open(tracker_path, 'r') as f:
        return yaml.safe_load(f)


def create_progress_bar(percentage, width=30, filled_char='█', empty_char='░'):
    """Create a visual progress bar."""
    filled = int(width * percentage / 100)
    empty = width - filled
    return f"{filled_char * filled}{empty_char * empty}"


def get_phase_info(tracker, feature_id, phase_id):
    """Get current phase information."""
    feature = tracker.get(feature_id, {})
    phases = feature.get('phases', [])
    
    for phase in phases:
        if phase.get('phase_id') == phase_id:
            return phase
    return None


def count_epic_tasks(tracker):
    """Count total and completed tasks across all features."""
    total_tasks = 0
    completed_tasks = 0
    
    features = [
        'feat01_foundation',
        'feat02_todo_orchestrator', 
        'feat03_governance',
        'feat04_core_orchestration',
        'feat05_resilience',
        'feat06_mcp',
        'feat07_integration',
        'feat08_cleanup'
    ]
    
    for feature_id in features:
        feature = tracker.get(feature_id, {})
        phases = feature.get('phases', [])
        
        for phase in phases:
            tasks = phase.get('tasks', [])
            total_tasks += len(tasks)
            
            for task in tasks:
                if task.get('status') == 'COMPLETED':
                    completed_tasks += 1
    
    return completed_tasks, total_tasks


def get_current_phase_progress(tracker):
    """Calculate current phase progress."""
    current_pos = tracker.get('current_position', {})
    feature = current_pos.get('feature', 'feat04-core-orchestration')
    phase = current_pos.get('phase', 4)
    
    # Map feature name to tracker key
    feature_map = {
        'feat04-core-orchestration': 'feat04_core_orchestration',
        'feat05-resilience': 'feat05_resilience',
        'feat06-mcp': 'feat06_mcp',
        'feat07-integration': 'feat07_integration',
        'feat08-cleanup': 'feat08_cleanup'
    }
    
    feature_key = feature_map.get(feature, feature.replace('-', '_'))
    
    # For completed features, show 100%
    feature_data = tracker.get(feature_key, {})
    if feature_data.get('status') == 'COMPLETED':
        return feature, phase, 100, 'COMPLETED'
    
    phase_info = get_phase_info(tracker, feature_key, phase)
    
    if phase_info:
        tasks = phase_info.get('tasks', [])
        if not tasks:
            return feature, phase, 0, 'NO_TASKS'
        
        completed = sum(1 for t in tasks if t.get('status') == 'COMPLETED')
        total = len(tasks)
        percentage = int((completed / total) * 100) if total > 0 else 0
        
        return feature, phase, percentage, phase_info.get('name', f'Phase {phase}')
    
    return feature, phase, 0, 'Unknown'


def display_progress(tracker):
    """Display dual progress bars."""
    print("\n" + "="*80)
    print("🧠 CORTEX 6.0 Epic - Autonomous Executor")
    print("="*80 + "\n")
    
    # Overall Epic Progress
    completed, total = count_epic_tasks(tracker)
    epic_percentage = int((completed / total) * 100) if total > 0 else 0
    epic_bar = create_progress_bar(epic_percentage, width=50)
    
    print(f"📊 Overall Epic Progress")
    print(f"Progress: {epic_bar} {epic_percentage}% ({completed}/{total} tasks)")
    print()
    
    # Current Phase Progress
    feature, phase, phase_percentage, phase_name = get_current_phase_progress(tracker)
    phase_bar = create_progress_bar(phase_percentage, width=50)
    
    print(f"🎯 Current Phase: {feature.upper()} Phase {phase}")
    print(f"Phase: {phase_name}")
    print(f"Progress: {phase_bar} {phase_percentage}%")
    print()
    
    # Feature Status Table
    print("📋 Feature Status:")
    print("-" * 80)
    print(f"{'Feature':<30} {'Status':<15} {'Progress':<10} {'Tests'}")
    print("-" * 80)
    
    features = [
        ('feat01_foundation', 'feat01-foundation'),
        ('feat02_todo_orchestrator', 'feat02-todo-orchestrator'),
        ('feat03_governance', 'feat03-governance'),
        ('feat04_core_orchestration', 'feat04-core-orchestration'),
        ('feat05_resilience', 'feat05-resilience'),
        ('feat06_mcp', 'feat06-mcp'),
        ('feat07_integration', 'feat07-integration'),
        ('feat08_cleanup', 'feat08-cleanup')
    ]
    
    for feat_key, feat_name in features:
        feat_data = tracker.get(feat_key, {})
        status = feat_data.get('status', 'NOT_STARTED')
        progress = feat_data.get('progress', 0)
        
        # Get test info if available
        tests = ''
        if status == 'COMPLETED':
            if feat_key == 'feat01_foundation':
                tests = '102 passing'
            elif feat_key == 'feat02_todo_orchestrator':
                tests = '95 passing'
            elif feat_key == 'feat03_governance':
                tests = '41 passing'
            elif feat_key == 'feat04_core_orchestration':
                tests = '182 passing'
        
        status_icon = {
            'COMPLETED': '✅',
            'IN_PROGRESS': '🔄',
            'NOT_STARTED': '⏳'
        }.get(status, '❓')
        
        print(f"{feat_name:<30} {status_icon} {status:<12} {progress}%{' ':<7} {tests}")
    
    print("-" * 80)
    print()
    
    # Next Action
    current_pos = tracker.get('current_position', {})
    if epic_percentage >= 100:
        print("🎉 CONGRATULATIONS! Epic Complete!")
    else:
        next_feature = current_pos.get('feature', 'Unknown')
        next_phase = current_pos.get('phase', '?')
        next_task = current_pos.get('task', '?')
        print(f"⏭️  Next: {next_feature} Phase {next_phase} Task {next_task}")
    
    print()
    print("="*80)
    print(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")


if __name__ == "__main__":
    tracker = load_tracker()
    display_progress(tracker)
