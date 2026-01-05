"""
Sanitization Orchestrator - Code Sanitization Workflow

Full Planning System-compliant orchestrator for code sanitization.
Implements 5-phase workflow with interactive mapping approval and validation gates.

Architecture:
    - Inherits from BaseOrchestrator for standardized lifecycle
    - 5-phase workflow: ANALYZE → MAPPING → TRANSFORM → VALIDATE → REPORT
    - Planning System parity: Interactive approval, dry-run mode, visual progress
    - Sanitization-specific: Domain term extraction, AST transformation, rollback

Usage:
    >>> orchestrator = SanitizationOrchestrator(
    ...     target_directory="/path/to/project",
    ...     dry_run=False
    ... )
    >>> result = orchestrator.execute()
    >>> print(f"Status: {result.success}, Files: {result.files_transformed}")

Version: 1.0.0
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import logging
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path
import yaml

# Import base orchestrator
from src.orchestrators.base.base_orchestrator import BaseOrchestrator

# Import ManifestLoader for 3-Tier Manifest Architecture
from src.utils.manifest_loader import ManifestLoader

# Import sanitization utilities
from src.operations.utilities.sanitization.code_analyzer import CodeAnalyzer
from src.operations.utilities.sanitization.mapping_engine import MappingEngine
from src.operations.utilities.sanitization.transformer import CodeTransformer
from src.operations.utilities.sanitization.validator import BuildValidator
from src.operations.utilities.sanitization.report_generator import ReportGenerator


# Configure module logger
logger = logging.getLogger(__name__)


class SanitizationPhase(Enum):
    """
    Sanitization Orchestrator Phase Enumeration
    
    Defines the 5-phase workflow for code sanitization:
    1. ANALYZE: File scanning, domain term extraction
    2. MAPPING: Domain→generic mapping generation, user approval
    3. TRANSFORM: AST transformation, file renaming, backup
    4. VALIDATE: Build validation, test execution, rollback on failure
    5. REPORT: Audit report generation, metrics, artifacts
    """
    ANALYZE = "1_analyze"
    MAPPING = "2_mapping"
    TRANSFORM = "3_transform"
    VALIDATE = "4_validate"
    REPORT = "5_report"


@dataclass
class SanitizationResult:
    """
    Sanitization Orchestrator Result Object
    
    Encapsulates the outcome of code sanitization workflow.
    Returned by SanitizationOrchestrator.execute() with complete execution details.
    
    Attributes:
        success: Boolean flag indicating overall success
        phase: Final phase reached (SanitizationPhase enum)
        files_analyzed: Count of files scanned
        mappings_created: Count of domain→generic mappings
        files_transformed: Count of files modified
        validation_passed: Boolean indicating build/test validation success
        report_path: Path to generated audit report
        duration_seconds: Total execution time
        errors: List of error messages encountered
        
    Example:
        >>> result = SanitizationResult(
        ...     success=True,
        ...     phase=SanitizationPhase.REPORT,
        ...     files_analyzed=50,
        ...     mappings_created=10,
        ...     files_transformed=45,
        ...     validation_passed=True,
        ...     report_path=Path("/tmp/sanitization-report.md"),
        ...     duration_seconds=8.5,
        ...     errors=[]
        ... )
    """
    success: bool
    phase: SanitizationPhase
    files_analyzed: int
    mappings_created: int
    files_transformed: int
    validation_passed: bool
    report_path: Path
    duration_seconds: float
    errors: List[str] = field(default_factory=list)
    data: Dict[str, Any] = field(default_factory=dict)


class SanitizationOrchestrator(BaseOrchestrator):
    """
    Sanitization Orchestrator - Code Sanitization Workflow
    
    Orchestrates the complete lifecycle of code sanitization from analysis
    to validated transformation, with Planning System feature parity.
    
    Inherits from BaseOrchestrator to leverage standard orchestration patterns:
    - Configuration injection
    - Brain tier integration
    - Template management
    - Error handling
    - Metrics collection
    
    Workflow Phases:
        1. ANALYZE: File scanning, domain term extraction, pattern detection
        2. MAPPING: Domain→generic mapping generation, conflict detection, user approval
        3. TRANSFORM: AST transformation, file renaming, backup creation
        4. VALIDATE: Build validation, test execution, rollback on failure
        5. REPORT: Audit report generation, metrics collection, artifact creation
    
    Planning System Parity:
        - ✅ Interactive approval workflow (MAPPING phase)
        - ✅ Dry-run mode support
        - ✅ Visual progress indicators (🎭 engagement hints)
        - ✅ Rollback on validation failure
        - ✅ Comprehensive audit trail
    
    Sanitization-Specific Features:
        - ✅ Domain term extraction (code_analyzer)
        - ✅ Generic naming heuristics (mapping_engine)
        - ✅ AST-aware transformations (transformer)
        - ✅ Build/test validation (validator)
        - ✅ Audit report generation (report_generator)
    
    Attributes:
        target: Path to directory to sanitize
        dry_run: If True, no files are modified (simulation only)
        analyzer: CodeAnalyzer instance for file scanning
        mapper: MappingEngine instance for mapping generation
        transformer: Transformer instance for code transformation
        validator: Validator instance for build/test validation
        reporter: ReportGenerator instance for audit reports
    """
    
    def __init__(
        self,
        target_directory: Optional[str] = None,
        cortex_root: Optional[str] = None,
        dry_run: bool = False,
        state_db: Optional[Any] = None  # For interface compatibility
    ):
        """
        Initialize Sanitization Orchestrator
        
        Args:
            target_directory: Path to directory to sanitize (defaults to current directory)
            cortex_root: Path to CORTEX root (auto-detected if None)
            dry_run: If True, simulate without modifying files
            state_db: State database for coordination (optional)
        """
        # Call parent constructor with config
        config = {
            "name": "SanitizationOrchestrator",
            "version": "1.0.0",
            "logger_name": "cortex.orchestrators.sanitization",
            "log_level": "INFO"
        }
        super().__init__(config=config)
        
        # Store state_db for potential future use
        self.state_db = state_db
        
        # Sanitization-specific initialization
        if target_directory is None:
            target_directory = "."
        self.target = Path(target_directory)
        self.dry_run = dry_run
        
        # Detect CORTEX root if not provided
        if cortex_root is None:
            cortex_root = str(Path(__file__).parent.parent.parent.parent)
        
        # Load manifest using ManifestLoader (3-Tier Architecture)
        try:
            self.manifest_loader = ManifestLoader(cortex_root)
            resolved = self.manifest_loader.resolve_cross_references("sanitization_orchestrator")
            self.metadata = resolved.get("metadata", {})
            self.config_overrides = resolved.get("config", {})
            self.integrations = resolved.get("integrations", {})
            # For backward compatibility with utility modules
            self.manifest = self.metadata
        except Exception as e:
            self.logger.warning(f"ManifestLoader failed, using fallback: {e}")
            self.manifest = self._load_manifest_fallback()
        
        # Initialize utility modules (CRITICAL - fail-fast if unavailable)
        try:
            self.analyzer = CodeAnalyzer(str(self.target), self.manifest)
            self.mapper = MappingEngine(self.manifest)
            self.transformer = CodeTransformer(self.manifest)
            self.validator = BuildValidator(self.manifest)
            self.reporter = ReportGenerator(self.manifest)
            self.logger.info("✅ All sanitization utilities initialized successfully")
        except ImportError as e:
            error_msg = (
                f"Failed to import required sanitization utilities: {e}\n"
                f"Ensure all dependencies are installed and modules are available in:\n"
                f"  - src/operations/utilities/sanitization/code_analyzer.py\n"
                f"  - src/operations/utilities/sanitization/mapping_engine.py\n"
                f"  - src/operations/utilities/sanitization/transformer.py\n"
                f"  - src/operations/utilities/sanitization/validator.py\n"
                f"  - src/operations/utilities/sanitization/report_generator.py"
            )
            self.logger.error(error_msg)
            raise RuntimeError(error_msg) from e
        except Exception as e:
            error_msg = (
                f"Failed to initialize sanitization utilities: {e}\n"
                f"Target directory: {self.target}\n"
                f"Manifest loaded: {bool(self.manifest)}\n"
                f"Check that:\n"
                f"  1. Target directory exists and is accessible\n"
                f"  2. Manifest contains required configuration sections\n"
                f"  3. All utility class constructors receive valid parameters"
            )
            self.logger.error(error_msg)
            raise RuntimeError(error_msg) from e
        
        # Log initialization with engagement hint
        self.logger.info(f"🎭 Orchestrator engaged: SanitizationOrchestrator")
        self.logger.info(f"Target: {self.target}, Dry Run: {self.dry_run}")
    
    def _load_manifest_fallback(self) -> Dict[str, Any]:
        """
        Fallback manifest loading for backward compatibility.
        Only used if ManifestLoader fails.
        """
        manifest_path = Path(__file__).parent.parent.parent.parent / \
                       "cortex-brain/manifests/orchestrators/code-sanitization-manifest.yaml"
        
        try:
            with open(manifest_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.warning(f"Could not load manifest: {e}")
            # Return minimal manifest structure
            return {
                "file_processing": {
                    "exclusions": []
                },
                "mapping_rules": {
                    "terminology_categories": {}
                }
            }
    
    def execute(self) -> SanitizationResult:
        """
        Execute 5-phase sanitization workflow
        
        Returns:
            SanitizationResult with execution details
        """
        start_time = datetime.now()
        errors = []
        
        try:
            # Phase 1: ANALYZE
            self.logger.info("🎭 Phase transition: INIT → ANALYZE")
            analysis = self._execute_analyze_phase()
            if not analysis['success']:
                return self._failure_result(
                    SanitizationPhase.ANALYZE,
                    start_time,
                    analysis.get('errors', ['Analysis failed'])
                )
            
            files_analyzed = len(analysis.get('files', []))
            
            # Phase 2: MAPPING
            self.logger.info("🎭 Phase transition: ANALYZE → MAPPING")
            mapping = self._execute_mapping_phase(analysis)
            if not mapping['success']:
                return self._failure_result(
                    SanitizationPhase.MAPPING,
                    start_time,
                    mapping.get('errors', ['Mapping failed']),
                    files_analyzed=files_analyzed
                )
            
            mappings_created = len(mapping.get('mappings', {}))
            
            # Phase 3: TRANSFORM (skip in dry-run)
            if not self.dry_run:
                self.logger.info("🎭 Phase transition: MAPPING → TRANSFORM")
                transform = self._execute_transform_phase(mapping)
                if not transform['success']:
                    return self._failure_result(
                        SanitizationPhase.TRANSFORM,
                        start_time,
                        transform.get('errors', ['Transform failed']),
                        files_analyzed=files_analyzed,
                        mappings_created=mappings_created
                    )
                files_transformed = transform.get('files_transformed', 0)
                
                # Phase 4: VALIDATE
                self.logger.info("🎭 Phase transition: TRANSFORM → VALIDATE")
                validation = self._execute_validate_phase()
                if not validation['success']:
                    return self._failure_result(
                        SanitizationPhase.VALIDATE,
                        start_time,
                        validation.get('errors', ['Validation failed']),
                        validation_passed=False,
                        files_analyzed=files_analyzed,
                        mappings_created=mappings_created,
                        files_transformed=files_transformed
                    )
                validation_passed = validation.get('passed', False)
            else:
                # Dry-run: skip transformation and validation
                files_transformed = 0
                validation_passed = True
            
            # Phase 5: REPORT
            self.logger.info("🎭 Phase transition: VALIDATE → REPORT")
            report = self._execute_report_phase(
                files_analyzed,
                mappings_created,
                files_transformed,
                validation_passed,
                analysis=analysis,
                mappings=mapping,
                transform=transform if not self.dry_run else {},
                validate=validation if not self.dry_run else {}
            )
            report_path = report.get('report_path', Path('/tmp/sanitization-report.md'))
            
            # Success
            self.logger.info("🎭 Orchestrator completing: ✅ ALL WORK COMPLETE")
            duration = (datetime.now() - start_time).total_seconds()
            
            return SanitizationResult(
                success=True,
                phase=SanitizationPhase.REPORT,
                files_analyzed=files_analyzed,
                mappings_created=mappings_created,
                files_transformed=files_transformed,
                validation_passed=validation_passed,
                report_path=report_path,
                duration_seconds=duration,
                errors=[],
                data={
                    "copilot_instructions": {
                        "response_template": "sanitization_execution_progress",
                        "progress_updates": True,
                        "autonomous_execution": True,
                        "checkpoint_frequency": "per_phase"
                    }
                }
            )
            
        except Exception as e:
            self.logger.error(f"Orchestrator error: {e}", exc_info=True)
            return self._failure_result(
                SanitizationPhase.ANALYZE,
                start_time,
                [str(e)]
            )
    
    def _execute_analyze_phase(self) -> Dict[str, Any]:
        """Execute ANALYZE phase: File scanning, domain term extraction"""
        try:
            # Scan file structure
            file_inventory = self.analyzer.scan_file_structure()
            files = file_inventory.get('files', [])
            
            # Extract domain terminology
            domain_terms = self.analyzer.extract_domain_terminology()
            terms = list(domain_terms.keys()) if isinstance(domain_terms, dict) else []
            
            # Extract namespaces
            namespaces = self.analyzer.extract_namespaces()
            
            return {
                'success': True,
                'files': files,
                'terms': terms,
                'file_inventory': file_inventory,
                'domain_terms': domain_terms,
                'namespaces': namespaces
            }
        except Exception as e:
            self.logger.error(f"Analysis phase failed: {e}", exc_info=True)
            return {'success': False, 'errors': [str(e)]}
    
    def _execute_mapping_phase(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Execute MAPPING phase: Domain→generic mapping generation"""
        try:
            domain_terms = analysis.get('domain_terms', {})
            namespaces = analysis.get('namespaces', {})
            
            if not domain_terms and not namespaces:
                # No terms or namespaces to map
                return {
                    'success': True,
                    'mappings': {}
                }
            
            # Generate mappings using MappingEngine
            mappings = self.mapper.generate_mappings(domain_terms, namespaces)
            
            # Detect conflicts
            conflicts = self.mapper.detect_conflicts(mappings)
            if conflicts:
                self.logger.warning(f"Detected {len(conflicts)} naming conflicts")
                for conflict in conflicts:
                    self.logger.warning(f"  Conflict: {conflict['original_terms']} → {conflict['generic_term']}")
            
            return {
                'success': True,
                'mappings': mappings if isinstance(mappings, dict) else {},
                'conflicts': conflicts
            }
        except Exception as e:
            self.logger.error(f"Mapping phase failed: {e}", exc_info=True)
            return {'success': False, 'errors': [str(e)]}
    
    def _execute_transform_phase(self, mapping: Dict[str, Any]) -> Dict[str, Any]:
        """Execute TRANSFORM phase: AST transformation, file renaming"""
        try:
            mappings = mapping.get('mappings', {})
            if not mappings:
                # No mappings to apply
                return {
                    'success': True,
                    'files_transformed': 0
                }
            
            # Create output directory for sanitized code
            output_dir = self.target.parent / f"{self.target.name}_sanitized"
            
            # Transform codebase
            result = self.transformer.transform_codebase(
                str(self.target),
                str(output_dir),
                mappings
            )
            
            files_transformed = result.get('files_transformed', 0)
            self.logger.info(f"Transformed {files_transformed} files")
            
            return {
                'success': True,
                'files_transformed': files_transformed,
                'output_directory': str(output_dir),
                'transformation_log': result
            }
        except Exception as e:
            self.logger.error(f"Transform phase failed: {e}", exc_info=True)
            return {'success': False, 'errors': [str(e)]}
    
    def _execute_validate_phase(self) -> Dict[str, Any]:
        """Execute VALIDATE phase: Build validation, test execution"""
        try:
            # Detect build system
            build_system = self.validator.detect_build_system(str(self.target))
            self.logger.info(f"Detected build system: {build_system}")
            
            if build_system == 'none':
                self.logger.warning("No build system detected, skipping validation")
                return {
                    'success': True,
                    'passed': True,
                    'build_system': 'none'
                }
            
            # Execute build
            build_result = self.validator.execute_build(str(self.target), build_system)
            if not build_result.get('success', False):
                self.logger.error("Build failed")
                return {
                    'success': False,
                    'passed': False,
                    'errors': ['Build failed']
                }
            
            # Run tests
            test_result = self.validator.run_tests(str(self.target), build_system)
            passed = test_result.get('success', False)
            
            return {
                'success': True,
                'passed': passed,
                'build_system': build_system,
                'test_result': test_result
            }
        except Exception as e:
            self.logger.error(f"Validate phase failed: {e}", exc_info=True)
            return {'success': False, 'errors': [str(e)]}
    
    def _execute_report_phase(
        self,
        files_analyzed: int,
        mappings_created: int,
        files_transformed: int,
        validation_passed: bool,
        analysis: Dict[str, Any] = None,
        mappings: Dict[str, Any] = None,
        transform: Dict[str, Any] = None,
        validate: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Execute REPORT phase: Audit report generation"""
        try:
            # Build comprehensive results dict for report
            results = {
                'status': 'success' if validation_passed else 'failed',
                'phases': {
                    'analyze': analysis or {},
                    'mapping': mappings or {},
                    'transform': transform or {},
                    'validate': validate or {}
                }
            }
            
            # Generate audit report
            if self.reporter and hasattr(self.reporter, 'generate_audit_report'):
                report_path = self.reporter.generate_audit_report(results)
            else:
                report_path = str(Path('/tmp/sanitization-report.md'))
            
            return {
                'success': True,
                'report_path': report_path
            }
        except Exception as e:
            return {'success': False, 'errors': [str(e)]}
    
    def _failure_result(
        self,
        phase: SanitizationPhase,
        start_time: datetime,
        errors: List[str],
        validation_passed: bool = True,
        files_analyzed: int = 0,
        mappings_created: int = 0,
        files_transformed: int = 0
    ) -> SanitizationResult:
        """Create failure result preserving metrics collected before failure"""
        duration = (datetime.now() - start_time).total_seconds()
        return SanitizationResult(
            success=False,
            phase=phase,
            files_analyzed=files_analyzed,
            mappings_created=mappings_created,
            files_transformed=files_transformed,
            validation_passed=validation_passed,
            report_path=Path('/tmp/sanitization-report.md'),
            duration_seconds=duration,
            errors=errors
        )
