"""
Automated Documentation Generator

Extracts documentation from Python code and generates markdown files.
Convention-based approach for scalable documentation.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import ast
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class DocExtractor:
    """Extract documentation from Python source code."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.src_dir = project_root / "src"
        self.docs_dir = project_root / "docs"
        
    def extract_module_doc(self, file_path: Path) -> Dict[str, Any]:
        """Extract documentation from a Python module."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Get module docstring
            module_doc = ast.get_docstring(tree) or ""
            
            # Extract classes
            classes = []
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_doc = ast.get_docstring(node) or ""
                    methods = []
                    
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            method_doc = ast.get_docstring(item) or ""
                            # Extract parameters
                            params = [arg.arg for arg in item.args.args if arg.arg != 'self']
                            
                            # Check for property decorator safely
                            is_prop = False
                            try:
                                is_prop = any(
                                    isinstance(d, ast.Name) and d.id == 'property'
                                    for d in item.decorator_list
                                )
                            except:
                                pass
                            
                            methods.append({
                                'name': item.name,
                                'doc': method_doc,
                                'params': params,
                                'is_property': is_prop
                            })
                    
                    classes.append({
                        'name': node.name,
                        'doc': class_doc,
                        'methods': methods,
                        'bases': [self._get_base_name(base) for base in node.bases]
                    })
            
            # Extract functions (not in classes)
            functions = []
            top_level_funcs = [node for node in tree.body if isinstance(node, ast.FunctionDef)]
            
            for node in top_level_funcs:
                func_doc = ast.get_docstring(node) or ""
                params = [arg.arg for arg in node.args.args]
                functions.append({
                    'name': node.name,
                    'doc': func_doc,
                    'params': params
                })
            
            # Extract metadata from docstring
            metadata = self._extract_metadata(module_doc)
            
            return {
                'file_path': str(file_path.relative_to(self.project_root)),
                'module_doc': module_doc,
                'metadata': metadata,
                'classes': classes,
                'functions': functions
            }
            
        except Exception as e:
            print(f"⚠️ Error parsing {file_path}: {e}")
            return None
    
    def _get_base_name(self, base) -> str:
        """Get base class name from AST node."""
        if isinstance(base, ast.Name):
            return base.id
        elif isinstance(base, ast.Attribute):
            return f"{self._get_base_name(base.value)}.{base.attr}"
        return str(base)
    
    def _extract_metadata(self, docstring: str) -> Dict[str, str]:
        """Extract metadata fields from docstring."""
        metadata = {}
        patterns = {
            'author': r'Author:\s*(.+)',
            'copyright': r'Copyright:\s*(.+)',
            'version': r'Version:\s*(.+)',
            'status': r'Status:\s*(.+)',
            'purpose': r'Purpose:\s*(.+)'
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, docstring, re.IGNORECASE)
            if match:
                metadata[key] = match.group(1).strip()
        
        return metadata
    
    def generate_markdown(self, doc_data: Dict[str, Any]) -> str:
        """Generate markdown documentation from extracted data."""
        if not doc_data:
            return ""
        
        lines = []
        
        # Title
        module_name = Path(doc_data['file_path']).stem
        title = module_name.replace('_', ' ').title()
        lines.append(f"# {title}")
        lines.append("")
        
        # Metadata
        metadata = doc_data.get('metadata', {})
        if metadata:
            if 'author' in metadata:
                lines.append(f"**Author:** {metadata['author']}  ")
            if 'version' in metadata:
                lines.append(f"**Version:** {metadata['version']}  ")
            if 'status' in metadata:
                lines.append(f"**Status:** {metadata['status']}  ")
            lines.append("")
        
        # Module description
        module_doc = doc_data.get('module_doc', '')
        if module_doc:
            # Extract first paragraph
            first_para = module_doc.split('\n\n')[0]
            lines.append(first_para)
            lines.append("")
        
        # Source file location
        lines.append("---")
        lines.append("")
        lines.append(f"**Source:** `{doc_data['file_path']}`")
        lines.append("")
        
        # Classes
        classes = doc_data.get('classes', [])
        if classes:
            lines.append("## Classes")
            lines.append("")
            
            for cls in classes:
                lines.append(f"### `{cls['name']}`")
                lines.append("")
                
                if cls.get('bases'):
                    bases_str = ', '.join(cls['bases'])
                    lines.append(f"**Inherits:** `{bases_str}`")
                    lines.append("")
                
                if cls.get('doc'):
                    lines.append(cls['doc'])
                    lines.append("")
                
                # Methods
                methods = [m for m in cls.get('methods', []) if not m['name'].startswith('_')]
                if methods:
                    lines.append("**Methods:**")
                    lines.append("")
                    
                    for method in methods:
                        params_str = ', '.join(method['params']) if method['params'] else ''
                        
                        if method.get('is_property'):
                            lines.append(f"- **`{method['name']}`** (property)")
                        else:
                            lines.append(f"- **`{method['name']}({params_str})`**")
                        
                        if method.get('doc'):
                            # First line of docstring
                            first_line = method['doc'].split('\n')[0]
                            lines.append(f"  {first_line}")
                        
                        lines.append("")
        
        # Functions
        functions = doc_data.get('functions', [])
        public_functions = [f for f in functions if not f['name'].startswith('_')]
        if public_functions:
            lines.append("## Functions")
            lines.append("")
            
            for func in public_functions:
                params_str = ', '.join(func['params']) if func['params'] else ''
                lines.append(f"### `{func['name']}({params_str})`")
                lines.append("")
                
                if func.get('doc'):
                    lines.append(func['doc'])
                    lines.append("")
        
        return '\n'.join(lines)


class DocsGenerator:
    """Generate documentation for new features."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.extractor = DocExtractor(project_root)
        self.docs_dir = project_root / "docs"
        
    def generate_for_commit(self, commit_hash: str = "HEAD") -> List[Path]:
        """Generate docs for files changed in commit."""
        import subprocess
        
        # Get changed Python files
        result = subprocess.run(
            ['git', 'diff-tree', '--no-commit-id', '--name-only', '-r', commit_hash],
            cwd=self.project_root,
            capture_output=True,
            text=True
        )
        
        py_files = [
            self.project_root / line.strip()
            for line in result.stdout.splitlines()
            if line.strip().endswith('.py')
        ]
        
        generated_docs = []
        
        for py_file in py_files:
            if not py_file.exists():
                continue
            
            # Extract documentation
            doc_data = self.extractor.extract_module_doc(py_file)
            if not doc_data:
                continue
            
            # Determine output path
            relative_path = py_file.relative_to(self.project_root)
            
            # Map to docs directory
            if relative_path.parts[0] == 'src':
                # src/operations/modules/admin/system_alignment_orchestrator.py
                # -> docs/reference/admin/system-alignment-orchestrator.md
                doc_path = self.docs_dir / 'reference'
                for part in relative_path.parts[1:-1]:
                    doc_path = doc_path / part
                
                filename = relative_path.stem.replace('_', '-') + '.md'
                doc_path = doc_path / filename
            
            elif relative_path.parts[0] == 'scripts':
                # scripts/operations/upgrade_orchestrator.py
                # -> docs/reference/scripts/upgrade-orchestrator.md
                doc_path = self.docs_dir / 'reference' / 'scripts'
                for part in relative_path.parts[1:-1]:
                    doc_path = doc_path / part
                
                filename = relative_path.stem.replace('_', '-') + '.md'
                doc_path = doc_path / filename
            else:
                continue
            
            # Generate markdown
            markdown = self.extractor.generate_markdown(doc_data)
            if not markdown:
                continue
            
            # Create directory if needed
            doc_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            with open(doc_path, 'w', encoding='utf-8') as f:
                f.write(markdown)
            
            generated_docs.append(doc_path)
            print(f"✅ Generated: {doc_path.relative_to(self.project_root)}")
        
        return generated_docs
    
    def generate_index(self, generated_docs: List[Path]):
        """Generate index files for documentation sections."""
        # Group by section
        by_section = {}
        for doc in generated_docs:
            relative = doc.relative_to(self.docs_dir)
            section = relative.parts[1] if len(relative.parts) > 1 else 'general'
            
            if section not in by_section:
                by_section[section] = []
            by_section[section].append(doc)
        
        # Generate index for each section
        for section, docs in by_section.items():
            index_path = self.docs_dir / 'reference' / section / 'index.md'
            index_path.parent.mkdir(parents=True, exist_ok=True)
            
            lines = [
                f"# {section.title()} Reference",
                "",
                f"**Generated:** {datetime.now().strftime('%Y-%m-%d')}",
                "",
                "## Modules",
                ""
            ]
            
            for doc in sorted(docs):
                title = doc.stem.replace('-', ' ').title()
                rel_path = doc.relative_to(index_path.parent)
                lines.append(f"- [{title}]({rel_path})")
            
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            
            print(f"✅ Generated index: {index_path.relative_to(self.project_root)}")


def main():
    """Main entry point."""
    project_root = Path(__file__).parent.parent
    generator = DocsGenerator(project_root)
    
    print("🧠 CORTEX Automated Documentation Generator")
    print("=" * 60)
    print()
    
    # Generate for latest commit
    print("📝 Generating documentation from latest commit...")
    generated = generator.generate_for_commit("HEAD")
    
    print()
    print(f"✅ Generated {len(generated)} documentation files")
    
    # Generate indexes
    if generated:
        print()
        print("📚 Generating section indexes...")
        generator.generate_index(generated)
    
    print()
    print("🎉 Documentation generation complete!")


if __name__ == "__main__":
    main()
