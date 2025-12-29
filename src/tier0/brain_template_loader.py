"""
Brain Template Loader - Option 1: Symlink-Based Sharing
=======================================================

**Purpose:** Load CORTEX brain templates from centralized location with fallback
**Author:** Asif Hussain
**Date:** December 21, 2025
**Phase:** CORTEX 4.0 Phase 5 - Brain Architecture Options

**Architecture:**
- Primary: ~/.cortex/brain-templates/ (centralized)
- Fallback: cortex-brain/ (per-repo, backwards compatible)
- Zero Tier 0 violations (fully compliant)

**Template Files:**
- capabilities.yaml
- response-templates-v4.yaml
- brain-protection-rules.yaml
- cortex.config.template.json

**Usage:**
    from src.tier0.brain_template_loader import BrainTemplateLoader
    
    loader = BrainTemplateLoader()
    capabilities = loader.load_capabilities()
    templates = loader.load_response_templates()
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any
import yaml
import json


logger = logging.getLogger(__name__)


class BrainTemplateLoader:
    """Load brain templates from centralized location with fallback."""
    
    # Centralized template location (Option 1)
    CENTRAL_TEMPLATES_DIR = Path.home() / ".cortex" / "brain-templates"
    
    # Template filenames
    CAPABILITIES_FILE = "capabilities.yaml"
    RESPONSE_TEMPLATES_FILE = "response-templates-v4.yaml"
    BRAIN_PROTECTION_FILE = "brain-protection-rules.yaml"
    CONFIG_TEMPLATE_FILE = "cortex.config.template.json"
    
    def __init__(self, fallback_dir: Optional[Path] = None):
        """
        Initialize template loader.
        
        Args:
            fallback_dir: Fallback directory for templates (default: CORTEX/cortex-brain/)
        """
        self.central_dir = self.CENTRAL_TEMPLATES_DIR
        self.fallback_dir = fallback_dir or self._get_default_fallback()
        
        logger.info(f"🧠 BrainTemplateLoader initialized")
        logger.info(f"   Central: {self.central_dir}")
        logger.info(f"   Fallback: {self.fallback_dir}")
    
    def _get_default_fallback(self) -> Path:
        """Get default fallback directory (CORTEX repo)."""
        # Assume this file is in src/tier0/
        repo_root = Path(__file__).parent.parent.parent
        return repo_root / "cortex-brain"
    
    def _resolve_template_path(self, filename: str) -> Path:
        """
        Resolve template file path with central → fallback priority.
        
        Args:
            filename: Template filename to resolve
            
        Returns:
            Path to template file
            
        Raises:
            FileNotFoundError: If template not found in either location
        """
        # Try central location first
        central_path = self.central_dir / filename
        if central_path.exists():
            logger.debug(f"✅ Template found (central): {filename}")
            return central_path
        
        # Fallback to per-repo location
        fallback_path = self.fallback_dir / filename
        if fallback_path.exists():
            logger.debug(f"✅ Template found (fallback): {filename}")
            return fallback_path
        
        # Check metadata subdirectory for capabilities
        if filename == self.CAPABILITIES_FILE:
            metadata_path = self.fallback_dir / "metadata" / filename
            if metadata_path.exists():
                logger.debug(f"✅ Template found (metadata): {filename}")
                return metadata_path
        
        # Check core subdirectory for brain protection
        if filename == self.BRAIN_PROTECTION_FILE:
            core_path = self.fallback_dir / "core" / filename
            if core_path.exists():
                logger.debug(f"✅ Template found (core): {filename}")
                return core_path
        
        raise FileNotFoundError(
            f"Template not found: {filename}\n"
            f"  Checked: {central_path}\n"
            f"  Checked: {fallback_path}"
        )
    
    def load_yaml(self, filename: str) -> Dict[str, Any]:
        """
        Load YAML template file.
        
        Args:
            filename: YAML file to load
            
        Returns:
            Parsed YAML content as dict
        """
        path = self._resolve_template_path(filename)
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            logger.info(f"📄 Loaded YAML: {filename} ({path})")
            return data or {}
        except Exception as e:
            logger.error(f"❌ Failed to load {filename}: {e}")
            raise
    
    def load_json(self, filename: str) -> Dict[str, Any]:
        """
        Load JSON template file.
        
        Args:
            filename: JSON file to load
            
        Returns:
            Parsed JSON content as dict
        """
        path = self._resolve_template_path(filename)
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"📄 Loaded JSON: {filename} ({path})")
            return data or {}
        except Exception as e:
            logger.error(f"❌ Failed to load {filename}: {e}")
            raise
    
    def load_capabilities(self) -> Dict[str, Any]:
        """Load capabilities.yaml template."""
        return self.load_yaml(self.CAPABILITIES_FILE)
    
    def load_response_templates(self) -> Dict[str, Any]:
        """Load response-templates-v4.yaml template."""
        return self.load_yaml(self.RESPONSE_TEMPLATES_FILE)
    
    def load_brain_protection_rules(self) -> Dict[str, Any]:
        """Load brain-protection-rules.yaml template."""
        return self.load_yaml(self.BRAIN_PROTECTION_FILE)
    
    def load_config_template(self) -> Dict[str, Any]:
        """Load cortex.config.template.json template."""
        return self.load_json(self.CONFIG_TEMPLATE_FILE)
    
    def is_central_location_available(self) -> bool:
        """Check if centralized template location exists."""
        return self.central_dir.exists()
    
    def get_template_source(self, filename: str) -> str:
        """
        Get source location of template (central or fallback).
        
        Returns:
            "central" or "fallback"
        """
        try:
            path = self._resolve_template_path(filename)
            if self.central_dir in path.parents or path.parent == self.central_dir:
                return "central"
            return "fallback"
        except FileNotFoundError:
            return "not_found"


# Singleton instance for global access
_loader_instance: Optional[BrainTemplateLoader] = None


def get_loader(fallback_dir: Optional[Path] = None) -> BrainTemplateLoader:
    """
    Get singleton template loader instance.
    
    Args:
        fallback_dir: Override fallback directory (optional)
        
    Returns:
        BrainTemplateLoader instance
    """
    global _loader_instance
    if _loader_instance is None or fallback_dir is not None:
        _loader_instance = BrainTemplateLoader(fallback_dir)
    return _loader_instance


# Convenience functions for quick access
def load_capabilities(fallback_dir: Optional[Path] = None) -> Dict[str, Any]:
    """Load capabilities.yaml from central or fallback location."""
    return get_loader(fallback_dir).load_capabilities()


def load_response_templates(fallback_dir: Optional[Path] = None) -> Dict[str, Any]:
    """Load response-templates-v4.yaml from central or fallback location."""
    return get_loader(fallback_dir).load_response_templates()


def load_brain_protection_rules(fallback_dir: Optional[Path] = None) -> Dict[str, Any]:
    """Load brain-protection-rules.yaml from central or fallback location."""
    return get_loader(fallback_dir).load_brain_protection_rules()


def load_config_template(fallback_dir: Optional[Path] = None) -> Dict[str, Any]:
    """Load cortex.config.template.json from central or fallback location."""
    return get_loader(fallback_dir).load_config_template()


if __name__ == "__main__":
    # Demo usage
    logging.basicConfig(level=logging.INFO)
    
    loader = BrainTemplateLoader()
    
    print("\n=== Template Source Locations ===")
    for filename in [
        BrainTemplateLoader.CAPABILITIES_FILE,
        BrainTemplateLoader.RESPONSE_TEMPLATES_FILE,
        BrainTemplateLoader.BRAIN_PROTECTION_FILE,
        BrainTemplateLoader.CONFIG_TEMPLATE_FILE
    ]:
        source = loader.get_template_source(filename)
        print(f"{filename:40s} → {source}")
    
    print("\n=== Loading Templates ===")
    try:
        caps = loader.load_capabilities()
        print(f"✅ Capabilities: {len(caps)} keys")
        
        templates = loader.load_response_templates()
        print(f"✅ Response Templates: {len(templates)} keys")
        
        rules = loader.load_brain_protection_rules()
        print(f"✅ Brain Protection Rules: {len(rules)} keys")
        
        config = loader.load_config_template()
        print(f"✅ Config Template: {len(config)} keys")
        
    except Exception as e:
        print(f"❌ Error: {e}")
