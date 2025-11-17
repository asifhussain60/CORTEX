"""
CORTEX Documentation Generator - Monolithic Script

Single-script implementation for documentation update operation.
Auto-generates docs from code/YAML, validates links, updates MkDocs structure.

Design Philosophy (CORTEX 3.0):
- Monolithic-then-modular: Ship working MVP first
- User value over perfect architecture
- Refactor only when complexity warrants (>500 lines)

Features:
- API reference extraction from docstrings
- Operation documentation auto-generation
- Link validation system
- MkDocs navigation updates
- YAML-based configuration

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0 (CORTEX 3.0 Phase 1.1 Week 2)
"""

import os
import re
import sys
import ast
import yaml
import json
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
import inspect


@dataclass
class DocGenerationResult:
    """Result of documentation generation operation."""
    success: bool
    docs_generated: List[str] = field(default_factory=list)
    docs_updated: List[str] = field(default_factory=list)
    links_validated: int = 0
    links_broken: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    duration_seconds: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'success': self.success,
            'docs_generated': self.docs_generated,
            'docs_updated': self.docs_updated,
            'links_validated': self.links_validated,
            'links_broken': self.links_broken,
            'warnings': self.warnings,
            'errors': self.errors,
            'duration_seconds': self.duration_seconds,
            'timestamp': self.timestamp.isoformat()
        }


