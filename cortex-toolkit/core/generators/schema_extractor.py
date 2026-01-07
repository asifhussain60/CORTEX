#!/usr/bin/env python3
"""
CORTEX Toolkit - C# Schema Extractor
Extracts OpenAPI schemas from C# entity classes using AST-based parsing.

Author: Asif Hussain
GitHub: github.com/asifhussain60/CORTEX
Version: 1.0.0
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum


class CSharpType(Enum):
    """C# type categories"""
    PRIMITIVE = "primitive"
    STRING = "string"
    DATETIME = "datetime"
    DECIMAL = "decimal"
    COLLECTION = "collection"
    OBJECT = "object"
    NULLABLE = "nullable"


@dataclass
class PropertyInfo:
    """Extracted C# property information"""
    name: str
    csharp_type: str
    is_nullable: bool = False
    is_required: bool = False
    is_collection: bool = False
    collection_item_type: Optional[str] = None
    validation_attributes: Dict[str, Any] = field(default_factory=dict)
    description: Optional[str] = None
    line_number: int = 0
    
    def to_openapi_property(self) -> Dict[str, Any]:
        """Convert to OpenAPI property definition"""
        prop = {}
        
        # Determine OpenAPI type
        openapi_type = self._get_openapi_type()
        prop.update(openapi_type)
        
        # Add description
        if self.description:
            prop["description"] = self.description
        else:
            prop["description"] = f"{self.name} property"
        
        # Add nullable
        if self.is_nullable:
            prop["nullable"] = True
        
        # Add validations from attributes
        if "Range" in self.validation_attributes:
            range_vals = self.validation_attributes["Range"]
            if "min" in range_vals:
                prop["minimum"] = range_vals["min"]
            if "max" in range_vals:
                prop["maximum"] = range_vals["max"]
        
        if "StringLength" in self.validation_attributes:
            length_vals = self.validation_attributes["StringLength"]
            if "max" in length_vals:
                prop["maxLength"] = length_vals["max"]
            if "min" in length_vals:
                prop["minLength"] = length_vals["min"]
        
        if "MinLength" in self.validation_attributes:
            prop["minLength"] = self.validation_attributes["MinLength"]
        
        if "MaxLength" in self.validation_attributes:
            prop["maxLength"] = self.validation_attributes["MaxLength"]
        
        if "RegularExpression" in self.validation_attributes:
            prop["pattern"] = self.validation_attributes["RegularExpression"]
        
        return prop
    
    def _get_openapi_type(self) -> Dict[str, Any]:
        """Map C# type to OpenAPI type"""
        type_mappings = {
            "string": {"type": "string"},
            "int": {"type": "integer", "format": "int32"},
            "long": {"type": "integer", "format": "int64"},
            "short": {"type": "integer", "format": "int16"},
            "byte": {"type": "integer", "format": "byte"},
            "float": {"type": "number", "format": "float"},
            "double": {"type": "number", "format": "double"},
            "decimal": {"type": "number", "format": "decimal"},
            "bool": {"type": "boolean"},
            "boolean": {"type": "boolean"},
            "DateTime": {"type": "string", "format": "date-time"},
            "DateTimeOffset": {"type": "string", "format": "date-time"},
            "Guid": {"type": "string", "format": "uuid"},
            "byte[]": {"type": "string", "format": "byte"},
        }
        
        # Handle collections
        if self.is_collection and self.collection_item_type:
            base_type = type_mappings.get(self.collection_item_type, {"type": "object"})
            if self.collection_item_type not in type_mappings:
                # Reference to another schema
                return {
                    "type": "array",
                    "items": {"$ref": f"#/components/schemas/{self.collection_item_type}"}
                }
            else:
                return {
                    "type": "array",
                    "items": base_type
                }
        
        # Check if it's a known primitive
        base_type = self.csharp_type.rstrip("?")
        if base_type in type_mappings:
            return type_mappings[base_type]
        
        # Default to object reference
        return {"$ref": f"#/components/schemas/{base_type}"}


@dataclass
class ClassInfo:
    """Extracted C# class information"""
    name: str
    namespace: str
    properties: List[PropertyInfo] = field(default_factory=list)
    base_class: Optional[str] = None
    implements: List[str] = field(default_factory=list)
    xml_doc: Optional[str] = None
    line_number: int = 0
    
    def to_openapi_schema(self) -> Dict[str, Any]:
        """Convert to OpenAPI schema definition"""
        schema = {
            "type": "object",
            "properties": {},
            "description": self.xml_doc or f"{self.name} entity"
        }
        
        # Add required fields
        required = [p.name for p in self.properties if p.is_required]
        if required:
            schema["required"] = required
        
        # Add properties
        for prop in self.properties:
            schema["properties"][prop.name] = prop.to_openapi_property()
        
        return schema


