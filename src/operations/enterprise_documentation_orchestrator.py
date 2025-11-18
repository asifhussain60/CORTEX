"""
CORTEX Enterprise Documentation EPM Orchestrator
Entry point module for comprehensive documentation generation

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - Part of CORTEX 3.0

Triggered by natural language commands:
- "Generate documentation" 
- "Generate Cortex docs"
- "/CORTEX Generate documentation"
- "Update documentation"
- "Refresh docs"
"""

import sys
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.epm.doc_generator import DocumentationGenerator
from src.operations.documentation_component_registry import create_default_registry
from src.operations.base_operation_module import OperationResult, OperationStatus
from src.plugins.story_generator_plugin import StoryGeneratorPlugin

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnterpriseDocumentationOrchestrator:
    """
    Enterprise Documentation EPM (Entry Point Module) Orchestrator
    
    Provides natural language interface to CORTEX documentation generation system.
    Integrates with existing EPM doc_generator for complete documentation lifecycle.
    """
    
    def __init__(self, workspace_root: Optional[Path] = None):
        """Initialize the orchestrator"""
        self.workspace_root = workspace_root or Path.cwd()
        self.brain_path = self.workspace_root / "cortex-brain"
        self.docs_path = self.workspace_root / "docs"
        self.timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        
        # Validate workspace structure
        if not self.brain_path.exists():
            raise FileNotFoundError(f"CORTEX brain not found at {self.brain_path}")
        
        logger.info(f"Enterprise Documentation Orchestrator initialized")
        logger.info(f"Workspace: {self.workspace_root}")
        logger.info(f"Brain: {self.brain_path}")
    
    def execute(self, 
                profile: str = "standard",
                dry_run: bool = False,
                stage: Optional[str] = None,
                options: Optional[Dict[str, Any]] = None) -> OperationResult:
        """
        Execute enterprise documentation generation
        
        Args:
            profile: Generation profile ('quick', 'standard', 'comprehensive')
            dry_run: Preview mode (no actual generation)
            stage: Specific stage to run (None for full pipeline)
            options: Additional options from user request
            
        Returns:
            OperationResult with generation report
        """
        start_time = datetime.now()
        
        try:
            logger.info("🚀 Starting Enterprise Documentation Generation")
            logger.info(f"Profile: {profile}")
            logger.info(f"Dry Run: {dry_run}")
            if stage:
                logger.info(f"Stage: {stage}")
            
            # If specific components are requested, use the new component registry
            requested_components: Optional[List[str]] = None
            if options:
                # Accept multiple possible keys to be NL-friendly
                requested_components = options.get("components") or options.get("component")
                if isinstance(requested_components, str):
                    requested_components = [requested_components]

            # Map stage shortcuts to components
            stage_component_map = {
                "diagrams": ["diagrams"],
                "mkdocs": ["mkdocs"],
                "feature-list": ["feature_list"],
                "all": ["diagrams", "feature_list", "mkdocs"],
            }
            if not requested_components and stage in stage_component_map:
                requested_components = stage_component_map.get(stage)

            registry_result: Optional[Dict[str, Any]] = None
            if requested_components:
                logger.info("Executing documentation via Component Registry")
                registry = create_default_registry(self.workspace_root)
                pipeline = requested_components
                # Default output path is docs/
                registry_result = registry.execute_pipeline(
                    component_ids=pipeline,
                    output_path=self.docs_path,
                    profile=profile,
                    stop_on_failure=True,
                )
                # Align to previous data shape
                generation_result = {
                    "success": registry_result.get("all_success", False),
                    "stages": {c["id"]: {"status": "success" if c.get("success") else "failed"} for c in registry_result.get("components", [])},
                    "files_generated": {},
                    "errors": [],
                    "warnings": [],
                }
            else:
                # Initialize EPM Documentation Generator (legacy pipeline)
                doc_generator = DocumentationGenerator(
                    root_path=self.workspace_root,
                    profile=profile,
                    dry_run=dry_run
                )
                
                # Execute generation pipeline
                if stage:
                    logger.info(f"Executing single stage: {stage}")
                    generation_result = doc_generator.execute(stage=stage)
                else:
                    logger.info("Executing full 6-stage documentation pipeline")
                    generation_result = doc_generator.execute()
            
            # Execute Story Generation Plugin (if enabled)
            story_enabled = options.get("generate_story", True) if options else True
            if story_enabled and not stage:  # Only run for full pipeline
                logger.info("")
                logger.info("=" * 80)
                logger.info("Running Story Generation Plugin...")
                logger.info("=" * 80)
                
                story_plugin = StoryGeneratorPlugin(config={
                    "root_path": str(self.workspace_root)
                })
                
                if story_plugin.initialize():
                    story_context = {
                        "dry_run": dry_run,
                        "chapters": options.get("story_chapters", 10) if options else 10,
                        "max_words_per_chapter": options.get("story_max_words", 5000) if options else 5000
                    }
                    
                    story_result = story_plugin.execute(story_context)
                    
                    # Add story results to generation result
                    generation_result["story_generation"] = story_result
                    
                    story_plugin.cleanup()
                else:
                    logger.warning("⚠️ Story generation plugin initialization failed")
            
            # Calculate duration
            duration = (datetime.now() - start_time).total_seconds()
            
            # Build comprehensive result
            result_data = self._build_result_report(
                generation_result, 
                profile, 
                dry_run, 
                stage,
                duration
            )

            # Attach registry execution summary if used
            if registry_result is not None:
                result_data["registry_execution"] = registry_result
            
            # Create operation result
            if generation_result.get("success", False):
                # Add metadata to data dict instead of separate parameter
                result_data["metadata"] = {
                    "operation": "enterprise_documentation",
                    "profile": profile,
                    "dry_run": dry_run,
                    "stage": stage,
                    "timestamp": self.timestamp
                }
                
                return OperationResult(
                    success=True,
                    status=OperationStatus.SUCCESS,
                    message="✅ Enterprise documentation generation completed successfully",
                    data=result_data,
                    duration_seconds=duration
                )
            else:
                # Add metadata to data dict for failure case too
                result_data["metadata"] = {
                    "operation": "enterprise_documentation",
                    "profile": profile,
                    "dry_run": dry_run,
                    "stage": stage,
                    "timestamp": self.timestamp
                }
                
                return OperationResult(
                    success=False,
                    status=OperationStatus.FAILED,
                    message="❌ Enterprise documentation generation failed",
                    data=result_data,
                    duration_seconds=duration,
                    errors=generation_result.get("errors", [])
                )
                
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            logger.error(f"Enterprise documentation generation failed: {str(e)}")
            
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"❌ Documentation generation failed: {str(e)}",
                duration_seconds=duration,
                errors=[str(e)]
            )
    
    def _build_result_report(self, 
                           generation_result: Dict,
                           profile: str,
                           dry_run: bool,
                           stage: Optional[str],
                           duration: float) -> Dict[str, Any]:
        """Build comprehensive result report"""
        
        # Extract key metrics from generation result
        stages_completed = generation_result.get("stages", {})
        files_generated = generation_result.get("files_generated", {})
        warnings = generation_result.get("warnings", [])
        errors = generation_result.get("errors", [])
        
        # Count files by category
        file_counts = {
            "total": sum(len(files) if isinstance(files, list) else 1 
                        for files in files_generated.values()),
            "by_category": {}
        }
        
        for category, files in files_generated.items():
            if isinstance(files, list):
                file_counts["by_category"][category] = len(files)
            else:
                file_counts["by_category"][category] = 1
        
        # Build stage summary
        stage_summary = {}
        for stage_name, stage_data in stages_completed.items():
            if isinstance(stage_data, dict):
                stage_summary[stage_name] = {
                    "status": stage_data.get("status", "unknown"),
                    "duration": stage_data.get("duration", 0),
                    "files_affected": stage_data.get("files_affected", 0)
                }
        
        # Extract story generation metrics
        story_metrics = {}
        if "story_generation" in generation_result:
            story_data = generation_result["story_generation"]
            if story_data.get("success"):
                story_metrics = {
                    "chapters_generated": story_data.get("chapters_generated", 0),
                    "total_words": story_data.get("total_words", 0),
                    "files_created": len(story_data.get("files_created", [])),
                    "output_path": story_data.get("output_path", "")
                }
        
        return {
            "execution_summary": {
                "profile": profile,
                "dry_run": dry_run,
                "stage_filter": stage,
                "duration_seconds": round(duration, 2),
                "timestamp": self.timestamp,
                "success": generation_result.get("success", False)
            },
            "pipeline_stages": stage_summary,
            "file_generation": file_counts,
            "story_generation": story_metrics,  # Add story metrics
            "documentation_structure": self._analyze_docs_structure(),
            "quality_metrics": {
                "warnings_count": len(warnings),
                "errors_count": len(errors),
                "completion_rate": self._calculate_completion_rate(stages_completed)
            },
            "next_steps": self._generate_next_steps(
                generation_result, dry_run, errors, warnings
            ),
            "raw_generation_data": generation_result
        }
    
    def _analyze_docs_structure(self) -> Dict[str, Any]:
        """Analyze generated documentation structure"""
        if not self.docs_path.exists():
            return {"status": "docs_folder_not_found"}
        
        structure = {
            "docs_folder_exists": True,
            "total_files": 0,
            "markdown_files": 0,
            "directories": [],
            "key_files": {}
        }
        
        try:
            # Count files and directories
            for item in self.docs_path.rglob("*"):
                if item.is_file():
                    structure["total_files"] += 1
                    if item.suffix == ".md":
                        structure["markdown_files"] += 1
                elif item.is_dir():
                    rel_path = str(item.relative_to(self.docs_path))
                    if rel_path not in structure["directories"]:
                        structure["directories"].append(rel_path)
            
            # Check for key documentation files
            key_files = [
                "index.md", "README.md", "quick-start.md", 
                "architecture.md", "operations.md", "guides/admin-guide.md"
            ]
            
            for key_file in key_files:
                file_path = self.docs_path / key_file
                structure["key_files"][key_file] = file_path.exists()
                
        except Exception as e:
            structure["analysis_error"] = str(e)
        
        return structure
    
    def _calculate_completion_rate(self, stages_completed: Dict) -> float:
        """Calculate pipeline completion rate"""
        if not stages_completed:
            return 0.0
        
        total_stages = len(stages_completed)
        successful_stages = sum(
            1 for stage_data in stages_completed.values()
            if isinstance(stage_data, dict) and stage_data.get("status") == "success"
        )
        
        return round((successful_stages / total_stages) * 100, 1) if total_stages > 0 else 0.0
    
    def _generate_next_steps(self, 
                           generation_result: Dict,
                           dry_run: bool,
                           errors: List[str],
                           warnings: List[str]) -> List[str]:
        """Generate contextual next steps based on results"""
        steps = []
        
        if dry_run:
            steps.extend([
                "Review the dry-run output above",
                "Run actual generation: 'Generate Cortex docs' (without dry-run)",
                "Check for any configuration issues in cortex-brain/admin/documentation/config/"
            ])
        elif errors:
            steps.extend([
                "Fix the errors listed above before proceeding",
                "Check EPM documentation generator logs for details",
                "Validate YAML configuration files in cortex-brain/admin/documentation/config/"
            ])
        elif warnings:
            steps.extend([
                "Review warnings and consider addressing them",
                "Test generated documentation: 'mkdocs serve'",
                "Commit generated documentation to git"
            ])
        else:
            # Successful generation
            steps.extend([
                "Review generated documentation in docs/ folder",
                "Test locally: 'mkdocs serve' and visit http://localhost:8000",
                "Check for broken links in the documentation",
                "Commit generated documentation to git repository"
            ])
        
        # Add universal helpful steps
        steps.extend([
            "Run 'Generate Cortex docs --dry-run' to preview changes",
            "Use 'Generate Cortex docs --stage=diagrams' to regenerate only diagrams",
            "See EPM admin guide for troubleshooting: docs/operations/epm-doc-generator-admin-guide.md"
        ])
        
        return steps


