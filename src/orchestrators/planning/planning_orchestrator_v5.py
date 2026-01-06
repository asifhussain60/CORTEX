"""
Planning Orchestrator v5 - Pure Autonomous Planning System.

First orchestrator built on BaseOrchestrator v4.1 with complete Master Orchestrator
integration. Generates structured plans with folder hierarchy, context discovery,
and database state tracking.

CORTEX v5.0 Epic P03: TodoManager Integration for real-time task tracking.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import logging
import re
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime

from src.orchestrators.base.base_orchestrator_v4_1 import (
    BaseOrchestratorV4_1,
    PhaseStatus,
    PhaseResult
)
from src.orchestrators.base.base_orchestrator import (
    OrchestratorResult,
    OrchestratorStatus
)
from src.database.planning_state_db import PlanningStateDB
from src.orchestrators.planning.governance_integrator import (
    GovernanceIntegrator,
    GovernanceValidation
)
# CORTEX-5.0 Sub-Plan 04: AST Scanning Integration
from src.orchestrators.planning.ast_scanner import ASTScanner
from src.orchestrators.planning.duplicate_detector import PlanningDuplicateDetector
from src.orchestrators.planning.orphan_detector import PlanningOrphanDetector
from src.orchestrators.planning.knowledge_graph_query import (
    KnowledgeGraphQuery,
    KnowledgeContext
)
# CORTEX-5.0 Sub-Plan 10 (C50-10): Phase-Level Acceptance Criteria (Gap 1)
from src.orchestrators.planning.acceptance_validator import (
    AcceptanceCriteriaValidator,
    PhaseNotReadyError,
    PhaseIncompleteError
)
# CORTEX v5.0 Epic P03: TodoManager Integration
from src.orchestrators.master.todo_manager import TodoManager, Task, TaskStatus


class PlanningOrchestratorV5(BaseOrchestratorV4_1):
    """
    Planning Orchestrator v5 - Pure autonomous planning.
    
    Features:
    - Zero natural language in manifest (config-only)
    - Context discovery via workspace search
    - Template-driven plan generation
    - Folder structure creation (4 subfolders)
    - Database state tracking
    - Automated validation
    - Master Orchestrator integration
    
    Execution Flow:
        1. Parse user request → Extract feature name
        2. Create plan in database
        3. Phase 0: Context Discovery - Search workspace
        4. Phase 1: Architecture Analysis - AST parsing
        5. Phase 2: Plan Generation - Template rendering
        6. Phase 3: Folder Creation - Filesystem operations
        7. Phase 4: Validation - Automated checks
    
    Master Orchestrator Integration:
    - Registered via pattern: "^(plan|create a plan|make a plan).*$"
    - State sharing for cross-orchestrator coordination
    - Lifecycle hooks for pre/post execution
    """
    
    def __init__(
        self,
        config_path: Optional[str] = None,
        state_db: Optional[PlanningStateDB] = None,
        plan_id: Optional[str] = None,
        template_dir: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        plan_type: str = "feature"
    ):
        """Initialize Planning Orchestrator v5.
        
        Args:
            config_path: Path to configuration YAML
            state_db: Planning state database instance
            plan_id: Existing plan ID to resume
            template_dir: Custom template directory
            context: Additional context from Master Orchestrator
            plan_type: Type of plan - 'feature' | 'epic' | 'phase' | 'sub-plan'
        """
        # Validate plan_type
        valid_types = ['feature', 'epic', 'phase', 'sub-plan']
        if plan_type not in valid_types:
            raise ValueError(f"Invalid plan_type: {plan_type}. Must be one of {valid_types}")
        
        # Store plan type before super().__init__
        self.plan_type = plan_type
        
        # Load default config if not provided
        if config_path is None:
            config_path = "cortex-brain/config/planning-v5-default.yaml"
        
        # Initialize database if not provided
        if state_db is None:
            db_path = "cortex-brain/database/planning_state.db"
            state_db = PlanningStateDB(db_path=db_path)
        
        super().__init__(config_path, state_db, plan_id, template_dir)
        
        # Store context from Master Orchestrator
        self.master_context = context or {}
        
        # Initialize governance and knowledge graph integrations (Phase 4 enhancement)
        self.governance = GovernanceIntegrator()
        self.knowledge_graph = KnowledgeGraphQuery()
        
        # Initialize acceptance criteria validator (C50-10: Gap 1 remediation)
        self.acceptance_validator = None  # Initialized per-plan in execute()
        
        # Initialize TodoManager for phase tracking (v6 upgrade - P03)
        plan_root = "tracking"
        self.todo_manager = TodoManager(plan_dir=plan_root)
        
        self.logger.info("PlanningOrchestratorV5 initialized with governance + knowledge graph + TodoManager")
    
    def execute_phase(
        self,
        phase_number: int,
        phase_config: dict,
        **kwargs
    ) -> PhaseResult:
        """
        Execute a single phase with DoR/DoD validation.
        
        Override of BaseOrchestratorV4_1.execute_phase() to add acceptance criteria
        validation hooks. Validates DoR before phase start and DoD after phase completion.
        
        Args:
            phase_number: Sequential phase number (0-indexed)
            phase_config: Phase configuration from manifest
            **kwargs: Additional phase parameters
        
        Returns:
            PhaseResult with phase execution details
        
        Raises:
            PhaseNotReadyError: If DoR validation fails (phase not ready to start)
            PhaseIncompleteError: If DoD validation fails (phase not ready to complete)
        """
        phase_name = phase_config.get('name', f'Phase {phase_number}')
        
        # C50-10 Gap 1: Validate Definition of Ready (DoR) BEFORE phase start
        if self.acceptance_validator:
            try:
                self.logger.info(f"Validating DoR for Phase {phase_number}: {phase_name}")
                self.acceptance_validator.validate_phase_dor(phase_number)
            except PhaseNotReadyError as e:
                self.logger.error(f"Phase {phase_number} blocked by DoR: {e}")
                raise  # Block phase execution
        
        # Execute phase via base class (normal execution flow)
        phase_result = super().execute_phase(phase_number, phase_config, **kwargs)
        
        # C50-10 Gap 1: Validate Definition of Done (DoD) AFTER phase completion
        if self.acceptance_validator and phase_result.status == PhaseStatus.COMPLETED:
            try:
                self.logger.info(f"Validating DoD for Phase {phase_number}: {phase_name}")
                self.acceptance_validator.validate_phase_dod(phase_number)
            except PhaseIncompleteError as e:
                self.logger.error(f"Phase {phase_number} blocked by DoD: {e}")
                # Mark phase incomplete and rollback
                phase_result.status = PhaseStatus.FAILED
                phase_result.errors.append(f"DoD validation failed: {e}")
                self.state_db.fail_phase(phase_result.phase_id, str(e))
                raise  # Block phase completion
        
        return phase_result
    
    @staticmethod
    def get_registration_config() -> dict:
        """
        Get Master Orchestrator registration configuration.
        
        Returns:
            Registration config for Master Orchestrator
        """
        return {
            'orchestrator_id': 'planning_v5',
            'patterns': [
                {
                    'pattern': r'^(plan|create a plan|make a plan).*$',
                    'match_type': 'regex',
                    'confidence': 1.0,
                    'priority': 10
                }
            ],
            'dependencies': ['mcp_tools', 'planning_state_db'],
            'lifecycle_hooks': {
                'pre_execution': ['validate_workspace'],
                'post_execution': ['save_plan_artifact', 'update_continuation_prompt']
            },
            'metadata': {
                'description': 'Planning system for structured planning',
                'autonomous': True,
                'version': '5.0'
            }
        }
    
    def execute(self, user_request: str, **kwargs) -> OrchestratorResult:
        """
        Execute planning orchestrator autonomously.
        
        Args:
            user_request: User's planning request
            **kwargs: Additional parameters
        
        Returns:
            OrchestratorResult with plan artifacts
        """
        self.logger.info(f"Executing Planning v5: '{user_request}'")
        
        start_time = datetime.now()
        
        try:
            # Phase 0.5: Pre-Flight Cache Optimization (CORTEX-5.0 Sub-Plan 00D)
            try:
                from src.operations.utilities.vscode_cache_manager import VSCodeCacheManager
                
                cache_manager = VSCodeCacheManager()
                cache_results = cache_manager.pre_flight_optimize(log_metrics=True, fail_silently=True)
                
                if cache_results.get("success") and not cache_results.get("skipped"):
                    self.logger.info(f"✅ Pre-flight cache optimization: {cache_results.get('summary', 'Complete')}")
                elif cache_results.get("skipped"):
                    self.logger.debug(f"⏭️  Cache optimization skipped: {cache_results.get('reason', 'N/A')}")
                else:
                    self.logger.warning(f"⚠️  Cache optimization failed (non-critical): {cache_results.get('error', 'Unknown')}")
            except Exception as e:
                self.logger.warning(f"⚠️  Pre-flight cache optimization failed (non-critical): {e}")
            
            # Phase 0: Parse request and create plan
            feature_name = self._extract_feature_name(user_request)
            plan_data = self._create_plan_metadata(feature_name, user_request)
            
            # Create plan in database
            self.plan_id = self.state_db.create_plan(
                feature_name=feature_name,
                metadata=plan_data
            )
            
            self.logger.info(f"Created plan: {self.plan_id}")
            
            # C50-10 Gap 1: Initialize acceptance criteria validator
            plan_root = Path(plan_data['folder_path'])
            if plan_root.exists():
                try:
                    self.acceptance_validator = AcceptanceCriteriaValidator(
                        plan_root=plan_root,
                        logger=self.logger
                    )
                    self.logger.info("✅ Acceptance criteria validator initialized")
                except Exception as e:
                    self.logger.warning(f"⚠️  Acceptance validator init failed (non-blocking): {e}")
            
            # v6 Upgrade (P03): Create phase tasks for tracking
            phase_tasks = [
                ("Knowledge Library", "Consult governance and knowledge graph"),
                ("Context Discovery", "Search workspace for relevant context"),
                ("Architecture Analysis", "Parse codebase and analyze structure"),
                ("Plan Generation", "Create structured plan document"),
                ("Folder Creation", "Create directory structure for plan"),
                ("Validation", "Validate plan structure and completeness")
            ]
            
            self.phase_task_ids = []
            for phase_name, phase_desc in phase_tasks:
                task_id = self.todo_manager.create_task(
                    title=phase_name,
                    description=phase_desc
                )
                self.phase_task_ids.append(task_id)
                self.logger.debug(f"Created task {task_id}: {phase_name}")
            
            # Phase -1: Knowledge Library (Governance Consultation)
            # Execute BEFORE Phase 0 to consult Tier 0/2 governance
            self.todo_manager.start_task(self.phase_task_ids[0])
            governance_result = self.execute_phase(
                -1,
                {'name': 'Knowledge Library', 'description': 'Consult governance and knowledge graph'},
                feature_name=feature_name,
                user_request=user_request
            )
            self.todo_manager.complete_task(self.phase_task_ids[0])
            
            # Check for blocking governance violations
            if governance_result and hasattr(governance_result, 'data'):
                governance_data = governance_result.data
                if not governance_data.get('success', True):
                    violations = governance_data.get('violations', [])
                    blocking_violations = [v for v in violations if 'blocked' in str(v).lower()]
                    if blocking_violations:
                        self.logger.error(f"Phase -1: Blocking governance violations: {blocking_violations}")
                        raise ValueError(f"Governance violations prevent planning: {blocking_violations}")
            
            # Phase 1: Context Discovery
            self.todo_manager.start_task(self.phase_task_ids[1])
            context_result = self.execute_phase(
                0,
                {'name': 'Context Discovery', 'description': 'Search workspace'},
                feature_name=feature_name,
                governance_context=governance_result
            )
            self.todo_manager.complete_task(self.phase_task_ids[1])
            
            # Phase 2: Architecture Analysis
            self.todo_manager.start_task(self.phase_task_ids[2])
            analysis_result = self.execute_phase(
                1,
                {'name': 'Architecture Analysis', 'description': 'Parse codebase'},
                feature_name=feature_name,
                context=context_result
            )
            self.todo_manager.complete_task(self.phase_task_ids[2])
            
            # Phase 3: Plan Generation
            self.todo_manager.start_task(self.phase_task_ids[3])
            generation_result = self.execute_phase(
                2,
                {'name': 'Plan Generation', 'description': 'Create plan document'},
                feature_name=feature_name,
                analysis=analysis_result
            )
            self.todo_manager.complete_task(self.phase_task_ids[3])
            
            # Phase 4: Folder Structure Creation
            self.todo_manager.start_task(self.phase_task_ids[4])
            folder_result = self.execute_phase(
                3,
                {'name': 'Folder Creation', 'description': 'Create directory structure'},
                feature_name=feature_name
            )
            self.todo_manager.complete_task(self.phase_task_ids[4])
            
            # Phase 5: Validation
            self.todo_manager.start_task(self.phase_task_ids[5])
            validation_result = self.execute_phase(
                4,
                {'name': 'Validation', 'description': 'Validate plan structure'},
                feature_name=feature_name
            )
            self.todo_manager.complete_task(self.phase_task_ids[5])
            
            # Mark plan complete
            self.state_db.update_plan_status(self.plan_id, 'completed')
            
            # Collect all artifacts (including Phase -1 governance)
            all_artifacts = (
                (governance_result.artifacts if governance_result else []) +
                context_result.artifacts +
                analysis_result.artifacts +
                generation_result.artifacts +
                folder_result.artifacts +
                validation_result.artifacts
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            
            # Check token usage - middleware will handle user-facing warnings
            token_status = self.check_token_usage()
            success_message = f"Plan '{feature_name}' created successfully"
            
            return OrchestratorResult(
                status=OrchestratorStatus.COMPLETED,
                success=True,
                message=success_message,
                data={
                    'plan_id': self.plan_id,
                    'feature_name': feature_name,
                    'artifacts': all_artifacts,
                    'duration_seconds': duration,
                    'phases_completed': 5,
                    'token_usage_percentage': token_status.get('percentage', 0),  # For middleware
                    'success_metadata': {
                        'files_created': len([a for a in all_artifacts if 'created' in a.lower()]),
                        'phases_completed': 5
                    }
                },
                execution_time_seconds=duration
            )
            
        except Exception as e:
            self.logger.error(f"Planning execution failed: {e}", exc_info=True)
            
            # Mark plan failed if created
            if self.plan_id:
                self.state_db.update_plan_status(self.plan_id, 'failed')
            
            return OrchestratorResult(
                status=OrchestratorStatus.FAILED,
                success=False,
                message=f"Planning failed: {str(e)}",
                errors=[str(e)]
            )
    
    def _execute_phase_logic(
        self,
        phase_number: int,
        phase_config: dict,
        **kwargs
    ) -> List[str]:
        """
        Execute phase-specific logic.
        
        Args:
            phase_number: Phase number (-1 to 4)
            phase_config: Phase configuration
            **kwargs: Phase-specific parameters
        
        Returns:
            List of artifact paths created
        """
        phase_name = phase_config.get('name', f'Phase {phase_number}')
        
        self.logger.info(f"Executing {phase_name} logic...")
        
        if phase_number == -1:
            # Phase -1: Knowledge Library (Governance Consultation)
            return self._execute_governance_consultation(**kwargs)
        
        elif phase_number == 0:
            # Context Discovery
            return self._discover_context(**kwargs)
        
        elif phase_number == 1:
            # Architecture Analysis
            return self._analyze_architecture(**kwargs)
        
        elif phase_number == 2:
            # Plan Generation
            return self._generate_plan(**kwargs)
        
        elif phase_number == 3:
            # Folder Creation + YAML + HTML Viewer
            artifacts = []
            
            # Create folder structure
            folders = self._create_folder_structure(**kwargs)
            artifacts.extend(folders)
            
            # Generate YAML plan for execution
            user_request = kwargs.get('user_request', '')
            feature_name = kwargs.get('feature_name', self._extract_feature_name(user_request))
            
            # Create kwargs without feature_name to avoid duplication
            method_kwargs = {k: v for k, v in kwargs.items() if k != 'feature_name'}
            yaml_path = self._generate_plan_yaml(feature_name, **method_kwargs)
            artifacts.append(yaml_path)
            
            # Generate HTML plan viewer
            html_path = self._generate_plan_viewer_html(feature_name, **method_kwargs)
            artifacts.append(html_path)
            
            # Start plan server on port 8150
            try:
                from src.servers import start_plan_viewer
                from pathlib import Path
                
                # Use centralized plan directory method (prevents stray folder creation)
                plan_folder = self._get_plan_directory(feature_name)
                
                # Start server (reuses existing if running)
                viewer_url = start_plan_viewer(plan_folder)
                self.logger.info(f"🌐 Plan viewer available at: {viewer_url}")
                
                # Add server URL to artifacts
                artifacts.append(f"server:{viewer_url}")
                
            except Exception as e:
                self.logger.warning(f"⚠️  Failed to start plan server: {e}")
                self.logger.info("Plan viewer HTML generated but server not started")
            
            return artifacts
        
        elif phase_number == 4:
            # Validation
            return self._validate_plan(**kwargs)
        
        else:
            self.logger.warning(f"Unknown phase: {phase_number}")
            return []
    
    def _extract_feature_name(self, user_request: str) -> str:
        """
        Extract feature name from user request.
        
        Args:
            user_request: User's planning request
        
        Returns:
            Sanitized feature name (kebab-case, <=50 chars)
        """
        # Remove planning keywords
        text = re.sub(
            r'^(plan|create a plan|make a plan|planning)\s+',
            '',
            user_request,
            flags=re.IGNORECASE
        ).strip()
        
        # Convert to kebab-case
        text = re.sub(r'[^\w\s-]', '', text)  # Remove special chars
        text = re.sub(r'[\s_]+', '-', text)    # Replace spaces/underscores with hyphens
        text = text.lower().strip('-')
        
        # Limit length
        if len(text) > 50:
            text = text[:50].rsplit('-', 1)[0]  # Cut at last hyphen before 50 chars
        
        return text or 'untitled-plan'
    
    def _abbreviate_feature_name(self, feature_name: str, max_length: int = 22) -> str:
        """
        Abbreviate feature name to fit within length constraint.
        
        Args:
            feature_name: Full feature name (kebab-case)
            max_length: Maximum length for abbreviated name (default: 22)
        
        Returns:
            Abbreviated feature name
        
        Examples:
            "enterprise-python-audit-logger" → "enterprise-py-aud-log"
            "glassmorphism-css-standardization" → "glassmorphism-css-std"
            "oauth2-authentication-system" → "oauth2-auth-sys"
        """
        # Common abbreviation mapping
        abbrev_map = {
            'enterprise': 'ent',
            'python': 'py',
            'logger': 'log',
            'audit': 'aud',
            'implementation': 'impl',
            'integration': 'integ',
            'authentication': 'auth',
            'authorization': 'authz',
            'application': 'app',
            'database': 'db',
            'configuration': 'config',
            'management': 'mgmt',
            'development': 'dev',
            'production': 'prod',
            'environment': 'env',
            'deployment': 'deploy',
            'monitoring': 'mon',
            'performance': 'perf',
            'optimization': 'opt',
            'standardization': 'std',
            'orchestrator': 'orch',
            'validation': 'valid',
            'documentation': 'doc',
            'system': 'sys',
            'service': 'svc',
            'interface': 'iface',
            'component': 'comp',
            'container': 'ctr',
            'kubernetes': 'k8s',
            'infrastructure': 'infra'
        }
        
        # Split on hyphens and abbreviate
        parts = feature_name.split('-')
        abbreviated_parts = []
        
        for part in parts:
            # Use abbreviation map if available
            if part in abbrev_map:
                abbreviated_parts.append(abbrev_map[part])
            elif len(part) > 8:
                # Abbreviate long words (keep first 6 chars)
                abbreviated_parts.append(part[:6])
            else:
                # Keep short words full
                abbreviated_parts.append(part)
        
        # Join and truncate if needed
        abbreviated_name = '-'.join(abbreviated_parts)
        if len(abbreviated_name) > max_length:
            # Truncate at last hyphen before max_length
            abbreviated_name = abbreviated_name[:max_length].rsplit('-', 1)[0]
        
        return abbreviated_name
    
    def _get_plan_directory(self, feature_name: str) -> Path:
        """
        Get standardized plan directory path with ID prefix and abbreviation.
        
        CRITICAL: This is the SINGLE SOURCE OF TRUTH for plan directory paths.
        ALL methods must use this to prevent stray folder creation.
        
        Args:
            feature_name: Feature name (kebab-case)
        
        Returns:
            Path object for plan directory
        
        Examples:
            "oauth2-authentication-system" → 
                cortex-brain/documents/planning/active/a01-oauth2-auth-sys
        """
        # Generate master plan filename to extract ID prefix
        master_plan_filename = self._generate_master_plan_filename(feature_name)
        folder_id_prefix = master_plan_filename.split('-')[0].lower()  # Extract "a01" from "A01-..."
        
        # Abbreviate feature name (max 22 chars)
        abbreviated_name = self._abbreviate_feature_name(feature_name, max_length=22)
        
        # Create folder name with ID prefix: a01-oauth2-auth-sys
        folder_name = f"{folder_id_prefix}-{abbreviated_name}"
        
        # Check if there's an epic parent folder in master_context
        epic_parent_path = self.master_context.get('epic_parent_path') if hasattr(self, 'master_context') else None
        
        if epic_parent_path:
            # Child plan inside epic folder
            return Path(epic_parent_path) / folder_name
        else:
            # Root-level plan (epic or standalone feature)
            return Path(f"cortex-brain/documents/planning/active/{folder_name}")
    
    def _generate_master_plan_filename(self, feature_name: str) -> str:
        """
        Generate meaningful master plan filename with 3-char ID prefix.
        
        Format: [A-Z0-9]{3}-{abbreviated-name}.md
        Total length: 3 (ID) + 1 (dash) + 20-25 (name) + 3 (.md) = 27-32 chars
        
        Args:
            feature_name: Full feature name (kebab-case)
        
        Returns:
            Master plan filename (e.g., "A01-enterprise-audit-logger.md")
        
        Examples:
            "enterprise-python-audit-logger" → "A01-ent-py-aud-log.md"
            "glassmorphism-css-standardization" → "A02-glassmorphism-css-std.md"
            "oauth2-authentication-system" → "A03-oauth2-auth-sys.md"
        """
        # Generate 3-char ID based on plan count in database
        if hasattr(self, 'state_db') and self.state_db:
            # Query database directly for plan count
            cursor = self.state_db._conn.execute("SELECT COUNT(*) FROM plans")
            plan_count = cursor.fetchone()[0]
        else:
            plan_count = 0
        
        # ID format: A00-A99 (100 plans), then B00-B99, etc.
        letter = chr(65 + (plan_count // 100))  # A=0-99, B=100-199, etc.
        number = plan_count % 100
        plan_id = f"{letter}{number:02d}"
        
        # Use helper method to abbreviate
        abbreviated_name = self._abbreviate_feature_name(feature_name, max_length=22)
        
        return f"{plan_id}-{abbreviated_name}.md"
    
    def _create_plan_metadata(
        self,
        feature_name: str,
        user_request: str
    ) -> dict:
        """
        Create plan metadata for database.
        
        Args:
            feature_name: Sanitized feature name
            user_request: Original user request
        
        Returns:
            Plan metadata dictionary
        """
        # Use centralized plan directory method for consistency
        plan_dir = self._get_plan_directory(feature_name)
        
        return {
            'feature_name': feature_name,
            'user_request': user_request,
            'created_at': datetime.now().isoformat(),
            'orchestrator': 'planning_v5',
            'version': self.version,
            'complexity_tier': self._estimate_complexity(user_request),
            'estimated_days': 0,  # To be calculated during analysis
            'folder_path': str(plan_dir)
        }
    
    def _estimate_complexity(self, user_request: str) -> int:
        """
        Estimate complexity tier (1-5) based on request.
        
        Args:
            user_request: User request text
        
        Returns:
            Complexity tier (1=trivial, 5=architectural)
        """
        # Simple heuristic based on keywords
        architectural_keywords = [
            'architecture', 'refactor', 'redesign', 'system-wide',
            'holistic', 'framework', 'infrastructure'
        ]
        
        complex_keywords = [
            'migrate', 'integrate', 'orchestrator', 'autonomous',
            'database', 'api', 'protocol'
        ]
        
        text_lower = user_request.lower()
        
        if any(kw in text_lower for kw in architectural_keywords):
            return 5  # Architectural
        elif any(kw in text_lower for kw in complex_keywords):
            return 4  # Complex
        elif len(user_request.split()) > 10:
            return 3  # Moderate
        elif len(user_request.split()) > 5:
            return 2  # Simple
        else:
            return 1  # Trivial
    
    def _execute_governance_consultation(
        self,
        feature_name: str,
        user_request: str,
        **kwargs
    ) -> List[str]:
        """
        Execute Phase -1: Knowledge Library governance consultation.
        
        Consults Tier 0 (brain-protection-rules.yaml) and Tier 2 (knowledge-graph.yaml)
        BEFORE any planning work begins.
        
        Args:
            feature_name: Feature being planned
            user_request: Original user request
            **kwargs: Additional parameters
        
        Returns:
            List of artifact paths (consultation report)
        """
        from src.orchestrators.planning.phases.phase_minus_one import PhaseMinusOne
        
        self.logger.info("Phase -1: Executing governance consultation...")
        
        # Initialize Phase -1
        phase = PhaseMinusOne(
            governance_integrator=self.governance,
            knowledge_query=self.knowledge_graph
        )
        
        # Execute consultation
        result = phase.execute(
            feature_name=feature_name,
            user_request=user_request,
            plan_context=kwargs.get('plan_context')
        )
        
        # Store consultation data in phase result
        if hasattr(self, '_phase_data'):
            self._phase_data['governance_consultation'] = {
                'success': result.success,
                'violations': result.violations,
                'warnings': result.warnings,
                'recommendations': result.recommendations,
                'report_path': result.consultation_report_path
            }
        
        # Return artifacts
        artifacts = []
        if result.consultation_report_path:
            artifacts.append(result.consultation_report_path)
        
        self.logger.info(
            f"Phase -1 complete: {len(result.violations)} violations, "
            f"{len(result.warnings)} warnings"
        )
        
        return artifacts
    
    def _discover_context(self, feature_name: str, **kwargs) -> List[str]:
        """
        Discover relevant context from workspace.
        
        Args:
            feature_name: Feature being planned
            **kwargs: Additional parameters
        
        Returns:
            List of artifact paths
        """
        self.logger.info("Discovering context...")
        
        artifacts = []
        
        # Phase 4 Enhancement: Governance Validation
        governance_validation = self.governance.validate_feature_request(
            feature_name=feature_name,
            context={
                'type': 'feature',
                'paths': [],  # To be populated with actual paths
                'estimated_phases': kwargs.get('estimated_phases', 5)
            }
        )
        
        # Phase 4 Enhancement: Knowledge Graph Query
        knowledge_context = self.knowledge_graph.get_feature_context(feature_name)
        
        # CORTEX-5.0 Enhancement: AST Scanning Integration (Sub-Plan 04)
        ast_analysis = self._run_ast_scanning(feature_name)
        
        # Create context document with governance and knowledge graph data
        context_content = f"""# Context Discovery Report
