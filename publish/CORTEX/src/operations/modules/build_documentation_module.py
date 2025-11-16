"""
Build documentation module for documentation generation.

Part of the Documentation Update operation - transforms docstrings into structured Markdown files.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

from src.operations.base_operation_module import (
    BaseOperationModule,
    OperationModuleMetadata,
    OperationResult,
    OperationPhase,
    OperationStatus
)


class BuildDocumentationModule(BaseOperationModule):
    """
    Build documentation from docstring index.
    
    Transforms the docstring index from ScanDocstringsModule into:
    - Markdown reference documentation
    - Module hierarchy pages
    - API reference index
    - Search-friendly structure
    
    Output format compatible with MkDocs, GitHub Pages, and static site generators.
    """
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Get module metadata."""
        return OperationModuleMetadata(
            module_id="build_documentation",
            name="Build Documentation",
            description="Generate Markdown documentation from docstrings",
            phase=OperationPhase.PROCESSING,
            priority=20,
            dependencies=["scan_docstrings"]
        )
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Execute documentation building.
        
        Args:
            context: Operation context with docstring_index from scan module
            
        Returns:
            OperationResult with build status and file paths
        """
        try:
            # Get docstring index from context
            docstring_index = context.get("docstring_index")
            if not docstring_index:
                return OperationResult(
                    success=False,
                    status=OperationStatus.FAILED,
                    message="No docstring index found in context",
                    errors=["docstring_index missing from context"]
                )
            
            project_root = Path(context.get("project_root", os.getcwd()))
            output_dir = project_root / "docs" / "api"
            
            self.log_info(f"Building documentation in {output_dir}")
            
            # Create output directory
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Build documentation files
            files_created = []
            
            # 1. Generate module documentation
            module_files = self._build_module_docs(
                docstring_index.get("modules", []),
                output_dir
            )
            files_created.extend(module_files)
            
            # 2. Generate class documentation
            class_files = self._build_class_docs(
                docstring_index.get("classes", []),
                output_dir
            )
            files_created.extend(class_files)
            
            # 3. Generate function documentation
            function_files = self._build_function_docs(
                docstring_index.get("functions", []),
                output_dir
            )
            files_created.extend(function_files)
            
            # 4. Generate index page
            index_file = self._build_index(docstring_index, output_dir)
            files_created.append(index_file)
            
            # 5. Generate navigation structure
            nav_file = self._build_navigation(docstring_index, output_dir)
            files_created.append(nav_file)
            
            stats = docstring_index.get("stats", {})
            
            self.log_info(
                f"Built {len(files_created)} documentation files "
                f"({stats.get('modules', 0)} modules, "
                f"{stats.get('classes', 0)} classes, "
                f"{stats.get('functions', 0)} functions)"
            )
            
            return OperationResult(
                success=True,
                status=OperationStatus.SUCCESS,
                message=f"Generated {len(files_created)} documentation files",
                data={
                    "output_dir": str(output_dir),
                    "files_created": [str(f) for f in files_created],
                    "total_files": len(files_created),
                    "stats": stats
                }
            )
            
        except Exception as e:
            self.log_error(f"Failed to build documentation: {e}")
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message="Documentation build failed",
                errors=[str(e)]
            )
    
    def _build_module_docs(self, modules: List[Dict], output_dir: Path) -> List[Path]:
        """
        Build module documentation files.
        
        Args:
            modules: List of module docstring info
            output_dir: Output directory
            
        Returns:
            List of created file paths
        """
        files = []
        modules_dir = output_dir / "modules"
        modules_dir.mkdir(exist_ok=True)
        
        for module in modules:
            module_path = module["module_path"]
            safe_name = module_path.replace(".", "_")
            
            content = self._format_module_page(module)
            
            file_path = modules_dir / f"{safe_name}.md"
            file_path.write_text(content, encoding='utf-8')
            files.append(file_path)
        
        return files
    
    def _build_class_docs(self, classes: List[Dict], output_dir: Path) -> List[Path]:
        """
        Build class documentation files.
        
        Args:
            classes: List of class docstring info
            output_dir: Output directory
            
        Returns:
            List of created file paths
        """
        files = []
        classes_dir = output_dir / "classes"
        classes_dir.mkdir(exist_ok=True)
        
        # Group classes by module
        classes_by_module = {}
        for cls in classes:
            module = cls["module_path"]
            if module not in classes_by_module:
                classes_by_module[module] = []
            classes_by_module[module].append(cls)
        
        # Generate one file per module with all its classes
        for module, module_classes in classes_by_module.items():
            safe_name = module.replace(".", "_")
            
            content = self._format_class_page(module, module_classes)
            
            file_path = classes_dir / f"{safe_name}.md"
            file_path.write_text(content, encoding='utf-8')
            files.append(file_path)
        
        return files
    
    def _build_function_docs(self, functions: List[Dict], output_dir: Path) -> List[Path]:
        """
        Build function documentation files.
        
        Args:
            functions: List of function docstring info
            output_dir: Output directory
            
        Returns:
            List of created file paths
        """
        files = []
        functions_dir = output_dir / "functions"
        functions_dir.mkdir(exist_ok=True)
        
        # Group functions by module
        functions_by_module = {}
        for func in functions:
            module = func["module_path"]
            if module not in functions_by_module:
                functions_by_module[module] = []
            functions_by_module[module].append(func)
        
        # Generate one file per module with all its functions
        for module, module_functions in functions_by_module.items():
            safe_name = module.replace(".", "_")
            
            content = self._format_function_page(module, module_functions)
            
            file_path = functions_dir / f"{safe_name}.md"
            file_path.write_text(content, encoding='utf-8')
            files.append(file_path)
        
        return files
    
    def _build_index(self, docstring_index: Dict, output_dir: Path) -> Path:
        """
        Build API reference index page.
        
        Args:
            docstring_index: Complete docstring index
            output_dir: Output directory
            
        Returns:
            Path to index file
        """
        stats = docstring_index.get("stats", {})
        
        content = f"""# API Reference

Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overview

