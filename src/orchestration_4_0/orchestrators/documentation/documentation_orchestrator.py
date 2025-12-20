"""
Documentation Orchestrator - Auto-generate comprehensive technical documentation

Phase-based documentation generation workflow:
1. ANALYZE: Scan target modules and extract metadata
2. EXTRACT: Parse code structure and type information
3. GENERATE_DOCS: Create API documentation
4. GENERATE_DIAGRAMS: Create D3.js visualizations
5. VALIDATE: Verify documentation completeness
6. EXPORT: Save all documentation files
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    # Only for type checking - avoid runtime import conflict
    from logging import Logger

from ...base.base_orchestrator import BaseOrchestrator
from ...base.error_handler import ErrorHandler, RecoveryStrategy
from ...base.phase_manager import PhaseManager
from .extractors.code_analyzer import CodeAnalyzer, ModuleInfo, ClassInfo
from .extractors.type_extractor import TypeExtractor
from .generators.api_doc_generator import APIDocGenerator
from .generators.diagram_generator import DiagramGenerator


@dataclass
class DocumentationConfig:
    """Configuration for documentation generation"""
    source_paths: List[Path] = field(default_factory=list)
    output_dir: Path = Path("docs/api")
    include_private: bool = False
    generate_diagrams: bool = True
    generate_quick_ref: bool = True
    diagram_types: List[str] = field(default_factory=lambda: [
        "class_hierarchy",
        "phase_flow"
    ])


@dataclass
class DocumentationResult:
    """Results from documentation generation"""
    modules_analyzed: int = 0
    classes_documented: int = 0
    functions_documented: int = 0
    diagrams_generated: int = 0
    output_files: List[Path] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class DocumentationOrchestrator(BaseOrchestrator):
    """
    Orchestrates comprehensive technical documentation generation
    
    Features:
    - AST-based code analysis
    - Type hint extraction
    - API documentation generation
    - Interactive D3.js diagrams
    - Phase flow visualization
    - Class hierarchy diagrams
    
    Example:
        orchestrator = DocumentationOrchestrator(logger, config)
        
        context = {
            'config': DocumentationConfig(
                source_paths=[Path("src/orchestration_4_0")],
                output_dir=Path("docs/orchestration")
            )
        }
        
        result = orchestrator.execute(context)
        print(f"Documented {result['modules_analyzed']} modules")
    """
    
    def __init__(
        self,
        logger: Optional["Logger"] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            name="documentation",
            logger=logger,
            config=config
        )
        
        # Initialize documentation components
        self.code_analyzer = CodeAnalyzer()
        self.type_extractor = TypeExtractor()
        self.api_doc_generator = APIDocGenerator()
        self.diagram_generator = DiagramGenerator()
        
        # Inject loggers
        self.code_analyzer.logger = self.logger
        self.type_extractor.logger = self.logger
        self.api_doc_generator.logger = self.logger
        self.diagram_generator.logger = self.logger
        
        # Store analyzed modules
        self.modules: List[ModuleInfo] = []
        self.doc_config: Optional[DocumentationConfig] = None
        self.doc_result: Optional[DocumentationResult] = None
        
        # Adaptive execution mode
        self.execution_mode = self.config.get("execution_mode", "AUTONOMOUS")
        self.logger.info(f"🎯 Documentation execution mode: {self.execution_mode}")
    
    def _setup(self, context: Dict[str, Any]) -> None:
        """
        Setup documentation generation
        
        Validates configuration and prepares output directories
        """
        self.logger.info("🔧 Setting up documentation generation")
        
        # Extract configuration
        config_data = context.get('config', {})
        if isinstance(config_data, DocumentationConfig):
            self.doc_config = config_data
        elif isinstance(config_data, dict):
            self.doc_config = DocumentationConfig(**config_data)
        else:
            raise ValueError("Invalid documentation configuration")
        
        # Validate source paths
        if not self.doc_config.source_paths:
            raise ValueError("No source paths specified for documentation")
        
        for path in self.doc_config.source_paths:
            if not path.exists():
                raise FileNotFoundError(f"Source path not found: {path}")
        
        # Create output directory
        self.doc_config.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Override execution mode if specified
        if "execution_mode" in context:
            self.execution_mode = context["execution_mode"]
            self.logger.info(f"🎯 Execution mode overridden: {self.execution_mode}")
        
        self.logger.info(f"✅ Documentation will be generated at: {self.doc_config.output_dir}")
        
        # Initialize result in context and store in instance
        self.doc_result = DocumentationResult()
        context['config'] = self.doc_config
        context['result'] = self.doc_result
    
    def _register_phases(self) -> None:
        """Register documentation generation phases"""
        self.phase_manager.register_phase(
            "analyze",
            description="Analyze Python files and extract metadata"
        )
        
        self.phase_manager.register_phase(
            "extract",
            description="Extract type information and signatures"
        )
        
        self.phase_manager.register_phase(
            "generate_docs",
            description="Generate API documentation"
        )
        
        if self.doc_config and self.doc_config.generate_diagrams:
            self.phase_manager.register_phase(
                "generate_diagrams",
                description="Generate D3.js interactive diagrams"
            )
        
        self.phase_manager.register_phase(
            "validate",
            description="Validate documentation completeness"
        )
        
        self.phase_manager.register_phase(
            "export",
            description="Export all documentation files"
        )
    
    def _execute_phase(
        self,
        phase_name: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a documentation generation phase with adaptive modes
        
        Execution modes:
        - AUTONOMOUS: Execute all phases without intervention
        - CHECKPOINT: Validate completeness at each phase
        - INTERACTIVE: Request approval before expensive operations
        """
        result: DocumentationResult = context['result']
        
        # CHECKPOINT mode: Validate phase prerequisites
        if self.execution_mode == "CHECKPOINT":
            if not self._validate_phase_prerequisites(phase_name, context):
                return {"status": "skipped", "reason": "Prerequisites not met"}
        
        # INTERACTIVE mode: Request approval for expensive phases
        if self.execution_mode == "INTERACTIVE":
            if phase_name in ["generate_diagrams", "export"]:
                if not self._request_phase_approval(phase_name):
                    return {"status": "skipped", "reason": "User declined"}
        
        if phase_name == "analyze":
            return self._analyze_phase(context, result)
        elif phase_name == "extract":
            return self._extract_phase(context, result)
        elif phase_name == "generate_docs":
            return self._generate_docs_phase(context, result)
        elif phase_name == "generate_diagrams":
            return self._generate_diagrams_phase(context, result)
        elif phase_name == "validate":
            return self._validate_phase(context, result)
        elif phase_name == "export":
            return self._export_phase(context, result)
        else:
            raise ValueError(f"Unknown phase: {phase_name}")
    
    def _analyze_phase(
        self,
        context: Dict[str, Any],
        result: DocumentationResult
    ) -> Dict[str, Any]:
        """Analyze Python files and extract metadata"""
        self.logger.info("Phase: ANALYZE - Scanning Python files")
        
        self.modules.clear()
        
        for source_path in self.doc_config.source_paths:
            if source_path.is_file():
                # Single file
                if source_path.suffix == '.py':
                    try:
                        module_info = self.code_analyzer.analyze_file(source_path)
                        self.modules.append(module_info)
                        result.modules_analyzed += 1
                    except Exception as e:
                        error_msg = f"Failed to analyze {source_path}: {e}"
                        self.logger.error(error_msg)
                        result.errors.append(error_msg)
            else:
                # Directory - recursively find Python files
                for py_file in source_path.rglob("*.py"):
                    # Skip test files and __pycache__
                    if '__pycache__' in str(py_file) or py_file.name.startswith('test_'):
                        continue
                    
                    try:
                        module_info = self.code_analyzer.analyze_file(py_file)
                        self.modules.append(module_info)
                        result.modules_analyzed += 1
                    except Exception as e:
                        error_msg = f"Failed to analyze {py_file}: {e}"
                        self.logger.warning(error_msg)
                        result.warnings.append(error_msg)
        
        self.logger.info(f"Analyzed {result.modules_analyzed} modules")
        
        return {'modules': self.modules, 'result': result}
    
    def _extract_phase(
        self,
        context: Dict[str, Any],
        result: DocumentationResult
    ) -> Dict[str, Any]:
        """Extract type information and enhance metadata"""
        self.logger.info("Phase: EXTRACT - Extracting type information")
        
        for module in self.modules:
            # Count documented items
            for cls in module.classes:
                result.classes_documented += 1
                for method in cls.methods:
                    if not method.name.startswith('_') or self.doc_config.include_private:
                        # Type information already extracted by code analyzer
                        pass
            
            for func in module.functions:
                if not func.name.startswith('_') or self.doc_config.include_private:
                    result.functions_documented += 1
        
        self.logger.info(
            f"Extracted: {result.classes_documented} classes, "
            f"{result.functions_documented} functions"
        )
        
        return context
    
    def _generate_docs_phase(
        self,
        context: Dict[str, Any],
        result: DocumentationResult
    ) -> Dict[str, Any]:
        """Generate API documentation"""
        self.logger.info("Phase: GENERATE_DOCS - Creating API documentation")
        
        if not self.modules:
            result.warnings.append("No modules to document")
            return context
        
        # Generate individual module docs
        docs_dir = self.doc_config.output_dir / "modules"
        docs_dir.mkdir(parents=True, exist_ok=True)
        
        for module in self.modules:
            output_path = docs_dir / f"{module.name}.md"
            try:
                self.api_doc_generator.generate_module_docs(
                    module,
                    output_path,
                    self.doc_config.include_private
                )
                result.output_files.append(output_path)
                self.logger.info(f"Generated docs: {output_path.name}")
            except Exception as e:
                error_msg = f"Failed to generate docs for {module.name}: {e}"
                self.logger.error(error_msg)
                result.errors.append(error_msg)
        
        # Generate index
        try:
            index_path = self.api_doc_generator.generate_multi_module_docs(
                self.modules,
                docs_dir,
                "index.md"
            )
            result.output_files.append(index_path)
            self.logger.info(f"Generated index: {index_path}")
        except Exception as e:
            error_msg = f"Failed to generate index: {e}"
            self.logger.error(error_msg)
            result.errors.append(error_msg)
        
        # Generate quick reference if requested
        if self.doc_config.generate_quick_ref:
            try:
                quick_ref_path = self.doc_config.output_dir / "quick-reference.md"
                self.api_doc_generator.generate_quick_reference(
                    self.modules,
                    quick_ref_path
                )
                result.output_files.append(quick_ref_path)
                self.logger.info(f"Generated quick reference: {quick_ref_path}")
            except Exception as e:
                error_msg = f"Failed to generate quick reference: {e}"
                self.logger.error(error_msg)
                result.errors.append(error_msg)
        
        return context
    
    def _generate_diagrams_phase(
        self,
        context: Dict[str, Any],
        result: DocumentationResult
    ) -> Dict[str, Any]:
        """Generate D3.js interactive diagrams"""
        self.logger.info("Phase: GENERATE_DIAGRAMS - Creating visualizations")
        
        diagrams_dir = self.doc_config.output_dir / "diagrams"
        diagrams_dir.mkdir(parents=True, exist_ok=True)
        
        # Class hierarchy diagram
        if "class_hierarchy" in self.doc_config.diagram_types and self.modules:
            try:
                output_path = diagrams_dir / "class-hierarchy.html"
                self.diagram_generator.generate_class_hierarchy(
                    self.modules,
                    output_path,
                    "Class Hierarchy"
                )
                result.output_files.append(output_path)
                result.diagrams_generated += 1
                self.logger.info(f"Generated diagram: {output_path.name}")
            except Exception as e:
                error_msg = f"Failed to generate class hierarchy diagram: {e}"
                self.logger.error(error_msg)
                result.errors.append(error_msg)
        
        # Phase flow diagrams (for orchestrators)
        if "phase_flow" in self.doc_config.diagram_types:
            for module in self.modules:
                # Check if module contains an orchestrator
                for cls in module.classes:
                    if 'Orchestrator' in cls.name:
                        try:
                            # Extract phase information
                            phase_data = self._extract_phase_flow(cls)
                            if phase_data:
                                output_path = diagrams_dir / f"{cls.name.lower()}-flow.html"
                                self.diagram_generator.generate_phase_flow_diagram(
                                    phase_data,
                                    output_path,
                                    f"{cls.name} Phase Flow"
                                )
                                result.output_files.append(output_path)
                                result.diagrams_generated += 1
                                self.logger.info(f"Generated diagram: {output_path.name}")
                        except Exception as e:
                            error_msg = f"Failed to generate phase flow for {cls.name}: {e}"
                            self.logger.warning(error_msg)
                            result.warnings.append(error_msg)
        
        return context
    
    def _validate_phase(
        self,
        context: Dict[str, Any],
        result: DocumentationResult
    ) -> Dict[str, Any]:
        """Validate documentation completeness"""
        self.logger.info("Phase: VALIDATE - Checking documentation quality")
        
        # Check that we generated output files
        if not result.output_files:
            result.errors.append("No documentation files were generated")
        
        # Check for undocumented public classes
        for module in self.modules:
            for cls in module.classes:
                if not cls.docstring:
                    warning = f"{module.name}.{cls.name}: Missing class docstring"
                    result.warnings.append(warning)
                
                for method in cls.methods:
                    if not method.name.startswith('_') and not method.docstring:
                        warning = f"{module.name}.{cls.name}.{method.name}: Missing method docstring"
                        result.warnings.append(warning)
        
        self.logger.info(f"Validation complete: {len(result.errors)} errors, {len(result.warnings)} warnings")
        
        return context
    
    def _export_phase(
        self,
        context: Dict[str, Any],
        result: DocumentationResult
    ) -> Dict[str, Any]:
        """Export documentation summary"""
        self.logger.info("Phase: EXPORT - Creating summary")
        
        # Generate summary file
        summary_path = self.doc_config.output_dir / "summary.md"
        summary_lines = [
            "# Documentation Generation Summary\n",
            f"## Statistics\n",
            f"- **Modules Analyzed:** {result.modules_analyzed}",
            f"- **Classes Documented:** {result.classes_documented}",
            f"- **Functions Documented:** {result.functions_documented}",
            f"- **Diagrams Generated:** {result.diagrams_generated}",
            f"- **Output Files:** {len(result.output_files)}",
            f"- **Errors:** {len(result.errors)}",
            f"- **Warnings:** {len(result.warnings)}\n",
        ]
        
        if result.output_files:
            summary_lines.append("## Generated Files\n")
            for file_path in result.output_files:
                relative_path = file_path.relative_to(self.doc_config.output_dir)
                summary_lines.append(f"- {relative_path}")
            summary_lines.append("\n")
        
        if result.errors:
            summary_lines.append("## Errors\n")
            for error in result.errors:
                summary_lines.append(f"- {error}")
            summary_lines.append("\n")
        
        if result.warnings:
            summary_lines.append("## Warnings\n")
            for warning in result.warnings[:10]:  # Limit to first 10
                summary_lines.append(f"- {warning}")
            if len(result.warnings) > 10:
                summary_lines.append(f"- ... and {len(result.warnings) - 10} more")
            summary_lines.append("\n")
        
        summary_path.write_text('\n'.join(summary_lines), encoding='utf-8')
        result.output_files.append(summary_path)
        
        self.logger.info(f"Documentation summary: {summary_path}")
        
        return context
    
    def _extract_phase_flow(self, cls: ClassInfo) -> List[Dict[str, Any]]:
        """Extract phase flow information from an orchestrator class"""
        phases = []
        
        # Look for _register_phases method
        for method in cls.methods:
            if method.name == "_register_phases":
                # Parse the method body to extract phase registrations
                # This is a simplified implementation
                # In reality, would need to parse the method's AST
                pass
        
        # Return empty list if no phases found
        # A full implementation would parse the _register_phases method
        return phases
    
    def _teardown(self) -> None:
        """Cleanup after documentation generation"""
        self.logger.info("✅ Documentation generation complete")
    
    def _collect_results(self) -> Dict[str, Any]:
        """Collect orchestrator results including DocumentationResult"""
        # Get base results from parent
        base_results = super()._collect_results()
        
        # Add DocumentationResult if available
        if self.doc_result:
            base_results['result'] = self.doc_result
        
        return base_results
    
    def _validate_phase_prerequisites(self, phase_name: str, context: Dict[str, Any]) -> bool:
        """
        Validate phase prerequisites in CHECKPOINT mode
        
        Args:
            phase_name: Phase to validate
            context: Execution context
            
        Returns:
            True if prerequisites met
        """
        result: DocumentationResult = context.get('result')
        
        if phase_name == "extract":
            # Need analyzed modules
            return len(self.modules) > 0
        elif phase_name == "generate_docs":
            # Need extracted modules
            return len(self.modules) > 0
        elif phase_name == "generate_diagrams":
            # Need generated docs
            return result and result.modules_analyzed > 0
        elif phase_name == "validate":
            # Need generated docs
            return result and len(result.output_files) > 0
        elif phase_name == "export":
            # Need validation complete
            return True
        
        return True
    
    def _request_phase_approval(self, phase_name: str) -> bool:
        """
        Request user approval in INTERACTIVE mode
        
        Args:
            phase_name: Phase requesting approval
            
        Returns:
            True if user approves
        """
        self.logger.info(f"🤔 INTERACTIVE mode: Requesting approval for phase '{phase_name}'")
        
        # Auto-approve for now (can be overridden)
        self.logger.info(f"✅ Auto-approved: {phase_name}")
        return True
    
    # Validation methods
    def _validate_analyze(self, context: Dict[str, Any]) -> bool:
        """Validate analyze phase"""
        return len(self.modules) > 0
    
    def _validate_extract(self, context: Dict[str, Any]) -> bool:
        """Validate extract phase"""
        result: DocumentationResult = context['result']
        return result.classes_documented > 0 or result.functions_documented > 0
    
    def _validate_docs(self, context: Dict[str, Any]) -> bool:
        """Validate docs generation phase"""
        result: DocumentationResult = context['result']
        return len(result.output_files) > 0
    
    def _validate_diagrams(self, context: Dict[str, Any]) -> bool:
        """Validate diagram generation phase"""
        result: DocumentationResult = context['result']
        return result.diagrams_generated > 0 or not self.doc_config.generate_diagrams
    
    def _validate_validation(self, context: Dict[str, Any]) -> bool:
        """Validate validation phase"""
        result: DocumentationResult = context['result']
        # Validation always succeeds, but may add warnings
        return len(result.errors) == 0
    
    def _validate_export(self, context: Dict[str, Any]) -> bool:
        """Validate export phase"""
        summary_path = self.doc_config.output_dir / "summary.md"
        return summary_path.exists()
