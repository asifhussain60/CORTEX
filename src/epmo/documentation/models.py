"""
Data Models for CORTEX EPM Documentation Generator

Defines comprehensive data structures for representing Entry Point Module
analysis, documentation, and metadata in a structured, JSON-serializable format.

Features:
- Complete EPM representation models
- Documentation content structures
- Health integration data models
- Mermaid diagram specifications
- Template configuration schemas
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional, Union, Tuple
from pathlib import Path
from datetime import datetime
from enum import Enum


class DocumentationFormat(Enum):
    """Supported documentation output formats."""
    MARKDOWN = "markdown"
    HTML = "html"
    JSON = "json"


class DiagramType(Enum):
    """Supported Mermaid diagram types."""
    ARCHITECTURE = "architecture"
    DEPENDENCY_GRAPH = "dependency_graph"
    CLASS_DIAGRAM = "class_diagram"
    FLOWCHART = "flowchart"
    SEQUENCE_DIAGRAM = "sequence_diagram"


class HealthDimension(Enum):
    """Health validation dimensions."""
    CODE_QUALITY = "code_quality"
    DOCUMENTATION = "documentation"
    TEST_COVERAGE = "test_coverage"
    PERFORMANCE = "performance"
    ARCHITECTURE = "architecture"
    MAINTAINABILITY = "maintainability"


@dataclass
class CodeElement:
    """Represents a code element (function, class, method)."""
    name: str
    element_type: str  # 'function', 'class', 'method'
    line_number: int
    docstring: Optional[str] = None
    parameters: List[str] = field(default_factory=list)
    return_type: Optional[str] = None
    decorators: List[str] = field(default_factory=list)
    visibility: str = "public"  # 'public', 'private', 'protected'
    complexity: int = 0
    has_tests: bool = False


@dataclass
class ClassModel:
    """Represents a class with its methods and metadata."""
    name: str
    line_number: int
    docstring: Optional[str] = None
    base_classes: List[str] = field(default_factory=list)
    methods: List[CodeElement] = field(default_factory=list)
    decorators: List[str] = field(default_factory=list)
    visibility: str = "public"
    is_abstract: bool = False
    interface_methods: List[str] = field(default_factory=list)


@dataclass
class ImportDependency:
    """Represents an import dependency."""
    module: str
    import_type: str  # 'direct', 'from', 'relative'
    line_number: int
    names: List[str] = field(default_factory=list)
    alias: Optional[str] = None
    is_external: bool = False
    is_relative: bool = False
    package_origin: Optional[str] = None


@dataclass
class FileAnalysis:
    """Complete analysis of a single Python file."""
    file_path: str
    relative_path: str
    module_name: str
    file_size_bytes: int
    total_lines: int
    code_lines: int
    comment_lines: int
    blank_lines: int
    docstring: Optional[str] = None
    functions: List[CodeElement] = field(default_factory=list)
    classes: List[ClassModel] = field(default_factory=list)
    imports: List[ImportDependency] = field(default_factory=list)
    complexity_score: int = 0
    has_test_file: bool = False
    test_file_path: Optional[str] = None
    last_modified: Optional[str] = None


@dataclass
class DependencyRelation:
    """Represents a dependency relationship between modules."""
    source_module: str
    target_module: str
    relationship_type: str  # 'imports', 'extends', 'implements', 'uses'
    strength: float = 1.0  # Relationship strength (0.0 - 1.0)
    is_circular: bool = False
    line_references: List[int] = field(default_factory=list)


@dataclass
class ArchitectureMetrics:
    """Architecture and design metrics for the EPMO."""
    total_modules: int
    total_classes: int
    total_functions: int
    total_lines: int
    dependency_count: int
    circular_dependencies: int
    coupling_score: float
    cohesion_score: float
    external_dependencies: List[str] = field(default_factory=list)
    dependency_layers: List[List[str]] = field(default_factory=list)
    hotspot_modules: List[str] = field(default_factory=list)


@dataclass
class HealthMetrics:
    """Health validation metrics and scores."""
    overall_score: float
    dimension_scores: Dict[str, float] = field(default_factory=dict)
    dimension_weights: Dict[str, float] = field(default_factory=dict)
    health_status: str = "unknown"  # 'excellent', 'good', 'fair', 'poor'
    validation_timestamp: Optional[str] = None
    issues_found: int = 0
    auto_fixable_issues: int = 0
    priority_issues: int = 0
    estimated_fix_time_minutes: int = 0


@dataclass
class RemediationItem:
    """Individual remediation action item."""
    description: str
    action_type: str
    priority: str  # 'high', 'medium', 'low'
    auto_fixable: bool
    estimated_effort_minutes: int
    affected_files: List[str] = field(default_factory=list)
    health_dimension: Optional[str] = None
    detailed_guidance: Optional[str] = None


@dataclass
class MermaidDiagram:
    """Mermaid diagram specification."""
    diagram_type: DiagramType
    title: str
    mermaid_syntax: str
    description: Optional[str] = None
    file_path: Optional[str] = None
    thumbnail_path: Optional[str] = None


@dataclass
class DocumentationSection:
    """Individual documentation section."""
    section_id: str
    title: str
    content: str
    section_type: str  # 'overview', 'api', 'health', 'architecture', 'usage'
    order: int = 0
    include_in_toc: bool = True
    diagrams: List[MermaidDiagram] = field(default_factory=list)
    code_examples: List[str] = field(default_factory=list)
    cross_references: List[str] = field(default_factory=list)


@dataclass
class DocumentationMetadata:
    """Metadata about generated documentation."""
    epmo_name: str
    epmo_path: str
    generated_at: str
    generated_by: str = "CORTEX EPM Documentation Generator"
    version: str = "1.0.0"
    format: DocumentationFormat = DocumentationFormat.MARKDOWN
    template_used: Optional[str] = None
    total_sections: int = 0
    total_diagrams: int = 0
    generation_time_seconds: float = 0.0
    include_health_data: bool = True
    include_diagrams: bool = True


@dataclass
class EPMDocumentationModel:
    """Complete documentation model for an Entry Point Module."""
    metadata: DocumentationMetadata
    files: List[FileAnalysis] = field(default_factory=list)
    architecture: ArchitectureMetrics = None
    health: HealthMetrics = None
    dependencies: List[DependencyRelation] = field(default_factory=list)
    sections: List[DocumentationSection] = field(default_factory=list)
    diagrams: List[MermaidDiagram] = field(default_factory=list)
    remediation: List[RemediationItem] = field(default_factory=list)
    quality_badges: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        return asdict(self)
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get high-level summary statistics."""
        return {
            'total_files': len(self.files),
            'total_classes': sum(len(f.classes) for f in self.files),
            'total_functions': sum(len(f.functions) for f in self.files),
            'total_lines': sum(f.total_lines for f in self.files),
            'has_health_data': self.health is not None,
            'health_score': self.health.overall_score if self.health else 0.0,
            'remediation_items': len(self.remediation),
            'auto_fixable_items': len([r for r in self.remediation if r.auto_fixable]),
            'total_diagrams': len(self.diagrams),
            'external_dependencies': len(self.architecture.external_dependencies) if self.architecture else 0
        }
    
    def get_files_by_complexity(self, limit: int = 10) -> List[FileAnalysis]:
        """Get files sorted by complexity (highest first)."""
        return sorted(self.files, key=lambda f: f.complexity_score, reverse=True)[:limit]
    
    def get_priority_remediation_items(self) -> List[RemediationItem]:
        """Get high-priority remediation items."""
        return [item for item in self.remediation if item.priority == 'high']
    
    def get_auto_fixable_items(self) -> List[RemediationItem]:
        """Get items that can be automatically fixed."""
        return [item for item in self.remediation if item.auto_fixable]


