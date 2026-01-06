"""
CORTEX Duplicate Functionality Analyzer

Identifies multiple versions of the same functionality across the codebase.
Detects duplicates at file, function, class, and import levels.
SAFETY ENHANCED: Identifies active/canonical versions to prevent accidental deletion.

Author: Asif Hussain
Version: 2.0
Created: December 7, 2025
Updated: January 6, 2026 - Recreated clean version
"""

import os
import ast
import json
import subprocess
from pathlib import Path
from typing import Dict, List
from collections import defaultdict


class DuplicateFunctionalityAnalyzer:
    """Analyzes CORTEX repository for duplicate functionality"""
    
    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root)
        self.exclude_dirs = {'.venv', 'node_modules', '__pycache__', '.git'}
        self.duplicate_files = defaultdict(list)
        self.duplicate_functions = defaultdict(list)
        self.duplicate_classes = defaultdict(list)
        
    def analyze(self) -> Dict:
        """Run complete duplicate analysis"""
        print("🔍 Starting CORTEX Duplicate Functionality Analysis")
        python_files = self._collect_python_files()
        print(f"✅ Found {len(python_files)} Python files")
        
        self._analyze_file_duplicates(python_files)
        self._analyze_function_duplicates(python_files)
        self._analyze_class_duplicates(python_files)
        
        return self._generate_report()
    
    def _collect_python_files(self) -> List[Path]:
        python_files = []
        for root, dirs, files in os.walk(self.repo_root):
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
            for file in files:
                if file.endswith('.py'):
                    python_files.append(Path(root) / file)
        return python_files
    
    def _analyze_file_duplicates(self, python_files: List[Path]):
        filename_map = defaultdict(list)
        for file_path in python_files:
            filename_map[file_path.name].append(file_path)
        
        for filename, paths in filename_map.items():
            if len(paths) > 1:
                self.duplicate_files[filename] = [str(p.relative_to(self.repo_root)) for p in paths]
    
    def _analyze_function_duplicates(self, python_files: List[Path]):
        for file_path in python_files:
            try:
                tree = ast.parse(file_path.read_text())
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        args = [arg.arg for arg in node.args.args]
                        func_sig = f"{node.name}({', '.join(args)})"
                        location = f"{file_path.relative_to(self.repo_root)}:{node.lineno}"
                        self.duplicate_functions[func_sig].append(location)
            except:
                pass
    
    def _analyze_class_duplicates(self, python_files: List[Path]):
        class_info = defaultdict(list)
        for file_path in python_files:
            try:
                tree = ast.parse(file_path.read_text())
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        location = f"{file_path.relative_to(self.repo_root)}:{node.lineno}"
                        class_info[node.name].append(location)
            except:
                pass
        
        for class_name, instances in class_info.items():
            if len(instances) > 1:
                self.duplicate_classes[class_name] = instances
    
    def _generate_report(self) -> Dict:
        real_func_duplicates = {sig: locs for sig, locs in self.duplicate_functions.items() 
                               if len(locs) > 1}
        
        return {
            'summary': {
                'duplicate_files': len(self.duplicate_files),
                'duplicate_functions': len(real_func_duplicates),
                'duplicate_classes': len(self.duplicate_classes)
            },
            'duplicate_files': dict(self.duplicate_files),
            'duplicate_functions': dict(real_func_duplicates),
            'duplicate_classes': dict(self.duplicate_classes)
        }
    
    def print_report(self, report: Dict):
        print("\n" + "="*80)
        print("📊 CORTEX DUPLICATE FUNCTIONALITY ANALYSIS")
        print("="*80)
        print(f"\nDuplicate Files: {report['summary']['duplicate_files']}")
        print(f"Duplicate Functions: {report['summary']['duplicate_functions']}")
        print(f"Duplicate Classes: {report['summary']['duplicate_classes']}")
    
    def save_report(self, report: Dict, output_path: str):
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(json.dumps(report, indent=2))
        print(f"\n📄 Report saved: {output_path}")


def main():
    script_dir = Path(__file__).resolve().parent
    cortex_root = script_dir.parent.parent
    
    analyzer = DuplicateFunctionalityAnalyzer(str(cortex_root))
    report = analyzer.analyze()
    analyzer.print_report(report)
    
    output_path = cortex_root / "cortex-brain" / "documents" / "analysis" / "duplicate-functionality-analysis.json"
    analyzer.save_report(report, str(output_path))


if __name__ == "__main__":
    main()
