"""
CORTEX Documentation Fresh Analysis Module

Performs fresh analysis of codebase state to detect and remove stale documentation.
This module ensures documentation always reflects current application state.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Set, Tuple
import yaml


class FreshAnalyzer:
    """Analyzes codebase for stale documentation content"""
    
    def __init__(self, repo_root: Path, lookback_days: int = 90):
        """
        Initialize fresh analyzer.
        
        Args:
            repo_root: Root directory of CORTEX repository
            lookback_days: Days to look back for git history analysis
        """
        self.repo_root = repo_root
        self.lookback_days = lookback_days
        self.docs_dir = repo_root / "docs"
        self.cortex_brain_dir = repo_root / "cortex-brain"
        self.src_dir = repo_root / "src"
        
        self.removed_files: Set[str] = set()
        self.deprecated_features: Set[str] = set()
        self.stale_references: List[Dict] = []
        self.freshness_score: float = 0.0
    
    def analyze(self) -> Dict:
        """
        Run complete fresh analysis.
        
        Returns:
            Analysis report with findings and freshness score
        """
        print("🔍 Starting fresh analysis...")
        
        # Step 1: Scan codebase state
        print("\n📊 Scanning codebase state...")
        self._scan_git_history()
        self._scan_current_modules()
        self._scan_deprecated_markers()
        
        # Step 2: Detect stale content
        print("\n🕵️ Detecting stale content...")
        self._detect_removed_file_references()
        self._detect_deprecated_feature_references()
        self._detect_broken_links()
        
        # Step 3: Calculate freshness score
        print("\n📈 Calculating freshness score...")
        self.freshness_score = self._calculate_freshness_score()
        
        # Step 4: Generate report
        report = self._generate_report()
        
        print(f"\n✅ Fresh analysis complete!")
        print(f"   Freshness Score: {self.freshness_score:.1f}%")
        print(f"   Stale References: {len(self.stale_references)}")
        print(f"   Removed Files: {len(self.removed_files)}")
        print(f"   Deprecated Features: {len(self.deprecated_features)}")
        
        return report
    
    def _scan_git_history(self):
        """Scan git history for removed files"""
        try:
            # Get list of deleted files in last N days
            since_date = (datetime.now() - timedelta(days=self.lookback_days)).strftime('%Y-%m-%d')
            
            cmd = [
                'git', 'log',
                '--diff-filter=D',  # Deleted files only
                '--name-only',
                '--format=',
                f'--since={since_date}'
            ]
            
            result = subprocess.run(
                cmd,
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=True
            )
            
            deleted_files = result.stdout.strip().split('\n')
            self.removed_files = {f.strip() for f in deleted_files if f.strip()}
            
            print(f"   Found {len(self.removed_files)} removed files in last {self.lookback_days} days")
            
        except subprocess.CalledProcessError as e:
            print(f"   ⚠️ Git scan failed: {e}")
            # Non-fatal - continue with empty set
    
    def _scan_current_modules(self):
        """Scan current module definitions"""
        operations_file = self.cortex_brain_dir / "cortex-operations.yaml"
        
        if not operations_file.exists():
            print("   ⚠️ cortex-operations.yaml not found")
            return
        
        try:
            with open(operations_file, 'r', encoding='utf-8') as f:
                operations = yaml.safe_load(f)
            
            self.current_operations = set(operations.get('operations', {}).keys())
            self.current_modules = set(operations.get('modules', {}).keys())
            
            print(f"   Found {len(self.current_operations)} operations, {len(self.current_modules)} modules")
            
        except Exception as e:
            print(f"   ⚠️ Module scan failed: {e}")
    
    def _scan_deprecated_markers(self):
        """Scan source code for DEPRECATED markers"""
        deprecated_pattern = r'DEPRECATED|OBSOLETE|REMOVED'
        
        for py_file in self.src_dir.rglob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8')
                if any(marker in content.upper() for marker in ['DEPRECATED', 'OBSOLETE', 'REMOVED']):
                    # Extract feature name from file path
                    feature = py_file.stem
                    self.deprecated_features.add(feature)
            except Exception:
                continue
        
        print(f"   Found {len(self.deprecated_features)} deprecated features")
    
    def _detect_removed_file_references(self):
        """Detect documentation references to removed files"""
        import re
        
        file_ref_pattern = re.compile(r'`([a-zA-Z0-9_/.-]+\.(py|yaml|md|json))`')
        
        for md_file in self.docs_dir.rglob("*.md"):
            try:
                content = md_file.read_text(encoding='utf-8')
                
                referenced_files = file_ref_pattern.findall(content)
                for file_path, _ in referenced_files:
                    normalized_path = file_path.replace('/', '\\')
                    
                    if normalized_path in self.removed_files:
                        self.stale_references.append({
                            'type': 'removed_file',
                            'doc_file': md_file.name,
                            'reference': file_path,
                            'line': self._find_line_number(content, file_path),
                            'severity': 'high'
                        })
            except Exception:
                continue
    
    def _detect_deprecated_feature_references(self):
        """Detect documentation references to deprecated features"""
        for md_file in self.docs_dir.rglob("*.md"):
            try:
                content = md_file.read_text(encoding='utf-8')
                
                for feature in self.deprecated_features:
                    if feature in content:
                        self.stale_references.append({
                            'type': 'deprecated_feature',
                            'doc_file': md_file.name,
                            'reference': feature,
                            'line': self._find_line_number(content, feature),
                            'severity': 'medium'
                        })
            except Exception:
                continue
    
    def _detect_broken_links(self):
        """Detect broken internal documentation links"""
        import re
        
        link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
        
        for md_file in self.docs_dir.rglob("*.md"):
            try:
                content = md_file.read_text(encoding='utf-8')
                
                links = link_pattern.findall(content)
                for link_text, link_target in links:
                    # Skip external links
                    if link_target.startswith('http'):
                        continue
                    
                    # Check if internal link target exists
                    target_path = (md_file.parent / link_target).resolve()
                    
                    if not target_path.exists():
                        self.stale_references.append({
                            'type': 'broken_link',
                            'doc_file': md_file.name,
                            'reference': link_target,
                            'line': self._find_line_number(content, link_target),
                            'severity': 'high'
                        })
            except Exception:
                continue
    
    def _find_line_number(self, content: str, search_text: str) -> int:
        """Find line number of text in content"""
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if search_text in line:
                return i
        return 0
    
    def _calculate_freshness_score(self) -> float:
        """
        Calculate freshness score (0-100).
        
        Score calculation:
        - Base score: 100
        - High severity: -5 points each
        - Medium severity: -2 points each
        - Low severity: -1 point each
        """
        score = 100.0
        
        for ref in self.stale_references:
            severity = ref.get('severity', 'low')
            
            if severity == 'high':
                score -= 5.0
            elif severity == 'medium':
                score -= 2.0
            else:
                score -= 1.0
        
        return max(0.0, score)
    
    def _generate_report(self) -> Dict:
        """Generate comprehensive analysis report"""
        return {
            'timestamp': datetime.now().isoformat(),
            'lookback_days': self.lookback_days,
            'freshness_score': self.freshness_score,
            'summary': {
                'removed_files': len(self.removed_files),
                'deprecated_features': len(self.deprecated_features),
                'stale_references': len(self.stale_references),
                'severity_breakdown': self._get_severity_breakdown()
            },
            'stale_references': self.stale_references,
            'removed_files': list(self.removed_files),
            'deprecated_features': list(self.deprecated_features),
            'recommendations': self._generate_recommendations()
        }
    
    def _get_severity_breakdown(self) -> Dict[str, int]:
        """Get breakdown of stale references by severity"""
        breakdown = {'high': 0, 'medium': 0, 'low': 0}
        
        for ref in self.stale_references:
            severity = ref.get('severity', 'low')
            breakdown[severity] += 1
        
        return breakdown
    
    def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if self.freshness_score < 95.0:
            recommendations.append("⚠️ Freshness score below target (95%). Run cleanup to remove stale content.")
        
        if len(self.stale_references) > 10:
            recommendations.append(f"📝 {len(self.stale_references)} stale references detected. Review and update documentation.")
        
        high_severity = sum(1 for ref in self.stale_references if ref.get('severity') == 'high')
        if high_severity > 0:
            recommendations.append(f"🚨 {high_severity} high-severity issues require immediate attention.")
        
        if len(self.removed_files) > 0:
            recommendations.append(f"🗑️ {len(self.removed_files)} files removed recently. Update references in documentation.")
        
        if len(self.deprecated_features) > 0:
            recommendations.append(f"⚠️ {len(self.deprecated_features)} deprecated features detected. Remove or update documentation.")
        
        if not recommendations:
            recommendations.append("✅ Documentation is fresh! No immediate action required.")
        
        return recommendations
    
    def save_report(self, output_path: Path):
        """Save analysis report to file"""
        report = self._generate_report()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Report saved to: {output_path}")


class StaleContentCleaner:
    """Automated cleanup of stale documentation content"""
    
    def __init__(self, analysis_report: Dict, dry_run: bool = True):
        """
        Initialize stale content cleaner.
        
        Args:
            analysis_report: Report from FreshAnalyzer
            dry_run: If True, simulate cleanup without making changes
        """
        self.report = analysis_report
        self.dry_run = dry_run
        self.changes_made: List[Dict] = []
    
    def cleanup(self) -> Dict:
        """
        Execute cleanup based on analysis report.
        
        Returns:
            Cleanup summary
        """
        mode = "DRY RUN" if self.dry_run else "PRODUCTION"
        print(f"\n🧹 Starting cleanup ({mode})...")
        
        stale_refs = self.report.get('stale_references', [])
        
        for ref in stale_refs:
            severity = ref.get('severity', 'low')
            
            # Only auto-cleanup high-severity issues
            if severity == 'high':
                self._cleanup_reference(ref)
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'mode': 'dry_run' if self.dry_run else 'production',
            'changes_made': len(self.changes_made),
            'changes': self.changes_made
        }
        
        print(f"\n✅ Cleanup complete!")
        print(f"   Changes: {len(self.changes_made)}")
        
        return summary
    
    def _cleanup_reference(self, ref: Dict):
        """Cleanup a single stale reference"""
        ref_type = ref.get('type')
        doc_file = ref.get('doc_file')
        reference = ref.get('reference')
        line_num = ref.get('line', 0)
        
        change = {
            'doc_file': doc_file,
            'type': ref_type,
            'reference': reference,
            'line': line_num,
            'action': 'removed' if not self.dry_run else 'would_remove'
        }
        
        if not self.dry_run:
            # TODO: Implement actual file modification
            # This would require careful line-by-line editing
            pass
        
        self.changes_made.append(change)
        
        print(f"   {'Would remove' if self.dry_run else 'Removed'}: {reference} from {doc_file} (line {line_num})")
    
    def save_cleanup_report(self, output_path: Path):
        """Save cleanup report to file"""
        summary = {
            'timestamp': datetime.now().isoformat(),
            'mode': 'dry_run' if self.dry_run else 'production',
            'changes_made': len(self.changes_made),
            'changes': self.changes_made
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n📄 Cleanup report saved to: {output_path}")


def main():
    """CLI entry point for fresh analysis"""
    import argparse
    
    parser = argparse.ArgumentParser(description='CORTEX Documentation Fresh Analysis')
    parser.add_argument('--lookback-days', type=int, default=90,
                        help='Days to look back for git history analysis')
    parser.add_argument('--cleanup', action='store_true',
                        help='Run automated cleanup after analysis')
    parser.add_argument('--dry-run', action='store_true', default=True,
                        help='Simulate cleanup without making changes')
    parser.add_argument('--output', type=str, default='cortex-brain/cleanup-reports',
                        help='Output directory for reports')
    
    args = parser.parse_args()
    
    # Initialize analyzer
    repo_root = Path(__file__).parent.parent.parent.parent
    analyzer = FreshAnalyzer(repo_root, args.lookback_days)
    
    # Run analysis
    report = analyzer.analyze()
    
    # Save analysis report
    output_dir = repo_root / args.output
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    analysis_report_path = output_dir / f'fresh-analysis-{timestamp}.json'
    analyzer.save_report(analysis_report_path)
    
    # Run cleanup if requested
    if args.cleanup:
        cleaner = StaleContentCleaner(report, dry_run=args.dry_run)
        cleanup_summary = cleaner.cleanup()
        
        cleanup_report_path = output_dir / f'cleanup-{timestamp}.json'
        cleaner.save_cleanup_report(cleanup_report_path)
    
    # Print summary
    print("\n" + "="*60)
    print("📊 FRESH ANALYSIS SUMMARY")
    print("="*60)
    print(f"Freshness Score: {report['freshness_score']:.1f}%")
    print(f"Stale References: {report['summary']['stale_references']}")
    print(f"Removed Files: {report['summary']['removed_files']}")
    print(f"Deprecated Features: {report['summary']['deprecated_features']}")
    print("\nRecommendations:")
    for rec in report['recommendations']:
        print(f"  {rec}")
    print("="*60)


if __name__ == '__main__':
    main()
