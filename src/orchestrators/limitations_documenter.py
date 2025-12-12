"""
Limitations Documentation Template - Feature 7
Standardizes blocker and constraint documentation across orchestrators

This module provides a framework for documenting orchestrator limitations
in a consistent YAML-based format, enabling better troubleshooting and
knowledge management across the CORTEX system.

Key Features:
    - YAML-based templates for consistency
    - Auto-generation from phase metadata
    - Comprehensive validation against schema
    - Integration hooks for all orchestrators
    - Three limitation types: blockers, constraints, workarounds

Author: Asif Hussain
GitHub: github.com/asifhussain60/CORTEX
Version: 1.0.0
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Any
import yaml


class LimitationType(Enum):
    """
    Types of limitations in CORTEX orchestrators
    
    Categorizes limitations to enable consistent documentation
    and appropriate handling strategies.
    
    Values:
        BLOCKER: Complete prevention of functionality (highest priority)
        CONSTRAINT: Limitation that reduces effectiveness (medium priority)
        WORKAROUND: Known solution to circumvent issue (informational)
    """
    BLOCKER = "blocker"
    CONSTRAINT = "constraint"
    WORKAROUND = "workaround"


@dataclass
class LimitationEntry:
    """
    Single limitation entry
    
    Represents a documented limitation with its associated metadata.
    Supports conversion to dictionary format for YAML serialization.
    
    Attributes:
        type: Type of limitation (blocker, constraint, or workaround)
        title: Brief title describing the limitation
        description: Detailed description (optional)
        impact: Impact level (low, medium, high, critical)
        workaround: Potential workaround or mitigation strategy (optional)
    """
    type: LimitationType
    title: str
    description: str = ""
    impact: str = "medium"
    workaround: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for YAML serialization
        
        Returns:
            Dictionary representation with only non-empty fields
        """
        data = {
            'type': self.type.value,
            'title': self.title
        }
        
        if self.description:
            data['description'] = self.description
        if self.impact:
            data['impact'] = self.impact
        if self.workaround:
            data['workaround'] = self.workaround
        
        return data


