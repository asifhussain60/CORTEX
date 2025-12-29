#!/usr/bin/env python3
"""
CLI Wrapper for Code Sanitization

Provides command-line interface for sanitizing codebases.

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.

Usage:
    python sanitize_wrapper.py <source_directory> [options]
    
Options:
    --output <path>         Output directory (default: {source}-sanitized)
    --dry-run               Preview changes without applying
    --auto-approve          Skip user approval prompts
    --mapping-file <path>   Custom mapping file (JSON)
"""

import argparse
import json
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.operations.modules.orchestration.sanitization_orchestrator import SanitizationOrchestrator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point for CLI wrapper."""
    parser = argparse.ArgumentParser(
        description="CORTEX Code Sanitization - Transform domain-specific codebases to generic versions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Sanitize codebase with default settings
  python sanitize_wrapper.py C:\\Projects\\MyApp
  
  # Dry-run preview
  python sanitize_wrapper.py C:\\Projects\\MyApp --dry-run
  
  # Custom output directory
  python sanitize_wrapper.py C:\\Projects\\MyApp --output C:\\Projects\\MyApp-Generic
  
  # Auto-approve with custom mappings
  python sanitize_wrapper.py C:\\Projects\\MyApp --auto-approve --mapping-file mappings.json
        """
    )
    
    parser.add_argument(
        "source_directory",
        help="Path to codebase to sanitize"
    )
    
    parser.add_argument(
        "--output",
        "-o",
        dest="output_directory",
        help="Output directory for sanitized code (default: {source}-sanitized)"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview transformations without applying changes"
    )
    
    parser.add_argument(
        "--auto-approve",
        action="store_true",
        help="Skip user approval prompts"
    )
    
    parser.add_argument(
        "--mapping-file",
        help="Path to custom mapping file (JSON format)"
    )
    
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output"
    )

    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Validate source directory
    source_path = Path(args.source_directory)
    if not source_path.exists():
        logger.error(f"Source directory not found: {args.source_directory}")
        sys.exit(1)

    # Load custom mappings if provided
    mapping_overrides = None
    if args.mapping_file:
        try:
            with open(args.mapping_file, 'r', encoding='utf-8') as f:
                mapping_overrides = json.load(f)
            logger.info(f"Loaded {len(mapping_overrides)} custom mappings")
        except Exception as e:
            logger.error(f"Failed to load mapping file: {e}")
            sys.exit(1)

    # Display banner
    print("=" * 70)
    print("CORTEX Code Sanitization Orchestrator v1.0.0")
    print("=" * 70)
    print(f"Source: {args.source_directory}")
    print(f"Output: {args.output_directory or f'{args.source_directory}-sanitized'}")
    print(f"Mode: {'DRY-RUN (preview only)' if args.dry_run else 'LIVE TRANSFORMATION'}")
    print("=" * 70)
    print()

    try:
        # Initialize orchestrator
        orchestrator = SanitizationOrchestrator()

        # Execute sanitization
        results = orchestrator.execute_sanitization(
            source_directory=args.source_directory,
            output_directory=args.output_directory,
            mapping_overrides=mapping_overrides,
            dry_run=args.dry_run,
            auto_approve=args.auto_approve
        )

        # Display results
        print("\n" + "=" * 70)
        print("SANITIZATION RESULTS")
        print("=" * 70)
        print(f"Status: {results.get('status', 'unknown').upper()}")
        
        if results.get("status") == "success":
            print("\n✅ Sanitization completed successfully!")
            
            # Show metrics
            analyze = results.get("phases", {}).get("analyze", {})
            transform = results.get("phases", {}).get("transform", {})
            validate = results.get("phases", {}).get("validate", {})
            
            print(f"\nMetrics:")
            print(f"  Files scanned: {analyze.get('file_inventory', {}).get('total_files', 0)}")
            print(f"  Files transformed: {transform.get('files_transformed', 0)}")
            print(f"  Transformations applied: {transform.get('transformations_applied', 0)}")
            print(f"  Build success: {'✅ YES' if validate.get('build_success') else '❌ NO'}")
            print(f"  Tests passed: {validate.get('tests_passed', 0)}")
            
            # Show artifact locations
            report = results.get("phases", {}).get("report", {})
            print(f"\nArtifacts:")
            print(f"  Audit report: {report.get('audit_report', 'N/A')}")
            print(f"  Mapping reference: {report.get('mapping_reference', 'N/A')}")
            print(f"  Sanitized code: {transform.get('output_directory', 'N/A')}")
            print(f"  Backup: {transform.get('backup_location', 'N/A')}")
            
        elif results.get("status") == "cancelled":
            print("\n⚠️  Sanitization cancelled by user")
            
        else:
            print("\n❌ Sanitization failed!")
            print(f"Error: {results.get('error', 'Unknown error')}")
            sys.exit(1)

        print("=" * 70)

    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Sanitization failed: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
