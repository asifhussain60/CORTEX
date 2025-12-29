"""
Documentation Generation Orchestrator.

Provides automatic documentation generation from Python code using AST parsing.
"""

import ast
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from pathlib import Path


@dataclass
class DocstringInfo:
    """Information about a docstring."""
    name: str
    type: str  # 'function', 'class', 'method'
    docstring: str
    lineno: int = 0


@dataclass
class APIReference:
    """Generated API reference documentation."""
    module_name: str
    markdown: str
    sections: List[str] = field(default_factory=list)


@dataclass
class UsageGuide:
    """Generated usage guide documentation."""
    module_name: str
    markdown: str
    examples: List[Dict[str, str]] = field(default_factory=list)


class DocumentationGenerationOrchestrator:
    """
    Orchestrator for automatic documentation generation.
    
    Features:
    - Extract docstrings from Python source code
    - Generate API reference documentation
    - Create usage guides with examples
    - Markdown formatting
    """
    
    def __init__(self):
        """Initialize the orchestrator."""
        self.extracted_docs: List[DocstringInfo] = []
    
    def extract_docstrings(self, source_code: str) -> List[DocstringInfo]:
        """
        Extract docstrings from Python source code.
        
        Args:
            source_code: Python source code as string
            
        Returns:
            List of DocstringInfo objects
        """
        docstrings = []
        
        try:
            tree = ast.parse(source_code)
        except SyntaxError:
            return docstrings
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                docstring = ast.get_docstring(node)
                if docstring:
                    # Determine if it's a method or function
                    is_method = any(
                        isinstance(parent, ast.ClassDef)
                        for parent in ast.walk(tree)
                        if hasattr(parent, 'body') and node in parent.body
                    )
                    
                    docstrings.append(DocstringInfo(
                        name=node.name,
                        type='method' if is_method else 'function',
                        docstring=docstring,
                        lineno=node.lineno
                    ))
            
            elif isinstance(node, ast.ClassDef):
                docstring = ast.get_docstring(node)
                if docstring:
                    docstrings.append(DocstringInfo(
                        name=node.name,
                        type='class',
                        docstring=docstring,
                        lineno=node.lineno
                    ))
        
        self.extracted_docs = docstrings
        return docstrings
    
    def generate_api_reference(
        self, 
        docstrings: List[DocstringInfo], 
        module_name: str = "Module"
    ) -> APIReference:
        """
        Generate API reference documentation.
        
        Args:
            docstrings: List of extracted docstrings
            module_name: Name of the module
            
        Returns:
            APIReference with markdown documentation
        """
        markdown_lines = [f"# {module_name} API Reference\n"]
        sections = []
        
        # Group by type
        classes = [d for d in docstrings if d.type == 'class']
        functions = [d for d in docstrings if d.type == 'function']
        methods = [d for d in docstrings if d.type == 'method']
        
        # Add classes
        if classes:
            markdown_lines.append("## Classes\n")
            sections.append("Classes")
            for doc in classes:
                markdown_lines.append(f"### {doc.name}\n")
                markdown_lines.append(f"{doc.docstring}\n")
        
        # Add functions
        if functions:
            markdown_lines.append("## Functions\n")
            sections.append("Functions")
            for doc in functions:
                markdown_lines.append(f"### {doc.name}\n")
                markdown_lines.append(f"{doc.docstring}\n")
        
        # Add methods
        if methods:
            markdown_lines.append("## Methods\n")
            sections.append("Methods")
            for doc in methods:
                markdown_lines.append(f"### {doc.name}\n")
                markdown_lines.append(f"{doc.docstring}\n")
        
        markdown = "\n".join(markdown_lines)
        
        return APIReference(
            module_name=module_name,
            markdown=markdown,
            sections=sections
        )
    
    def create_usage_guide(
        self,
        module_name: str,
        examples: List[Dict[str, str]],
        description: str = ""
    ) -> UsageGuide:
        """
        Create usage guide with examples.
        
        Args:
            module_name: Name of the module
            examples: List of example dicts with 'title' and 'code' keys
            description: Optional module description
            
        Returns:
            UsageGuide with markdown documentation
        """
        markdown_lines = [f"# {module_name} Usage Guide\n"]
        
        if description:
            markdown_lines.append(f"{description}\n")
        
        if examples:
            markdown_lines.append("## Examples\n")
            for example in examples:
                title = example.get('title', 'Example')
                code = example.get('code', '')
                
                markdown_lines.append(f"### {title}\n")
                markdown_lines.append("```python")
                markdown_lines.append(code)
                markdown_lines.append("```\n")
        
        markdown = "\n".join(markdown_lines)
        
        return UsageGuide(
            module_name=module_name,
            markdown=markdown,
            examples=examples
        )