class DocumentationGenerator:
    """
    CORTEX Documentation Generator.
    
    Generates and updates documentation from source code and YAML files.
    """
    
    def __init__(self, cortex_root: Optional[Path] = None):
        """
        Initialize documentation generator.
        
        Args:
            cortex_root: Path to CORTEX root directory
        """
        self.cortex_root = cortex_root or Path.cwd()
        self.docs_dir = self.cortex_root / "docs"
        self.src_dir = self.cortex_root / "src"
        self.brain_dir = self.cortex_root / "cortex-brain"
        self.config_file = self.brain_dir / "doc-generation-rules.yaml"
        self.mkdocs_file = self.cortex_root / "mkdocs.yml"
        
        self.config: Dict[str, Any] = {}
        self.python_files: List[Path] = []
        self.yaml_files: List[Path] = []
        self.markdown_files: List[Path] = []
        
    def load_config(self) -> bool:
        """Load documentation generation configuration."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = yaml.safe_load(f) or {}
            else:
                # Create default config
                self.config = self._create_default_config()
                self._save_config()
            return True
        except Exception as e:
            print(f"Error loading config: {e}")
            return False
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Create default documentation generation configuration."""
        return {
            'version': '1.0.0',
            'author': 'Asif Hussain',
            'copyright': '© 2024-2025 Asif Hussain. All rights reserved.',
            
            'sources': {
                'python_dirs': ['src/', 'tests/'],
                'yaml_dirs': ['cortex-brain/'],
                'exclude_patterns': [
                    '**/__pycache__/**',
                    '**/.*',
                    '**/dist/**',
                    '**/site/**',
                    '**/node_modules/**'
                ]
            },
            
            'output': {
                'api_reference': 'docs/api/',
                'operations': 'docs/operations/',
                'architecture': 'docs/architecture/',
                'auto_generated_marker': '<!-- AUTO-GENERATED -->',
                'update_existing': True
            },
            
            'docstring_format': 'google',  # google, numpy, sphinx
            
            'link_validation': {
                'enabled': True,
                'check_external': False,  # Skip external links (slow)
                'check_anchors': True
            },
            
            'mkdocs': {
                'auto_update_nav': True,
                'preserve_custom_sections': True
            }
        }
    
    def _save_config(self) -> None:
        """Save configuration to file."""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
    
    def discover_files(self) -> bool:
        """Discover all relevant files for documentation generation."""
        try:
            exclude_patterns = self.config.get('sources', {}).get('exclude_patterns', [])
            
            # Discover Python files
            python_dirs = self.config.get('sources', {}).get('python_dirs', ['src/'])
            for dir_path in python_dirs:
                full_path = self.cortex_root / dir_path
                if full_path.exists():
                    self.python_files.extend(self._find_files(full_path, '*.py', exclude_patterns))
            
            # Discover YAML files
            yaml_dirs = self.config.get('sources', {}).get('yaml_dirs', ['cortex-brain/'])
            for dir_path in yaml_dirs:
                full_path = self.cortex_root / dir_path
                if full_path.exists():
                    self.yaml_files.extend(self._find_files(full_path, '*.yaml', exclude_patterns))
            
            # Discover existing Markdown files
            if self.docs_dir.exists():
                self.markdown_files.extend(self._find_files(self.docs_dir, '*.md', exclude_patterns))
            
            return True
        except Exception as e:
            print(f"Error discovering files: {e}")
            return False
    
    def _find_files(self, base_path: Path, pattern: str, exclude_patterns: List[str]) -> List[Path]:
        """Find files matching pattern, excluding specified patterns."""
        files = []
        for file_path in base_path.rglob(pattern):
            # Check if file matches any exclude pattern
            relative_path = file_path.relative_to(self.cortex_root)
            excluded = False
            for exclude_pattern in exclude_patterns:
                if file_path.match(exclude_pattern):
                    excluded = True
                    break
            
            if not excluded:
                files.append(file_path)
        
        return files
    
    def extract_python_docstrings(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract docstrings from Python file.
        
        Args:
            file_path: Path to Python file
            
        Returns:
            Dictionary with module, classes, functions, and their docstrings
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            result = {
                'file': str(file_path.relative_to(self.cortex_root)),
                'module_doc': ast.get_docstring(tree),
                'classes': [],
                'functions': []
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_info = {
                        'name': node.name,
                        'docstring': ast.get_docstring(node),
                        'methods': []
                    }
                    
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            class_info['methods'].append({
                                'name': item.name,
                                'docstring': ast.get_docstring(item),
                                'args': self._extract_function_args(item)
                            })
                    
                    result['classes'].append(class_info)
                
                elif isinstance(node, ast.FunctionDef) and node.col_offset == 0:
                    # Top-level function
                    result['functions'].append({
                        'name': node.name,
                        'docstring': ast.get_docstring(node),
                        'args': self._extract_function_args(node)
                    })
            
            return result
        
        except Exception as e:
            print(f"Error extracting docstrings from {file_path}: {e}")
            return {}
    
    def _extract_function_args(self, func_node: ast.FunctionDef) -> List[str]:
        """Extract function argument names."""
        args = []
        for arg in func_node.args.args:
            args.append(arg.arg)
        return args
    
    def generate_api_reference(self, docstrings: List[Dict[str, Any]]) -> str:
        """
        Generate API reference markdown from docstrings.
        
        Args:
            docstrings: List of docstring dictionaries
            
        Returns:
            Markdown content
        """
        lines = [
            "# CORTEX API Reference",
            "",
            f"**Auto-generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Copyright:** {self.config.get('copyright', '')}",
            "",
            "---",
            ""
        ]
        
        # Group by module
        modules = {}
        for doc in docstrings:
            module_path = doc.get('file', '')
            if module_path:
                module_name = module_path.replace('/', '.').replace('.py', '')
                modules[module_name] = doc
        
        # Generate documentation for each module
        for module_name in sorted(modules.keys()):
            doc = modules[module_name]
            
            lines.append(f"## {module_name}")
            lines.append("")
            
            if doc.get('module_doc'):
                lines.append(doc['module_doc'])
                lines.append("")
            
            # Classes
            for cls in doc.get('classes', []):
                lines.append(f"### {cls['name']}")
                lines.append("")
                
                if cls.get('docstring'):
                    lines.append(cls['docstring'])
                    lines.append("")
                
                # Methods
                if cls.get('methods'):
                    lines.append("**Methods:**")
                    lines.append("")
                    
                    for method in cls['methods']:
                        if not method['name'].startswith('_'):  # Skip private methods
                            args = ', '.join(method.get('args', []))
                            lines.append(f"#### `{method['name']}({args})`")
                            lines.append("")
                            
                            if method.get('docstring'):
                                lines.append(method['docstring'])
                                lines.append("")
            
            # Functions
            for func in doc.get('functions', []):
                if not func['name'].startswith('_'):  # Skip private functions
                    args = ', '.join(func.get('args', []))
                    lines.append(f"### `{func['name']}({args})`")
                    lines.append("")
                    
                    if func.get('docstring'):
                        lines.append(func['docstring'])
                        lines.append("")
            
            lines.append("---")
            lines.append("")
        
        return '\n'.join(lines)
    
    def generate_operations_docs(self) -> List[Tuple[str, str]]:
        """
        Generate documentation for all operations.
        
        Returns:
            List of (filename, content) tuples
        """
        operations_docs = []
        
        # Find all operation files
        operations_dir = self.src_dir / "operations"
        if not operations_dir.exists():
            return operations_docs
        
        operation_files = list(operations_dir.glob("*.py"))
        
        for op_file in operation_files:
            if op_file.name.startswith('_') or op_file.name == 'base_operation_module.py':
                continue
            
            # Extract docstrings
            docstrings = self.extract_python_docstrings(op_file)
            
            # Generate operation-specific doc
            operation_name = op_file.stem.replace('_', '-')
            content = self._generate_operation_doc(operation_name, docstrings)
            
            operations_docs.append((f"{operation_name}.md", content))
        
        return operations_docs
    
    def _generate_operation_doc(self, operation_name: str, docstrings: Dict[str, Any]) -> str:
        """Generate documentation for a specific operation."""
        lines = [
            f"# {operation_name.replace('-', ' ').title()} Operation",
            "",
            f"**Auto-generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "---",
            ""
        ]
        
        # Module description
        if docstrings.get('module_doc'):
            lines.append("## Overview")
            lines.append("")
            lines.append(docstrings['module_doc'])
            lines.append("")
        
        # Main class (usually the operation class)
        classes = docstrings.get('classes', [])
        if classes:
            main_class = classes[0]  # Assume first class is the operation
            
            lines.append("## Usage")
            lines.append("")
            lines.append(f"```python")
            lines.append(f"from src.operations.{operation_name.replace('-', '_')} import {main_class['name']}")
            lines.append(f"")
            lines.append(f"operation = {main_class['name']}()")
            lines.append(f"result = operation.execute()")
            lines.append(f"```")
            lines.append("")
            
            # Methods
            if main_class.get('methods'):
                lines.append("## Methods")
                lines.append("")
                
                for method in main_class['methods']:
                    if method['name'].startswith('_'):
                        continue
                    
                    args = ', '.join(method.get('args', []))
                    lines.append(f"### `{method['name']}({args})`")
                    lines.append("")
                    
                    if method.get('docstring'):
                        lines.append(method['docstring'])
                        lines.append("")
        
        return '\n'.join(lines)
    
    def validate_links(self, markdown_files: List[Path]) -> Tuple[int, List[str]]:
        """
        Validate links in markdown files.
        
        Args:
            markdown_files: List of markdown files to validate
            
        Returns:
            Tuple of (total_links, broken_links)
        """
        if not self.config.get('link_validation', {}).get('enabled', True):
            return (0, [])
        
        total_links = 0
        broken_links = []
        
        # Regex patterns for different link types
        markdown_link_pattern = re.compile(r'\[([^\]]+)\]\(([^\)]+)\)')
        
        for md_file in markdown_files:
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                links = markdown_link_pattern.findall(content)
                
                for link_text, link_url in links:
                    total_links += 1
                    
                    # Skip external links if configured
                    if link_url.startswith('http') and not self.config.get('link_validation', {}).get('check_external', False):
                        continue
                    
                    # Check internal file links
                    if not link_url.startswith('http'):
                        # Remove anchor
                        file_link = link_url.split('#')[0]
                        
                        # Resolve relative path
                        link_path = (md_file.parent / file_link).resolve()
                        
                        if not link_path.exists():
                            broken_links.append(f"{md_file.name}: {link_url}")
            
            except Exception as e:
                print(f"Error validating links in {md_file}: {e}")
        
        return (total_links, broken_links)
    
    def update_mkdocs_nav(self, generated_docs: List[str]) -> bool:
        """
        Update MkDocs navigation with generated documentation.
        
        Args:
            generated_docs: List of generated documentation files
            
        Returns:
            Success status
        """
        if not self.config.get('mkdocs', {}).get('auto_update_nav', True):
            return True
        
        try:
            if not self.mkdocs_file.exists():
                print("mkdocs.yml not found")
                return False
            
            with open(self.mkdocs_file, 'r', encoding='utf-8') as f:
                mkdocs_config = yaml.safe_load(f)
            
            # Get or create nav section
            nav = mkdocs_config.get('nav', [])
            
            # Find or create API Reference section
            api_section = None
            for item in nav:
                if isinstance(item, dict) and 'API Reference' in item:
                    api_section = item['API Reference']
                    break
            
            if api_section is None:
                api_section = []
                nav.append({'API Reference': api_section})
            
            # Add generated docs to nav (if not already present)
            for doc_file in generated_docs:
                doc_path = f"api/{doc_file}"
                if doc_path not in api_section:
                    api_section.append(doc_path)
            
            # Update mkdocs config
            mkdocs_config['nav'] = nav
            
            # Save updated config
            with open(self.mkdocs_file, 'w', encoding='utf-8') as f:
                yaml.dump(mkdocs_config, f, default_flow_style=False, sort_keys=False)
            
            return True
        
        except Exception as e:
            print(f"Error updating MkDocs navigation: {e}")
            return False
    
    def execute(self) -> DocGenerationResult:
        """
        Execute documentation generation.
        
        Returns:
            DocGenerationResult with execution details
        """
        start_time = datetime.now()
        result = DocGenerationResult(success=False)
        
        try:
            print("🧠 CORTEX Documentation Generator")
            print("=" * 60)
            
            # Load configuration
            print("\n📋 Loading configuration...")
            if not self.load_config():
                result.errors.append("Failed to load configuration")
                return result
            print(f"✓ Configuration loaded from {self.config_file}")
            
            # Discover files
            print("\n🔍 Discovering files...")
            if not self.discover_files():
                result.errors.append("Failed to discover files")
                return result
            print(f"✓ Found {len(self.python_files)} Python files")
            print(f"✓ Found {len(self.yaml_files)} YAML files")
            print(f"✓ Found {len(self.markdown_files)} Markdown files")
            
            # Extract docstrings
            print("\n📖 Extracting docstrings...")
            all_docstrings = []
            for py_file in self.python_files:
                docstrings = self.extract_python_docstrings(py_file)
                if docstrings:
                    all_docstrings.append(docstrings)
            print(f"✓ Extracted docstrings from {len(all_docstrings)} files")
            
            # Generate API reference
            print("\n📝 Generating API reference...")
            api_dir = self.docs_dir / "api"
            api_dir.mkdir(parents=True, exist_ok=True)
            
            api_content = self.generate_api_reference(all_docstrings)
            api_file = api_dir / "reference.md"
            
            with open(api_file, 'w', encoding='utf-8') as f:
                f.write(api_content)
            
            result.docs_generated.append(str(api_file.relative_to(self.cortex_root)))
            print(f"✓ Generated {api_file}")
            
            # Generate operations documentation
            print("\n📝 Generating operations documentation...")
            operations_dir = self.docs_dir / "operations"
            operations_dir.mkdir(parents=True, exist_ok=True)
            
            operations_docs = self.generate_operations_docs()
            for filename, content in operations_docs:
                op_file = operations_dir / filename
                with open(op_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                result.docs_generated.append(str(op_file.relative_to(self.cortex_root)))
                print(f"✓ Generated {op_file}")
            
            # Validate links
            print("\n🔗 Validating links...")
            total_links, broken_links = self.validate_links(self.markdown_files)
            result.links_validated = total_links
            result.links_broken = broken_links
            
            if broken_links:
                print(f"⚠️  Found {len(broken_links)} broken links:")
                for broken_link in broken_links[:5]:  # Show first 5
                    print(f"   - {broken_link}")
                if len(broken_links) > 5:
                    print(f"   ... and {len(broken_links) - 5} more")
            else:
                print(f"✓ All {total_links} links validated successfully")
            
            # Update MkDocs navigation
            print("\n📚 Updating MkDocs navigation...")
            if self.update_mkdocs_nav([doc for doc, _ in operations_docs]):
                print("✓ MkDocs navigation updated")
            else:
                result.warnings.append("Failed to update MkDocs navigation")
            
            result.success = True
            
        except Exception as e:
            result.errors.append(f"Execution failed: {str(e)}")
            print(f"\n❌ Error: {e}")
        
        finally:
            result.duration_seconds = (datetime.now() - start_time).total_seconds()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 Documentation Generation Summary")
        print("=" * 60)
        print(f"✅ Generated: {len(result.docs_generated)} files")
        print(f"🔗 Links validated: {result.links_validated}")
        print(f"⚠️  Broken links: {len(result.links_broken)}")
        print(f"⏱️  Duration: {result.duration_seconds:.2f}s")
        print("=" * 60)
        
        return result


def main():
    """Main entry point for documentation generator."""
    import argparse
    
    parser = argparse.ArgumentParser(description="CORTEX Documentation Generator")
    parser.add_argument('--cortex-root', type=str, help="Path to CORTEX root directory")
    parser.add_argument('--config', type=str, help="Path to custom configuration file")
    
    args = parser.parse_args()
    
    # Determine CORTEX root
    cortex_root = Path(args.cortex_root) if args.cortex_root else Path.cwd()
    
    # Create generator
    generator = DocumentationGenerator(cortex_root)
    
    # Override config file if provided
    if args.config:
        generator.config_file = Path(args.config)
    
    # Execute
    result = generator.execute()
    
    # Exit with appropriate code
    sys.exit(0 if result.success else 1)


if __name__ == "__main__":
    main()
