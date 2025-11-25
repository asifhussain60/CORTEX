"""
Environment Setup Operation - Module Wrapper
Integrates monolithic setup.py with CORTEX 2.0 operations system

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from pathlib import Path
from typing import Dict, Any
from src.operations.base_operation_module import BaseOperationModule, OperationModuleMetadata, OperationResult

# Import monolithic setup implementation
from src.operations.setup import setup_environment as setup_impl


class EnvironmentSetupModule(BaseOperationModule):
    """
    Module wrapper for environment setup operation.
    
    Bridges monolithic setup.py implementation with CORTEX 2.0
    module-based operations architecture.
    """
    
    def _get_metadata(self) -> OperationModuleMetadata:
        """Return module metadata."""
        return OperationModuleMetadata(
            module_id="environment_setup",
            name="Environment Setup",
            description="Configure development environment for CORTEX 3.0",
            version="1.0.0",
            author="Asif Hussain",
            phase="Phase 1.1 Week 3",
            dependencies=[],
            estimated_duration_seconds=180  # 2-5 minutes
        )
    
    def validate(self, context: Dict[str, Any]) -> tuple[bool, str]:
        """
        Validate execution context.
        
        Args:
            context: Execution context with optional 'profile' and 'project_root'
        
        Returns:
            (is_valid, message)
        """
        # Profile validation
        profile = context.get('profile', 'standard')
        valid_profiles = ['minimal', 'standard', 'full']
        
        if profile not in valid_profiles:
            return False, f"Invalid profile '{profile}'. Must be one of: {valid_profiles}"
        
        # Project root validation
        project_root = context.get('project_root')
        if project_root:
            root_path = Path(project_root)
            if not root_path.exists():
                return False, f"Project root does not exist: {project_root}"
        
        return True, "Validation passed"
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Execute environment setup.
        
        Args:
            context: {
                'profile': 'minimal' | 'standard' | 'full',
                'project_root': Optional[Path]
            }
        
        Returns:
            OperationResult with setup details
        """
        # Extract parameters
        profile = context.get('profile', 'standard')
        project_root = context.get('project_root')
        if project_root:
            project_root = Path(project_root)
        
        # Execute monolithic setup implementation
        try:
            result = setup_impl(profile=profile, project_root=project_root)
            
            # Convert to OperationResult
            if result.get('success'):
                return OperationResult(
                    success=True,
                    data={
                        'platform': result.get('platform'),
                        'python_version': result.get('python_version'),
                        'git_version': result.get('git_version'),
                        'venv_created': result.get('venv_created', False),
                        'dependencies_installed': result.get('dependencies_installed', 0),
                        'brain_initialized': result.get('brain_initialized', False)
                    },
                    message=f"Environment setup complete (profile: {profile})",
                    metadata={
                        'profile': profile,
                        'project_root': str(project_root) if project_root else 'auto-detected',
                        'steps_completed': result.get('steps_completed', [])
                    }
                )
            else:
                # Setup failed
                error_msg = result.get('error', 'Unknown error during setup')
                return OperationResult(
                    success=False,
                    data=result,
                    message=f"Environment setup failed: {error_msg}",
                    metadata={
                        'profile': profile,
                        'failed_step': result.get('failed_step')
                    }
                )
        
        except Exception as e:
            return OperationResult(
                success=False,
                data={},
                message=f"Environment setup error: {str(e)}",
                metadata={'exception': type(e).__name__}
            )
    
    def cleanup(self) -> None:
        """Cleanup after execution (no-op for setup)."""
        pass


# Registration function for operations system
def register() -> BaseOperationModule:
    """Register environment setup module with operations system."""
    return EnvironmentSetupModule()
