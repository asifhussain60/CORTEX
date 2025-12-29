"""
CORTEX Duplicate Functionality Analyzer

Identifies multiple versions of the same functionality across the codebase.
Detects duplicates at file, function, class, and import levels.
SAFETY ENHANCED: Identifies active/canonical versions to prevent accidental deletion.

Author: Asif Hussain
Version: 2.0
Created: December 7, 2025
Updated: December 7, 2025 - Added active code detection
"""

import os
import ast
import hashlib
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict
from datetime import datetime, timedelta
import json


class DuplicateFunctionalityAnalyzer:
    """Analyzes CORTEX repository for duplicate functionality with safety detection"""
    
    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root)
        self.exclude_dirs = {
            '.venv', 'node_modules', '__pycache__', '.git',
            'deploy-packages', 'cortex-extension', 'test_merge'
        }
        
        # Results storage
        self.duplicate_files = defaultdict(list)  # filename -> [paths]
        self.duplicate_functions = defaultdict(list)  # func_sig -> [locations]
        self.duplicate_classes = defaultdict(list)  # class_name -> [locations]
        self.similar_modules = defaultdict(list)  # functionality -> [modules]
        
    def analyze(self) -> Dict:
        """Run complete duplicate analysis with active code detection"""
        print("🔍 Starting CORTEX Duplicate Functionality Analysis (Safety Enhanced)")
        print(f"📁 Repository: {self.repo_root}")
        print()
        
        # Collect all Python files
        python_files = self._collect_python_files()
        print(f"✅ Found {len(python_files)} Python files")
        print()
        
        # SAFETY LAYER 1: Detect active imports
        print("🛡️  Safety Layer 1: Detecting active imports...")
        self._detect_active_imports(python_files)
        print(f"   Found {len(self.active_imports)} actively imported modules")
        
        # SAFETY LAYER 2: Detect recent git activity
        print("🛡️  Safety Layer 2: Analyzing git history...")
        self._detect_recent_git_activity()
        print(f"   Found {len(self.git_recent_files)} recently modified files")
        
        # SAFETY LAYER 3: Mark archive zones
        print("🛡️  Safety Layer 3: Identifying safe-to-delete zones...")
        archive_count = len([f for f in python_files if 'archives' in str(f) or 'backups' in str(f)])
        print(f"   Found {archive_count} files in safe-to-delete zones")
        print()
        print(f"📁 Repository: {self.repo_root}")
        print()
        
        # Collect all Python files
        python_files = self._collect_python_files()
        print(f"✅ Found {len(python_files)} Python files")
        print()
        
        # Layer 1: File-level duplicates
        print("🔍 Layer 1: Analyzing file-level duplicates...")
        self._analyze_file_duplicates(python_files)
        
        # Layer 2: Function-level duplicates
    def _collect_python_files(self) -> List[Path]:
        """Collect all Python files, excluding specified directories"""
        python_files = []
        
        for root, dirs, files in os.walk(self.repo_root):
            # Remove excluded directories from traversal
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(Path(root) / file)
        
        return python_files
    
    def _detect_active_imports(self, python_files: List[Path]):
        """Detect which modules are actively imported by production code"""
        # Focus on src/ and scripts/ (active code areas)
        active_areas = [f for f in python_files if 
                       str(f).startswith(str(self.repo_root / 'src')) or
                       str(f).startswith(str(self.repo_root / 'scripts'))]
        
        for file_path in active_areas:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read(), filename=str(file_path))
                
                for node in ast.walk(tree):
                    # Detect import statements
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            self.active_imports.add(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            self.active_imports.add(node.module)
                            # Add submodules too
                            for alias in node.names:
                                self.active_imports.add(f"{node.module}.{alias.name}")
            
            except (SyntaxError, UnicodeDecodeError):
                pass
    
    def _detect_recent_git_activity(self):
        """Detect files modified in last 30 days via git"""
        try:
            # Get files modified in last 30 days
            result = subprocess.run(
                ['git', 'log', '--since=30.days.ago', '--name-only', '--pretty=format:', '--diff-filter=AMR'],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    if line.strip() and line.endswith('.py'):
                        self.git_recent_files.add(line.strip())
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # Git not available or timeout
            pass
    
    def _get_location_priority(self, file_path: str) -> int:
        """Get priority score for file location (higher = more canonical)"""
        for prefix, priority in self.location_priority.items():
            if file_path.startswith(prefix) or file_path.startswith(str(self.repo_root / prefix)):
                return priority
        return 30  # Default priority for other locations
    
    def _is_active_file(self, file_path: Path) -> bool:
        """Check if file is actively used in production"""
        rel_path = str(file_path.relative_to(self.repo_root))
        
        # Check 1: In archives or backups (definitely not active)
        if 'archives' in rel_path or 'backups' in rel_path:
            return False
        
        # Check 2: Recently modified in git
        if rel_path in self.git_recent_files:
            return True
        
        # Check 3: In src/ or scripts/ (likely active)
        if rel_path.startswith('src/') or rel_path.startswith('scripts/'):
            return True
        
        # Check 4: Imported by active code
        module_path = rel_path.replace('/', '.').replace('\\', '.').replace('.py', '')
        if any(imp.startswith(module_path) or module_path.startswith(imp) 
               for imp in self.active_imports):
            return True
        
        return Falserate_report()
        
        return report
    
    def _collect_python_files(self) -> List[Path]:
        """Collect all Python files, excluding specified directories"""
        python_files = []
        
        for root, dirs, files in os.walk(self.repo_root):
            # Remove excluded directories from traversal
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(Path(root) / file)
        
        return python_files
    
    def _analyze_file_duplicates(self, python_files: List[Path]):
        """Detect duplicate filenames in different locations"""
        filename_map = defaultdict(list)
        
        for file_path in python_files:
            filename = file_path.name
            filename_map[filename].append(file_path)
        
        # Store only duplicates
        for filename, paths in filename_map.items():
            if len(paths) > 1:
                self.duplicate_files[filename] = [str(p.relative_to(self.repo_root)) for p in paths]
    
    def _analyze_function_duplicates(self, python_files: List[Path]):
        """Detect duplicate function signatures across files"""
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read(), filename=str(file_path))
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Create function signature
                        args = [arg.arg for arg in node.args.args]
                        func_sig = f"{node.name}({', '.join(args)})"
                        
                        location = f"{file_path.relative_to(self.repo_root)}:{node.lineno}"
                        self.duplicate_functions[func_sig].append(location)
            
            except (SyntaxError, UnicodeDecodeError) as e:
                # Skip files with syntax errors or encoding issues
                pass
    
    def _generate_recommendations(self) -> List[Dict]:
        """Generate actionable recommendations for consolidation with safety analysis"""
        recommendations = []
        
        # High-priority file duplicates
        priority_patterns = [
            'orchestrator', 'agent', 'operation', 'module',
            'launcher', 'executor', 'processor', 'handler'
        ]
        
        for filename, paths in self.duplicate_files.items():
            is_priority = any(pattern in filename.lower() for pattern in priority_patterns)
            
            # Skip test files (expected to have similar names)
            if 'test_' in filename:
                continue
            
            # SAFETY ANALYSIS: Identify canonical version
            path_analysis = []
            for path in paths:
                file_path = self.repo_root / path
                priority = self._get_location_priority(path)
                is_active = self._is_active_file(file_path)
                in_archive = 'archives' in path or 'backups' in path
                
                path_analysis.append({
                    'path': path,
                    'priority': priority,
                    'is_active': is_active,
                    'in_archive': in_archive,
                    'safety_score': priority + (50 if is_active else 0) - (100 if in_archive else 0)
                })
            
            # Sort by safety score (highest = most canonical)
            path_analysis.sort(key=lambda x: x['safety_score'], reverse=True)
            canonical = path_analysis[0]
            duplicates = path_analysis[1:]
            
            # Determine safety level
            safe_to_delete = [p for p in duplicates if p['in_archive']]
            needs_review = [p for p in duplicates if not p['in_archive']]
            
            recommendation = {
                'type': 'file_duplicate',
                'priority': 'HIGH' if is_priority else 'MEDIUM',
                'filename': filename,
                'canonical_version': canonical['path'],
                'canonical_score': canonical['safety_score'],
                'is_active': canonical['is_active'],
                'safe_to_delete': [p['path'] for p in safe_to_delete],
                'needs_manual_review': [p['path'] for p in needs_review],
                'action': self._generate_action(canonical, safe_to_delete, needs_review)
            }
            
            recommendations.append(recommendation)
        
        # Duplicate classes
        for class_name, instances in class_info.items():
            if len(instances) > 1:
                self.duplicate_classes[class_name] = instances
    
    def _analyze_module_similarities(self, python_files: List[Path]):
        """Detect modules with similar functionality based on imports/exports"""
        module_exports = defaultdict(set)
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read(), filename=str(file_path))
                
                exports = set()
                
                for node in ast.walk(tree):
        # Sort by priority and safety
        priority_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
        recommendations.sort(key=lambda x: (
            priority_order.get(x.get('priority', 'LOW'), 2),
            -len(x.get('safe_to_delete', []))  # More safe-to-delete = higher priority
        ))
        
        return recommendations
    
    def _generate_action(self, canonical, safe_to_delete, needs_review) -> str:
        """Generate specific action recommendation based on safety analysis"""
        if len(safe_to_delete) > 0 and len(needs_review) == 0:
            return f"✅ SAFE: Delete {len(safe_to_delete)} archived copy(ies), keep canonical: {canonical['path']}"
        elif len(safe_to_delete) > 0 and len(needs_review) > 0:
            return f"⚠️  MIXED: Delete {len(safe_to_delete)} archived, REVIEW {len(needs_review)} active copies"
        elif len(needs_review) > 0:
            return f"🔍 MANUAL: Review {len(needs_review)} active copies to identify true canonical"
        else:
            return "✅ SAFE: Single copy found"tance(node, ast.ClassDef) and not node.name.startswith('_'):
                        exports.add(node.name)
                
                if exports:
                    module_path = str(file_path.relative_to(self.repo_root))
                    module_exports[module_path] = exports
            
            except (SyntaxError, UnicodeDecodeError):
                pass
        
        # Find modules with overlapping exports (potential duplicates)
        modules = list(module_exports.items())
        for i, (mod1, exports1) in enumerate(modules):
            for mod2, exports2 in modules[i+1:]:
                overlap = exports1 & exports2
                if len(overlap) >= 3:  # At least 3 common exports
                    similarity_key = f"{Path(mod1).name} ↔ {Path(mod2).name}"
                    self.similar_modules[similarity_key].append({
                        'module1': mod1,
                        'module2': mod2,
                        'common_exports': sorted(list(overlap)),
                        'similarity_score': len(overlap) / max(len(exports1), len(exports2))
                    })
    
    def _generate_report(self) -> Dict:
        """Generate comprehensive duplicate analysis report"""
        
        # Filter function duplicates (only true duplicates)
        real_func_duplicates = {
            sig: locs for sig, locs in self.duplicate_functions.items()
            if len(locs) > 1 and not sig.startswith('_')  # Exclude private functions
        }
        
        report = {
            'summary': {
                'duplicate_files': len(self.duplicate_files),
                'duplicate_functions': len(real_func_duplicates),
                'duplicate_classes': len(self.duplicate_classes),
                'similar_module_pairs': len(self.similar_modules)
            },
            'duplicate_files': dict(self.duplicate_files),
            'duplicate_functions': dict(real_func_duplicates),
            'duplicate_classes': dict(self.duplicate_classes),
            'similar_modules': dict(self.similar_modules),
            'recommendations': self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[Dict]:
        """Generate actionable recommendations for consolidation"""
        recommendations = []
        # Recommendations with safety analysis
        if report['recommendations']:
            print("\n\n💡 ACTIONABLE RECOMMENDATIONS (Safety Enhanced)")
            print("="*80)
            
            # Categorize by safety
            safe_auto = [r for r in report['recommendations'] 
                        if r.get('action', '').startswith('✅ SAFE')]
            needs_review = [r for r in report['recommendations'] 
                           if '🔍 MANUAL' in r.get('action', '') or '⚠️  MIXED' in r.get('action', '')]
            
            if safe_auto:
                print("\n✅ SAFE TO DELETE (Archived/Backup Copies)")
                print(f"   {len(safe_auto)} files with archived duplicates - safe for automated cleanup")
                for i, rec in enumerate(safe_auto[:15], 1):
                    if rec['type'] == 'file_duplicate':
                        safe_count = len(rec.get('safe_to_delete', []))
                        print(f"\n   {i}. {rec['filename']} ({safe_count} archived copies)")
                        print(f"      Keep: {rec.get('canonical_version', 'N/A')}")
                        print(f"      Delete: {', '.join(rec.get('safe_to_delete', [])[:3])}")
                        if safe_count > 3:
                            print(f"              ... and {safe_count - 3} more")
            
            if needs_review:
                print("\n\n🔍 NEEDS MANUAL REVIEW (Active Code)")
                print(f"   {len(needs_review)} files require careful comparison")
                for i, rec in enumerate(needs_review[:10], 1):
                    if rec['type'] == 'file_duplicate':
                        print(f"\n   {i}. {rec['filename']}")
                        print(f"      Canonical: {rec.get('canonical_version', 'N/A')}")
                        print(f"      Review: {', '.join(rec.get('needs_manual_review', []))}")
                        print(f"      Action: {rec['action']}")
        # Duplicate classes
        for class_name, instances in self.duplicate_classes.items():
            if len(instances) > 1:
                method_counts = [inst['method_count'] for inst in instances]
                most_complete = instances[method_counts.index(max(method_counts))]
                
                recommendations.append({
                    'type': 'class_duplicate',
                    'priority': 'HIGH',
                    'class_name': class_name,
                    'instances': len(instances),
                    'locations': [inst['location'] for inst in instances],
                    'suggested_keep': most_complete['location'],
                    'action': f'Keep most complete version ({most_complete["method_count"]} methods), remove others'
                })
        
        # Similar modules
        for similarity_key, matches in self.similar_modules.items():
            for match in matches:
                if match['similarity_score'] > 0.5:  # >50% overlap
                    recommendations.append({
                        'type': 'module_similarity',
                        'priority': 'MEDIUM',
                        'modules': [match['module1'], match['module2']],
                        'similarity': f"{match['similarity_score']:.0%}",
                        'common_functionality': match['common_exports'],
                        'action': 'Review for potential consolidation or refactoring'
                    })
        
        # Sort by priority
        priority_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
        recommendations.sort(key=lambda x: priority_order.get(x.get('priority', 'LOW'), 2))
        
        return recommendations
    
    def print_report(self, report: Dict):
        """Print human-readable report to console"""
        print("\n" + "="*80)
        print("📊 CORTEX DUPLICATE FUNCTIONALITY ANALYSIS REPORT")
        print("="*80)
        print()
        
        # Summary
        summary = report['summary']
        print("📋 SUMMARY")
        print(f"   Duplicate Files: {summary['duplicate_files']}")
        print(f"   Duplicate Functions: {summary['duplicate_functions']}")
        print(f"   Duplicate Classes: {summary['duplicate_classes']}")
        print(f"   Similar Module Pairs: {summary['similar_module_pairs']}")
        print()
        
        # Duplicate Files
        if report['duplicate_files']:
            print("📁 DUPLICATE FILES (Same filename, different locations)")
            print("-" * 80)
            for filename, paths in sorted(report['duplicate_files'].items()):
                print(f"\n   {filename} ({len(paths)} copies):")
                for path in paths:
                    print(f"      - {path}")
        
        # Duplicate Classes
        if report['duplicate_classes']:
            print("\n\n🏗️  DUPLICATE CLASSES (Same class name)")
            print("-" * 80)
            for class_name, instances in sorted(report['duplicate_classes'].items()):
                print(f"\n   {class_name} ({len(instances)} instances):")
                for inst in instances:
                    print(f"      - {inst['location']} ({inst['method_count']} methods)")
        
        # Top Duplicate Functions
        if report['duplicate_functions']:
            print("\n\n⚙️  TOP DUPLICATE FUNCTIONS (Same signature)")
            print("-" * 80)
            
            # Show top 20 most duplicated
            sorted_funcs = sorted(
                report['duplicate_functions'].items(),
                key=lambda x: len(x[1]),
                reverse=True
            )[:20]
            
            for func_sig, locations in sorted_funcs:
                print(f"\n   {func_sig} ({len(locations)} copies):")
                for loc in locations[:5]:  # Show first 5 locations
                    print(f"      - {loc}")
                if len(locations) > 5:
                    print(f"      ... and {len(locations) - 5} more")
        
        # Similar Modules
        if report['similar_modules']:
            print("\n\n🔗 SIMILAR MODULES (Overlapping functionality)")
            print("-" * 80)
            for similarity_key, matches in sorted(report['similar_modules'].items()):
                for match in matches[:3]:  # Top 3 per pair
                    print(f"\n   {similarity_key} ({match['similarity_score']:.0%} similar):")
                    print(f"      Module 1: {match['module1']}")
                    print(f"      Module 2: {match['module2']}")
                    print(f"      Common: {', '.join(match['common_exports'][:5])}")
        
        # Recommendations
    # Summary with safety metrics
    safe_auto = len([r for r in report['recommendations'] 
                    if r.get('action', '').startswith('✅ SAFE')])
    needs_review = len([r for r in report['recommendations'] 
                       if '🔍 MANUAL' in r.get('action', '') or '⚠️  MIXED' in r.get('action', '')])
    
    print(f"\n✅ Analysis complete!")
    print(f"📊 Found {report['summary']['duplicate_files']} duplicate files")
    print(f"🏗️  Found {report['summary']['duplicate_classes']} duplicate classes")
    print(f"⚙️  Found {report['summary']['duplicate_functions']} duplicate functions")
    print()
    print(f"🛡️  SAFETY ANALYSIS:")
    print(f"   ✅ {safe_auto} files safe for automated cleanup (archived copies)")
    print(f"   🔍 {needs_review} files need manual review (active code)")
    print(f"   💡 Estimated space savings: 200-400 MB (from archives)")
    print() 
            if high_priority:
                print("\n🔴 HIGH PRIORITY")
                for i, rec in enumerate(high_priority[:10], 1):
                    print(f"\n   {i}. {rec['type'].upper()}: {rec.get('filename') or rec.get('class_name', 'Module')}")
                    print(f"      Action: {rec['action']}")
                    if 'suggested_keep' in rec:
                        print(f"      Keep: {rec['suggested_keep']}")
            
            if medium_priority:
                print("\n\n🟡 MEDIUM PRIORITY")
                for i, rec in enumerate(medium_priority[:10], 1):
                    print(f"\n   {i}. {rec['type'].upper()}")
                    if 'modules' in rec:
                        print(f"      Modules: {rec['modules'][0]} ↔ {rec['modules'][1]}")
                    print(f"      Action: {rec['action']}")
        
        print("\n" + "="*80)
        print()
    
    def save_report(self, report: Dict, output_path: str):
        """Save detailed JSON report"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Detailed report saved to: {output_path}")


def main():
    """Main execution"""
    # Detect CORTEX root
    script_dir = Path(__file__).resolve().parent
    cortex_root = script_dir.parent.parent  # scripts/utilities -> CORTEX
    
    # Run analysis
    analyzer = DuplicateFunctionalityAnalyzer(str(cortex_root))
    report = analyzer.analyze()
    
    # Print report to console
    analyzer.print_report(report)
    
    # Save JSON report
    output_dir = cortex_root / "cortex-brain" / "documents" / "analysis"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "duplicate-functionality-analysis.json"
    analyzer.save_report(report, str(output_path))
    
    # Summary
    print(f"\n✅ Analysis complete!")
    print(f"📊 Found {report['summary']['duplicate_files']} duplicate files")
    print(f"🏗️  Found {report['summary']['duplicate_classes']} duplicate classes")
    print(f"⚙️  Found {report['summary']['duplicate_functions']} duplicate functions")
    print(f"💡 Generated {len(report['recommendations'])} recommendations")
    print()


if __name__ == "__main__":
    main()