class SchemaExtractor:
    """
    Extracts OpenAPI schemas from C# entity classes.
    
    Features:
    - AST-based C# parsing
    - Type conversion (C# → OpenAPI)
    - Validation attribute extraction
    - Nested entity handling
    - Collection support
    - XML documentation parsing
    """
    
    def __init__(
        self,
        source_file: Path,
        output_dir: Optional[Path] = None,
        format: str = "json",
        registry_path: Optional[Path] = None
    ):
        """
        Initialize schema extractor.
        
        Args:
            source_file: Path to C# source file
            output_dir: Output directory for schemas (default: ./schemas)
            format: Output format ('json' or 'yaml')
            registry_path: Path to schema registry for deduplication
        """
        self.source_file = Path(source_file)
        self.output_dir = Path(output_dir or "./schemas")
        self.format = format
        self.registry_path = Path(registry_path) if registry_path else None
        
        self.classes: List[ClassInfo] = []
        self.schemas: Dict[str, Dict[str, Any]] = {}
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def extract(self) -> Dict[str, Dict[str, Any]]:
        """
        Extract all schemas from source file.
        
        Returns:
            Dictionary of schema_name -> OpenAPI schema
        """
        # Read source file
        if not self.source_file.exists():
            raise FileNotFoundError(f"Source file not found: {self.source_file}")
        
        # Try multiple encodings (handle copyright symbols and other special chars)
        for encoding in ['utf-8', 'utf-8-sig', 'cp1252', 'latin-1']:
            try:
                content = self.source_file.read_text(encoding=encoding)
                break
            except UnicodeDecodeError:
                if encoding == 'latin-1':  # latin-1 should always work as fallback
                    raise
                continue
        
        # Parse classes
        self.classes = self._parse_classes(content)
        
        # Convert to OpenAPI schemas
        for cls in self.classes:
            self.schemas[cls.name] = cls.to_openapi_schema()
        
        # Write output
        self._write_schemas()
        
        return self.schemas
    
    def _parse_classes(self, content: str) -> List[ClassInfo]:
        """Parse C# classes from file content"""
        classes = []
        lines = content.split('\n')
        
        # Find class definitions
        class_pattern = r'(?:public|internal|private|protected)?\s+(?:partial\s+)?class\s+(\w+)(?:\s*:\s*([^{]+))?'
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Match class declaration
            match = re.search(class_pattern, line)
            if match:
                class_name = match.group(1)
                inheritance = match.group(2) if match.group(2) else ""
                
                # Parse inheritance/implements
                base_class = None
                implements = []
                if inheritance:
                    parts = [p.strip() for p in inheritance.split(',')]
                    if parts:
                        base_class = parts[0]
                        implements = parts[1:] if len(parts) > 1 else []
                
                # Get XML doc comment
                xml_doc = self._get_xml_doc(lines, i)
                
                # Get namespace
                namespace = self._get_namespace(lines[:i])
                
                # Create class info
                cls = ClassInfo(
                    name=class_name,
                    namespace=namespace,
                    base_class=base_class,
                    implements=implements,
                    xml_doc=xml_doc,
                    line_number=i + 1
                )
                
                # Parse properties
                cls.properties = self._parse_properties(lines, i)
                
                classes.append(cls)
            
            i += 1
        
        return classes
    
    def _parse_properties(self, lines: List[str], class_start: int) -> List[PropertyInfo]:
        """Parse properties from class body"""
        properties = []
        
        # Find class body bounds
        brace_count = 0
        in_class = False
        i = class_start
        
        while i < len(lines):
            line = lines[i].strip()
            
            if '{' in line:
                brace_count += line.count('{')
                in_class = True
            
            if '}' in line:
                brace_count -= line.count('}')
                if brace_count == 0 and in_class:
                    break
            
            if in_class and brace_count == 1:
                # Look for property declarations
                prop_pattern = r'(?:public|internal|private|protected)\s+(.+?)\s+(\w+)\s*\{\s*get;.*?set;.*?\}'
                match = re.search(prop_pattern, line)
                
                if match:
                    csharp_type = match.group(1).strip()
                    prop_name = match.group(2).strip()
                    
                    # Parse type details
                    is_nullable = csharp_type.endswith('?')
                    is_collection, collection_type = self._parse_collection_type(csharp_type)
                    
                    # Get validation attributes
                    validation_attrs = self._parse_validation_attributes(lines, i)
                    
                    # Check if required
                    is_required = "Required" in validation_attrs
                    
                    # Get XML doc
                    xml_doc = self._get_xml_doc(lines, i)
                    
                    prop = PropertyInfo(
                        name=prop_name,
                        csharp_type=csharp_type.rstrip('?'),
                        is_nullable=is_nullable,
                        is_required=is_required,
                        is_collection=is_collection,
                        collection_item_type=collection_type,
                        validation_attributes=validation_attrs,
                        description=xml_doc,
                        line_number=i + 1
                    )
                    
                    properties.append(prop)
            
            i += 1
        
        return properties
    
    def _parse_collection_type(self, csharp_type: str) -> tuple[bool, Optional[str]]:
        """Parse collection type and extract item type"""
        # Handle List<T>, IList<T>, IEnumerable<T>, etc.
        collection_pattern = r'(?:List|IList|IEnumerable|ICollection|Array)<(.+?)>'
        match = re.search(collection_pattern, csharp_type)
        
        if match:
            item_type = match.group(1).strip()
            return True, item_type
        
        # Handle T[]
        if csharp_type.endswith('[]'):
            item_type = csharp_type[:-2].strip()
            return True, item_type
        
        return False, None
    
    def _parse_validation_attributes(self, lines: List[str], prop_line: int) -> Dict[str, Any]:
        """Parse validation attributes above property"""
        attributes = {}
        
        # Look backwards for attributes
        i = prop_line - 1
        while i >= 0:
            line = lines[i].strip()
            
            if not line or line.startswith('//'):
                i -= 1
                continue
            
            if not line.startswith('['):
                break
            
            # Parse attribute
            # [Required]
            if '[Required]' in line:
                attributes['Required'] = True
            
            # [Range(min, max)]
            range_match = re.search(r'\[Range\(([^,]+),\s*([^)]+)\)\]', line)
            if range_match:
                try:
                    attributes['Range'] = {
                        'min': float(range_match.group(1)),
                        'max': float(range_match.group(2))
                    }
                except ValueError:
                    pass
            
            # [StringLength(max, MinimumLength = min)]
            strlen_match = re.search(r'\[StringLength\((\d+)(?:,\s*MinimumLength\s*=\s*(\d+))?\)\]', line)
            if strlen_match:
                attributes['StringLength'] = {'max': int(strlen_match.group(1))}
                if strlen_match.group(2):
                    attributes['StringLength']['min'] = int(strlen_match.group(2))
            
            # [MinLength(n)]
            minlen_match = re.search(r'\[MinLength\((\d+)\)\]', line)
            if minlen_match:
                attributes['MinLength'] = int(minlen_match.group(1))
            
            # [MaxLength(n)]
            maxlen_match = re.search(r'\[MaxLength\((\d+)\)\]', line)
            if maxlen_match:
                attributes['MaxLength'] = int(maxlen_match.group(1))
            
            # [RegularExpression("pattern")]
            regex_match = re.search(r'\[RegularExpression\("([^"]+)"\)\]', line)
            if regex_match:
                attributes['RegularExpression'] = regex_match.group(1)
            
            i -= 1
        
        return attributes
    
    def _get_xml_doc(self, lines: List[str], target_line: int) -> Optional[str]:
        """Extract XML documentation comment"""
        docs = []
        i = target_line - 1
        
        while i >= 0:
            line = lines[i].strip()
            
            if line.startswith('///'):
                # Extract summary content
                summary_match = re.search(r'<summary>(.+?)</summary>', line)
                if summary_match:
                    docs.insert(0, summary_match.group(1).strip())
                else:
                    # Just the comment text
                    comment_text = line.replace('///', '').strip()
                    if comment_text and not comment_text.startswith('<'):
                        docs.insert(0, comment_text)
            elif not line or line.startswith('['):
                i -= 1
                continue
            else:
                break
            
            i -= 1
        
        return ' '.join(docs) if docs else None
    
    def _get_namespace(self, lines: List[str]) -> str:
        """Extract namespace from previous lines"""
        for line in reversed(lines):
            namespace_match = re.search(r'namespace\s+([\w.]+)', line)
            if namespace_match:
                return namespace_match.group(1)
        return "Unknown"
    
    def _write_schemas(self):
        """Write schemas to output files"""
        if self.format == "json":
            output_file = self.output_dir / f"{self.source_file.stem}_schemas.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.schemas, f, indent=2)
        elif self.format == "yaml":
            import yaml
            output_file = self.output_dir / f"{self.source_file.stem}_schemas.yaml"
            with open(output_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.schemas, f, default_flow_style=False, sort_keys=False)
        
        # Also write individual schema files
        for schema_name, schema_def in self.schemas.items():
            if self.format == "json":
                schema_file = self.output_dir / f"{schema_name}.json"
                with open(schema_file, 'w', encoding='utf-8') as f:
                    json.dump(schema_def, f, indent=2)
            elif self.format == "yaml":
                import yaml
                schema_file = self.output_dir / f"{schema_name}.yaml"
                with open(schema_file, 'w', encoding='utf-8') as f:
                    yaml.dump(schema_def, f, default_flow_style=False, sort_keys=False)


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Extract OpenAPI schemas from C# entity classes"
    )
    parser.add_argument(
        "source_file",
        help="Path to C# source file"
    )
    parser.add_argument(
        "--output-dir",
        default="./schemas",
        help="Output directory for schemas (default: ./schemas)"
    )
    parser.add_argument(
        "--format",
        choices=["json", "yaml"],
        default="json",
        help="Output format (default: json)"
    )
    parser.add_argument(
        "--registry",
        help="Path to schema registry file for deduplication"
    )
    
    args = parser.parse_args()
    
    extractor = SchemaExtractor(
        source_file=Path(args.source_file),
        output_dir=Path(args.output_dir),
        format=args.format,
        registry_path=Path(args.registry) if args.registry else None
    )
    
    try:
        schemas = extractor.extract()
        print(f"✅ Extracted {len(schemas)} schemas:")
        for schema_name in schemas:
            print(f"   - {schema_name}")
        print(f"\n📁 Output: {extractor.output_dir}")
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
