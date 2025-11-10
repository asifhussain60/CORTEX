"""
Generate API documentation module for automated documentation.

Part of the Documentation Update operation - creates API reference from docstrings.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import os
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

from src.operations.base_operation_module import (
    BaseOperationModule,
    OperationModuleMetadata,
    OperationResult,
    OperationPhase,
    OperationStatus
)


class GenerateAPIDocsModule(BaseOperationModule):
    """
    Generate API documentation from docstring index.
    
    Takes the structured docstring index from scan_docstrings module
    and generates Markdown API reference documentation organized by
    module hierarchy.
    """
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Get module metadata."""
        return OperationModuleMetadata(
            module_id="generate_api_docs",
            name="Generate API Documentation",
            description="Create API reference from docstrings",
            phase=OperationPhase.PROCESSING,
            priority=10
        )
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Execute API documentation generation.
        
        Args:
            context: Operation context with docstring_index
            
        Returns:
            OperationResult with generated documentation info
        """
        try:
            # Get docstring index from context
            docstring_index = context.get("docstring_index")
            if not docstring_index:
                return OperationResult(
                    success=False,
                    status=OperationStatus.FAILED,
                    message="No docstring index found in context",
                    errors=["scan_docstrings must run first"]
                )
            
            project_root = Path(context.get("project_root", os.getcwd()))
            docs_dir = project_root / "docs" / "api"
            docs_dir.mkdir(parents=True, exist_ok=True)
            
            self.log_info(f"Generating API documentation in {docs_dir}")
            
            # Generate documentation by module
            generated_files = []
            
            # Group by module path
            modules_map = self._group_by_module(docstring_index)
            
            # Generate index file
            index_file = self._generate_index(modules_map, docs_dir)
            generated_files.append(index_file)
            
            # Generate module documentation files
            for module_path, items in modules_map.items():
                module_file = self._generate_module_doc(module_path, items, docs_dir)
                if module_file:
                    generated_files.append(module_file)
            
            self.log_info(f"Generated {len(generated_files)} API documentation files")
            
            return OperationResult(
                success=True,
                status=OperationStatus.SUCCESS,
                message=f"Generated API docs for {len(modules_map)} modules",
                data={
                    "generated_files": generated_files,
                    "modules_documented": len(modules_map),
                    "output_directory": str(docs_dir)
                }
            )
            
        except Exception as e:
            self.log_error(f"Failed to generate API docs: {e}")
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message="API documentation generation failed",
                errors=[str(e)]
            )
    
    def _group_by_module(self, docstring_index: Dict[str, Any]) -> Dict[str, List[Dict]]:
        """
        Group docstrings by module path.
        
        Args:
            docstring_index: Docstring index from scan_docstrings
            
        Returns:
            Dictionary mapping module paths to their docstrings
        """
        modules_map = {}
        
        # Process all types of docstrings
        for doc_type in ["modules", "classes", "functions", "methods"]:
            for item in docstring_index.get(doc_type, []):
                module_path = item["module_path"]
                if module_path not in modules_map:
                    modules_map[module_path] = []
                
                item_copy = item.copy()
                item_copy["type"] = doc_type.rstrip("s")  # Remove plural
                modules_map[module_path].append(item_copy)
        
        return modules_map
    
    def _generate_index(self, modules_map: Dict[str, List[Dict]], docs_dir: Path) -> str:
        """
        Generate API documentation index.
        
        Args:
            modules_map: Module documentation mapping
            docs_dir: Documentation output directory
            
        Returns:
            Path to generated index file
        """
        index_file = docs_dir / "index.md"
        
        content = [
            "# CORTEX API Reference",
            "",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Modules",
            ""
        ]
        
        # Sort modules alphabetically
        sorted_modules = sorted(modules_map.keys())
        
        for module_path in sorted_modules:
            items = modules_map[module_path]
            module_name = module_path.split('.')[-1]
            
            # Count types
            classes = sum(1 for i in items if i["type"] == "class")
            functions = sum(1 for i in items if i["type"] == "function")
            
            # Create link
            module_file = module_path.replace('.', '_') + '.md'
            content.append(f"- [{module_path}]({module_file}) - {classes} classes, {functions} functions")
        
        content.append("")
        
        index_file.write_text("\n".join(content), encoding="utf-8")
        return str(index_file)
    
    def _generate_module_doc(self, module_path: str, items: List[Dict], docs_dir: Path) -> str:
        """
        Generate documentation for a single module.
        
        Args:
            module_path: Module path (e.g., "src.tier1.conversation_memory")
            items: Docstring items for this module
            docs_dir: Documentation output directory
            
        Returns:
            Path to generated module file
        """
        # Create filename from module path
        filename = module_path.replace('.', '_') + '.md'
        module_file = docs_dir / filename
        
        content = [
            f"# {module_path}",
            ""
        ]
        
        # Add module-level docstring if available
        module_items = [i for i in items if i["type"] == "module"]
        if module_items:
            content.append(module_items[0]["docstring"])
            content.append("")
        
        # Group by type
        classes = [i for i in items if i["type"] == "class"]
        functions = [i for i in items if i["type"] == "function"]
        methods = [i for i in items if i["type"] == "method"]
        
        # Document classes
        if classes:
            content.append("## Classes")
            content.append("")
            
            for cls in classes:
                content.extend(self._format_class(cls, methods))
                content.append("")
        
        # Document functions
        if functions:
            content.append("## Functions")
            content.append("")
            
            for func in functions:
                content.extend(self._format_function(func))
                content.append("")
        
        module_file.write_text("\n".join(content), encoding="utf-8")
        return str(module_file)
    
    def _format_class(self, cls: Dict, all_methods: List[Dict]) -> List[str]:
        """
        Format class documentation.
        
        Args:
            cls: Class docstring info
            all_methods: All methods from module
            
        Returns:
            Formatted documentation lines
        """
        lines = [
            f"### {cls['name']}",
            ""
        ]
        
        if cls.get("docstring"):
            lines.append(cls["docstring"])
            lines.append("")
        
        # Find methods for this class
        class_methods = [m for m in all_methods if m.get("parent_class") == cls["name"]]
        
        if class_methods:
            lines.append("**Methods:**")
            lines.append("")
            
            for method in class_methods:
                signature = method.get("signature", method["name"] + "()")
                lines.append(f"#### `{signature}`")
                lines.append("")
                
                if method.get("docstring"):
                    lines.append(method["docstring"])
                    lines.append("")
        
        return lines
    
    def _format_function(self, func: Dict) -> List[str]:
        """
        Format function documentation.
        
        Args:
            func: Function docstring info
            
        Returns:
            Formatted documentation lines
        """
        signature = func.get("signature", func["name"] + "()")
        
        lines = [
            f"### `{signature}`",
            ""
        ]
        
        if func.get("docstring"):
            lines.append(func["docstring"])
        
        return lines


def register() -> BaseOperationModule:
    """Register module for discovery."""
    return GenerateAPIDocsModule()
