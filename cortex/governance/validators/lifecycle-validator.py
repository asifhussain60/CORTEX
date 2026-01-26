"""
Lifecycle Metadata Validator for CORE-040 Documentation Lifecycle Management

Validates that all documentation files include expiration timestamps
to prevent bloat at source through lifecycle management.
"""

import re
import yaml
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Tuple, List, Any, Union


class LifecycleMetadataValidator:
    """Validates CORE-040 lifecycle metadata for documentation files."""
    
    # Default lifetimes in days by category
    LIFETIME_DEFAULTS: Dict[str, int] = {
        'session': 7,
        'analysis': 30,
        'phase': 90,
        'test': 14,
        'tool': 30,
    }
    
    # Patterns requiring lifecycle metadata
    MONITORED_PATTERNS: List[Tuple[str, str]] = [
        ('reports/session/', 'session'),
        ('reports/analysis/', 'analysis'),
        ('reports/phase/', 'phase'),
        ('reports/test/', 'test'),
        ('reports/tool/', 'tool'),
    ]
    
    # Patterns exempt from lifecycle requirements
    EXEMPT_PATTERNS: List[str] = [
        'docs/',
        'reports/*/README.md',
        'reports/*.yaml',
    ]
    
    def __init__(self) -> None:
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate_file(self, file_path: Path) -> Tuple[bool, Dict[str, Any]]:
        """
        Validate that a file has proper lifecycle metadata.
        
        Returns:
            (is_valid, metadata_dict or error_dict)
        """
        self.errors = []
        self.warnings = []
        
        # Check if file is exempt
        if self._is_exempt(file_path):
            return True, {'status': 'exempt'}
        
        # Check if file requires lifecycle metadata
        category = self._get_category(file_path)
        if not category:
            return True, {'status': 'not_monitored'}
        
        # Extract metadata
        metadata = self._extract_metadata(file_path)
        
        # Validate metadata
        if not metadata:
            self.errors.append(f"No lifecycle metadata found in {file_path}")
            return False, {'error': 'missing_metadata', 'file': str(file_path)}
        
        # Validate required fields
        if 'expires_at' not in metadata:
            self.errors.append(f"Missing 'expires_at' in {file_path}")
            return False, {'error': 'missing_expires_at', 'file': str(file_path)}
        
        # Validate ISO8601 timestamp
        try:
            expires_at = datetime.fromisoformat(
                str(metadata['expires_at']).replace('Z', '+00:00')
            )
        except (ValueError, AttributeError) as e:
            self.errors.append(f"Invalid expires_at format in {file_path}: {e}")
            return False, {'error': 'invalid_timestamp_format', 'file': str(file_path)}
        
        # Validate lifetime matches category
        if 'lifetime_days' in metadata:
            lifetime = int(metadata['lifetime_days'])
            expected_lifetime = self.LIFETIME_DEFAULTS.get(category)
            if expected_lifetime and abs(lifetime - expected_lifetime) > 5:
                self.warnings.append(
                    f"Lifetime {lifetime} days differs from category default "
                    f"{expected_lifetime} for {file_path}"
                )
        
        # All checks passed
        return True, {
            'status': 'valid',
            'category': category,
            'expires_at': metadata['expires_at'],
            'created_at': metadata.get('created_at', 'unknown'),
        }
    
    def _is_exempt(self, file_path: Path) -> bool:
        """Check if file is exempt from lifecycle requirements."""
        path_str = str(file_path)
        for pattern in self.EXEMPT_PATTERNS:
            if pattern in path_str:
                return True
        return False
    
    def _get_category(self, file_path: Path) -> Optional[str]:
        """Determine file category based on path."""
        path_str = str(file_path)
        
        # Only check .md and .txt files in reports/
        if not (path_str.endswith('.md') or path_str.endswith('.txt')):
            return None
        
        if 'reports/' not in path_str:
            return None
        
        # Find matching category
        for pattern, category in self.MONITORED_PATTERNS:
            if pattern in path_str:
                return category
        
        return None
    
    def _extract_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract lifecycle metadata from file (YAML front-matter or sidecar)."""
        metadata: Dict[str, Any] = {}
        
        # Try YAML front-matter first
        metadata = self._extract_yaml_frontmatter(file_path)
        if metadata:
            return metadata
        
        # Try sidecar .metadata.yaml file
        metadata = self._extract_sidecar_metadata(file_path)
        if metadata:
            return metadata
        
        return {}
    
    def _extract_yaml_frontmatter(self, file_path: Path) -> Dict[str, Any]:
        """Extract YAML front-matter from file."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
                # Check for YAML front-matter delimiter
                if not content.startswith('---'):
                    return {}
                
                # Find end of front-matter
                lines = content.split('\n')
                if len(lines) < 2:
                    return {}
                
                end_idx = None
                for i, line in enumerate(lines[1:], 1):
                    if line.strip() == '---':
                        end_idx = i
                        break
                
                if end_idx is None:
                    return {}
                
                # Parse YAML
                yaml_content = '\n'.join(lines[1:end_idx])
                loaded = yaml.safe_load(yaml_content)
                return loaded if isinstance(loaded, dict) else {}
        
        except Exception:
            return {}
    
    def _extract_sidecar_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata from .metadata.yaml sidecar file."""
        metadata_path = file_path.parent / f"{file_path.stem}.metadata.yaml"
        
        try:
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    loaded = yaml.safe_load(f)
                    return loaded if isinstance(loaded, dict) else {}
        except Exception:
            pass
        
        return {}
    
    def is_expired(self, file_path: Path) -> bool:
        """Check if file has expired based on metadata."""
        _, result = self.validate_file(file_path)
        
        if not result.get('expires_at'):
            return False
        
        try:
            expires_at = datetime.fromisoformat(
                str(result['expires_at']).replace('Z', '+00:00')
            )
            return datetime.now(expires_at.tzinfo) > expires_at
        except Exception:
            return False
    
    def should_delete(self, file_path: Path) -> bool:
        """Check if file should be deleted (expired + auto_delete enabled)."""
        if not self.is_expired(file_path):
            return False
        
        # Check if auto_delete is enabled
        metadata = self._extract_metadata(file_path)
        auto_delete: Union[bool, str] = metadata.get('auto_delete_on_expiry', True)
        
        # Handle string conversion
        if isinstance(auto_delete, str):
            auto_delete = auto_delete.lower() in ('true', 'yes', '1')
        
        return bool(auto_delete)


def validate_documentation_file(file_path: Path) -> Tuple[bool, Dict[str, Any]]:
    """Convenience function to validate a single file."""
    validator = LifecycleMetadataValidator()
    return validator.validate_file(file_path)


def check_expired_files(reports_dir: Optional[Path] = None) -> Dict[str, Any]:
    """
    Find all expired files in reports directory.
    
    Returns:
        {'expired': [list of expired files], 'warnings': [...]}
    """
    if reports_dir is None:
        reports_dir = Path('reports')
    
    validator = LifecycleMetadataValidator()
    expired_files: List[str] = []
    
    # Find all .md and .txt files
    for file_path in reports_dir.rglob('*'):
        if file_path.suffix not in ('.md', '.txt'):
            continue
        
        if validator.is_expired(file_path):
            expired_files.append(str(file_path))
    
    return {
        'expired': expired_files,
        'warnings': validator.warnings,
    }
