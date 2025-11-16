"""
CORTEX EPM Documentation Generator - Main Orchestrator
Generates complete CORTEX 3.0 documentation from source files

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - Part of CORTEX 3.0
"""

import sys
import argparse
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.epm.modules.validation_engine import ValidationEngine
from src.epm.modules.cleanup_manager import CleanupManager
from src.epm.modules.diagram_generator import DiagramGenerator
from src.epm.modules.page_generator import PageGenerator
from src.epm.modules.cross_reference_builder import CrossReferenceBuilder

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DocumentationGenerator:
    """
    EPM Orchestrator for complete documentation generation
    
    Executes 6-stage pipeline:
    1. Pre-Flight Validation
    2. Destructive Cleanup  
    3. Diagram Generation
    4. Page Generation
    5. Cross-Reference & Navigation
    6. Post-Generation Validation
    """
    
    def __init__(self, root_path: Path, profile: str = "standard", dry_run: bool = False):
        self.root_path = root_path
        self.brain_path = root_path / "cortex-brain"
        self.profile = profile
        self.dry_run = dry_run
        self.timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        
        # Initialize modules
        self.validator = ValidationEngine(root_path)
        self.cleanup_manager = CleanupManager(root_path, dry_run)
        self.diagram_generator = DiagramGenerator(root_path, dry_run)
        self.page_generator = PageGenerator(root_path, dry_run)
        self.cross_ref_builder = CrossReferenceBuilder(root_path, dry_run)
        
        # Track generation results
        self.results = {
            "timestamp": self.timestamp,
            "profile": profile,
            "dry_run": dry_run,
            "stages": {},
            "files_generated": {},
            "duration": {},
            "errors": [],
            "warnings": []
        }
    
    def execute(self, stage: Optional[str] = None, skip_backup: bool = False, 
                keep_old: bool = False) -> Dict:
        """
        Execute documentation generation pipeline
        
        Args:
            stage: Specific stage to run (None = all stages)
            skip_backup: Skip backup creation (dangerous!)
            keep_old: Keep old docs instead of deleting
        
        Returns:
            Dictionary with generation results
        """
        logger.info("=" * 80)
        logger.info("CORTEX Documentation Generator v1.0.0")
        logger.info("=" * 80)
        logger.info(f"Profile: {self.profile}")
        logger.info(f"Dry Run: {self.dry_run}")
        logger.info(f"Timestamp: {self.timestamp}")
        logger.info("")
        
        try:
            if stage:
                # Run specific stage only
                self._execute_stage(stage, skip_backup, keep_old)
            else:
                # Run all stages
                self._execute_all_stages(skip_backup, keep_old)
            
            # Generate final report
            self._generate_summary_report()
            
            logger.info("")
            logger.info("=" * 80)
            logger.info("✅ Documentation Generation Complete!")
            logger.info("=" * 80)
            
            return self.results
            
        except Exception as e:
            logger.error(f"❌ Documentation generation failed: {e}")
            self.results["errors"].append(str(e))
            
            # Attempt rollback if not dry run
            if not self.dry_run:
                logger.warning("Attempting rollback...")
                self._rollback()
            
            raise
    
    def _execute_all_stages(self, skip_backup: bool, keep_old: bool):
        """Execute all 6 pipeline stages"""
        stages = [
            ("pre_flight_validation", "Pre-Flight Validation"),
            ("destructive_cleanup", "Destructive Cleanup"),
            ("diagram_generation", "Diagram Generation"),
            ("page_generation", "Page Generation"),
            ("cross_reference", "Cross-Reference & Navigation"),
            ("post_validation", "Post-Generation Validation")
        ]
        
        for stage_id, stage_name in stages:
            logger.info("")
            logger.info(f"{'='*80}")
            logger.info(f"Stage: {stage_name}")
            logger.info(f"{'='*80}")
            
            self._execute_stage(stage_id, skip_backup, keep_old)
    
    def _execute_stage(self, stage: str, skip_backup: bool, keep_old: bool):
        """Execute a specific pipeline stage"""
        start_time = datetime.now()
        
        try:
            if stage == "validation" or stage == "pre_flight_validation":
                result = self._stage_pre_flight_validation()
            elif stage == "cleanup" or stage == "destructive_cleanup":
                result = self._stage_destructive_cleanup(skip_backup, keep_old)
            elif stage == "diagrams" or stage == "diagram_generation":
                result = self._stage_diagram_generation()
            elif stage == "pages" or stage == "page_generation":
                result = self._stage_page_generation()
            elif stage == "cross-ref" or stage == "cross_reference":
                result = self._stage_cross_reference()
            elif stage == "validate" or stage == "post_validation":
                result = self._stage_post_validation()
            else:
                raise ValueError(f"Unknown stage: {stage}")
            
            duration = (datetime.now() - start_time).total_seconds()
            
            self.results["stages"][stage] = result
            self.results["duration"][stage] = duration
            
            logger.info(f"✅ Stage completed in {duration:.2f}s")
            
        except Exception as e:
            logger.error(f"❌ Stage failed: {e}")
            self.results["errors"].append(f"{stage}: {str(e)}")
            raise
    
    def _stage_pre_flight_validation(self) -> Dict:
        """Stage 1: Pre-Flight Validation"""
        logger.info("Validating source files...")
        
        # Validate CORTEX brain structure
        brain_valid = self.validator.validate_brain_structure()
        if not brain_valid:
            raise RuntimeError("CORTEX brain structure validation failed")
        
        # Validate YAML schemas
        yaml_valid = self.validator.validate_yaml_schemas()
        if not yaml_valid:
            raise RuntimeError("YAML schema validation failed")
        
        # Validate code structure
        code_valid = self.validator.validate_code_structure()
        if not code_valid:
            raise RuntimeError("Code structure validation failed")
        
        # Check write permissions
        perms_valid = self.validator.check_write_permissions()
        if not perms_valid:
            raise RuntimeError("Write permissions check failed")
        
        logger.info("✓ All source validations passed")
        
        return {
            "brain_structure": "VALID",
            "yaml_schemas": "VALID",
            "code_structure": "VALID",
            "write_permissions": "VALID"
        }
    
    def _stage_destructive_cleanup(self, skip_backup: bool, keep_old: bool) -> Dict:
        """Stage 2: Destructive Cleanup"""
        logger.info("Performing destructive cleanup...")
        
        if not skip_backup:
            logger.info("Creating backup...")
            backup_path = self.cleanup_manager.create_backup(self.timestamp)
            logger.info(f"✓ Backup created: {backup_path}")
        else:
            logger.warning("⚠️  SKIPPING BACKUP (use with caution!)")
            backup_path = None
        
        # Clear generated content
        logger.info("Clearing generated content...")
        cleanup_result = self.cleanup_manager.clear_generated_content(keep_old)
        
        logger.info(f"✓ Removed {cleanup_result['files_removed']} files")
        logger.info(f"✓ Freed {cleanup_result['space_freed_mb']:.2f} MB")
        
        return {
            "backup_path": str(backup_path) if backup_path else None,
            "files_removed": cleanup_result["files_removed"],
            "space_freed_mb": cleanup_result["space_freed_mb"]
        }
    
    def _stage_diagram_generation(self) -> Dict:
        """Stage 3: Diagram Generation"""
        logger.info("Generating diagrams...")
        
        # Load diagram definitions
        definitions_file = self.brain_path / "doc-generation-config" / "diagram-definitions.yaml"
        
        # Generate all diagrams from definitions
        result = self.diagram_generator.generate_all_diagrams(definitions_file)
        
        total_diagrams = result["diagrams_generated"]
        logger.info(f"✓ Generated {total_diagrams} diagrams")
        
        self.results["files_generated"]["diagrams"] = total_diagrams
        
        return {
            "total": total_diagrams,
            "files": result["files"]
        }
    
    def _stage_page_generation(self) -> Dict:
        """Stage 4: Page Generation"""
        logger.info("Generating documentation pages...")
        
        # Load page definitions
        definitions_file = self.brain_path / "doc-generation-config" / "page-definitions.yaml"
        
        # Load source mapping
        source_mapping_file = self.brain_path / "doc-generation-config" / "source-mapping.yaml"
        with open(source_mapping_file, 'r') as f:
            import yaml
            config = yaml.safe_load(f)
            source_mapping = {}
            # Flatten source mapping
            for category in ['brain_sources', 'code_sources', 'config_sources', 'document_sources', 'diagram_sources']:
                if category in config:
                    source_mapping.update(config[category])
        
        # Generate all pages from definitions
        result = self.page_generator.generate_all_pages(definitions_file, source_mapping)
        
        total_pages = result["pages_generated"]
        logger.info(f"✓ Generated {total_pages} pages")
        
        self.results["files_generated"]["pages"] = total_pages
        
        return {
            "total": total_pages,
            "files": result["files"]
        }
    
    def _stage_cross_reference(self) -> Dict:
        """Stage 5: Cross-Reference & Navigation"""
        logger.info("Building cross-references and navigation...")
        
        # Build complete cross-reference index and navigation
        result = self.cross_ref_builder.build_cross_references()
        
        logger.info(f"✓ Indexed {result['total_links']} links across {result['total_pages']} pages")
        
        if result['broken_links'] > 0:
            logger.warning(f"⚠️ Found {result['broken_links']} broken links")
        
        return result
    
    def _stage_post_validation(self) -> Dict:
        """Stage 6: Post-Generation Validation"""
        logger.info("Validating generated documentation...")
        
        # Check internal links
        logger.info("Checking internal links...")
        links_valid, broken_links = self.validator.check_internal_links()
        
        # Verify diagrams
        logger.info("Verifying diagram references...")
        diagrams_valid = self.validator.verify_diagram_references()
        
        # Validate markdown syntax
        logger.info("Validating markdown syntax...")
        markdown_valid = self.validator.validate_markdown_syntax()
        
        # Run MkDocs build test
        logger.info("Running MkDocs build test...")
        mkdocs_valid = self.validator.test_mkdocs_build()
        
        validation_result = {
            "internal_links": "VALID" if links_valid else "INVALID",
            "broken_links": broken_links,
            "diagram_references": "VALID" if diagrams_valid else "INVALID",
            "markdown_syntax": "VALID" if markdown_valid else "INVALID",
            "mkdocs_build": "VALID" if mkdocs_valid else "INVALID"
        }
        
        if not all([links_valid, diagrams_valid, markdown_valid, mkdocs_valid]):
            self.results["warnings"].append("Post-validation found issues")
            logger.warning("⚠️  Validation found issues (see report)")
        else:
            logger.info("✓ All validations passed")
        
        return validation_result
    
    def _generate_summary_report(self):
        """Generate final summary report"""
        report_path = self.root_path / "docs" / f"GENERATION-REPORT-{self.timestamp}.md"
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would generate report: {report_path}")
            return
        
        total_duration = sum(self.results["duration"].values())
        
        report_content = f"""# CORTEX Documentation Generation Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Profile:** {self.profile}  
**Duration:** {total_duration:.2f} seconds

## Summary

- **Diagrams Generated:** {self.results['files_generated'].get('diagrams', 0)}
- **Pages Generated:** {self.results['files_generated'].get('pages', 0)}
- **Errors:** {len(self.results['errors'])}
- **Warnings:** {len(self.results['warnings'])}

## Pipeline Stages

"""
        
        for stage, result in self.results["stages"].items():
            duration = self.results["duration"].get(stage, 0)
            report_content += f"### {stage.replace('_', ' ').title()}\n\n"
            report_content += f"- **Duration:** {duration:.2f}s\n"
            report_content += f"- **Result:** {json.dumps(result, indent=2)}\n\n"
        
        if self.results["errors"]:
            report_content += "## Errors\n\n"
            for error in self.results["errors"]:
                report_content += f"- {error}\n"
            report_content += "\n"
        
        if self.results["warnings"]:
            report_content += "## Warnings\n\n"
            for warning in self.results["warnings"]:
                report_content += f"- {warning}\n"
            report_content += "\n"
        
        report_content += """
---

**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**Generated by:** CORTEX EPM Documentation Generator v1.0.0
"""
        
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report_content, encoding='utf-8')
        
        logger.info(f"✓ Report generated: {report_path}")
    
    def _rollback(self):
        """Attempt to rollback changes on error"""
        logger.info("Rolling back changes...")
        
        try:
            backup_dir = self.root_path / f"docs-backup-{self.timestamp}"
            if backup_dir.exists():
                self.cleanup_manager.restore_from_backup(backup_dir)
                logger.info("✓ Rollback complete")
            else:
                logger.warning("⚠️  No backup found for rollback")
        except Exception as e:
            logger.error(f"❌ Rollback failed: {e}")


