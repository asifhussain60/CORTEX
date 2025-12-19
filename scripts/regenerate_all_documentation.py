#!/usr/bin/env python3
"""
Regenerate All Documentation for CORTEX 4.0 Migration
Generates missing documentation for all completed phases and orchestrators.

This script:
1. Documents all completed orchestrators (Execution, Documentation, TDD)
2. Generates phase documentation (Phase 2, 3, 4)
3. Updates MASTER-PLAN metrics with documentation counts
4. Validates completeness against MASTER-PLAN requirements

Author: Asif Hussain
Version: 1.0
Date: December 19, 2025
"""

import sys
import logging
from pathlib import Path
from typing import List, Dict, Tuple

# Add src to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from orchestration_4_0.orchestrators.documentation.documentation_orchestrator import (
    DocumentationOrchestrator,
    DocumentationConfig,
    DocumentationResult
)
from core.progress_tracker import update_master_plan_progress


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("doc_regeneration")


def generate_orchestrator_docs(
    orchestrator_name: str,
    source_path: Path,
    output_path: Path,
    diagram_types: List[str] = None
) -> Tuple[bool, DocumentationResult]:
    """
    Generate documentation for a single orchestrator.
    
    Args:
        orchestrator_name: Name for logging
        source_path: Path to orchestrator source code
        output_path: Path to output documentation
        diagram_types: List of diagram types to generate
    
    Returns:
        Tuple of (success, DocumentationResult)
    """
    logger.info(f"\n{'='*80}")
    logger.info(f"Generating documentation: {orchestrator_name}")
    logger.info(f"  Source: {source_path}")
    logger.info(f"  Output: {output_path}")
    logger.info(f"{'='*80}")
    
    if not source_path.exists():
        logger.error(f"❌ Source path not found: {source_path}")
        return False, None
    
    # Default diagram types if not specified
    if diagram_types is None:
        diagram_types = ["class_hierarchy", "phase_flow"]
    
    # Create config
    config = DocumentationConfig(
        source_paths=[source_path],
        output_dir=output_path,
        include_private=False,
        generate_diagrams=True,
        generate_quick_ref=True,
        diagram_types=diagram_types
    )
    
    # Execute documentation generation
    try:
        doc_orchestrator = DocumentationOrchestrator(logger=logger)
        result = doc_orchestrator.execute({'config': config})
        
        # Check if workflow is complete (BaseOrchestrator returns 'is_complete')
        if result.get('is_complete', False):
            doc_result = result.get('result')
            if not doc_result:
                # Try to get from phase_results
                phase_results = result.get('phase_results', {})
                for phase_result in phase_results.values():
                    if isinstance(phase_result, dict) and 'result' in phase_result:
                        doc_result = phase_result['result']
                        break
            
            if not doc_result:
                logger.error(f"❌ No documentation result found in orchestrator output")
                return False, None
            
            logger.info(f"✅ SUCCESS: {orchestrator_name}")
            logger.info(f"  📊 Modules analyzed: {doc_result.modules_analyzed}")
            logger.info(f"  📦 Classes documented: {doc_result.classes_documented}")
            logger.info(f"  🔧 Functions documented: {doc_result.functions_documented}")
            logger.info(f"  📈 Diagrams generated: {doc_result.diagrams_generated}")
            logger.info(f"  📄 Files created: {len(doc_result.output_files)}")
            
            if doc_result.warnings:
                logger.warning(f"  ⚠️  Warnings: {len(doc_result.warnings)}")
                for warning in doc_result.warnings[:5]:  # Show first 5
                    logger.warning(f"    - {warning}")
            
            return True, doc_result
        else:
            errors = result.get('errors', {})
            logger.error(f"❌ FAILED: {orchestrator_name}")
            logger.error(f"  Workflow incomplete. Errors: {errors}")
            return False, None
            
    except Exception as e:
        logger.error(f"❌ EXCEPTION: {orchestrator_name}")
        logger.error(f"  {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def main():
    """Main documentation regeneration workflow."""
    logger.info("\n" + "="*80)
    logger.info("CORTEX 4.0 - Documentation Regeneration")
    logger.info("="*80 + "\n")
    
    src_path = PROJECT_ROOT / "src" / "orchestration_4_0"
    docs_path = PROJECT_ROOT / "docs" / "orchestration_4_0"
    
    # Track overall results
    total_success = 0
    total_failed = 0
    total_files = 0
    
    # Define orchestrators to document
    orchestrators_to_document = [
        {
            "name": "ExecutionOrchestrator",
            "key": "execution",
            "source": src_path / "orchestrators" / "execution",
            "output": docs_path / "execution_orchestrator",
            "diagrams": ["class_hierarchy", "phase_flow"],
            "reason": "Complete missing flowchart and sequence diagrams"
        },
        {
            "name": "DocumentationOrchestrator",
            "key": "documentation",
            "source": src_path / "orchestrators" / "documentation",
            "output": docs_path / "documentation_orchestrator",
            "diagrams": ["class_hierarchy", "phase_flow"],
            "reason": "Self-documenting system (MISSING)"
        },
        {
            "name": "TDDOrchestrator v4.0",
            "key": "tdd",
            "source": src_path.parent / "orchestrators" / "tdd",  # In src/orchestrators, not src/orchestration_4_0
            "output": docs_path / "tdd_orchestrator",
            "diagrams": ["class_hierarchy", "phase_flow"],
            "reason": "Strategy pattern architecture (MISSING)"
        },
        {
            "name": "BaseOrchestrator",
            "key": "base",
            "source": src_path / "base",
            "output": docs_path / "base_framework",
            "diagrams": ["class_hierarchy"],
            "reason": "Foundation framework documentation"
        }
    ]
    
    # Generate documentation for each orchestrator
    logger.info(f"📋 Documentation targets: {len(orchestrators_to_document)}\n")
    
    for idx, orch in enumerate(orchestrators_to_document, 1):
        logger.info(f"\n[{idx}/{len(orchestrators_to_document)}] {orch['name']}")
        logger.info(f"Reason: {orch['reason']}")
        
        success, result = generate_orchestrator_docs(
            orchestrator_name=orch['name'],
            source_path=orch['source'],
            output_path=orch['output'],
            diagram_types=orch['diagrams']
        )
        
        if success:
            total_success += 1
            total_files += len(result.output_files)
        else:
            total_failed += 1
        
        # Small delay between generations
        import time
        time.sleep(0.5)
    
    # Summary
    logger.info("\n" + "="*80)
    logger.info("DOCUMENTATION REGENERATION COMPLETE")
    logger.info("="*80)
    logger.info(f"✅ Successful: {total_success}/{len(orchestrators_to_document)}")
    logger.info(f"❌ Failed: {total_failed}/{len(orchestrators_to_document)}")
    logger.info(f"📄 Total files generated: {total_files}")
    
    # Update MASTER-PLAN metrics
    if total_success > 0:
        logger.info("\n📊 Updating MASTER-PLAN.md metrics...")
        
        # Calculate current documentation count
        # Base: 13 (from ExecutionOrchestrator) + new files
        current_docs = 13 + total_files
        
        update_master_plan_progress(
            phase="4",  # Documentation phase
            completion_percentage=100,
            metrics={
                "docs_generated": current_docs,
                "orchestrators_migrated": 3  # Execution, Documentation, TDD
            },
            auto_document=False  # Already doing manual regeneration
        )
        
        logger.info(f"✅ Updated MASTER-PLAN: {current_docs}/200+ docs generated")
    
    # Validation check
    logger.info("\n🔍 Validation:")
    required_docs = [
        (docs_path / "execution_orchestrator" / "summary.md", "ExecutionOrchestrator"),
        (docs_path / "documentation_orchestrator" / "summary.md", "DocumentationOrchestrator"),
        (docs_path / "tdd_orchestrator" / "summary.md", "TDDOrchestrator"),
        (docs_path / "base_framework" / "summary.md", "BaseOrchestrator")
    ]
    
    all_present = True
    for doc_path, name in required_docs:
        if doc_path.exists():
            logger.info(f"  ✅ {name}: {doc_path.name}")
        else:
            logger.error(f"  ❌ {name}: MISSING")
            all_present = False
    
    if all_present:
        logger.info("\n🎉 All required documentation generated successfully!")
        return 0
    else:
        logger.error("\n⚠️  Some documentation is missing. Check logs above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
