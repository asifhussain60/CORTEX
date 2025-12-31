#!/usr/bin/env python3
"""
CORTEX DocGen Discovery Tool

Discovers all documentable code elements in the CORTEX codebase:
- Python modules, classes, functions, methods
- Docstrings and type hints
- Orchestrator manifests
- Existing documentation pages

Author: Asif Hussain
Version: 1.1.0

Security:
- Path traversal protection via safe_path()
- Atomic file writes prevent corruption
- Automatic backups before overwrite
"""

import ast
import hashlib
import json
import os
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


def safe_path(project_root: Path, user_path: str) -> Path:
    """Validate path stays within project root (prevent path traversal)."""
    resolved = (project_root / user_path).resolve()
    if not str(resolved).startswith(str(project_root.resolve())):
        raise ValueError(f"Path escapes project root: {user_path}")
    return resolved


class DocGenDiscovery:
    """Discover documentable elements in CORTEX codebase."""
    
    MAX_BACKUPS = 5  # Keep last N backups
    
    def __init__(self, project_root: Path):
        self.project_root = project_root.resolve()
        self.src_dir = project_root / "src"
        self.docs_dir = project_root / "docs"
        self.brain_dir = project_root / "cortex-brain"
        self.manifests_dir = self.brain_dir / "manifests" / "orchestrators"
        
    def discover_all(self) -> Dict[str, Any]:
        """Run full discovery and return manifest."""
        return {
            "version": "1.0",
            "generated": datetime.now().isoformat(),
            "generator": "docgen_discovery.py",
            "python_modules": self._discover_python_modules(),
            "orchestrators": self._discover_orchestrators(),
            "documentation_pages": self._discover_doc_pages(),
            "statistics": {}
        }
    
    def _discover_python_modules(self) -> List[Dict[str, Any]]:
        """Discover all Python modules in src/."""
        modules = []
        
        if not self.src_dir.exists():
            return modules
            
        for py_file in self.src_dir.rglob("*.py"):
            if py_file.name.startswith("__"):
                continue
                
            module_info = self._analyze_module(py_file)
            if module_info:
                modules.append(module_info)
                
        return modules
    
    def _analyze_module(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Analyze a Python module for documentable elements."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Get module docstring
            module_doc = ast.get_docstring(tree) or ""
            
            # Get relative path
            rel_path = file_path.relative_to(self.project_root)
            
            # Extract classes
            classes = []
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_info = self._extract_class_info(node)
                    classes.append(class_info)
            
            # Extract top-level functions
            functions = []
            for node in tree.body:
                if isinstance(node, ast.FunctionDef):
                    func_info = self._extract_function_info(node)
                    functions.append(func_info)
            
            return {
                "path": str(rel_path),
                "name": file_path.stem,
                "docstring": module_doc[:200] if module_doc else None,
                "has_docstring": bool(module_doc),
                "classes": classes,
                "functions": functions,
                "class_count": len(classes),
                "function_count": len(functions),
                "lines": len(content.splitlines())
            }
            
        except Exception as e:
            print(f"Warning: Could not analyze {file_path}: {e}")
            return None
    
    def _extract_class_info(self, node: ast.ClassDef) -> Dict[str, Any]:
        """Extract information about a class."""
        class_doc = ast.get_docstring(node) or ""
        
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_info = self._extract_function_info(item, is_method=True)
                methods.append(method_info)
        
        # Get base classes
        bases = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
            elif isinstance(base, ast.Attribute):
                bases.append(f"{base.value.id if isinstance(base.value, ast.Name) else '?'}.{base.attr}")
        
        return {
            "name": node.name,
            "docstring": class_doc[:200] if class_doc else None,
            "has_docstring": bool(class_doc),
            "bases": bases,
            "methods": methods,
            "method_count": len(methods),
            "public_methods": len([m for m in methods if not m["name"].startswith("_")])
        }
    
    def _extract_function_info(self, node: ast.FunctionDef, is_method: bool = False) -> Dict[str, Any]:
        """Extract information about a function or method."""
        func_doc = ast.get_docstring(node) or ""
        
        # Extract parameters
        params = []
        for arg in node.args.args:
            if arg.arg == 'self':
                continue
            param_info = {"name": arg.arg}
            if arg.annotation:
                param_info["type"] = self._get_annotation_str(arg.annotation)
            params.append(param_info)
        
        # Get return type
        return_type = None
        if node.returns:
            return_type = self._get_annotation_str(node.returns)
        
        # Check decorators
        decorators = []
        for dec in node.decorator_list:
            if isinstance(dec, ast.Name):
                decorators.append(dec.id)
            elif isinstance(dec, ast.Attribute):
                decorators.append(dec.attr)
        
        return {
            "name": node.name,
            "docstring": func_doc[:150] if func_doc else None,
            "has_docstring": bool(func_doc),
            "params": params,
            "return_type": return_type,
            "decorators": decorators,
            "is_property": "property" in decorators,
            "is_private": node.name.startswith("_")
        }
    
    def _get_annotation_str(self, annotation) -> str:
        """Convert AST annotation to string."""
        if isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Constant):
            return str(annotation.value)
        elif isinstance(annotation, ast.Subscript):
            base = self._get_annotation_str(annotation.value)
            if isinstance(annotation.slice, ast.Tuple):
                args = ", ".join(self._get_annotation_str(e) for e in annotation.slice.elts)
            else:
                args = self._get_annotation_str(annotation.slice)
            return f"{base}[{args}]"
        elif isinstance(annotation, ast.Attribute):
            return f"{self._get_annotation_str(annotation.value)}.{annotation.attr}"
        return "Any"
    
    def _discover_orchestrators(self) -> List[Dict[str, Any]]:
        """Discover orchestrator manifests."""
        orchestrators = []
        
        if not self.manifests_dir.exists():
            return orchestrators
            
        for manifest_file in self.manifests_dir.glob("*.yaml"):
            orchestrators.append({
                "name": manifest_file.stem,
                "path": str(manifest_file.relative_to(self.project_root)),
                "size": manifest_file.stat().st_size,
                "modified": datetime.fromtimestamp(manifest_file.stat().st_mtime).isoformat()
            })
            
        return orchestrators
    
    def _discover_doc_pages(self) -> List[Dict[str, Any]]:
        """Discover existing documentation pages."""
        pages = []
        
        if not self.docs_dir.exists():
            return pages
            
        for html_file in self.docs_dir.rglob("*.html"):
            rel_path = html_file.relative_to(self.docs_dir)
            
            # Determine level
            parts = rel_path.parts
            if len(parts) == 1:
                level = "home"
            elif len(parts) == 2 and parts[-1] == "index.html":
                level = "level1"
            else:
                level = "level2"
            
            # Check for D3.js or Mermaid
            try:
                content = html_file.read_text(encoding='utf-8')
                has_d3 = 'd3.' in content or 'd3.js' in content
                has_mermaid = 'mermaid' in content.lower()
            except:
                has_d3 = False
                has_mermaid = False
            
            pages.append({
                "path": str(rel_path),
                "section": parts[0] if len(parts) > 1 else "root",
                "level": level,
                "has_d3": has_d3,
                "has_mermaid": has_mermaid,
                "size": html_file.stat().st_size,
                "modified": datetime.fromtimestamp(html_file.stat().st_mtime).isoformat()
            })
            
        return pages
    
    def save_manifest(self, output_path: Path, data: Dict[str, Any]) -> None:
        """Save discovery results to JSON manifest."""
        # Calculate statistics
        data["statistics"] = {
            "total_modules": len(data["python_modules"]),
            "total_classes": sum(m["class_count"] for m in data["python_modules"]),
            "total_functions": sum(m["function_count"] for m in data["python_modules"]),
            "modules_with_docstrings": len([m for m in data["python_modules"] if m["has_docstring"]]),
            "orchestrator_count": len(data["orchestrators"]),
            "doc_page_count": len(data["documentation_pages"]),
            "pages_with_d3": len([p for p in data["documentation_pages"] if p["has_d3"]]),
            "pages_with_mermaid": len([p for p in data["documentation_pages"] if p["has_mermaid"]])
        }
        
        # Add checksum for integrity verification
        content_for_hash = json.dumps(data, sort_keys=True)
        data["_checksum"] = hashlib.sha256(content_for_hash.encode()).hexdigest()[:16]
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Backup existing manifest
        if output_path.exists():
            backup_path = output_path.with_suffix(
                f'.json.bak.{datetime.now().strftime("%Y%m%d_%H%M%S")}'
            )
            shutil.copy2(output_path, backup_path)
            
            # Cleanup old backups (keep last N)
            backups = sorted(output_path.parent.glob(f"{output_path.stem}.json.bak.*"))
            for old_backup in backups[:-self.MAX_BACKUPS]:
                old_backup.unlink()
        
        # Atomic write using temp file
        fd, temp_path = tempfile.mkstemp(suffix='.json', dir=output_path.parent)
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            shutil.move(temp_path, output_path)
        except Exception:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise
        
        print(f"✅ Manifest saved to: {output_path}")
        print(f"   - {data['statistics']['total_modules']} Python modules")
        print(f"   - {data['statistics']['total_classes']} classes")
        print(f"   - {data['statistics']['total_functions']} functions")
        print(f"   - {data['statistics']['orchestrator_count']} orchestrators")
        print(f"   - {data['statistics']['doc_page_count']} documentation pages")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="CORTEX DocGen Discovery Tool")
    parser.add_argument("--output", "-o", 
                       default="cortex-brain/documents/docgen-manifest.json",
                       help="Output manifest file path")
    parser.add_argument("--project-root", "-p",
                       default=None,
                       help="Project root directory (default: auto-detect)")
    
    args = parser.parse_args()
    
    # Auto-detect project root
    if args.project_root:
        project_root = Path(args.project_root).resolve()
    else:
        # Walk up from script location to find project root
        script_path = Path(__file__).resolve()
        project_root = script_path.parent.parent.parent  # toolkit/documentation -> toolkit -> project
        
        # Verify we found the right directory
        if not (project_root / "cortex-brain").exists():
            print("Error: Could not find project root. Use --project-root option.")
            sys.exit(3)  # Exit code 3 = project root not found
    
    print(f"🔍 CORTEX DocGen Discovery")
    print(f"   Project root: {project_root}")
    print()
    
    discovery = DocGenDiscovery(project_root)
    manifest = discovery.discover_all()
    
    # Validate output path stays within project (security)
    try:
        output_path = safe_path(project_root, args.output)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(2)  # Exit code 2 = invalid arguments
    
    discovery.save_manifest(output_path, manifest)


if __name__ == "__main__":
    main()
