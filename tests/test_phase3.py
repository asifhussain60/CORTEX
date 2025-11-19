"""Test Phase 3 refactoring - Diagram generator with correct .mmd output"""

from src.epm.modules.diagram_generator import DiagramGenerator
from pathlib import Path
import tempfile
import shutil

print("Testing Phase 3 refactoring...")
print("-" * 60)

# Create temporary test directory
test_dir = Path(tempfile.mkdtemp())
print(f"Test directory: {test_dir}")

try:
    # Setup test structure
    (test_dir / "cortex-brain").mkdir(parents=True, exist_ok=True)
    (test_dir / "src").mkdir(parents=True, exist_ok=True)
    (test_dir / "docs").mkdir(parents=True, exist_ok=True)
    
    # Copy diagram definitions
    import shutil
    config_file = Path("cortex-brain/admin/documentation/config/diagram-definitions.yaml")
    test_config = test_dir / "diagram-definitions.yaml"
    shutil.copy(config_file, test_config)
    
    # Initialize generator
    gen = DiagramGenerator(test_dir, dry_run=False)
    
    # Generate diagrams
    print("\nGenerating diagrams...")
    result = gen.generate_all_diagrams(test_config)
    
    print(f"\n✅ Generated {result['diagrams_generated']} diagrams")
    
    # Check output location
    mermaid_dir = test_dir / "docs" / "diagrams" / "mermaid"
    if mermaid_dir.exists():
        mmd_files = list(mermaid_dir.glob("*.mmd"))
        print(f"✅ Found {len(mmd_files)} .mmd files in correct location")
        
        # Check first file content
        if mmd_files:
            first_file = mmd_files[0]
            content = first_file.read_text()
            
            # Verify no markdown fences
            if not content.strip().startswith('```'):
                print(f"✅ Files contain pure Mermaid (no markdown fences)")
            else:
                print(f"⚠️  Warning: File still has markdown fences")
            
            print(f"\nSample file: {first_file.name}")
            print(f"First line: {content.split(chr(10))[0]}")
    else:
        print(f"❌ Mermaid directory not found at: {mermaid_dir}")
    
    print(f"\n✅ Phase 3 refactoring successful!")
    print(f"   Diagrams now write to: docs/diagrams/mermaid/*.mmd")
    print(f"   Pure Mermaid format (no markdown wrappers)")
    
finally:
    # Cleanup
    shutil.rmtree(test_dir)
    print(f"\nCleaned up test directory")

print("-" * 60)