def get_natural_language_patterns() -> List[str]:
    """
    Return natural language patterns that trigger this orchestrator
    Used by CORTEX intent detection system
    """
    return [
        # Primary triggers
        "generate documentation",
        "generate cortex docs",
        "generate cortex documentation",
        "/CORTEX generate documentation",
        "update documentation",
        "refresh documentation",
        "refresh docs",
        "update docs",
        "build documentation",
        "build docs",
        
        # Variations
        "regenerate documentation",
        "recreate docs", 
        "rebuild documentation",
        "create documentation",
        "make documentation",
        "produce documentation",
        "compile documentation",
        
        # Specific requests
        "generate enterprise docs",
        "create enterprise documentation",
        "build enterprise docs",
        "update enterprise documentation",
        
        # EPM specific
        "run documentation generator",
        "run doc generator",
        "execute documentation epm",
        "run epm documentation",
        
        # With options
        "generate documentation dry run",
        "generate docs preview",
        "generate documentation quick",
        "generate documentation comprehensive"
    ]


def execute_enterprise_documentation(
    workspace_root: Optional[Path] = None,
    profile: str = "standard",
    dry_run: bool = False,
    stage: Optional[str] = None,
    **kwargs
) -> OperationResult:
    """
    Entry point function for enterprise documentation generation
    
    This function is called by CORTEX operations system when natural language
    commands are detected that match documentation generation patterns.
    
    Args:
        workspace_root: Path to CORTEX workspace (auto-detected if None)
        profile: Generation profile ('quick', 'standard', 'comprehensive') 
        dry_run: Preview mode (no actual file generation)
        stage: Specific pipeline stage to run (None for full pipeline)
        **kwargs: Additional options from user request
        
    Returns:
        OperationResult with comprehensive generation report
    """
    orchestrator = EnterpriseDocumentationOrchestrator(workspace_root)
    return orchestrator.execute(
        profile=profile,
        dry_run=dry_run, 
        stage=stage,
        options=kwargs
    )


