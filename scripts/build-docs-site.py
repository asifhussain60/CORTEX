"""
Build CORTEX documentation site.

Main CLI entry point for documentation generation pipeline.
Orchestrates discovery → extraction → rendering → validation.

Usage:
    python scripts/build-docs-site.py [--full|--incremental] [--dry-run]

AC_START: AC-PHASE98-S3-T1
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, Any
import time

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cortex.orchestrators.internal.cortex_docs_orchestrator import (
    CortexDocsOrchestrator,
    BuildMode,
    PipelineStage,
)


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Build CORTEX documentation site",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument(
        "--mode",
        choices=["full", "incremental"],
        default="incremental",
        help="Build mode (default: incremental)",
    )
    
    parser.add_argument(
        "--skip-discovery",
        action="store_true",
        help="Skip discovery pipeline stage",
    )
    
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip validation pipeline stage",
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview without writing files",
    )
    
    parser.add_argument(
        "--content-root",
        type=Path,
        default=Path("cortex-docs/content/src"),
        help="Source Markdown directory",
    )
    
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("cortex-docs"),
        help="Generated HTML output directory",
    )
    
    return parser.parse_args()


def print_summary(result: Dict[str, Any]) -> None:
    """
    Print build summary table.
    
    Args:
        result: Pipeline execution results
    """
    print("\n" + "=" * 60)
    print("CORTEX Documentation Build Summary")
    print("=" * 60)
    print(f"Status:           {result['status'].upper()}")
    print(f"Duration:         {result['duration']:.2f}s")
    print(f"Stages Complete:  {result['stages_completed']}")
    print(f"Files Processed:  {result['files_processed']}")
    print(f"Files Written:    {result['files_written']}")
    
    if result.get('cache_hit'):
        print("Cache Hit:        YES (no changes detected)")
    
    if result.get('validation_errors', 0) > 0:
        print(f"Validation Errors: {result['validation_errors']}")
    
    print("=" * 60 + "\n")


def main() -> int:
    """
    Main entry point.
    
    Returns:
        Exit code (0 = success, 1 = failure)
    """
    args = parse_args()
    
    print(f"\n🏗️  CORTEX Documentation Build")
    print(f"Mode: {args.mode}")
    print(f"Dry Run: {args.dry_run}")
    print(f"Content: {args.content_root}")
    print(f"Output: {args.output_root}\n")
    
    # Determine skip stages
    skip_stages = []
    if args.skip_discovery:
        skip_stages.append(PipelineStage.DISCOVER)
    if args.skip_validation:
        skip_stages.append(PipelineStage.VALIDATE)
    
    # Create orchestrator
    orchestrator = CortexDocsOrchestrator(
        content_root=args.content_root,
        output_root=args.output_root,
        build_mode=BuildMode.FULL if args.mode == "full" else BuildMode.INCREMENTAL,
        skip_stages=skip_stages,
        dry_run=args.dry_run,
    )
    
    # Run pipeline
    try:
        start_time = time.time()
        print("⏳ Running pipeline...")
        
        result = orchestrator.run()
        
        print(f"✅ Build completed in {time.time() - start_time:.2f}s")
        print_summary(result)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Build failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())


# AC_COMPLETE: AC-PHASE98-S3-T1
