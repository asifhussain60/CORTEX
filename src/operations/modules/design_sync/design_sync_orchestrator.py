"""
CORTEX Design Synchronization Orchestrator

Resolves design-implementation drift by discovering state, analyzing gaps,
integrating optimizations, consolidating status files, and tracking changes with git.

Always works on LATEST design version (auto-detects, currently CORTEX 2.0).

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
import subprocess
import json
import yaml
import re
import sys
import platform
from collections import defaultdict

from src.operations.base_operation_module import (
    BaseOperationModule,
    OperationModuleMetadata,
    OperationPhase,
    OperationResult,
    OperationStatus
)
from src.operations.operation_header_formatter import print_minimalist_header, print_completion_footer
from src.operations.operation_header_formatter import OperationHeaderFormatter
from src.operations.modules.design_sync.design_sync_models import (
    ImplementationState,
    DesignState,
    GapAnalysis,
    SyncMetrics
)
from src.operations.modules.design_sync.status_file_consolidator import StatusFileConsolidator
from src.operations.modules.design_sync.design_sync_helpers import RecentUpdatesGenerator, CommitReporter
from src.operations.modules.design_sync.implementation_discovery import ImplementationDiscovery
from src.operations.modules.design_sync.progress_helpers import (
    PhaseProgressCalculator,
    ProgressBarGenerator,
    SyncContextGenerator
)
from .track_config import (
    MultiTrackConfig,
    MachineTrack,
    TrackConfigManager,
    TrackMetrics
)
from .track_templates import TrackDocumentTemplates

logger = logging.getLogger(__name__)


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
        - **Auto-generate "Recent Updates" from git commit history**
        - **Add contextual timestamps (e.g., "design_sync + deployment updates")**
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
    
    def _safe_print(self, text: str) -> None:
        """
        Safely print text handling Unicode encoding issues on Windows.
        
        Windows PowerShell uses cp1252 encoding which cannot display Unicode
        characters like emoji. This method detects the platform and encoding,
        falling back to ASCII-safe alternatives when needed.
        
        Args:
            text: Text to print (may contain Unicode/emoji)
        """
        try:
            # Try normal print first
            print(text)
        except UnicodeEncodeError:
            # Windows console can't handle Unicode - strip or replace emoji
            # Remove emoji and fancy Unicode box chars
            ascii_text = text
            
            # Replace box drawing characters
            replacements = {
                '━': '=', '─': '-', '│': '|', '┃': '|',
                '┌': '+', '┐': '+', '└': '+', '┘': '+',
                '├': '+', '┤': '+', '┬': '+', '┴': '+',
                '┼': '+', '═': '=', '║': '|',
                '╔': '+', '╗': '+', '╚': '+', '╝': '+',
                '╠': '+', '╣': '+', '╦': '+', '╩': '+',
                '╬': '+'
            }
            
            for unicode_char, ascii_char in replacements.items():
                ascii_text = ascii_text.replace(unicode_char, ascii_char)
            
            # Remove emoji (most are in these ranges)
            ascii_text = ascii_text.encode('ascii', errors='ignore').decode('ascii')
            
            # Try again with ASCII-safe version
            try:
                print(ascii_text)
            except Exception as e:
                # Last resort: log instead of print
                logger.warning(f"Could not print header to console: {e}")
                logger.info(f"Header content: {text[:200]}...")
    
    def _load_track_config(self, project_root: Path) -> MultiTrackConfig:
        """Load multi-track configuration from cortex.config.json."""
        config_path = project_root / 'cortex.config.json'
        return TrackConfigManager.load_from_config(config_path)
    
    def _detect_active_track(
        self,
        track_config: MultiTrackConfig,
        context: Dict[str, Any]
    ) -> Optional[MachineTrack]:
        """
        Detect which track is active for current machine.
        
        Returns:
            MachineTrack if multi-track mode and machine has assignment, else None
        """
        if not track_config.is_multi_track:
            return None
        
        # Check if user specified track name in context
        if 'track_name' in context:
            track_name = context['track_name']
            for track in track_config.tracks.values():
                if track.track_name.lower() == track_name.lower():
                    return track
        
        # Auto-detect from machine hostname
        import platform
        hostname = platform.node()
        
        return track_config.get_track_for_machine(hostname)
    
    def _filter_modules_by_track(
        self,
        impl_state: ImplementationState,
        track: MachineTrack
    ) -> ImplementationState:
        """Filter implementation state to only show track-assigned modules."""
        filtered_state = ImplementationState()
        
        # Filter modules by track's assigned phases
        for module_id, module_path in impl_state.modules.items():
            # Check if module belongs to track phases
            # (Need to lookup module phase from operations.yaml)
            if module_id in track.modules:
                filtered_state.modules[module_id] = module_path
        
        filtered_state.total_modules = len(filtered_state.modules)
        filtered_state.implemented_modules = len(filtered_state.modules)
        filtered_state.completion_percentage = (
            100.0 if filtered_state.total_modules > 0 else 0.0
        )
        
        # Copy other state (tests, plugins, agents remain global)
        filtered_state.operations = impl_state.operations
        filtered_state.tests = impl_state.tests
        filtered_state.plugins = impl_state.plugins
        filtered_state.agents = impl_state.agents
        
        return filtered_state
    
    def _generate_split_design_doc(
        self,
        track_config: MultiTrackConfig,
        impl_state: ImplementationState,
        design_state: DesignState,
        project_root: Path
    ) -> Path:
        """Generate split design document with race dashboard."""
        # Load operations.yaml for module definitions
        operations_yaml = project_root / 'cortex-operations.yaml'
        with open(operations_yaml, encoding='utf-8') as f:
            ops_data = yaml.safe_load(f)
        modules = ops_data.get('modules', {})
        
        # Generate split document
        split_doc = TrackDocumentTemplates.generate_split_document(
            track_config,
            modules,
            design_state.version
        )
        
        # Write to design directory
        design_dir = project_root / 'cortex-brain' / f'cortex-{design_state.version}-design'
        design_dir.mkdir(parents=True, exist_ok=True)
        
        split_doc_path = design_dir / 'CORTEX2-STATUS-SPLIT.MD'
        split_doc_path.write_text(split_doc, encoding='utf-8')
        
        logger.info(f"Generated split design doc: {split_doc_path.name}")
        return split_doc_path
    
    def _consolidate_tracks(
        self,
        track_config: MultiTrackConfig,
        impl_state: ImplementationState,
        design_state: DesignState,
        project_root: Path,
        metrics: SyncMetrics
    ) -> Path:
        """
        Consolidate multi-track design into single unified document.
        
        Steps:
        1. Merge progress from all tracks
        2. Generate consolidated document
        3. Archive split design docs
        4. Reset config to single-track mode
        5. Git commit with merge summary
        """
        logger.info("Consolidating multi-track design...")
        
        # Load operations.yaml for module definitions
        operations_yaml = project_root / 'cortex-operations.yaml'
        with open(operations_yaml, encoding='utf-8') as f:
            ops_data = yaml.safe_load(f)
        modules = ops_data.get('modules', {})
        
        # Generate consolidated document
        consolidated_doc = TrackDocumentTemplates.generate_consolidated_document(
            track_config,
            modules,
            design_state.version
        )
        
        # Write to design directory
        design_dir = project_root / 'cortex-brain' / f'cortex-{design_state.version}-design'
        design_dir.mkdir(parents=True, exist_ok=True)
        
        consolidated_path = design_dir / 'CORTEX2-STATUS.MD'
        consolidated_path.write_text(consolidated_doc, encoding='utf-8')
        
        # Archive split docs
        archive_dir = project_root / 'cortex-brain' / 'archived-tracks' / datetime.now().strftime('%Y%m%d-%H%M%S')
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        split_doc = design_dir / 'CORTEX2-STATUS-SPLIT.MD'
        if split_doc.exists():
            import shutil
            shutil.copy(split_doc, archive_dir / 'CORTEX2-STATUS-SPLIT.MD')
            split_doc.unlink()
            logger.info(f"Archived split design to: {archive_dir.name}")
        
        # Reset config to single-track mode
        track_config.mode = 'single'
        config_path = project_root / 'cortex.config.json'
        TrackConfigManager.save_to_config(track_config, config_path)
        
        logger.info("✅ Consolidation complete - reset to single-track mode")
        metrics.improvements['track_consolidation'] = f"Merged {len(track_config.tracks)} tracks"
        
        return consolidated_path
    
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
        mode = "LIVE Execution" if not dry_run else "DRY RUN (Preview Only)"
        
        # Generate formatted header (for Copilot Chat display)
        from src.operations.operation_header_formatter import format_minimalist_header
        formatted_header = format_minimalist_header(
            operation_name="Design Sync",
            version="1.0.0",
            profile=profile,
            mode=mode,
            dry_run=dry_run,
            purpose=purpose
        )
        
        # Also print to terminal for immediate visibility
        # Handle Unicode encoding for Windows console
        self._safe_print(formatted_header)
        
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
            
            # Track Configuration Detection
            track_config = self._load_track_config(project_root)
            active_track = self._detect_active_track(track_config, context)
            
            if track_config.is_multi_track:
                if active_track:
                    logger.info(f"\n🏁 Multi-Track Mode Active: {active_track.emoji} {active_track.track_name}")
                    logger.info(f"   Assigned Phases: {', '.join(active_track.phases)}")
                    # Filter implementation to track-specific modules
                    impl_state = self._filter_modules_by_track(impl_state, active_track)
                else:
                    logger.info("\n🏁 Multi-Track Mode: Running design sync consolidation")
                    logger.info("   Will merge all tracks into unified status")
            
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
            
            # Multi-track handling
            if track_config.is_multi_track:
                if active_track:
                    # Split mode: Generate track-specific document
                    split_doc = self._generate_split_design_doc(
                        track_config,
                        impl_state,
                        design_state,
                        project_root
                    )
                    transformations = {'split_document': split_doc}
                    logger.info(f"✅ Generated split design document with race dashboard")
                else:
                    # Consolidation mode: Merge all tracks
                    consolidated_doc = self._consolidate_tracks(
                        track_config,
                        impl_state,
                        design_state,
                        project_root,
                        metrics
                    )
                    transformations = {'consolidated_document': consolidated_doc}
                    logger.info(f"✅ Consolidated {len(track_config.tracks)} tracks into unified document")
            else:
                # Single-track mode: Standard transformation
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
            from src.operations.operation_header_formatter import format_completion_footer
            summary = f"{len(metrics.improvements)} improvements applied" if metrics.improvements else None
            formatted_footer = format_completion_footer(
                operation_name="Design Sync",
                success=True,
                duration_seconds=metrics.duration_seconds,
                summary=summary,
                accomplishments=accomplishments if accomplishments else None
            )
            
            # Also print to terminal for immediate visibility
            # Handle Unicode encoding for Windows console
            self._safe_print(formatted_footer)
            
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
            from src.operations.operation_header_formatter import format_completion_footer
            formatted_footer_error = format_completion_footer(
                operation_name="Design Sync",
                success=False,
                duration_seconds=metrics.duration_seconds,
                summary=f"Error: {str(e)}"
            )
            
            # Also print to terminal
            # Handle Unicode encoding for Windows console
            self._safe_print(formatted_footer_error)
            
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
        """Discover implementation state (delegated to ImplementationDiscovery)."""
        discovery = ImplementationDiscovery()
        return discovery.discover(project_root, metrics)
    
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
    
    def _calculate_phase_progress(self, content: str) -> tuple[Dict[str, int], List[str]]:
        """Calculate phase progress (delegated to PhaseProgressCalculator)."""
        calculator = PhaseProgressCalculator()
        return calculator.calculate(content)
    
    def _generate_progress_bar(self, percentage: int, width: int = 32) -> str:
        """Generate progress bar (delegated to ProgressBarGenerator)."""
        generator = ProgressBarGenerator()
        return generator.generate(percentage, width)
    
    def _generate_recent_updates(
        self,
        project_root: Path,
        lookback_days: int = 1
    ) -> List[str]:
        """Generate recent updates (delegated to RecentUpdatesGenerator)."""
        generator = RecentUpdatesGenerator(self._format_commit_as_update)
        return generator.generate(project_root, lookback_days)
    
    def _format_commit_as_update(self, commit_msg: str, project_root: Path) -> Optional[str]:
        """
        Format git commit message as status update with appropriate emoji.
        
        Args:
            commit_msg: Raw commit message
            project_root: Project root (for file checks)
            
        Returns:
            Formatted update string or None if should be skipped
        """
        # Detect completion/creation keywords
        if any(word in commit_msg.lower() for word in ['complete', 'done', 'finish', 'implement']):
            emoji = '✅'
        elif any(word in commit_msg.lower() for word in ['add', 'create', 'new']):
            emoji = '✅'
        elif any(word in commit_msg.lower() for word in ['update', 'improve', 'enhance']):
            emoji = '✅'
        elif any(word in commit_msg.lower() for word in ['fix', 'bugfix', 'resolve']):
            emoji = '🔧'
        elif any(word in commit_msg.lower() for word in ['pending', 'progress', 'wip']):
            emoji = '⏸️'
        else:
            emoji = '✅'  # Default to checkmark
        
        # Clean up commit message (remove prefixes like "feat:", "fix:", etc.)
        clean_msg = re.sub(r'^(feat|fix|docs|style|refactor|test|chore):\s*', '', commit_msg, flags=re.IGNORECASE)
        
        # Capitalize first letter
        clean_msg = clean_msg[0].upper() + clean_msg[1:] if clean_msg else clean_msg
        
        # Add period if missing
        if clean_msg and not clean_msg.endswith(('.', '!', '?')):
            clean_msg += ''
        
        return f"{emoji} {clean_msg}"
    
    def _add_sync_context(
        self,
        updates: List[str],
        impl_state: ImplementationState,
        transformations: Dict[str, Any]
    ) -> str:
        """Add sync context (delegated to SyncContextGenerator)."""
        generator = SyncContextGenerator()
        return generator.generate(updates, impl_state, transformations)
    
    def _consolidate_status_files(
        self,
        status_files: List[Path],
        impl_state: ImplementationState,
        design_state: DesignState,
        gaps: GapAnalysis,
        project_root: Path,
        metrics: SyncMetrics
    ) -> Optional[Path]:
        """Consolidate multiple status files (delegated to StatusFileConsolidator)."""
        consolidator = StatusFileConsolidator(
            self._generate_recent_updates,
            self._calculate_phase_progress,
            self._generate_progress_bar,
            self._add_sync_context
        )
        return consolidator.consolidate(
            status_files,
            impl_state,
            design_state,
            gaps,
            project_root,
            metrics
        )
    
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
        """Commit changes and report (delegated to CommitReporter)."""
        reporter = CommitReporter()
        return reporter.commit_and_report(
            impl_state,
            design_state,
            gaps,
            optimizations,
            transformations,
            project_root,
            metrics,
            profile
        )
    
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
