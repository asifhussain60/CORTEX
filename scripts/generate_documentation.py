"""
Generate comprehensive documentation for CORTEX using documentation orchestrator
"""
import logging
from pathlib import Path
from src.orchestration_4_0.orchestrators.documentation.documentation_orchestrator import (
    DocumentationOrchestrator,
    DocumentationConfig
)

def main():
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger('doc_generation')
    
    logger.info("🎯 Starting CORTEX Documentation Generation")
    
    # Create orchestrator
    orchestrator = DocumentationOrchestrator(logger)
    
    # Configure documentation generation
    config = DocumentationConfig(
        source_paths=[
            Path('src/orchestration_4_0'),
            Path('src/operations'),
            Path('src/agents'),
            Path('src/tier0'),
            Path('src/tier1'),
            Path('src/tier2')
        ],
        output_dir=Path('docs/api'),
        include_private=False,
        generate_diagrams=True,
        generate_quick_ref=True,
        diagram_types=['class_hierarchy', 'phase_flow']
    )
    
    # Execute documentation generation
    logger.info("📚 Generating API documentation...")
    result = orchestrator.execute({'config': config})
    
    # Report results
    doc_result = result.get('result')
    if doc_result:
        logger.info("=" * 60)
        logger.info("📊 DOCUMENTATION GENERATION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"✅ Modules Analyzed: {doc_result.modules_analyzed}")
        logger.info(f"✅ Classes Documented: {doc_result.classes_documented}")
        logger.info(f"✅ Functions Documented: {doc_result.functions_documented}")
        logger.info(f"✅ Diagrams Generated: {doc_result.diagrams_generated}")
        logger.info(f"✅ Output Files: {len(doc_result.output_files)}")
        
        if doc_result.errors:
            logger.warning(f"⚠️ Errors: {len(doc_result.errors)}")
            for error in doc_result.errors[:5]:
                logger.warning(f"  - {error}")
        
        if doc_result.warnings:
            logger.warning(f"⚠️ Warnings: {len(doc_result.warnings)}")
            for warning in doc_result.warnings[:5]:
                logger.warning(f"  - {warning}")
        
        logger.info("=" * 60)
        logger.info(f"📁 Documentation available at: {config.output_dir}")
        logger.info("=" * 60)
    else:
        logger.error("❌ Documentation generation failed")
    
    return result

if __name__ == "__main__":
    main()