This API reference provides comprehensive documentation for all CORTEX modules, classes, and functions.

**Statistics:**
- **Modules:** {stats.get('modules', 0)}
- **Classes:** {stats.get('classes', 0)}
- **Functions:** {stats.get('functions', 0)}
- **Methods:** {stats.get('methods', 0)}

## Documentation Structure

- [Modules](modules/) - Module-level documentation
- [Classes](classes/) - Class reference documentation
- [Functions](functions/) - Function reference documentation

## Quick Links

### Core Modules

"""
        
        # Add module links
        modules = docstring_index.get("modules", [])
        for module in sorted(modules, key=lambda m: m["module_path"])[:10]:
            safe_name = module["module_path"].replace(".", "_")
            content += f"- [{module['module_path']}](modules/{safe_name}.md)\n"
        
        if len(modules) > 10:
            content += f"\n*...and {len(modules) - 10} more modules*\n"
        
        content += "\n---\n\n*Documentation generated by CORTEX Documentation Operation*\n"
        
        file_path = output_dir / "index.md"
        file_path.write_text(content, encoding='utf-8')
        
        return file_path
    
    def _build_navigation(self, docstring_index: Dict, output_dir: Path) -> Path:
        """
        Build navigation structure for MkDocs.
        
        Args:
            docstring_index: Complete docstring index
            output_dir: Output directory
            
        Returns:
            Path to navigation file
        """
        nav = {
            "nav": [
                {"API Reference": "api/index.md"},
                {"Modules": []},
                {"Classes": []},
                {"Functions": []}
            ]
        }
        
        # Add module links
        for module in docstring_index.get("modules", [])[:20]:
            safe_name = module["module_path"].replace(".", "_")
            nav["nav"][1]["Modules"].append({
                module["module_path"]: f"api/modules/{safe_name}.md"
            })
        
        file_path = output_dir / "nav.json"
        file_path.write_text(json.dumps(nav, indent=2), encoding='utf-8')
        
        return file_path
    
    def _format_module_page(self, module: Dict) -> str:
        """Format a module documentation page."""
        content = f"""# Module: `{module['module_path']}`

{module.get('docstring', 'No module documentation available.')}

---

**Module Path:** `{module['module_path']}`  
**Source Line:** {module.get('line_number', 'N/A')}

## Related Documentation

- [View Source Code](../../{module['module_path'].replace('.', '/')}.py)

---

*Generated by CORTEX Documentation Operation*
"""
        return content
    
    def _format_class_page(self, module: str, classes: List[Dict]) -> str:
        """Format a class documentation page."""
        content = f"""# Classes: `{module}`

## Overview

This module contains {len(classes)} class(es).

---

"""
        
        for cls in classes:
            content += f"""## Class: `{cls['name']}`

{cls.get('docstring', 'No class documentation available.')}

**Module:** `{cls['module_path']}`  
**Source Line:** {cls.get('line_number', 'N/A')}

"""
            
            # Add methods if available
            methods = [m for m in cls.get('methods', []) if m]
            if methods:
                content += "### Methods\n\n"
                for method in methods:
                    sig = method.get('signature', method['name'])
                    content += f"- `{sig}` (line {method.get('line_number', 'N/A')})\n"
                content += "\n"
            
            content += "---\n\n"
        
        content += "*Generated by CORTEX Documentation Operation*\n"
        return content
    
    def _format_function_page(self, module: str, functions: List[Dict]) -> str:
        """Format a function documentation page."""
        content = f"""# Functions: `{module}`

## Overview

This module contains {len(functions)} function(s).

---

"""
        
        for func in functions:
            sig = func.get('signature', func['name'])
            
            content += f"""## Function: `{sig}`

{func.get('docstring', 'No function documentation available.')}

**Module:** `{func['module_path']}`  
**Source Line:** {func.get('line_number', 'N/A')}

---

"""
        
        content += "*Generated by CORTEX Documentation Operation*\n"
        return content
