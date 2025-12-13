"""
Universal JSON Schema

Defines the standardized data structure for all analysis results.
"""

import json
from pathlib import Path
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class UniversalSchema:
    """
    Universal schema for repository analysis data
    
    Provides schema definition, validation, and helper methods
    for working with the standardized data format.
    """
    
    @staticmethod
    def get_schema() -> Dict[str, Any]:
        """
        Get the complete universal schema definition
        
        Returns:
            Schema dictionary with all required and optional fields
        """
        return {
            "metadata": {
                "required": True,
                "fields": {
                    "repo_name": "string",
                    "repo_type": "list[string]",
                    "scan_timestamp": "ISO8601",
                    "cortex_version": "string",
                    "languages": "dict[string, float]",
                    "total_files": "int",
                    "total_loc": "int"
                }
            },
            "classification": {
                "required": True,
                "fields": {
                    "primary_type": "string",
                    "confidence": "float",
                    "detected_patterns": "dict[string, bool]"
                }
            },
            "architecture": {
                "required": False,
                "fields": {
                    "layers": "list[Layer]",
                    "dependencies": "list[Dependency]"
                }
            },
            "entities": {
                "required": False,
                "fields": {
                    "api_endpoints": "list[Endpoint]",
                    "database_tables": "list[Table]",
                    "frontend_routes": "list[Route]",
                    "classes": "list[Class]",
                    "methods": "list[Method]"
                }
            },
            "metrics": {
                "required": False,
                "fields": {
                    "complexity": "dict",
                    "test_coverage": "dict",
                    "performance": "dict"
                }
            },
            "security": {
                "required": False,
                "fields": {
                    "vulnerabilities": "list[Vulnerability]",
                    "authentication_patterns": "list[string]"
                }
            },
            "comments": {
                "required": False,
                "fields": {
                    "extraction": "list[Comment]",
                    "regulatory_keywords": "list[string]"
                }
            },
            "narrative": {
                "required": False,
                "fields": {
                    "executive_summary": "string",
                    "key_capabilities": "list[string]",
                    "technical_highlights": "list[string]"
                }
            }
        }
    
    @staticmethod
    def create_empty() -> Dict[str, Any]:
        """
        Create an empty data structure conforming to schema
        
        Returns:
            Empty structure with all required fields initialized
        """
        return {
            "metadata": {
                "repo_name": "",
                "repo_type": [],
                "scan_timestamp": "",
                "cortex_version": "1.0.0",
                "languages": {},
                "total_files": 0,
                "total_loc": 0
            },
            "classification": {
                "primary_type": "unknown",
                "confidence": 0.0,
                "detected_patterns": {}
            },
            "architecture": {
                "layers": [],
                "dependencies": []
            },
            "entities": {
                "api_endpoints": [],
                "database_tables": [],
                "frontend_routes": [],
                "classes": [],
                "methods": []
            },
            "metrics": {
                "complexity": {},
                "test_coverage": {},
                "performance": {}
            },
            "security": {
                "vulnerabilities": [],
                "authentication_patterns": []
            },
            "comments": {
                "extraction": [],
                "regulatory_keywords": []
            },
            "narrative": {
                "executive_summary": "",
                "key_capabilities": [],
                "technical_highlights": []
            }
        }
    
    @staticmethod
    def validate(data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate data against schema
        
        Args:
            data: Data to validate
            
        Returns:
            (is_valid, list_of_errors)
        """
        schema = UniversalSchema.get_schema()
        errors = []
        
        # Check required sections
        for section_name, section_def in schema.items():
            if section_def.get("required", False):
                if section_name not in data:
                    errors.append(f"Missing required section: {section_name}")
                    continue
                
                # Check required fields within section
                fields = section_def.get("fields", {})
                for field_name in fields:
                    if field_name not in data[section_name]:
                        errors.append(
                            f"Missing required field: {section_name}.{field_name}"
                        )
        
        is_valid = len(errors) == 0
        
        if is_valid:
            logger.info("✅ Schema validation passed")
        else:
            logger.warning(f"❌ Schema validation failed: {len(errors)} errors")
            for error in errors:
                logger.warning(f"  - {error}")
        
        return is_valid, errors
    
    @staticmethod
    def to_json(data: Dict[str, Any], output_path: Path, indent: int = 2):
        """
        Export data to JSON file
        
        Args:
            data: Data to export
            output_path: Output file path
            indent: JSON indentation (default: 2)
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with output_path.open('w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        
        logger.info(f"💾 Exported JSON: {output_path}")
    
    @staticmethod
    def from_json(input_path: Path) -> Dict[str, Any]:
        """
        Load data from JSON file
        
        Args:
            input_path: Input file path
            
        Returns:
            Loaded data dictionary
        """
        with input_path.open('r', encoding='utf-8') as f:
            data = json.load(f)
        
        logger.info(f"📂 Loaded JSON: {input_path}")
        return data
    
    @staticmethod
    def to_yaml(data: Dict[str, Any], output_path: Path):
        """
        Export data to YAML file
        
        Args:
            data: Data to export
            output_path: Output file path
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed. Install with: pip install pyyaml")
            return
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with output_path.open('w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"💾 Exported YAML: {output_path}")
    
    @staticmethod
    def to_csv(data: Dict[str, Any], output_path: Path):
        """
        Export metrics data to CSV file
        
        Args:
            data: Data to export
            output_path: Output file path
        """
        import csv
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Extract flat metrics for CSV
        rows = []
        
        # Add metadata
        metadata = data.get('metadata', {})
        rows.append(['Metadata', 'Value'])
        for key, value in metadata.items():
            if not isinstance(value, (dict, list)):
                rows.append([key, str(value)])
        
        rows.append([])  # Empty row separator
        
        # Add metrics
        metrics = data.get('metrics', {})
        rows.append(['Metric', 'Value'])
        for category, values in metrics.items():
            if isinstance(values, dict):
                for key, value in values.items():
                    rows.append([f"{category}.{key}", str(value)])
        
        with output_path.open('w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(rows)
        
        logger.info(f"💾 Exported CSV: {output_path}")
