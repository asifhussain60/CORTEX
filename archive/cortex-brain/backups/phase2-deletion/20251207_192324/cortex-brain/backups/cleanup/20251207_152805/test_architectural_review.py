"""
Test script for Architectural Review Orchestrator

Tests the review orchestrator directly without CLI routing.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.operations.modules.architectural.review_orchestrator import ReviewOrchestrator


def main():
    """Test the architectural review orchestrator."""
    print("=" * 80)
    print("CORTEX Architectural Review Test")
    print("=" * 80)
    print()
    
    # Create orchestrator
    orchestrator = ReviewOrchestrator()
    
    # Execute review on CORTEX itself
    print("Executing architectural review...")
    print()
    
    result = orchestrator.execute({})
    
    # Display results
    print()
    print("=" * 80)
    print("RESULTS")
    print("=" * 80)
    print()
    
    if result.success:
        print("SUCCESS - Review completed successfully!")
        print()
        print(f"Overall Score: {result.data['overall_score']}/100")
        print(f"Sections Analyzed: {result.data['sections']}")
        print(f"Total Findings: {result.data['total_findings']}")
        print(f"  - Critical: {result.data['critical_findings']}")
        print(f"  - High: {result.data['high_findings']}")
        print()
        print(f"Full Report: {result.data['report_path']}")
        print()
        
        # Read and display summary
        report_path = Path(result.data['report_path'])
        if report_path.exists():
            print("=" * 80)
            print("REPORT PREVIEW (First 50 lines)")
            print("=" * 80)
            print()
            lines = report_path.read_text(encoding='utf-8').split('\n')
            for line in lines[:50]:
                print(line)
            
            if len(lines) > 50:
                print()
                print(f"... ({len(lines) - 50} more lines)")
                print()
                print(f"View full report: {report_path}")
    else:
        print(f"FAILED - Review failed: {result.message}")
        if 'error' in result.data:
            print(f"Error: {result.data['error']}")
    
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
