"""
Enterprise Documentation Orchestrator Module

Wraps the Enterprise Documentation Orchestrator to integrate with CORTEX operations system.
Generates comprehensive MkDocs documentation with diagrams, guides, and API references.

Features:
    - Architecture diagrams and guides
    - API reference documentation
    - Real Live Data dashboards (conditional)
    - Cross-references and navigation

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import logging
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, Optional

from src.operations.base_operation_module import (
    BaseOperationModule,
    OperationModuleMetadata,
    OperationResult,
    OperationPhase,
    OperationStatus
)

# Add analytics path for Real Live Data generator
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "cortex-brain"))

logger = logging.getLogger(__name__)


class EnterpriseDocumentationOrchestratorModule(BaseOperationModule):
    """
    Orchestrates CORTEX documentation generation.
    
    This module wraps the Enterprise Documentation Orchestrator located at:
    cortex-brain/admin/scripts/documentation/enterprise_documentation_orchestrator.py
    
    Features:
        - Generates MkDocs documentation site
        - Creates architecture diagrams
        - Builds user guides and API references
        - Cross-references and navigation
        - Dry-run mode for validation
    
    Usage:
        # Natural language
        "generate docs"
        "build documentation"
        "generate mkdocs"
        
        # Preview mode
        "generate docs dry run"
    """
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Get module metadata."""
        return OperationModuleMetadata(
            module_id="enterprise_documentation_orchestrator_module",
            name="Enterprise Documentation Orchestrator",
            description="Generate comprehensive MkDocs documentation with diagrams and guides",
            phase=OperationPhase.GENERATION,
            dependencies=[],
            optional_dependencies=[],
            estimated_duration_seconds=120,  # 2 minutes for full docs generation
            tags=["documentation", "mkdocs", "diagrams", "admin"],
            version="1.0.0"
        )
    
    def validate_context(self, context: Dict[str, Any]) -> tuple[bool, str]:
        """
        Validate execution context.
        
        Checks:
            - Project root exists
            - Enterprise documentation orchestrator script exists
            - cortex-brain/admin/ directory exists (admin-only operation)
        """
        project_root = context.get('project_root')
        if not project_root:
            return False, "Project root not specified"
        
        project_root = Path(project_root)
        if not project_root.exists():
            return False, f"Project root does not exist: {project_root}"
        
        # Verify this is CORTEX development repository (admin operation)
        admin_dir = project_root / 'cortex-brain' / 'admin'
        if not admin_dir.exists():
            return False, (
                "Enterprise documentation generation is an admin-only operation. "
                "This operation is only available in the CORTEX development repository."
            )
        
        # Verify orchestrator script exists
        orchestrator_script = project_root / 'cortex-brain' / 'admin' / 'scripts' / 'documentation' / 'enterprise_documentation_orchestrator.py'
        if not orchestrator_script.exists():
            return False, f"Enterprise documentation orchestrator not found: {orchestrator_script}"
        
        return True, "Context validated"
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Execute documentation generation.
        
        Args:
            context: Execution context with:
                - project_root: Project root directory
                - dry_run: Preview mode (optional)
                - profile: Generation profile (quick/standard/comprehensive)
        
        Returns:
            OperationResult with generation status and statistics
        """
        project_root = Path(context.get('project_root', Path.cwd()))
        dry_run = context.get('dry_run', False)
        profile = context.get('profile', 'standard')
        
        try:
            logger.info(f"Starting documentation generation (profile: {profile}, dry_run: {dry_run})")
            
            # Generate Real Live Data dashboards first (if data exists)
            real_live_data_nav = None
            if not dry_run:
                real_live_data_nav = self._generate_real_live_data(project_root)
            
            # Build command
            orchestrator_script = (
                project_root / 'cortex-brain' / 'admin' / 'scripts' / 
                'documentation' / 'enterprise_documentation_orchestrator.py'
            )
            
            cmd = [sys.executable, str(orchestrator_script)]
            
            if dry_run:
                cmd.append('--dry-run')
            
            if profile != 'standard':
                cmd.extend(['--profile', profile])
            
            # Execute orchestrator
            logger.info(f"Executing: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                cwd=str(project_root),
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                # Parse output for statistics
                stats = self._parse_generation_stats(result.stdout)
                
                # Add Real Live Data info to stats
                if real_live_data_nav:
                    stats['real_live_data_generated'] = True
                    stats['real_live_data_apps'] = len(real_live_data_nav.get('Real Live Data', [])) - 1  # -1 for overview
                
                return OperationResult(
                    success=True,
                    status=OperationStatus.COMPLETED,
                    message=f"Documentation generated successfully ({profile} profile)",
                    data={
                        'profile': profile,
                        'dry_run': dry_run,
                        'statistics': stats,
                        'output': result.stdout,
                        'real_live_data_nav': real_live_data_nav
                    },
                    metadata={
                        'module_id': self.get_metadata().module_id,
                        'profile': profile
                    }
                )
            else:
                return OperationResult(
                    success=False,
                    status=OperationStatus.FAILED,
                    message="Documentation generation failed",
                    error=result.stderr or "Unknown error",
                    data={
                        'returncode': result.returncode,
                        'stdout': result.stdout,
                        'stderr': result.stderr
                    }
                )
                
        except subprocess.TimeoutExpired:
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message="Documentation generation timeout",
                error="Operation exceeded 5 minute timeout"
            )
        except Exception as e:
            logger.exception("Documentation generation failed")
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message="Documentation generation error",
                error=str(e)
            )
    
    def _parse_generation_stats(self, output: str) -> Dict[str, Any]:
        """
        Parse generation statistics from orchestrator output.
        
        Args:
            output: Orchestrator stdout
        
        Returns:
            Dictionary with parsed statistics
        """
        stats = {
            'files_generated': 0,
            'diagrams_created': 0,
            'pages_created': 0,
            'duration': None
        }
        
        try:
            # Look for common output patterns
            import re
            
            # Files generated
            files_match = re.search(r'(\d+)\s+files?\s+generated', output, re.IGNORECASE)
            if files_match:
                stats['files_generated'] = int(files_match.group(1))
            
            # Diagrams created
            diagrams_match = re.search(r'(\d+)\s+diagrams?\s+created', output, re.IGNORECASE)
            if diagrams_match:
                stats['diagrams_created'] = int(diagrams_match.group(1))
            
            # Pages created
            pages_match = re.search(r'(\d+)\s+pages?\s+created', output, re.IGNORECASE)
            if pages_match:
                stats['pages_created'] = int(pages_match.group(1))
            
            # Duration
            duration_match = re.search(r'completed in\s+([\d.]+)\s+seconds', output, re.IGNORECASE)
            if duration_match:
                stats['duration'] = float(duration_match.group(1))
                
        except Exception as e:
            logger.warning(f"Failed to parse generation stats: {e}")
        
        return stats
    
    def _generate_real_live_data(self, project_root: Path) -> Optional[Dict]:
        """
        Generate Real Live Data dashboards if analytics data exists.
        
        Args:
            project_root: Project root directory
        
        Returns:
            Navigation structure if data exists, None otherwise
        """
        try:
            from analytics.real_live_data_generator import RealLiveDataGenerator
            
            analytics_root = project_root / 'cortex-brain' / 'analytics'
            docs_output_dir = project_root / 'docs'
            
            generator = RealLiveDataGenerator(analytics_root, docs_output_dir)
            
            # Check if data exists
            if not generator.has_data():
                logger.info("No analytics data found, skipping Real Live Data generation")
                return None
            
            # Generate dashboards
            logger.info("Generating Real Live Data dashboards...")
            result = generator.generate_all_dashboards()
            
            logger.info(
                f"Generated {len(result['app_dashboards'])} app dashboards" +
                (f" + aggregate dashboard" if result['aggregate_dashboard'] else "")
            )
            
            # Return navigation structure
            return generator.get_navigation_structure()
            
        except ImportError as e:
            logger.warning(f"Real Live Data generator not available: {e}")
            return None
        except Exception as e:
            logger.error(f"Error generating Real Live Data: {e}")
            return None


def register() -> BaseOperationModule:
    """Register module for discovery."""
    return EnterpriseDocumentationOrchestratorModule()
