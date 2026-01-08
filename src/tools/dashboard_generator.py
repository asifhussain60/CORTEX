#!/usr/bin/env python3
"""
Progress Dashboard Generator (P0-T4)

Generates real-time progress dashboard for CORTEX 6.0 Remediation Plan.
Shows phase completion, health metrics, and validation gate status.

Part of: CORTEX 6.0 Remediation Plan - Phase P0
Author: GitHub Copilot + Asif Hussain
Created: 2026-01-08

Usage:
    python -m src.tools.dashboard_generator
    python -m src.tools.dashboard_generator --format html
    python -m src.tools.dashboard_generator --output dashboard.yaml
"""

import yaml
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict


@dataclass
class PhaseStatus:
    """Status of a remediation phase."""
    phase_id: str
    name: str
    status: str  # NOT_STARTED, IN_PROGRESS, COMPLETE
    tasks_total: int
    tasks_complete: int
    estimated_hours: float
    actual_hours: float
    completion_percentage: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'phase_id': self.phase_id,
            'name': self.name,
            'status': self.status,
            'tasks_total': self.tasks_total,
            'tasks_complete': self.tasks_complete,
            'estimated_hours': self.estimated_hours,
            'actual_hours': self.actual_hours,
            'completion_percentage': self.completion_percentage
        }


@dataclass
class DashboardMetrics:
    """Overall dashboard metrics."""
    overall_completion: float
    total_phases: int
    phases_complete: int
    total_tasks: int
    tasks_complete: int
    total_estimated_hours: float
    total_actual_hours: float
    efficiency_ratio: float  # actual / estimated
    health_score: int  # 0-100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'overall_completion': self.overall_completion,
            'total_phases': self.total_phases,
            'phases_complete': self.phases_complete,
            'total_tasks': self.total_tasks,
            'tasks_complete': self.tasks_complete,
            'total_estimated_hours': self.total_estimated_hours,
            'total_actual_hours': self.total_actual_hours,
            'efficiency_ratio': self.efficiency_ratio,
            'health_score': self.health_score
        }


