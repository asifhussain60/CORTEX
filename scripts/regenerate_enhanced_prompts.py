"""
Regenerate All Enhanced Image Prompts and Narratives

This script regenerates all enhanced image generation prompts and narratives
using the EnhancedImagePromptGenerator. It creates professional, cinematic
prompts for DALL-E 3 and Gemini image generators.

Usage:
    python scripts/regenerate_enhanced_prompts.py

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sys
from pathlib import Path
import logging
import importlib.util

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Direct import to avoid dependency chain issues
def import_enhanced_generator():
    """Directly import the enhanced generator module"""
    module_path = PROJECT_ROOT / "src" / "epm" / "modules" / "image_prompt_generator_enhanced.py"
    spec = importlib.util.spec_from_file_location("image_prompt_generator_enhanced", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.EnhancedImagePromptGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main execution function"""
    logger.info("=" * 80)
    logger.info("CORTEX Enhanced Prompt & Narrative Regeneration")
    logger.info("=" * 80)
    logger.info("")
    
    try:
        # Import the enhanced generator
        EnhancedImagePromptGenerator = import_enhanced_generator()
        
        # Initialize the enhanced generator
        output_dir = PROJECT_ROOT / 'docs' / 'diagrams'
        logger.info(f"Output directory: {output_dir}")
        
        generator = EnhancedImagePromptGenerator(output_dir=str(output_dir))
        
        logger.info("")
        logger.info("Generating enhanced tier architecture diagram...")
        logger.info("-" * 80)
        
        # Generate the enhanced tier architecture prompt and narrative
        result = generator.generate_enhanced_tier_architecture()
        
        logger.info("")
        logger.info("✅ Generation Complete!")
        logger.info("")
        logger.info("Results:")
        logger.info(f"  - Diagram ID: {result['id']}")
        logger.info(f"  - Status: {result['status']}")
        logger.info(f"  - Prompt saved to: {result['prompt_path']}")
        logger.info(f"  - Narrative saved to: {result['narrative_path']}")
        logger.info("")
        
        # Display directory structure
        prompts_dir = Path(result['prompt_path']).parent
        narratives_dir = Path(result['narrative_path']).parent
        
        logger.info("Directory Structure:")
        logger.info(f"  📁 {output_dir}/")
        logger.info(f"    📁 prompts/")
        for prompt_file in sorted(prompts_dir.glob("*.md")):
            logger.info(f"      📄 {prompt_file.name}")
        logger.info(f"    📁 narratives/")
        for narrative_file in sorted(narratives_dir.glob("*.md")):
            logger.info(f"      📄 {narrative_file.name}")
        logger.info(f"    📁 generated/ (awaiting AI generation)")
        logger.info("")
        
        logger.info("=" * 80)
        logger.info("Next Steps:")
        logger.info("=" * 80)
        logger.info("")
        logger.info("1. Review the generated prompts in:")
        logger.info(f"   {prompts_dir}")
        logger.info("")
        logger.info("2. Use DALL-E 3 or Gemini to generate images from prompts")
        logger.info("")
        logger.info("3. Save generated images to:")
        logger.info(f"   {output_dir / 'generated'}/")
        logger.info("")
        logger.info("4. Review narratives for documentation context:")
        logger.info(f"   {narratives_dir}")
        logger.info("")
        logger.info("=" * 80)
        
        return 0
        
    except Exception as e:
        logger.error("")
        logger.error("❌ Error during generation:")
        logger.error(f"   {str(e)}")
        logger.error("")
        import traceback
        logger.error(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(main())
