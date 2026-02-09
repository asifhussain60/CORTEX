"""
Custom Pattern Registry for Enterprise Pattern Definitions

AC_START: AC-PHASE60.0-S1-001
Authority: phase-60-enterprise-pattern-registry.yaml Stage 1
Purpose: Enable users to define and manage custom architectural patterns via YAML/JSON
         - Pattern definition schema validation
         - Registry loading and caching
         - Pattern metadata management
         - Detection rule compilation

Tests Target: 12 tests (pattern loading, schema validation, registry operations)
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import hashlib
from datetime import datetime
import jsonschema


# ============================================================================
# Enums and Constants
# ============================================================================

class PatternCategory(Enum):
    """Pattern categories for classification."""
    CREATIONAL = "creational"
    STRUCTURAL = "structural"
    BEHAVIORAL = "behavioral"
    CONCURRENCY = "concurrency"
    ARCHITECTURAL = "architectural"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"


class DetectionRuleType(Enum):
    """Types of detection rules."""
    AST = "ast"
    SEMANTIC = "semantic"
    STRUCTURAL = "structural"


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class DetectionRule:
    """Detection rule for pattern matching."""
    type: DetectionRuleType
    confidence_threshold: float = 0.75
    ast_patterns: List[Dict[str, Any]] = field(default_factory=list)
    semantic_rules: List[Dict[str, Any]] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate confidence threshold."""
        if not 0.0 <= self.confidence_threshold <= 1.0:
            raise ValueError(
                f"Confidence threshold must be between 0 and 1, got {self.confidence_threshold}"
            )


@dataclass
class PatternMetadata:
    """Metadata for a custom pattern."""
    id: str
    name: str
    category: PatternCategory
    description: str = ""
    use_cases: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    impact_score: float = 5.0
    effort_score: float = 5.0
    tags: List[str] = field(default_factory=list)
    related_patterns: List[str] = field(default_factory=list)
    custom_metadata: Dict[str, Any] = field(default_factory=dict)
    detection_rules: Optional[DetectionRule] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    author: str = ""
    version: str = "1.0"
    
    def __post_init__(self):
        """Validate pattern metadata."""
        if not self.id or not isinstance(self.id, str):
            raise ValueError("Pattern ID must be a non-empty string")
        
        if not self.name or not isinstance(self.name, str):
            raise ValueError("Pattern name must be a non-empty string")
        
        if not isinstance(self.category, PatternCategory):
            raise ValueError(f"Invalid pattern category: {self.category}")
        
        if not 0 <= self.impact_score <= 10:
            raise ValueError("Impact score must be between 0 and 10")
        
        if not 0 <= self.effort_score <= 10:
            raise ValueError("Effort score must be between 0 and 10")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        if self.category:
            data['category'] = self.category.value
        if self.detection_rules:
            data['detection_rules'] = asdict(self.detection_rules)
            if self.detection_rules.type:
                data['detection_rules']['type'] = self.detection_rules.type.value
        return data
    
    def compute_hash(self) -> str:
        """Compute hash of pattern for versioning."""
        data = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()[:16]


# ============================================================================
# Custom Pattern Registry
# ============================================================================

