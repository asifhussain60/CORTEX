"""
Enterprise Documentation Orchestrator Module

Operations module for comprehensive CORTEX documentation generation using EPM system.
Integrates with the Universal Operations architecture and uses response templates
for user communication.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import logging
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from src.operations.base_operation_module import (
    BaseOperationModule, 
    OperationModuleMetadata, 
    OperationResult,
    OperationStatus,
    OperationPhase
)
from src.operations.enterprise_documentation_orchestrator import (
    EnterpriseDocumentationOrchestrator as EPMOrchestrator,
    execute_enterprise_documentation
)

logger = logging.getLogger(__name__)


class EnterpriseDocumentationOrchestratorModule(BaseOperationModule):
    """
    Enterprise Documentation Orchestrator Module
    
    Provides integration between CORTEX Operations system and EPM Documentation Generator.
    Routes natural language documentation requests to the EPM system for comprehensive
    enterprise-grade documentation generation. Uses response templates for consistent
    user communication.
    """
    
    def __init__(self):
        """Initialize the module and load response templates"""
        super().__init__()
        self.response_templates = self._load_response_templates()
    
    def _load_response_templates(self) -> Dict[str, Any]:
        """Load response templates from cortex-brain/response-templates.yaml"""
        try:
            template_path = Path("cortex-brain/response-templates.yaml")
            if template_path.exists():
                with open(template_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    return data.get('templates', {})
            else:
                logger.warning(f"Response templates file not found: {template_path}")
                return {}
        except Exception as e:
            logger.error(f"Failed to load response templates: {str(e)}")
            return {}
    
    def _get_intro_message(self) -> str:
        """Get introduction message from template (without Challenge section)"""
        template = self.response_templates.get('generate_documentation_intro', {})
        return template.get('content', 
            "🧠 **CORTEX Documentation Generation**\n\nStarting documentation generation..."
        )
    
    def _get_completion_message(self, generation_data: Dict[str, Any]) -> str:
        """
        Get completion message from template with actual generation data
        
        Args:
            generation_data: Dictionary containing:
                - api_files: Number of API reference files
                - arch_files: Number of architecture files
                - ops_files: Number of operations files
                - guide_files: Number of guide files
                - xref_count: Number of cross-references
                - total_files: Total file count
                - total_pages: Total page count
                - coverage: Documentation coverage percentage
                - duration: Generation duration
        """
        template = self.response_templates.get('generate_documentation_completion', {})
        message_template = template.get('content', 
            "✅ Documentation generation completed.\n\n📊 Generated {total_files} files."
        )
        
        # Format the message with actual data
        try:
            formatted_message = message_template.format(
                api_files=generation_data.get('api_files', 0),
                arch_files=generation_data.get('arch_files', 0),
                ops_files=generation_data.get('ops_files', 0),
                guide_files=generation_data.get('guide_files', 0),
                xref_count=generation_data.get('xref_count', 0),
                total_files=generation_data.get('total_files', 0),
                total_pages=generation_data.get('total_pages', 0),
                coverage=generation_data.get('coverage', 0),
                duration=generation_data.get('duration', '0s')
            )
            return formatted_message
        except KeyError as e:
            logger.warning(f"Missing template variable: {e}")
            return message_template
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Return metadata for this module"""
        return OperationModuleMetadata(
            module_id="enterprise_documentation_orchestrator",
            name="Enterprise Documentation Orchestrator",
            description="EPM-based comprehensive documentation generation",
            phase=OperationPhase.PROCESSING,
            priority=50,
            dependencies=[],
            optional=False,
            version="1.0.0",
            author="Asif Hussain",
            tags=["documentation", "epm", "enterprise", "generator"]
        )
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Execute enterprise documentation generation
        
        Args:
            context: Operation context with:
                - project_root: Path to CORTEX workspace
                - profile: Generation profile (quick/standard/comprehensive)
                - dry_run: Preview mode flag
                - stage: Optional specific EPM stage to run
                - user_request: Original natural language request
                
        Returns:
            OperationResult with comprehensive generation report
        """
        start_time = datetime.now()
        
        try:
            # Show introduction message using response template
            intro_message = self._get_intro_message()
            logger.info("\n" + intro_message)
            
            # Extract context parameters
            project_root = Path(context.get('project_root', Path.cwd()))
            profile = context.get('profile', 'standard')
            dry_run = context.get('dry_run', False)
            stage = context.get('stage')
            user_request = context.get('user_request', '')
            
            logger.info(f"Starting enterprise documentation generation")
            logger.info(f"Project root: {project_root}")
            logger.info(f"Profile: {profile}")
            logger.info(f"Dry run: {dry_run}")
            logger.info(f"Stage: {stage}")
            
            # Validate workspace
            brain_path = project_root / "cortex-brain"
            if not brain_path.exists():
                return OperationResult(
                    success=False,
                    status=OperationStatus.FAILED,
                    message="❌ CORTEX brain not found. Ensure you're in a CORTEX workspace.",
                    duration_seconds=(datetime.now() - start_time).total_seconds(),
                    errors=[f"Missing: {brain_path}"]
                )
            
            # Parse user request for specific options
            execution_options = self._parse_user_request(user_request, profile, dry_run)
            
            # Execute documentation generation using EPM orchestrator
            result = execute_enterprise_documentation(
                workspace_root=project_root,
                profile=execution_options['profile'],
                dry_run=execution_options['dry_run'],
                stage=stage,
                **execution_options.get('additional_options', {})
            )
            
            # Extract generation data for completion message
            generation_data = self._extract_generation_data(result)
            
            # Generate completion message using response template
            completion_message = self._get_completion_message(generation_data)
            
            # Enhance result with module-specific data
            enhanced_data = result.data.copy() if result.data else {}
            enhanced_data.update({
                "module_execution": {
                    "module_name": self.get_metadata().name,
                    "module_id": self.get_metadata().module_id,
                    "integration_type": "EPM",
                    "epm_orchestrator": "doc_generator",
                    "user_request_parsed": execution_options,
                    "workspace_validated": True,
                    "brain_path": str(brain_path)
                },
                "user_messages": {
                    "intro": intro_message,
                    "completion": completion_message
                }
            })
            
            # Display completion message
            logger.info("\n" + completion_message)
            
            # Return enhanced result with template-based message
            return OperationResult(
                success=result.success,
                status=result.status,
                message=completion_message if result.success else result.message,
                data=enhanced_data,
                errors=result.errors,
                warnings=result.warnings,
                duration_seconds=result.duration_seconds,
                execution_mode=result.execution_mode
            )
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            logger.error(f"Enterprise documentation module failed: {str(e)}")
            
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"❌ Enterprise documentation generation failed: {str(e)}",
                duration_seconds=duration,
                errors=[str(e)]
            )
    
    def _extract_generation_data(self, result: OperationResult) -> Dict[str, Any]:
        """
        Extract generation data from EPM result for completion message
        
        Args:
            result: OperationResult from EPM execution
            
        Returns:
            Dictionary with formatted data for template
        """
        data = result.data or {}
        files_generated = data.get('files_generated', {})
        
        # Count files by category
        api_files = len(files_generated.get('api_reference', []))
        arch_files = len(files_generated.get('architecture', []))
        ops_files = len(files_generated.get('operations', []))
        guide_files = len(files_generated.get('guides', []))
        
        # Total calculations
        total_files = sum([api_files, arch_files, ops_files, guide_files])
        total_pages = data.get('total_pages', total_files)  # Estimate if not provided
        
        # Cross-references
        xref_count = data.get('cross_references_count', 0)
        
        # Coverage
        coverage = data.get('documentation_coverage', 85)  # Default 85%
        
        # Duration
        duration_seconds = result.duration_seconds or 0
        if duration_seconds < 60:
            duration = f"{duration_seconds:.1f}s"
        else:
            minutes = int(duration_seconds // 60)
            seconds = int(duration_seconds % 60)
            duration = f"{minutes}m {seconds}s"
        
        return {
            'api_files': api_files,
            'arch_files': arch_files,
            'ops_files': ops_files,
            'guide_files': guide_files,
            'xref_count': xref_count,
            'total_files': total_files,
            'total_pages': total_pages,
            'coverage': coverage,
            'duration': duration
        }
    
    def _parse_user_request(self, user_request: str, default_profile: str, default_dry_run: bool) -> Dict[str, Any]:
        """
        Parse natural language user request for execution options
        
        Examples:
        - "generate documentation dry run" -> dry_run=True
        - "generate cortex docs comprehensive" -> profile=comprehensive  
        - "/CORTEX Generate documentation" -> uses defaults
        """
        request_lower = user_request.lower()
        
        # Parse profile from request
        profile = default_profile
        if 'quick' in request_lower:
            profile = 'quick'
        elif 'comprehensive' in request_lower or 'complete' in request_lower or 'full' in request_lower:
            profile = 'comprehensive'
        elif 'standard' in request_lower:
            profile = 'standard'
        
        # Parse dry run from request
        dry_run = default_dry_run
        if any(phrase in request_lower for phrase in ['dry run', 'dry-run', 'preview', 'test', 'validate']):
            dry_run = True
        elif any(phrase in request_lower for phrase in ['live', 'execute', 'run', 'generate']):
            dry_run = False
        
        # Parse additional options
        additional_options = {}
        
        # Stage-specific requests
        if 'diagrams' in request_lower or 'diagram' in request_lower:
            additional_options['stage'] = 'diagram-generation'
        elif 'pages' in request_lower or 'page' in request_lower:
            additional_options['stage'] = 'page-generation'
        elif 'cleanup' in request_lower and 'only' in request_lower:
            additional_options['stage'] = 'destructive-cleanup'
        
        return {
            'profile': profile,
            'dry_run': dry_run,
            'additional_options': additional_options,
            'parsed_from': user_request
        }
    
    def validate(self, context: Dict[str, Any]) -> OperationResult:
        """
        Validate readiness for enterprise documentation generation
        
        Checks:
        - CORTEX workspace structure
        - EPM system availability  
        - Configuration files
        - Template availability
        """
        try:
            project_root = Path(context.get('project_root', Path.cwd()))
            
            validation_results = {
                "workspace_structure": self._validate_workspace_structure(project_root),
                "epm_system": self._validate_epm_system(project_root),
                "configuration": self._validate_configuration(project_root),
                "templates": self._validate_templates(project_root)
            }
            
            # Check overall validation status
            all_passed = all(
                result.get("status") == "valid" 
                for result in validation_results.values()
            )
            
            warnings = []
            errors = []
            
            for category, result in validation_results.items():
                if result.get("status") == "warning":
                    warnings.extend(result.get("issues", []))
                elif result.get("status") == "invalid":
                    errors.extend(result.get("issues", []))
            
            if errors:
                return OperationResult(
                    success=False,
                    status=OperationStatus.FAILED,
                    message="❌ Validation failed - workspace not ready for enterprise documentation",
                    data={"validation_results": validation_results},
                    errors=errors,
                    warnings=warnings
                )
            else:
                return OperationResult(
                    success=True,
                    status=OperationStatus.SUCCESS,
                    message="✅ Workspace validated - ready for enterprise documentation generation",
                    data={"validation_results": validation_results},
                    warnings=warnings
                )
                
        except Exception as e:
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"❌ Validation error: {str(e)}",
                errors=[str(e)]
            )
    
    def _validate_workspace_structure(self, project_root: Path) -> Dict[str, Any]:
        """Validate CORTEX workspace structure"""
        required_paths = [
            "cortex-brain",
            "src/epm",
            "docs"
        ]
        
        missing_paths = []
        for path_str in required_paths:
            path = project_root / path_str
            if not path.exists():
                missing_paths.append(path_str)
        
        if missing_paths:
            return {
                "status": "invalid",
                "issues": [f"Missing required path: {path}" for path in missing_paths]
            }
        else:
            return {
                "status": "valid",
                "message": "Workspace structure validated"
            }
    
    def _validate_epm_system(self, project_root: Path) -> Dict[str, Any]:
        """Validate EPM system availability"""
        epm_components = [
            "src/epm/doc_generator.py",
            "src/epm/modules/validation_engine.py",
            "src/epm/modules/cleanup_manager.py",
            "src/epm/modules/diagram_generator.py",
            "src/epm/modules/page_generator.py",
            "src/epm/modules/cross_reference_builder.py"
        ]
        
        missing_components = []
        for component in epm_components:
            if not (project_root / component).exists():
                missing_components.append(component)
        
        if missing_components:
            return {
                "status": "invalid", 
                "issues": [f"Missing EPM component: {comp}" for comp in missing_components]
            }
        else:
            return {
                "status": "valid",
                "message": "EPM system validated"
            }
    
    def _validate_configuration(self, project_root: Path) -> Dict[str, Any]:
        """Validate documentation configuration"""
        config_files = [
            "cortex-brain/admin/documentation/config",
            "cortex-brain/templates/doc-templates"
        ]
        
        missing_configs = []
        for config in config_files:
            if not (project_root / config).exists():
                missing_configs.append(config)
        
        if missing_configs:
            return {
                "status": "warning",
                "issues": [f"Missing config directory: {config}" for config in missing_configs],
                "message": "Some configuration directories missing - EPM will use defaults"
            }
        else:
            return {
                "status": "valid",
                "message": "Configuration validated"
            }
    
    def _validate_templates(self, project_root: Path) -> Dict[str, Any]:
        """Validate documentation templates"""
        templates_path = project_root / "cortex-brain/templates/doc-templates"
        
        if not templates_path.exists():
            return {
                "status": "warning",
                "issues": ["Templates directory missing - EPM will create default templates"],
                "message": "Templates will be auto-generated"
            }
        
        # Count available templates
        template_files = list(templates_path.glob("*.j2"))
        
        return {
            "status": "valid",
            "message": f"Templates validated - {len(template_files)} templates available",
            "template_count": len(template_files)
        }


# Register the module with metadata for factory discovery
ENTERPRISE_DOCUMENTATION_ORCHESTRATOR_MODULE = EnterpriseDocumentationOrchestratorModule