"""
CORTEX 3.0 - EPMO Health System Integration
===========================================

Integration module for EPMO health validation system.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import json
from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime

from .validation_suite import EPMOHealthValidator
from .remediation_engine import RemediationEngine
from .dashboard import HealthDashboard


class EPMOHealthSystem:
    """Complete EPMO health monitoring and remediation system."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.validator = EPMOHealthValidator()
        self.remediation_engine = RemediationEngine()
        self.dashboard = HealthDashboard(project_root)
        
        # Ensure health reports directory exists
        self.reports_dir = project_root / 'cortex-brain' / 'health-reports'
        self.reports_dir.mkdir(parents=True, exist_ok=True)
    
    def run_comprehensive_health_check(self, epmo_path: Path) -> Dict[str, Any]:
        """Run comprehensive health check on an EPMO."""
        print(f"🏥 Running comprehensive health check on {epmo_path.name}")
        
        # Step 1: Validate EPMO health
        print("  📊 Running validation suite...")
        health_report = self.validator.validate_epmo_health(epmo_path, self.project_root)
        
        # Step 2: Generate remediation plan
        print("  🔧 Generating remediation plan...")
        all_results = []
        for dimension_results in health_report['dimension_scores'].values():
            # Get original ValidationResult objects from results list
            original_results = dimension_results.get('original_results', [])
            all_results.extend(original_results)
        
        remediation_plan = self.remediation_engine.generate_remediation_plan(all_results)
        effort_estimate = self.remediation_engine.estimate_total_effort(remediation_plan)
        
        # Step 3: Update historical data
        print("  📈 Updating historical trends...")
        self.dashboard.update_historical_data(epmo_path, health_report)
        
        # Step 4: Generate dashboard
        dashboard_file = self.reports_dir / f'{epmo_path.name}_dashboard.html'
        print(f"  🎨 Generating dashboard: {dashboard_file}")
        self.dashboard.generate_html_dashboard(epmo_path, dashboard_file)
        
        # Step 5: Save detailed report
        report_file = self.reports_dir / f'{epmo_path.name}_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        # Create JSON-serializable version of health_report
        json_health_report = health_report.copy()
        json_dimension_scores = {}
        for dim_name, dim_data in health_report['dimension_scores'].items():
            json_dimension_scores[dim_name] = {
                'score': dim_data['score'],
                'weight': dim_data['weight'],
                'weighted_score': dim_data['weighted_score'],
                'results': dim_data['results']  # These are already serialized
            }
        json_health_report['dimension_scores'] = json_dimension_scores
        
        detailed_report = {
            'timestamp': datetime.now().isoformat(),
            'epmo_path': str(epmo_path),
            'health_report': json_health_report,
            'remediation_plan': [self._serialize_action(action) for action in remediation_plan],
            'effort_estimate': effort_estimate,
            'dashboard_file': str(dashboard_file)
        }
        
        with open(report_file, 'w') as f:
            json.dump(detailed_report, f, indent=2)
        
        print(f"  💾 Detailed report saved: {report_file}")
        
        return detailed_report
    
    def apply_auto_fixes(self, epmo_path: Path) -> Dict[str, Any]:
        """Apply all available auto-fixes for an EPMO."""
        print(f"🔧 Applying auto-fixes to {epmo_path.name}")
        
        # Run health check to get current issues
        health_report = self.validator.validate_epmo_health(epmo_path, self.project_root)
        
        # Generate remediation plan
        all_results = []
        for dimension_results in health_report['dimension_scores'].values():
            all_results.extend(dimension_results.get('results', []))
        
        remediation_plan = self.remediation_engine.generate_remediation_plan(all_results)
        
        # Apply auto-fixes
        auto_fix_results = []
        python_files = list(epmo_path.rglob("*.py"))
        
        for action in remediation_plan:
            if action.auto_fixable:
                print(f"  🔧 Applying: {action.description}")
                
                # Try to apply fix to each Python file
                for file_path in python_files:
                    success, message = self.remediation_engine.execute_remediation(action, file_path)
                    auto_fix_results.append({
                        'action': action.action_type,
                        'file': str(file_path),
                        'success': success,
                        'message': message
                    })
        
        # Re-run health check to measure improvement
        print("  📊 Measuring improvement...")
        new_health_report = self.validator.validate_epmo_health(epmo_path, self.project_root)
        
        improvement = new_health_report['overall_score'] - health_report['overall_score']
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'epmo_path': str(epmo_path),
            'auto_fixes_applied': len([r for r in auto_fix_results if r['success']]),
            'total_auto_fixes_attempted': len(auto_fix_results),
            'initial_score': health_report['overall_score'],
            'final_score': new_health_report['overall_score'],
            'improvement': improvement,
            'auto_fix_results': auto_fix_results
        }
        
        print(f"  ✅ Auto-fixes complete. Score improvement: {improvement:+.1f} points")
        
        return result
    
    def monitor_epmo_health(self, epmo_paths: List[Path]) -> Dict[str, Any]:
        """Monitor health across multiple EPMOs."""
        print(f"👥 Monitoring health across {len(epmo_paths)} EPMOs")
        
        epmo_health_data = {}
        overall_stats = {
            'total_epmos': len(epmo_paths),
            'healthy_epmos': 0,
            'warning_epmos': 0,
            'critical_epmos': 0,
            'average_score': 0,
            'total_remediation_hours': 0
        }
        
        for epmo_path in epmo_paths:
            if not epmo_path.exists():
                continue
                
            print(f"  🔍 Checking {epmo_path.name}...")
            
            # Run health check
            health_report = self.validator.validate_epmo_health(epmo_path, self.project_root)
            score = health_report['overall_score']
            
            # Categorize health status
            if score >= 85:
                status = 'healthy'
                overall_stats['healthy_epmos'] += 1
            elif score >= 70:
                status = 'warning'
                overall_stats['warning_epmos'] += 1
            else:
                status = 'critical'
                overall_stats['critical_epmos'] += 1
            
            # Generate remediation estimate
            all_results = []
            for dimension_results in health_report['dimension_scores'].values():
                all_results.extend(dimension_results.get('results', []))
            
            remediation_plan = self.remediation_engine.generate_remediation_plan(all_results)
            effort_estimate = self.remediation_engine.estimate_total_effort(remediation_plan)
            
            epmo_health_data[epmo_path.name] = {
                'path': str(epmo_path),
                'score': score,
                'status': status,
                'remediation_hours': effort_estimate['total_hours'],
                'auto_fixable_actions': effort_estimate['auto_fixable_actions'],
                'manual_actions': effort_estimate['manual_actions']
            }
            
            overall_stats['total_remediation_hours'] += effort_estimate['total_hours']
        
        overall_stats['average_score'] = sum(epmo['score'] for epmo in epmo_health_data.values()) / len(epmo_health_data)
        
        monitoring_report = {
            'timestamp': datetime.now().isoformat(),
            'overall_stats': overall_stats,
            'epmo_details': epmo_health_data,
            'recommendations': self._generate_monitoring_recommendations(overall_stats, epmo_health_data)
        }
        
        # Save monitoring report
        report_file = self.reports_dir / f'monitoring_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(report_file, 'w') as f:
            json.dump(monitoring_report, f, indent=2)
        
        print(f"  📊 Monitoring complete. Average score: {overall_stats['average_score']:.1f}")
        print(f"  💾 Monitoring report saved: {report_file}")
        
        return monitoring_report
    
    def _serialize_action(self, action) -> Dict[str, Any]:
        """Serialize remediation action for JSON storage."""
        return {
            'action_type': action.action_type,
            'description': action.description,
            'auto_fixable': action.auto_fixable,
            'estimated_effort_minutes': action.estimated_effort_minutes,
            'priority': action.priority,
            'metadata': action.metadata
        }
    
    def _serialize_validation_result(self, result) -> Dict[str, Any]:
        """Serialize ValidationResult for JSON storage."""
        return {
            'dimension': result.dimension.value,
            'check_name': result.check_name,
            'severity': result.severity.value,
            'score': result.score,
            'max_score': result.max_score,
            'message': result.message,
            'details': result.details,
            'metadata': result.metadata
        }
    
    def _generate_monitoring_recommendations(self, stats: Dict[str, Any], epmo_data: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on monitoring results."""
        recommendations = []
        
        # Overall health recommendations
        if stats['average_score'] < 70:
            recommendations.append("🚨 Overall EPMO health is below acceptable threshold. Prioritize immediate remediation.")
        elif stats['average_score'] < 85:
            recommendations.append("⚠️ EPMO health shows room for improvement. Focus on targeted enhancements.")
        else:
            recommendations.append("✅ EPMO health is excellent. Maintain current standards.")
        
        # Critical EPMOs
        critical_epmos = [name for name, data in epmo_data.items() if data['status'] == 'critical']
        if critical_epmos:
            recommendations.append(f"🔥 Critical attention needed for: {', '.join(critical_epmos)}")
        
        # Auto-fix opportunities
        total_auto_fixes = sum(data['auto_fixable_actions'] for data in epmo_data.values())
        if total_auto_fixes > 0:
            recommendations.append(f"🔧 {total_auto_fixes} issues can be auto-fixed across all EPMOs.")
        
        # Effort estimation
        if stats['total_remediation_hours'] > 40:
            recommendations.append("📊 High remediation effort detected. Consider phased approach.")
        elif stats['total_remediation_hours'] > 0:
            recommendations.append(f"📊 Estimated {stats['total_remediation_hours']:.1f} hours for complete remediation.")
        
        return recommendations