class CustomPatternRegistry:
    """Registry for managing custom pattern definitions."""
    
    def __init__(self, registry_path: Optional[Path] = None):
        """Initialize pattern registry.
        
        Args:
            registry_path: Path to registry directory (defaults to cortex/intelligence/patterns/registry)
        """
        self.registry_path = registry_path or Path(__file__).parent / "registry"
        self.patterns: Dict[str, PatternMetadata] = {}
        self._schema_validator: Optional[jsonschema.Draft7Validator] = None
        self._load_schema()
    
    def _load_schema(self) -> None:
        """Load JSON schema from schema.yaml."""
        schema_file = Path(__file__).parent / "schema.yaml"
        if schema_file.exists():
            with open(schema_file) as f:
                schema_data = yaml.safe_load(f)
                if schema_data and 'json_schema' in schema_data:
                    self._schema_validator = jsonschema.Draft7Validator(
                        schema_data['json_schema']
                    )
    
    def validate_pattern(self, pattern_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate pattern definition against schema.
        
        Args:
            pattern_data: Pattern definition to validate
        
        Returns:
            Tuple of (is_valid, error_messages)
        """
        if not self._schema_validator:
            return True, []
        
        errors = []
        for error in self._schema_validator.iter_errors(pattern_data):
            errors.append(f"{'.'.join(str(p) for p in error.path)}: {error.message}")
        
        return len(errors) == 0, errors
    
    def load_from_yaml(self, yaml_path: Path) -> Tuple[bool, str, Optional[PatternMetadata]]:
        """Load pattern from YAML file.
        
        Args:
            yaml_path: Path to YAML file
        
        Returns:
            Tuple of (success, message, pattern_metadata)
        """
        try:
            with open(yaml_path) as f:
                data = yaml.safe_load(f)
            
            # Validate against schema
            is_valid, errors = self.validate_pattern(data)
            if not is_valid:
                return False, f"Validation errors: {', '.join(errors)}", None
            
            # Create pattern metadata
            pattern = self._dict_to_pattern(data)
            self.patterns[pattern.id] = pattern
            return True, f"Pattern '{pattern.id}' loaded successfully", pattern
        
        except FileNotFoundError:
            return False, f"File not found: {yaml_path}", None
        except yaml.YAMLError as e:
            return False, f"YAML parse error: {str(e)}", None
        except Exception as e:
            return False, f"Error loading pattern: {str(e)}", None
    
    def load_from_json(self, json_path: Path) -> Tuple[bool, str, Optional[PatternMetadata]]:
        """Load pattern from JSON file.
        
        Args:
            json_path: Path to JSON file
        
        Returns:
            Tuple of (success, message, pattern_metadata)
        """
        try:
            with open(json_path) as f:
                data = json.load(f)
            
            # Validate against schema
            is_valid, errors = self.validate_pattern(data)
            if not is_valid:
                return False, f"Validation errors: {', '.join(errors)}", None
            
            # Create pattern metadata
            pattern = self._dict_to_pattern(data)
            self.patterns[pattern.id] = pattern
            return True, f"Pattern '{pattern.id}' loaded successfully", pattern
        
        except FileNotFoundError:
            return False, f"File not found: {json_path}", None
        except json.JSONDecodeError as e:
            return False, f"JSON parse error: {str(e)}", None
        except Exception as e:
            return False, f"Error loading pattern: {str(e)}", None
    
    def register_pattern(self, pattern: PatternMetadata) -> Tuple[bool, str]:
        """Register a custom pattern.
        
        Args:
            pattern: Pattern metadata to register
        
        Returns:
            Tuple of (success, message)
        """
        try:
            # Validate pattern
            pattern_dict = pattern.to_dict()
            is_valid, errors = self.validate_pattern(pattern_dict)
            if not is_valid:
                return False, f"Validation errors: {', '.join(errors)}"
            
            # Check for duplicate
            if pattern.id in self.patterns:
                return False, f"Pattern '{pattern.id}' already exists"
            
            self.patterns[pattern.id] = pattern
            return True, f"Pattern '{pattern.id}' registered successfully"
        
        except Exception as e:
            return False, f"Error registering pattern: {str(e)}"
    
    def get_pattern(self, pattern_id: str) -> Optional[PatternMetadata]:
        """Get pattern by ID.
        
        Args:
            pattern_id: Pattern identifier
        
        Returns:
            Pattern metadata or None if not found
        """
        return self.patterns.get(pattern_id)
    
    def get_patterns_by_category(self, category: PatternCategory) -> List[PatternMetadata]:
        """Get patterns by category.
        
        Args:
            category: Pattern category
        
        Returns:
            List of patterns in category
        """
        return [p for p in self.patterns.values() if p.category == category]
    
    def get_patterns_by_tag(self, tag: str) -> List[PatternMetadata]:
        """Get patterns by tag.
        
        Args:
            tag: Search tag
        
        Returns:
            List of patterns with tag
        """
        return [p for p in self.patterns.values() if tag in p.tags]
    
    def list_patterns(self) -> List[PatternMetadata]:
        """List all registered patterns.
        
        Returns:
            List of all patterns
        """
        return list(self.patterns.values())
    
    def export_registry(self, output_path: Path, format: str = "yaml") -> Tuple[bool, str]:
        """Export registry to file.
        
        Args:
            output_path: Path to output file
            format: Export format ('yaml' or 'json')
        
        Returns:
            Tuple of (success, message)
        """
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                'metadata': {
                    'exported_at': datetime.utcnow().isoformat(),
                    'pattern_count': len(self.patterns),
                    'format_version': '1.0'
                },
                'patterns': [p.to_dict() for p in self.patterns.values()]
            }
            
            if format == "yaml":
                with open(output_path, 'w') as f:
                    yaml.dump(data, f, default_flow_style=False)
            else:  # json
                with open(output_path, 'w') as f:
                    json.dump(data, f, indent=2)
            
            return True, f"Registry exported to {output_path}"
        
        except Exception as e:
            return False, f"Error exporting registry: {str(e)}"
    
    def _dict_to_pattern(self, data: Dict[str, Any]) -> PatternMetadata:
        """Convert dictionary to PatternMetadata.
        
        Args:
            data: Pattern dictionary
        
        Returns:
            PatternMetadata instance
        """
        # Handle category conversion
        category = data.get('category')
        if isinstance(category, str):
            category = PatternCategory(category)
        
        # Handle detection rules
        detection_rules_data = data.get('detection_rules')
        detection_rules = None
        if detection_rules_data:
            rule_type = detection_rules_data.get('type')
            if isinstance(rule_type, str):
                rule_type = DetectionRuleType(rule_type)
            detection_rules = DetectionRule(
                type=rule_type,
                confidence_threshold=detection_rules_data.get('confidence_threshold', 0.75),
                ast_patterns=detection_rules_data.get('ast_patterns', []),
                semantic_rules=detection_rules_data.get('semantic_rules', [])
            )
        
        return PatternMetadata(
            id=data['id'],
            name=data['name'],
            category=category,
            description=data.get('description', ''),
            use_cases=data.get('use_cases', []),
            constraints=data.get('constraints', []),
            impact_score=data.get('impact_score', 5.0),
            effort_score=data.get('effort_score', 5.0),
            tags=data.get('tags', []),
            related_patterns=data.get('related_patterns', []),
            custom_metadata=data.get('custom_metadata', {}),
            detection_rules=detection_rules,
            created_at=data.get('created_at', datetime.utcnow().isoformat()),
            updated_at=data.get('updated_at', datetime.utcnow().isoformat()),
            author=data.get('author', ''),
            version=data.get('version', '1.0')
        )


# AC_COMPLETE: AC-PHASE60.0-S1-001 ✅
# ✅ Pattern registry with YAML/JSON loading
# ✅ Schema validation with jsonschema
# ✅ Pattern metadata management
# ✅ Category and tag-based queries
# ✅ Export to YAML/JSON
