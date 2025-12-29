"""
Implementation Discovery

Scans codebase to discover actual implementation state.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0
"""

import logging
import yaml
import re
from pathlib import Path
from src.operations.modules.design_sync.design_sync_models import ImplementationState, SyncMetrics

logger = logging.getLogger(__name__)


class ImplementationDiscovery:
    """
    Discovers actual implementation state by scanning the codebase.
    
    Scans for:
    - Operations from cortex-operations.yaml
    - Modules in src/operations/modules/
    - Tests in tests/ directory
    - Plugins in src/plugins/
    - Agents in src/cortex_agents/
    """
    
    def discover(self, project_root: Path, metrics: SyncMetrics) -> ImplementationState:
        """
        Discover actual implementation state.
        
        Args:
            project_root: Project root directory
            metrics: Metrics collector
        
        Returns:
            ImplementationState with accurate counts
        """
        state = ImplementationState()
        
        # Discover operations from YAML
        operations_yaml = project_root / 'cortex-operations.yaml'
        if operations_yaml.exists():
            with open(operations_yaml, encoding='utf-8') as f:
                ops_data = yaml.safe_load(f)
                if 'operations' in ops_data:
                    state.operations = ops_data['operations']
        
        # Discover modules by scanning filesystem
        modules_dir = project_root / 'src' / 'operations' / 'modules'
        if modules_dir.exists():
            for py_file in modules_dir.rglob('*.py'):
                if py_file.name != '__init__.py' and py_file.name != '__pycache__':
                    module_name = py_file.stem
                    state.modules[module_name] = py_file
        
        state.total_modules = len(state.modules)
        state.implemented_modules = len(state.modules)
        state.completion_percentage = (
            100.0 if state.total_modules > 0 
            else 0.0
        )
        
        # Discover tests
        tests_dir = project_root / 'tests'
        if tests_dir.exists():
            for test_file in tests_dir.rglob('test_*.py'):
                # Count test functions in file
                test_count = 0
                try:
                    with open(test_file, encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        test_count = len(re.findall(r'^\s*def test_', content, re.MULTILINE))
                    state.tests[str(test_file.relative_to(project_root))] = test_count
                except Exception as e:
                    logger.warning(f"Could not read test file {test_file}: {e}")
        
        # Discover plugins
        plugins_dir = project_root / 'src' / 'plugins'
        if plugins_dir.exists():
            for plugin_file in plugins_dir.glob('*_plugin.py'):
                state.plugins.append(plugin_file.stem)
        
        # Discover agents
        agents_dir = project_root / 'src' / 'cortex_agents'
        if agents_dir.exists():
            for agent_file in agents_dir.glob('*_agent.py'):
                state.agents.append(agent_file.stem)
        
        metrics.implementation_discovered = True
        return state