class DashboardGenerator:
    """Generates progress dashboards from remediation plan YAML files."""
    
    def __init__(self, plan_dir: Optional[Path] = None):
        """
        Initialize dashboard generator.
        
        Args:
            plan_dir: Directory containing plan YAML files
        """
        if plan_dir is None:
            # Default to cortex6-fixes directory
            self.plan_dir = Path(__file__).parent.parent.parent / ".asif" / "AI-Learning" / "cortex6-fixes"
        else:
            self.plan_dir = Path(plan_dir)
        
        self.phases: List[PhaseStatus] = []
        self.metrics: Optional[DashboardMetrics] = None
    
    def load_plans(self) -> None:
        """Load all phase plan files."""
        self.phases = []
        
        # Find all phase YAML files (P0-*.yaml, P1-*.yaml, etc.)
        phase_files = sorted(self.plan_dir.glob("P*.yaml"))
        
        for phase_file in phase_files:
            with open(phase_file) as f:
                phase_data = yaml.safe_load(f)
            
            # Calculate task completion
            tasks = phase_data.get('tasks', [])
            tasks_complete = sum(1 for t in tasks if t.get('status') == 'COMPLETE')
            
            phase_status = PhaseStatus(
                phase_id=phase_data.get('phase_id', 'UNKNOWN'),
                name=phase_data.get('phase_name', 'Unknown Phase'),
                status=phase_data.get('status', 'NOT_STARTED'),
                tasks_total=len(tasks),
                tasks_complete=tasks_complete,
                estimated_hours=phase_data.get('estimated_hours', 0),
                actual_hours=phase_data.get('actual_hours', 0),
                completion_percentage=tasks_complete / len(tasks) * 100 if tasks else 0
            )
            
            self.phases.append(phase_status)
    
    def calculate_metrics(self) -> DashboardMetrics:
        """Calculate overall metrics."""
        if not self.phases:
            self.load_plans()
        
        total_tasks = sum(p.tasks_total for p in self.phases)
        tasks_complete = sum(p.tasks_complete for p in self.phases)
        total_estimated = sum(p.estimated_hours for p in self.phases)
        total_actual = sum(p.actual_hours for p in self.phases)
        phases_complete = sum(1 for p in self.phases if p.status == 'COMPLETE')
        
        overall_completion = tasks_complete / total_tasks * 100 if total_tasks > 0 else 0
        efficiency_ratio = total_actual / total_estimated if total_estimated > 0 else 0
        
        # Calculate health score (0-100)
        health_score = self._calculate_health_score(
            overall_completion, efficiency_ratio, phases_complete, len(self.phases)
        )
        
        self.metrics = DashboardMetrics(
            overall_completion=overall_completion,
            total_phases=len(self.phases),
            phases_complete=phases_complete,
            total_tasks=total_tasks,
            tasks_complete=tasks_complete,
            total_estimated_hours=total_estimated,
            total_actual_hours=total_actual,
            efficiency_ratio=efficiency_ratio,
            health_score=health_score
        )
        
        return self.metrics
    
    def _calculate_health_score(
        self, completion: float, efficiency: float, phases_done: int, total_phases: int
    ) -> int:
        """Calculate health score based on multiple factors."""
        # Weighted scoring:
        # - 40% completion
        # - 30% efficiency (1.0 = 100%, <1.0 is better, >1.5 is concerning)
        # - 30% phase progress
        
        completion_score = completion * 0.4
        
        # Efficiency score (100 if ratio is 1.0, decreases if ratio increases)
        if efficiency <= 1.0:
            efficiency_score = 30  # Perfect or under-estimate
        elif efficiency <= 1.5:
            efficiency_score = 30 - (efficiency - 1.0) * 30  # Gradual decrease
        else:
            efficiency_score = max(0, 15 - (efficiency - 1.5) * 10)  # Significant overrun
        
        phase_score = (phases_done / total_phases * 100 if total_phases > 0 else 0) * 0.3
        
        return int(completion_score + efficiency_score + phase_score)
    
    def generate_ascii_progress_bars(self) -> str:
        """Generate ASCII progress bars for accessibility."""
        if not self.phases:
            self.load_plans()
        
        lines = []
        lines.append("=" * 80)
        lines.append("CORTEX 6.0 REMEDIATION PROGRESS")
        lines.append("=" * 80)
        lines.append("")
        
        for phase in self.phases:
            # Progress bar: [######----] 60%
            bar_length = 40
            filled = int(phase.completion_percentage / 100 * bar_length)
            bar = "#" * filled + "-" * (bar_length - filled)
            
            status_emoji = {
                'NOT_STARTED': '⏳',
                'IN_PROGRESS': '🚧',
                'COMPLETE': '✅',
                'BLOCKED': '🚫'
            }.get(phase.status, '❓')
            
            lines.append(f"{status_emoji} {phase.phase_id}: {phase.name}")
            lines.append(f"   [{bar}] {phase.completion_percentage:.1f}%")
            lines.append(f"   Tasks: {phase.tasks_complete}/{phase.tasks_total} | "
                        f"Hours: {phase.actual_hours:.1f}/{phase.estimated_hours:.1f}")
            lines.append("")
        
        # Overall metrics
        if self.metrics:
            lines.append("=" * 80)
            lines.append(f"OVERALL: {self.metrics.overall_completion:.1f}% Complete | "
                        f"Health Score: {self.metrics.health_score}/100")
            lines.append(f"Tasks: {self.metrics.tasks_complete}/{self.metrics.total_tasks} | "
                        f"Hours: {self.metrics.total_actual_hours:.1f}/{self.metrics.total_estimated_hours:.1f}")
            lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def generate_yaml_dashboard(self) -> Dict[str, Any]:
        """Generate dashboard as YAML structure."""
        if not self.metrics:
            self.calculate_metrics()
        
        return {
            'generated_at': datetime.now().isoformat(),
            'metrics': self.metrics.to_dict(),
            'phases': [p.to_dict() for p in self.phases]
        }
    
    def generate_html_dashboard(self) -> str:
        """Generate HTML dashboard (optional, for visualization)."""
        if not self.metrics:
            self.calculate_metrics()
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>CORTEX 6.0 Remediation Dashboard</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #1a1a1a; color: #fff; }}
        .header {{ background: #2a2a2a; padding: 20px; border-radius: 5px; }}
        .metrics {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin: 20px 0; }}
        .metric-card {{ background: #2a2a2a; padding: 20px; border-radius: 5px; text-align: center; }}
        .metric-value {{ font-size: 36px; font-weight: bold; color: #4CAF50; }}
        .phase {{ background: #2a2a2a; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .progress-bar {{ background: #444; height: 30px; border-radius: 5px; overflow: hidden; }}
        .progress-fill {{ background: #4CAF50; height: 100%; transition: width 0.3s; }}
        .health-score {{ color: {'#4CAF50' if self.metrics.health_score >= 70 else '#FFA500' if self.metrics.health_score >= 50 else '#F44336'}; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🛡️ CORTEX 6.0 Remediation Dashboard</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="metrics">
        <div class="metric-card">
            <div class="metric-value">{self.metrics.overall_completion:.1f}%</div>
            <div>Overall Completion</div>
        </div>
        <div class="metric-card">
            <div class="metric-value health-score">{self.metrics.health_score}</div>
            <div>Health Score</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{self.metrics.tasks_complete}/{self.metrics.total_tasks}</div>
            <div>Tasks Complete</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{self.metrics.total_actual_hours:.1f}h</div>
            <div>Hours Invested</div>
        </div>
    </div>
    
    <h2>Phase Progress</h2>
"""
        
        for phase in self.phases:
            status_emoji = {'NOT_STARTED': '⏳', 'IN_PROGRESS': '🚧', 'COMPLETE': '✅', 'BLOCKED': '🚫'}.get(phase.status, '❓')
            html += f"""
    <div class="phase">
        <h3>{status_emoji} {phase.phase_id}: {phase.name}</h3>
        <div class="progress-bar">
            <div class="progress-fill" style="width: {phase.completion_percentage}%"></div>
        </div>
        <p>Tasks: {phase.tasks_complete}/{phase.tasks_total} | Hours: {phase.actual_hours:.1f}/{phase.estimated_hours:.1f}</p>
    </div>
"""
        
        html += """
</body>
</html>
"""
        return html
    
    def save(self, output_path: Path, format: str = 'yaml') -> None:
        """Save dashboard to file."""
        if format == 'yaml':
            data = self.generate_yaml_dashboard()
            with open(output_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        elif format == 'html':
            html = self.generate_html_dashboard()
            with open(output_path, 'w') as f:
                f.write(html)
        elif format == 'json':
            data = self.generate_yaml_dashboard()
            with open(output_path, 'w') as f:
                json.dump(data, f, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate CORTEX remediation progress dashboard")
    parser.add_argument('--plan-dir', type=Path, help="Directory containing plan YAML files")
    parser.add_argument('--output', type=Path, help="Output file path")
    parser.add_argument('--format', choices=['yaml', 'html', 'json', 'ascii'], default='ascii',
                       help="Output format")
    
    args = parser.parse_args()
    
    generator = DashboardGenerator(args.plan_dir)
    generator.load_plans()
    generator.calculate_metrics()
    
    if args.format == 'ascii':
        print(generator.generate_ascii_progress_bars())
    else:
        if not args.output:
            args.output = Path(f"dashboard.{args.format}")
        generator.save(args.output, args.format)
        print(f"✅ Dashboard saved to: {args.output}")


if __name__ == "__main__":
    main()
