#!/usr/bin/env python3
"""
YAML Validator for CORTEX Knowledge Base

Validates knowledge YAML files against schema requirements.
Ensures metadata completeness, pattern structure, and references.
"""

import sys
from pathlib import Path
from typing import Dict, List, Any
import yaml


class YAMLValidator:
    """Validates CORTEX knowledge YAML files."""
    
    REQUIRED_METADATA_FIELDS = [
        "domain",
        "version",
        "source",
        "authority",
        "date",
        "description",
        "tags"
    ]
    
    def __init__(self, knowledge_dir: Path):
        self.knowledge_dir = knowledge_dir
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate_all(self) -> bool:
        """Validate all YAML files in knowledge directory."""
        yaml_files = list(self.knowledge_dir.rglob("*.yaml"))
        yaml_files = [f for f in yaml_files if f.name != "INDEX.yaml"]
        
        print(f"🔍 Validating {len(yaml_files)} knowledge YAMLs...")
        
        success_count = 0
        for yaml_file in yaml_files:
            if self.validate_file(yaml_file):
                success_count += 1
        
        print(f"\n✅ {success_count}/{len(yaml_files)} YAMLs valid")
        
        if self.errors:
            print(f"\n❌ {len(self.errors)} errors found:")
            for error in self.errors[:10]:  # Show first 10
                print(f"  - {error}")
        
        if self.warnings:
            print(f"\n⚠️  {len(self.warnings)} warnings:")
            for warning in self.warnings[:5]:  # Show first 5
                print(f"  - {warning}")
        
        return len(self.errors) == 0
    
    def validate_file(self, yaml_file: Path) -> bool:
        """Validate single YAML file."""
        try:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if not data:
                self.errors.append(f"{yaml_file.name}: Empty YAML")
                return False
            
            # Validate structure
            self.validate_metadata(yaml_file, data)
            self.validate_content(yaml_file, data)
            self.validate_references(yaml_file, data)
            
            return True
            
        except yaml.YAMLError as e:
            self.errors.append(f"{yaml_file.name}: YAML syntax error: {e}")
            return False
        except Exception as e:
            self.errors.append(f"{yaml_file.name}: Validation error: {e}")
            return False
    
    def validate_metadata(self, yaml_file: Path, data: Dict[str, Any]):
        """Validate metadata section."""
        if "metadata" not in data:
            self.errors.append(f"{yaml_file.name}: Missing 'metadata' section")
            return
        
        metadata = data["metadata"]
        
        for field in self.REQUIRED_METADATA_FIELDS:
            if field not in metadata:
                self.errors.append(f"{yaml_file.name}: Missing metadata.{field}")
            elif not metadata[field]:
                self.errors.append(f"{yaml_file.name}: Empty metadata.{field}")
        
        # Validate version format
        if "version" in metadata:
            version = metadata["version"]
            if not isinstance(version, str) or not version.count('.') == 2:
                self.warnings.append(f"{yaml_file.name}: version should be semver (e.g., '1.0.0')")
        
        # Validate tags is list
        if "tags" in metadata:
            if not isinstance(metadata["tags"], list):
                self.errors.append(f"{yaml_file.name}: metadata.tags must be list")
            elif len(metadata["tags"]) == 0:
                self.warnings.append(f"{yaml_file.name}: metadata.tags is empty")
    
    def validate_content(self, yaml_file: Path, data: Dict[str, Any]):
        """Validate main content sections."""
        # At least one of these sections should exist
        content_sections = ["patterns", "anti_patterns", "best_practices", "security_controls"]
        
        has_content = any(section in data for section in content_sections)
        
        if not has_content:
            self.warnings.append(f"{yaml_file.name}: No content sections (patterns/anti_patterns/best_practices)")
    
    def validate_references(self, yaml_file: Path, data: Dict[str, Any]):
        """Validate references section if present."""
        if "references" not in data:
            self.warnings.append(f"{yaml_file.name}: No references section")
            return
        
        references = data["references"]
        if not isinstance(references, list):
            self.errors.append(f"{yaml_file.name}: references must be list")
            return
        
        for idx, ref in enumerate(references):
            if not isinstance(ref, dict):
                self.errors.append(f"{yaml_file.name}: references[{idx}] must be dict")
                continue
            
            if "name" not in ref:
                self.errors.append(f"{yaml_file.name}: references[{idx}] missing 'name'")
            if "url" not in ref:
                self.errors.append(f"{yaml_file.name}: references[{idx}] missing 'url'")
            elif not ref["url"].startswith(("http://", "https://")):
                self.errors.append(f"{yaml_file.name}: references[{idx}] URL must start with http(s)")


def main():
    """Main entry point."""
    knowledge_dir = Path(__file__).parent.parent.parent / "knowledge" / "best-practices"
    
    if not knowledge_dir.exists():
        print(f"❌ Knowledge directory not found: {knowledge_dir}")
        sys.exit(1)
    
    validator = YAMLValidator(knowledge_dir)
    success = validator.validate_all()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