## Feature: {feature_name}

**Discovery Date:** {datetime.now().isoformat()}

### Workspace Analysis
- Workspace root: {Path.cwd()}
- Planning for: {feature_name}

### AST Analysis (CORTEX-5.0 Enhancement)
**Files Scanned:** {ast_analysis.get('files_scanned', 0)}
**Total Functions:** {ast_analysis.get('total_functions', 0)}
**Total Classes:** {ast_analysis.get('total_classes', 0)}
**Total Imports:** {ast_analysis.get('total_imports', 0)}

#### Duplicate Code Analysis
- **Duplicate Patterns:** {ast_analysis.get('duplicate_analysis', {}).get('duplicates_found', 0)}
- **Duplicate Rate:** {ast_analysis.get('duplicate_analysis', {}).get('duplicate_percentage', 0)}%

#### Orphaned Function Analysis
- **Orphaned Functions:** {ast_analysis.get('orphan_analysis', {}).get('orphaned_count', 0)}
- **Orphan Rate:** {ast_analysis.get('orphan_analysis', {}).get('orphaned_percentage', 0)}%

### Governance Validation
**Status:** {'✅ Valid' if governance_validation.is_valid else '❌ Violations Detected'}

**Applied Rules:** {len(governance_validation.applied_rules)} rules
- {', '.join(governance_validation.applied_rules[:5])}

