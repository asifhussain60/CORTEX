"""
Orchestration Documentation Generator

Generates comprehensive documentation for CORTEX orchestrators including:
- Automated discovery of all orchestrator files
- AST-based metadata extraction (classes, methods, docstrings)
- Mermaid workflow diagrams
- Structured markdown documentation pages

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
import ast
import logging
import re

from .base_generator import (
    BaseDocumentationGenerator,
    GenerationConfig,
    GenerationResult,
    GeneratorType
)

logger = logging.getLogger(__name__)


class OrchestrationDocsGenerator(BaseDocumentationGenerator):
    """
    Generate documentation for CORTEX orchestrators.
    
    Discovers all orchestrator files in src/orchestrators/, extracts metadata
    using AST parsing, generates Mermaid workflow diagrams, and creates
    comprehensive markdown documentation.
    
    Output Structure:
        docs/orchestration/{orchestrator-name}.md - Main documentation
        docs/diagrams/orchestration/{orchestrator-name}-workflow.mmd - Workflow diagram
    """
    
    def __init__(self, config: GenerationConfig, workspace_root: Optional[Path] = None):
        super().__init__(config, workspace_root)
        self.docs_path = self.config.output_path
        self.orchestrators_path = self.workspace_root / "src" / "orchestrators"
        self.orchestration_docs_path = self.docs_path / "orchestration"
        self.diagram_path = self.docs_path / "diagrams" / "orchestration"
        
        # Ensure output directories exist
        self.orchestration_docs_path.mkdir(parents=True, exist_ok=True)
        self.diagram_path.mkdir(parents=True, exist_ok=True)
    
    def get_component_name(self) -> str:
        return "Orchestration Documentation"
    
    def collect_data(self) -> Dict[str, Any]:
        """
        Collect orchestrator data for documentation generation.
        
        Returns:
            Dictionary with orchestrator metadata
        """
        orchestrators = self._discover_orchestrators()
        
        data = {
            "generated_at": self._get_timestamp(),
            "orchestrator_count": len(orchestrators),
            "orchestrators": []
        }
        
        for orchestrator_file in orchestrators:
            try:
                metadata = self._extract_metadata(orchestrator_file)
                metadata["file_path"] = str(orchestrator_file.relative_to(self.workspace_root))
                data["orchestrators"].append(metadata)
            except Exception as e:
                self.record_warning(f"Failed to extract metadata from {orchestrator_file.name}: {e}")
        
        return data
    
    def generate(self) -> GenerationResult:
        """
        Generate orchestration documentation.
        
        Returns:
            GenerationResult with files generated
        """
        logger.info("Generating orchestration documentation...")
        
        data = self.collect_data()
        
        for orchestrator in data["orchestrators"]:
            try:
                # Generate workflow diagram
                diagram_content = self._generate_workflow_diagram(orchestrator)
                diagram_file = self.diagram_path / f"{orchestrator['name'].lower().replace('_', '-')}-workflow.mmd"
                diagram_file.write_text(diagram_content)
                self.files_generated.append(diagram_file)
                
                # Generate documentation page
                doc_content = self._generate_documentation_page(orchestrator, diagram_file)
                doc_file = self.orchestration_docs_path / f"{orchestrator['name'].lower().replace('_', '-')}.md"
                doc_file.write_text(doc_content)
                self.files_generated.append(doc_file)
                
            except Exception as e:
                self.record_error(f"Failed to generate docs for {orchestrator['name']}: {e}")
        
        # Generate index page
        index_content = self._generate_index_page(data)
        index_file = self.orchestration_docs_path / "index.md"
        index_file.write_text(index_content)
        self.files_generated.append(index_file)
        
        return self._create_success_result(metadata={
            "orchestrators_documented": len(data["orchestrators"]),
            "files_generated": len(self.files_generated),
            "warnings": len(self.warnings),
            "errors": len(self.errors)
        })
    
    def validate(self) -> bool:
        """
        Validate generated documentation.
        
        Returns:
            True if validation passes
        """
        # Check that files were generated
        if not self.files_generated:
            self.record_error("No files were generated")
            return False
        
        # Check that all generated files exist
        for file_path in self.files_generated:
            if not file_path.exists():
                self.record_error(f"Generated file does not exist: {file_path}")
                return False
            
            if file_path.stat().st_size == 0:
                self.record_error(f"Generated file is empty: {file_path}")
                return False
        
        return len(self.errors) == 0
    
    def _discover_orchestrators(self) -> List[Path]:
        """
        Discover all orchestrator files in src/orchestrators/.
        
        Returns:
            List of Path objects for orchestrator files
        """
        if not self.orchestrators_path.exists():
            self.record_warning(f"Orchestrators path does not exist: {self.orchestrators_path}")
            return []
        
        orchestrators = []
        for file_path in self.orchestrators_path.glob("*.py"):
            # Skip __init__.py and test files
            if file_path.name == "__init__.py" or file_path.name.startswith("test_"):
                continue
            
            orchestrators.append(file_path)
        
        return sorted(orchestrators)
    
    def _extract_metadata(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract metadata from orchestrator file using AST parsing.
        
        Args:
            file_path: Path to orchestrator file
            
        Returns:
            Dictionary with extracted metadata
        """
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content)
        
        metadata = {
            "name": file_path.stem,
            "module_docstring": ast.get_docstring(tree),
            "classes": [],
            "functions": [],
            "imports": []
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_info = {
                    "name": node.name,
                    "docstring": ast.get_docstring(node),
                    "methods": [],
                    "bases": [self._get_name(base) for base in node.bases]
                }
                
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        method_info = {
                            "name": item.name,
                            "docstring": ast.get_docstring(item),
                            "params": [arg.arg for arg in item.args.args],
                            "is_async": isinstance(item, ast.AsyncFunctionDef)
                        }
                        class_info["methods"].append(method_info)
                
                metadata["classes"].append(class_info)
            
            elif isinstance(node, ast.FunctionDef) and node.col_offset == 0:
                # Top-level functions only
                func_info = {
                    "name": node.name,
                    "docstring": ast.get_docstring(node),
                    "params": [arg.arg for arg in node.args.args]
                }
                metadata["functions"].append(func_info)
        
        return metadata
    
    def _get_name(self, node) -> str:
        """Extract name from AST node"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        return str(node)
    
    def _generate_workflow_diagram(self, metadata: Dict[str, Any]) -> str:
        """
        Generate Mermaid workflow diagram for orchestrator.
        
        Args:
            metadata: Orchestrator metadata
            
        Returns:
            Mermaid diagram content
        """
        lines = [
            "flowchart TD",
            f"    Start([{metadata['name']}])",
            ""
        ]
        
        # Find main orchestrator class (usually has most methods)
        main_class = None
        if metadata["classes"]:
            main_class = max(metadata["classes"], key=lambda c: len(c["methods"]))
        
        if main_class:
            lines.append(f"    Init[Initialize {main_class['name']}]")
            lines.append("    Start --> Init")
            lines.append("")
            
            # Add methods as workflow steps
            for i, method in enumerate(main_class["methods"]):
                if method["name"].startswith("_") and not method["name"].startswith("__"):
                    continue  # Skip private methods
                
                method_id = f"M{i}"
                method_label = method["name"].replace("_", " ").title()
                lines.append(f"    {method_id}[{method_label}]")
                
                if i == 0:
                    lines.append(f"    Init --> {method_id}")
                else:
                    lines.append(f"    M{i-1} --> {method_id}")
            
            lines.append("")
            lines.append(f"    M{len(main_class['methods'])-1} --> End([Complete])")
        else:
            lines.append("    Init[No workflow detected]")
            lines.append("    Start --> Init")
            lines.append("    Init --> End([Complete])")
        
        return "\n".join(lines)
    
    def _generate_documentation_page(self, metadata: Dict[str, Any], diagram_file: Path) -> str:
        """
        Generate markdown documentation page for orchestrator.
        
        Args:
            metadata: Orchestrator metadata
            diagram_file: Path to workflow diagram
            
        Returns:
            Markdown content
        """
        lines = [
            f"# {metadata['name'].replace('_', ' ').title()}",
            "",
            "**Author:** Asif Hussain | **Copyright:** © 2024-2025 Asif Hussain. All rights reserved.",
            "",
            "---",
            ""
        ]
        
        # Module docstring
        if metadata["module_docstring"]:
            lines.append("## Overview")
            lines.append("")
            lines.append(metadata["module_docstring"])
            lines.append("")
        
        # Workflow diagram
        diagram_rel_path = diagram_file.relative_to(self.docs_path)
        lines.append("## Workflow")
        lines.append("")
        lines.append("```mermaid")
        lines.append(diagram_file.read_text())
        lines.append("```")
        lines.append("")
        
        # Classes
        for class_info in metadata["classes"]:
            lines.append(f"## Class: {class_info['name']}")
            lines.append("")
            
            if class_info["docstring"]:
                lines.append(class_info["docstring"])
                lines.append("")
            
            if class_info["bases"]:
                lines.append(f"**Inherits from:** {', '.join(class_info['bases'])}")
                lines.append("")
            
            # Methods
            if class_info["methods"]:
                lines.append("### Methods")
                lines.append("")
                
                for method in class_info["methods"]:
                    if method["name"].startswith("__") and method["name"] != "__init__":
                        continue  # Skip dunder methods except __init__
                    
                    async_marker = "async " if method["is_async"] else ""
                    params_str = ", ".join(method["params"])
                    lines.append(f"#### `{async_marker}{method['name']}({params_str})`")
                    lines.append("")
                    
                    if method["docstring"]:
                        lines.append(method["docstring"])
                        lines.append("")
        
        # Top-level functions
        if metadata["functions"]:
            lines.append("## Functions")
            lines.append("")
            
            for func in metadata["functions"]:
                params_str = ", ".join(func["params"])
                lines.append(f"### `{func['name']}({params_str})`")
                lines.append("")
                
                if func["docstring"]:
                    lines.append(func["docstring"])
                    lines.append("")
        
        # File location
        lines.append("---")
        lines.append("")
        lines.append(f"**Source:** `{metadata.get('file_path', 'Unknown')}`")
        lines.append("")
        
        return "\n".join(lines)
    
    def _generate_index_page(self, data: Dict[str, Any]) -> str:
        """
        Generate index page listing all orchestrators.
        
        Args:
            data: Collected orchestrator data
            
        Returns:
            Markdown content
        """
        lines = [
            "# CORTEX Orchestrators",
            "",
            "**Author:** Asif Hussain | **Copyright:** © 2024-2025 Asif Hussain. All rights reserved.",
            "",
            "---",
            "",
            "## Overview",
            "",
            f"CORTEX orchestration system contains **{data['orchestrator_count']} orchestrators** that coordinate complex workflows.",
            "",
            "## Orchestrator Catalog",
            ""
        ]
        
        for orchestrator in sorted(data["orchestrators"], key=lambda x: x["name"]):
            doc_file = f"{orchestrator['name'].lower().replace('_', '-')}.md"
            title = orchestrator["name"].replace("_", " ").title()
            
            lines.append(f"### [{title}]({doc_file})")
            lines.append("")
            
            # Get first line of module docstring as summary
            if orchestrator["module_docstring"]:
                summary = orchestrator["module_docstring"].split("\n")[0]
                lines.append(summary)
                lines.append("")
        
        lines.append("---")
        lines.append("")
        lines.append(f"*Generated: {data['generated_at']}*")
        lines.append("")
        
        return "\n".join(lines)
    
    def _get_timestamp(self) -> str:
        """Get formatted timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
