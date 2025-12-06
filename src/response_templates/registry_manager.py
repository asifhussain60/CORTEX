"""
Registry Manager for Template Registration and Discovery

This module manages the central template registry that maps template IDs
to file locations, categories, and metadata.

Registry Format (template-registry.yaml):
    version: 4.0
    templates:
      template_id:
        file: path/to/file.yaml
        id: template_id
        category: agents|orchestrators|operations|specialized
        tags: [tag1, tag2, tag3]
        created: 2025-12-05
        last_modified: 2025-12-05

Author: Asif Hussain
Phase: 2 - Core Infrastructure
Version: 1.0
Created: December 5, 2025
"""

import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib
import logging

logger = logging.getLogger(__name__)


@dataclass
class TemplateRegistryEntry:
    """Represents a template registry entry."""
    template_id: str
    file: str  # Relative path from template_dir
    category: str  # agents, orchestrators, operations, specialized
    tags: List[str]
    created: Optional[str] = None
    last_modified: Optional[str] = None
    description: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for YAML serialization."""
        return {k: v for k, v in asdict(self).items() if v is not None}


class RegistryManager:
    """
    Central template registry management.
    
    Features:
    - Template registration and lookup
    - Category-based organization
    - Tag-based search
    - Duplicate ID detection
    - Registry validation
    - Auto-generation from file structure
    
    Usage:
        manager = RegistryManager(
            registry_file=Path("cortex-brain/response-templates/config/template-registry.yaml")
        )
        
        # Lookup template file
        file_path = manager.get_template_file("planning")
        
        # Register new template
        manager.register_template("new_template", "agents/tactical/new.yaml", "agents")
        
        # Save registry
        manager.save_registry()
    """
    
    def __init__(
        self,
        registry_file: Path,
        template_dir: Optional[Path] = None
    ):
        """
        Initialize registry manager.
        
        Args:
            registry_file: Path to template-registry.yaml
            template_dir: Base directory for templates (for validation)
        """
        self.registry_file = registry_file
        self.template_dir = template_dir or registry_file.parent.parent
        
        # Registry data: template_id → TemplateRegistryEntry
        self.registry: Dict[str, TemplateRegistryEntry] = {}
        
        # Registry metadata
        self.version = "4.0"
        self.last_updated: Optional[str] = None
        
        # Load existing registry
        if self.registry_file.exists():
            self._load_registry()
        else:
            logger.warning(f"Registry file not found: {registry_file}. Starting with empty registry.")
        
        logger.info(f"RegistryManager initialized: {len(self.registry)} templates")
    
    def _load_registry(self):
        """Load registry from YAML file."""
        try:
            with open(self.registry_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if not data:
                logger.warning("Registry file is empty")
                return
            
            self.version = data.get('version', '4.0')
            self.last_updated = data.get('last_updated')
            
            templates_data = data.get('templates', {})
            
            for template_id, template_info in templates_data.items():
                entry = TemplateRegistryEntry(
                    template_id=template_id,
                    file=template_info.get('file', ''),
                    category=template_info.get('category', 'uncategorized'),
                    tags=template_info.get('tags', []),
                    created=template_info.get('created'),
                    last_modified=template_info.get('last_modified'),
                    description=template_info.get('description')
                )
                self.registry[template_id] = entry
            
            logger.info(f"Registry loaded: {len(self.registry)} templates")
        
        except Exception as e:
            logger.error(f"Failed to load registry: {e}")
    
    def save_registry(self):
        """Save registry to YAML file."""
        try:
            # Ensure directory exists
            self.registry_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Prepare data
            data = {
                'version': self.version,
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'templates': {}
            }
            
            # Add templates (sorted by ID)
            for template_id in sorted(self.registry.keys()):
                entry = self.registry[template_id]
                data['templates'][template_id] = entry.to_dict()
            
            # Write to file
            with open(self.registry_file, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
            
            logger.info(f"Registry saved: {len(self.registry)} templates")
        
        except Exception as e:
            logger.error(f"Failed to save registry: {e}")
            raise
    
    def register_template(
        self,
        template_id: str,
        file_path: str,
        category: str,
        tags: Optional[List[str]] = None,
        description: Optional[str] = None,
        overwrite: bool = False
    ) -> bool:
        """
        Register a new template in the registry.
        
        Args:
            template_id: Unique template identifier
            file_path: Relative path to template file (from template_dir)
            category: Template category (agents, orchestrators, operations, specialized)
            tags: Optional list of tags
            description: Optional description
            overwrite: If True, overwrite existing entry
        
        Returns:
            True if registered successfully, False if duplicate and not overwriting
        """
        # Check for duplicate
        if template_id in self.registry and not overwrite:
            logger.warning(f"Template ID already exists: {template_id}")
            return False
        
        # Create registry entry
        entry = TemplateRegistryEntry(
            template_id=template_id,
            file=file_path,
            category=category,
            tags=tags or [],
            created=datetime.now().strftime('%Y-%m-%d'),
            last_modified=datetime.now().strftime('%Y-%m-%d'),
            description=description
        )
        
        self.registry[template_id] = entry
        logger.info(f"Template registered: {template_id} → {file_path}")
        
        return True
    
    def unregister_template(self, template_id: str) -> bool:
        """
        Remove template from registry.
        
        Args:
            template_id: Template ID to remove
        
        Returns:
            True if removed, False if not found
        """
        if template_id in self.registry:
            del self.registry[template_id]
            logger.info(f"Template unregistered: {template_id}")
            return True
        else:
            logger.warning(f"Template not found in registry: {template_id}")
            return False
    
    def get_template_file(self, template_id: str) -> Optional[str]:
        """
        Get file path for template ID.
        
        Args:
            template_id: Template identifier
        
        Returns:
            Relative file path or None if not found
        """
        entry = self.registry.get(template_id)
        return entry.file if entry else None
    
    def get_template_entry(self, template_id: str) -> Optional[TemplateRegistryEntry]:
        """
        Get complete registry entry for template.
        
        Args:
            template_id: Template identifier
        
        Returns:
            TemplateRegistryEntry or None if not found
        """
        return self.registry.get(template_id)
    
    def get_templates_by_category(self, category: str) -> List[str]:
        """
        Get all template IDs in a category.
        
        Args:
            category: Category name (agents, orchestrators, operations, specialized)
        
        Returns:
            List of template IDs in category
        """
        return [
            template_id
            for template_id, entry in self.registry.items()
            if entry.category == category
        ]
    
    def get_templates_by_tag(self, tag: str) -> List[str]:
        """
        Get all template IDs with a specific tag.
        
        Args:
            tag: Tag to search for
        
        Returns:
            List of template IDs with tag
        """
        return [
            template_id
            for template_id, entry in self.registry.items()
            if tag in entry.tags
        ]
    
    def search_templates(self, query: str) -> List[str]:
        """
        Search templates by ID, description, or tags.
        
        Args:
            query: Search query (case-insensitive)
        
        Returns:
            List of matching template IDs
        """
        query_lower = query.lower()
        matches = []
        
        for template_id, entry in self.registry.items():
            # Search in template ID
            if query_lower in template_id.lower():
                matches.append(template_id)
                continue
            
            # Search in description
            if entry.description and query_lower in entry.description.lower():
                matches.append(template_id)
                continue
            
            # Search in tags
            if any(query_lower in tag.lower() for tag in entry.tags):
                matches.append(template_id)
                continue
        
        return matches
    
    def validate_registry(self) -> List[str]:
        """
        Validate registry integrity.
        
        Checks:
        - All referenced files exist
        - No duplicate file paths
        - Valid categories
        
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        valid_categories = {'agents', 'orchestrators', 'operations', 'specialized', 'uncategorized'}
        file_to_ids: Dict[str, List[str]] = {}
        
        for template_id, entry in self.registry.items():
            # Check file exists
            file_path = self.template_dir / entry.file
            if not file_path.exists():
                errors.append(f"{template_id}: File not found: {entry.file}")
            
            # Check category is valid
            if entry.category not in valid_categories:
                errors.append(f"{template_id}: Invalid category: {entry.category}")
            
            # Track duplicate files
            if entry.file not in file_to_ids:
                file_to_ids[entry.file] = []
            file_to_ids[entry.file].append(template_id)
        
        # Report duplicate file mappings (info, not error)
        for file_path, template_ids in file_to_ids.items():
            if len(template_ids) > 1:
                logger.info(
                    f"Multiple templates in same file: {file_path} → {', '.join(template_ids)}"
                )
        
        return errors
    
    def auto_discover_templates(self, scan_dir: Optional[Path] = None) -> int:
        """
        Auto-discover templates from file structure.
        
        Scans template directory and registers any YAML files not already in registry.
        
        Args:
            scan_dir: Directory to scan (default: template_dir)
        
        Returns:
            Number of new templates discovered
        """
        scan_dir = scan_dir or self.template_dir
        discovered = 0
        
        # Find all YAML files
        for yaml_file in scan_dir.rglob('*.yaml'):
            # Skip registry file itself
            if yaml_file == self.registry_file:
                continue
            
            # Get relative path
            try:
                rel_path = yaml_file.relative_to(self.template_dir)
            except ValueError:
                # File is outside template_dir
                continue
            
            # Determine category from path
            parts = rel_path.parts
            if len(parts) > 0:
                category = parts[0]
                if category == 'core':
                    category = 'core'
                elif category in {'agents', 'orchestrators', 'operations', 'specialized'}:
                    pass
                else:
                    category = 'uncategorized'
            else:
                category = 'uncategorized'
            
            # Try to load file and extract template IDs
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    content = yaml.safe_load(f)
                
                if isinstance(content, dict):
                    # Multi-template file or single template
                    for key in content.keys():
                        template_id = key
                        
                        # Check if already registered
                        if template_id not in self.registry:
                            self.register_template(
                                template_id=template_id,
                                file_path=str(rel_path),
                                category=category,
                                tags=[],
                                description=f"Auto-discovered from {rel_path}"
                            )
                            discovered += 1
            
            except Exception as e:
                logger.warning(f"Failed to parse {yaml_file}: {e}")
        
        logger.info(f"Auto-discovery complete: {discovered} new templates found")
        return discovered
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get registry statistics."""
        stats = {
            'total_templates': len(self.registry),
            'by_category': {},
            'total_files': len(set(entry.file for entry in self.registry.values())),
            'version': self.version,
            'last_updated': self.last_updated,
        }
        
        # Count by category
        for entry in self.registry.values():
            category = entry.category
            stats['by_category'][category] = stats['by_category'].get(category, 0) + 1
        
        return stats
    
    def get_all_template_ids(self) -> List[str]:
        """Get list of all registered template IDs."""
        return sorted(self.registry.keys())
    
    def export_to_markdown(self, output_file: Path):
        """
        Export registry to markdown documentation.
        
        Args:
            output_file: Output markdown file path
        """
        lines = [
            "# Template Registry",
            "",
            f"**Version:** {self.version}",
            f"**Last Updated:** {self.last_updated or 'N/A'}",
            f"**Total Templates:** {len(self.registry)}",
            "",
            "---",
            ""
        ]
        
        # Group by category
        categories = {}
        for template_id, entry in self.registry.items():
            category = entry.category
            if category not in categories:
                categories[category] = []
            categories[category].append((template_id, entry))
        
        # Output by category
        for category in sorted(categories.keys()):
            lines.append(f"## {category.capitalize()}")
            lines.append("")
            
            templates = sorted(categories[category], key=lambda x: x[0])
            
            for template_id, entry in templates:
                lines.append(f"### `{template_id}`")
                lines.append("")
                lines.append(f"- **File:** `{entry.file}`")
                lines.append(f"- **Tags:** {', '.join(entry.tags) if entry.tags else 'None'}")
                if entry.description:
                    lines.append(f"- **Description:** {entry.description}")
                lines.append(f"- **Created:** {entry.created or 'N/A'}")
                lines.append(f"- **Last Modified:** {entry.last_modified or 'N/A'}")
                lines.append("")
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        logger.info(f"Registry exported to markdown: {output_file}")
