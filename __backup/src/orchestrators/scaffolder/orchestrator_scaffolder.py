"""
Orchestrator Scaffolder - AC-SCAFFOLD-001.

CLI tool for creating new orchestrators with templates.
Enables team extensibility while maintaining governance enforcement.

Features:
- Template-based scaffolding
- Configuration generation
- Governance integration
- Module structure creation
- Test file generation

Author: GitHub Copilot
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
import json
from datetime import datetime, timezone


class OrchestratorScaffolder:
    """
    CLI scaffolder for creating new orchestrators.
    
    Enables domain teams to build orchestrators using CORTEX governance.
    
    Usage:
        scaffolder = OrchestratorScaffolder(
            workspace_root=Path.cwd(),
            templates_dir=Path.cwd() / "templates" / "orchestrator"
        )
        
        result = scaffolder.create_orchestrator({
            'name': 'APIOrchestrator',
            'domain': 'api_management',
            'description': 'Manage API requests and responses'
        })
    """
    
    def __init__(
        self,
        workspace_root: Path,
        templates_dir: Path
    ):
        """
        Initialize orchestrator scaffolder.
        
        Args:
            workspace_root: Root directory of workspace
            templates_dir: Directory containing scaffolder templates
        """
        self.workspace_root = workspace_root
        self.templates_dir = templates_dir
        self.logger = logging.getLogger("cortex.orchestrators.scaffolder")
        
        self.logger.info(
            f"OrchestratorScaffolder initialized (workspace={workspace_root}, "
            f"templates={templates_dir})"
        )
    
    def create_orchestrator(
        self,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create new orchestrator from config.
        
        Args:
            config: Orchestrator configuration with:
                - name: Orchestrator class name (e.g., 'APIOrchestrator')
                - domain: Domain identifier (e.g., 'api_management')
                - description: Human-readable description
                - output_dir: (optional) Output directory for files
                - template: (optional) Template variant ('basic', 'advanced')
                - include_governance: (optional) Include governance integration
                - generate_tests: (optional) Generate test files
        
        Returns:
            Dict with:
                - success: bool
                - orchestrator_name: str
                - files_created: List[str]
                - config_file: str
                - metadata: Dict
        """
        self.logger.info(f"Creating orchestrator: {config.get('name')} (domain={config.get('domain')})")
        
        # Validate config
        validation = self._validate_config(config)
        if not validation.get('valid'):
            self.logger.error(f"Invalid config: {validation.get('errors')}")
            return {
                'success': False,
                'errors': validation.get('errors', [])
            }
        
        # Normalize config
        normalized_config = self._normalize_config(config)
        
        # Create orchestrator files
        output_dir = Path(config.get('output_dir', self.workspace_root / 'src' / 'orchestrators' / 'custom'))
        output_dir.mkdir(parents=True, exist_ok=True)
        
        files_created = []
        
        # Generate main orchestrator file
        orchestrator_file = self._generate_orchestrator_file(normalized_config, output_dir)
        if orchestrator_file:
            files_created.append(str(orchestrator_file))
        
        # Generate test file if requested
        if config.get('generate_tests', True):
            test_file = self._generate_test_file(normalized_config, output_dir)
            if test_file:
                files_created.append(str(test_file))
        
        # Generate config file
        config_file = self._generate_config_file(normalized_config, output_dir)
        if config_file:
            files_created.append(str(config_file))
        
        # Generate __init__.py if needed
        init_file = output_dir / '__init__.py'
        if not init_file.exists():
            init_file.touch()
            files_created.append(str(init_file))
        
        result = {
            'success': True,
            'orchestrator_name': normalized_config['class_name'],
            'domain': normalized_config['domain'],
            'files_created': files_created,
            'config_file': str(config_file) if config_file else None,
            'metadata': {
                'created_at': datetime.now(timezone.utc).isoformat(),
                'template': config.get('template', 'basic'),
                'governance_integrated': config.get('include_governance', True),
                'tests_generated': config.get('generate_tests', True),
                'file_count': len(files_created)
            }
        }
        
        self.logger.info(
            f"Orchestrator created successfully: {normalized_config['class_name']} "
            f"({len(files_created)} files)"
        )
        
        return result
    
    def _validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate orchestrator configuration.
        
        Args:
            config: Configuration to validate
        
        Returns:
            Dict with 'valid' bool and 'errors' list
        """
        errors = []
        
        # Required fields
        if not config.get('name'):
            errors.append("Missing required field: 'name'")
        
        if not config.get('domain'):
            errors.append("Missing required field: 'domain'")
        
        # Name validation
        name = config.get('name', '')
        if not name.replace('_', '').replace('-', '').isalnum():
            errors.append(f"Invalid name: '{name}' contains invalid characters")
        
        # Domain validation
        domain = config.get('domain', '')
        if not domain.replace('_', '').isalnum():
            errors.append(f"Invalid domain: '{domain}' contains invalid characters")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def _normalize_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize configuration for code generation.
        
        Converts snake_case to PascalCase for class names, etc.
        
        Args:
            config: Configuration to normalize
        
        Returns:
            Normalized configuration dict
        """
        name = config.get('name', '')
        domain = config.get('domain', '')
        
        # Convert to class name if not already
        class_name = name if name[0].isupper() else self._snake_to_pascal(name)
        
        return {
            'name': name,
            'class_name': class_name,
            'domain': domain,
            'description': config.get('description', f'{class_name} for {domain} domain'),
            'template': config.get('template', 'basic'),
            'include_governance': config.get('include_governance', True),
            'generate_tests': config.get('generate_tests', True),
            'author': config.get('author', 'CORTEX Team'),
            'version': config.get('version', '1.0.0'),
            'features': config.get('features', [])
        }
    
    def _generate_orchestrator_file(
        self,
        config: Dict[str, Any],
        output_dir: Path
    ) -> Optional[Path]:
        """
        Generate main orchestrator Python file.
        
        Args:
            config: Normalized configuration
            output_dir: Output directory
        
        Returns:
            Path to generated file or None
        """
        class_name = config['class_name']
        module_name = self._pascal_to_snake(class_name)
        output_file = output_dir / f'{module_name}.py'
        
        # Generate content
        content = self._get_orchestrator_template(config)
        
        # Write file
        try:
            output_file.write_text(content)
            self.logger.debug(f"Generated orchestrator file: {output_file}")
            return output_file
        except Exception as e:
            self.logger.error(f"Failed to generate orchestrator file: {e}")
            return None
    
    def _generate_test_file(
        self,
        config: Dict[str, Any],
        output_dir: Path
    ) -> Optional[Path]:
        """
        Generate test file for orchestrator.
        
        Args:
            config: Normalized configuration
            output_dir: Output directory
        
        Returns:
            Path to generated file or None
        """
        class_name = config['class_name']
        module_name = self._pascal_to_snake(class_name)
        test_file = Path(self.workspace_root) / 'tests' / 'unit' / f'test_{module_name}.py'
        
        # Generate content
        content = self._get_test_template(config)
        
        # Write file
        try:
            test_file.parent.mkdir(parents=True, exist_ok=True)
            test_file.write_text(content)
            self.logger.debug(f"Generated test file: {test_file}")
            return test_file
        except Exception as e:
            self.logger.error(f"Failed to generate test file: {e}")
            return None
    
    def _generate_config_file(
        self,
        config: Dict[str, Any],
        output_dir: Path
    ) -> Optional[Path]:
        """
        Generate configuration file for orchestrator.
        
        Args:
            config: Normalized configuration
            output_dir: Output directory
        
        Returns:
            Path to generated file or None
        """
        class_name = config['class_name']
        module_name = self._pascal_to_snake(class_name)
        config_file = output_dir / f'{module_name}_config.json'
        
        config_content = {
            'orchestrator': class_name,
            'domain': config['domain'],
            'description': config['description'],
            'version': config['version'],
            'author': config['author'],
            'metadata': {
                'created_at': datetime.now(timezone.utc).isoformat(),
                'governance_integrated': config['include_governance'],
                'template': config['template'],
                'features': config['features']
            }
        }
        
        # Write file
        try:
            config_file.write_text(json.dumps(config_content, indent=2))
            self.logger.debug(f"Generated config file: {config_file}")
            return config_file
        except Exception as e:
            self.logger.error(f"Failed to generate config file: {e}")
            return None
    
    def _get_orchestrator_template(self, config: Dict[str, Any]) -> str:
        """Get orchestrator Python template."""
        class_name = config['class_name']
        domain = config['domain']
        description = config['description']
        
        governance_import = ""
        governance_init = ""
        if config['include_governance']:
            governance_import = "from src.orchestrators.core.governance_merger import GovernanceMerger\n"
            governance_init = "        self.governance_merger = GovernanceMerger()\n"
        
        return f'''"""
{class_name} - {domain.title()} Domain Orchestrator.

{description}

Author: {config['author']}
Version: {config['version']}
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path

{governance_import}from src.orchestrators.base_orchestrator import BaseOrchestrator


class {class_name}(BaseOrchestrator):
    """
    {description}
    
    Domain: {domain}
    """
    
    def __init__(self):
        """Initialize {class_name}."""
        super().__init__()
        self.logger = logging.getLogger("cortex.orchestrators.{domain}")
        self.domain = "{domain}"
{governance_init}
        self.logger.info(f"{{self.__class__.__name__}} initialized for domain={{self.domain}}")
    
    def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute orchestrator logic.
        
        Args:
            request: Execution request
        
        Returns:
            Execution result
        """
        self.logger.info(f"Executing request: {{request.get('intent')}}")
        
        # TODO: Implement domain-specific logic
        
        return {{
            'success': True,
            'orchestrator': self.__class__.__name__,
            'domain': self.domain,
            'message': 'Orchestrator executed successfully'
        }}
'''
    
    def _get_test_template(self, config: Dict[str, Any]) -> str:
        """Get test template."""
        class_name = config['class_name']
        module_name = self._pascal_to_snake(class_name)
        domain = config['domain']
        
        return f'''"""
Tests for {class_name}.

Author: Test Suite
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
from src.orchestrators.{module_name} import {class_name}


class Test{class_name}:
    """Test {class_name} orchestrator."""
    
    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance."""
        return {class_name}()
    
    def test_initialization(self, orchestrator):
        """Orchestrator should initialize."""
        assert orchestrator is not None
        assert orchestrator.domain == "{domain}"
    
    def test_execute_basic(self, orchestrator):
        """Orchestrator should execute basic request."""
        request = {{'intent': 'test'}}
        result = orchestrator.execute(request)
        
        assert result is not None
        assert result.get('success') is not None
        assert result.get('orchestrator') == "{class_name}"
'''
    
    def _generate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate configuration dict."""
        return self._normalize_config(config)
    
    @staticmethod
    def _snake_to_pascal(name: str) -> str:
        """Convert snake_case to PascalCase."""
        parts = name.split('_')
        return ''.join(p.capitalize() for p in parts if p)
    
    @staticmethod
    def _pascal_to_snake(name: str) -> str:
        """Convert PascalCase to snake_case."""
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
