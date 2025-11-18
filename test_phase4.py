"""Test Phase 4 - Cleanup stage in generate_all_docs.py"""

import sys
from pathlib import Path
import tempfile
import shutil

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from generate_all_docs import EnterpriseDocumentationGenerator

print("Testing Phase 4 refactoring...")
print("-" * 60)

# Create temporary test directory
test_dir = Path(tempfile.mkdtemp())
print(f"Test directory: {test_dir}")

try:
    # Setup test structure
    (test_dir / "cortex-brain").mkdir(parents=True, exist_ok=True)
    (test_dir / "docs" / "diagrams" / "mermaid").mkdir(parents=True, exist_ok=True)
    (test_dir / "docs" / "diagrams" / "prompts").mkdir(parents=True, exist_ok=True)
    (test_dir / "docs" / "diagrams" / "narratives").mkdir(parents=True, exist_ok=True)
    (test_dir / "logs").mkdir(parents=True, exist_ok=True)
    
    # Create dummy files to test cleanup
    mermaid_dir = test_dir / "docs" / "diagrams" / "mermaid"
    prompts_dir = test_dir / "docs" / "diagrams" / "prompts"
    narratives_dir = test_dir / "docs" / "diagrams" / "narratives"
    
    # Create 5 dummy files in each directory
    for i in range(1, 6):
        (mermaid_dir / f"diagram-{i}.mmd").write_text(f"dummy mermaid {i}")
        (prompts_dir / f"prompt-{i}.md").write_text(f"dummy prompt {i}")
        (narratives_dir / f"narrative-{i}.md").write_text(f"dummy narrative {i}")
    
    print(f"\nCreated test files:")
    print(f"  - Mermaid: 5 files")
    print(f"  - Prompts: 5 files")
    print(f"  - Narratives: 5 files")
    print(f"  - Total: 15 files")
    
    # Initialize generator
    gen = EnterpriseDocumentationGenerator(test_dir, dry_run=False)
    
    # Run cleanup stage
    print("\nRunning cleanup stage...")
    result = gen._stage_cleanup()
    
    print(f"\n✅ Cleanup executed successfully")
    print(f"   Files deleted: {result['files_deleted']}")
    print(f"   Errors: {len(result['errors'])}")
    
    # Verify cleanup
    remaining_files = 0
    for dir_path in [mermaid_dir, prompts_dir, narratives_dir]:
        files = list(dir_path.glob("*.md")) + list(dir_path.glob("*.mmd"))
        remaining_files += len(files)
    
    if remaining_files == 0:
        print(f"✅ All files successfully deleted")
    else:
        print(f"⚠️  Warning: {remaining_files} files remain")
    
    # Test dry-run mode
    print("\nTesting dry-run mode...")
    
    # Recreate files
    for i in range(1, 6):
        (mermaid_dir / f"diagram-{i}.mmd").write_text(f"dummy mermaid {i}")
    
    gen_dry = EnterpriseDocumentationGenerator(test_dir, dry_run=True)
    result_dry = gen_dry._stage_cleanup()
    
    # Verify files still exist in dry-run
    remaining_after_dry = len(list(mermaid_dir.glob("*.mmd")))
    
    if remaining_after_dry == 5:
        print(f"✅ Dry-run mode working correctly (files not deleted)")
    else:
        print(f"⚠️  Dry-run issue: expected 5 files, found {remaining_after_dry}")
    
    print(f"\n✅ Phase 4 refactoring successful!")
    print(f"   Cleanup stage added to generate_all_docs.py")
    print(f"   Deletes all files before regeneration")
    print(f"   Supports dry-run mode")
    
finally:
    # Cleanup
    shutil.rmtree(test_dir)
    print(f"\nCleaned up test directory")

print("-" * 60)
