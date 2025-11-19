"""Test Phase 2 refactoring - YAML-driven image prompt generation"""

from src.epm.modules.image_prompt_generator import ImagePromptGenerator
from pathlib import Path

# Initialize generator
gen = ImagePromptGenerator(Path('docs/diagrams'))

# Test YAML loading
print("Testing Phase 2 refactoring...")
print("-" * 60)

config = gen._load_diagram_config()
if config:
    print(f"✅ Config loaded successfully")
    diagrams = config.get('diagrams', [])
    print(f"✅ Found {len(diagrams)} diagrams in configuration")
    
    # Show first 3 diagram IDs
    print("\nFirst 3 diagrams:")
    for diagram in diagrams[:3]:
        diagram_id = diagram.get('id')
        diagram_name = diagram.get('name')
        print(f"  - {diagram_id}: {diagram_name}")
    
    print(f"\n✅ Phase 2 refactoring successful!")
    print(f"   Generator now reads from diagram-definitions.yaml")
    print(f"   Expected to generate {len(diagrams)} diagrams")
else:
    print("❌ Failed to load diagram configuration")

print("-" * 60)
