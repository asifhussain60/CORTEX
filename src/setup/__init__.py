"""
CORTEX Setup System

Modular, extensible setup system using SOLID design principles.

Architecture:
    BaseSetupModule (abstract interface)
           ↓
    Concrete Modules (VisionAPIModule, PlatformDetectionModule, etc.)
           ↓
    SetupOrchestrator (coordinates execution)
           ↓
    Module Factory (YAML-driven configuration)

Usage:
    from src.setup import create_setup_orchestrator, run_setup
    
    # Quick setup
    result = run_setup(profile='standard')
    
    # Custom setup
    orchestrator = create_setup_orchestrator(profile='full')
    context = {'project_root': Path('/path/to/cortex')}
    report = orchestrator.execute_setup(context)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from pathlib import Path
from typing import Dict, Optional

from .base_setup_module import (
    BaseSetupModule,
    SetupModuleMetadata,
    SetupResult,
    SetupStatus,
    SetupPhase
)
from .setup_orchestrator import SetupOrchestrator, SetupExecutionReport
from .module_factory import (
    create_orchestrator_from_yaml,
    register_module_class,
    load_setup_config
)
from .post_installation_handler import (
    PostInstallationHandler,
    handle_post_installation_choice
)


def create_setup_orchestrator(
    profile: str = "standard",
    config_path: Optional[Path] = None
) -> SetupOrchestrator:
    """
    Create a configured SetupOrchestrator.
    
    Args:
        profile: Setup profile (minimal, standard, full)
        config_path: Optional path to custom setup_modules.yaml
    
    Returns:
        SetupOrchestrator ready to execute
    """
    return create_orchestrator_from_yaml(config_path, profile)


def run_setup(
    profile: str = "standard",
    project_root: Optional[Path] = None,
    context: Optional[Dict] = None
) -> SetupExecutionReport:
    """
    Convenience function to run complete setup.
    
    Args:
        profile: Setup profile to use
        project_root: Path to CORTEX project (default: auto-detect)
        context: Additional context to pass to modules
    
    Returns:
        SetupExecutionReport with results
    
    Example:
        # Standard setup
        report = run_setup()
        if report.overall_success:
            print("✅ Setup complete!")
        
        # Full setup with Vision API
        report = run_setup(profile='full')
        
        # Custom project path
        report = run_setup(project_root=Path('/custom/path'))
    """
    # Auto-detect project root if not provided
    if project_root is None:
        project_root = _find_project_root()
    
    # Build context
    if context is None:
        context = {}
    
    context.setdefault('project_root', project_root)
    context.setdefault('setup_profile', profile)
    
    # Create orchestrator and execute
    orchestrator = create_setup_orchestrator(profile=profile)
    return orchestrator.execute_setup(context)


def _find_project_root() -> Path:
    """Find CORTEX project root directory."""
    current = Path.cwd()
    while current != current.parent:
        if (current / "cortex-brain").exists() and (current / "src").exists():
            return current
        current = current.parent
    return Path.cwd()


__all__ = [
    # Core classes
    'BaseSetupModule',
    'SetupModuleMetadata',
    'SetupResult',
    'SetupStatus',
    'SetupPhase',
    'SetupOrchestrator',
    'SetupExecutionReport',
    
    # Factory functions
    'create_setup_orchestrator',
    'create_orchestrator_from_yaml',
    'register_module_class',
    'load_setup_config',
    
    # Post-installation
    'PostInstallationHandler',
    'handle_post_installation_choice',
    
    # Convenience function
    'run_setup',
]
