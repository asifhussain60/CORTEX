"""
Plugin Registry Crawler

Inventories CORTEX plugin ecosystem and capabilities.
"""

from pathlib import Path
from typing import Dict, Any, List
import importlib.util
import sys

from .base_crawler import BaseCrawler


class PluginRegistryCrawler(BaseCrawler):
    """
    Inventories CORTEX plugin system to analyze:
    - Registered plugins (active/inactive)
    - Natural language patterns
    - Command registry entries
    - Plugin health and initialization
    """
    
    def get_name(self) -> str:
        return "Plugin Registry"
    
    def crawl(self) -> Dict[str, Any]:
        """
        Inventory plugin ecosystem.
        
        Returns:
            Dict containing plugin analysis
        """
        self.log_info("Starting plugin inventory")
        
        plugin_data = {
            'total_plugins': 0,
            'active_plugins': 0,
            'inactive_plugins': 0,
            'plugin_list': [],
            'natural_language_patterns': 0,
            'commands_registered': 0,
            'initialization_success_rate': 0.0
        }
        
        # Scan plugins directory
        plugins_dir = Path(self.project_root) / 'src' / 'plugins'
        
        if not plugins_dir.exists():
            self.log_warning("Plugins directory not found")
            return {"success": True, "data": plugin_data}
        
        # Find all plugin files
        plugin_files = list(plugins_dir.glob('*_plugin.py'))
        plugin_data['total_plugins'] = len(plugin_files)
        
        self.log_info(f"Found {len(plugin_files)} plugin files")
        
        successful_loads = 0
        
        for plugin_file in plugin_files:
            try:
                plugin_info = self._analyze_plugin(plugin_file)
                plugin_data['plugin_list'].append(plugin_info)
                
                if plugin_info['status'] == 'active':
                    plugin_data['active_plugins'] += 1
                    successful_loads += 1
                else:
                    plugin_data['inactive_plugins'] += 1
                
                plugin_data['natural_language_patterns'] += plugin_info.get('patterns', 0)
                plugin_data['commands_registered'] += plugin_info.get('commands', 0)
                
            except Exception as e:
                self.log_warning(f"Could not analyze {plugin_file.name}: {e}")
                plugin_data['plugin_list'].append({
                    'name': plugin_file.stem,
                    'status': 'error',
                    'error': str(e)
                })
        
        # Calculate success rate
        if plugin_data['total_plugins'] > 0:
            plugin_data['initialization_success_rate'] = (
                successful_loads / plugin_data['total_plugins'] * 100
            )
        
        self.log_info(
            f"Plugin inventory complete: {plugin_data['active_plugins']} active, "
            f"{plugin_data['inactive_plugins']} inactive"
        )
        
        return {
            "success": True,
            "data": plugin_data
        }
    
    def _analyze_plugin(self, plugin_file: Path) -> Dict[str, Any]:
        """
        Analyze a single plugin file.
        
        Args:
            plugin_file: Path to plugin file
            
        Returns:
            Dict with plugin information
        """
        plugin_info = {
            'name': self._format_plugin_name(plugin_file.stem),
            'filename': plugin_file.name,
            'status': 'unknown',
            'patterns': 0,
            'commands': 0,
            'has_metadata': False
        }
        
        try:
            # Read file content to check for key indicators
            with open(plugin_file, 'r') as f:
                content = f.read()
            
            # Check for BasePlugin inheritance
            if 'BasePlugin' in content:
                plugin_info['status'] = 'active'
            
            # Count natural language patterns
            if 'get_natural_language_patterns' in content:
                # Rough count - look for return statement with list
                pattern_lines = [line for line in content.split('\n') 
                               if 'return [' in line or '"' in line]
                plugin_info['patterns'] = len([l for l in pattern_lines if '"' in l])
            
            # Count commands
            if 'register_commands' in content or '@command' in content:
                command_lines = [line for line in content.split('\n') 
                               if 'command=' in line or '@command' in line]
                plugin_info['commands'] = len(command_lines)
            
            # Check for metadata
            if 'PluginMetadata' in content or '_get_metadata' in content:
                plugin_info['has_metadata'] = True
            
        except Exception as e:
            self.log_warning(f"Could not read {plugin_file.name}: {e}")
            plugin_info['status'] = 'error'
        
        return plugin_info
    
    def _format_plugin_name(self, stem: str) -> str:
        """
        Format plugin filename to human-readable name.
        
        Args:
            stem: Plugin filename without extension
            
        Returns:
            Formatted name
        """
        # Remove '_plugin' suffix
        name = stem.replace('_plugin', '')
        
        # Convert snake_case to Title Case
        name = name.replace('_', ' ').title()
        
        return name
