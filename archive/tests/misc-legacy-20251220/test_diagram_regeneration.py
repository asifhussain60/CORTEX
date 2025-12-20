#!/usr/bin/env python3
"""
Test script for diagram regeneration operation

Tests:
1. Operation can be loaded from factory
2. CORTEX features can be analyzed
3. Diagrams can be generated
4. Files can be saved properly

Author: Asif Hussain
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.operations import execute_operation

def test_diagram_regeneration():
    """Test the diagram regeneration operation"""
    print("=" * 80)
    print("CORTEX Diagram Regeneration Test")
    print("=" * 80)
    
    try:
        # Execute operation
        print("\n1. Executing diagram regeneration operation...")
        report = execute_operation(
            'regenerate_diagrams',
            profile='standard',
            project_root=Path(__file__).parent.parent
        )
        
        # Check result
        if report.success:
            print("✅ Operation completed successfully!")
            print(f"\n📊 Results:")
            print(f"   - Modules executed: {len(report.modules_executed)}")
            print(f"   - Modules succeeded: {len(report.modules_succeeded)}")
            print(f"   - Total duration: {report.total_duration_seconds:.2f}s")
            
            # Check context for results
            context = report.context or {}
            print(f"   - Features analyzed: {context.get('features_analyzed', 0)}")
            print(f"   - Diagrams generated: {context.get('diagrams_generated', 0)}")
            
            files_stats = context.get('files_created', {})
            if files_stats:
                print(f"   - Mermaid files: {files_stats.get('mermaid', 0)}")
                print(f"   - Illustration prompts: {files_stats.get('prompts', 0)}")
                print(f"   - Narratives: {files_stats.get('narratives', 0)}")
                print(f"   - Total files: {files_stats.get('total_files', 0)}")
            
            if context.get('report'):
                print(f"\n📄 Report Preview:")
                print("-" * 80)
                print(context['report'][:500] + "...")
            
            print("\n✅ Test PASSED")
            return True
        else:
            print(f"❌ Operation failed")
            if report.errors:
                for error in report.errors:
                    print(f"   Error: {error}")
            print("\n❌ Test FAILED")
            return False
            
    except Exception as e:
        print(f"❌ Test exception: {e}")
        import traceback
        traceback.print_exc()
        print("\n❌ Test FAILED")
        return False

if __name__ == "__main__":
    success = test_diagram_regeneration()
    sys.exit(0 if success else 1)