@dataclass
class TemplateConfiguration:
    """Configuration for documentation template."""
    template_name: str
    include_sections: List[str] = field(default_factory=lambda: [
        'overview', 'architecture', 'api', 'health', 'remediation'
    ])
    include_diagrams: bool = True
    include_health_badges: bool = True
    include_code_examples: bool = True
    custom_sections: Dict[str, str] = field(default_factory=dict)
    header_template: Optional[str] = None
    footer_template: Optional[str] = None
    css_styles: Optional[str] = None
    mermaid_theme: str = "default"


@dataclass
class GenerationConfig:
    """Configuration for documentation generation process."""
    output_format: DocumentationFormat = DocumentationFormat.MARKDOWN
    output_directory: str = "docs"
    template_config: TemplateConfiguration = field(default_factory=lambda: TemplateConfiguration("comprehensive"))
    include_health_analysis: bool = True
    include_dependency_analysis: bool = True
    include_architecture_diagrams: bool = True
    include_api_documentation: bool = True
    include_remediation_guide: bool = True
    generate_separate_files: bool = False
    file_naming_pattern: str = "{epmo_name}_documentation.md"
    diagram_output_directory: str = "diagrams"
    max_diagram_complexity: int = 50  # Maximum nodes in diagrams
    

def create_epmo_model(
    epmo_path: Path,
    ast_analysis: Dict[str, Any],
    dependency_analysis: Dict[str, Any],
    health_data: Optional[Dict[str, Any]] = None
) -> EPMDocumentationModel:
    """
    Create a complete EPM documentation model from analysis data.
    
    Args:
        epmo_path: Path to the Entry Point Module
        ast_analysis: Results from AST parser
        dependency_analysis: Results from dependency mapper  
        health_data: Optional health integration data
        
    Returns:
        Complete EPMDocumentationModel ready for documentation generation
    """
    # Create metadata
    metadata = DocumentationMetadata(
        epmo_name=epmo_path.name,
        epmo_path=str(epmo_path),
        generated_at=datetime.now().isoformat(),
        include_health_data=health_data is not None
    )
    
    # Convert file analyses
    files = []
    for file_data in ast_analysis.get('files', []):
        # Convert functions
        functions = [
            CodeElement(
                name=f['name'],
                element_type='function',
                line_number=f['line_number'],
                docstring=f.get('docstring'),
                parameters=f.get('parameters', []),
                return_type=f.get('return_type'),
                decorators=f.get('decorators', []),
                visibility='private' if f.get('is_private') else 'public',
                complexity=f.get('complexity', 0)
            )
            for f in file_data.get('functions', [])
        ]
        
        # Convert classes
        classes = []
        for c in file_data.get('classes', []):
            class_methods = [
                CodeElement(
                    name=m['name'],
                    element_type='method',
                    line_number=m['line_number'],
                    docstring=m.get('docstring'),
                    parameters=m.get('parameters', []),
                    return_type=m.get('return_type'),
                    decorators=m.get('decorators', []),
                    visibility='private' if m.get('is_private') else 'public',
                    complexity=m.get('complexity', 0)
                )
                for m in c.get('methods', [])
            ]
            
            class_model = ClassModel(
                name=c['name'],
                line_number=c['line_number'],
                docstring=c.get('docstring'),
                base_classes=c.get('base_classes', []),
                methods=class_methods,
                decorators=c.get('decorators', []),
                visibility='private' if c.get('is_private') else 'public'
            )
            classes.append(class_model)
        
        # Convert imports
        imports = [
            ImportDependency(
                module=i['module'],
                import_type='from' if i.get('is_from_import') else 'direct',
                line_number=i.get('line_number', 0),
                names=i.get('names', []),
                alias=i.get('alias'),
                is_external=i.get('is_external', True),
                is_relative=i.get('is_relative', False)
            )
            for i in file_data.get('imports', [])
        ]
        
        file_analysis = FileAnalysis(
            file_path=file_data['path'],
            relative_path=str(Path(file_data['path']).relative_to(epmo_path)),
            module_name=Path(file_data['path']).stem,
            file_size_bytes=0,  # Would need to calculate
            total_lines=file_data.get('total_lines', 0),
            code_lines=file_data.get('total_lines', 0),  # Simplified
            comment_lines=0,
            blank_lines=0,
            docstring=file_data.get('docstring'),
            functions=functions,
            classes=classes,
            imports=imports,
            complexity_score=file_data.get('complexity_score', 0),
            has_test_file=file_data.get('has_tests', False)
        )
        files.append(file_analysis)
    
    # Create architecture metrics
    architecture = ArchitectureMetrics(
        total_modules=dependency_analysis.get('total_modules', 0),
        total_classes=ast_analysis.get('total_classes', 0),
        total_functions=ast_analysis.get('total_functions', 0),
        total_lines=ast_analysis.get('total_lines', 0),
        dependency_count=dependency_analysis.get('total_relationships', 0),
        circular_dependencies=len(dependency_analysis.get('circular_dependency_chains', [])),
        coupling_score=0.0,  # Would need to calculate average
        cohesion_score=0.0,  # Would need to calculate
        external_dependencies=dependency_analysis.get('external_packages', []),
        dependency_layers=dependency_analysis.get('dependency_layers', [])
    )
    
    # Create health metrics if available
    health = None
    if health_data and health_data.get('status') == 'success':
        health = HealthMetrics(
            overall_score=health_data.get('overall_score', 0.0),
            health_status=health_data.get('health_status', 'unknown'),
            validation_timestamp=datetime.now().isoformat(),
            issues_found=health_data.get('remediation_actions_count', 0),
            auto_fixable_issues=health_data.get('auto_fixable_count', 0),
            priority_issues=health_data.get('priority_issues_count', 0)
        )
    
    # Create model
    model = EPMDocumentationModel(
        metadata=metadata,
        files=files,
        architecture=architecture,
        health=health,
        quality_badges=health_data.get('quality_badges', []) if health_data else [],
        warnings=health_data.get('health_warnings', []) if health_data else []
    )
    
    return model


def validate_model(model: EPMDocumentationModel) -> List[str]:
    """
    Validate EPM documentation model for completeness and consistency.
    
    Args:
        model: EPM documentation model to validate
        
    Returns:
        List of validation warnings/errors
    """
    warnings = []
    
    # Basic structure validation
    if not model.files:
        warnings.append("No files found in EPMO analysis")
    
    if not model.metadata.epmo_name:
        warnings.append("EPMO name not specified")
    
    # Content validation
    total_functions = sum(len(f.functions) for f in model.files)
    functions_with_docs = sum(
        len([func for func in f.functions if func.docstring]) 
        for f in model.files
    )
    
    if total_functions > 0:
        doc_coverage = functions_with_docs / total_functions
        if doc_coverage < 0.5:
            warnings.append(f"Low documentation coverage: {doc_coverage:.1%}")
    
    # Health data validation
    if model.health and model.health.overall_score < 70:
        warnings.append(f"Low health score: {model.health.overall_score:.1f}/100")
    
    # Architecture validation
    if model.architecture and model.architecture.circular_dependencies > 0:
        warnings.append(f"Circular dependencies detected: {model.architecture.circular_dependencies}")
    
    return warnings