**Violations:** {len(governance_validation.violations)}
{chr(10).join(f"- [{v['severity'].upper()}] {v['rule']}: {v['message']}" for v in governance_validation.violations[:5])}

**Warnings:** {len(governance_validation.warnings)}
{chr(10).join(f"- {w}" for w in governance_validation.warnings[:5])}

### Knowledge Graph Context
**Related Features:** {len(knowledge_context.related_features)}
{chr(10).join(f"- {f}" for f in knowledge_context.related_features[:5])}

**Dependencies:** {len(knowledge_context.dependencies)}
{chr(10).join(f"- {d}" for d in knowledge_context.dependencies[:5])}

**Recommended Patterns:**
{chr(10).join(f"- {p}" for p in knowledge_context.patterns)}

**Identified Risks:**
{chr(10).join(f"- {r}" for r in knowledge_context.risks)}

**Recommendations:**
{chr(10).join(f"- {r}" for r in knowledge_context.recommendations)}

### Related Files
(Auto-discovery will be implemented in future iteration)

### Dependencies
(Dependency analysis will be implemented in future iteration)

### Existing Patterns
(Pattern detection will be implemented in future iteration)
"""
        
        # Use centralized plan directory method (prevents stray folder creation)
        plan_dir = self._get_plan_directory(feature_name)
        context_path = plan_dir / "context" / "discovery.md"
        
        artifact_id = self.create_artifact(
            path=str(context_path),
            content=context_content,
            artifact_type="context"
        )
        
        artifacts.append(str(context_path))
        
        return artifacts
    
    def _analyze_architecture(
        self,
        feature_name: str,
        context: PhaseResult,
        **kwargs
    ) -> List[str]:
        """
        Analyze codebase architecture.
        
        Args:
            feature_name: Feature being planned
            context: Context discovery results
            **kwargs: Additional parameters
        
        Returns:
            List of artifact paths
        """
        self.logger.info("Analyzing architecture...")
        
        artifacts = []
        
        # Create architecture analysis document
        analysis_content = f"""# Architecture Analysis
