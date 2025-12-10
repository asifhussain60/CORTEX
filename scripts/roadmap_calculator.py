#!/usr/bin/env python3
"""
CORTEX Roadmap Calculator
Analyzes git history to calculate development velocity and project realistic timelines.

Usage:
    python scripts/roadmap_calculator.py

Outputs:
    - docs/gh-pages/assets/data/roadmap-data.json (for D3.js visualizations)
    - cortex-brain/documents/analysis/velocity-analysis.md (detailed report)
"""

import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
import re


class RoadmapCalculator:
    """Calculates development velocity and generates roadmap projections."""
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.analysis_days = 90
        self.confidence_buffer_months = 1  # ±1 month per quarter
        
    def get_git_commits(self, since_days: int = 90) -> List[Dict[str, str]]:
        """Fetch git commits from the last N days."""
        since_date = (datetime.now() - timedelta(days=since_days)).strftime('%Y-%m-%d')
        
        try:
            result = subprocess.run(
                ['git', 'log', f'--since={since_date}', '--pretty=format:%h|%s|%ad|%an', '--date=short'],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=True
            )
            
            commits = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                parts = line.split('|')
                if len(parts) >= 4:
                    commits.append({
                        'hash': parts[0],
                        'subject': parts[1],
                        'date': parts[2],
                        'author': parts[3]
                    })
            
            return commits
        except subprocess.CalledProcessError as e:
            print(f"Error fetching git commits: {e}", file=sys.stderr)
            return []
    
    def categorize_commit(self, subject: str) -> str:
        """Categorize commit by type (feature, fix, docs, refactor, test, chore)."""
        subject_lower = subject.lower()
        
        if any(word in subject_lower for word in ['feat', 'feature', 'add', 'implement', 'complete']):
            return 'feature'
        elif any(word in subject_lower for word in ['fix', 'resolve', 'correct']):
            return 'fix'
        elif any(word in subject_lower for word in ['docs', 'documentation']):
            return 'docs'
        elif any(word in subject_lower for word in ['refactor', 'clean', 'optimize']):
            return 'refactor'
        elif any(word in subject_lower for word in ['test', 'coverage']):
            return 'test'
        else:
            return 'chore'
    
    def extract_features(self, commits: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Extract feature-related commits and identify features."""
        features = []
        feature_commits = [c for c in commits if self.categorize_commit(c['subject']) == 'feature']
        
        # Group by feature patterns
        for commit in feature_commits:
            subject = commit['subject']
            
            # Extract feature name from commit message
            # Patterns: "feat(name):", "feat: name", "feature: name", "complete name"
            feature_match = re.search(r'feat\(([^)]+)\):|feat:\s+(.+?)(?:\s*-|$)|feature:\s+(.+?)(?:\s*-|$)|complete\s+(.+?)(?:\s*-|$)', subject, re.IGNORECASE)
            
            if feature_match:
                feature_name = next((g for g in feature_match.groups() if g), 'Unknown Feature')
                feature_name = feature_name.strip()
                
                features.append({
                    'name': feature_name,
                    'commit': commit['hash'],
                    'date': commit['date'],
                    'subject': subject
                })
        
        return features
    
    def calculate_velocity(self, commits: List[Dict[str, str]]) -> Dict[str, Any]:
        """Calculate development velocity metrics."""
        if not commits:
            return {
                'features_per_month': 0,
                'commits_per_week': 0,
                'avg_features_per_sprint': 0,
                'total_commits': 0,
                'total_features': 0
            }
        
        # Calculate time span
        dates = [datetime.strptime(c['date'], '%Y-%m-%d') for c in commits]
        earliest = min(dates)
        latest = max(dates)
        days_span = (latest - earliest).days or 1
        weeks = days_span / 7
        months = days_span / 30.44
        
        # Count features
        features = self.extract_features(commits)
        total_features = len(features)
        
        # Calculate velocity
        features_per_month = total_features / months if months > 0 else 0
        commits_per_week = len(commits) / weeks if weeks > 0 else 0
        avg_features_per_sprint = features_per_month / 2 if features_per_month > 0 else 0  # 2-week sprints
        
        return {
            'features_per_month': round(features_per_month, 2),
            'commits_per_week': round(commits_per_week, 2),
            'avg_features_per_sprint': round(avg_features_per_sprint, 2),
            'total_commits': len(commits),
            'total_features': total_features,
            'analysis_period_days': days_span,
            'earliest_commit': earliest.isoformat(),
            'latest_commit': latest.isoformat()
        }
    
    def load_cortex_4_vision(self) -> Dict[str, Any]:
        """Load CORTEX 4.0 vision from YAML file."""
        vision_file = self.repo_root / 'cortex-brain' / 'documents' / 'planning' / 'cortex-4.0-vision.yaml'
        
        if not vision_file.exists():
            return {'roadmap': {'milestones': []}}
        
        try:
            import yaml
            with open(vision_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading CORTEX 4.0 vision: {e}", file=sys.stderr)
            return {'roadmap': {'milestones': []}}
    
    def project_timeline(self, velocity: Dict[str, Any], vision: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Project timeline for CORTEX 4.0 milestones based on velocity."""
        milestones = vision.get('roadmap', {}).get('milestones', [])
        projected_timeline = []
        
        base_date = datetime.now()
        
        for milestone in milestones:
            milestone_name = milestone.get('name', 'Unknown')
            target_quarter = milestone.get('target', 'Q1 2026')
            features_count = len(milestone.get('key_features', []))
            
            # Calculate estimated completion based on velocity
            if velocity['features_per_month'] > 0:
                months_needed = features_count / velocity['features_per_month']
                confidence_range = self.confidence_buffer_months
            else:
                months_needed = features_count * 2  # Fallback: 2 months per feature
                confidence_range = 2
            
            projected_date = base_date + timedelta(days=30.44 * months_needed)
            early_date = projected_date - timedelta(days=30.44 * confidence_range)
            late_date = projected_date + timedelta(days=30.44 * confidence_range)
            
            projected_timeline.append({
                'milestone': milestone_name,
                'target_quarter': target_quarter,
                'features_count': features_count,
                'estimated_months': round(months_needed, 1),
                'projected_date': projected_date.strftime('%Y-%m-%d'),
                'confidence_range': {
                    'early': early_date.strftime('%Y-%m-%d'),
                    'late': late_date.strftime('%Y-%m-%d')
                },
                'key_features': milestone.get('key_features', [])
            })
            
            # Next milestone starts after this one
            base_date = late_date
        
        return projected_timeline
    
    def prioritize_features(self, vision: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Prioritize features based on strategic goals and dependencies."""
        strategic_goals = vision.get('strategic_goals', [])
        prioritized = []
        
        for idx, goal in enumerate(strategic_goals):
            priority = 'HIGH' if idx < 2 else ('MEDIUM' if idx < 4 else 'LOW')
            
            prioritized.append({
                'goal': goal.get('goal', 'Unknown'),
                'priority': priority,
                'category': goal.get('category', 'uncategorized'),
                'success_metrics': goal.get('success_metrics', {}),
                'dependencies': goal.get('dependencies', [])
            })
        
        return prioritized
    
    def generate_roadmap_data(self) -> Dict[str, Any]:
        """Generate complete roadmap data for visualization."""
        print("Analyzing git history...")
        commits = self.get_git_commits(self.analysis_days)
        
        print(f"Found {len(commits)} commits in last {self.analysis_days} days")
        
        print("Calculating velocity metrics...")
        velocity = self.calculate_velocity(commits)
        
        print("Loading CORTEX 4.0 vision...")
        vision = self.load_cortex_4_vision()
        
        print("Projecting timeline...")
        timeline = self.project_timeline(velocity, vision)
        
        print("Prioritizing features...")
        priorities = self.prioritize_features(vision)
        
        roadmap_data = {
            'generated_at': datetime.now().isoformat(),
            'analysis_period_days': self.analysis_days,
            'velocity': velocity,
            'timeline': timeline,
            'priorities': priorities,
            'metadata': {
                'version': '1.0.0',
                'source': 'git history + CORTEX 4.0 vision',
                'confidence_buffer_months': self.confidence_buffer_months
            }
        }
        
        return roadmap_data
    
    def save_roadmap_data(self, data: Dict[str, Any]) -> None:
        """Save roadmap data to JSON file for D3.js consumption."""
        output_dir = self.repo_root / 'docs' / 'gh-pages' / 'assets' / 'data'
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / 'roadmap-data.json'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Roadmap data saved to: {output_file}")
        print(f"   Size: {output_file.stat().st_size / 1024:.1f} KB")
    
    def generate_analysis_report(self, data: Dict[str, Any]) -> None:
        """Generate human-readable analysis report."""
        output_dir = self.repo_root / 'cortex-brain' / 'documents' / 'analysis'
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / 'velocity-analysis.md'
        
        velocity = data['velocity']
        timeline = data['timeline']
        
        report = f"""# CORTEX Development Velocity Analysis
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Analysis Period:** {velocity['analysis_period_days']} days  
**Confidence Buffer:** ±{data['metadata']['confidence_buffer_months']} month per quarter

---

## 📊 Velocity Metrics

### Overall Performance
- **Total Commits:** {velocity['total_commits']}
- **Total Features Delivered:** {velocity['total_features']}
- **Commits per Week:** {velocity['commits_per_week']}
- **Features per Month:** {velocity['features_per_month']}
- **Avg Features per Sprint:** {velocity['avg_features_per_sprint']} (2-week sprints)

### Commit Activity Period
- **Earliest Commit:** {velocity['earliest_commit']}
- **Latest Commit:** {velocity['latest_commit']}
- **Analysis Period:** {velocity['analysis_period_days']} days

---

## 🗺️ Projected Timeline

"""
        
        for milestone in timeline:
            report += f"""### {milestone['milestone']}
- **Target Quarter:** {milestone['target_quarter']}
- **Features Count:** {milestone['features_count']}
- **Estimated Duration:** {milestone['estimated_months']} months
- **Projected Completion:** {milestone['projected_date']}
- **Confidence Range:** {milestone['confidence_range']['early']} to {milestone['confidence_range']['late']}

**Key Features:**
"""
            for feature in milestone['key_features'][:5]:  # Top 5
                report += f"- {feature}\n"
            
            if len(milestone['key_features']) > 5:
                report += f"- ... and {len(milestone['key_features']) - 5} more\n"
            
            report += "\n"
        
        report += f"""---

## 🎯 Feature Prioritization

"""
        
        for priority in data['priorities']:
            report += f"""### {priority['goal']} ({priority['priority']} Priority)
- **Category:** {priority['category']}
- **Dependencies:** {', '.join(priority['dependencies']) if priority['dependencies'] else 'None'}

"""
        
        report += f"""---

## 📈 Velocity Interpretation

"""
        
        if velocity['features_per_month'] >= 10:
            report += "**Status:** 🚀 High Velocity - Excellent feature delivery rate\n"
        elif velocity['features_per_month'] >= 5:
            report += "**Status:** ✅ Good Velocity - Solid feature delivery rate\n"
        elif velocity['features_per_month'] >= 2:
            report += "**Status:** ⚠️ Moderate Velocity - Consider optimization\n"
        else:
            report += "**Status:** 🔴 Low Velocity - Requires attention\n"
        
        report += f"""
**Confidence Level:** ±{data['metadata']['confidence_buffer_months']} month buffer accounts for:
- Complexity variations
- Dependency delays
- Resource availability
- Technical challenges

---

## 🔮 Recommendations

"""
        
        if velocity['features_per_month'] < 5:
            report += """1. **Increase Velocity:**
   - Break down features into smaller increments
   - Reduce work-in-progress (WIP) limits
   - Automate repetitive tasks

"""
        
        report += """2. **Maintain Quality:**
   - Continue TDD practices (RED-GREEN-REFACTOR)
   - Regular code reviews
   - Comprehensive testing

3. **Timeline Management:**
   - Review milestones quarterly
   - Adjust projections based on actual velocity
   - Communicate changes early

---

*This analysis is automatically generated from git history and CORTEX 4.0 vision data.*
"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✅ Analysis report saved to: {output_file}")
        print(f"   Size: {output_file.stat().st_size / 1024:.1f} KB")


def main():
    """Main entry point."""
    repo_root = Path(__file__).parent.parent
    
    print("=" * 70)
    print("CORTEX Roadmap Calculator")
    print("=" * 70)
    print()
    
    calculator = RoadmapCalculator(repo_root)
    
    try:
        # Generate roadmap data
        roadmap_data = calculator.generate_roadmap_data()
        
        # Save to JSON file
        calculator.save_roadmap_data(roadmap_data)
        
        # Generate analysis report
        calculator.generate_analysis_report(roadmap_data)
        
        print("\n✅ Roadmap calculation complete!")
        print("\n📊 Summary:")
        print(f"   - Features per month: {roadmap_data['velocity']['features_per_month']}")
        print(f"   - Total commits analyzed: {roadmap_data['velocity']['total_commits']}")
        print(f"   - Milestones projected: {len(roadmap_data['timeline'])}")
        print(f"   - Priorities identified: {len(roadmap_data['priorities'])}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
