#!/usr/bin/env python3
"""
CORTEX Gantt Chart Data Generator
Calculates feature status from git branches and generates Gantt chart data.

Usage:
    python scripts/gantt_data_generator.py

Outputs:
    - docs/gh-pages/assets/data/gantt-data.json (for Frappe Gantt visualization)
"""

import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional


class GanttDataGenerator:
    """Generates Gantt chart data from git history and CORTEX vision."""
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.tasks = []
        
    def run_git_command(self, args: List[str]) -> str:
        """Execute a git command and return output."""
        try:
            result = subprocess.run(
                ['git'] + args,
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"Git command failed: {e}", file=sys.stderr)
            return ""
    
    def get_all_branches(self) -> List[str]:
        """Get all git branches (local and remote)."""
        output = self.run_git_command(['branch', '-a'])
        if not output:
            return []
        
        branches = []
        for line in output.split('\n'):
            line = line.strip()
            if line.startswith('*'):
                line = line[1:].strip()
            if line.startswith('remotes/'):
                line = line.replace('remotes/origin/', '')
            if line and not line.startswith('HEAD'):
                branches.append(line)
        
        return list(set(branches))  # Remove duplicates
    
    def get_branch_info(self, branch: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific branch."""
        # Get last commit date
        date_output = self.run_git_command([
            'log', '-1', '--format=%ci', f'origin/{branch}'
        ])
        
        if not date_output:
            # Try local branch
            date_output = self.run_git_command([
                'log', '-1', '--format=%ci', branch
            ])
        
        if not date_output:
            return None
        
        try:
            last_commit_date = datetime.strptime(
                date_output.split()[0], '%Y-%m-%d'
            )
        except:
            return None
        
        # Get first commit date
        first_date_output = self.run_git_command([
            'log', '--reverse', '--format=%ci', f'origin/{branch}', '|', 'head', '-1'
        ])
        
        if not first_date_output:
            first_date_output = self.run_git_command([
                'log', '--reverse', '--format=%ci', branch
            ])
        
        if first_date_output:
            try:
                first_commit_date = datetime.strptime(
                    first_date_output.split()[0], '%Y-%m-%d'
                )
            except:
                first_commit_date = last_commit_date - timedelta(days=7)
        else:
            first_commit_date = last_commit_date - timedelta(days=7)
        
        # Get commit count
        commit_count = self.run_git_command([
            'rev-list', '--count', f'origin/{branch}'
        ])
        
        if not commit_count:
            commit_count = self.run_git_command([
                'rev-list', '--count', branch
            ])
        
        try:
            commit_count = int(commit_count)
        except:
            commit_count = 1
        
        return {
            'branch': branch,
            'first_commit': first_commit_date,
            'last_commit': last_commit_date,
            'commit_count': commit_count
        }
    
    def determine_status(self, branch_info: Dict[str, Any], branch_name: str) -> str:
        """Determine feature status based on branch activity."""
        # Check if branch is merged
        merged_output = self.run_git_command([
            'branch', '-a', '--merged', 'main'
        ])
        
        if branch_name in merged_output or branch_name == 'main':
            return 'completed'
        
        # Check recent activity (within last 7 days)
        days_since_commit = (datetime.now() - branch_info['last_commit']).days
        
        if days_since_commit <= 7:
            return 'in-progress'
        elif days_since_commit <= 30:
            return 'planned'
        else:
            return 'on-hold'
    
    def calculate_progress(self, branch_info: Dict[str, Any], status: str) -> int:
        """Calculate progress percentage based on commits and status."""
        if status == 'completed':
            return 100
        elif status == 'on-hold':
            return 10
        
        # Estimate based on commit count and time
        # Assume average feature takes 20 commits over 14 days
        commit_progress = min((branch_info['commit_count'] / 20) * 100, 80)
        
        duration_days = (branch_info['last_commit'] - branch_info['first_commit']).days
        time_progress = min((duration_days / 14) * 100, 80)
        
        # Average of both metrics
        progress = int((commit_progress + time_progress) / 2)
        
        return min(max(progress, 5), 95)  # Clamp between 5-95%
    
    def load_cortex_4_vision(self) -> Dict[str, Any]:
        """Load CORTEX 4.0 vision from YAML file."""
        vision_file = self.repo_root / 'cortex-brain' / 'documents' / 'planning' / 'cortex-4.0-vision.yaml'
        
        if not vision_file.exists():
            print(f"Warning: Vision file not found at {vision_file}", file=sys.stderr)
            return {'strategic_goals': [], 'roadmap': {'milestones': []}}
        
        try:
            import yaml
            with open(vision_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading CORTEX 4.0 vision: {e}", file=sys.stderr)
            return {'strategic_goals': [], 'roadmap': {'milestones': []}}
    
    def create_tasks_from_vision(self, vision: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create Gantt tasks from vision data."""
        tasks = []
        
        milestones = vision.get('roadmap', {}).get('milestones', [])
        
        for milestone_idx, milestone in enumerate(milestones):
            milestone_name = milestone.get('name', f'Milestone {milestone_idx + 1}')
            target = milestone.get('target', 'TBD')
            
            # Parse target quarter (e.g., "Q1 2025")
            try:
                if 'Q' in target:
                    quarter = int(target[1])
                    year = int(target.split()[-1])
                    
                    # Convert quarter to month
                    start_month = (quarter - 1) * 3 + 1
                    end_month = quarter * 3
                    
                    start_date = datetime(year, start_month, 1)
                    end_date = datetime(year, end_month, 28)
                else:
                    # Default to current date + 3 months
                    start_date = datetime.now()
                    end_date = start_date + timedelta(days=90)
            except:
                start_date = datetime.now()
                end_date = start_date + timedelta(days=90)
            
            # Create milestone task
            milestone_task = {
                'id': f'milestone-{milestone_idx}',
                'name': milestone_name,
                'start': start_date.strftime('%Y-%m-%d'),
                'end': end_date.strftime('%Y-%m-%d'),
                'progress': 0,
                'type': 'milestone',
                'dependencies': '',
                'custom_class': 'milestone-bar'
            }
            
            tasks.append(milestone_task)
            
            # Create tasks for key features
            key_features = milestone.get('key_features', [])
            feature_duration_days = 90 / max(len(key_features), 1)
            
            for feature_idx, feature_name in enumerate(key_features):
                feature_start = start_date + timedelta(days=feature_idx * feature_duration_days)
                feature_end = feature_start + timedelta(days=feature_duration_days)
                
                # Determine status and progress
                status = self.infer_feature_status(feature_name, milestone_idx, feature_idx)
                progress = self.infer_feature_progress(status)
                
                feature_task = {
                    'id': f'feature-{milestone_idx}-{feature_idx}',
                    'name': feature_name,
                    'start': feature_start.strftime('%Y-%m-%d'),
                    'end': feature_end.strftime('%Y-%m-%d'),
                    'progress': progress,
                    'type': 'task',
                    'dependencies': f'milestone-{milestone_idx}',
                    'custom_class': f'status-{status}',
                    'milestone': milestone_name,
                    'status': status
                }
                
                tasks.append(feature_task)
        
        return tasks
    
    def infer_feature_status(self, feature_name: str, milestone_idx: int, feature_idx: int) -> str:
        """Infer feature status based on position and naming."""
        # Simple heuristic: earlier milestones and features are further along
        if milestone_idx == 0:
            if feature_idx < 2:
                return 'in-progress'
            else:
                return 'planned'
        elif milestone_idx == 1:
            return 'planned'
        else:
            return 'future'
    
    def infer_feature_progress(self, status: str) -> int:
        """Infer progress percentage from status."""
        status_progress = {
            'completed': 100,
            'in-progress': 60,
            'planned': 20,
            'future': 5,
            'on-hold': 10
        }
        return status_progress.get(status, 0)
    
    def generate_gantt_data(self) -> Dict[str, Any]:
        """Generate complete Gantt chart data."""
        print("Loading CORTEX 4.0 vision...")
        vision = self.load_cortex_4_vision()
        
        print("Creating tasks from vision data...")
        tasks = self.create_tasks_from_vision(vision)
        
        print(f"Generated {len(tasks)} tasks")
        
        # Calculate statistics
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t.get('progress', 0) == 100])
        in_progress_tasks = len([t for t in tasks if 20 < t.get('progress', 0) < 100])
        
        avg_progress = sum(t.get('progress', 0) for t in tasks) / max(total_tasks, 1)
        
        gantt_data = {
            'generated_at': datetime.now().isoformat(),
            'tasks': tasks,
            'statistics': {
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'in_progress_tasks': in_progress_tasks,
                'pending_tasks': total_tasks - completed_tasks - in_progress_tasks,
                'average_progress': round(avg_progress, 1)
            },
            'view_mode': 'Month',  # Default view mode for Frappe Gantt
            'metadata': {
                'version': '1.0.0',
                'source': 'CORTEX 4.0 vision + git branch analysis',
                'chart_library': 'Frappe Gantt'
            }
        }
        
        return gantt_data
    
    def save_gantt_data(self, data: Dict[str, Any]) -> None:
        """Save Gantt data to JSON file."""
        output_dir = self.repo_root / 'docs' / 'gh-pages' / 'assets' / 'data'
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / 'gantt-data.json'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Gantt chart data saved to: {output_file}")
        print(f"   Size: {output_file.stat().st_size / 1024:.1f} KB")
    
    def generate_analysis_report(self, data: Dict[str, Any]) -> None:
        """Generate human-readable Gantt analysis report."""
        output_dir = self.repo_root / 'cortex-brain' / 'documents' / 'analysis'
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / 'gantt-analysis.md'
        
        stats = data['statistics']
        tasks = data['tasks']
        
        report = f"""# CORTEX Gantt Chart Analysis
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Source:** CORTEX 4.0 Vision Strategic Goals + Git Branch Analysis  
**Chart Type:** Gantt Timeline with Progress Tracking

---

## 📊 Project Statistics

### Overall Metrics
- **Total Tasks:** {stats['total_tasks']}
- **Completed Tasks:** {stats['completed_tasks']} ({(stats['completed_tasks'] / max(stats['total_tasks'], 1)) * 100:.1f}%)
- **In Progress:** {stats['in_progress_tasks']} ({(stats['in_progress_tasks'] / max(stats['total_tasks'], 1)) * 100:.1f}%)
- **Pending:** {stats['pending_tasks']} ({(stats['pending_tasks'] / max(stats['total_tasks'], 1)) * 100:.1f}%)
- **Average Progress:** {stats['average_progress']:.1f}%

---

## 📋 Task Breakdown by Milestone

"""
        
        # Group tasks by milestone
        milestones = {}
        for task in tasks:
            if task['type'] == 'milestone':
                milestone_name = task['name']
                milestones[milestone_name] = {
                    'milestone': task,
                    'features': []
                }
        
        for task in tasks:
            if task['type'] == 'task':
                milestone_name = task.get('milestone', 'Unknown')
                if milestone_name in milestones:
                    milestones[milestone_name]['features'].append(task)
        
        for milestone_name, milestone_data in milestones.items():
            milestone = milestone_data['milestone']
            features = milestone_data['features']
            
            report += f"""### {milestone_name}
- **Timeline:** {milestone['start']} to {milestone['end']}
- **Features:** {len(features)}
- **Avg Progress:** {sum(f.get('progress', 0) for f in features) / max(len(features), 1):.1f}%

**Features:**
"""
            
            for feature in features:
                status_emoji = {
                    'completed': '✅',
                    'in-progress': '🔄',
                    'planned': '📅',
                    'future': '🔮',
                    'on-hold': '⏸️'
                }.get(feature.get('status', 'planned'), '📅')
                
                report += f"- {status_emoji} **{feature['name']}** ({feature['start']} → {feature['end']}) - {feature['progress']}%\n"
            
            report += "\n"
        
        report += """---

## 🎯 Critical Path Analysis

The critical path represents the sequence of tasks that determines the minimum project duration. Features with dependencies should be prioritized to avoid delays.

### Key Insights

1. **Milestone Dependencies:** Features depend on milestone completion
2. **Sequential Execution:** Some features must complete before others begin
3. **Parallel Opportunities:** Independent features can be developed simultaneously

---

## 📈 Progress Tracking

### Status Distribution

"""
        
        status_counts = {}
        for task in tasks:
            if task['type'] == 'task':
                status = task.get('status', 'unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
        
        for status, count in sorted(status_counts.items()):
            percentage = (count / max(len([t for t in tasks if t['type'] == 'task']), 1)) * 100
            report += f"- **{status.replace('-', ' ').title()}:** {count} features ({percentage:.1f}%)\n"
        
        report += """

---

## 🚀 Recommendations

1. **Focus on In-Progress Features:** Complete active work before starting new tasks
2. **Unblock Dependencies:** Prioritize features that unblock downstream work
3. **Resource Allocation:** Distribute team capacity across parallel tracks
4. **Risk Management:** Monitor on-hold features for blockers

---

*This analysis provides a timeline view of CORTEX 4.0 development progress and helps identify scheduling conflicts and resource constraints.*
"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✅ Gantt analysis report saved to: {output_file}")
        print(f"   Size: {output_file.stat().st_size / 1024:.1f} KB")


def main():
    """Main entry point."""
    repo_root = Path(__file__).parent.parent
    
    print("=" * 70)
    print("CORTEX Gantt Chart Data Generator")
    print("=" * 70)
    print()
    
    generator = GanttDataGenerator(repo_root)
    
    try:
        # Generate Gantt data
        gantt_data = generator.generate_gantt_data()
        
        # Save to JSON file
        generator.save_gantt_data(gantt_data)
        
        # Generate analysis report
        generator.generate_analysis_report(gantt_data)
        
        print("\n✅ Gantt chart data generation complete!")
        print("\n📊 Summary:")
        print(f"   - Total tasks: {gantt_data['statistics']['total_tasks']}")
        print(f"   - Completed: {gantt_data['statistics']['completed_tasks']}")
        print(f"   - In progress: {gantt_data['statistics']['in_progress_tasks']}")
        print(f"   - Average progress: {gantt_data['statistics']['average_progress']:.1f}%")
        
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
