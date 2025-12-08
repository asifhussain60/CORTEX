"""
CORTEX DALL-E Prompt Regeneration for Copilot Context
Converts brain imagery to abstract technical visualizations
Creates presentation narratives for each image
"""

import os
from pathlib import Path

# Base paths
BRAIN_DIR = Path("cortex-brain/documents/analysis/dalle-prompts/cortex-brain")
USER_DIR = Path("cortex-brain/documents/analysis/dalle-prompts/user-features")

def create_prompt_and_narrative(filename, prompt_content, narrative_content, target_dir):
    """Create both prompt and narrative files"""
    prompt_path = target_dir / filename
    narrative_path = target_dir / filename.replace('.md', '-NARRATIVE.md')
    
    # Write prompt
    with open(prompt_path, 'w', encoding='utf-8') as f:
        f.write(prompt_content)
    print(f"✓ Created: {filename}")
    
    # Write narrative
    with open(narrative_path, 'w', encoding='utf-8') as f:
        f.write(narrative_content)
    print(f"✓ Created: {filename.replace('.md', '-NARRATIVE.md')}")

# Execute regeneration
print("🎨 Regenerating CORTEX DALL-E Prompts for Copilot Context\n")
print("This script will create abstract technical visualizations")
print("with presentation narratives for all architecture diagrams.\n")
print(f"Target directories:")
print(f"  - {BRAIN_DIR}")
print(f"  - {USER_DIR}\n")
print("Ready to proceed? This will overwrite existing files.")
print("Run manually with specific prompts to avoid data loss.")