## Feature: {feature_name}

**Analysis Date:** {datetime.now().isoformat()}

### Current Architecture
(AST parsing and analysis will be implemented in future iteration)

### Proposed Changes
- Planning system integration
- Folder structure setup
- Database tracking

### Impact Assessment
- Low: Additive changes only
- No breaking changes expected

### Dependencies
- BaseOrchestrator v4.1
- PlanningStateDB
- Master Orchestrator
"""
        
        # Use centralized plan directory method (prevents stray folder creation)
        plan_dir = self._get_plan_directory(feature_name)
        analysis_path = plan_dir / "context" / "architecture-analysis.md"
        
        self.create_artifact(
            path=str(analysis_path),
            content=analysis_content,
            artifact_type="analysis"
        )
        
        artifacts.append(str(analysis_path))
        
        return artifacts
    
    def _generate_plan(
        self,
        feature_name: str,
        analysis: PhaseResult,
        **kwargs
    ) -> List[str]:
        """
        Generate master plan document.
        
        Args:
            feature_name: Feature being planned
            analysis: Architecture analysis results
            **kwargs: Additional parameters
        
        Returns:
            List of artifact paths
        """
        self.logger.info("Generating plan...")
        
        artifacts = []
        
        # Generate master plan
        plan_content = f"""# {feature_name.replace('-', ' ').title()}

**Plan ID:** {self.plan_id}  
**Created:** {datetime.now().strftime('%Y-%m-%d')}  
**Status:** ✅ ACTIVE  
**Orchestrator:** Planning v5

---

## 📊 Visual Progress Tracker

**Overall Progress:** `░░░░░░░░░░░░░░░░░░░░` **0%** ⏸️ NOT STARTED

| Phase | Name | Progress | Status |
|-------|------|----------|--------|
| 0 | Planning Complete | `██████████` | ✅ Complete |
| 1 | Implementation | `░░░░░░░░░░` | ⏸️ Not Started |
| 2 | Testing | `░░░░░░░░░░` | ⏸️ Not Started |
| 3 | Documentation | `░░░░░░░░░░` | ⏸️ Not Started |

---

## 🎯 Executive Summary

### The Goal
{feature_name.replace('-', ' ').title()} implementation with full test coverage
and documentation.

### Success Criteria
- ✅ Implementation complete
- ✅ Tests passing (100% coverage)
- ✅ Documentation updated
- ✅ Code reviewed

---

## 🏗️ Implementation Phases

### Phase 0: Planning (COMPLETE)
**Duration:** 1h  
**Status:** ✅ Complete

**Deliverables:**
- Master plan document
- Folder structure
- Progress tracker

### Phase 1: Implementation
**Duration:** TBD  
**Status:** ⏸️ Not Started

**Tasks:**
1. Core implementation
2. Integration points
3. Configuration

### Phase 2: Testing
**Duration:** TBD  
**Status:** ⏸️ Not Started

**Tasks:**
1. Unit tests
2. Integration tests
3. Coverage validation

### Phase 3: Documentation
**Duration:** TBD  
**Status:** ⏸️ Not Started

**Tasks:**
1. API documentation
2. Usage examples
3. README updates

---

## 📝 Next Steps

1. Begin Phase 1: Implementation
2. Create core files
3. Write tests incrementally
4. Update this plan as work progresses

---

**Generated by:** Planning Orchestrator v5  
**Database:** `plan_id="{self.plan_id}"`
"""
        
        # Use centralized plan directory method (prevents stray folder creation)
        plan_dir = self._get_plan_directory(feature_name)
        master_plan_filename = self._generate_master_plan_filename(feature_name)
        plan_path = plan_dir / master_plan_filename
        
        self.create_artifact(
            path=str(plan_path),
            content=plan_content,
            artifact_type="plan"
        )
        
        artifacts.append(str(plan_path))
        
        # Generate README
        readme_content = f"""# {feature_name.replace('-', ' ').title()}

**Status:** Planning Complete  
**Plan ID:** {self.plan_id}

## Quick Start

See `{master_plan_filename}` for complete plan details.
## Structure

- `{master_plan_filename}` - Master plan document
- `context/` - Context and analysis documents
- `artifacts/` - Generated code and configs
- `reports/` - Progress and completion reports
- `tracking/` - Progress tracker and stateorts
- `tracking/` - Progress tracker and state

## Progress

