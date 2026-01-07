"""
Orchestration Documentation Generator

Generates comprehensive documentation for CORTEX orchestrators including:
- Automated discovery of all orchestrator files
- AST-based metadata extraction (classes, methods, docstrings)
- Mermaid workflow diagrams embedded in HTML
- Glassmorphism-styled HTML documentation pages

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
import ast
import logging
import re
import markdown

from .base_generator import (
    BaseDocumentationGenerator,
    GenerationConfig,
    GenerationResult,
    GeneratorType
)

logger = logging.getLogger(__name__)


class OrchestrationDocsGenerator(BaseDocumentationGenerator):
    """
    Generate glassmorphism HTML documentation for CORTEX orchestrators.
    
    Discovers all orchestrator files in src/orchestrators/, extracts metadata
    using AST parsing, generates Mermaid workflow diagrams, and creates
    beautiful glassmorphism-styled HTML documentation.
    
    Output Structure:
        docs/orchestration/{orchestrator-name}/index.html - Main documentation
        docs/orchestration/index.html - Master catalog
    """
    
    def __init__(self, config: GenerationConfig, workspace_root: Optional[Path] = None):
        super().__init__(config, workspace_root)
        self.docs_path = self.config.output_path
        self.orchestrators_path = self.workspace_root / "src" / "orchestrators"
        self.orchestration_docs_path = self.docs_path / "orchestration"
        
        # Ensure output directory exists
        self.orchestration_docs_path.mkdir(parents=True, exist_ok=True)
    
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
        Generate orchestration documentation as glassmorphism HTML.
        
        Returns:
            GenerationResult with files generated
        """
        logger.info("Generating glassmorphism HTML orchestration documentation...")
        
        data = self.collect_data()
        
        for orchestrator in data["orchestrators"]:
            try:
                # Create subdirectory for orchestrator
                orchestrator_slug = orchestrator['name'].lower().replace('_', '-')
                orchestrator_dir = self.orchestration_docs_path / orchestrator_slug
                orchestrator_dir.mkdir(parents=True, exist_ok=True)
                
                # Generate workflow diagram content
                diagram_content = self._generate_workflow_diagram(orchestrator)
                
                # Generate HTML documentation page
                html_content = self._generate_html_page(orchestrator, diagram_content)
                html_file = orchestrator_dir / "index.html"
                html_file.write_text(html_content)
                self.files_generated.append(html_file)
                
            except Exception as e:
                self.record_error(f"Failed to generate docs for {orchestrator['name']}: {e}")
        
        # Generate index page
        index_content = self._generate_index_html(data)
        index_file = self.orchestration_docs_path / "index.html"
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
    
    def _generate_html_page(self, metadata: Dict[str, Any], diagram_content: str) -> str:
        """
        Generate glassmorphism HTML documentation page for orchestrator.
        
        Args:
            metadata: Orchestrator metadata
            diagram_content: Mermaid diagram content
            
        Returns:
            HTML content
        """
        title = metadata['name'].replace('_', ' ').title()
        orchestrator_slug = metadata['name'].lower().replace('_', '-')
        
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - CORTEX Orchestrators</title>
    <link rel="icon" type="image/png" href="../../assets/images/CORTEX-logo.png">
    <link rel="stylesheet" href="../../assets/css/main.css">
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
</head>
<body>
    <!-- Breadcrumb -->
    <nav class="breadcrumb">
        <a href="../../index.html">Home</a>
        <span class="breadcrumb-separator">›</span>
        <a href="../index.html">Orchestrators</a>
        <span class="breadcrumb-separator">›</span>
        <span class="breadcrumb-current">{title}</span>
    </nav>

    <!-- Hero -->
    <section class="section">
        <div class="container">
            <div class="glass-card">
                <div style="display: flex; align-items: center; gap: 2rem; margin-bottom: 1rem;">
                    <div class="icon" style="font-size: 3rem;">🔧</div>
                    <div>
                        <h1 style="margin-bottom: 0.5rem;">{title}</h1>
                        <p style="color: var(--text-secondary); font-size: 1.125rem; margin: 0;">
                            CORTEX Orchestration System
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Overview -->
    <section class="section" style="padding-top: 0;">
        <div class="container">
            <h2>Overview</h2>
            <div class="glass-card">
                <p style="font-size: 1.125rem; line-height: 1.8; color: var(--text-secondary);">
                    {self._format_docstring(metadata.get("module_docstring", "No description available."))}
                </p>
            </div>
        </div>
    </section>

    <!-- Workflow Diagram -->
    <section class="section" style="padding-top: 0;">
        <div class="container">
            <h2>Workflow Diagram</h2>
            <div class="glass-card">
                <div class="mermaid">
{diagram_content}
                </div>
            </div>
        </div>
    </section>

    <!-- Classes and Methods -->
    <section class="section" style="padding-top: 0;">
        <div class="container">
            <h2>Implementation Details</h2>
