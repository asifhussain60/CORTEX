"""
Integration Health Dashboard Generator

Creates visual reports with status indicators, trend analysis,
priority matrices, and historical comparisons for system alignment.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


@dataclass
class TrendData:
    """Trend analysis data."""
    current_score: int
    previous_score: Optional[int]
    direction: str  # 'improving', 'stable', 'degrading'
    change_percent: float
    velocity: float  # Score change per day


class DashboardGenerator:
    """
    Generates visual integration health dashboards.
    
    Features:
    - Emoji status indicators (✅ ⚠️ ❌)
    - Score trends (↗️ → ↘️)
    - Priority matrices (Critical/Warning/Info)
    - Historical comparison
    - Estimated fix time
    """
    
    def __init__(self, project_root: Path):
        """Initialize dashboard generator."""
        self.project_root = project_root
        self.brain_path = project_root / "cortex-brain"
        self.history_file = self.brain_path / "metrics-history" / "alignment_history.jsonl"
    
    def generate_dashboard(self, report: 'AlignmentReport', conflicts: List['Conflict']) -> str:
        """
        Generate complete dashboard report.
        
        Args:
            report: Alignment report with scores
            conflicts: List of detected conflicts
            
        Returns:
            Formatted dashboard string
        """
        lines = [
            "",
            "=" * 100,
            "🧠 CORTEX INTEGRATION HEALTH DASHBOARD",
            "=" * 100,
            "",
            self._generate_overview_section(report),
            "",
            self._generate_trends_section(report),
            "",
            self._generate_conflicts_section(conflicts),
            "",
            self._generate_priority_matrix(report, conflicts),
            "",
            self._generate_recommendations(report, conflicts),
            "",
            "=" * 100,
            ""
        ]
        
        return "\n".join(lines)
    
    def _generate_overview_section(self, report: 'AlignmentReport') -> str:
        """Generate overview with status indicators."""
        status_emoji = self._get_status_emoji(report.overall_health)
        trend_emoji = self._get_trend_emoji(report)
        
        lines = [
            "📊 OVERALL HEALTH",
            "-" * 100,
            f"",
            f"  {status_emoji} Overall Score: {report.overall_health}% {trend_emoji}",
            f"  ❌ Critical Issues: {report.critical_issues}",
            f"  ⚠️  Warnings: {report.warnings}",
            f"  📅 Assessed: {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            ""
        ]
        
        # Feature breakdown
        total_features = len(report.feature_scores)
        healthy = sum(1 for s in report.feature_scores.values() if s.score >= 90)
        warning = sum(1 for s in report.feature_scores.values() if 70 <= s.score < 90)
        critical = sum(1 for s in report.feature_scores.values() if s.score < 70)
        
        lines.extend([
            f"  📦 Total Features: {total_features}",
            f"     ✅ Healthy (≥90%): {healthy} ({healthy/total_features*100:.1f}%)",
            f"     ⚠️  Warning (70-89%): {warning} ({warning/total_features*100:.1f}%)",
            f"     ❌ Critical (<70%): {critical} ({critical/total_features*100:.1f}%)",
        ])
        
        return "\n".join(lines)
    
    def _generate_trends_section(self, report: 'AlignmentReport') -> str:
        """Generate trend analysis with historical comparison."""
        lines = [
            "📈 TREND ANALYSIS",
            "-" * 100,
            ""
        ]
        
        # Load historical data
        history = self._load_history()
        
        if len(history) < 2:
            lines.append("  ℹ️  Insufficient data for trend analysis (need 2+ data points)")
            return "\n".join(lines)
        
        # Calculate trends
        current = report.overall_health
        previous = history[-2]['overall_health']
        
        trend = self._calculate_trend(current, previous)
        
        lines.extend([
            f"  Current Score: {current}%",
            f"  Previous Score: {previous}%",
            f"  Change: {trend.direction} {abs(trend.change_percent):.1f}% {self._get_trend_arrow(trend.direction)}",
            f"  Velocity: {trend.velocity:+.2f} points/day",
            ""
        ])
        
        # 7-day trend if available
        week_ago = None
        for entry in reversed(history):
            entry_date = datetime.fromisoformat(entry['timestamp'])
            if datetime.now() - entry_date >= timedelta(days=7):
                week_ago = entry['overall_health']
                break
        
        if week_ago:
            week_change = current - week_ago
            lines.append(f"  7-Day Change: {week_change:+d} points")
        
        return "\n".join(lines)
    
    def _generate_conflicts_section(self, conflicts: List['Conflict']) -> str:
        """Generate conflicts summary."""
        lines = [
            "⚔️  DETECTED CONFLICTS",
            "-" * 100,
            ""
        ]
        
        if not conflicts:
            lines.append("  ✅ No conflicts detected - ecosystem is consistent!")
            return "\n".join(lines)
        
        # Group by severity
        critical = [c for c in conflicts if c.severity == 'critical']
        warning = [c for c in conflicts if c.severity == 'warning']
        info = [c for c in conflicts if c.severity == 'info']
        
        lines.extend([
            f"  Total Conflicts: {len(conflicts)}",
            f"    ❌ Critical: {len(critical)}",
            f"    ⚠️  Warning: {len(warning)}",
            f"    ℹ️  Info: {len(info)}",
            ""
        ])
        
        # Show top 5 conflicts
        lines.append("  Top Issues:")
        lines.append("")
        
        for idx, conflict in enumerate(conflicts[:5], 1):
            emoji = self._get_severity_emoji(conflict.severity)
            fixable = "🔧 Auto-fixable" if conflict.auto_fixable else "👤 Manual fix"
            
            lines.extend([
                f"  {idx}. {emoji} {conflict.title}",
                f"     {conflict.description}",
                f"     {fixable}",
                ""
            ])
        
        if len(conflicts) > 5:
            lines.append(f"  ... and {len(conflicts) - 5} more conflicts")
        
        return "\n".join(lines)
    
    def _generate_priority_matrix(self, report: 'AlignmentReport', conflicts: List['Conflict']) -> str:
        """Generate action priority matrix."""
        lines = [
            "🎯 ACTION PRIORITY MATRIX",
            "-" * 100,
            ""
        ]
        
        # Collect all action items
        actions = []
        
        # From conflicts
        for conflict in conflicts:
            actions.append({
                'priority': 1 if conflict.severity == 'critical' else 2 if conflict.severity == 'warning' else 3,
                'title': conflict.title,
                'estimated_time': '5-15 min' if conflict.auto_fixable else '30-60 min',
                'impact': 'High' if conflict.severity == 'critical' else 'Medium' if conflict.severity == 'warning' else 'Low'
            })
        
        # From feature scores
        for name, score in report.feature_scores.items():
            if score.score < 70:
                actions.append({
                    'priority': 1,
                    'title': f"Fix {name} integration (score: {score.score}%)",
                    'estimated_time': '30-60 min',
                    'impact': 'High'
                })
            elif score.score < 90:
                actions.append({
                    'priority': 2,
                    'title': f"Improve {name} integration (score: {score.score}%)",
                    'estimated_time': '15-30 min',
                    'impact': 'Medium'
                })
        
        # Sort by priority
        actions.sort(key=lambda a: a['priority'])
        
        if not actions:
            lines.append("  ✅ No actions required - system is healthy!")
            return "\n".join(lines)
        
        # Priority 1 (Critical)
        p1_actions = [a for a in actions if a['priority'] == 1]
        if p1_actions:
            lines.append("  🔴 PRIORITY 1: Critical (Do Now)")
            lines.append("")
            for idx, action in enumerate(p1_actions[:3], 1):
                lines.append(f"     {idx}. {action['title']}")
                lines.append(f"        ⏱  Est. Time: {action['estimated_time']} | 💥 Impact: {action['impact']}")
                lines.append("")
        
        # Priority 2 (Important)
        p2_actions = [a for a in actions if a['priority'] == 2]
        if p2_actions:
            lines.append("  🟡 PRIORITY 2: Important (Do Soon)")
            lines.append("")
            for idx, action in enumerate(p2_actions[:3], 1):
                lines.append(f"     {idx}. {action['title']}")
                lines.append(f"        ⏱  Est. Time: {action['estimated_time']} | 💥 Impact: {action['impact']}")
                lines.append("")
        
        # Priority 3 (Nice to Have)
        p3_actions = [a for a in actions if a['priority'] == 3]
        if p3_actions:
            lines.append("  🟢 PRIORITY 3: Nice to Have (Do Later)")
            lines.append(f"     {len(p3_actions)} items - run 'align report --full' to see all")
            lines.append("")
        
        # Total estimated time
        total_time = len(actions) * 20  # Rough estimate: 20 min average
        lines.append(f"  📊 Total Estimated Time: ~{total_time} minutes ({total_time/60:.1f} hours)")
        
        return "\n".join(lines)
    
    def _generate_recommendations(self, report: 'AlignmentReport', conflicts: List['Conflict']) -> str:
        """Generate smart recommendations."""
        lines = [
            "💡 SMART RECOMMENDATIONS",
            "-" * 100,
            ""
        ]
        
        recommendations = []
        
        # Based on overall health
        if report.overall_health < 70:
            recommendations.append("🚨 System health critical - prioritize fixing critical issues before new development")
        elif report.overall_health < 80:
            recommendations.append("⚠️  System health needs improvement - allocate time for technical debt")
        else:
            recommendations.append("✅ System health good - maintain with regular alignment checks")
        
        # Based on conflicts
        critical_conflicts = [c for c in conflicts if c.severity == 'critical']
        if critical_conflicts:
            auto_fixable = [c for c in critical_conflicts if c.auto_fixable]
            if auto_fixable:
                recommendations.append(f"🔧 {len(auto_fixable)} critical issues can be auto-fixed - run 'align fix --auto'")
            else:
                recommendations.append(f"👤 {len(critical_conflicts)} critical issues require manual fixes - review detailed report")
        
        # Based on trends
        history = self._load_history()
        if len(history) >= 2:
            current = report.overall_health
            previous = history[-2]['overall_health']
            if current < previous:
                recommendations.append("📉 Health declining - investigate recent changes causing degradation")
            elif current > previous:
                recommendations.append("📈 Health improving - keep up the good work!")
        
        # Integration-specific
        low_scoring = [name for name, score in report.feature_scores.items() if score.score < 70]
        if low_scoring:
            recommendations.append(f"📦 {len(low_scoring)} features need attention - focus on: {', '.join(low_scoring[:3])}")
        
        for rec in recommendations:
            lines.append(f"  • {rec}")
            lines.append("")
        
        return "\n".join(lines)
    
    def save_history(self, report: 'AlignmentReport') -> None:
        """Save alignment report to history."""
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        
        entry = {
            'timestamp': report.timestamp.isoformat(),
            'overall_health': report.overall_health,
            'critical_issues': report.critical_issues,
            'warnings': report.warnings,
            'feature_count': len(report.feature_scores)
        }
        
        with open(self.history_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + '\n')
    
    def _load_history(self) -> List[Dict]:
        """Load alignment history."""
        if not self.history_file.exists():
            return []
        
        history = []
        with open(self.history_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    history.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        
        return history
    
    def _calculate_trend(self, current: int, previous: int) -> TrendData:
        """Calculate trend from current and previous scores."""
        change = current - previous
        change_percent = (change / previous * 100) if previous > 0 else 0
        
        if abs(change) < 2:
            direction = 'stable'
        elif change > 0:
            direction = 'improving'
        else:
            direction = 'degrading'
        
        # Assume 1 day between measurements for velocity
        velocity = change
        
        return TrendData(
            current_score=current,
            previous_score=previous,
            direction=direction,
            change_percent=change_percent,
            velocity=velocity
        )
    
    # Helper methods
    
    def _get_status_emoji(self, score: int) -> str:
        """Get emoji for score."""
        if score >= 90:
            return "✅"
        elif score >= 70:
            return "⚠️"
        else:
            return "❌"
    
    def _get_trend_emoji(self, report: 'AlignmentReport') -> str:
        """Get trend emoji."""
        history = self._load_history()
        if len(history) < 2:
            return ""
        
        current = report.overall_health
        previous = history[-2]['overall_health']
        
        if current > previous + 2:
            return "↗️"
        elif current < previous - 2:
            return "↘️"
        else:
            return "→"
    
    def _get_trend_arrow(self, direction: str) -> str:
        """Get arrow for trend direction."""
        return {
            'improving': '↗️',
            'stable': '→',
            'degrading': '↘️'
        }.get(direction, '→')
    
    def _get_severity_emoji(self, severity: str) -> str:
        """Get emoji for severity."""
        return {
            'critical': '❌',
            'warning': '⚠️',
            'info': 'ℹ️'
        }.get(severity, 'ℹ️')