@dataclass
class ValidationResult:
    """
    Result of template validation
    
    Encapsulates validation outcomes including errors and warnings.
    Used throughout the validation pipeline to track issues.
    
    Attributes:
        is_valid: Whether validation passed (no errors)
        errors: List of error messages (prevent saving)
        warnings: List of warning messages (non-blocking)
    """
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class LimitationsDocumenter:
    """
    Limitations Documentation Template - Feature 7
    
    Standardizes documentation of orchestrator limitations:
    - YAML-based templates for consistency
    - Auto-generation from phase metadata
    - Validation against schema
    - Integration hooks for all orchestrators
    """
    
    VALID_IMPACT_VALUES = ['low', 'medium', 'high', 'critical']
    VALID_TYPES = [t.value for t in LimitationType]
    
    def __init__(self, template_path: Optional[Path] = None):
        """
        Initialize limitations documenter
        
        Args:
            template_path: Path to template file (optional)
        """
        self.template_path = template_path
        self.template_data: Optional[Dict[str, Any]] = None
    
    def load_template(self) -> Dict[str, Any]:
        """
        Load YAML template from file
        
        Returns:
            Dictionary with template data
        """
        if not self.template_path or not self.template_path.exists():
            raise FileNotFoundError(f"Template file not found: {self.template_path}")
        
        with open(self.template_path, 'r') as f:
            self.template_data = yaml.safe_load(f)
        
        return self.template_data
    
    def validate_template(self) -> ValidationResult:
        """
        Validate loaded template
        
        Returns:
            ValidationResult with errors/warnings
        """
        if not self.template_data:
            if self.template_path and self.template_path.exists():
                self.load_template()
            else:
                return ValidationResult(
                    is_valid=False,
                    errors=["No template loaded"]
                )
        
        return self.validate_template_dict(self.template_data)
    
    def validate_template_dict(self, template: Dict[str, Any]) -> ValidationResult:
        """
        Validate template dictionary
        
        Args:
            template: Template data to validate
            
        Returns:
            ValidationResult with errors/warnings
        """
        errors = []
        warnings = []
        
        # Validate required fields
        errors.extend(self._validate_required_fields(template))
        
        # Validate limitations list
        if 'limitations' in template:
            if not isinstance(template['limitations'], list):
                errors.append("Field 'limitations' must be a list")
            else:
                errors.extend(self._validate_limitations_list(template['limitations']))
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def _validate_required_fields(self, template: Dict[str, Any]) -> List[str]:
        """
        Validate required template fields
        
        Args:
            template: Template dictionary
            
        Returns:
            List of error messages
        """
        errors = []
        required_fields = ['orchestrator_name', 'version', 'limitations']
        
        for field in required_fields:
            if field not in template:
                errors.append(f"Missing required field: {field}")
        
        return errors
    
    def _validate_limitations_list(self, limitations: List[Dict[str, Any]]) -> List[str]:
        """
        Validate list of limitations
        
        Args:
            limitations: List of limitation dictionaries
            
        Returns:
            List of error messages
        """
        errors = []
        
        for i, limitation in enumerate(limitations):
            lim_validation = self.validate_limitation(limitation)
            if not lim_validation.is_valid:
                for error in lim_validation.errors:
                    errors.append(f"Limitation {i}: {error}")
        
        return errors
    
    def validate_limitation(self, limitation: Dict[str, Any]) -> ValidationResult:
        """
        Validate individual limitation structure
        
        Args:
            limitation: Limitation data to validate
            
        Returns:
            ValidationResult with errors/warnings
        """
        errors = []
        warnings = []
        
        # Validate required fields and values
        errors.extend(self._validate_limitation_type(limitation))
        errors.extend(self._validate_limitation_title(limitation))
        errors.extend(self._validate_limitation_impact(limitation))
        
        # Check for optional fields
        if 'description' not in limitation:
            warnings.append("Missing optional field: description")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def _validate_limitation_type(self, limitation: Dict[str, Any]) -> List[str]:
        """
        Validate limitation type field
        
        Args:
            limitation: Limitation dictionary
            
        Returns:
            List of error messages
        """
        errors = []
        
        if 'type' not in limitation:
            errors.append("Missing required field: type")
        elif limitation['type'] not in self.VALID_TYPES:
            errors.append(f"Invalid type: {limitation['type']}. Must be one of {self.VALID_TYPES}")
        
        return errors
    
    def _validate_limitation_title(self, limitation: Dict[str, Any]) -> List[str]:
        """
        Validate limitation title field
        
        Args:
            limitation: Limitation dictionary
            
        Returns:
            List of error messages
        """
        errors = []
        
        if 'title' not in limitation:
            errors.append("Missing required field: title")
        
        return errors
    
    def _validate_limitation_impact(self, limitation: Dict[str, Any]) -> List[str]:
        """
        Validate limitation impact field
        
        Args:
            limitation: Limitation dictionary
            
        Returns:
            List of error messages
        """
        errors = []
        
        if 'impact' in limitation and limitation['impact'] not in self.VALID_IMPACT_VALUES:
            errors.append(f"Invalid impact: {limitation['impact']}. Must be one of {self.VALID_IMPACT_VALUES}")
        
        return errors
    
    def create_default_template(
        self,
        orchestrator_name: str,
        version: str = "1.0.0"
    ) -> Dict[str, Any]:
        """
        Create default template structure
        
        Args:
            orchestrator_name: Name of orchestrator
            version: Version number
            
        Returns:
            Default template dictionary
        """
        template = {
            'orchestrator_name': orchestrator_name,
            'version': version,
            'limitations': []
        }
        
        # Save if template_path is set
        if self.template_path:
            self.template_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.template_path, 'w') as f:
                yaml.dump(template, f, default_flow_style=False, sort_keys=False)
        
        return template
    
    def parse_limitations(self) -> List[LimitationEntry]:
        """
        Parse limitations from loaded template
        
        Returns:
            List of LimitationEntry objects
        """
        if not self.template_data:
            self.load_template()
        
        limitations = []
        
        for lim_data in self.template_data.get('limitations', []):
            limitation = LimitationEntry(
                type=LimitationType(lim_data['type']),
                title=lim_data['title'],
                description=lim_data.get('description', ''),
                impact=lim_data.get('impact', 'medium'),
                workaround=lim_data.get('workaround')
            )
            limitations.append(limitation)
        
        return limitations
    
    def generate_from_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate template from phase metadata
        
        Args:
            metadata: Metadata dictionary with orchestrator info and limitations
            
        Returns:
            Generated template dictionary
        """
        template = {
            'orchestrator_name': metadata.get('orchestrator_name', 'Unknown'),
            'version': metadata.get('version', '1.0.0'),
            'limitations': []
        }
        
        # Process all limitation types
        template['limitations'].extend(
            self._process_limitations_by_type(metadata.get('blockers', []), 'blocker', 'high')
        )
        template['limitations'].extend(
            self._process_limitations_by_type(metadata.get('constraints', []), 'constraint', 'medium')
        )
        template['limitations'].extend(
            self._process_limitations_by_type(metadata.get('workarounds', []), 'workaround', 'low')
        )
        
        return template
    
    def _process_limitations_by_type(
        self,
        items: List[Dict[str, Any]],
        limitation_type: str,
        default_impact: str
    ) -> List[Dict[str, Any]]:
        """
        Process limitations of a specific type
        
        Args:
            items: List of limitation items
            limitation_type: Type of limitation (blocker, constraint, workaround)
            default_impact: Default impact value
            
        Returns:
            List of processed limitation dictionaries
        """
        limitations = []
        
        for item in items:
            limitation = {
                'type': limitation_type,
                'title': item.get('title', f'Untitled {limitation_type}'),
                'description': item.get('description', ''),
                'impact': item.get('impact', default_impact)
            }
            
            # Add workaround if present
            if item.get('workaround'):
                limitation['workaround'] = item['workaround']
            
            limitations.append(limitation)
        
        return limitations
    
    def format_as_yaml(
        self,
        orchestrator_name: str,
        version: str,
        limitations: List[LimitationEntry]
    ) -> str:
        """
        Format limitations as YAML string
        
        Args:
            orchestrator_name: Orchestrator name
            version: Version number
            limitations: List of limitations
            
        Returns:
            YAML-formatted string
        """
        template = {
            'orchestrator_name': orchestrator_name,
            'version': version,
            'limitations': [lim.to_dict() for lim in limitations]
        }
        
        return yaml.dump(template, default_flow_style=False, sort_keys=False)
    
    def generate_and_save(
        self,
        metadata: Dict[str, Any],
        output_path: Path
    ) -> Path:
        """
        Generate template from metadata and save to file
        
        Args:
            metadata: Metadata dictionary
            output_path: Output file path
            
        Returns:
            Path to saved file
        """
        template = self.generate_from_metadata(metadata)
        self._save_template_to_file(template, output_path)
        return output_path
    
    def _save_template_to_file(self, template: Dict[str, Any], file_path: Path) -> None:
        """
        Save template dictionary to YAML file
        
        Args:
            template: Template dictionary
            file_path: Path to save file
        """
        # Ensure directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save to file
        with open(file_path, 'w') as f:
            yaml.dump(template, f, default_flow_style=False, sort_keys=False)
    
    def document_orchestrator_limitations(
        self,
        orchestrator_name: str,
        limitations: List[Dict[str, Any]],
        version: str = "1.0.0",
        output_dir: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Hook for orchestrators to document their limitations
        
        This is the primary integration point for orchestrators to document
        their blockers, constraints, and workarounds in a standardized format.
        
        Args:
            orchestrator_name: Name of orchestrator
            limitations: List of limitation dictionaries
            version: Version number (default: "1.0.0")
            output_dir: Optional output directory (default: cortex-brain/documents/limitations)
            
        Returns:
            Dictionary with success status and file path
            
        Example:
            >>> documenter = LimitationsDocumenter()
            >>> limitations = [
            ...     {'type': 'blocker', 'title': 'No API access', 'impact': 'high'},
            ...     {'type': 'constraint', 'title': 'Rate limited', 'impact': 'medium'}
            ... ]
            >>> result = documenter.document_orchestrator_limitations(
            ...     'TestOrchestrator', limitations
            ... )
            >>> print(result['success'])
            True
        """
        # Convert limitations to metadata format
        metadata = self._build_metadata_from_limitations(
            orchestrator_name, version, limitations
        )
        
        # Determine output path
        output_path = self._determine_output_path(orchestrator_name, output_dir)
        
        # Generate and save
        saved_path = self.generate_and_save(metadata, output_path)
        
        return {
            'success': True,
            'file_path': str(saved_path),
            'orchestrator_name': orchestrator_name
        }
    
    def _build_metadata_from_limitations(
        self,
        orchestrator_name: str,
        version: str,
        limitations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Build metadata dictionary from limitations list
        
        Args:
            orchestrator_name: Name of orchestrator
            version: Version number
            limitations: List of limitation dictionaries
            
        Returns:
            Metadata dictionary organized by limitation type
        """
        return {
            'orchestrator_name': orchestrator_name,
            'version': version,
            'blockers': [lim for lim in limitations if lim.get('type') == 'blocker'],
            'constraints': [lim for lim in limitations if lim.get('type') == 'constraint'],
            'workarounds': [lim for lim in limitations if lim.get('type') == 'workaround']
        }
    
    def _determine_output_path(
        self,
        orchestrator_name: str,
        output_dir: Optional[Path]
    ) -> Path:
        """
        Determine output file path for limitations documentation
        
        Args:
            orchestrator_name: Name of orchestrator
            output_dir: Optional output directory
            
        Returns:
            Complete path to output file
        """
        if output_dir is None:
            output_dir = Path("cortex-brain/documents/limitations")
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        filename = orchestrator_name.lower().replace(' ', '-') + '-limitations.yaml'
        return output_dir / filename