'''
        
        # Add classes
        for class_info in metadata["classes"]:
            html += f'''
            <div class="glass-card" style="margin-bottom: 2rem;">
                <h3>Class: {class_info["name"]}</h3>
'''
            if class_info["docstring"]:
                html += f'''
                <p style="color: var(--text-secondary); line-height: 1.8;">
                    {self._format_docstring(class_info["docstring"])}
                </p>
'''
            
            if class_info["bases"]:
                html += f'''
                <p><strong>Inherits from:</strong> <code>{", ".join(class_info["bases"])}</code></p>
'''
            
            # Add methods
            if class_info["methods"]:
                html += '''
                <h4 style="margin-top: 1.5rem;">Methods</h4>
                <div style="margin-left: 1rem;">
'''
                for method in class_info["methods"]:
                    if method["name"].startswith("__") and method["name"] != "__init__":
                        continue
                    
                    async_marker = "async " if method["is_async"] else ""
                    params_str = ", ".join(method["params"])
                    
                    html += f'''
                    <div style="margin-bottom: 1.5rem;">
                        <h5 style="font-family: 'Courier New', monospace; color: var(--accent-primary);">
                            {async_marker}{method["name"]}({params_str})
                        </h5>
'''
                    if method["docstring"]:
                        html += f'''
                        <p style="color: var(--text-secondary); line-height: 1.6; margin-left: 1rem;">
                            {self._format_docstring(method["docstring"])}
                        </p>
'''
                    html += '''
                    </div>
'''
                html += '''
                </div>
'''
            
            html += '''
            </div>
'''
        
        # Add top-level functions
        if metadata["functions"]:
            html += '''
            <div class="glass-card">
                <h3>Functions</h3>
                <div style="margin-left: 1rem;">
'''
            for func in metadata["functions"]:
                params_str = ", ".join(func["params"])
                html += f'''
                <div style="margin-bottom: 1.5rem;">
                    <h4 style="font-family: 'Courier New', monospace; color: var(--accent-primary);">
                        {func["name"]}({params_str})
                    </h4>
'''
                if func["docstring"]:
                    html += f'''
                    <p style="color: var(--text-secondary); line-height: 1.6;">
                        {self._format_docstring(func["docstring"])}
                    </p>
'''
                html += '''
                </div>
'''
            html += '''
                </div>
            </div>
'''
        
        # Footer
        html += f'''
        </div>
    </section>

    <!-- Source File Info -->
    <section class="section" style="padding-top: 0;">
        <div class="container">
            <div class="glass-card" style="text-align: center; color: var(--text-secondary);">
                <p><strong>Source:</strong> <code>{metadata.get('file_path', 'Unknown')}</code></p>
                <p style="margin-top: 0.5rem; font-size: 0.875rem;">
                    Author: Asif Hussain | Copyright © 2024-2025 Asif Hussain. All rights reserved.
                </p>
            </div>
        </div>
    </section>

    <script>
        mermaid.initialize({{ startOnLoad: true, theme: 'dark' }});
    </script>
