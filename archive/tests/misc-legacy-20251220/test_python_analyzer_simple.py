"""
Simple test for Python analyzer integration.
"""

from pathlib import Path
from src.dashboard.analyzers.python_analyzer import PythonAnalyzer

def main():
    print("Testing PythonAnalyzer...")
    
    analyzer = PythonAnalyzer()
    test_file = Path(__file__)  # Test on self
    
    try:
        result = analyzer.analyze(test_file)
        
        print(f"\n[PASS] Analysis completed")
        print(f"  - File: {result.file_path}")
        print(f"  - Language: {result.language}")
        print(f"  - Classes: {len(result.classes)}")
        print(f"  - Methods: {len(result.methods)}")
        print(f"  - Dependencies: {len(result.dependencies)}")
        print(f"  - Errors: {len(result.errors)}")
        
        if result.errors:
            print("\n[ERRORS]")
            for error in result.errors:
                print(f"  - {error}")
        
        print("\n[SUCCESS] Python analyzer working correctly!")
        return 0
        
    except Exception as e:
        print(f"\n[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    exit(main())
