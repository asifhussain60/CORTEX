"""
Test Benchmarking System

Quick test of the collection validation with current repository data.

Author: Asif Hussain
"""

from pathlib import Path
from src.orchestrators.dashboard_validation import CollectionValidator
from src.dashboard_config import get_config

def test_benchmarking():
    """Test validation on existing repositories"""
    config = get_config()
    validator = CollectionValidator()
    
    repos_path = config.get_path('repos')
    
    if not repos_path.exists():
        print(f"❌ Repos path not found: {repos_path}")
        return
    
    print("=" * 70)
    print("CORTEX Dashboard Collection Validation Test")
    print("=" * 70)
    print()
    
    for repo_dir in repos_path.iterdir():
        if not repo_dir.is_dir() or repo_dir.name.startswith('.'):
            continue
        
        print(f"\n📁 Repository: {repo_dir.name}")
        print("-" * 70)
        
        validation = validator.validate_collection(repo_dir)
        
        # Summary
        print(validator.format_validation_summary(validation))
        
        # Details
        if validation["details"]:
            print()
            for file_type, details in validation["details"].items():
                status_icon = {
                    "passed": "✅",
                    "warning": "⚠️ ",
                    "failed": "❌"
                }.get(details["status"], "❓")
                
                print(f"  {status_icon} {file_type}.json: {details['size']:,} bytes ({details['percentage_of_target']}% of target)")
        
        print()

if __name__ == "__main__":
    test_benchmarking()
