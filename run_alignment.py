"""
System Alignment Runner
Executes comprehensive system alignment validation
"""
import sys
sys.path.insert(0, 'src')

from operations.modules.admin.system_alignment_orchestrator import SystemAlignmentOrchestrator
from pathlib import Path

def main():
    """Run system alignment validation"""
    print("=== CORTEX System Alignment ===\n")
    print("Initializing orchestrator...")
    
    orchestrator = SystemAlignmentOrchestrator()
    
    print("Running alignment validation...")
    context = {}
    result = orchestrator.execute(context)
    
    print("\n=== ALIGNMENT RESULTS ===")
    
    # Access OperationResult attributes
    print(f"Success: {result.success}")
    print(f"Message: {result.message}")
    
    # Access result dictionary
    result_data = result.result if hasattr(result, 'result') else {}
    
    print(f"\nOverall Health: {result_data.get('overall_health', 'N/A')}%")
    print(f"Total Features: {result_data.get('total_features', 0)}")
    print(f"Status: {result_data.get('status', 'unknown')}")
    
    # Feature breakdown
    if 'features_by_status' in result_data:
        print(f"\nFeature Status Breakdown:")
        for status, count in result_data['features_by_status'].items():
            print(f"  {status}: {count}")
    
    # Layer scores
    if 'layer_scores' in result_data:
        print(f"\nLayer Scores:")
        for layer, score in result_data['layer_scores'].items():
            print(f"  {layer}: {score}%")
    
    # Report location
    if 'report_path' in result_data:
        print(f"\nDetailed report: {result_data['report_path']}")
    
    # Print full result for debugging
    print(f"\nFull result data keys: {list(result_data.keys())}")
    
    return result

if __name__ == '__main__':
    main()
