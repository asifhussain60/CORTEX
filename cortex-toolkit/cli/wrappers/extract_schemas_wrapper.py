#!/usr/bin/env python3
"""
CORTEX Toolkit - Extract Schemas CLI Wrapper
CLI wrapper for schema extraction from C# entities.

Author: Asif Hussain
GitHub: github.com/asifhussain60/CORTEX
Version: 1.0.0
"""

import sys
import argparse
from pathlib import Path

# Add toolkit to path
TOOLKIT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(TOOLKIT_ROOT))

from core.generators.schema_extractor import SchemaExtractor


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Extract OpenAPI schemas from C# entity classes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract schemas from C# file
  python extract_schemas_wrapper.py path/to/Entities.cs
  
  # Specify output directory and format
  python extract_schemas_wrapper.py path/to/Entities.cs \\
    --output-dir ./schemas --format yaml
  
  # Use registry for deduplication
  python extract_schemas_wrapper.py path/to/Entities.cs \\
    --registry schema-registry.json
        """
    )
    
    parser.add_argument(
        "source_file",
        help="Path to C# source file containing entity definitions"
    )
    parser.add_argument(
        "--output-dir",
        default="./schemas",
        help="Output directory for schema JSON/YAML files (default: ./schemas)"
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
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Validate source file
    source_file = Path(args.source_file)
    if not source_file.exists():
        print(f"❌ Error: Source file not found: {source_file}")
        return 1
    
    if not source_file.suffix == ".cs":
        print(f"⚠️  Warning: File does not have .cs extension: {source_file}")
    
    # Initialize extractor
    try:
        extractor = SchemaExtractor(
            source_file=source_file,
            output_dir=Path(args.output_dir),
            format=args.format,
            registry_path=Path(args.registry) if args.registry else None
        )
        
        print(f"🔍 Extracting schemas from: {source_file.name}")
        print(f"📁 Output directory: {extractor.output_dir}")
        print(f"📄 Format: {args.format.upper()}\n")
        
        # Extract schemas
        schemas = extractor.extract()
        
        # Report results
        print(f"✅ Successfully extracted {len(schemas)} schema(s):")
        for schema_name in sorted(schemas.keys()):
            schema = schemas[schema_name]
            prop_count = len(schema.get("properties", {}))
            required_count = len(schema.get("required", []))
            print(f"   📦 {schema_name}")
            print(f"      └─ {prop_count} properties ({required_count} required)")
            
            if args.verbose and schema.get("properties"):
                print(f"      └─ Properties:")
                for prop_name, prop_def in list(schema["properties"].items())[:5]:
                    prop_type = prop_def.get("type", "object")
                    if "$ref" in prop_def:
                        ref_name = prop_def["$ref"].split("/")[-1]
                        print(f"         • {prop_name}: {ref_name} (reference)")
                    else:
                        print(f"         • {prop_name}: {prop_type}")
                
                if len(schema["properties"]) > 5:
                    remaining = len(schema["properties"]) - 5
                    print(f"         ... and {remaining} more")
        
        print(f"\n📂 Output files:")
        print(f"   • {extractor.output_dir / f'{source_file.stem}_schemas.{args.format}'}")
        for schema_name in schemas:
            print(f"   • {extractor.output_dir / f'{schema_name}.{args.format}'}")
        
        print(f"\n🎉 Schema extraction complete!")
        return 0
        
    except Exception as e:
        print(f"\n❌ Error during schema extraction:")
        print(f"   {str(e)}")
        
        if args.verbose:
            import traceback
            print(f"\n📋 Stack trace:")
            traceback.print_exc()
        
        return 1


if __name__ == "__main__":
    sys.exit(main())