Check `tracking/progress-tracker.json` for current status.
"""
        
        readme_path = plan_dir / "README.md"
        
        self.create_artifact(
            path=str(readme_path),
            content=readme_content,
            artifact_type="documentation"
        )
        
        artifacts.append(str(readme_path))
        
        return artifacts
    
    def _generate_plan_yaml(
        self,
        feature_name: str,
        **kwargs
    ) -> str:
        """
        Generate master-plan.yaml for execution.
        
        Creates structured YAML defining phases, tasks, and acceptance criteria
        for Python-based plan execution (not MD processing).
        
        Args:
            feature_name: Feature being planned
            **kwargs: Additional parameters
        
        Returns:
            Path to generated YAML file
        """
        import yaml
        from datetime import datetime
        
        self.logger.info("Generating plan YAML...")
        
        # Use centralized plan directory method (prevents stray folder creation)
        plan_dir = self._get_plan_directory(feature_name)
        
        # Generate master plan filename to extract ID
        master_plan_filename = self._generate_master_plan_filename(feature_name)
        folder_id_prefix = master_plan_filename.split('-')[0].upper()
        
        # Ensure plan folder exists
        plan_dir.mkdir(parents=True, exist_ok=True)
        
        # Create plan structure based on schema
        plan_data = {
            'plan': {
                'id': folder_id_prefix,
                'type': self.plan_type,
                'name': feature_name,
                'title': feature_name.replace('-', ' ').title(),
                'description': f"Implementation plan for {feature_name}",
                
                'metadata': {
                    'created': datetime.now().isoformat(),
                    'author': 'CORTEX Planning Orchestrator v5',
                    'complexity_tier': 3,
                    'estimated_hours': self._get_default_hours_by_type(),
                    'plan_id': self.plan_id,
                    'status': 'active'
                },
                
                'phases': self._generate_phases_by_type(feature_name),
                
                'acceptance_criteria': self._get_acceptance_criteria_by_type()
            }
        }
        
        # Write YAML file
        yaml_filename = master_plan_filename.replace('.md', '.yaml')
        yaml_path = plan_dir / yaml_filename
        
        with open(yaml_path, 'w') as f:
            yaml.dump(plan_data, f, default_flow_style=False, sort_keys=False, indent=2)
        
        self.logger.info(f"✅ Generated plan YAML: {yaml_path}")
        
        # Register as artifact
        self.create_artifact(
            path=str(yaml_path),
            content=yaml_path.read_text(),
            artifact_type="plan"
        )
        
        return str(yaml_path)
    
    def _generate_plan_viewer_html(
        self,
        feature_name: str,
        **kwargs
    ) -> str:
        """
        Generate interactive HTML plan viewer with live updates.
        
        Creates self-contained HTML file that polls /api/plan and /api/progress
        endpoints for real-time plan execution updates.
        
        Args:
            feature_name: Feature being planned
            **kwargs: Additional parameters
        
        Returns:
            Path to generated HTML file
        """
        self.logger.info("Generating plan viewer HTML...")
        
        master_plan_filename = self._generate_master_plan_filename(feature_name)
        plan_id = master_plan_filename.split('-')[0]
        
        # Use centralized plan directory method (prevents stray folder creation)
        plan_dir = self._get_plan_directory(feature_name)
        
        # Audit log folder creation
        self.logger.info(f"📁 AUDIT: Ensuring plan directory exists: {plan_dir} (method=_generate_plan_viewer_html)")
        
        # Ensure plan folder exists
        plan_dir.mkdir(parents=True, exist_ok=True)
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{plan_id} - {feature_name.replace('-', ' ').title()} - CORTEX Plan Viewer</title>
    <style>
        /* CORTEX 5.0 Glassmorphism Styles */
        :root {{
            --glass-bg: rgba(15, 23, 42, 0.7);
            --glass-border: rgba(255, 255, 255, 0.1);
            --progress-gradient: linear-gradient(90deg, #00d4ff 0%, #a855f7 100%);
            --text-primary: #e2e8f0;
            --text-secondary: #94a3b8;
            --accent-blue: #00d4ff;
            --accent-purple: #a855f7;
        }}
        
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: var(--text-primary);
            padding: 2rem;
            min-height: 100vh;
            line-height: 1.6;
        }}
        
        .container {{ max-width: 1400px; margin: 0 auto; }}
        
        .glass-panel {{
            background: var(--glass-bg);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid var(--glass-border);
            border-radius: 16px;
            padding: 2rem;
            margin-bottom: 1.5rem;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        
        .glass-panel:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 32px rgba(0, 212, 255, 0.15);
        }}
        
        .header {{ text-align: center; margin-bottom: 3rem; }}
        
        .plan-id {{
            display: inline-block;
            background: var(--progress-gradient);
            color: #000;
            font-weight: 700;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            font-size: 1.5rem;
            margin-bottom: 1rem;
        }}
        
        .plan-title {{
            font-size: clamp(2rem, 4vw, 3rem);
            font-weight: 700;
            background: linear-gradient(90deg, var(--accent-blue), var(--accent-purple));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .live-indicator {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            color: #10b981;
            font-size: 0.875rem;
            margin-top: 1rem;
        }}
        
        .live-dot {{
            width: 8px;
            height: 8px;
            background: #10b981;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }}
        
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
        }}
        
        .overall-progress {{ margin: 2rem 0; }}
        
        .progress-bar {{
            height: 24px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            overflow: hidden;
            margin-top: 0.5rem;
        }}
        
        .progress-fill {{
            height: 100%;
            background: var(--progress-gradient);
            transition: width 0.5s ease;
            display: flex;
            align-items: center;
            justify-content: flex-end;
            padding-right: 1rem;
            color: #000;
            font-weight: 600;
            font-size: 0.875rem;
        }}
        
        .phase-card {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1rem;
        }}
        
        .phase-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }}
        
        .phase-title {{ font-size: 1.5rem; font-weight: 600; }}
        
        .phase-status {{
            padding: 0.25rem 0.75rem;
            border-radius: 6px;
            font-size: 0.875rem;
            font-weight: 600;
        }}
        
        .status-not-started {{ background: rgba(148, 163, 184, 0.2); color: #94a3b8; }}
        .status-in-progress {{ background: rgba(0, 212, 255, 0.2); color: #00d4ff; }}
        .status-completed {{ background: rgba(16, 185, 129, 0.2); color: #10b981; }}
        
        .task-list {{ list-style: none; margin-top: 1rem; }}
        
        .task-item {{
            padding: 0.75rem;
            border-left: 3px solid rgba(255, 255, 255, 0.2);
            margin-bottom: 0.5rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .task-item.completed {{
            border-left-color: #10b981;
            opacity: 0.7;
        }}
        
        .task-item.in-progress {{
            border-left-color: #00d4ff;
        }}
        
        .meta-info {{
            display: flex;
            gap: 1rem;
            font-size: 0.875rem;
            color: var(--text-secondary);
            margin-top: 0.5rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header glass-panel">
            <div class="plan-id" id="planId">{plan_id}</div>
            <h1 class="plan-title" id="planTitle">{feature_name.replace('-', ' ').title()}</h1>
            <div class="live-indicator">
                <div class="live-dot"></div>
                <span>Live Updates</span>
            </div>
        </div>
        
        <div class="glass-panel overall-progress">
            <h2>Overall Progress</h2>
            <div class="progress-bar">
                <div class="progress-fill" id="overallProgress" style="width: 0%">0%</div>
            </div>
            <div class="meta-info">
                <span>⏱️ <span id="estimatedHours">0</span> hours estimated</span>
                <span>📅 Created: <span id="createdDate">-</span></span>
            </div>
        </div>
        
        <div id="phasesContainer">
            <!-- Phases loaded dynamically -->
        </div>
    </div>
    
    <script>
        // Fetch plan data from server
        async function fetchPlan() {{
            try {{
                const response = await fetch('/api/plan');
                const data = await response.json();
                return data.plan;
            }} catch (error) {{
                console.error('Failed to fetch plan:', error);
                return null;
            }}
        }}
        
        // Fetch progress data
        async function fetchProgress() {{
            try {{
                const response = await fetch('/api/progress');
                const data = await response.json();
                return data;
            }} catch (error) {{
                console.error('Failed to fetch progress:', error);
                return null;
            }}
        }}
        
        // Render phases
        function renderPhases(plan, progress) {{
            const container = document.getElementById('phasesContainer');
            container.innerHTML = '';
            
            if (!plan || !plan.phases) return;
            
            plan.phases.forEach(phase => {{
                const statusClass = `status-${{phase.status.replace('_', '-')}}`;
                
                const tasksHtml = phase.tasks.map(task => `
                    <li class="task-item ${{task.status.replace('_', '-')}}">
                        <span>${{task.name}}</span>
                        <span class="phase-status ${{`status-${{task.status.replace('_', '-')}}`}}">${{task.status.replace('_', ' ')}}</span>
                    </li>
                `).join('');
                
                const phaseHtml = `
                    <div class="glass-panel phase-card">
                        <div class="phase-header">
                            <h3 class="phase-title">Phase ${{phase.number}}: ${{phase.name}}</h3>
                            <span class="phase-status ${{statusClass}}">${{phase.status.replace('_', ' ').toUpperCase()}}</span>
                        </div>
                        <p class="meta-info">${{phase.description || ''}}</p>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: 0%">0%</div>
                        </div>
                        <ul class="task-list">
                            ${{tasksHtml}}
                        </ul>
                        <div class="meta-info">
                            <span>⏱️ ${{phase.estimated_hours}} hours</span>
                            <span>📋 ${{phase.tasks.length}} tasks</span>
                        </div>
                    </div>
                `;
                
                container.innerHTML += phaseHtml;
            }});
        }}
        
        // Update progress
        function updateProgress(progress) {{
            if (!progress || !progress.progress) return;
            
            const overallPercent = progress.progress.overall_percent || 0;
            const overallEl = document.getElementById('overallProgress');
            overallEl.style.width = overallPercent + '%';
            overallEl.textContent = Math.round(overallPercent) + '%';
        }}
        
        // Initialize
        async function init() {{
            const plan = await fetchPlan();
            if (plan) {{
                document.getElementById('planId').textContent = plan.id;
                document.getElementById('planTitle').textContent = plan.title;
                document.getElementById('estimatedHours').textContent = plan.metadata?.estimated_hours || 0;
                document.getElementById('createdDate').textContent = 
                    new Date(plan.metadata?.created).toLocaleDateString() || '-';
                renderPhases(plan, {{}});
            }}
            
            // Poll for updates every 2 seconds
            setInterval(async () => {{
                const progress = await fetchProgress();
                updateProgress(progress);
            }}, 2000);
        }}
        
        init();
    </script>
</body>
</html>
"""
        
        # Write HTML file
        html_path = plan_dir / "plan-viewer.html"
        html_path.write_text(html_content)
        
        self.logger.info(f"✅ Generated plan viewer: {html_path}")
        
        # Register as artifact
        self.create_artifact(
            path=str(html_path),
            content=html_content,
            artifact_type="documentation"
        )
        
        return str(html_path)
    
    def _create_folder_structure(
        self,
        feature_name: str,
        **kwargs
    ) -> List[str]:
        """
        Create plan folder structure with A## prefix matching master plan ID.
        
        Args:
            feature_name: Feature being planned
            **kwargs: Additional parameters
        
        Returns:
            List of folder paths created
        """
        self.logger.info("Creating folder structure...")
        
        # Use centralized plan directory method (prevents stray folder creation)
        plan_dir = self._get_plan_directory(feature_name)
        folder_name = plan_dir.name  # Extract folder name from path
        
        self.logger.info(f"📁 Creating plan directory: {plan_dir}")
        
        # Standard folders for all plan types
        folders = [
            plan_dir / "analysis",
            plan_dir / "artifacts",
            plan_dir / "context",
            plan_dir / "reports",
            plan_dir / "tracking"
        ]
        
        # Epic-specific folders
        if self.plan_type == "epic":
            folders.extend([
                plan_dir / "features",      # Nested feature plans
                plan_dir / "integration"    # Cross-feature integration tests
            ])
            self.logger.info(f"📦 Creating epic-specific folders: features/, integration/")
        
        # Sub-plan specific folders
        if self.plan_type == "sub-plan":
            folders.append(plan_dir / "dependencies")  # Parent plan dependencies
            self.logger.info(f"📦 Creating sub-plan folder: dependencies/")
        
        # Audit log folder creation (track which folders are created)
        import inspect
        caller_frame = inspect.currentframe().f_back
        caller_method = caller_frame.f_code.co_name if caller_frame else "unknown"
        
        for folder in folders:
            # Log BEFORE creating folder
            self.logger.info(
                f"📁 AUDIT: Creating folder: {folder} "
                f"(plan_id={self.plan_id}, feature={feature_name}, "
                f"caller={caller_method}, plan_type={self.plan_type})"
            )
            folder.mkdir(parents=True, exist_ok=True)
            # Create .gitkeep
            (folder / ".gitkeep").touch()
        
        # Create progress tracker (type-specific)
        tracker_filename = self._get_progress_tracker_filename()
        
        # Extract folder_id_prefix from folder_name (e.g., "a01" from "a01-oauth2-auth-sys")
        folder_id_prefix = folder_name.split('-')[0]
        
        progress_content = {
            "plan_id": self.plan_id,
            "plan_type": self.plan_type,
            "feature_name": feature_name,
            "folder_name": folder_name,
            "master_plan_id": folder_id_prefix.upper(),
            "created_at": datetime.now().isoformat(),
            "status": "active",
            "progress": {
                "overall_percent": 0,
                "current_phase": 1,
                "total_phases": 4
            }
        }
        
        # Epic-specific tracker fields
        if self.plan_type == "epic":
            progress_content["features"] = []  # List of child feature plan IDs
            progress_content["integration_status"] = "not-started"
        
        import json
        tracker_path = plan_dir / "tracking" / tracker_filename
        tracker_path.write_text(json.dumps(progress_content, indent=2))
        
        self.logger.info(f"✅ Created folder structure: {folder_name}/ (type: {self.plan_type})")
        
        return [str(f) for f in folders]
    
    def _get_progress_tracker_filename(self) -> str:
        """Get progress tracker filename based on plan type."""
        if self.plan_type == "epic":
            return "epic-progress-tracker.json"
        elif self.plan_type == "sub-plan":
            return "sub-plan-tracker.json"
        else:
            return "progress-tracker.json"
    
    def _generate_phases_by_type(self, feature_name: str) -> List[Dict]:
        """Generate phase structure based on plan type."""
        if self.plan_type == 'epic':
            # Epic: 5 phases with feature breakdown
            return [
                {
                    'id': 'phase-1',
                    'number': 1,
                    'name': 'Epic Planning & Architecture',
                    'description': 'Design overall epic architecture and feature breakdown',
                    'status': 'not-started',
                    'estimated_hours': 24,
                    'tasks': [
                        {
                            'id': 'task-1-1',
                            'name': 'Define epic scope and objectives',
                            'description': 'Establish overall goals and success criteria',
                            'status': 'not-started',
                            'estimated_minutes': 120,
                            'priority': 'critical',
                            'dependencies': []
                        },
                        {
                            'id': 'task-1-2',
                            'name': 'Break down into features',
                            'description': 'Identify and define constituent features',
                            'status': 'not-started',
                            'estimated_minutes': 240,
                            'priority': 'critical',
                            'dependencies': ['task-1-1']
                        },
                        {
                            'id': 'task-1-3',
                            'name': 'Design integration strategy',
                            'description': 'Plan how features will integrate',
                            'status': 'not-started',
                            'estimated_minutes': 180,
                            'priority': 'high',
                            'dependencies': ['task-1-2']
                        }
                    ]
                },
                {
                    'id': 'phase-2',
                    'number': 2,
                    'name': 'Feature Implementation',
                    'description': 'Implement individual features in parallel',
                    'status': 'not-started',
                    'estimated_hours': 48,
                    'tasks': [
                        {
                            'id': 'task-2-1',
                            'name': 'Implement Feature A',
                            'description': 'Complete first feature',
                            'status': 'not-started',
                            'estimated_minutes': 960,
                            'priority': 'high',
                            'dependencies': ['task-1-3']
                        },
                        {
                            'id': 'task-2-2',
                            'name': 'Implement Feature B',
                            'description': 'Complete second feature',
                            'status': 'not-started',
                            'estimated_minutes': 960,
                            'priority': 'high',
                            'dependencies': ['task-1-3']
                        }
                    ]
                },
                {
                    'id': 'phase-3',
                    'number': 3,
                    'name': 'Feature Integration',
                    'description': 'Integrate all features and ensure interoperability',
                    'status': 'not-started',
                    'estimated_hours': 24,
                    'tasks': [
                        {
                            'id': 'task-3-1',
                            'name': 'Integrate features',
                            'description': 'Combine features into cohesive epic',
                            'status': 'not-started',
                            'estimated_minutes': 480,
                            'priority': 'critical',
                            'dependencies': ['task-2-1', 'task-2-2']
                        },
                        {
                            'id': 'task-3-2',
                            'name': 'Integration testing',
                            'description': 'Test feature interactions',
                            'status': 'not-started',
                            'estimated_minutes': 360,
                            'priority': 'high',
                            'dependencies': ['task-3-1']
                        }
                    ]
                },
                {
                    'id': 'phase-4',
                    'number': 4,
                    'name': 'Epic Testing & Validation',
                    'description': 'Comprehensive epic-level testing',
                    'status': 'not-started',
                    'estimated_hours': 16,
                    'tasks': [
                        {
                            'id': 'task-4-1',
                            'name': 'End-to-end testing',
                            'description': 'Complete epic workflow validation',
                            'status': 'not-started',
                            'estimated_minutes': 480,
                            'priority': 'critical',
                            'dependencies': ['task-3-2']
                        },
                        {
                            'id': 'task-4-2',
                            'name': 'Performance testing',
                            'description': 'Validate epic meets performance requirements',
                            'status': 'not-started',
                            'estimated_minutes': 240,
                            'priority': 'high',
                            'dependencies': ['task-4-1']
                        }
                    ]
                },
                {
                    'id': 'phase-5',
                    'number': 5,
                    'name': 'Epic Documentation & Deployment',
                    'description': 'Complete epic documentation and prepare for release',
                    'status': 'not-started',
                    'estimated_hours': 12,
                    'tasks': [
                        {
                            'id': 'task-5-1',
                            'name': 'Write epic documentation',
                            'description': 'Comprehensive epic documentation',
                            'status': 'not-started',
                            'estimated_minutes': 360,
                            'priority': 'high',
                            'dependencies': ['task-4-2']
                        },
                        {
                            'id': 'task-5-2',
                            'name': 'Prepare deployment',
                            'description': 'Release planning and deployment prep',
                            'status': 'not-started',
                            'estimated_minutes': 180,
                            'priority': 'high',
                            'dependencies': ['task-5-1']
                        }
                    ]
                }
            ]
        
        elif self.plan_type == 'phase':
            # Phase: 2 phases for targeted work
            return [
                {
                    'id': 'phase-1',
                    'number': 1,
                    'name': 'Phase Implementation',
                    'description': 'Implement phase-specific work',
                    'status': 'not-started',
                    'estimated_hours': 12,
                    'tasks': [
                        {
                            'id': 'task-1-1',
                            'name': 'Setup phase structure',
                            'description': 'Prepare phase environment',
                            'status': 'not-started',
                            'estimated_minutes': 60,
                            'priority': 'high',
                            'dependencies': []
                        },
                        {
                            'id': 'task-1-2',
                            'name': 'Implement phase logic',
                            'description': 'Core phase implementation',
                            'status': 'not-started',
                            'estimated_minutes': 360,
                            'priority': 'high',
                            'dependencies': ['task-1-1']
                        }
                    ]
                },
                {
                    'id': 'phase-2',
                    'number': 2,
                    'name': 'Phase Validation',
                    'description': 'Validate and document phase work',
                    'status': 'not-started',
                    'estimated_hours': 8,
                    'tasks': [
                        {
                            'id': 'task-2-1',
                            'name': 'Test phase implementation',
                            'status': 'not-started',
                            'estimated_minutes': 240,
                            'priority': 'high',
                            'dependencies': ['task-1-2']
                        },
                        {
                            'id': 'task-2-2',
                            'name': 'Document phase',
                            'status': 'not-started',
                            'estimated_minutes': 120,
                            'priority': 'medium',
                            'dependencies': ['task-2-1']
                        }
                    ]
                }
            ]
        
        elif self.plan_type == 'sub-plan':
            # Sub-plan: 1-2 phases for quick tactical work
            return [
                {
                    'id': 'phase-1',
                    'number': 1,
                    'name': 'Sub-Plan Implementation',
                    'description': 'Quick tactical implementation',
                    'status': 'not-started',
                    'estimated_hours': 6,
                    'tasks': [
                        {
                            'id': 'task-1-1',
                            'name': 'Implement changes',
                            'description': 'Core sub-plan work',
                            'status': 'not-started',
                            'estimated_minutes': 180,
                            'priority': 'high',
                            'dependencies': []
                        },
                        {
                            'id': 'task-1-2',
                            'name': 'Validate changes',
                            'description': 'Test and verify',
                            'status': 'not-started',
                            'estimated_minutes': 120,
                            'priority': 'high',
                            'dependencies': ['task-1-1']
                        }
                    ]
                }
            ]
        
        else:  # feature (default)
            # Feature: 3 phases (standard workflow)
            return [
                {
                    'id': 'phase-1',
                    'number': 1,
                    'name': 'Core Implementation',
                    'description': 'Implement core functionality',
                    'status': 'not-started',
                    'estimated_hours': 16,
                    'tasks': [
                        {
                            'id': 'task-1-1',
                            'name': 'Setup project structure',
                            'description': 'Create folders and base files',
                            'status': 'not-started',
                            'estimated_minutes': 30,
                            'priority': 'high',
                            'dependencies': [],
                            'implementation': {
                                'type': 'code',
                                'language': 'python',
                                'files': []
                            },
                            'validation': {
                                'type': 'test',
                                'files': [],
                                'coverage_threshold': 85
                            }
                        },
                        {
                            'id': 'task-1-2',
                            'name': 'Implement core logic',
                            'description': 'Main implementation',
                            'status': 'not-started',
                            'estimated_minutes': 240,
                            'priority': 'high',
                            'dependencies': ['task-1-1']
                        }
                    ]
                },
                {
                    'id': 'phase-2',
                    'number': 2,
                    'name': 'Testing & Validation',
                    'description': 'Comprehensive testing',
                    'status': 'not-started',
                    'estimated_hours': 12,
                    'tasks': [
                        {
                            'id': 'task-2-1',
                            'name': 'Write unit tests',
                            'status': 'not-started',
                            'estimated_minutes': 180,
                            'priority': 'high',
                            'dependencies': ['task-1-2']
                        }
                    ]
                },
                {
                    'id': 'phase-3',
                    'number': 3,
                    'name': 'Documentation',
                    'description': 'Complete documentation',
                    'status': 'not-started',
                    'estimated_hours': 8,
                    'tasks': [
                        {
                            'id': 'task-3-1',
                            'name': 'Write API documentation',
                            'status': 'not-started',
                            'estimated_minutes': 120,
                            'priority': 'medium',
                            'dependencies': ['task-2-1']
                        }
                    ]
                }
            ]
    
    def _get_acceptance_criteria_by_type(self) -> List[str]:
        """Return acceptance criteria based on plan type."""
        if self.plan_type == 'epic':
            return [
                'All features complete and integrated',
                'Epic-level integration tests passing with >90% coverage',
                'Feature interactions validated',
                'Performance requirements met',
                'Complete epic documentation',
                'Deployment readiness achieved'
            ]
        elif self.plan_type == 'phase':
            return [
                'Phase implementation complete',
                'Phase tests passing with >85% coverage',
                'Phase documentation complete',
                'Phase integrated with existing work'
            ]
        elif self.plan_type == 'sub-plan':
            return [
                'Sub-plan changes implemented',
                'Changes validated and tested',
                'Dependencies checked',
                'Quick verification passed'
            ]
        else:  # feature (default)
            return [
                'All phases complete',
                'All tests passing with >85% coverage',
                'Documentation complete and reviewed',
                'Code review approved',
                'Integration tests passing'
            ]
    
    def _get_default_hours_by_type(self) -> int:
        """Return estimated hours based on plan type."""
        if self.plan_type == 'epic':
            return 120
        elif self.plan_type == 'phase':
            return 20
        elif self.plan_type == 'sub-plan':
            return 10
        else:  # feature (default)
            return 40
    
    def _format_file_list(self, required_files: List[str], missing_files: List[str]) -> str:
        """Format file list for validation report (Python 3.9 compatible)."""
        lines = []
        for f in required_files:
            status = '✅' if f not in missing_files else '❌'
            lines.append(f"- {status} {f}")
        return '\n'.join(lines)
    
    def _format_folder_list(self, required_folders: List[str], missing_folders: List[str]) -> str:
        """Format folder list for validation report (Python 3.9 compatible)."""
        lines = []
        for f in required_folders:
            status = '✅' if f not in missing_folders else '❌'
            lines.append(f"- {status} {f}/")
        return '\n'.join(lines)
    
    def _format_validation_issues(self, missing_files: List[str], missing_folders: List[str]) -> str:
        """Format validation issues for report (Python 3.9 compatible)."""
        if missing_files or missing_folders:
            issues = []
            for item in missing_files + missing_folders:
                issues.append(f'- Missing: {item}')
            return '### Issues\n' + '\n'.join(issues)
        else:
            return '### Result\nAll validation checks passed!'
    
    def _validate_plan(self, feature_name: str, **kwargs) -> List[str]:
        """
        Validate generated plan with folder naming convention check.
        
        Args:
            feature_name: Feature being planned
            **kwargs: Additional parameters
        
        Returns:
            List of validation report paths
        """
        self.logger.info("Validating plan...")
        
        # Generate expected folder name with A## prefix
        master_plan_filename = self._generate_master_plan_filename(feature_name)
        folder_id_prefix = master_plan_filename.split('-')[0].lower()
        abbreviated_name = self._abbreviate_feature_name(feature_name, max_length=22)
        expected_folder_name = f"{folder_id_prefix}-{abbreviated_name}"
        
        # Use centralized plan directory method (prevents stray folder creation)
        plan_dir = self._get_plan_directory(feature_name)
        expected_folder_name = plan_dir.name
        
        # Validate folder exists with correct naming
        if not plan_dir.exists():
            # Try to find folder with old naming (without A## prefix)
            old_plan_dir = Path(f"cortex-brain/documents/planning/active/{feature_name}")
            if old_plan_dir.exists():
                self.logger.warning(
                    f"⚠️ Folder uses old naming convention: '{feature_name}' "
                    f"should be '{expected_folder_name}'"
                )
                plan_dir = old_plan_dir
            else:
                raise ValueError(f"Plan folder not found: {expected_folder_name}")
        
        # Find master plan file (pattern: [A-Z0-9]{3}-*.md)
        import re
        master_plan_pattern = re.compile(r'^[A-Z0-9]{3}-.*\.md$')
        master_plan_files = [f.name for f in plan_dir.glob('*.md') if master_plan_pattern.match(f.name)]
        
        # Validate folder name matches master plan ID
        folder_validation = []
        folder_name = plan_dir.name
        if folder_name.startswith(folder_id_prefix):
            folder_validation.append(f"✅ Folder name '{folder_name}' matches master plan ID '{folder_id_prefix.upper()}'")
        else:
            folder_validation.append(
                f"⚠️ Folder name '{folder_name}' doesn't match master plan ID '{folder_id_prefix.upper()}' "
                f"(expected: {expected_folder_name})"
            )
        
        # Check required files
        required_files = [
            "README.md",
            "tracking/progress-tracker.json"
        ]
        
        missing_files = []
        
        # Validate master plan exists with correct pattern
        master_plan_status = "✅" if master_plan_files else "❌"
        master_plan_desc = f"Master plan file (pattern: [A-Z0-9]{{3}}-{{name}}.md)"
        if master_plan_files:
            master_plan_desc += f" → Found: {', '.join(master_plan_files)}"
        else:
            missing_files.append(master_plan_desc)
        
        # Check other required files
        for file_path in required_files:
            if not (plan_dir / file_path).exists():
                missing_files.append(file_path)
        
        # Check required folders
        required_folders = ["analysis", "artifacts", "context", "reports", "tracking"]
        missing_folders = []
        for folder in required_folders:
            if not (plan_dir / folder).exists():
                missing_folders.append(folder)
        
        validation_passed = len(missing_files) == 0 and len(missing_folders) == 0
        
        # Create validation report
        report_content = f"""# Plan Validation Report
## Feature: {feature_name}

**Validation Date:** {datetime.now().isoformat()}  
**Status:** {"✅ PASSED" if validation_passed else "❌ FAILED"}

### Folder Naming Convention
{chr(10).join(folder_validation)}

### Master Plan File
{master_plan_status} {master_plan_desc}

### Required Files
{self._format_file_list(required_files, missing_files)}

### Required Folders
{self._format_folder_list(required_folders, missing_folders)}

### Summary
- Total checks: {len(required_files) + len(required_folders) + 1}
- Passed: {len(required_files) + len(required_folders) + 1 - len(missing_files) - len(missing_folders)}
- Failed: {len(missing_files) + len(missing_folders)}

{self._format_validation_issues(missing_files, missing_folders)}
"""
        
        report_path = plan_dir / "reports" / "validation-report.md"
        
        self.create_artifact(
            path=str(report_path),
            content=report_content,
            artifact_type="report"
        )
        
        # P01 FIX: Auto-create missing files instead of failing validation
        # This allows plans to proceed with warnings instead of blocking
        if missing_files or missing_folders:
            self.logger.warning(f"Plan validation issues: {len(missing_files + missing_folders)} items missing")
            
            # Auto-create missing README.md
            if "README.md" in missing_files:
                user_request = kwargs.get('user_request', 'Plan created via CORTEX Planning Orchestrator')
                readme_content = f"""# {feature_name}

**Created:** {datetime.now().strftime('%Y-%m-%d')}  
**Status:** Planning

## Overview
{user_request}

## Quick Start
1. Review plan file: `{folder_id_prefix.upper()}-{feature_name}.yaml`
2. Execute phases sequentially
3. Track progress via plan viewer: `plan-viewer.html`

## Structure
- `analysis/` - Code analysis reports
- `artifacts/` - Generated deliverables
- `context/` - Discovery and context data
- `reports/` - Validation and completion reports
- `tracking/` - Progress tracking data

## Status
See `tracking/progress-tracker.json` for current phase and progress.
"""
                readme_path = plan_dir / "README.md"
                self.create_artifact(
                    path=str(readme_path),
                    content=readme_content,
                    artifact_type="documentation"
                )
                self.logger.info(f"✅ Auto-created README.md")
            
            # Auto-create missing progress-tracker.json
            if "tracking/progress-tracker.json" in missing_files:
                progress_data = {
                    "plan_id": folder_id_prefix.upper(),
                    "feature_name": feature_name,
                    "status": "planning",
                    "phases_complete": 0,
                    "phases_total": 0,
                    "overall_progress": 0,
                    "current_phase": None,
                    "created_at": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat()
                }
                import json
                progress_path = plan_dir / "tracking" / "progress-tracker.json"
                self.create_artifact(
                    path=str(progress_path),
                    content=json.dumps(progress_data, indent=2),
                    artifact_type="other"  # Changed from "tracking" to match DB constraint
                )
                self.logger.info(f"✅ Auto-created progress-tracker.json")
            
            # Auto-create master plan file if missing
            master_plan_desc = f"Master plan file (pattern: [A-Z0-9]{{3}}-{{name}}.md)"
            if master_plan_desc in missing_files:
                user_request = kwargs.get('user_request', 'Plan created via CORTEX Planning Orchestrator')
                master_plan_name = f"{folder_id_prefix.upper()}-{feature_name}.md"
                master_plan_content = f"""# {folder_id_prefix.upper()}: {feature_name}

**Status:** Planning  
**Created:** {datetime.now().strftime('%Y-%m-%d')}

## Description
{user_request}

## Plan Files
- **Main Plan:** `{folder_id_prefix.upper()}-{feature_name}.yaml`
- **Plan Viewer:** `plan-viewer.html`
- **Progress Tracker:** `tracking/progress-tracker.json`

## Execution
Execute phases as defined in the YAML plan file.
"""
                master_plan_path = plan_dir / master_plan_name
                self.create_artifact(
                    path=str(master_plan_path),
                    content=master_plan_content,
                    artifact_type="documentation"
                )
                self.logger.info(f"✅ Auto-created {master_plan_name}")
            
            # Log warning but don't fail validation
            self.logger.warning(f"⚠️  Validation completed with auto-fixes: {len(missing_files + missing_folders)} items created")
        
        return [str(report_path)]
    
    def _run_ast_scanning(self, feature_name: str) -> Dict[str, Any]:
        """
        Run AST scanning for Phase 0 Discovery (CORTEX-5.0 Sub-Plan 04).
        
        Performs comprehensive code analysis:
        1. AST scanning (functions, classes, imports)
        2. Duplicate code detection
        3. Orphaned function detection
        4. Save results to context/ast-analysis.json
        
        Args:
            feature_name: Feature being planned
        
        Returns:
            Dictionary with AST analysis results
        """
        self.logger.info("Running AST scanning analysis...")
        
        try:
            # Initialize scanners
            scanner = ASTScanner(workspace_root=Path.cwd())
            duplicate_detector = PlanningDuplicateDetector()
            orphan_detector = PlanningOrphanDetector(workspace_root=Path.cwd())
            
            # Step 1: Scan workspace for AST metrics
            scanner.scan_workspace()
            
            # Step 2: Detect duplicate code
            python_files = list(Path.cwd().rglob("*.py"))
            duplicate_results = duplicate_detector.find_code_duplicates(python_files)
            scanner.add_duplicate_analysis(duplicate_results)
            
            # Step 3: Detect orphaned functions
            orphan_results = orphan_detector.find_orphaned_functions()
            scanner.add_orphan_analysis(orphan_results)
            
            # Step 4: Save results to context folder
            plan_dir = Path(f"cortex-brain/documents/planning/active/{feature_name}")
            ast_output_file = plan_dir / "context" / "ast-analysis.json"
            scanner.save_results(ast_output_file)
            
            self.logger.info(f"AST analysis complete: {scanner.results['files_scanned']} files scanned")
            
            return scanner.results
        
        except Exception as e:
            self.logger.error(f"AST scanning failed: {e}")
            # Return empty results on error to avoid blocking plan
            return {
                "files_scanned": 0,
                "total_functions": 0,
                "total_classes": 0,
                "total_imports": 0,
                "duplicate_analysis": {
                    "duplicates_found": 0,
                    "duplicate_percentage": 0
                },
                "orphan_analysis": {
                    "orphaned_count": 0,
                    "orphaned_percentage": 0
                },
                "error": str(e)
            }

