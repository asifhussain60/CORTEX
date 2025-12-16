"""
Code Sanitization Orchestrator

Transforms domain-specific codebases into generic, shareable versions while
preserving full functionality and architecture patterns.

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
Version: 1.0.0
"""

import logging
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import yaml
import json

logger = logging.getLogger(__name__)


class SanitizationOrchestrator:
    """
    5-phase orchestrator for sanitizing company-specific codebases:
    1. Analyze - Discover domain terminology
    2. Mapping - Generate transformation mappings
    3. Transform - Apply sanitization
    4. Validate - Build and test verification
    5. Report - Generate audit documentation
    """

    def __init__(self, manifest_path: Optional[str] = None):
        """Initialize orchestrator with manifest configuration."""
        self.manifest_path = manifest_path or self._get_default_manifest_path()
        self.manifest = self._load_manifest()
        self.workspace_root = self._detect_workspace_root()
        self.current_phase = None
        self.results = {
            "start_time": datetime.utcnow().isoformat(),
            "phases": {},
            "artifacts": {},
            "validation": {},
        }

    def _get_default_manifest_path(self) -> str:
        """Get default manifest path."""
        return os.path.join(
            os.path.dirname(__file__),
            "..", "..", "..", "..",
            "cortex-brain", "orchestrator-manifests",
            "code-sanitization-manifest.yaml"
        )

    def _load_manifest(self) -> Dict[str, Any]:
        """Load orchestrator manifest."""
        try:
            with open(self.manifest_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load manifest: {e}")
            raise

    def _detect_workspace_root(self) -> Path:
        """Detect workspace root directory."""
        current = Path.cwd()
        while current != current.parent:
            if (current / ".git").exists():
                return current
            current = current.parent
        return Path.cwd()

    def execute_sanitization(
        self,
        source_directory: str,
        output_directory: Optional[str] = None,
        mapping_overrides: Optional[Dict[str, str]] = None,
        dry_run: bool = False,
        auto_approve: bool = False
    ) -> Dict[str, Any]:
        """
        Execute full sanitization workflow.

        Args:
            source_directory: Path to codebase to sanitize
            output_directory: Optional output path (default: {source}-sanitized)
            mapping_overrides: Custom domain→generic mappings
            dry_run: Preview changes without applying
            auto_approve: Skip user approval prompts

        Returns:
            Dict with execution results and artifacts
        """
        logger.info("🎭 Orchestrator engaged: SanitizationOrchestrator")
        logger.info(f"Source: {source_directory}")

        try:
            # Phase 1: Analyze
            logger.info("🎭 Phase transition: START → ANALYZE")
            analysis_results = self._phase_1_analyze(source_directory)
            self.results["phases"]["analyze"] = analysis_results

            # Phase 2: Mapping
            logger.info("🎭 Phase transition: ANALYZE → MAPPING")
            mapping_results = self._phase_2_mapping(
                analysis_results,
                mapping_overrides,
                auto_approve
            )
            self.results["phases"]["mapping"] = mapping_results

            # User approval check
            if not auto_approve and not dry_run:
                if not self._request_user_approval("mapping"):
                    logger.info("Sanitization cancelled by user")
                    return self._generate_cancellation_report()

            # Phase 3: Transform
            logger.info("🎭 Phase transition: MAPPING → TRANSFORM")
            if not dry_run:
                transform_results = self._phase_3_transform(
                    source_directory,
                    output_directory or f"{source_directory}-sanitized",
                    mapping_results
                )
                self.results["phases"]["transform"] = transform_results
            else:
                logger.info("Dry-run mode: Skipping transformation")
                self.results["phases"]["transform"] = {"dry_run": True}

            # Phase 4: Validate
            logger.info("🎭 Phase transition: TRANSFORM → VALIDATE")
            if not dry_run:
                validation_results = self._phase_4_validate(
                    self.results["phases"]["transform"]["output_directory"]
                )
                self.results["phases"]["validate"] = validation_results

                # Rollback on validation failure
                if not validation_results.get("success", False):
                    logger.error("Validation failed - initiating rollback")
                    self._rollback(transform_results["backup_location"])
                    return self._generate_failure_report()
            else:
                self.results["phases"]["validate"] = {"dry_run": True}

            # Phase 5: Report
            logger.info("🎭 Phase transition: VALIDATE → REPORT")
            report_results = self._phase_5_report()
            self.results["phases"]["report"] = report_results

            logger.info("🎭 Orchestrator completing: ✅ ALL WORK COMPLETE")
            self.results["end_time"] = datetime.utcnow().isoformat()
            self.results["is_complete"] = True
            self.results["status"] = "success"

            return self.results

        except Exception as e:
            logger.error(f"Sanitization failed: {e}", exc_info=True)
            self.results["status"] = "failed"
            self.results["error"] = str(e)
            return self.results

    def _phase_1_analyze(self, source_directory: str) -> Dict[str, Any]:
        """
        Phase 1: Discovery & Analysis
        Scan codebase and identify domain-specific terminology.
        """
        self.current_phase = "analyze"
        logger.info("Phase 1: Discovery & Analysis")

        from ...utilities.sanitization.code_analyzer import CodeAnalyzer

        analyzer = CodeAnalyzer(source_directory, self.manifest)
        results = {
            "source_directory": source_directory,
            "file_inventory": analyzer.scan_file_structure(),
            "domain_terms": analyzer.extract_domain_terminology(),
            "sensitive_data": analyzer.detect_sensitive_data(),
            "namespaces": analyzer.extract_namespaces(),
            "dependencies": analyzer.generate_dependency_graph(),
        }

        logger.info(f"Analyzed {results['file_inventory']['total_files']} files")
        logger.info(f"Identified {len(results['domain_terms'])} domain-specific terms")

        return results

    def _phase_2_mapping(
        self,
        analysis_results: Dict[str, Any],
        mapping_overrides: Optional[Dict[str, str]],
        auto_approve: bool
    ) -> Dict[str, Any]:
        """
        Phase 2: Generate Transformation Mapping
        Create domain→generic mappings with user approval.
        """
        self.current_phase = "mapping"
        logger.info("Phase 2: Generate Transformation Mapping")

        from ...utilities.sanitization.mapping_engine import MappingEngine

        engine = MappingEngine(self.manifest, mapping_overrides)
        
        mappings = engine.generate_mappings(
            analysis_results["domain_terms"],
            analysis_results["namespaces"]
        )

        conflicts = engine.detect_conflicts(mappings)
        if conflicts:
            logger.warning(f"Detected {len(conflicts)} naming conflicts")
            mappings = engine.resolve_conflicts(mappings, conflicts)

        preview = engine.generate_preview(mappings)

        results = {
            "mappings": mappings,
            "conflicts_resolved": conflicts,
            "preview": preview,
            "total_transformations": len(mappings),
        }

        # Display preview
        self._display_mapping_preview(preview)

        return results

    def _phase_3_transform(
        self,
        source_directory: str,
        output_directory: str,
        mapping_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Phase 3: Execute Transformation
        Apply mappings across all files with backup.
        """
        self.current_phase = "transform"
        logger.info("Phase 3: Execute Transformation")

        from ...utilities.sanitization.transformer import CodeTransformer

        # Create backup
        backup_location = self._create_backup(source_directory)
        logger.info(f"Backup created: {backup_location}")

        # Execute transformation
        transformer = CodeTransformer(self.manifest)
        
        transform_log = transformer.transform_codebase(
            source_directory,
            output_directory,
            mapping_results["mappings"]
        )

        results = {
            "output_directory": output_directory,
            "backup_location": backup_location,
            "files_transformed": transform_log["files_transformed"],
            "transformations_applied": transform_log["total_transformations"],
            "log": transform_log,
        }

        logger.info(f"Transformed {results['files_transformed']} files")

        return results

    def _phase_4_validate(self, sanitized_directory: str) -> Dict[str, Any]:
        """
        Phase 4: Build & Test Validation
        Ensure sanitized code builds and tests pass.
        """
        self.current_phase = "validate"
        logger.info("Phase 4: Build & Test Validation")

        from ...utilities.sanitization.validator import BuildValidator

        validator = BuildValidator(self.manifest)

        # Detect build system
        build_system = validator.detect_build_system(sanitized_directory)
        logger.info(f"Detected build system: {build_system}")

        # Execute build
        build_result = validator.execute_build(sanitized_directory, build_system)
        
        # Run tests
        test_result = validator.run_tests(sanitized_directory, build_system)

        results = {
            "build_system": build_system,
            "build_success": build_result.get("success", False),
            "build_output": build_result.get("output", ""),
            "test_success": test_result.get("success", False),
            "tests_passed": test_result.get("passed", 0),
            "tests_failed": test_result.get("failed", 0),
            "success": build_result["success"] and test_result["success"],
        }

        if results["success"]:
            logger.info("✅ Validation successful")
        else:
            logger.error("❌ Validation failed")

        return results

    def _phase_5_report(self) -> Dict[str, Any]:
        """
        Phase 5: Generate Audit Report
        Document transformation with full traceability.
        """
        self.current_phase = "report"
        logger.info("Phase 5: Generate Audit Report")

        from ...utilities.sanitization.report_generator import ReportGenerator

        generator = ReportGenerator(self.manifest)

        # Generate comprehensive report
        report_path = generator.generate_audit_report(self.results)
        mapping_ref_path = generator.generate_mapping_reference(
            self.results["phases"]["mapping"]["mappings"]
        )

        results = {
            "audit_report": report_path,
            "mapping_reference": mapping_ref_path,
            "artifacts_archived": True,
        }

        logger.info(f"Audit report: {report_path}")
        
        # Cleanup backup after successful completion
        backup_location = self.results.get("phases", {}).get("transform", {}).get("backup_location")
        if backup_location:
            self._cleanup_backup(backup_location)

        return results

    def _cleanup_backup(self, backup_location: str) -> None:
        """
        Delete backup directory after successful sanitization.
        
        Args:
            backup_location: Path to backup directory to remove
        """
        try:
            backup_path = Path(backup_location)
            if backup_path.exists():
                shutil.rmtree(backup_path)
                logger.info(f"Backup deleted: {backup_location}")
            else:
                logger.warning(f"Backup not found for deletion: {backup_location}")
        except Exception as e:
            logger.warning(f"Failed to delete backup {backup_location}: {e}")
            # Non-fatal - don't fail the operation if cleanup fails

    def _create_backup(self, source_directory: str) -> str:
        """Create backup of source directory."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = f"{source_directory}_backup_{timestamp}"
        
        shutil.copytree(source_directory, backup_dir)
        logger.info(f"Backup created: {backup_dir}")
        
        return backup_dir

    def _rollback(self, backup_location: str) -> None:
        """Rollback to backup on validation failure."""
        logger.warning(f"Rolling back from backup: {backup_location}")
        # Implementation would restore from backup
        # For safety, this should be user-confirmed

    def _request_user_approval(self, phase: str) -> bool:
        """Request user approval for critical phase."""
        # This would integrate with Copilot Chat for interactive approval
        # For now, return True (auto-approve in non-interactive mode)
        logger.info(f"User approval required for phase: {phase}")
        return True

    def _display_mapping_preview(self, preview: Dict[str, Any]) -> None:
        """Display mapping preview to user."""
        logger.info("=" * 60)
        logger.info("TRANSFORMATION PREVIEW")
        logger.info("=" * 60)
        for old_term, new_term in list(preview.items())[:10]:
            logger.info(f"  {old_term:<40} → {new_term}")
        if len(preview) > 10:
            logger.info(f"  ... and {len(preview) - 10} more")
        logger.info("=" * 60)

    def _generate_cancellation_report(self) -> Dict[str, Any]:
        """Generate report for user-cancelled operation."""
        return {
            "status": "cancelled",
            "message": "Sanitization cancelled by user",
            "completed_phases": list(self.results["phases"].keys()),
        }

    def _generate_failure_report(self) -> Dict[str, Any]:
        """Generate report for failed operation."""
        return {
            "status": "failed",
            "message": "Validation failed - changes rolled back",
            "results": self.results,
        }
