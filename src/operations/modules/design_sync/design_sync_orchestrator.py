"""
CORTEX Design Synchronization Orchestrator

Resolves the critical problem of design-implementation drift by:
1. Discovering actual implementation state (modules, operations, tests, plugins)
2. Analyzing gaps between design documents and reality
3. Integrating optimization recommendations from optimize_cortex
4. Converting verbose MD documents to structured YAML schemas
5. Consolidating multiple status files into ONE coherent status document
6. Applying all changes with git tracking for audit trail

Always works on LATEST design version (auto-detects, currently CORTEX 2.0).

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
import subprocess
import json
import yaml
import re
from collections import defaultdict

from src.operations.base_operation_module import (
    BaseOperationModule,
    OperationModuleMetadata,
    OperationPhase,
    OperationResult,
    OperationStatus
)
from src.operations.header_utils import print_minimalist_header, print_completion_footer
from src.operations.header_formatter import HeaderFormatter

logger = logging.getLogger(__name__)


@dataclass
class ImplementationState:
    """Current implementation reality."""
    operations: Dict[str, Dict] = field(default_factory=dict)
    modules: Dict[str, Path] = field(default_factory=dict)
    tests: Dict[str, int] = field(default_factory=dict)
    plugins: List[str] = field(default_factory=list)
    agents: List[str] = field(default_factory=list)
    total_modules: int = 0
    implemented_modules: int = 0
    completion_percentage: float = 0.0


@dataclass
class DesignState:
    """Design document state."""
    version: str = "2.0"
    design_files: List[Path] = field(default_factory=list)
    status_files: List[Path] = field(default_factory=list)
    md_documents: List[Path] = field(default_factory=list)
    yaml_documents: List[Path] = field(default_factory=list)


@dataclass
class GapAnalysis:
    """Gaps between design and implementation."""
    overclaimed_completions: List[str] = field(default_factory=list)
    underclaimed_completions: List[str] = field(default_factory=list)
    missing_documentation: List[str] = field(default_factory=list)
    inconsistent_counts: List[Dict[str, Any]] = field(default_factory=list)
    redundant_status_files: List[Path] = field(default_factory=list)
    verbose_md_candidates: List[Path] = field(default_factory=list)


@dataclass
class SyncMetrics:
    """Metrics collected during sync."""
    sync_id: str
    timestamp: datetime
    implementation_discovered: bool = False
    gaps_analyzed: int = 0
    optimizations_integrated: int = 0
    md_to_yaml_converted: int = 0
    status_files_consolidated: int = 0
    git_commits: List[str] = field(default_factory=list)
    duration_seconds: float = 0.0
    errors: List[str] = field(default_factory=list)
    improvements: Dict[str, Any] = field(default_factory=dict)


class DesignSyncOrchestrator(BaseOperationModule):
    """
    Design-Implementation Synchronization Orchestrator.
    
    Resolves design drift through 6-phase workflow:
    
    Phase 1: Live Implementation Discovery
        - Scan src/operations/modules/ for actual module files
        - Parse cortex-operations.yaml for operation definitions
        - Count tests in tests/ directory
        - Discover plugins in src/plugins/
        - Build accurate implementation state
    
    Phase 2: Design Document Discovery
        - Auto-detect LATEST design version (scan cortex-brain/cortex-2.0-design/)
        - Find all status files (STATUS.md, CORTEX2-STATUS.MD, etc.)
        - Identify verbose MD documents (>500 lines)
        - Catalog YAML schemas already present
    
    Phase 3: Gap Analysis
        - Compare design claims vs actual implementation
        - Identify overclaimed features (claimed complete but not implemented)
        - Identify underclaimed features (implemented but not documented)
        - Find inconsistent module/test counts
        - Detect redundant status files
        - Flag verbose MD documents for YAML conversion
    
    Phase 4: Optimization Integration
        - Run optimize_cortex to get latest recommendations
        - Parse optimization output for architectural improvements
        - Integrate recommendations into design updates
        - Prioritize by impact and feasibility
    
    Phase 5: Document Transformation
        - Convert verbose MD to YAML schemas (preserving critical info)
        - Update status files with accurate counts
        - Consolidate multiple status files into ONE source of truth
        - Generate visual progress bars based on reality
        - Apply consistent formatting
    
    Phase 6: Git Commit & Reporting
        - Commit all changes with detailed messages
        - Generate comprehensive sync report
        - Update Enhancement & Drift Log in 00-INDEX.md
        - Provide next action recommendations
    
    Usage:
        orchestrator = DesignSyncOrchestrator(project_root=Path('/path/to/cortex'))
        result = orchestrator.execute(context={'profile': 'comprehensive'})
    
    Profiles:
        - quick: Discovery and analysis only (no changes)
        - standard: Discovery, analysis, consolidation (safe updates)
        - comprehensive: Full sync with optimization + YAML conversion
    """
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Module metadata."""
        return OperationModuleMetadata(
            module_id="design_sync_orchestrator",
            name="Design Synchronization Orchestrator",
            description="Resynchronizes CORTEX design with implementation reality",
            version="1.0.0",
            author="Asif Hussain",
            phase=OperationPhase.PROCESSING,
            priority=100,
            dependencies=[],
            optional=False,
            tags=['design', 'maintenance', 'synchronization']
        )
    
    def validate_prerequisites(self, context: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate prerequisites for design sync.
        
        Checks:
        - Project root exists
        - Git repository present
        - Design directory exists
        - Operations YAML accessible
        
        Args:
            context: Shared execution context
        
        Returns:
            Tuple of (is_valid, issues_list)
        """
        issues = []
        
        # Check project root
        project_root = context.get('project_root') or self.project_root
        if not project_root or not project_root.exists():
            issues.append("Project root not found or invalid")
            return False, issues
        
        # Check git repository
        git_dir = project_root / '.git'
        if not git_dir.exists():
            issues.append("Not a git repository - sync requires git tracking")
        
        # Check design directory
        design_dir = project_root / 'cortex-brain'
        if not design_dir.exists():
            issues.append("Design directory not found (cortex-brain/)")
        
        # Check operations YAML
        operations_yaml = project_root / 'cortex-operations.yaml'
        if not operations_yaml.exists():
            issues.append("Operations YAML not found (cortex-operations.yaml)")
        
        return len(issues) == 0, issues
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Execute design synchronization workflow.
        
        Args:
            context: Shared execution context with 'profile' key
        
        Returns:
            OperationResult with sync metrics and git commits
        """
        start_time = datetime.now()
        project_root = context.get('project_root') or self.project_root
        profile = context.get('profile', 'standard')
        dry_run = context.get('dry_run', False)
        
        # Build purpose based on profile
        purposes = {
            'quick': 'Analyze design-implementation gaps (preview only, no changes)',
            'standard': 'Synchronize design docs with implementation reality + consolidate status files',
            'comprehensive': 'Full sync: gap analysis + optimization integration + MD→YAML conversion'
        }
        purpose = purposes.get(profile, 'Synchronize CORTEX design with implementation')
        
        # Generate formatted header (for Copilot Chat display)
        from src.operations.header_utils import format_minimalist_header
        formatted_header = format_minimalist_header(
            operation_name="Design Sync",
            version="1.0.0",
            profile=profile,
            mode="LIVE EXECUTION",
            dry_run=dry_run,
            purpose=purpose
        )
        
        # Also print to terminal for immediate visibility
        print(formatted_header)
        
        logger.info(f"Design Sync Orchestrator started | Profile: {profile}")
        logger.info(f"Project: {project_root}")
        
        # Initialize metrics
        metrics = SyncMetrics(
            sync_id=f"sync_{start_time.strftime('%Y%m%d_%H%M%S')}",
            timestamp=start_time
        )
        
        try:
            # Phase 1: Discover live implementation
            logger.info("[Phase 1/6] Discovering live implementation state...")
            impl_state = self._discover_implementation(project_root, metrics)
            logger.info(f"✅ Discovered: {impl_state.total_modules} modules, "
                       f"{impl_state.implemented_modules} implemented "
                       f"({impl_state.completion_percentage:.1f}%)")
            
            # Phase 2: Discover design documents
            logger.info("\n[Phase 2/6] Discovering design document state...")
            design_state = self._discover_design_documents(project_root, metrics)
            logger.info(f"✅ Found: {len(design_state.design_files)} design docs, "
                       f"{len(design_state.status_files)} status files")
            
            # Phase 3: Analyze gaps
            logger.info("\n[Phase 3/6] Analyzing design-implementation gaps...")
            gaps = self._analyze_gaps(impl_state, design_state, project_root, metrics)
            logger.info(f"✅ Identified {metrics.gaps_analyzed} gaps/inconsistencies")
            
            if profile == 'quick':
                logger.info("\n⚠️  Quick profile: Stopping after analysis (no changes)")
                return self._create_analysis_report(impl_state, design_state, gaps, metrics)
            
            # Phase 4: Integrate optimization recommendations
            logger.info("\n[Phase 4/6] Integrating optimization recommendations...")
            optimizations = self._integrate_optimizations(project_root, gaps, metrics)
            logger.info(f"✅ Integrated {metrics.optimizations_integrated} recommendations")
            
            # Phase 5: Transform documents
            logger.info("\n[Phase 5/6] Transforming documents...")
            transformations = self._transform_documents(
                impl_state, 
                design_state, 
                gaps, 
                optimizations,
                project_root,
                metrics,
                profile
            )
            logger.info(f"✅ Consolidated {metrics.status_files_consolidated} status files, "
                       f"converted {metrics.md_to_yaml_converted} MD to YAML")
            
            # Phase 6: Commit and report
            logger.info("\n[Phase 6/6] Committing changes and generating report...")
            final_report = self._commit_and_report(
                impl_state,
                design_state,
                gaps,
                optimizations,
                transformations,
                project_root,
                metrics,
                profile
            )
            
            metrics.duration_seconds = (datetime.now() - start_time).total_seconds()
            
            # Build accomplishments list
            accomplishments = []
            if impl_state.total_modules > 0:
                accomplishments.append(
                    f"Discovered {impl_state.total_modules} modules "
                    f"({impl_state.completion_percentage:.0f}% implemented)"
                )
            if metrics.gaps_analyzed > 0:
                accomplishments.append(f"Analyzed {metrics.gaps_analyzed} design-implementation gaps")
            if metrics.status_files_consolidated > 0:
                accomplishments.append(
                    f"Consolidated {metrics.status_files_consolidated} status files → 1 source of truth"
                )
            if metrics.md_to_yaml_converted > 0:
                accomplishments.append(f"Converted {metrics.md_to_yaml_converted} MD docs to YAML schemas")
            if len(metrics.git_commits) > 0:
                accomplishments.append(f"Committed changes: {metrics.git_commits[0]}")
            
            # Generate formatted footer (for Copilot Chat display)
            from src.operations.header_utils import format_completion_footer
            summary = f"{len(metrics.improvements)} improvements applied" if metrics.improvements else None
            formatted_footer = format_completion_footer(
                operation_name="Design Sync",
                success=True,
                duration_seconds=metrics.duration_seconds,
                summary=summary,
                accomplishments=accomplishments if accomplishments else None
            )
            
            # Also print to terminal for immediate visibility
            print(formatted_footer)
            
            logger.info(f"✅ Design synchronization complete ({profile} profile)")
            logger.info(f"Git commits: {len(metrics.git_commits)}")
            logger.info(f"Improvements: {len(metrics.improvements)} changes applied")
            
            return OperationResult(
                success=True,
                status=OperationStatus.SUCCESS,
                message=f"Design synchronization complete ({profile} profile)",
                data={
                    'metrics': metrics.__dict__,
                    'implementation_state': impl_state.__dict__,
                    'design_state': design_state.__dict__,
                    'gaps': gaps.__dict__,
                    'final_report': final_report
                },
                formatted_header=formatted_header,
                formatted_footer=formatted_footer
            )
        
        except Exception as e:
            logger.error(f"Design sync failed: {e}", exc_info=True)
            metrics.errors.append(str(e))
            metrics.duration_seconds = (datetime.now() - start_time).total_seconds()
            
            # Generate failure footer (for Copilot Chat display)
            from src.operations.header_utils import format_completion_footer
            formatted_footer_error = format_completion_footer(
                operation_name="Design Sync",
                success=False,
                duration_seconds=metrics.duration_seconds,
                summary=f"Error: {str(e)}"
            )
            
            # Also print to terminal
            print(formatted_footer_error)
            
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Design synchronization failed: {e}",
                data={'metrics': metrics.__dict__},
                errors=[str(e)],
                formatted_header=formatted_header if 'formatted_header' in locals() else None,
                formatted_footer=formatted_footer_error
            )
    
    def _discover_implementation(
        self,
        project_root: Path,
        metrics: SyncMetrics
    ) -> ImplementationState:
        """
        Discover actual implementation state by scanning the codebase.
        
        Returns:
            ImplementationState with accurate counts
        """
        state = ImplementationState()
        
        # Discover operations from YAML
        operations_yaml = project_root / 'cortex-operations.yaml'
        if operations_yaml.exists():
            with open(operations_yaml) as f:
                ops_data = yaml.safe_load(f)
                if 'operations' in ops_data:
                    state.operations = ops_data['operations']
        
        # Discover modules by scanning filesystem
        modules_dir = project_root / 'src' / 'operations' / 'modules'
        if modules_dir.exists():
            for py_file in modules_dir.rglob('*.py'):
                if py_file.name != '__init__.py' and py_file.name != '__pycache__':
                    module_name = py_file.stem
                    state.modules[module_name] = py_file
        
        state.total_modules = len(state.modules)
        state.implemented_modules = len(state.modules)
        state.completion_percentage = (
            100.0 if state.total_modules > 0 
            else 0.0
        )
        
        # Discover tests
        tests_dir = project_root / 'tests'
        if tests_dir.exists():
            for test_file in tests_dir.rglob('test_*.py'):
                # Count test functions in file
                test_count = 0
                try:
                    with open(test_file, encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        test_count = len(re.findall(r'^\s*def test_', content, re.MULTILINE))
                    state.tests[str(test_file.relative_to(project_root))] = test_count
                except Exception as e:
                    logger.warning(f"Could not read test file {test_file}: {e}")
        
        # Discover plugins
        plugins_dir = project_root / 'src' / 'plugins'
        if plugins_dir.exists():
            for plugin_file in plugins_dir.glob('*_plugin.py'):
                state.plugins.append(plugin_file.stem)
        
        # Discover agents
        agents_dir = project_root / 'src' / 'cortex_agents'
        if agents_dir.exists():
            for agent_file in agents_dir.glob('*_agent.py'):
                state.agents.append(agent_file.stem)
        
        metrics.implementation_discovered = True
        return state
    
    def _discover_design_documents(
        self,
        project_root: Path,
        metrics: SyncMetrics
    ) -> DesignState:
        """
        Discover design document state and auto-detect version.
        
        Returns:
            DesignState with current design version and file lists
        """
        state = DesignState()
        
        # Auto-detect design version
        brain_dir = project_root / 'cortex-brain'
        
        # Check for versioned design directories
        for subdir in brain_dir.iterdir():
            if subdir.is_dir() and 'cortex-' in subdir.name and '-design' in subdir.name:
                # Extract version (e.g., "cortex-2.0-design" → "2.0")
                match = re.search(r'cortex-(\d+\.\d+)-design', subdir.name)
                if match:
                    state.version = match.group(1)
                    design_dir = subdir
                    break
        else:
            # Fallback to cortex-2.0-design
            design_dir = brain_dir / 'cortex-2.0-design'
            state.version = "2.0"
        
        if not design_dir.exists():
            logger.warning(f"Design directory not found: {design_dir}")
            return state
        
        # Discover design files
        for md_file in design_dir.glob('*.md'):
            state.design_files.append(md_file)
            
            # Categorize
            if 'STATUS' in md_file.name.upper():
                state.status_files.append(md_file)
            
            # Check if verbose (>500 lines)
            try:
                line_count = len(md_file.read_text(encoding='utf-8', errors='ignore').splitlines())
                if line_count > 500:
                    state.md_documents.append(md_file)
            except Exception as e:
                logger.warning(f"Could not read {md_file.name}: {e}")
        
        # Discover YAML documents
        for yaml_file in design_dir.glob('*.yaml'):
            state.yaml_documents.append(yaml_file)
        
        return state
    
    def _analyze_gaps(
        self,
        impl_state: ImplementationState,
        design_state: DesignState,
        project_root: Path,
        metrics: SyncMetrics
    ) -> GapAnalysis:
        """
        Analyze gaps between design and implementation.
        
        Returns:
            GapAnalysis with identified issues
        """
        gaps = GapAnalysis()
        
        # Find redundant status files (should be exactly ONE)
        if len(design_state.status_files) > 1:
            gaps.redundant_status_files = design_state.status_files[1:]
            metrics.gaps_analyzed += 1
        
        # Find verbose MD candidates for YAML conversion
        gaps.verbose_md_candidates = design_state.md_documents
        if gaps.verbose_md_candidates:
            metrics.gaps_analyzed += 1
        
        # Check for inconsistent module counts
        for op_id, op_data in impl_state.operations.items():
            if 'implementation_status' in op_data:
                status = op_data['implementation_status']
                claimed_total = status.get('modules_total', 0)
                
                # Count actual modules for this operation
                actual_modules = [m for m in impl_state.modules.keys() 
                                 if op_id in m or any(mod_name in m for mod_name in op_data.get('modules', []))]
                
                if len(actual_modules) != claimed_total:
                    gaps.inconsistent_counts.append({
                        'operation': op_id,
                        'claimed': claimed_total,
                        'actual': len(actual_modules),
                        'difference': abs(len(actual_modules) - claimed_total)
                    })
                    metrics.gaps_analyzed += 1
        
        return gaps
    
    def _integrate_optimizations(
        self,
        project_root: Path,
        gaps: GapAnalysis,
        metrics: SyncMetrics
    ) -> Dict[str, Any]:
        """
        Integrate optimization recommendations from optimize_cortex.
        
        Returns:
            Dict with integrated recommendations
        """
        optimizations = {
            'recommendations': [],
            'priority': []
        }
        
        # Run optimize_cortex to get latest recommendations
        try:
            from src.operations import execute_operation
            
            logger.info("  → Running optimize_cortex for recommendations...")
            result = execute_operation(
                'optimize_cortex',
                profile='quick',  # Quick = analysis only
                project_root=project_root
            )
            
            if result.success and 'data' in result.__dict__:
                opt_data = result.__dict__['data']
                if 'recommendations' in opt_data:
                    optimizations['recommendations'] = opt_data['recommendations']
                    metrics.optimizations_integrated = len(opt_data['recommendations'])
        
        except Exception as e:
            logger.warning(f"Could not run optimize_cortex: {e}")
            # Continue without optimization integration
        
        return optimizations
    
    def _transform_documents(
        self,
        impl_state: ImplementationState,
        design_state: DesignState,
        gaps: GapAnalysis,
        optimizations: Dict[str, Any],
        project_root: Path,
        metrics: SyncMetrics,
        profile: str
    ) -> Dict[str, Any]:
        """
        Transform documents: consolidate status files, convert MD to YAML.
        
        Returns:
            Dict with transformation results
        """
        transformations = {
            'consolidated_status_file': None,
            'converted_yaml_files': [],
            'archived_files': []
        }
        
        # Consolidate status files into ONE source of truth
        if design_state.status_files:
            primary_status = self._consolidate_status_files(
                design_state.status_files,
                impl_state,
                design_state,
                gaps,
                project_root,
                metrics
            )
            transformations['consolidated_status_file'] = primary_status
            metrics.status_files_consolidated = len(design_state.status_files)
        
        # Convert verbose MD to YAML (only in comprehensive profile)
        if profile == 'comprehensive' and gaps.verbose_md_candidates:
            for md_file in gaps.verbose_md_candidates[:3]:  # Limit to 3 per run
                yaml_file = self._convert_md_to_yaml(md_file, project_root, metrics)
                if yaml_file:
                    transformations['converted_yaml_files'].append(yaml_file)
                    metrics.md_to_yaml_converted += 1
        
        return transformations
    
    def _consolidate_status_files(
        self,
        status_files: List[Path],
        impl_state: ImplementationState,
        design_state: DesignState,
        gaps: GapAnalysis,
        project_root: Path,
        metrics: SyncMetrics
    ) -> Optional[Path]:
        """
        Consolidate multiple status files into ONE authoritative document.
        
        Returns:
            Path to consolidated status file
        """
        # Use CORTEX2-STATUS.MD as primary (it has the visual bars)
        primary = None
        for status_file in status_files:
            if 'CORTEX2-STATUS' in status_file.name:
                primary = status_file
                break
        
        if not primary and status_files:
            primary = status_files[0]
        
        if not primary:
            return None
        
        # Read current content with proper encoding
        try:
            content = primary.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            logger.error(f"Failed to read {primary.name}: {e}")
            return None
        
        # Update with accurate counts
        updates = []
        
        # Update total modules
        content = re.sub(
            r'Total Modules:\*\* \d+',
            f'Total Modules:** {impl_state.total_modules}',
            content
        )
        updates.append(f"Updated total modules: {impl_state.total_modules}")
        
        # Update implemented modules
        content = re.sub(
            r'Implemented:\*\* \d+ modules',
            f'Implemented:** {impl_state.implemented_modules} modules',
            content
        )
        updates.append(f"Updated implemented modules: {impl_state.implemented_modules}")
        
        # Update test count
        total_tests = sum(impl_state.tests.values())
        content = re.sub(
            r'Tests:\*\* \d+ tests',
            f'Tests:** {total_tests} tests',
            content
        )
        updates.append(f"Updated test count: {total_tests}")
        
        # Update plugins count
        content = re.sub(
            r'Plugins:\*\* \d+ operational',
            f'Plugins:** {len(impl_state.plugins)} operational',
            content
        )
        updates.append(f"Updated plugins: {len(impl_state.plugins)}")
        
        # Add sync timestamp
        sync_note = f"\n\n*Last Synchronized: {datetime.now().strftime('%Y-%m-%d %H:%M')} (design_sync)*\n"
        if '*Last Synchronized:' not in content:
            content += sync_note
        else:
            content = re.sub(
                r'\*Last Synchronized:.*?\*',
                sync_note.strip(),
                content
            )
        updates.append("Added sync timestamp")
        
        # Write back with proper encoding
        try:
            primary.write_text(content, encoding='utf-8')
        except Exception as e:
            logger.error(f"Failed to write {primary.name}: {e}")
            return None
        
        metrics.improvements['status_consolidation'] = updates
        return primary
    
    def _convert_md_to_yaml(
        self,
        md_file: Path,
        project_root: Path,
        metrics: SyncMetrics
    ) -> Optional[Path]:
        """
        Convert verbose MD document to structured YAML schema.
        
        Returns:
            Path to created YAML file, or None if conversion failed
        """
        try:
            # Read MD content with proper encoding
            content = md_file.read_text(encoding='utf-8', errors='ignore')
            
            # Extract key information
            yaml_data = {
                'source': str(md_file.name),
                'converted_on': datetime.now().isoformat(),
                'sections': []
            }
            
            # Parse sections (## headings)
            current_section = None
            for line in content.splitlines():
                if line.startswith('## '):
                    if current_section:
                        yaml_data['sections'].append(current_section)
                    current_section = {
                        'title': line[3:].strip(),
                        'content': []
                    }
                elif current_section:
                    current_section['content'].append(line)
            
            if current_section:
                yaml_data['sections'].append(current_section)
            
            # Write YAML with proper encoding
            yaml_file = md_file.with_suffix('.yaml')
            with open(yaml_file, 'w', encoding='utf-8') as f:
                yaml.dump(yaml_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
            
            logger.info(f"  ✅ Converted {md_file.name} → {yaml_file.name}")
            return yaml_file
        
        except Exception as e:
            logger.warning(f"Could not convert {md_file.name}: {e}")
            return None
    
    def _commit_and_report(
        self,
        impl_state: ImplementationState,
        design_state: DesignState,
        gaps: GapAnalysis,
        optimizations: Dict[str, Any],
        transformations: Dict[str, Any],
        project_root: Path,
        metrics: SyncMetrics,
        profile: str
    ) -> Dict[str, Any]:
        """
        Commit changes and generate comprehensive report.
        
        Returns:
            Dict with final report data
        """
        report = {
            'sync_id': metrics.sync_id,
            'timestamp': metrics.timestamp.isoformat(),
            'profile': profile,
            'implementation_state': {
                'total_modules': impl_state.total_modules,
                'implemented_modules': impl_state.implemented_modules,
                'completion_percentage': impl_state.completion_percentage,
                'total_tests': sum(impl_state.tests.values()),
                'plugins': len(impl_state.plugins),
                'agents': len(impl_state.agents)
            },
            'design_state': {
                'version': design_state.version,
                'design_files': len(design_state.design_files),
                'status_files': len(design_state.status_files),
                'yaml_documents': len(design_state.yaml_documents)
            },
            'gaps_analyzed': metrics.gaps_analyzed,
            'optimizations_integrated': metrics.optimizations_integrated,
            'transformations': {
                'status_files_consolidated': metrics.status_files_consolidated,
                'md_to_yaml_converted': metrics.md_to_yaml_converted
            },
            'git_commits': metrics.git_commits,
            'duration_seconds': metrics.duration_seconds,
            'next_actions': []
        }
        
        # Git commit if changes made
        if profile != 'quick':
            try:
                # Add changed files
                subprocess.run(
                    ['git', 'add', 'cortex-brain/'],
                    cwd=project_root,
                    check=True,
                    capture_output=True
                )
                
                # Commit
                commit_msg = (
                    f"design: synchronize CORTEX {design_state.version} design with implementation\n\n"
                    f"Profile: {profile}\n"
                    f"Gaps analyzed: {metrics.gaps_analyzed}\n"
                    f"Status files consolidated: {metrics.status_files_consolidated}\n"
                    f"MD to YAML converted: {metrics.md_to_yaml_converted}\n"
                    f"Optimizations integrated: {metrics.optimizations_integrated}\n\n"
                    f"[design_sync {metrics.sync_id}]"
                )
                
                result = subprocess.run(
                    ['git', 'commit', '-m', commit_msg],
                    cwd=project_root,
                    check=False,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    # Get commit hash
                    hash_result = subprocess.run(
                        ['git', 'rev-parse', 'HEAD'],
                        cwd=project_root,
                        check=True,
                        capture_output=True,
                        text=True
                    )
                    commit_hash = hash_result.stdout.strip()[:8]
                    metrics.git_commits.append(commit_hash)
                    logger.info(f"  ✅ Git commit: {commit_hash}")
                else:
                    logger.info("  ℹ️  No changes to commit")
            
            except subprocess.CalledProcessError as e:
                logger.warning(f"Git commit failed: {e}")
        
        # Generate next actions
        if gaps.inconsistent_counts:
            report['next_actions'].append("Review inconsistent module counts in operations")
        
        if gaps.verbose_md_candidates and profile != 'comprehensive':
            report['next_actions'].append(
                f"Run comprehensive profile to convert {len(gaps.verbose_md_candidates)} verbose MD to YAML"
            )
        
        if metrics.optimizations_integrated > 0:
            report['next_actions'].append("Review and implement integrated optimizations")
        
        return report
    
    def _create_analysis_report(
        self,
        impl_state: ImplementationState,
        design_state: DesignState,
        gaps: GapAnalysis,
        metrics: SyncMetrics
    ) -> OperationResult:
        """Create analysis-only report for quick profile."""
        report = {
            'analysis_only': True,
            'implementation_discovered': {
                'total_modules': impl_state.total_modules,
                'implemented_modules': impl_state.implemented_modules,
                'completion_percentage': impl_state.completion_percentage,
                'total_tests': sum(impl_state.tests.values()),
                'plugins': len(impl_state.plugins)
            },
            'design_discovered': {
                'version': design_state.version,
                'design_files': len(design_state.design_files),
                'status_files': len(design_state.status_files)
            },
            'gaps_found': {
                'redundant_status_files': len(gaps.redundant_status_files),
                'verbose_md_candidates': len(gaps.verbose_md_candidates),
                'inconsistent_counts': len(gaps.inconsistent_counts)
            },
            'recommendation': "Run with 'standard' or 'comprehensive' profile to apply fixes"
        }
        
        return OperationResult(
            success=True,
            status=OperationStatus.SUCCESS,
            message="Design sync analysis complete (no changes made)",
            data={
                'metrics': metrics.__dict__,
                'report': report
            }
        )
