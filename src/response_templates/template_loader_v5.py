"""
YAML Include Loader for Modular Templates
Supports !include directive for composing templates from component files
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import re


class IncludeLoader(yaml.SafeLoader):
    """Custom YAML loader supporting !include directive for file composition"""
    
    def __init__(self, stream):
        self._root = Path(stream.name).parent if hasattr(stream, 'name') else Path.cwd()
        super().__init__(stream)


def include_constructor(loader: IncludeLoader, node: yaml.Node) -> Any:
    """
    Construct a Python object from !include directive
    
    Syntax:
        !include path/to/file.yaml           # Load entire file
        !include path/to/file.yaml#key       # Load specific key from file
    
    Examples:
        cortex_header: !include blocks/headers.yaml#cortex_header
        progress_bar: !include core/progress-bar-config.yaml
    """
    value = loader.construct_scalar(node)
    
    # Parse path#key syntax
    if '#' in value:
        file_path, key_path = value.split('#', 1)
    else:
        file_path, key_path = value, None
    
    # Resolve relative to current file
    include_path = loader._root / file_path
    
    if not include_path.exists():
        raise FileNotFoundError(f"Include file not found: {include_path}")
    
    # Load included file
    with open(include_path, 'r') as f:
        data = yaml.load(f, Loader=IncludeLoader)
    
    # Extract specific key if specified
    if key_path:
        keys = key_path.split('.')
        for key in keys:
            data = data[key]
    
    return data


# Register !include constructor
yaml.add_constructor('!include', include_constructor, IncludeLoader)


class ModularTemplateLoader:
    """
    Enhanced template loader supporting modular component architecture
    Handles !include directives and caching for performance
    """
    
    def __init__(self, base_path: Path):
        self.base_path = Path(base_path)
        self.cache: Dict[str, Any] = {}
        self._cache_enabled = True
    
    def load_template(self, file_path: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        Load template file with !include support
        
        Args:
            file_path: Relative path from base_path
            use_cache: Whether to use cached version
        
        Returns:
            Parsed template dictionary
        """
        full_path = self.base_path / file_path
        
        # Check cache
        cache_key = str(full_path)
        if use_cache and self._cache_enabled and cache_key in self.cache:
            return self.cache[cache_key]
        
        # Load file
        with open(full_path, 'r') as f:
            data = yaml.load(f, Loader=IncludeLoader)
        
        # Cache result
        if self._cache_enabled:
            self.cache[cache_key] = data
        
        return data
    
    def load_core_component(self, component_name: str) -> Dict[str, Any]:
        """Load core component by name"""
        return self.load_template(f"core/{component_name}.yaml")
    
    def load_block(self, block_name: str) -> Dict[str, Any]:
        """Load standard block by name"""
        return self.load_template(f"blocks/{block_name}.yaml")
    
    def load_orchestrator_block(self, orchestrator: str, block_name: str) -> Dict[str, Any]:
        """Load orchestrator-specific block"""
        return self.load_template(f"orchestrators/{orchestrator}/{block_name}.yaml")
    
    def load_named_template(self, template_name: str) -> Dict[str, Any]:
        """Load named template"""
        return self.load_template(f"templates/{template_name}.yaml")
    
    def clear_cache(self):
        """Clear template cache"""
        self.cache.clear()
    
    def disable_cache(self):
        """Disable caching (useful for development)"""
        self._cache_enabled = False
        self.clear_cache()
    
    def enable_cache(self):
        """Enable caching (default behavior)"""
        self._cache_enabled = True
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        return {
            'cached_files': len(self.cache),
            'cache_enabled': self._cache_enabled
        }


def load_template_with_includes(file_path: Path) -> Dict[str, Any]:
    """
    Convenience function to load a template file with !include support
    
    Args:
        file_path: Path to template file
    
    Returns:
        Parsed template dictionary
    """
    with open(file_path, 'r') as f:
        return yaml.load(f, Loader=IncludeLoader)