</body>
</html>
'''
        return html
    
    def _format_docstring(self, text: str) -> str:
        """Format docstring for HTML display."""
        if not text:
            return ""
        
        # Replace newlines with <br> for simple formatting
        text = text.strip().replace("\n\n", "</p><p>").replace("\n", "<br>")
        return text
    
    def _generate_index_html(self, data: Dict[str, Any]) -> str:
        """
        Generate glassmorphism HTML index page listing all orchestrators.
        
        Args:
            data: Collected orchestrator data
            
        Returns:
            HTML content
        """
        html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Orchestrators - CORTEX 3.0</title>
    <link rel="icon" type="image/png" href="../assets/images/CORTEX-logo.png">
    <link rel="stylesheet" href="../assets/css/main.css">
</head>
<body>
    <!-- Breadcrumb -->
    <nav class="breadcrumb">
        <a href="../index.html">Home</a>
        <span class="breadcrumb-separator">›</span>
        <span class="breadcrumb-current">Orchestrators</span>
    </nav>

    <!-- Hero -->
    <section class="section">
        <div class="container">
            <h1 class="section-title">CORTEX Orchestrators</h1>
            <p class="text-center" style="max-width: 800px; margin: 0 auto 3rem; color: var(--text-secondary); font-size: 1.125rem;">
                Intelligent workflow coordination for complex development operations. 
                ''' + f'''{data["orchestrator_count"]} orchestrators power CORTEX's automation engine.
            </p>
        </div>
    </section>

    <!-- Overview Stats -->
    <section class="section" style="padding-top: 0;">
        <div class="container">
            <div class="glass-card">
                <h2>System Overview</h2>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem; margin-top: 1.5rem;">
                    <div style="text-align: center; padding: 1.5rem; background: rgba(0, 212, 255, 0.1); border-radius: 8px;">
                        <div style="font-size: 2.5rem; font-weight: 700; color: var(--accent-primary);">{data["orchestrator_count"]}</div>
                        <div style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.5rem;">Total Orchestrators</div>
                    </div>
                    <div style="text-align: center; padding: 1.5rem; background: rgba(123, 97, 255, 0.1); border-radius: 8px;">
                        <div style="font-size: 2.5rem; font-weight: 700; color: var(--accent-secondary);">∞</div>
                        <div style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.5rem;">Workflow Combinations</div>
                    </div>
                    <div style="text-align: center; padding: 1.5rem; background: rgba(0, 255, 136, 0.1); border-radius: 8px;">
                        <div style="font-size: 2.5rem; font-weight: 700; color: var(--success);">100%</div>
                        <div style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.5rem;">Automation Coverage</div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Orchestrator Catalog -->
    <section class="section" style="padding-top: 0;">
        <div class="container">
            <h2>Orchestrator Catalog</h2>
            <div class="feature-grid">
'''
        
        # Add orchestrator cards
        for orchestrator in sorted(data["orchestrators"], key=lambda x: x["name"]):
            orchestrator_slug = orchestrator['name'].lower().replace('_', '-')
            title = orchestrator['name'].replace('_', ' ').title()
            
            # Get summary from module docstring
            summary = "Orchestrator workflow coordination"
            if orchestrator["module_docstring"]:
                summary = orchestrator["module_docstring"].split("\n")[0].strip()
                if len(summary) > 150:
                    summary = summary[:147] + "..."
            
            html += f'''
                <a href="{orchestrator_slug}/" class="feature-card">
                    <div class="icon">🔧</div>
                    <h3>{title}</h3>
                    <p>{summary}</p>
                </a>
'''
        
        html += '''
            </div>
        </div>
    </section>

    <!-- Footer -->
    <section class="section" style="padding-top: 0;">
        <div class="container">
            <div class="glass-card" style="text-align: center; color: var(--text-secondary);">
                <p style="font-size: 0.875rem;">
                    Author: Asif Hussain | Copyright © 2024-2025 Asif Hussain. All rights reserved.
                </p>
                <p style="margin-top: 0.5rem; font-size: 0.875rem;">
                    Generated: ''' + data['generated_at'] + '''
                </p>
            </div>
        </div>
    </section>
</body>
</html>
'''
        return html
    
    def _get_timestamp(self) -> str:
        """Get formatted timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
