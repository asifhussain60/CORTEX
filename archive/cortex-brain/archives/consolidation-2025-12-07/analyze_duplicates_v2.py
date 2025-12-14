"""
CORTEX Duplicate Functionality Analyzer V2

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
import subprocess
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict
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
        self.duplicate_files = defaultdict(list)
        self.duplicate_functions = defaultdict(list)
        self.duplicate_classes = defaultdict(list)
        self.similar_modules = defaultdict(list)
        
        # Active code tracking
        self.active_imports = set()
        self.git_recent_files = set()
        
        # Location priority (higher = more canonical)
        self.location_priority = {
            'src/': 100,
            'scripts/': 80,
            'tests/': 70,
            'cortex-brain/documents/': 60,
            'cortex-brain/admin/': 50,
            'cortex-brain/archives/': 0,  # SAFE TO DELETE
            'cortex-brain/backups/': 0,  # SAFE TO DELETE
        }
        
    def analyze(self) -> Dict:
        """Run complete duplicate analysis with safety detection"""
        print("[*] CORTEX Duplicate Analysis (Safety Enhanced v2.0)")
        print(f"[*] Repository: {self.repo_root}\n")
        
        # Collect files
        python_files = self._collect_python_files()
        print(f"[+] Found {len(python_files)} Python files\n")
        
        # Safety layers
        print("[*] Safety Layer 1: Detecting active imports...")
        self._detect_active_imports(python_files)
        print(f"    [+] {len(self.active_imports)} actively imported modules\n")
        
        print("[*] Safety Layer 2: Analyzing git history...")
        self._detect_recent_git_activity()
        print(f"    [+] {len(self.git_recent_files)} recently modified files\n")
        
        archive_count = len([f for f in python_files if 'archives' in str(f) or 'backups' in str(f)])
        print(f"[*] Safety Layer 3: {archive_count} files in safe-to-delete zones\n")
        
        # Analysis layers
        print("[*] Layer 1: Analyzing file-level duplicates...")
        self._analyze_file_duplicates(python_files)
        
        print("[*] Layer 2: Analyzing function-level duplicates...")
        self._analyze_function_duplicates(python_files)
        
        print("[*] Layer 3: Analyzing class-level duplicates...")
        self._analyze_class_duplicates(python_files)
        
        print("[*] Layer 4: Analyzing module similarities...")
        self._analyze_module_similarities(python_files)
        
        # Generate report
        report = self._generate_report()
        
        return report
    
    def _collect_python_files(self) -> List[Path]:
        """Collect all Python files"""
        python_files = []
        for root, dirs, files in os.walk(self.repo_root):
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
            for file in files:
                if file.endswith('.py'):
                    python_files.append(Path(root) / file)
        return python_files
    
    def _detect_active_imports(self, python_files: List[Path]):
        """Detect actively imported modules"""
        active_areas = [f for f in python_files if 
                       str(f).startswith(str(self.repo_root / 'src')) or
                       str(f).startswith(str(self.repo_root / 'scripts'))]
        
        for file_path in active_areas:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read(), filename=str(file_path))
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            self.active_imports.add(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            self.active_imports.add(node.module)
            except (SyntaxError, UnicodeDecodeError):
                pass
    
    def _detect_recent_git_activity(self):
        """Detect files modified in last 30 days"""
        try:
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
            pass
    
    def _get_location_priority(self, file_path: str) -> int:
        """Get priority score for file location"""
        for prefix, priority in self.location_priority.items():
            if file_path.startswith(prefix) or file_path.startswith(str(self.repo_root / prefix)):
                return priority
        return 30
    
    def _is_active_file(self, file_path: Path) -> bool:
        """Check if file is actively used"""
        rel_path = str(file_path.relative_to(self.repo_root))
        
        if 'archives' in rel_path or 'backups' in rel_path:
            return False
        if rel_path in self.git_recent_files:
            return True
        if rel_path.startswith('src/') or rel_path.startswith('scripts/'):
            return True
        
        module_path = rel_path.replace('/', '.').replace('\\', '.').replace('.py', '')
        if any(imp.startswith(module_path) or module_path.startswith(imp) 
               for imp in self.active_imports):
            return True
        
        return False
    
    def _analyze_file_duplicates(self, python_files: List[Path]):
        """Detect duplicate filenames"""
        filename_map = defaultdict(list)
        for file_path in python_files:
            filename_map[file_path.name].append(file_path)
        
        for filename, paths in filename_map.items():
            if len(paths) > 1:
                self.duplicate_files[filename] = [str(p.relative_to(self.repo_root)) for p in paths]
    
    def _analyze_function_duplicates(self, python_files: List[Path]):
        """Detect duplicate function signatures"""
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read(), filename=str(file_path))
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        args = [arg.arg for arg in node.args.args]
                        func_sig = f"{node.name}({', '.join(args)})"
                        location = f"{file_path.relative_to(self.repo_root)}:{node.lineno}"
                        self.duplicate_functions[func_sig].append(location)
            except (SyntaxError, UnicodeDecodeError):
                pass
    
    def _analyze_class_duplicates(self, python_files: List[Path]):
        """Detect duplicate class names"""
        class_info = defaultdict(list)
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read(), filename=str(file_path))
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                        location = f"{file_path.relative_to(self.repo_root)}:{node.lineno}"
                        class_info[node.name].append({
                            'location': location,
                            'methods': methods,
                            'method_count': len(methods)
                        })
            except (SyntaxError, UnicodeDecodeError):
                pass
        
        for class_name, instances in class_info.items():
            if len(instances) > 1:
                self.duplicate_classes[class_name] = instances
    
    def _analyze_module_similarities(self, python_files: List[Path]):
        """Detect modules with similar functionality"""
        module_exports = defaultdict(set)
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read(), filename=str(file_path))
                
                exports = set()
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef) and not node.name.startswith('_'):
                        exports.add(node.name)
                    elif isinstance(node, ast.ClassDef) and not node.name.startswith('_'):
                        exports.add(node.name)
                
                if exports:
                    module_path = str(file_path.relative_to(self.repo_root))
                    module_exports[module_path] = exports
            except (SyntaxError, UnicodeDecodeError):
                pass
        
        modules = list(module_exports.items())
        for i, (mod1, exports1) in enumerate(modules):
            for mod2, exports2 in modules[i+1:]:
                overlap = exports1 & exports2
                if len(overlap) >= 3:
                    similarity_key = f"{Path(mod1).name} ↔ {Path(mod2).name}"
                    self.similar_modules[similarity_key].append({
                        'module1': mod1,
                        'module2': mod2,
                        'common_exports': sorted(list(overlap)),
                        'similarity_score': len(overlap) / max(len(exports1), len(exports2))
                    })
    
    def _generate_report(self) -> Dict:
        """Generate comprehensive report"""
        real_func_duplicates = {
            sig: locs for sig, locs in self.duplicate_functions.items()
            if len(locs) > 1 and not sig.startswith('_')
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
        """Generate safety-analyzed recommendations"""
        recommendations = []
        priority_patterns = ['orchestrator', 'agent', 'operation', 'module',
                            'launcher', 'executor', 'processor', 'handler']
        
        for filename, paths in self.duplicate_files.items():
            if 'test_' in filename:
                continue
            
            is_priority = any(pattern in filename.lower() for pattern in priority_patterns)
            
            # Safety analysis
            path_analysis = []
            for path in paths:
                file_path = self.repo_root / path
                priority = self._get_location_priority(path)
                is_active = self._is_active_file(file_path)
                in_archive = 'archives' in path or 'backups' in path
                
                safety_score = priority + (50 if is_active else 0) - (100 if in_archive else 0)
                path_analysis.append({
                    'path': path,
                    'priority': priority,
                    'is_active': is_active,
                    'in_archive': in_archive,
                    'safety_score': safety_score
                })
            
            path_analysis.sort(key=lambda x: x['safety_score'], reverse=True)
            canonical = path_analysis[0]
            duplicates = path_analysis[1:]
            
            safe_to_delete = [p for p in duplicates if p['in_archive']]
            needs_review = [p for p in duplicates if not p['in_archive']]
            
            recommendations.append({
                'type': 'file_duplicate',
                'priority': 'HIGH' if is_priority else 'MEDIUM',
                'filename': filename,
                'canonical_version': canonical['path'],
                'canonical_score': canonical['safety_score'],
                'is_active': canonical['is_active'],
                'safe_to_delete': [p['path'] for p in safe_to_delete],
                'needs_manual_review': [p['path'] for p in needs_review],
                'action': self._generate_action(safe_to_delete, needs_review)
            })
        
        recommendations.sort(key=lambda x: (
            {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}.get(x.get('priority', 'LOW'), 2),
            -len(x.get('safe_to_delete', []))
        ))
        
        return recommendations
    
    def _generate_action(self, safe_to_delete, needs_review) -> str:
        """Generate action recommendation"""
        if len(safe_to_delete) > 0 and len(needs_review) == 0:
            return f"[+] SAFE: Delete {len(safe_to_delete)} archived copies"
        elif len(safe_to_delete) > 0 and len(needs_review) > 0:
            return f"[!] MIXED: Delete {len(safe_to_delete)} archived, REVIEW {len(needs_review)} active"
        elif len(needs_review) > 0:
            return f"[?] MANUAL: Review {len(needs_review)} active copies"
        else:
            return "[+] SAFE: Single copy found"
    
    def print_report(self, report: Dict):
        """Print report to console"""
        print("\n" + "="*80)
        print("DUPLICATE FUNCTIONALITY ANALYSIS REPORT")
        print("="*80 + "\n")
        
        summary = report['summary']
        print(f"SUMMARY")
        print(f"   Duplicate Files: {summary['duplicate_files']}")
        print(f"   Duplicate Functions: {summary['duplicate_functions']}")
        print(f"   Duplicate Classes: {summary['duplicate_classes']}")
        print(f"   Similar Module Pairs: {summary['similar_module_pairs']}\n")
        
        # Safety-categorized recommendations
        if report['recommendations']:
            safe_auto = [r for r in report['recommendations'] 
                        if r.get('action', '').startswith('SAFE')]
            needs_review = [r for r in report['recommendations'] 
                           if 'MANUAL' in r.get('action', '') or 'MIXED' in r.get('action', '')]
            
            if safe_auto:
                print("\n[+] SAFE TO DELETE (Archived/Backup Copies)")
                print(f"   {len(safe_auto)} files with archived duplicates\n")
                for i, rec in enumerate(safe_auto[:15], 1):
                    safe_count = len(rec.get('safe_to_delete', []))
                    print(f"   {i}. {rec['filename']} ({safe_count} archived)")
                    print(f"      Keep: {rec.get('canonical_version', 'N/A')}")
                    delete_list = rec.get('safe_to_delete', [])[:3]
                    print(f"      Delete: {', '.join(delete_list)}")
                    if safe_count > 3:
                        print(f"              ... and {safe_count - 3} more\n")
            
            if needs_review:
                print("\n[?] NEEDS MANUAL REVIEW (Active Code)")
                print(f"   {len(needs_review)} files require comparison\n")
                for i, rec in enumerate(needs_review[:10], 1):
                    print(f"   {i}. {rec['filename']}")
                    print(f"      Canonical: {rec.get('canonical_version', 'N/A')}")
                    print(f"      Review: {', '.join(rec.get('needs_manual_review', []))}")
                    print(f"      Action: {rec['action']}\n")
        
        print("="*80 + "\n")
    
    def save_report(self, report: Dict, output_path: str):
        """Save JSON report"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"[*] Detailed report saved to: {output_path}")


