#!/usr/bin/env python3
"""
STS Baseline Comparison
Compares current validation results against baseline to detect regressions

Usage:
    python scripts/compare_to_baseline.py
    python scripts/compare_to_baseline.py --results path/to/results.json
    python scripts/compare_to_baseline.py --threshold 15
"""
import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

CORTEX_ROOT = Path(__file__).parent.parent
BASELINE_PATH = CORTEX_ROOT / "cortex-brain/sts-baseline.json"
RESULTS_DIR = CORTEX_ROOT / "cortex-brain/sts-results"


class BaselineComparator:
    """Compare STS validation results against baseline"""
    
    def __init__(self, baseline_path: Path, threshold: float = 10.0):
        self.baseline_path = baseline_path
        self.threshold = threshold  # Percentage deviation considered regression
        self.baseline = self._load_baseline()
    
    def _load_baseline(self) -> Dict:
        """Load baseline JSON"""
        if not self.baseline_path.exists():
            raise FileNotFoundError(f"Baseline not found: {self.baseline_path}")
        
        with open(self.baseline_path, 'r') as f:
            return json.load(f)
    
    def _load_results(self, results_path: Path) -> Dict:
        """Load validation results JSON"""
        if not results_path.exists():
            raise FileNotFoundError(f"Results not found: {results_path}")
        
        with open(results_path, 'r') as f:
            return json.load(f)
    
    def compare(self, results: Dict) -> Dict:
        """
        Compare results to baseline
        Returns: {'regressions': [], 'improvements': [], 'unchanged': [], 'summary': {}}
        """
        regressions = []
        improvements = []
        unchanged = []
        
        # Compare overall status
        baseline_status = self.baseline.get('overall', 'UNKNOWN')
        current_status = results.get('overall', 'UNKNOWN')
        
        if baseline_status == 'PASS' and current_status == 'FAIL':
            regressions.append({
                'type': 'overall_status',
                'baseline': baseline_status,
                'current': current_status,
                'severity': 'CRITICAL'
            })
        
        # Compare per-capability
        baseline_caps = {c['capability']: c for c in self.baseline.get('capabilities', [])}
        current_caps = {c['capability']: c for c in results.get('capabilities', [])}
        
        for cap_name in baseline_caps.keys():
            if cap_name not in current_caps:
                regressions.append({
                    'type': 'missing_capability',
                    'capability': cap_name,
                    'severity': 'HIGH'
                })
                continue
            
            baseline_cap = baseline_caps[cap_name]
            current_cap = current_caps[cap_name]
            
            # Compare status
            if baseline_cap['status'] == 'PASS' and current_cap['status'] == 'FAIL':
                regressions.append({
                    'type': 'capability_failure',
                    'capability': cap_name,
                    'baseline_status': 'PASS',
                    'current_status': 'FAIL',
                    'severity': 'HIGH',
                    'issues': current_cap.get('issues', [])
                })
            elif baseline_cap['status'] == 'FAIL' and current_cap['status'] == 'PASS':
                improvements.append({
                    'type': 'capability_fixed',
                    'capability': cap_name
                })
            
            # Compare metrics
            baseline_metrics = baseline_cap.get('metrics', {})
            current_metrics = current_cap.get('metrics', {})
            
            for metric_name, baseline_value in baseline_metrics.items():
                if metric_name not in current_metrics:
                    continue
                
                current_value = current_metrics[metric_name]
                
                # Skip non-numeric metrics
                if not isinstance(baseline_value, (int, float)) or not isinstance(current_value, (int, float)):
                    continue
                
                # Calculate deviation
                if baseline_value != 0:
                    deviation_pct = ((current_value - baseline_value) / baseline_value) * 100
                else:
                    deviation_pct = 0 if current_value == 0 else 100
                
                # Determine if regression (context-dependent)
                is_regression = False
                severity = 'LOW'
                
                # Metrics where higher is worse
                if metric_name in ['build_time', 'upgrade_time', 'switch_latency_ms', 
                                   'avg_latency_ms', 'brain_query_ms', 'large_codebase_time']:
                    if deviation_pct > self.threshold:
                        is_regression = True
                        severity = 'MEDIUM' if deviation_pct < 25 else 'HIGH'
                
                # Metrics where lower is worse
                elif metric_name in ['context_isolation', 'data_preservation', 'confidence']:
                    if deviation_pct < -self.threshold:
                        is_regression = True
                        severity = 'MEDIUM' if abs(deviation_pct) < 25 else 'HIGH'
                
                if is_regression:
                    regressions.append({
                        'type': 'metric_regression',
                        'capability': cap_name,
                        'metric': metric_name,
                        'baseline': baseline_value,
                        'current': current_value,
                        'deviation_pct': deviation_pct,
                        'severity': severity
                    })
                elif abs(deviation_pct) > self.threshold:
                    # Improvement detected
                    improvements.append({
                        'type': 'metric_improvement',
                        'capability': cap_name,
                        'metric': metric_name,
                        'baseline': baseline_value,
                        'current': current_value,
                        'improvement_pct': abs(deviation_pct)
                    })
                else:
                    unchanged.append({
                        'capability': cap_name,
                        'metric': metric_name,
                        'deviation_pct': deviation_pct
                    })
        
        summary = {
            'total_regressions': len(regressions),
            'total_improvements': len(improvements),
            'total_unchanged': len(unchanged),
            'critical_regressions': sum(1 for r in regressions if r.get('severity') == 'CRITICAL'),
            'high_regressions': sum(1 for r in regressions if r.get('severity') == 'HIGH'),
            'medium_regressions': sum(1 for r in regressions if r.get('severity') == 'MEDIUM'),
            'overall_verdict': 'REGRESSION' if regressions else 'STABLE'
        }
        
        return {
            'timestamp': datetime.now().isoformat(),
            'baseline_file': str(self.baseline_path),
            'threshold': self.threshold,
            'regressions': regressions,
            'improvements': improvements,
            'unchanged': unchanged,
            'summary': summary
        }
    
    def print_report(self, comparison: Dict):
        """Print comparison report to console"""
        print(f"\n{'='*70}")
        print(f"📊 STS BASELINE COMPARISON REPORT")
        print(f"{'='*70}")
        print(f"Baseline: {self.baseline_path.name}")
        print(f"Threshold: ±{self.threshold}%")
        print(f"Timestamp: {comparison['timestamp']}")
        
        summary = comparison['summary']
        print(f"\n🎯 SUMMARY")
        print(f"  Overall Verdict: {summary['overall_verdict']}")
        print(f"  Total Regressions: {summary['total_regressions']}")
        print(f"    - Critical: {summary['critical_regressions']}")
        print(f"    - High: {summary['high_regressions']}")
        print(f"    - Medium: {summary['medium_regressions']}")
        print(f"  Total Improvements: {summary['total_improvements']}")
        print(f"  Unchanged: {summary['total_unchanged']}")
        
        # Print regressions
        if comparison['regressions']:
            print(f"\n⚠️  REGRESSIONS DETECTED")
            print(f"{'='*70}")
            for reg in comparison['regressions']:
                severity_icon = {'CRITICAL': '🔴', 'HIGH': '🟠', 'MEDIUM': '🟡', 'LOW': '🟢'}
                icon = severity_icon.get(reg['severity'], '⚪')
                
                if reg['type'] == 'overall_status':
                    print(f"{icon} Overall status changed: {reg['baseline']} → {reg['current']}")
                elif reg['type'] == 'capability_failure':
                    print(f"{icon} {reg['capability']}: PASS → FAIL")
                    if reg.get('issues'):
                        for issue in reg['issues']:
                            print(f"     - {issue}")
                elif reg['type'] == 'metric_regression':
                    print(f"{icon} {reg['capability']}.{reg['metric']}: {reg['baseline']:.2f} → {reg['current']:.2f} ({reg['deviation_pct']:+.1f}%)")
        
        # Print improvements
        if comparison['improvements']:
            print(f"\n✨ IMPROVEMENTS DETECTED")
            print(f"{'='*70}")
            for imp in comparison['improvements']:
                if imp['type'] == 'capability_fixed':
                    print(f"✅ {imp['capability']}: FAIL → PASS")
                elif imp['type'] == 'metric_improvement':
                    print(f"📈 {imp['capability']}.{imp['metric']}: {imp['baseline']:.2f} → {imp['current']:.2f} ({imp['improvement_pct']:+.1f}%)")
    
    def save_report(self, comparison: Dict, output_path: Path):
        """Save comparison report to JSON"""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(comparison, f, indent=2)
        
        print(f"\n💾 Comparison report saved: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='STS Baseline Comparison')
    parser.add_argument('--baseline', type=str,
                       help='Path to baseline JSON (default: cortex-brain/sts-baseline.json)')
    parser.add_argument('--results', type=str,
                       help='Path to validation results JSON (default: latest in sts-results/)')
    parser.add_argument('--threshold', type=float, default=10.0,
                       help='Regression threshold percentage (default: 10.0)')
    parser.add_argument('--output', type=str,
                       help='Output path for comparison report')
    
    args = parser.parse_args()
    
    # Resolve baseline path
    baseline_path = Path(args.baseline) if args.baseline else BASELINE_PATH
    if not baseline_path.is_absolute():
        baseline_path = CORTEX_ROOT / baseline_path
    
    # Resolve results path (use latest if not specified)
    if args.results:
        results_path = Path(args.results)
        if not results_path.is_absolute():
            results_path = CORTEX_ROOT / results_path
    else:
        # Find latest results file
        if not RESULTS_DIR.exists():
            print(f"❌ Results directory not found: {RESULTS_DIR}")
            return 1
        
        results_files = sorted(RESULTS_DIR.glob('*.json'), reverse=True)
        if not results_files:
            print(f"❌ No results files found in {RESULTS_DIR}")
            return 1
        
        results_path = results_files[0]
        print(f"📄 Using latest results: {results_path.name}")
    
    # Initialize comparator
    try:
        comparator = BaselineComparator(baseline_path, args.threshold)
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        return 1
    
    # Load results and compare
    try:
        results = comparator._load_results(results_path)
        comparison = comparator.compare(results)
    except Exception as e:
        print(f"❌ Comparison failed: {e}")
        return 1
    
    # Print report
    comparator.print_report(comparison)
    
    # Save report if requested
    if args.output:
        output_path = Path(args.output)
        if not output_path.is_absolute():
            output_path = CORTEX_ROOT / output_path
    else:
        timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M')
        output_path = RESULTS_DIR / f"{timestamp}-comparison.json"
    
    comparator.save_report(comparison, output_path)
    
    # Exit code based on verdict
    return 1 if comparison['summary']['overall_verdict'] == 'REGRESSION' else 0


if __name__ == '__main__':
    sys.exit(main())
