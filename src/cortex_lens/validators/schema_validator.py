"""
Schema Validator

Validates analysis data against universal schema.
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)


class SchemaValidator:
    """
    Validate analysis data against schema
    
    Ensures data quality and completeness.
    """
    
    def validate(
        self,
        data: Dict[str, Any],
        classification: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate data against universal schema
        
        Args:
            data: Analysis data
            classification: Classification results
            
        Returns:
            {
                'valid': bool,
                'errors': [...],
                'warnings': [...],
                'completeness': float
            }
        """
        logger.info("Validating data...")
        
        errors = []
        warnings = []
        
        # Check required sections
        required_sections = ['metadata', 'classification']
        for section in required_sections:
            if section not in data:
                errors.append(f"Missing required section: {section}")
        
        # Check metadata fields
        if 'metadata' in data:
            metadata = data['metadata']
            required_fields = ['repo_name', 'repo_type', 'scan_timestamp', 'cortex_version']
            for field in required_fields:
                if field not in metadata:
                    errors.append(f"Missing metadata field: {field}")
        
        # Check classification
        if 'classification' in data:
            classification_data = data['classification']
            if 'primary_type' not in classification_data:
                errors.append("Missing classification.primary_type")
            if 'confidence' not in classification_data:
                warnings.append("Missing classification.confidence")
        
        # Calculate completeness
        total_sections = 8  # metadata, classification, architecture, entities, metrics, security, comments, narrative
        present_sections = sum(1 for section in [
            'metadata', 'classification', 'architecture', 'entities',
            'metrics', 'security', 'comments', 'narrative'
        ] if section in data and data[section])
        
        completeness = (present_sections / total_sections) * 100
        
        is_valid = len(errors) == 0
        
        result = {
            'valid': is_valid,
            'errors': errors,
            'warnings': warnings,
            'completeness': completeness,
            'sections_present': present_sections,
            'total_sections': total_sections
        }
        
        if is_valid:
            logger.info(f"✅ Validation passed (completeness: {completeness:.1f}%)")
        else:
            logger.warning(f"❌ Validation failed: {len(errors)} errors, {len(warnings)} warnings")
        
        return result
