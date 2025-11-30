"""
Setup Module Factory

Discovers and instantiates setup modules from YAML configuration.
Implements Factory pattern for module creation.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import yaml
import logging
from pathlib import Path
from typing import Dict, List, Optional, Type

from .base_setup_module import BaseSetupModule, SetupModuleMetadata, SetupPhase
from .setup_orchestrator import SetupOrchestrator

# Module logger
logger = logging.getLogger(__name__)

# Module registry - maps module_id to class
MODULE_REGISTRY: Dict[str, Type[BaseSetupModule]] = {}


def register_module_class(module_id: str, module_class: Type[BaseSetupModule]):
    """
    Register a module class for factory instantiation.
    
    Args:
        module_id: Unique module identifier
        module_class: Class implementing BaseSetupModule
    """
    MODULE_REGISTRY[module_id] = module_class


def load_setup_config(config_path: Optional[Path] = None) -> Dict:
    """
    Load setup configuration from YAML.
    
    Args:
        config_path: Path to setup_modules.yaml (default: auto-detect)
    
    Returns:
        Dictionary with modules configuration
    """
    if config_path is None:
        # Auto-detect config file
        config_path = Path(__file__).parent / "setup_modules.yaml"
    
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def create_orchestrator_from_yaml(
    config_path: Optional[Path] = None,
    profile: str = "standard"
) -> SetupOrchestrator:
    """
    Create a fully configured SetupOrchestrator from YAML config.
    
    Args:
        config_path: Path to setup_modules.yaml
        profile: Profile to use (minimal, standard, full)
    
    Returns:
        SetupOrchestrator with registered modules
    """
    logger = logging.getLogger(__name__)
    
    # Load configuration
    config = load_setup_config(config_path)
    
    # Get profile or use default
    if profile not in config.get('profiles', {}):
        logger.warning(f"Profile '{profile}' not found, using default")
        profile = config.get('default_profile', 'standard')
    
    profile_config = config['profiles'][profile]
    selected_modules = profile_config['modules']
    
    logger.info(f"Loading setup profile: {profile}")
    logger.info(f"  Description: {profile_config['description']}")
    logger.info(f"  Modules: {len(selected_modules)}")
    
    # Create orchestrator
    orchestrator = SetupOrchestrator()
    
    # Register modules
    for module_config in config['modules']:
        module_id = module_config['module_id']
        
        # Skip if not in profile
        if module_id not in selected_modules:
            logger.debug(f"Skipping module (not in profile): {module_id}")
            continue
        
        # Get module class from registry
        module_class = MODULE_REGISTRY.get(module_id)
        if not module_class:
            logger.warning(f"Module class not found for: {module_id} (skipping)")
            continue
        
        # Instantiate module
        try:
            module = module_class()
            orchestrator.register_module(module)
            logger.debug(f"✓ Registered: {module_id}")
        except Exception as e:
            logger.error(f"Failed to instantiate {module_id}: {e}")
    
    return orchestrator


# Auto-register built-in modules
def _auto_register_modules():
    """Auto-register all known module classes."""
    try:
        from .modules.python_environment_module import PythonEnvironmentModule
        register_module_class('python_environment', PythonEnvironmentModule)
    except ImportError as e:
        logger.warning(f"Could not load PythonEnvironmentModule: {e}")
    
    try:
        from .modules.vision_api_module import VisionAPIModule
        register_module_class('vision_api', VisionAPIModule)
    except ImportError as e:
        logger.warning(f"Could not load VisionAPIModule: {e}")
    
    try:
        from .modules.platform_detection_module import PlatformDetectionModule
        register_module_class('platform_detection', PlatformDetectionModule)
    except ImportError as e:
        logger.warning(f"Could not load PlatformDetectionModule: {e}")
    
    try:
        from .modules.python_dependencies_module import PythonDependenciesModule
        register_module_class('python_dependencies', PythonDependenciesModule)
    except ImportError as e:
        logger.warning(f"Could not load PythonDependenciesModule: {e}")
    
    try:
        from .modules.brain_initialization_module import BrainInitializationModule
        register_module_class('brain_initialization', BrainInitializationModule)
    except ImportError as e:
        logger.warning(f"Could not load BrainInitializationModule: {e}")
    
    try:
        from .modules.refactoring_tools_module import RefactoringToolsModule
        register_module_class('refactoring_tools', RefactoringToolsModule)
    except ImportError as e:
        logger.warning(f"Could not load RefactoringToolsModule: {e}")
    
    try:
        from .modules.smart_refactoring_recommender import SmartRefactoringRecommender
        register_module_class('smart_refactoring_recommender', SmartRefactoringRecommender)
    except ImportError as e:
        logger.warning(f"Could not load SmartRefactoringRecommender: {e}")
    
    try:
        from .modules.gitignore_setup_module import GitIgnoreSetupModule
        register_module_class('gitignore_setup', GitIgnoreSetupModule)
    except ImportError as e:
        logger.warning(f"Could not load GitIgnoreSetupModule: {e}")
    
    try:
        from .modules.onboarding_module import OnboardingModule
        register_module_class('onboarding', OnboardingModule)
    except ImportError as e:
        logger.warning(f"Could not load OnboardingModule: {e}")


# Run auto-registration on module load
_auto_register_modules()
