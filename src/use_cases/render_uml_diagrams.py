"""
UML Diagram Rendering Use Case

Generates professional UML class diagrams from Python source code using
native Python libraries (diagrams + graphviz) with SVG output for CSS integration.

Performance target: <2 seconds for 500 nodes
Output format: SVG with embedded CSS classes for professional styling
"""

import ast
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from graphviz import Digraph


@dataclass
class ClassInfo:
    """Represents a Python class extracted from AST"""
    name: str
    module: str
    bases: List[str]
    methods: List[str]
    attributes: List[str]
    is_abstract: bool = False
    docstring: Optional[str] = None


@dataclass
class RelationshipInfo:
    """Represents a relationship between classes"""
    source: str
    target: str
    relationship_type: str  # inheritance, composition, aggregation, dependency
    label: Optional[str] = None


class UMLDiagramRenderer:
    """
    Generates UML class diagrams from Python source code.
    
    Uses AST parsing for accurate class extraction and Graphviz for
    professional SVG rendering with CSS integration.
    """
    
    # Color scheme matching dashboard (from onboarding_dashboard.css)
    COLORS = {
        'primary': '#007bff',
        'success': '#28a745',
        'warning': '#ffc107',
        'danger': '#dc3545',
        'light': '#f8f9fa',
        'dark': '#343a40',
        'border': '#dee2e6'
    }
    
    def __init__(self, workspace_path: str):
        """
        Initialize UML diagram renderer.
        
        Args:
            workspace_path: Root path of Python project to analyze
        """
        self.workspace_path = Path(workspace_path)
        self.classes: Dict[str, ClassInfo] = {}
        self.relationships: List[RelationshipInfo] = []
        
    def analyze_python_file(self, file_path: Path) -> None:
        """
        Extract class information from a Python file using AST parsing.
        
        Args:
            file_path: Path to Python file
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            tree = ast.parse(source, filename=str(file_path))
            module_name = self._get_module_name(file_path)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_info = self._extract_class_info(node, module_name)
                    self.classes[class_info.name] = class_info
                    
                    # Extract inheritance relationships
                    for base in node.bases:
                        if isinstance(base, ast.Name):
                            self.relationships.append(
                                RelationshipInfo(
                                    source=class_info.name,
                                    target=base.id,
                                    relationship_type='inheritance'
                                )
                            )
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
    
    def analyze_directory(self, directory: Optional[Path] = None, 
                         exclude_patterns: Optional[List[str]] = None) -> None:
        """
        Recursively analyze all Python files in directory.
        
        Args:
            directory: Directory to analyze (defaults to workspace_path)
            exclude_patterns: Patterns to exclude (e.g., ['test_', '__pycache__'])
        """
        if directory is None:
            directory = self.workspace_path
        
        if exclude_patterns is None:
            exclude_patterns = ['test_', '__pycache__', '.venv', 'venv', 'site-packages']
        
        for python_file in directory.rglob('*.py'):
            # Skip excluded patterns
            if any(pattern in str(python_file) for pattern in exclude_patterns):
                continue
            
            self.analyze_python_file(python_file)
    
    def generate_svg(self, output_path: Optional[Path] = None, 
                     title: str = "Class Diagram",
                     max_classes: int = 50,
                     wrap_in_html: bool = True) -> str:
        """
        Generate SVG UML diagram using Graphviz.
        
        Args:
            output_path: Where to save SVG file (optional)
            title: Diagram title
            max_classes: Maximum number of classes to render (performance limit)
            wrap_in_html: Whether to wrap SVG in HTML div (True for embedding, False for standalone)
            
        Returns:
            SVG content as string
        """
        dot = Digraph(comment=title, format='svg')
        dot.attr(
            rankdir='TB',  # Top to bottom layout
            bgcolor='transparent',
            fontname='Arial',
            fontsize='12',
            nodesep='0.5',
            ranksep='0.8'
        )
        
        # Node defaults (CSS classes will override these)
        dot.attr('node',
            shape='record',
            style='filled',
            fillcolor=self.COLORS['light'],
            color=self.COLORS['border'],
            fontname='Courier',
            fontsize='10'
        )
        
        # Edge defaults
        dot.attr('edge',
            color=self.COLORS['primary'],
            fontname='Arial',
            fontsize='9'
        )
        
        # Add classes as nodes (limit for performance)
        classes_to_render = list(self.classes.values())[:max_classes]
        
        for class_info in classes_to_render:
            label = self._format_class_label(class_info)
            node_class = 'uml-node uml-class'
            
            if class_info.is_abstract:
                node_class += ' uml-abstract'
            
            dot.node(
                class_info.name,
                label=label,
                _attributes={'class': node_class}
            )
        
        # Add relationships as edges
        for rel in self.relationships:
            # Only render if both classes are in the diagram
            if rel.source in [c.name for c in classes_to_render] and \
               rel.target in [c.name for c in classes_to_render]:
                
                edge_attrs = self._get_edge_attributes(rel)
                dot.edge(rel.source, rel.target, **edge_attrs)
        
        # Generate SVG
        svg_content = dot.pipe(encoding='utf-8')
        
        # Add CSS classes to SVG for styling (only if wrapping in HTML)
        if wrap_in_html:
            svg_content = self._inject_css_classes(svg_content)
        
        # Save to file if path provided
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(svg_content)
        
        return svg_content
    
    def _get_module_name(self, file_path: Path) -> str:
        """Convert file path to Python module name"""
        try:
            relative_path = file_path.relative_to(self.workspace_path)
            module_parts = list(relative_path.parts[:-1]) + [relative_path.stem]
            return '.'.join(module_parts)
        except ValueError:
            return file_path.stem
    
    def _extract_class_info(self, node: ast.ClassDef, module_name: str) -> ClassInfo:
        """Extract class information from AST ClassDef node"""
        # Extract methods
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                # Format: +public, -private, #protected
                prefix = '-' if item.name.startswith('_') else '+'
                methods.append(f"{prefix}{item.name}()")
        
        # Extract attributes (from __init__ or class level)
        attributes = []
        for item in node.body:
            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                prefix = '-' if item.target.id.startswith('_') else '+'
                attr_type = self._get_type_annotation(item.annotation)
                attributes.append(f"{prefix}{item.target.id}: {attr_type}")
            elif isinstance(item, ast.FunctionDef) and item.name == '__init__':
                # Extract from __init__ assignments
                for stmt in item.body:
                    if isinstance(stmt, ast.Assign):
                        for target in stmt.targets:
                            if isinstance(target, ast.Attribute) and \
                               isinstance(target.value, ast.Name) and \
                               target.value.id == 'self':
                                prefix = '-' if target.attr.startswith('_') else '+'
                                attributes.append(f"{prefix}{target.attr}")
        
        # Extract base classes
        bases = [self._get_base_name(base) for base in node.bases]
        
        is_abstract = any(
            isinstance(dec, ast.Name) and dec.id == 'abstractmethod'
            for item in node.body
            if isinstance(item, ast.FunctionDef)
            for dec in item.decorator_list
        )
        
        docstring = ast.get_docstring(node)
        
        return ClassInfo(
            name=node.name,
            module=module_name,
            bases=bases,
            methods=methods,
            attributes=attributes,
            is_abstract=is_abstract,
            docstring=docstring
        )
    
    def _get_base_name(self, base: ast.expr) -> str:
        """Extract base class name from AST node"""
        if isinstance(base, ast.Name):
            return base.id
        elif isinstance(base, ast.Attribute):
            return base.attr
        return 'Unknown'
    
    def _get_type_annotation(self, annotation: ast.expr) -> str:
        """Convert type annotation AST to string"""
        if isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Subscript):
            return f"{self._get_type_annotation(annotation.value)}[...]"
        return 'Any'
    
    def _format_class_label(self, class_info: ClassInfo) -> str:
        """
        Format class information as Graphviz record label.
        
        Format: {ClassName|+attribute: type|+method()}
        """
        parts = []
        
        if class_info.is_abstract:
            parts.append(f"«abstract»\\n{class_info.name}")
        else:
            parts.append(class_info.name)
        
        # Attributes section
        if class_info.attributes:
            attrs = '\\n'.join(class_info.attributes[:5])  # Limit to 5 for readability
            if len(class_info.attributes) > 5:
                attrs += f"\\n... ({len(class_info.attributes) - 5} more)"
            parts.append(attrs)
        
        # Methods section
        if class_info.methods:
            methods = '\\n'.join(class_info.methods[:5])  # Limit to 5
            if len(class_info.methods) > 5:
                methods += f"\\n... ({len(class_info.methods) - 5} more)"
            parts.append(methods)
        
        return '{' + '|'.join(parts) + '}'
    
    def _get_edge_attributes(self, rel: RelationshipInfo) -> Dict[str, str]:
        """Get Graphviz edge attributes based on relationship type"""
        if rel.relationship_type == 'inheritance':
            return {
                'arrowhead': 'empty',
                'style': 'solid',
                'color': self.COLORS['primary'],
                'penwidth': '2'
            }
        elif rel.relationship_type == 'composition':
            return {
                'arrowhead': 'diamond',
                'style': 'solid',
                'color': self.COLORS['success'],
                'label': rel.label or ''
            }
        elif rel.relationship_type == 'aggregation':
            return {
                'arrowhead': 'odiamond',
                'style': 'solid',
                'color': self.COLORS['warning'],
                'label': rel.label or ''
            }
        elif rel.relationship_type == 'dependency':
            return {
                'arrowhead': 'vee',
                'style': 'dashed',
                'color': self.COLORS['dark'],
                'label': rel.label or ''
            }
        else:
            return {'arrowhead': 'vee'}
    
    def _inject_css_classes(self, svg_content: str) -> str:
        """
        Inject CSS classes into SVG for external styling.
        
        Wraps SVG in container div with classes for CSS targeting.
        """
        # Add container wrapper with CSS class
        wrapped_svg = f'''<div class="uml-container">
    {svg_content}
</div>'''
        
        return wrapped_svg
    
    def get_statistics(self) -> Dict[str, int]:
        """Get statistics about analyzed code"""
        return {
            'total_classes': len(self.classes),
            'total_relationships': len(self.relationships),
            'abstract_classes': sum(1 for c in self.classes.values() if c.is_abstract),
            'inheritance_relationships': sum(
                1 for r in self.relationships if r.relationship_type == 'inheritance'
            )
        }


def render_uml_for_project(project_path: str, 
                           output_path: Optional[str] = None,
                           title: str = "Project Architecture",
                           exclude_patterns: Optional[List[str]] = None,
                           wrap_in_html: bool = True) -> Tuple[str, Dict]:
    """
    Convenience function to generate UML diagram for a project.
    
    Args:
        project_path: Root path of Python project
        output_path: Where to save SVG (optional)
        title: Diagram title
        exclude_patterns: Patterns to exclude from analysis
        wrap_in_html: Whether to wrap SVG in HTML div (True for embedding, False for standalone)
        
    Returns:
        Tuple of (SVG content as string, statistics dict)
    """
    renderer = UMLDiagramRenderer(project_path)
    renderer.analyze_directory(exclude_patterns=exclude_patterns)
    
    svg_content = renderer.generate_svg(
        output_path=Path(output_path) if output_path else None,
        title=title,
        wrap_in_html=wrap_in_html
    )
    
    stats = renderer.get_statistics()
    
    return svg_content, stats


if __name__ == '__main__':
    # Test with CORTEX source code
    import sys
    
    workspace = sys.argv[1] if len(sys.argv) > 1 else '/Users/asifhussain/PROJECTS/CORTEX'
    output = sys.argv[2] if len(sys.argv) > 2 else 'uml_diagram.svg'
    
    print(f"Analyzing Python project: {workspace}")
    svg, stats = render_uml_for_project(
        project_path=workspace,
        output_path=output,
        title="CORTEX Architecture",
        exclude_patterns=['test_', '__pycache__', '.venv', 'site-packages']
    )
    
    print(f"\nStatistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print(f"\nSVG diagram saved to: {output}")
    print(f"SVG size: {len(svg)} bytes")