# CLI interface for direct execution
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="CORTEX Enterprise Documentation Generator"
    )
    parser.add_argument(
        "--profile", 
        choices=["quick", "standard", "comprehensive"],
        default="standard",
        help="Generation profile"
    )
    parser.add_argument(
        "--dry-run", 
        action="store_true",
        help="Preview mode (no actual generation)"
    )
    parser.add_argument(
        "--stage",
        choices=[
            "pre-flight-validation", "destructive-cleanup", 
            "diagram-generation", "page-generation",
            "cross-reference", "post-validation"
        ],
        help="Run specific pipeline stage only"
    )
    parser.add_argument(
        "--workspace",
        type=Path,
        help="Path to CORTEX workspace (default: current directory)"
    )
    
    args = parser.parse_args()
    
    # Execute documentation generation
    result = execute_enterprise_documentation(
        workspace_root=args.workspace,
        profile=args.profile,
        dry_run=args.dry_run,
        stage=args.stage
    )
    
    # Print results
    print("\n" + "="*80)
    print("CORTEX ENTERPRISE DOCUMENTATION GENERATION RESULTS")
    print("="*80)
    print(f"Status: {result.status}")
    print(f"Success: {result.success}")
    print(f"Message: {result.message}")
    print(f"Duration: {result.duration_seconds}s")
    
    if result.data:
        execution_summary = result.data.get("execution_summary", {})
        file_generation = result.data.get("file_generation", {})
        quality_metrics = result.data.get("quality_metrics", {})
        
        print(f"\nFiles Generated: {file_generation.get('total', 0)}")
        print(f"Completion Rate: {quality_metrics.get('completion_rate', 0)}%")
        print(f"Warnings: {quality_metrics.get('warnings_count', 0)}")
        print(f"Errors: {quality_metrics.get('errors_count', 0)}")
        
        next_steps = result.data.get("next_steps", [])
        if next_steps:
            print("\nNext Steps:")
            for i, step in enumerate(next_steps[:5], 1):  # Show first 5 steps
                print(f"  {i}. {step}")
    
    # Exit with appropriate code
    sys.exit(0 if result.success else 1)