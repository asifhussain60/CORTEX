"""
API Documentation Generator - Generate comprehensive API docs

Creates structured API documentation from analyzed code:
- Module overview
- Class documentation with methods
- Function documentation
- Type signatures
- Usage examples
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from ..extractors.code_analyzer import ClassInfo, FunctionInfo, MethodInfo, ModuleInfo
from ..extractors.type_extractor import TypeExtractor


class APIDocGenerator:
    """
    Generates comprehensive API documentation in Markdown format
    
    Creates documentation with:
    - Table of contents
    - Module overview
    - Class documentation
    - Method signatures with type hints
    - Parameter descriptions
    - Return value documentation
    - Usage examples
    """
    
    def __init__(self):
        self.type_extractor = TypeExtractor()
        self.logger = None
    
    def generate_module_docs(
        self,
        module_info: ModuleInfo,
        output_path: Path,
        include_private: bool = False
    ) -> Path:
        """
        Generate complete documentation for a module
        
        Args:
            module_info: Analyzed module information
            output_path: Where to save the Markdown documentation
            include_private: Whether to document private methods (starting with _)
            
        Returns:
            Path to generated Markdown file
        """
        sections = []
        
        # Header
        sections.append(f"# {module_info.name}\n")
        
        # Module docstring
        if module_info.docstring:
            sections.append(module_info.docstring)
            sections.append("\n")
        
        # Table of contents
        sections.append(self._generate_toc(module_info, include_private))
        
        # Overview section
        sections.append(self._generate_overview(module_info))
        
        # Classes
        if module_info.classes:
            sections.append("## Classes\n")
            for cls in module_info.classes:
                sections.append(self._generate_class_docs(cls, include_private))
        
        # Functions
        if module_info.functions:
            sections.append("## Functions\n")
            for func in module_info.functions:
                if include_private or not func.name.startswith('_'):
                    sections.append(self._generate_function_docs(func))
        
        # Write to file
        content = '\n'.join(sections)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding='utf-8')
        
        return output_path
    
    def generate_multi_module_docs(
        self,
        modules: List[ModuleInfo],
        output_dir: Path,
        index_name: str = "index.md"
    ) -> Path:
        """
        Generate documentation for multiple modules with index
        
        Args:
            modules: List of analyzed modules
            output_dir: Directory to save documentation
            index_name: Name of the index file
            
        Returns:
            Path to index file
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate individual module docs
        module_files = []
        for module in modules:
            output_path = output_dir / f"{module.name}.md"
            self.generate_module_docs(module, output_path)
            module_files.append((module.name, output_path.name))
        
        # Generate index
        index_content = self._generate_index(modules, module_files)
        index_path = output_dir / index_name
        index_path.write_text(index_content, encoding='utf-8')
        
        return index_path
    
    def _generate_toc(self, module_info: ModuleInfo, include_private: bool) -> str:
        """Generate table of contents"""
        lines = ["## Table of Contents\n"]
        
        if module_info.classes:
            lines.append("### Classes")
            for cls in module_info.classes:
                lines.append(f"- [{cls.name}](#{cls.name.lower()})")
        
        if module_info.functions:
            lines.append("\n### Functions")
            for func in module_info.functions:
                if include_private or not func.name.startswith('_'):
                    lines.append(f"- [{func.name}](#{func.name.lower()})")
        
        lines.append("\n")
        return '\n'.join(lines)
    
    def _generate_overview(self, module_info: ModuleInfo) -> str:
        """Generate module overview section"""
        lines = ["## Overview\n"]
        
        # Statistics
        class_count = len(module_info.classes)
        function_count = len(module_info.functions)
        lines.append(f"- **Classes:** {class_count}")
        lines.append(f"- **Functions:** {function_count}")
        
        # Dependencies
        if module_info.dependencies:
            deps = sorted(module_info.dependencies)
            lines.append(f"- **Dependencies:** {', '.join(deps)}")
        
        lines.append("\n")
        return '\n'.join(lines)
    
    def _generate_class_docs(self, cls: ClassInfo, include_private: bool) -> str:
        """Generate documentation for a class"""
        lines = [f"### {cls.name}\n"]
        
        # Class signature
        if cls.base_classes:
            bases = ', '.join(cls.base_classes)
            lines.append(f"```python\nclass {cls.name}({bases})\n```\n")
        else:
            lines.append(f"```python\nclass {cls.name}\n```\n")
        
        # Decorators
        if cls.decorators:
            lines.append(f"**Decorators:** `{'`, `'.join(cls.decorators)}`\n")
        
        # Docstring
        if cls.docstring:
            lines.append(cls.docstring)
            lines.append("\n")
        
        # Attributes
        if cls.attributes:
            lines.append("**Attributes:**\n")
            for attr in cls.attributes:
                attr_type = attr.get('type', 'Any')
                lines.append(f"- `{attr['name']}`: {attr_type}")
            lines.append("\n")
        
        # Methods
        if cls.methods:
            lines.append("**Methods:**\n")
            for method in cls.methods:
                if include_private or not method.name.startswith('_'):
                    lines.append(self._generate_method_docs(method, indent=True))
        
        lines.append("\n---\n")
        return '\n'.join(lines)
    
    def _generate_method_docs(self, method: MethodInfo, indent: bool = False) -> str:
        """Generate documentation for a method"""
        prefix = "  " if indent else ""
        lines = []
        
        # Method signature
        lines.append(f"{prefix}#### `{method.name}`\n")
        
        if method.decorators:
            decorators_str = ', '.join(method.decorators)
            lines.append(f"{prefix}*Decorators:* `{decorators_str}`\n")
        
        # Signature with syntax highlighting
        lines.append(f"{prefix}```python\n{prefix}{method.signature}\n{prefix}```\n")
        
        # Docstring
        if method.docstring:
            # Extract parameter descriptions
            param_descriptions = self.type_extractor.extract_param_descriptions(method.docstring)
            
            lines.append(f"{prefix}{method.docstring}\n")
            
            # Enhanced parameter documentation
            if method.parameters:
                lines.append(f"{prefix}**Parameters:**\n")
                for param in method.parameters:
                    param_name = param['name'].lstrip('*')
                    param_type = param.get('type', 'Any')
                    param_desc = param_descriptions.get(param_name, '')
                    
                    param_line = f"{prefix}- `{param['name']}`"
                    if param_type:
                        param_line += f" ({param_type})"
                    if param.get('default'):
                        param_line += f" = `{param['default']}`"
                    if param_desc:
                        param_line += f": {param_desc}"
                    
                    lines.append(param_line)
                lines.append("\n")
            
            # Return type documentation
            if method.return_type:
                return_desc = self.type_extractor.extract_return_type_description(method.docstring)
                lines.append(f"{prefix}**Returns:** {method.return_type}")
                if return_desc:
                    lines.append(f"{prefix}  {return_desc}")
                lines.append("\n")
        
        return '\n'.join(lines)
    
    def _generate_function_docs(self, func: FunctionInfo) -> str:
        """Generate documentation for a standalone function"""
        lines = [f"### {func.name}\n"]
        
        # Signature
        lines.append(f"```python\n{func.signature}\n```\n")
        
        # Decorators
        if func.decorators:
            lines.append(f"**Decorators:** `{'`, `'.join(func.decorators)}`\n")
        
        # Docstring
        if func.docstring:
            param_descriptions = self.type_extractor.extract_param_descriptions(func.docstring)
            lines.append(func.docstring)
            lines.append("\n")
            
            # Parameters
            if func.parameters:
                lines.append("**Parameters:**\n")
                for param in func.parameters:
                    param_name = param['name'].lstrip('*')
                    param_type = param.get('type', 'Any')
                    param_desc = param_descriptions.get(param_name, '')
                    
                    param_line = f"- `{param['name']}`"
                    if param_type:
                        param_line += f" ({param_type})"
                    if param.get('default'):
                        param_line += f" = `{param['default']}`"
                    if param_desc:
                        param_line += f": {param_desc}"
                    
                    lines.append(param_line)
                lines.append("\n")
            
            # Return type
            if func.return_type:
                return_desc = self.type_extractor.extract_return_type_description(func.docstring)
                lines.append(f"**Returns:** {func.return_type}")
                if return_desc:
                    lines.append(f"  {return_desc}")
                lines.append("\n")
        
        lines.append("---\n")
        return '\n'.join(lines)
    
    def _generate_index(
        self,
        modules: List[ModuleInfo],
        module_files: List[tuple]
    ) -> str:
        """Generate index page for multi-module documentation"""
        lines = ["# API Documentation\n"]
        
        lines.append("## Modules\n")
        for module_name, file_name in module_files:
            module_info = next(m for m in modules if m.name == module_name)
            class_count = len(module_info.classes)
            func_count = len(module_info.functions)
            
            lines.append(f"### [{module_name}]({file_name})\n")
            if module_info.docstring:
                # First line of docstring
                first_line = module_info.docstring.split('\n')[0]
                lines.append(f"{first_line}\n")
            lines.append(f"- Classes: {class_count}")
            lines.append(f"- Functions: {func_count}\n")
        
        return '\n'.join(lines)
    
    def generate_quick_reference(
        self,
        modules: List[ModuleInfo],
        output_path: Path
    ) -> Path:
        """
        Generate a quick reference guide
        
        Compact single-page reference with all APIs
        
        Args:
            modules: List of analyzed modules
            output_path: Where to save the quick reference
            
        Returns:
            Path to generated file
        """
        lines = ["# Quick Reference\n"]
        
        for module in modules:
            lines.append(f"## {module.name}\n")
            
            # Classes
            for cls in module.classes:
                lines.append(f"### `{cls.name}`")
                if cls.base_classes:
                    lines.append(f" (inherits: {', '.join(cls.base_classes)})")
                lines.append("\n")
                
                # Method signatures only
                for method in cls.methods:
                    if not method.name.startswith('_'):
                        lines.append(f"- `{method.signature}`")
                lines.append("\n")
            
            # Functions
            for func in module.functions:
                if not func.name.startswith('_'):
                    lines.append(f"- `{func.signature}`")
            lines.append("\n")
        
        content = '\n'.join(lines)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding='utf-8')
        
        return output_path
