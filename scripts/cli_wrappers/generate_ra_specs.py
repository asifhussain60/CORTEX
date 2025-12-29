"""
CLI Wrapper for Legacy Specification Generator

Orchestrates the generation of PM/BA specifications from legacy C# code.
Stores CORTEX tooling in CORTEX repo, outputs to Platform.Classic.

Author: CORTEX
Version: 1.0.0
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parents[2] / 'src'))

from operations.modules.generators.legacy_spec_generator import LegacySpecGenerator


def main():
    """Generate specifications for RA legacy APIs."""
    
    print("="*70)
    print("🧠 CORTEX Legacy API Specification Generator")
    print("="*70)
    print()
    
    # Define the files to process
    platform_classic = Path(r"C:\PROJECTS\Platform.Classic")
    output_base = platform_classic / "cortex" / "ra-api-specs" / "specifications"
    
    apis_to_document = [
        {
            'name': 'Updater_CreateRAFundingInvoices',
            'file': platform_classic / "Segment4" / "Updaters" / "Updater_CreateRAFundingInvoices.cs",
            'output': output_base / "updater-createrafundinginvoices"
        },
        {
            'name': 'XGenerateFundingInvoice',
            'file': platform_classic / "Segment4" / "HETransactions" / "XGenerateFundingInvoice.cs",
            'output': output_base / "xgeneratefundinginvoice"
        }
    ]
    
    results = []
    
    for api in apis_to_document:
        print(f"🎭 Processing: {api['name']}")
        print(f"   Source: {api['file']}")
        print(f"   Output: {api['output']}")
        print()
        
        if not api['file'].exists():
            print(f"   ❌ File not found: {api['file']}")
            results.append({'name': api['name'], 'status': 'NOT_FOUND'})
            continue
        
        try:
            # Create generator
            generator = LegacySpecGenerator(api['file'], api['output'])
            
            # Analyze
            generator.analyze()
            
            # Generate all docs
            generator.generate_all()
            
            results.append({
                'name': api['name'],
                'status': 'SUCCESS',
                'methods': len(generator.methods),
                'rules': len(generator.business_rules),
                'validations': len(generator.validations),
                'db_ops': len(generator.db_operations)
            })
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results.append({'name': api['name'], 'status': 'ERROR', 'error': str(e)})
        
        print()
    
    # Print summary
    print("="*70)
    print("📊 Generation Summary")
    print("="*70)
    
    for result in results:
        if result['status'] == 'SUCCESS':
            print(f"✅ {result['name']}")
            print(f"   Methods: {result['methods']}")
            print(f"   Business Rules: {result['rules']}")
            print(f"   Validations: {result['validations']}")
            print(f"   DB Operations: {result['db_ops']}")
        elif result['status'] == 'NOT_FOUND':
            print(f"❌ {result['name']} - File not found")
        else:
            print(f"❌ {result['name']} - Error: {result.get('error', 'Unknown')}")
        print()
    
    print("="*70)
    print("🎉 Specification generation complete!")
    print("="*70)
    print()
    print("📁 Output Location: C:\\PROJECTS\\Platform.Classic\\cortex\\ra-api-specs\\specifications\\")
    print()
    print("Next Steps:")
    print("1. Review generated business-spec.md files")
    print("2. Run validation tools from Platform.Classic\\cortex\\ra-api-specs\\tools\\")
    print("3. Schedule PM/BA review sessions")
    print()


if __name__ == '__main__':
    main()
