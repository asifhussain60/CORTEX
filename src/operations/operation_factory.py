"""
Operation Factory - Load and Create Operations from YAML

This factory loads operation definitions from cortex-op                    # Convert snake_case to CamelCase, but preserve common acronyms
                    words = module_name.split('_')
                    # Preserve common acronyms in uppercase
                    acronyms = {'api': 'API', 'sql': 'SQL', 'sqlite': 'SQLite', 'html': 'HTML', 'css': 'CSS', 'json': 'JSON', 'yaml': 'YAML', 'mkdocs': 'MkDocs', 'pdf': 'PDF', 'cli': 'CLI'}
                    class_name = ''.join(
                        acronyms.get(word.lower(), word.capitalize()) 
                        for word in words
                    ).yaml and
instantiates orchestrators with the appropriate modules.

Author: Asif Hussain
Version: 2.0 (Universal Operations Architecture)
"""

import logging
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from src.operations.base_operation_module import BaseOperationModule
from src.operations.operations_orchestrator import OperationsOrchestrator

logger = logging.getLogger(__name__)


class OperationFactory:
    """
    Factory for creating operation orchestrators from YAML configuration.
    
    Loads cortex-operations.yaml and provides methods to:
        - Discover available operations
        - Load operation definitions
        - Instantiate module classes
        - Create orchestrators ready for execution
    
    Example Usage:
        factory = OperationFactory()
        
        # Get available operations
        ops = factory.get_available_operations()
        # ['environment_setup', 'refresh_cortex_story', 'workspace_cleanup', ...]
        
        # Create orchestrator for an operation
        orchestrator = factory.create_operation('refresh_cortex_story')
        report = orchestrator.execute_operation(context={'project_root': Path('...')})
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize operation factory.
        
        Args:
            config_path: Path to cortex-operations.yaml (auto-detected if None)
        """
        self.config_path = config_path or self._find_config_path()
        self.config: Dict[str, Any] = {}
        self.module_classes: Dict[str, type] = {}
        
        # Load configuration
        self._load_config()
        
        # Auto-register module classes
        self._auto_register_modules()
    
    def _find_config_path(self) -> Path:
        """Find cortex-operations.yaml in project root."""
        # Try current directory
        current = Path.cwd()
        config_file = current / "cortex-operations.yaml"
        if config_file.exists():
            return config_file
        
        # Try parent directories
        for parent in current.parents:
            config_file = parent / "cortex-operations.yaml"
            if config_file.exists():
                return config_file
        
        # Default to project root
        return Path(__file__).parent.parent.parent / "cortex-operations.yaml"
    
    def _load_config(self) -> None:
        """Load operations configuration from YAML."""
        try:
            logger.info(f"Loading operations config from: {self.config_path}")
            
            if not self.config_path.exists():
                logger.error(f"Config file not found: {self.config_path}")
                self.config = {'operations': {}, 'modules': {}}
                return
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            
            logger.info(f"Loaded {len(self.config.get('operations', {}))} operations")
            logger.info(f"Loaded {len(self.config.get('modules', {}))} module definitions")
        
        except Exception as e:
            logger.error(f"Failed to load config: {e}", exc_info=True)
            self.config = {'operations': {}, 'modules': {}}
    
    def _auto_register_modules(self) -> None:
        """
        Auto-register module classes from src/operations/modules/.
        
        Discovers Python module files and registers their classes.
        """
        try:
            modules_dir = Path(__file__).parent / "modules"
            if not modules_dir.exists():
                logger.warning(f"Modules directory not found: {modules_dir}")
                return
            
            # Find all module files
            module_files = list(modules_dir.glob("*_module.py"))
            logger.info(f"Found {len(module_files)} module files")
            
            # Import and register each module
            for module_file in module_files:
                try:
                    module_name = module_file.stem
                    
                    # Convert snake_case to CamelCase, but preserve common acronyms
                    words = module_name.split('_')
                    # Preserve common acronyms in uppercase
                    acronyms = {'api': 'API', 'sql': 'SQL', 'sqlite': 'SQLite', 'html': 'HTML', 'css': 'CSS', 'json': 'JSON', 'yaml': 'YAML', 'mkdocs': 'MkDocs'}
                    class_name = ''.join(
                        acronyms.get(word.lower(), word.capitalize()) 
                        for word in words
                    )
                    
                    # Dynamic import
                    import importlib
                    module = importlib.import_module(f"src.operations.modules.{module_name}")
                    
                    # Get class
                    if hasattr(module, class_name):
                        module_class = getattr(module, class_name)
                        
                        # Register by module_id (extract from class or use file name)
                        try:
                            instance = module_class()
                            module_id = instance.metadata.module_id
                            self.module_classes[module_id] = module_class
                            logger.debug(f"Registered module: {module_id} → {class_name}")
                        except Exception as e:
                            logger.warning(f"Could not instantiate {class_name}: {e}")
                    else:
                        logger.warning(f"Class {class_name} not found in {module_name}")
                
                except Exception as e:
                    logger.warning(f"Failed to register module {module_file.name}: {e}")
            
            logger.info(f"Registered {len(self.module_classes)} module classes")
        
        except Exception as e:
            logger.error(f"Module auto-registration failed: {e}", exc_info=True)
    
    def get_available_operations(self) -> List[str]:
        """
        Get list of available operation IDs.
        
        Returns:
            List of operation IDs (e.g., ['environment_setup', 'refresh_cortex_story'])
        """
        return list(self.config.get('operations', {}).keys())
    
    def get_operation_info(self, operation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about an operation.
        
        Args:
            operation_id: Operation identifier
        
        Returns:
            Operation configuration dict, or None if not found
        """
        return self.config.get('operations', {}).get(operation_id)
    
    def create_operation(
        self,
        operation_id: str,
        profile: str = 'standard',
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[OperationsOrchestrator]:
        """
        Create orchestrator for an operation.
        
        Args:
            operation_id: Operation identifier (e.g., 'refresh_cortex_story')
            profile: Profile to use (minimal/standard/full)
            context: Initial context dictionary
        
        Returns:
            Configured orchestrator, or None if operation not found
        
        Example:
            orchestrator = factory.create_operation('refresh_cortex_story')
            if orchestrator:
                report = orchestrator.execute_operation(context={'project_root': Path('.')})
        """
        try:
            # Get operation config
            op_config = self.get_operation_info(operation_id)
            if not op_config:
                logger.error(f"Operation not found: {operation_id}")
                return None
            
            # Determine module list (profile-specific or default)
            module_ids = self._get_module_list(op_config, profile)
            
            # Instantiate modules
            modules = []
            for module_id in module_ids:
                module = self._create_module(module_id)
                if module:
                    modules.append(module)
                else:
                    logger.warning(f"Module {module_id} not available, skipping")
            
            if not modules:
                logger.error(f"No modules available for operation: {operation_id}")
                return None
            
            # Create orchestrator
            orchestrator = OperationsOrchestrator(
                operation_id=operation_id,
                operation_name=op_config.get('name', operation_id),
                modules=modules,
                context=context or {}
            )
            
            logger.info(f"Created orchestrator for {operation_id} with {len(modules)} modules")
            return orchestrator
        
        except Exception as e:
            logger.error(f"Failed to create operation {operation_id}: {e}", exc_info=True)
            return None
    
    def _get_module_list(self, op_config: Dict[str, Any], profile: str) -> List[str]:
        """
        Get module list for operation and profile.
        
        Args:
            op_config: Operation configuration
            profile: Profile name (must be string)
        
        Returns:
            List of module IDs to execute
        """
        # Validate profile is a string (defensive programming)
        if not isinstance(profile, str):
            logger.warning(f"Profile must be string, got {type(profile).__name__}. Using 'standard'.")
            profile = 'standard'
        
        # Check if operation has profile-specific modules
        profiles = op_config.get('profiles', {})
        if profile in profiles:
            return profiles[profile].get('modules', [])
        
        # Fall back to default module list
        return op_config.get('modules', [])
    
    def _create_module(self, module_id: str) -> Optional[BaseOperationModule]:
        """
        Create module instance by ID.
        
        Args:
            module_id: Module identifier
        
        Returns:
            Module instance, or None if not available
        """
        try:
            # Check if class is registered
            if module_id not in self.module_classes:
                logger.warning(f"Module class not registered: {module_id}")
                return None
            
            # Instantiate module
            module_class = self.module_classes[module_id]
            module = module_class()
            
            return module
        
        except Exception as e:
            logger.error(f"Failed to create module {module_id}: {e}", exc_info=True)
            return None
    
    def list_operation_modules(self, operation_id: str, profile: str = 'standard') -> List[str]:
        """
        List modules for an operation without creating orchestrator.
        
        Args:
            operation_id: Operation identifier
            profile: Profile name
        
        Returns:
            List of module IDs
        """
        op_config = self.get_operation_info(operation_id)
        if not op_config:
            return []
        
        return self._get_module_list(op_config, profile)
    
    def get_natural_language_mappings(self) -> Dict[str, str]:
        """
        Get natural language → operation ID mappings.
        
        Returns:
            Dict mapping natural language phrases to operation IDs
        
        Example:
            {'refresh story': 'refresh_cortex_story',
             'cleanup': 'workspace_cleanup'}
        """
        mappings = {}
        
        for op_id, op_config in self.config.get('operations', {}).items():
            # Add natural language phrases
            for phrase in op_config.get('natural_language', []):
                mappings[phrase.lower()] = op_id
            
            # Add slash command
            slash_cmd = op_config.get('slash_command', '')
            if slash_cmd:
                mappings[slash_cmd.lower()] = op_id
        
        return mappings
    
    def find_operation_by_input(self, user_input: str) -> Optional[str]:
        """
        Find operation ID by user input (natural language or slash command).
        
        Args:
            user_input: User's input text
        
        Returns:
            Operation ID if found, None otherwise
        
        Example:
            factory.find_operation_by_input("refresh story") → 'refresh_cortex_story'
            factory.find_operation_by_input("/CORTEX, cleanup") → 'workspace_cleanup'
        """
        user_input_lower = user_input.lower().strip()
        mappings = self.get_natural_language_mappings()
        
        # Direct match
        if user_input_lower in mappings:
            return mappings[user_input_lower]
        
        # Fuzzy match (contains)
        for phrase, op_id in mappings.items():
            if phrase in user_input_lower or user_input_lower in phrase:
                return op_id
        
        return None