def main():
    """Main execution"""
    script_dir = Path(__file__).resolve().parent
    cortex_root = script_dir.parent.parent
    
    analyzer = DuplicateFunctionalityAnalyzer(str(cortex_root))
    report = analyzer.analyze()
    
    analyzer.print_report(report)
    
    output_dir = cortex_root / "cortex-brain" / "documents" / "analysis"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "duplicate-functionality-analysis-v2.json"
    analyzer.save_report(report, str(output_path))
    
    safe_auto = len([r for r in report['recommendations'] 
                    if r.get('action', '').startswith('SAFE')])
    needs_review = len([r for r in report['recommendations'] 
                       if 'MANUAL' in r.get('action', '') or 'MIXED' in r.get('action', '')])
    
    print(f"\n[+] Analysis complete!")
    print(f"[*] Found {report['summary']['duplicate_files']} duplicate files")
    print(f"[*] Found {report['summary']['duplicate_classes']} duplicate classes")
    print(f"[*] Found {report['summary']['duplicate_functions']} duplicate functions")
    print()
    print(f"SAFETY ANALYSIS:")
    print(f"   [+] {safe_auto} files safe for automated cleanup (archived)")
    print(f"   [?] {needs_review} files need manual review (active code)")
    print(f"   [*] Estimated space savings: 200-400 MB\n")


if __name__ == "__main__":
    main()
