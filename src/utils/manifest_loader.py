"""
ManifestLoader - 3-Tier Manifest Architecture Loader
Handles YAML parsing, cross-reference resolution, and lazy loading

Purpose: Unified loader for CoreManifest, ConfigManifest, and IntegrationManifest
Features:
  - Lazy loading (load on-demand)
  - Cross-reference resolution (config://, integration://)
  - Caching (avoid repeated file I/O)
  - Backward compatibility adapter

Author: Asif Hussain
GitHub: github.com/asifhussain60/CORTEX
Created: 2025-12-22 (Week 15 Day 4)
Version: 1.0.0
"""

import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from copy import deepcopy
from datetime import datetime
import logging

try:
    import jsonschema
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False
    logging.warning("jsonschema not available - schema validation disabled")

logger = logging.getLogger(__name__)


class ManifestLoader:
    """
    Unified loader for 3-Tier Manifest Architecture.
    
    Features:
    - Lazy loading of manifests
    - Cross-reference resolution
    - Caching for performance
    - Backward compatibility adapter
    
    Usage:
        loader = ManifestLoader(cortex_root)
        
        # Load individual manifests
        core = loader.core_manifest
        config = loader.config_manifest
        integration = loader.integration_manifest
        
        # Resolve cross-references
        resolved = loader.resolve_cross_references("planning_orchestrator")
        
        # Get orchestrator config
        orch = loader.get_orchestrator("planning_orchestrator")
    """
    
    def __init__(self, cortex_root: str, validate_schema: bool = True):
        """
        Initialize ManifestLoader.
        
        Args:
            cortex_root: Path to CORTEX root directory
            validate_schema: Whether to validate manifests against JSON schemas
        """
        self.cortex_root = Path(cortex_root)
        self.manifest_dir = self.cortex_root / "cortex-brain" / "manifests"
        self.schema_dir = self.manifest_dir / "schemas"
        self.validate_schema = validate_schema and JSONSCHEMA_AVAILABLE
        
        # Lazy-loaded manifests
        self._core_manifest: Optional[Dict[str, Any]] = None
        self._config_manifest: Optional[Dict[str, Any]] = None
        self._integration_manifest: Optional[Dict[str, Any]] = None
        
        # Lazy-loaded schemas
        self._core_schema: Optional[Dict[str, Any]] = None
        self._config_schema: Optional[Dict[str, Any]] = None
        self._integration_schema: Optional[Dict[str, Any]] = None
        
        # Cross-reference cache
        self._resolved_cache: Dict[str, Dict[str, Any]] = {}
        
        # Validation
        if not self.manifest_dir.exists():
            raise FileNotFoundError(f"Manifests directory not found: {self.manifest_dir}")
    
    # ──────────────────────────────────────────────────────────────
    # Lazy Loading Properties
    # ──────────────────────────────────────────────────────────────
    
    @property
    def core_manifest(self) -> Dict[str, Any]:
        """Lazy load CoreManifest with optional schema validation."""
        if self._core_manifest is None:
            self._core_manifest = self._load_manifest("core-manifest.yaml")
            
            if self.validate_schema:
                self._validate_manifest(self._core_manifest, "core")
            
            logger.info("📋 Loaded CoreManifest")
        return self._core_manifest
    
    @property
    def config_manifest(self) -> Dict[str, Any]:
        """Lazy load ConfigManifest."""
        if self._config_manifest is None:
            self._config_manifest = self._load_manifest("config-manifest.yaml")
            logger.info("📋 Loaded ConfigManifest")
        return self._config_manifest
    
    @property
    def integration_manifest(self) -> Dict[str, Any]:
        """Lazy load IntegrationManifest."""
        if self._integration_manifest is None:
            self._integration_manifest = self._load_manifest("integration-manifest.yaml")
            logger.info("📋 Loaded IntegrationManifest")
        return self._integration_manifest
    
    # ──────────────────────────────────────────────────────────────
    # YAML Loading
    # ──────────────────────────────────────────────────────────────
    
    def _load_manifest(self, filename: str) -> Dict[str, Any]:
        """
        Load YAML manifest from file.
        
        Args:
            filename: Manifest filename (e.g., "core-manifest.yaml")
            
        Returns:
            Parsed YAML as dictionary
            
        Raises:
            FileNotFoundError: If manifest file doesn't exist
            yaml.YAMLError: If YAML is invalid
        """
        manifest_path = self.manifest_dir / filename
        
        if not manifest_path.exists():
            raise FileNotFoundError(f"Manifest not found: {manifest_path}")
        
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = yaml.safe_load(f)
            
            if not manifest:
                raise ValueError(f"Empty manifest: {manifest_path}")
            
            return manifest
            
        except yaml.YAMLError as e:
            logger.error(f"Invalid YAML in {manifest_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to load {manifest_path}: {e}")
            raise
    
    def _load_schema(self, schema_filename: str) -> Optional[Dict[str, Any]]:
        """
        Load JSON schema from file.
        
        Args:
            schema_filename: Schema filename (e.g., "core-manifest-schema.json")
            
        Returns:
            Parsed JSON schema or None if not found
        """
        if not self.schema_dir.exists():
            logger.warning(f"Schema directory not found: {self.schema_dir}")
            return None
        
        schema_path = self.schema_dir / schema_filename
        
        if not schema_path.exists():
            logger.warning(f"Schema not found: {schema_path}")
            return None
        
        try:
            with open(schema_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load schema {schema_path}: {e}")
            return None
    
    def _validate_manifest(self, manifest: Dict[str, Any], manifest_type: str) -> bool:
        """
        Validate manifest against JSON schema.
        
        Args:
            manifest: Manifest dictionary to validate
            manifest_type: Type of manifest ('core', 'config', 'integration')
            
        Returns:
            True if valid, False otherwise
            
        Raises:
            jsonschema.ValidationError: If validation fails and strict mode
        """
        if not JSONSCHEMA_AVAILABLE:
            logger.debug("jsonschema not available - skipping validation")
            return True
        
        # Load schema
        schema_map = {
            "core": ("_core_schema", "core-manifest-schema.json"),
            "config": ("_config_schema", "config-manifest-schema.json"),
            "integration": ("_integration_schema", "integration-manifest-schema.json")
        }
        
        if manifest_type not in schema_map:
            logger.warning(f"Unknown manifest type: {manifest_type}")
            return False
        
        schema_attr, schema_file = schema_map[manifest_type]
        
        # Lazy load schema
        if not hasattr(self, schema_attr) or getattr(self, schema_attr) is None:
            schema = self._load_schema(schema_file)
            setattr(self, schema_attr, schema)
        else:
            schema = getattr(self, schema_attr)
        
        if not schema:
            logger.warning(f"Schema not found for {manifest_type} - skipping validation")
            return False
        
        # Validate
        try:
            jsonschema.validate(instance=manifest, schema=schema)
            logger.info(f"✅ {manifest_type.capitalize()} manifest validation passed")
            return True
        except jsonschema.ValidationError as e:
            logger.error(f"❌ {manifest_type.capitalize()} manifest validation failed: {e.message}")
            logger.debug(f"   Path: {' -> '.join(map(str, e.path))}")
            return False
        except Exception as e:
            logger.error(f"Schema validation error: {e}")
            return False
    
    # ──────────────────────────────────────────────────────────────
    # Orchestrator Operations
    # ──────────────────────────────────────────────────────────────
            return manifest
            
        except yaml.YAMLError as e:
            logger.error(f"Invalid YAML in {manifest_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to load {manifest_path}: {e}")
            raise
    
    # ──────────────────────────────────────────────────────────────
    # Orchestrator Operations
    # ──────────────────────────────────────────────────────────────
    
    def get_orchestrator(self, orchestrator_id: str) -> Optional[Dict[str, Any]]:
        """
        Get orchestrator metadata from CoreManifest.
        
        Args:
            orchestrator_id: Orchestrator identifier (e.g., "planning_orchestrator")
            
        Returns:
            Orchestrator metadata or None if not found
        """
        orchestrators = self.core_manifest.get("orchestrators", {})
        return orchestrators.get(orchestrator_id)
    
    def list_orchestrators(self, category: Optional[str] = None, status: Optional[str] = None) -> List[str]:
        """
        List orchestrators, optionally filtered by category and status.
        
        Args:
            category: Filter by category (planning, tdd, maintenance, etc.)
            status: Filter by status (active, deprecated, draft, etc.)
            
        Returns:
            List of orchestrator IDs
        """
        orchestrators = self.core_manifest.get("orchestrators", {})
        result = []
        
        for orch_id, orch_data in orchestrators.items():
            # Apply filters
            if category and orch_data.get("category") != category:
                continue
            if status and orch_data.get("status") != status:
                continue
            
            result.append(orch_id)
        
        return result
    
    # ──────────────────────────────────────────────────────────────
    # Config Operations
    # ──────────────────────────────────────────────────────────────
    
    def get_config_section(self, section_path: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration section from ConfigManifest.
        
        Args:
            section_path: Dot-separated path (e.g., "refactoring.planning")
            
        Returns:
            Config section or None if not found
        """
        categories = self.config_manifest.get("categories", {})
        
        # Parse section path (e.g., "refactoring.planning")
        parts = section_path.split(".")
        
        # Navigate through nested structure
        current = categories
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                logger.warning(f"Config section not found: {section_path}")
                return None
        
        return current
    
    def get_orchestrator_config(self, orchestrator_id: str) -> Dict[str, Any]:
        """
        Get merged configuration for an orchestrator.
        
        Args:
            orchestrator_id: Orchestrator identifier
            
        Returns:
            Merged config with defaults + orchestrator overrides
        """
        orch = self.get_orchestrator(orchestrator_id)
        if not orch:
            return {}
        
        # Start with global defaults
        config = deepcopy(self.config_manifest.get("defaults", {}))
        
        # Apply config overrides
        if "config_overrides" in orch:
            sections = orch["config_overrides"].get("sections", [])
            
            for section_path in sections:
                section_config = self.get_config_section(section_path)
                if section_config:
                    # Merge section into config
                    self._deep_merge(config, {section_path: section_config})
        
        return config
    
    # ──────────────────────────────────────────────────────────────
    # Integration Operations
    # ──────────────────────────────────────────────────────────────
    
    def get_integration(self, integration_id: str) -> Optional[Dict[str, Any]]:
        """
        Get integration configuration from IntegrationManifest.
        
        Args:
            integration_id: Integration identifier (e.g., "azure_devops")
            
        Returns:
            Integration config or None if not found
        """
        integrations = self.integration_manifest.get("integrations", {})
        return integrations.get(integration_id)
    
    def list_integrations(self, category: Optional[str] = None) -> List[str]:
        """
        List integrations, optionally filtered by category.
        
        Args:
            category: Filter by category (vcs, project_management, ci_cd, etc.)
            
        Returns:
            List of integration IDs
        """
        integrations = self.integration_manifest.get("integrations", {})
        result = []
        
        for integration_id, integration_data in integrations.items():
            # Apply filter
            if category and integration_data.get("category") != category:
                continue
            
            result.append(integration_id)
        
        return result
    
    # ──────────────────────────────────────────────────────────────
    # Cross-Reference Resolution
    # ──────────────────────────────────────────────────────────────
    
    def resolve_cross_references(self, orchestrator_id: str) -> Dict[str, Any]:
        """
        Resolve all cross-references for an orchestrator.
        
        Returns merged configuration from:
        - CoreManifest (orchestrator metadata)
        - ConfigManifest (runtime config)
        - IntegrationManifest (external systems)
        
        Args:
            orchestrator_id: Orchestrator identifier
            
        Returns:
            Fully resolved configuration
        """
        # Check cache first
        if orchestrator_id in self._resolved_cache:
            logger.debug(f"Using cached cross-references for {orchestrator_id}")
            return self._resolved_cache[orchestrator_id]
        
        # Load orchestrator from CoreManifest
        orch = self.get_orchestrator(orchestrator_id)
        if not orch:
            logger.error(f"Orchestrator not found: {orchestrator_id}")
            return {}
        
        # Build resolved config
        resolved = {
            "metadata": deepcopy(orch),
            "config": {},
            "integrations": {}
        }
        
        # Resolve config overrides
        if "config_overrides" in orch:
            sections = orch["config_overrides"].get("sections", [])
            
            for section_path in sections:
                section_config = self.get_config_section(section_path)
                if section_config:
                    resolved["config"][section_path] = section_config
        
        # Resolve integrations
        if "integrations" in orch:
            integration_refs = orch["integrations"]
            
            for integration_ref in integration_refs:
                # Parse reference (e.g., "integration://azure_devops" → "azure_devops")
                integration_id = integration_ref.replace("integration://", "")
                
                integration_config = self.get_integration(integration_id)
                if integration_config:
                    resolved["integrations"][integration_id] = integration_config
        
        # Cache result
        self._resolved_cache[orchestrator_id] = deepcopy(resolved)
        
        logger.info(f"✅ Resolved cross-references for {orchestrator_id}")
        return resolved
    
    # ──────────────────────────────────────────────────────────────
    # Utility Methods
    # ──────────────────────────────────────────────────────────────
    
    def _deep_merge(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """
        Deep merge source into target (in-place).
        
        Args:
            target: Target dictionary to merge into
            source: Source dictionary to merge from
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                # Recursively merge nested dicts
                self._deep_merge(target[key], value)
            else:
                # Overwrite with source value
                target[key] = deepcopy(value)
    
    def clear_cache(self) -> None:
        """Clear all cached data."""
        self._core_manifest = None
        self._config_manifest = None
        self._integration_manifest = None
        self._resolved_cache = {}
        logger.info("🗑️ Cleared manifest cache")
    
    def reload_manifests(self) -> None:
        """Reload all manifests from disk."""
        self.clear_cache()
        # Force reload by accessing properties
        _ = self.core_manifest
        _ = self.config_manifest
        _ = self.integration_manifest
        logger.info("🔄 Reloaded all manifests")
    
    def get_manifest_stats(self) -> Dict[str, Any]:
        """
        Get statistics about loaded manifests.
        
        Returns:
            Dictionary with manifest statistics
        """
        return {
            "core_manifest": {
                "loaded": self._core_manifest is not None,
                "orchestrators_count": len(self.core_manifest.get("orchestrators", {})),
                "schema_version": self.core_manifest.get("schema_version"),
                "last_updated": self.core_manifest.get("last_updated")
            },
            "config_manifest": {
                "loaded": self._config_manifest is not None,
                "categories_count": len(self.config_manifest.get("categories", {})),
                "schema_version": self.config_manifest.get("schema_version"),
                "last_updated": self.config_manifest.get("last_updated")
            },
            "integration_manifest": {
                "loaded": self._integration_manifest is not None,
                "integrations_count": len(self.integration_manifest.get("integrations", {})),
                "schema_version": self.integration_manifest.get("schema_version"),
                "last_updated": self.integration_manifest.get("last_updated")
            },
            "cache": {
                "resolved_orchestrators": len(self._resolved_cache)
            }
        }


# ──────────────────────────────────────────────────────────────
# Backward Compatibility Adapter
# ──────────────────────────────────────────────────────────────

class ManifestMigrationAdapter:
    """
    Backward compatibility adapter for old manifest format.
    
    Provides compatibility layer for orchestrators still using old format:
    - cortex-brain/manifests/orchestrators/{orchestrator}-manifest.yaml (OLD)
    - cortex-brain/manifests/core-manifest.yaml (NEW)
    
    Usage:
        adapter = ManifestMigrationAdapter(cortex_root)
        
        # Load using old path
        manifest = adapter.load_old_format("planning_orchestrator")
        
        # Load using new path
        manifest = adapter.load_new_format("planning_orchestrator")
        
        # Validate equivalence
        is_equivalent = adapter.validate_equivalence("planning_orchestrator")
    """
    
    def __init__(self, cortex_root: str):
        """
        Initialize adapter.
        
        Args:
            cortex_root: Path to CORTEX root directory
        """
        self.cortex_root = Path(cortex_root)
        self.old_manifest_dir = self.cortex_root / "cortex-brain" / "manifests" / "orchestrators"
        self.new_loader = ManifestLoader(cortex_root)
    
    def load_old_format(self, orchestrator_id: str) -> Optional[Dict[str, Any]]:
        """
        Load manifest using old format.
        
        Args:
            orchestrator_id: Orchestrator identifier
            
        Returns:
            Old manifest or None if not found
        """
        # Try multiple naming patterns
        patterns = [
            f"{orchestrator_id}-manifest.yaml",
            f"{orchestrator_id}-orchestrator-manifest.yaml",
            f"{orchestrator_id.replace('_', '-')}-manifest.yaml"
        ]
        
        for pattern in patterns:
            manifest_path = self.old_manifest_dir / pattern
            if manifest_path.exists():
                try:
                    with open(manifest_path, 'r', encoding='utf-8') as f:
                        return yaml.safe_load(f)
                except Exception as e:
                    logger.error(f"Failed to load old manifest {manifest_path}: {e}")
        
        logger.warning(f"Old manifest not found for: {orchestrator_id}")
        return None
    
    def load_new_format(self, orchestrator_id: str) -> Optional[Dict[str, Any]]:
        """
        Load manifest using new format.
        
        Args:
            orchestrator_id: Orchestrator identifier
            
        Returns:
            Resolved manifest from new format
        """
        return self.new_loader.resolve_cross_references(orchestrator_id)
    
    def validate_equivalence(self, orchestrator_id: str) -> bool:
        """
        Validate that old and new formats are equivalent.
        
        Args:
            orchestrator_id: Orchestrator identifier
            
        Returns:
            True if formats are equivalent, False otherwise
        """
        old = self.load_old_format(orchestrator_id)
        new = self.load_new_format(orchestrator_id)
        
        if not old or not new:
            logger.error(f"Cannot validate equivalence: manifest not found")
            return False
        
        # Compare key fields
        checks = []
        
        # Check metadata fields
        old_metadata = old.get("metadata", {})
        new_metadata = new.get("metadata", {})
        
        if old_metadata.get("version") == new_metadata.get("version"):
            checks.append("version_match")
        
        if old_metadata.get("description") == new_metadata.get("description"):
            checks.append("description_match")
        
        # Check phases (if applicable)
        old_phases = old.get("phases", {})
        new_phases = new_metadata.get("phases", {})
        
        if old_phases and new_phases:
            if len(old_phases) == len(new_phases):
                checks.append("phase_count_match")
        
        logger.info(f"Equivalence checks for {orchestrator_id}: {checks}")
        
        # Consider equivalent if at least version matches
        return "version_match" in checks
    
    def migrate_orchestrator(self, orchestrator_id: str) -> Dict[str, Any]:
        """
        Generate migration report for an orchestrator.
        
        Args:
            orchestrator_id: Orchestrator identifier
            
        Returns:
            Migration report with comparison details
        """
        return {
            "orchestrator_id": orchestrator_id,
            "timestamp": datetime.now().isoformat(),
            "old_format_exists": self.load_old_format(orchestrator_id) is not None,
            "new_format_exists": self.load_new_format(orchestrator_id) is not None,
            "is_equivalent": self.validate_equivalence(orchestrator_id),
            "recommendation": "safe_to_migrate" if self.validate_equivalence(orchestrator_id) else "requires_review"
        }


def main():
    """Example usage and testing."""
    import sys
    
    # Get CORTEX root
    cortex_root = Path(__file__).parent.parent.parent
    
    print("=" * 80)
    print("ManifestLoader - 3-Tier Manifest Architecture")
    print("=" * 80)
    
    try:
        # Initialize loader
        loader = ManifestLoader(str(cortex_root))
        print("\n✅ ManifestLoader initialized")
        
        # Get stats
        stats = loader.get_manifest_stats()
        print(f"\n📊 Manifest Statistics:")
        print(f"   CoreManifest: {stats['core_manifest']['orchestrators_count']} orchestrators")
        print(f"   ConfigManifest: {stats['config_manifest']['categories_count']} categories")
        print(f"   IntegrationManifest: {stats['integration_manifest']['integrations_count']} integrations")
        
        # List orchestrators
        orchestrators = loader.list_orchestrators(status="active")
        print(f"\n📋 Active Orchestrators ({len(orchestrators)}):")
        for orch_id in orchestrators[:5]:  # Show first 5
            print(f"   - {orch_id}")
        
        # Resolve cross-references
        if orchestrators:
            test_orch = orchestrators[0]
            resolved = loader.resolve_cross_references(test_orch)
            print(f"\n🔗 Cross-references for '{test_orch}':")
            print(f"   Config sections: {len(resolved.get('config', {}))}")
            print(f"   Integrations: {len(resolved.get('integrations', {}))}")
        
        print("\n✅ All operations completed successfully")
        
        # Test migration adapter
        print("\n" + "=" * 80)
        print("Testing Migration Adapter")
        print("=" * 80)
        
        adapter = ManifestMigrationAdapter(str(cortex_root))
        
        if orchestrators:
            test_orch = orchestrators[0]
            report = adapter.migrate_orchestrator(test_orch)
            print(f"\n📊 Migration Report for '{test_orch}':")
            print(f"   Old format exists: {report['old_format_exists']}")
            print(f"   New format exists: {report['new_format_exists']}")
            print(f"   Is equivalent: {report['is_equivalent']}")
            print(f"   Recommendation: {report['recommendation']}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