def main():
    """Main entry point for documentation generator"""
    parser = argparse.ArgumentParser(
        description='CORTEX Documentation Generator - Generate complete CORTEX 3.0 documentation'
    )
    
    parser.add_argument(
        '--full-refresh',
        action='store_true',
        help='Destructive full regeneration (default behavior)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be generated without actually doing it'
    )
    
    parser.add_argument(
        '--stage',
        choices=['validation', 'cleanup', 'diagrams', 'pages', 'cross-ref', 'validate'],
        help='Run specific stage only'
    )
    
    parser.add_argument(
        '--profile',
        choices=['minimal', 'standard', 'comprehensive'],
        default='standard',
        help='Generation profile (default: standard)'
    )
    
    parser.add_argument(
        '--skip-backup',
        action='store_true',
        help='Skip backup creation (USE WITH CAUTION)'
    )
    
    parser.add_argument(
        '--keep-old',
        action='store_true',
        help='Keep old docs in docs-old/ instead of deleting'
    )
    
    args = parser.parse_args()
    
    # Get CORTEX root path
    root_path = Path(__file__).parent.parent.parent
    
    # Create generator
    generator = DocumentationGenerator(
        root_path=root_path,
        profile=args.profile,
        dry_run=args.dry_run
    )
    
    # Execute generation
    try:
        result = generator.execute(
            stage=args.stage,
            skip_backup=args.skip_backup,
            keep_old=args.keep_old
        )
        
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
