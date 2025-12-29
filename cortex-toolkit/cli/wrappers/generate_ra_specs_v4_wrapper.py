#!/usr/bin/env python3
"""
CORTEX Toolkit - Generate RA Specs v4 CLI Wrapper
CLI wrapper for production-ready OpenAPI specification generation.

Author: Asif Hussain
GitHub: github.com/asifhussain60/CORTEX
Version: 4.0.0
"""

import sys
import argparse
from pathlib import Path

# Add toolkit to path
TOOLKIT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(TOOLKIT_ROOT))

from core.generators.openapi_generator_v4 import OpenAPIGeneratorV4


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Generate production-ready OpenAPI specifications (v4)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate spec with defaults
  python generate_ra_specs_v4_wrapper.py \\
    path/to/XUpdateFundingBatch.cs \\
    --output-dir ./specs/xupdatefundingbatch
  
  # Generate with custom security and no health endpoints
  python generate_ra_specs_v4_wrapper.py \\
    path/to/XGenerateFundingInvoice.cs \\
    --output-dir ./specs/xgeneratefundinginvoice \\
    --security oauth2-authorization-code \\
    --no-health-endpoints
        """
    )
    
    parser.add_argument(
        "legacy_file",
        help="Path to legacy C# file"
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Output directory for specification and schemas"
    )
    parser.add_argument(
        "--security",
        default="oauth2-client-credentials",
        choices=[
            "oauth2-client-credentials",
            "oauth2-authorization-code",
            "jwt-bearer",
            "api-key-header"
        ],
        help="Security template (default: oauth2-client-credentials)"
    )
    parser.add_argument(
        "--no-health-endpoints",
        action="store_true",
        help="Exclude /health and /ready endpoints"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Validate legacy file
    legacy_file = Path(args.legacy_file)
    if not legacy_file.exists():
        print(f"❌ Error: Legacy file not found: {legacy_file}")
        return 1
    
    if not legacy_file.suffix == ".cs":
        print(f"⚠️  Warning: File does not have .cs extension: {legacy_file}")
    
    # Initialize generator
    try:
        generator = OpenAPIGeneratorV4(
            legacy_file=legacy_file,
            output_dir=Path(args.output_dir),
            security_template=args.security,
            include_health_endpoints=not args.no_health_endpoints
        )
        
        print(f"🚀 CORTEX OpenAPI Generator v4.0")
        print(f"=" * 60)
        print(f"📄 Legacy File: {legacy_file.name}")
        print(f"📁 Output Dir: {generator.output_dir}")
        print(f"🔐 Security: {args.security}")
        print(f"🏥 Health Endpoints: {'No' if args.no_health_endpoints else 'Yes'}")
        print(f"=" * 60)
        print()
        
        # Generate specification
        print(f"⚙️  Phase 1: Extracting schemas from C# entities...")
        spec = generator.generate()
        
        # Report results
        schemas_count = len(spec["components"]["schemas"])
        paths_count = len(spec["paths"])
        operations_count = sum(len(methods) for methods in spec["paths"].values())
        
        print(f"✅ Phase 1 Complete: {schemas_count} schemas extracted")
        print()
        print(f"⚙️  Phase 2: Building OpenAPI specification...")
        print(f"✅ Phase 2 Complete: {paths_count} paths, {operations_count} operations")
        print()
        print(f"⚙️  Phase 3: Adding security schemes...")
        print(f"✅ Phase 3 Complete: {args.security} configured")
        print()
        
        if not args.no_health_endpoints:
            print(f"⚙️  Phase 4: Adding enterprise features...")
            print(f"✅ Phase 4 Complete: Health endpoints added")
            print()
        
        # Summary
        print(f"=" * 60)
        print(f"🎉 OpenAPI Specification Generated Successfully!")
        print(f"=" * 60)
        print()
        print(f"📊 Statistics:")
        print(f"   • Schemas: {schemas_count}")
        print(f"   • Paths: {paths_count}")
        print(f"   • Operations: {operations_count}")
        print(f"   • Security Schemes: 1 ({args.security})")
        print(f"   • Error Responses: 5 (400, 401, 403, 404, 500)")
        print()
        
        print(f"📂 Generated Files:")
        print(f"   • openapi.yaml")
        print(f"   • openapi.json")
        print(f"   • schemas/ ({schemas_count} schema files)")
        print(f"   • schema-registry.json")
        print()
        
        if args.verbose:
            print(f"📋 Schemas:")
            for schema_name in sorted(spec["components"]["schemas"].keys()):
                schema = spec["components"]["schemas"][schema_name]
                prop_count = len(schema.get("properties", {}))
                print(f"   • {schema_name} ({prop_count} properties)")
            print()
            
            print(f"📋 Paths:")
            for path, methods in spec["paths"].items():
                for method in methods:
                    op_id = methods[method].get("operationId", "unknown")
                    print(f"   • {method.upper()} {path} ({op_id})")
            print()
        
        print(f"✨ Next Steps:")
        print(f"   1. Review: {generator.output_dir / 'openapi.yaml'}")
        print(f"   2. Validate: cortex-validate-openapi {generator.output_dir / 'openapi.yaml'}")
        print(f"   3. Test: Import into Swagger UI or Postman")
        print()
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error during specification generation:")
        print(f"   {str(e)}")
        
        if args.verbose:
            import traceback
            print(f"\n📋 Stack trace:")
            traceback.print_exc()
        
        return 1


if __name__ == "__main__":
    sys.exit(main())
