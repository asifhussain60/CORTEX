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
from .parallel_analyzer import ParallelDocumentationAnalyzer
from .preference_tracker import DocumentationPreferenceTracker, DocumentationPreferences
from .style_adaptation import StyleAdaptationEngine, FeedbackLoopIntegrator
from .execution_mode_integration import ExecutionModeIntegration, FormattingConfig
from .enhanced_guardrails import (
    EnhancedDocumentationGuardrail,
    SensitivityLevel,
    RedactionStrategy
)


@dataclass
class DocumentationConfig:
    """Configuration for documentation generation"""
    source_paths: List[Path] = field(default_factory=list)
    output_dir: Path = Path("docs/api")
    include_private: bool = False
    generate_diagrams: bool = True
    generate_quick_ref: bool = True
    use_parallel_analysis: bool = True  # Enable parallel analysis
    enable_adaptive_style: bool = True  # NEW: Enable preference-based style adaptation
    user_id: Optional[str] = None  # NEW: User identifier for preference tracking
    project_id: Optional[str] = None  # NEW: Project identifier for preference scoping
    learn_from_feedback: bool = True  # NEW: Learn from user edits
    # Package 3: Enhanced Guardrails configuration
    enable_guardrails: bool = True  # NEW: Enable PII/PHI/PCI filtering
    sensitivity_level: str = "CONFIDENTIAL"  # NEW: Sensitivity level (PUBLIC, INTERNAL, CONFIDENTIAL, RESTRICTED)
    redaction_strategy: str = "MASK"  # NEW: Redaction strategy (MASK, HASH, REMOVE, PLACEHOLDER)
    enable_audit_trail: bool = True  # NEW: Track all redactions for compliance
    company_patterns: List[Dict[str, str]] = field(default_factory=list)  # NEW: Company-specific patterns to sanitize
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
    - Adaptive style based on user preferences (NEW)
    - Learning from user feedback (NEW)
    
    Example:
        orchestrator = DocumentationOrchestrator(logger, config)
        
        context = {
            'config': DocumentationConfig(
                source_paths=[Path("src/orchestration_4_0")],
                output_dir=Path("docs/orchestration"),
                user_id="dev123",  # Enable preference tracking
                enable_adaptive_style=True  # Enable style adaptation
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
        self.parallel_analyzer = ParallelDocumentationAnalyzer(logger)
        
        # NEW: Initialize AgentLearningEngine for pattern learning
        from ...learning.agent_learning_engine import AgentLearningEngine
        self.learning_engine = AgentLearningEngine()
        
        # NEW: Initialize preference tracking and style adaptation (with learning engine)
        self.preference_tracker = DocumentationPreferenceTracker(logger, learning_engine=self.learning_engine)
        self.style_engine = StyleAdaptationEngine(logger)
        self.feedback_integrator = FeedbackLoopIntegrator(self.preference_tracker, logger)
        
        # NEW: Initialize execution mode integration
        self.mode_integration = ExecutionModeIntegration(logger, config)
        
        # Package 3: Initialize Enhanced Guardrails for PII/PHI/PCI filtering
        self.guardrail = EnhancedDocumentationGuardrail(
            logger=logger,
            default_strategy=RedactionStrategy.MASK,
            enable_audit_trail=True
        )
        
        # Inject loggers
        self.code_analyzer.logger = self.logger
        self.type_extractor.logger = self.logger
        self.api_doc_generator.logger = self.logger
        self.diagram_generator.logger = self.logger
        
        # Store analyzed modules
        self.modules: List[ModuleInfo] = []
        self.doc_config: Optional[DocumentationConfig] = None
        self.doc_result: Optional[DocumentationResult] = None
        
        # NEW: Store user preferences for adaptive generation
        self.user_preferences: Optional[DocumentationPreferences] = None
        
        # NEW: Store formatting configuration from mode integration
        self.formatting_config: Optional[FormattingConfig] = None
        
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
        
        # NEW: Select execution mode and get formatting config
        selected_mode = self.mode_integration.select_mode_for_operation(
            operation_name="generate_documentation",
            estimated_duration=300,  # 5 minutes typical
            override_mode=context.get("execution_mode")
        )
        self.execution_mode = selected_mode.value
        
        # Get context-aware formatting configuration
        self.formatting_config = self.mode_integration.get_formatting_config(selected_mode)
        context['execution_mode'] = selected_mode
        context['formatting_config'] = self.formatting_config
        
        self.logger.info(
            f"🎭 Mode selected: {selected_mode.value}, "
            f"formatting: {self.formatting_config.detail_level.value}"
        )
        
        # NEW: Load user preferences if adaptive style is enabled
        if self.doc_config.enable_adaptive_style and self.doc_config.user_id:
            self.user_preferences = self.preference_tracker.get_preferences(
                user_id=self.doc_config.user_id,
                project_id=self.doc_config.project_id
            )
            self.logger.info(
                f"🎨 Loaded preferences for user '{self.doc_config.user_id}': "
                f"style={self.user_preferences.style.value}, "
                f"tone={self.user_preferences.tone.value}, "
                f"depth={self.user_preferences.depth.value}"
            )
            
            # Get confidence score
            confidence = self.feedback_integrator.get_preference_confidence(
                self.doc_config.user_id
            )
            if confidence > 0:
                self.logger.info(f"📊 Preference confidence: {confidence:.1%}")
        else:
            self.user_preferences = None
            if self.doc_config.enable_adaptive_style:
                self.logger.info("⚠️  Adaptive style enabled but no user_id provided")
        
        # Package 3: Configure guardrails with company-specific patterns
        if self.doc_config.enable_guardrails and self.doc_config.company_patterns:
            self.logger.info(f"🛡️  Configuring {len(self.doc_config.company_patterns)} company-specific patterns")
            for pattern_config in self.doc_config.company_patterns:
                pattern_name = pattern_config.get('name', 'CUSTOM_PATTERN')
                pattern_regex = pattern_config.get('pattern', '')
                if pattern_regex:
                    self.guardrail.add_company_pattern(pattern_name, pattern_regex)
                    self.logger.debug(f"  - Added pattern: {pattern_name}")
        
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
        
        # NEW: Add style adaptation phase if enabled
        if self.doc_config and self.doc_config.enable_adaptive_style and self.user_preferences:
            self.phase_manager.register_phase(
                "adapt_style",
                description="Adapt documentation style to user preferences"
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
        elif phase_name == "adapt_style":  # NEW
            return self._adapt_style_phase(context, result)
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
        
        # Use parallel analysis if enabled
        if self.doc_config.use_parallel_analysis:
            return self._analyze_phase_parallel(context, result)
        
        # Fall back to sequential analysis
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
    
    def _analyze_phase_parallel(
        self,
        context: Dict[str, Any],
        result: DocumentationResult
    ) -> Dict[str, Any]:
        """
        Analyze Python files using parallel multi-agent analysis
        
        Uses ParallelDocumentationAnalyzer to analyze API, architecture,
        and user guide documentation concurrently.
        """
        import asyncio
        
        self.logger.info("Phase: ANALYZE - Using parallel multi-agent analysis")
        
        # Run parallel analysis
        try:
            # Create event loop if not in async context
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            parallel_results = loop.run_until_complete(
                self.parallel_analyzer.analyze_parallel(self.doc_config.source_paths)
            )
            
            # Extract results
            api_result = parallel_results['api']
            arch_result = parallel_results['architecture']
            guide_result = parallel_results['user_guide']
            validation = parallel_results['validation']
            
            # Update documentation result
            result.modules_analyzed = api_result.modules_analyzed
            result.errors.extend(api_result.errors)
            result.errors.extend(arch_result.errors)
            result.errors.extend(guide_result.errors)
            result.warnings.extend(api_result.warnings)
            result.warnings.extend(arch_result.warnings)
            result.warnings.extend(guide_result.warnings)
            
            # Log validation issues
            if validation.broken_references > 0:
                self.logger.warning(
                    f"Cross-reference validation found {validation.broken_references} "
                    f"broken references out of {validation.references_checked} checked"
                )
                for issue in validation.issues:
                    result.warnings.append(
                        f"Cross-reference issue: {issue.description} ({issue.location})"
                    )
            
            # Still populate self.modules for subsequent phases using sequential analysis
            # (Parallel analyzer provides metadata, but full AST analysis still needed)
            self.modules.clear()
            for source_path in self.doc_config.source_paths:
                if source_path.is_dir():
                    for py_file in source_path.rglob("*.py"):
                        if '__pycache__' in str(py_file) or py_file.name.startswith('test_'):
                            continue
                        try:
                            module_info = self.code_analyzer.analyze_file(py_file)
                            self.modules.append(module_info)
                        except Exception as e:
                            error_msg = f"Failed to analyze {py_file}: {e}"
                            self.logger.warning(error_msg)
                            result.warnings.append(error_msg)
            
            self.logger.info(
                f"✅ Parallel analysis complete: {result.modules_analyzed} modules, "
                f"{validation.valid_references} valid refs, {validation.broken_references} broken refs"
            )
            
        except Exception as e:
            error_msg = f"Parallel analysis failed: {e}"
            self.logger.error(error_msg)
            result.errors.append(error_msg)
            
            # Fall back to sequential analysis
            self.logger.info("Falling back to sequential analysis")
            return self._analyze_phase(context, result)
        
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
        
        # Package 3: Apply guardrails to filter sensitive data from generated docs
        if self.doc_config.enable_guardrails:
            self.logger.info("🛡️  Applying guardrails to filter sensitive data")
            total_redactions = 0
            
            for doc_file in result.output_files:
                try:
                    # Read generated documentation
                    if doc_file.suffix == '.md':
                        original_content = doc_file.read_text(encoding='utf-8')
                        
                        # Apply guardrails
                        sensitivity = SensitivityLevel[self.doc_config.sensitivity_level]
                        strategy = RedactionStrategy[self.doc_config.redaction_strategy]
                        
                        redaction_result = self.guardrail.redact_sensitive_data(
                            text=original_content,
                            sensitivity=sensitivity,
                            strategy=strategy
                        )
                        
                        # Write filtered content if any redactions were made
                        if redaction_result.redaction_count > 0:
                            doc_file.write_text(redaction_result.redacted_text, encoding='utf-8')
                            total_redactions += redaction_result.redaction_count
                            
                            self.logger.info(
                                f"🛡️  Filtered {redaction_result.redaction_count} sensitive items from {doc_file.name} "
                                f"({', '.join(redaction_result.data_types_found)})"
                            )
                            
                            # Log audit trail if enabled
                            if self.doc_config.enable_audit_trail and redaction_result.audit_trail:
                                for audit_entry in redaction_result.audit_trail[:5]:  # Show first 5
                                    self.logger.debug(f"  - {audit_entry}")
                                if len(redaction_result.audit_trail) > 5:
                                    self.logger.debug(f"  ... and {len(redaction_result.audit_trail) - 5} more")
                        
                except Exception as e:
                    error_msg = f"Failed to apply guardrails to {doc_file.name}: {e}"
                    self.logger.warning(error_msg)
                    result.warnings.append(error_msg)
            
            if total_redactions > 0:
                self.logger.info(f"✅ Guardrails complete: {total_redactions} total redactions applied")
            else:
                self.logger.info("✅ Guardrails complete: No sensitive data detected")
        
        return context
    
    def _adapt_style_phase(
        self,
        context: Dict[str, Any],
        result: DocumentationResult
    ) -> Dict[str, Any]:
        """
        Adapt generated documentation to user preferences
        
        NEW: Applies learned preferences to transform documentation style,
        tone, and depth to match user expectations.
        """
        self.logger.info("Phase: ADAPT_STYLE - Applying user preferences")
        
        if not self.user_preferences:
            self.logger.warning("No user preferences available, skipping style adaptation")
            return context
        
        if not result.output_files:
            self.logger.warning("No documentation files to adapt")
            return context
        
        adapted_count = 0
        skip_count = 0
        
        # Adapt each generated markdown documentation file
        for doc_path in result.output_files:
            if doc_path.suffix == '.md' and doc_path.name != 'summary.md':
                try:
                    # Read original documentation
                    original_content = doc_path.read_text(encoding='utf-8')
                    
                    # Apply style adaptation
                    adapted_content = self.style_engine.adapt_documentation(
                        original_doc=original_content,
                        preferences=self.user_preferences
                    )
                    
                    # Write adapted content back
                    doc_path.write_text(adapted_content, encoding='utf-8')
                    adapted_count += 1
                    
                    self.logger.info(f"✨ Adapted: {doc_path.name}")
                    
                except Exception as e:
                    # Log as warning instead of error to avoid failing the phase
                    warning_msg = f"Could not adapt {doc_path.name}: {e}"
                    self.logger.warning(warning_msg)
                    result.warnings.append(warning_msg)
                    skip_count += 1
        
        # Log adaptation summary
        if adapted_count > 0:
            self.logger.info(
                f"✅ Adapted {adapted_count} files - "
                f"Style: {self.user_preferences.style.value}, "
                f"Tone: {self.user_preferences.tone.value}, "
                f"Depth: {self.user_preferences.depth.value}"
            )
            
            # Get and log confidence score
            confidence = self.feedback_integrator.get_preference_confidence(
                self.doc_config.user_id
            )
            self.logger.info(f"📊 Adaptation confidence: {confidence:.1%}")
        elif skip_count > 0:
            self.logger.info(f"⚠️  Skipped {skip_count} files due to adaptation issues")
        
        return context
    
    def _generate_diagrams_phase(
        self,
        context: Dict[str, Any],
        result: DocumentationResult
    ) -> Dict[str, Any]:
        """Generate D3.js interactive diagrams"""
        self.logger.info("Phase: GENERATE_DIAGRAMS - Creating visualizations")
        
        # NEW: Check if diagrams should be included based on mode
        if self.formatting_config and not self.formatting_config.include_diagrams:
            self.logger.info("⏭️  Skipping diagram generation (mode: AUTONOMOUS)")
            return context
        
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
        
        # NEW: Update user statistics after successful completion
        if hasattr(self, 'mode_integration') and self.mode_integration:
            self.mode_integration.update_user_stats(
                operation_name="generate_documentation",
                success=len(result.errors) == 0
            )
        
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
    
    # NEW: Preference learning and feedback methods
    
    def learn_from_user_edit(
        self,
        original_doc: str,
        edited_doc: str,
        user_id: Optional[str] = None,
        force_learn: bool = False
    ) -> None:
        """
        Learn from user's edits to generated documentation
        
        Analyzes the differences between generated and edited documentation
        to infer user preferences and improve future generations.
        
        Args:
            original_doc: Original generated documentation
            edited_doc: User-edited version
            user_id: User identifier (REQUIRED if called before execute())
            force_learn: Force learning even if learn_from_feedback=False
            
        Example:
            # After user edits generated docs
            orchestrator.learn_from_user_edit(
                original_doc=original_content,
                edited_doc=user_edited_content,
                user_id="user123"  # Required if doc_config not yet set
            )
        """
        # Determine target user_id
        target_user_id = user_id
        if not target_user_id and self.doc_config:
            target_user_id = self.doc_config.user_id
        
        if not target_user_id:
            self.logger.warning(
                "Cannot learn from edit: No user_id specified. "
                "Pass user_id parameter when calling before execute()."
            )
            return
        
        # Check if learning is enabled (skip if force_learn=True or user_id explicitly passed)
        if not force_learn and not user_id:
            if not self.doc_config or not self.doc_config.learn_from_feedback:
                self.logger.info("Learning from feedback is disabled")
                return
        
        self.logger.info(f"🧠 Learning from user edit for '{target_user_id}'")
        
        try:
            # Use feedback integrator to process edit
            self.feedback_integrator.process_user_edit(
                user_id=target_user_id,
                original_doc=original_doc,
                edited_doc=edited_doc
            )
            
            self.logger.info("✅ Successfully learned from user edit")
            
        except Exception as e:
            self.logger.error(f"Failed to learn from edit: {e}")
    
    def get_user_preferences(self, user_id: Optional[str] = None) -> Optional[DocumentationPreferences]:
        """
        Get current preferences for a user
        
        Args:
            user_id: User identifier (uses config user_id if not provided)
            
        Returns:
            DocumentationPreferences if available, None otherwise
        """
        target_user_id = user_id or (self.doc_config.user_id if self.doc_config else None)
        
        if not target_user_id:
            return None
        
        return self.preference_tracker.get_preferences(
            user_id=target_user_id,
            project_id=self.doc_config.project_id if self.doc_config else None
        )
    
    def update_user_preference(
        self,
        preference_type: str,
        new_value: str,
        reason: str = "user_feedback",
        user_id: Optional[str] = None
    ) -> None:
        """
        Manually update a specific user preference
        
        Args:
            preference_type: Type of preference (style, tone, depth, example_density)
            new_value: New value for the preference
            reason: Reason for update
            user_id: User identifier (REQUIRED if called before execute())
            
        Example:
            orchestrator.update_user_preference(
                preference_type="style",
                new_value="technical",
                reason="user_explicit_request",
                user_id="user123"  # Required if doc_config not yet set
            )
        """
        # Determine target user_id
        # Priority: 1) explicit user_id param, 2) config user_id, 3) error
        target_user_id = user_id
        if not target_user_id and self.doc_config:
            target_user_id = self.doc_config.user_id
        
        if not target_user_id:
            self.logger.warning(
                "Cannot update preference: No user_id specified. "
                "Pass user_id parameter when calling before execute()."
            )
            return
        
        self.logger.info(
            f"📝 Updating preference for '{target_user_id}': "
            f"{preference_type}={new_value} (reason: {reason})"
        )
        
        try:
            self.preference_tracker.update_preference(
                user_id=target_user_id,
                preference_type=preference_type,
                new_value=new_value,
                reason=reason,
                project_id=self.doc_config.project_id if self.doc_config else None
            )
            
            # Reload preferences
            self.user_preferences = self.preference_tracker.get_preferences(
                user_id=target_user_id,
                project_id=self.doc_config.project_id if self.doc_config else None
            )
            
            self.logger.info("✅ Preference updated successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to update preference: {e}")
    
    def get_preference_confidence(self, user_id: Optional[str] = None) -> float:
        """
        Get confidence score for user's preferences
        
        Higher confidence means more historical data and consistent preferences.
        
        Args:
            user_id: User identifier (uses config user_id if not provided)
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        target_user_id = user_id or (self.doc_config.user_id if self.doc_config else None)
        
        if not target_user_id:
            return 0.0
        
        return self.feedback_integrator.get_preference_confidence(target_user_id)
    
    # Package 3: Enhanced Guardrails methods
    
    def get_guardrail_statistics(self) -> Dict[str, int]:
        """
        Get guardrail usage statistics
        
        Returns:
            Dictionary with guardrail statistics:
            - total_scans: Number of scans performed
            - total_redactions: Total redactions applied
            - company_patterns: Number of company patterns configured
            - whitelist_entries: Number of whitelisted items
            
        Example:
            stats = orchestrator.get_guardrail_statistics()
            print(f"Applied {stats['total_redactions']} redactions across {stats['total_scans']} scans")
        """
        return self.guardrail.get_statistics()
    
    def add_guardrail_whitelist(self, text: str) -> None:
        """
        Add text to guardrail whitelist (won't be redacted)
        
        Useful for false positives like common variable names or test data.
        
        Args:
            text: Text to whitelist (case-insensitive)
            
        Example:
            # Prevent redacting test email addresses
            orchestrator.add_guardrail_whitelist("test@example.com")
            orchestrator.add_guardrail_whitelist("user@test.local")
        """
        self.guardrail.add_to_whitelist(text)
        self.logger.info(f"🛡️  Added to guardrail whitelist: {text}")
    
    def configure_company_guardrail_pattern(self, pattern_name: str, pattern_regex: str) -> None:
        """
        Add a company-specific pattern to guardrails
        
        Args:
            pattern_name: Name for the pattern (e.g., "COMPANY_DOMAIN")
            pattern_regex: Regex pattern to match
            
        Example:
            # Redact company domains
            orchestrator.configure_company_guardrail_pattern(
                "ACME_DOMAIN",
                r"\\b[\\w.-]+@acme\\.com\\b"
            )
            
            # Redact internal IPs
            orchestrator.configure_company_guardrail_pattern(
                "INTERNAL_IP",
                r"\\b10\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\b"
            )
        """
        self.guardrail.add_company_pattern(pattern_name, pattern_regex)
        self.logger.info(f"🛡️  Added company guardrail pattern: {pattern_name}")
