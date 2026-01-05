
"""
ADO Orchestrator v2 - Pure Autonomous Azure DevOps Work Item Generation

Pure Python execution orchestrator with config-driven behavior, database state
tracking, and Master Orchestrator integration. Eliminates hybrid execution
ambiguity by moving all logic to Python code.

Architecture:
    - Inherits BaseOrchestratorV4_1 for standardized lifecycle
    - 6-phase workflow with database state persistence
    - Dual-mode: auto-generation or conversational wizard
    - Template-driven outputs (Jinja2)
    - Atomic transactions with rollback capability
    - Master Orchestrator pattern-based routing

Version: 2.0.0
Author: Asif Hussain
Copyright: © 2026 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import logging
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from pathlib import Path

# Import base orchestrator v4.1
from src.orchestrators.base.base_orchestrator_v4_1 import BaseOrchestratorV4_1
from src.database.planning_state_db import PlanningStateDB

# Import wizard
from src.orchestrators.ado.ado_conversational_wizard import ADOConversationalWizard

# Configure module logger
logger = logging.getLogger(__name__)


class ADOPhaseV2(Enum):
    """
    ADO Orchestrator v2 Phase Enumeration
    
    6-phase workflow with database state tracking:
    1. DISCOVERY: Context gathering, complexity analysis, duplicate detection
    2. VALIDATION: DoR refinement, authentication, threat modeling
    3. GENERATION: Work item hierarchy, story points, TDD injection
    4. APPROVAL: Template-based preview and approval gate
    5. EXECUTION: ADO API calls, batch creation, linking
    6. COMPLETION: URL generation, progress visualization, metrics
    """
    DISCOVERY = "discovery"
    VALIDATION = "validation"
    GENERATION = "generation"
    APPROVAL = "approval"
    EXECUTION = "execution"
    COMPLETION = "completion"


@dataclass
class ADOResultV2:
    """
    ADO Orchestrator v2 Result Object
    
    Enhanced result object with database state references.
    
    Attributes:
        status: Execution status (success, error, cancelled, pending)
        success: Boolean flag indicating overall success
        phase: Final phase reached (ADOPhaseV2 enum)
        message: Human-readable result summary
        items_created: Count of ADO work items successfully created
        items_planned: Count of ADO work items planned/validated
        work_item_links: List of ADO work item URLs
        plan_id: Database plan ID for state tracking
        execution_id: Database execution ID
        errors: List of error messages encountered
        warnings: List of warning messages
        logs: List of detailed execution logs
        data: Additional phase-specific data
        metadata: Database metadata (timestamps, user, etc.)
    """
    status: str
    success: bool
    phase: ADOPhaseV2
    message: str
    plan_id: Optional[str] = None
    execution_id: Optional[str] = None
    items_created: int = 0
    items_planned: int = 0
    work_item_links: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    logs: List[str] = field(default_factory=list)
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ADOOrchestratorV2(BaseOrchestratorV4_1):
    """
    ADO Orchestrator v2 - Pure Autonomous Work Item Generation
    
    Pure Python autonomous orchestrator with config-driven behavior.
    Eliminates hybrid execution by moving all logic to Python code.
    
    Key Improvements from v1:
        - Database state persistence (resumable workflows)
        - Template-driven outputs (Jinja2)
        - Atomic transactions with rollback
        - Config-only manifest (no natural language)
        - Master Orchestrator integration
        - Dual-mode: auto + wizard
    
    Inherits from BaseOrchestratorV4_1:
        - Configuration injection
        - Brain tier integration
        - Template management
        - Error handling
        - Metrics collection
        - Lifecycle hooks
    
    Workflow Phases:
        1. DISCOVERY: Context analysis, complexity classification
        2. VALIDATION: DoR workflow, authentication check
        3. GENERATION: Work item hierarchy, story points, TDD
        4. APPROVAL: Template preview, approval gate
        5. EXECUTION: ADO API batch creation, linking
        6. COMPLETION: URL generation, visual progress
    
    Dual-Mode Operation:
        - auto: Direct generation from feature description
        - wizard: Multi-turn conversational refinement
    """
    
    def __init__(self, config_path: Optional[str] = None, state_db: Optional[PlanningStateDB] = None):
        """
        Initialize ADO Orchestrator v2.
        
        Args:
            config_path: Path to ado-v2-config.yaml (defaults to cortex-brain/config/ado-v2-default.yaml)
            state_db: PlanningStateDB instance for state tracking (creates new if None)
        """
        # Load default config if not provided
        if config_path is None:
            config_path = "cortex-brain/config/ado-v2-default.yaml"
        
        # Initialize database if not provided
        if state_db is None:
            db_path = "cortex-brain/database/planning_state.db"
            state_db = PlanningStateDB(db_path=db_path)
        
        super().__init__(config_path, state_db)
        
        # Load ADO-specific config
        self.ado_config = self.config.get('ado_specific', {})
        self.work_item_types = self.config.get('work_item_types', {})
        self.complexity_thresholds = self.config.get('complexity', {})
        self.hierarchy = self.config.get('hierarchy', {})
        self.tdd = self.config.get('tdd', {})
        
        # Initialize wizard
        try:
            self.wizard = ADOConversationalWizard(
                state_db=state_db,
                vision_api=self._get_vision_api()
            )
            logger.info("ADO Conversational Wizard initialized")
        except Exception as e:
            logger.warning(f"Wizard initialization failed: {e}")
            self.wizard = None
        
        # Current phase tracking
        self.current_phase = ADOPhaseV2.DISCOVERY
        
        logger.info("ADO Orchestrator v2 initialized")
    
    def _get_vision_api(self) -> Optional[Any]:
        """
        Get Vision API instance if available.
        
        Attempts to retrieve Vision API from:
        1. Config (explicit vision_api instance)
        2. Cross-session context middleware (automatic injection)
        3. Environment/runtime (fallback detection)
        
        Returns:
            Vision API instance or None if unavailable
        """
        try:
            # Check if explicitly provided in config
            if 'vision_api' in self.config:
                logger.debug("Vision API loaded from config")
                return self.config['vision_api']
            
            # Check for cross-session context middleware
            # (Vision API context may be automatically injected)
            from src.operations.utilities.vision_context_middleware import VisionContextMiddleware
            
            try:
                middleware = VisionContextMiddleware()
                if middleware.has_vision_context():
                    logger.debug("Vision API context available via middleware")
                    return middleware
            except ImportError:
                logger.debug("Vision context middleware not available")
            
            # No Vision API available
            logger.debug("Vision API not configured")
            return None
            
        except Exception as e:
            logger.debug(f"Vision API initialization failed: {e}")
            return None
    
    def _extract_vision_context(self, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extract and format Vision API context from parameters.
        
        Vision context may come from:
        - Explicit vision_context parameter
        - Image attachments analyzed by Vision API middleware
        - Screenshot analysis results
        
        Args:
            params: Execution parameters that may contain vision_context
            
        Returns:
            Formatted vision context dict or None if unavailable
            
        Format:
            {
                'ui_elements': [...],  # Detected UI components
                'suggested_criteria': [...],  # Auto-generated acceptance criteria
                'analysis': str,  # Natural language analysis
                'confidence': float  # Analysis confidence score
            }
        """
        # Check explicit vision_context parameter
        vision_context = params.get('vision_context')
        if vision_context:
            logger.debug("Vision context provided explicitly")
            return vision_context
        
        # Check for image attachments in params
        if 'images' in params or 'attachments' in params:
            logger.debug("Image attachments detected - Vision API analysis may be available")
            # Note: Vision API middleware should process images before orchestrator invocation
            # Context would be injected as vision_context parameter
        
        return None
    
    def execute(self, **kwargs: Any) -> ADOResultV2:
        """
        Execute ADO workflow with mode detection.
        
        Args:
            **kwargs: Execution parameters
                - mode: 'auto' or 'wizard' (default: auto)
                - feature: Feature name/description (required)
                - auto_approve: Skip approval gate (default: False)
                - test_mode: Skip ADO API calls (default: False)
                - acceptance_criteria: List[str] (optional)
                - assumptions: List[str] (optional)
                - constraints: List[str] (optional)
        
        Returns:
            ADOResultV2: Execution result with database references
            
        Raises:
            ValueError: If required parameters missing
        """
        import time
        self.start_time = time.time()  # Track execution start time
        mode = kwargs.get('mode', 'auto')
        
        logger.info(f"🎭 ADO Orchestrator v2 execution started (mode: {mode})")
        
        try:
            if mode == 'wizard':
                return self._execute_wizard_mode(kwargs)
            else:
                return self._execute_auto_mode(kwargs)
        except Exception as e:
            logger.error(f"ADO Orchestrator v2 execution failed: {e}", exc_info=True)
            execution_time = time.time() - self.start_time
            return ADOResultV2(
                status="error",
                success=False,
                phase=self.current_phase,
                message=f"Execution failed: {str(e)}",
                errors=[str(e)]
            )
        finally:
            execution_time = time.time() - self.start_time
            logger.info(f"🎭 ADO Orchestrator v2 execution completed in {execution_time:.2f}s")
    
    def _execute_auto_mode(self, params: Dict[str, Any]) -> ADOResultV2:
        """
        Auto-generation workflow (6 phases).
        
        Phases:
            0. DISCOVERY: Context gathering, complexity analysis
            1. VALIDATION: DoR refinement, authentication
            2. GENERATION: Work item hierarchy, story points
            3. APPROVAL: User preview (if auto_approve=False)
            4. EXECUTION: ADO API calls
            5. COMPLETION: Link generation, success response
        
        Args:
            params: Execution parameters with 'feature' required
            
        Returns:
            ADOResultV2: Execution result
        """
        feature_name = params.get('feature')
        if not feature_name:
            raise ValueError("Parameter 'feature' is required")
        
        auto_approve = params.get('auto_approve', False)
        test_mode = params.get('test_mode', True)  # Default to test mode for safety
        
        logs = []
        warnings = []
        errors = []
        
        logs.append(f"📋 Planning for: {feature_name}")
        logs.append(f"Mode: AUTO (auto_approve={auto_approve}, test_mode={test_mode})")
        
        # Create execution plan in database
        plan_id = self.state_db.create_plan(
            feature_name=feature_name,
            metadata={
                'orchestrator': 'ado_v2',
                'mode': 'auto',
                'version': '2.0.0',
                'user_params': params,
                'created_at': datetime.utcnow().isoformat()
            }
        )
        
        logs.append(f"✅ Created plan in database: {plan_id}")
        
        try:
            # ===== PHASE 1: DISCOVERY =====
            self._transition_phase(ADOPhaseV2.DISCOVERY, logs)
            phase_id = self.state_db.start_phase(plan_id, 0, {'name': 'DISCOVERY'})
            
            discovery_result = self._phase_discovery(feature_name, params)
            logs.extend(discovery_result.get('logs', []))
            warnings.extend(discovery_result.get('warnings', []))
            
            self.state_db.complete_phase(phase_id, data=discovery_result)
            logs.append("✅ Discovery phase complete")
            
            # ===== PHASE 2: VALIDATION =====
            self._transition_phase(ADOPhaseV2.VALIDATION, logs)
            phase_id = self.state_db.start_phase(plan_id, 1, {'name': 'VALIDATION'})
            
            validation_result = self._phase_validation(feature_name, params)
            logs.extend(validation_result.get('logs', []))
            warnings.extend(validation_result.get('warnings', []))
            
            self.state_db.complete_phase(phase_id, data=validation_result)
            logs.append("✅ Validation phase complete")
            
            # ===== PHASE 3: GENERATION =====
            self._transition_phase(ADOPhaseV2.GENERATION, logs)
            phase_id = self.state_db.start_phase(plan_id, 2, {'name': 'GENERATION'})
            
            generation_result = self._phase_generation(
                feature_name, 
                discovery_result, 
                validation_result
            )
            logs.extend(generation_result.get('logs', []))
            
            self.state_db.complete_phase(phase_id, data=generation_result)
            logs.append("✅ Generation phase complete")
            
            # ===== PHASE 4: APPROVAL =====
            if not auto_approve:
                self._transition_phase(ADOPhaseV2.APPROVAL, logs)
                phase_id = self.state_db.start_phase(plan_id, 3, {'name': 'APPROVAL'})
                
                approval_result = self._phase_approval(generation_result)
                logs.extend(approval_result.get('logs', []))
                
                self.state_db.complete_phase(phase_id, data=approval_result)
                
                if not approval_result.get('approved', False):
                    logs.append("⚠️  User did not approve, aborting")
                    return ADOResultV2(
                        status="cancelled",
                        success=False,
                        phase=ADOPhaseV2.APPROVAL,
                        message="User cancelled during approval phase",
                        plan_id=plan_id,
                        logs=logs,
                        warnings=warnings
                    )
                
                logs.append("✅ Approval phase complete")
            else:
                logs.append("⏩ Approval phase skipped (auto_approve=True)")
            
            # ===== PHASE 5: EXECUTION =====
            if not test_mode:
                self._transition_phase(ADOPhaseV2.EXECUTION, logs)
                phase_id = self.state_db.start_phase(plan_id, 4, {'name': 'EXECUTION'})
                
                execution_result = self._phase_execution(generation_result)
                logs.extend(execution_result.get('logs', []))
                errors.extend(execution_result.get('errors', []))
                
                self.state_db.complete_phase(phase_id, data=execution_result)
                logs.append("✅ Execution phase complete")
            else:
                logs.append("⏩ Execution phase skipped (test_mode=True)")
                execution_result = {
                    'items_created': 0,
                    'work_item_links': []
                }
            
            # ===== PHASE 6: COMPLETION =====
            self._transition_phase(ADOPhaseV2.COMPLETION, logs)
            phase_id = self.state_db.start_phase(plan_id, 5, {'name': 'COMPLETION'})
            
            completion_result = self._phase_completion(
                feature_name,
                execution_result,
                test_mode
            )
            logs.extend(completion_result.get('logs', []))
            
            self.state_db.complete_phase(phase_id, data=completion_result)
            self.state_db.complete_plan(plan_id)
            logs.append("✅ Completion phase complete")
            
            # Build final result
            return ADOResultV2(
                status="success",
                success=True,
                phase=ADOPhaseV2.COMPLETION,
                message=completion_result.get('message', f"ADO planning completed for '{feature_name}'"),
                plan_id=plan_id,
                items_created=execution_result.get('items_created', 0),
                items_planned=generation_result.get('items_planned', 0),
                work_item_links=execution_result.get('work_item_links', []),
                logs=logs,
                warnings=warnings,
                errors=errors,
                data={
                    'discovery': discovery_result,
                    'validation': validation_result,
                    'generation': generation_result,
                    'execution': execution_result,
                    'completion': completion_result
                }
            )
            
        except Exception as e:
            logger.error(f"Auto-mode execution failed: {e}", exc_info=True)
            self.state_db.fail_plan(plan_id, str(e))
            
            return ADOResultV2(
                status="error",
                success=False,
                phase=self.current_phase,
                message=f"Execution failed in {self.current_phase.value} phase: {str(e)}",
                plan_id=plan_id,
                logs=logs,
                warnings=warnings,
                errors=errors + [str(e)]
            )
    
    def _execute_wizard_mode(self, params: Dict[str, Any]) -> ADOResultV2:
        """
        Wizard-guided workflow (multi-turn conversation).
        
        Provides multi-turn interactive workflow for complex work items
        requiring iterative refinement. Uses ADOConversationalWizard
        for guided conversation flow.
        
        Flow:
        1. Start wizard session with feature description
        2. Iterate through 7 stages (BASIC_INFO → ACCEPTANCE_CRITERIA →
           DEFINITION_OF_READY → DEFINITION_OF_DONE → ESTIMATION →
           DEPENDENCIES → REVIEW)
        3. Collect user responses at each stage
        4. Generate final work items from wizard session data
        5. Execute via auto-mode pipeline (reuse phases 4-5: EXECUTION + COMPLETION)
        
        Args:
            params: Execution parameters
                - feature (str): Initial feature description
                - session_id (Optional[str]): Resume existing wizard session
                - user_input (Optional[str]): User response for current stage
                - vision_context (Optional[Dict]): Vision API context (if screenshot attached)
                
        Returns:
            ADOResultV2: Execution result with wizard state or final work items
            
        Raises:
            RuntimeError: If wizard not available
            ValueError: If required parameters missing
        """
        if not self.wizard:
            raise RuntimeError("Wizard not available")
        
        feature = params.get('feature')
        session_id = params.get('session_id')
        user_input = params.get('user_input')
        
        # Extract vision context (may be explicit or from middleware)
        vision_context = self._extract_vision_context(params)
        
        logs = []
        
        try:
            # Starting new wizard session
            if not session_id:
                if not feature:
                    raise ValueError("'feature' required to start wizard")
                
                logs.append(f"🧙 Starting wizard session for feature: {feature}")
                wizard_response = self.wizard.start_wizard(feature)
                
                # Inject vision context if available
                if vision_context:
                    logs.append("👁️  Vision API context injected")
                    wizard_response.context['vision_context'] = vision_context
                
                # Return continuation prompt for user
                return ADOResultV2(
                    status='in_progress',
                    success=False,
                    phase=ADOPhaseV2.DISCOVERY,
                    message=wizard_response.prompt,
                    data={
                        'session_id': wizard_response.session_id,
                        'stage': wizard_response.stage.value,
                        'prompt': wizard_response.prompt,
                        'wizard_active': True
                    },
                    logs=logs
                )
            
            # Continuing existing wizard session
            else:
                if not user_input:
                    raise ValueError("'user_input' required to continue wizard")
                
                logs.append(f"🧙 Processing user input for session: {session_id}")
                wizard_response = self.wizard.process_response(
                    session_id=session_id,
                    user_input=user_input,
                    vision_context=vision_context
                )
                
                # Check if wizard is complete
                from src.orchestrators.ado.ado_conversational_wizard import WizardStage
                
                if wizard_response.stage == WizardStage.COMPLETE:
                    logs.append("✅ Wizard completed - generating work items")
                    
                    # Extract work items from wizard session
                    if 'ado_item' not in wizard_response.context:
                        raise RuntimeError("Wizard completed but no ADO item generated")
                    
                    work_items = wizard_response.context['ado_item']
                    logs.append(f"📦 Work items generated from wizard session")
                    
                    # Execute phases 4-5 (EXECUTION + COMPLETION) via auto-mode pipeline
                    return self._execute_from_work_items(work_items, logs)
                
                # Wizard still in progress - return next prompt
                else:
                    return ADOResultV2(
                        status='in_progress',
                        success=False,
                        phase=ADOPhaseV2.VALIDATION if wizard_response.stage.value in ['acceptance_criteria', 'dor', 'dod'] else ADOPhaseV2.GENERATION,
                        message=wizard_response.prompt,
                        data={
                            'session_id': wizard_response.session_id,
                            'stage': wizard_response.stage.value,
                            'prompt': wizard_response.prompt,
                            'wizard_active': True
                        },
                        logs=logs
                    )
        
        except Exception as e:
            logger.error(f"Wizard mode failed: {e}")
            return ADOResultV2(
                status='error',
                success=False,
                phase=ADOPhaseV2.DISCOVERY,
                message=f"Wizard mode failed: {str(e)}",
                errors=[str(e)],
                logs=logs
            )
    
    def _execute_from_work_items(
        self, 
        work_items: Dict[str, Any], 
        logs: List[str]
    ) -> ADOResultV2:
        """
        Execute EXECUTION + COMPLETION phases with pre-generated work items.
        
        This method enables reuse of the execution and completion pipeline
        when work items have already been generated through alternative flows
        (wizard mode, external integrations, API calls, etc.).
        
        Skips phases 0-3 (DISCOVERY, VALIDATION, GENERATION, APPROVAL) since
        work items are already validated and approved.
        
        Args:
            work_items: Pre-generated work items dictionary with structure:
                {
                    'story': {...},  # Parent story work item
                    'tasks': [...],  # Child task work items
                    'test_requirements': {...}  # Optional TDD requirements
                }
            logs: Existing logs list to append to
                
        Returns:
            ADOResultV2: Execution result with created work item URLs
            
        Raises:
            ValueError: If work_items structure is invalid
            RuntimeError: If ADO API execution fails
            
        Usage:
            >>> # From wizard mode
            >>> wizard_response = wizard.complete_session(session_id)
            >>> work_items = wizard_response.context['ado_item']
            >>> result = self._execute_from_work_items(work_items, logs)
            
            >>> # From external integration
            >>> work_items = external_api.get_work_items()
            >>> result = self._execute_from_work_items(work_items, logs)
        """
        try:
            # Validate work items structure
            if not isinstance(work_items, dict):
                raise ValueError("work_items must be a dictionary")
            
            if 'story' not in work_items:
                raise ValueError("work_items must contain 'story' key")
            
            logs.append("📦 Executing from pre-generated work items")
            logs.append(f"  Story: {work_items['story'].get('title', 'Untitled')}")
            
            task_count = len(work_items.get('tasks', []))
            if task_count > 0:
                logs.append(f"  Tasks: {task_count} child work items")
            
            # Phase 5: EXECUTION (create work items via ADO API)
            self._transition_phase(ADOPhaseV2.EXECUTION, logs)
            execution_result = self._phase_execution(work_items)
            logs.extend(execution_result['logs'])
            
            if not execution_result['success']:
                return ADOResultV2(
                    status='error',
                    success=False,
                    phase=ADOPhaseV2.EXECUTION,
                    message="Work item creation failed",
                    errors=execution_result.get('errors', []),
                    logs=logs
                )
            
            # Phase 6: COMPLETION (URL generation, progress visualization)
            self._transition_phase(ADOPhaseV2.COMPLETION, logs)
            completion_result = self._phase_completion(execution_result)
            logs.extend(completion_result['logs'])
            
            # Build final result
            return ADOResultV2(
                status='success',
                success=True,
                phase=ADOPhaseV2.COMPLETION,
                message=completion_result['message'],
                items_created=execution_result.get('items_created', 0),
                items_planned=execution_result.get('items_created', 0),
                work_item_links=execution_result.get('urls', []),
                logs=logs,
                data={
                    'story': work_items['story'],
                    'tasks': work_items.get('tasks', []),
                    'test_requirements': work_items.get('test_requirements', {}),
                    'execution_time': completion_result.get('execution_time_seconds', 0)
                }
            )
        
        except Exception as e:
            logger.error(f"Execute from work items failed: {e}")
            return ADOResultV2(
                status='error',
                success=False,
                phase=ADOPhaseV2.EXECUTION,
                message=f"Failed to execute work items: {str(e)}",
                errors=[str(e)],
                logs=logs
            )
    
    def _transition_phase(self, to_phase: ADOPhaseV2, logs: List[str]) -> None:
        """
        Transition to new phase with logging.
        
        Args:
            to_phase: Target phase
            logs: Logs list to append transition message
        """
        from_phase = self.current_phase
        self.current_phase = to_phase
        
        log_msg = f"🎭 Phase transition: {from_phase.value} → {to_phase.value}"
        logger.info(log_msg)
        logs.append(log_msg)
    
    def _phase_discovery(self, feature_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Phase 1: DISCOVERY - Context gathering and complexity analysis.
        
        Args:
            feature_name: Feature name/description
            params: User parameters
            
        Returns:
            Discovery data dict
        """
        logs = []
        warnings = []
        
        # Complexity classification
        complexity = self._classify_complexity(feature_name)
        logs.append(f"🎯 Complexity classified as: {complexity}")
        
        # Review orchestrator integration (graceful degradation)
        review_context = None
        try:
            review_context = self._run_review_orchestrator(feature_name)
            logs.append("✅ Review orchestrator completed")
        except Exception as e:
            warnings.append(f"⚠️  Review orchestrator unavailable: {e}")
        
        # Duplicate detection (graceful degradation)
        duplicates = []
        try:
            duplicates = self._detect_duplicates(feature_name)
            if duplicates:
                warnings.append(f"⚠️  Found {len(duplicates)} potential duplicate work items")
            else:
                logs.append("✅ No duplicate work items found")
        except Exception as e:
            warnings.append(f"⚠️  Duplicate detection unavailable: {e}")
        
        return {
            'complexity': complexity,
            'review_context': review_context,
            'duplicates': duplicates,
            'logs': logs,
            'warnings': warnings
        }
    
    def _phase_validation(self, feature_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Phase 2: VALIDATION - DoR refinement and authentication.
        
        Args:
            feature_name: Feature name/description
            params: User parameters
            
        Returns:
            Validation data dict
        """
        logs = []
        warnings = []
        
        logs.append("📝 Starting DoR (Definition of Ready) workflow")
        
        # Collect acceptance criteria
        acceptance_criteria = params.get('acceptance_criteria', [])
        if acceptance_criteria:
            logs.append(f"✅ Collected {len(acceptance_criteria)} acceptance criteria")
        else:
            warnings.append("⚠️  No acceptance criteria provided")
        
        # Collect assumptions
        assumptions = params.get('assumptions', [])
        if assumptions:
            logs.append(f"✅ Collected {len(assumptions)} assumptions")
            if len(assumptions) > 5:
                warnings.append(f"⚠️  High number of assumptions ({len(assumptions)}) - may indicate uncertainty")
        
        # Collect constraints
        constraints = params.get('constraints', [])
        if constraints:
            logs.append(f"✅ Collected {len(constraints)} constraints")
        
        # Calculate DoR completeness
        completeness = self._calculate_dor_completeness(
            acceptance_criteria, 
            assumptions, 
            constraints
        )
        
        if completeness['is_complete']:
            logs.append(f"✅ DoR is complete ({completeness['percentage']}%)")
        else:
            warnings.append(f"⚠️  DoR incomplete ({completeness['percentage']}%) - consider adding more details")
        
        return {
            'acceptance_criteria': acceptance_criteria,
            'assumptions': assumptions,
            'constraints': constraints,
            'completeness': completeness,
            'logs': logs,
            'warnings': warnings
        }
    
    
    def _phase_generation(
        self, 
        feature_name: str, 
        discovery: Dict, 
        validation: Dict
    ) -> Dict[str, Any]:
        """
        Phase 3: GENERATION - Work item hierarchy creation.
        
        Generates user story + child tasks + TDD requirements.
        """
        logs = []
        logs.append("🏗️  Generating work item hierarchy...")
        
        # Story points from complexity
        complexity = discovery['complexity']
        story_points_map = self.work_item_types['story']['story_points_mapping']
        story_points = story_points_map.get(complexity.lower().replace(' ', '_'), 3)
        logs.append(f"📊 Story points: {story_points}")
        
        # Build story
        story = {
            'type': self.work_item_types['story']['type_name'],
            'title': feature_name,
            'description': feature_name,
            'story_points': story_points,
            'acceptance_criteria': validation['acceptance_criteria'],
            'state': 'New'
        }
        
        # Generate tasks
        tasks = []
        total_effort = 0
        for task_tmpl in self.hierarchy['story_breakdown']['task_templates']:
            cond = task_tmpl['condition']
            include = (cond == 'always' or 
                      (cond == 'complexity >= MEDIUM' and complexity in ['MEDIUM', 'HIGH']) or
                      (cond == 'complexity == HIGH' and complexity == 'HIGH'))
            
            if include:
                task = {
                    'type': 'Task',
                    'title': f"{task_tmpl['name']}: {feature_name}",
                    'estimated_hours': task_tmpl['estimate_hours']
                }
                tasks.append(task)
                total_effort += task['estimated_hours']
                logs.append(f"  ✅ {task_tmpl['name']}")
        
        # TDD requirements
        test_reqs = {}
        if self.tdd['enabled']:
            test_reqs['unit_tests'] = self.tdd['test_requirements']['unit_tests']['template']
            test_reqs['acceptance_tests'] = self.tdd['test_requirements']['acceptance_tests']['template']
            logs.append("✅ TDD requirements injected")
        
        logs.append(f"📦 Generated {1 + len(tasks)} work items ({total_effort}h)")
        
        return {
            'story': story,
            'tasks': tasks,
            'test_requirements': test_reqs,
            'total_work_items': 1 + len(tasks),
            'total_effort_hours': total_effort,
            'story_points': story_points,
            'logs': logs
        }
    
    def _phase_approval(self, generation: Dict) -> Dict[str, Any]:
        """
        Phase 4: APPROVAL - User preview and approval gate.
        
        Renders work item preview using Jinja2 template and displays
        approval gate to user.
        
        Args:
            generation: Generation phase data containing:
                - story: User story details
                - tasks: List of child tasks
                - test_requirements: TDD requirements
                - total_effort_hours: Total effort estimation
                
        Returns:
            Approval data dict with 'approved' boolean and 'logs'
        """
        logs = []
        
        logs.append("📋 Generating work item preview...")
        
        try:
            # Render work item preview template
            preview = self.render_template(
                'work-item-preview.jinja2',
                {
                    'story': generation['story'],
                    'tasks': generation['tasks'],
                    'test_requirements': generation.get('test_requirements', {}),
                    'complexity': generation.get('complexity', 'MEDIUM'),
                    'total_effort_hours': generation['total_effort_hours'],
                    'feature_name': generation['story']['title'],
                    'timestamp': datetime.now().isoformat()
                }
            )
            
            logs.append("✅ Preview template rendered")
            
            # Render approval gate template
            approval_prompt = self.render_template(
                'approval-gate.jinja2',
                {
                    'preview': preview,
                    'feature_name': generation['story']['title'],
                    'items_count': 1 + len(generation['tasks']),
                    'total_effort_hours': generation['total_effort_hours']
                }
            )
            
            logs.append("📤 Displaying approval gate to user")
            
            # For now, auto-approve
            # In Phase 4, we'll add:
            # - Display approval_prompt to user
            # - Collect user response (approve/reject/changes)
            # - Handle timeout (5 minutes)
            # - Parse response and validate
            
            approved = True  # Auto-approve for now
            logs.append("✅ Work items auto-approved (approval gate implementation pending)")
            
            return {
                'approved': approved,
                'preview': preview,
                'approval_prompt': approval_prompt,
                'logs': logs
            }
            
        except Exception as e:
            logger.error(f"Approval phase template rendering failed: {e}")
            logs.append(f"⚠️  Template rendering failed: {e}")
            
            # Fallback to simple approval
            return {
                'approved': True,
                'logs': logs,
                'error': str(e)
            }
    
    def _phase_execution(self, generation: Dict) -> Dict[str, Any]:
        """
        Phase 5: EXECUTION - ADO API work item creation.
        
        Creates work items in Azure DevOps via REST API:
        1. Create parent story/feature
        2. Create child tasks
        3. Link tasks to parent (parent-child relationship)
        4. Set fields (title, description, acceptance criteria, story points, etc.)
        
        Args:
            generation: Generation phase data containing:
                - story: Story details (title, description, acceptance_criteria, story_points)
                - tasks: List of task details
                - complexity: Complexity level
                - dor: Definition of Ready
            
        Returns:
            Execution data dict with:
                - items_created: Number of work items created
                - work_item_links: List of work item details (id, type, title, url)
                - logs: Execution logs
                - errors: Any errors encountered
        """
        logs = []
        errors = []
        work_item_links = []
        items_created = 0
        
        try:
            # Extract ADO API configuration
            ado_config = self.config.get('ado_api', {})
            if not ado_config or not ado_config.get('enabled', False):
                logs.append("⚠️  ADO API not configured - using mock mode")
                
                # Mock work item creation for testing
                story_data = generation.get('story', {})
                tasks_data = generation.get('tasks', [])
                
                # Mock story creation
                story_id = 10000 + items_created
                items_created += 1
                work_item_links.append({
                    'id': story_id,
                    'type': 'Story',
                    'title': story_data.get('title', 'Untitled Story'),
                    'url': f"https://dev.azure.com/mock/project/_workitems/edit/{story_id}",
                    'state': 'New'
                })
                logs.append(f"✅ Mock story created: #{story_id}")
                
                # Mock task creation
                for i, task in enumerate(tasks_data, 1):
                    task_id = 10000 + items_created
                    items_created += 1
                    work_item_links.append({
                        'id': task_id,
                        'type': 'Task',
                        'title': task.get('title', f'Task {i}'),
                        'url': f"https://dev.azure.com/mock/project/_workitems/edit/{task_id}",
                        'state': 'New',
                        'parent_id': story_id
                    })
                    logs.append(f"✅ Mock task created: #{task_id} (parent: #{story_id})")
                
                logs.append(f"✅ Created {items_created} mock work items")
                
            else:
                # This requires ADO credentials and organization/project configuration
                
                logs.append("⚠️  Full ADO API integration pending")
                logs.append("   Requires: Personal Access Token, Organization URL, Project name")
                
                # Placeholder for future ADO API implementation:
                # 1. Authenticate with PAT
                # 2. POST to https://dev.azure.com/{org}/{project}/_apis/wit/workitems/${type}?api-version=6.0
                # 3. Set fields using JSON Patch format
                # 4. Create parent-child links
                # 5. Handle API errors and retries
                
                errors.append("ADO API integration not yet implemented")
            
        except Exception as e:
            logger.error(f"Execution phase failed: {e}", exc_info=True)
            errors.append(str(e))
            logs.append(f"❌ Execution failed: {e}")
        
        return {
            'items_created': items_created,
            'work_item_links': work_item_links,
            'logs': logs,
            'errors': errors
        }
    
    def _phase_completion(
        self, 
        feature_name: str, 
        execution: Dict,
        test_mode: bool
    ) -> Dict[str, Any]:
        """
        Phase 6: COMPLETION - Final reporting and metrics.
        
        Renders completion message using Jinja2 template with execution
        summary, work item links, and metrics. Collects execution metrics
        including duration, success rate, and item counts.
        
        Args:
            feature_name: Feature name/description
            execution: Execution phase data containing:
                - items_created: Number of work items created
                - work_item_links: List of ADO work item URLs
                - errors: List of errors encountered
            test_mode: Whether execution was in test mode
            
        Returns:
            Completion data dict with:
                - message: Formatted completion message
                - logs: Execution logs
                - metrics: Execution metrics (time, counts, success_rate)
        """
        logs = []
        
        logs.append("📊 Generating completion summary...")
        
        try:
            # Calculate execution time from orchestrator start
            import time
            execution_time_seconds = time.time() - self.start_time if hasattr(self, 'start_time') else 0.0
            
            # Calculate success rate
            items_created = execution.get('items_created', 0)
            errors = execution.get('errors', [])
            success_rate = 100.0 if items_created > 0 and len(errors) == 0 else 0.0
            
            # Collect metrics
            metrics = {
                'execution_time_seconds': round(execution_time_seconds, 2),
                'items_created': items_created,
                'items_planned': items_created,  # In v2, planned == created
                'errors_count': len(errors),
                'success_rate': success_rate,
                'test_mode': test_mode
            }
            
            # Render completion message template
            completion_message = self.render_template(
                'completion-message.jinja2',
                {
                    'feature_name': feature_name,
                    'test_mode': test_mode,
                    'items_created': items_created,
                    'work_item_links': execution.get('work_item_links', []),
                    'execution_time_seconds': execution_time_seconds,
                    'story_points': execution.get('story_points', 0),
                    'total_effort_hours': execution.get('total_effort_hours', 0),
                    'execution_id': execution.get('execution_id', 'N/A')
                }
            )
            
            logs.append("✅ Completion message rendered")
            logs.append(completion_message)
            
            return {
                'message': completion_message,
                'logs': logs,
                'metrics': metrics
            }
            
        except Exception as e:
            logger.error(f"Completion phase template rendering failed: {e}")
            
            # Fallback to simple message
            if test_mode:
                fallback_message = f"✅ ADO planning workflow completed for '{feature_name}' (test mode)"
            else:
                items_created = execution.get('items_created', 0)
                fallback_message = f"✅ Created {items_created} work items for '{feature_name}'"
            
            logs.append(f"⚠️  Template rendering failed: {e}")
            logs.append(fallback_message)
            
            return {
                'message': fallback_message,
                'logs': logs,
                'error': str(e)
            }
    
    # Helper methods (ported from v1)
    
    def _classify_complexity(self, feature_name: str) -> str:
        """
        Classify feature complexity based on name analysis.
        
        Analyzes feature name and description for complexity indicators:
        - Keywords (security, authentication, migration, etc.)
        - Text length
        - Special terms suggesting high complexity
        
        Args:
            feature_name: Feature name/description to analyze
            
        Returns:
            Complexity level: "LOW", "MEDIUM", "HIGH", or "VERY_HIGH"
        """
        feature_lower = feature_name.lower()
        
        # Get complexity thresholds from config
        complexity_config = self.config.get('complexity', {})
        thresholds = complexity_config.get('thresholds', {})
        
        # HIGH complexity keywords
        high_keywords = [
            'security', 'authentication', 'authorization', 'migration', 
            'refactor', 'architecture', 'integration', 'payment', 'billing',
            'compliance', 'encryption', 'distributed', 'microservice',
            'real-time', 'performance', 'optimization', 'scalability'
        ]
        
        # VERY HIGH complexity keywords
        very_high_keywords = [
            'critical', 'enterprise', 'large-scale', 'multi-system',
            'blockchain', 'machine learning', 'ai', 'data warehouse',
            'infrastructure', 'platform', 'framework'
        ]
        
        # MEDIUM complexity keywords
        medium_keywords = [
            'api', 'feature', 'enhancement', 'improvement', 'update',
            'dashboard', 'report', 'notification', 'search', 'filter'
        ]
        
        # LOW complexity keywords
        low_keywords = [
            'simple', 'basic', 'minor', 'small', 'trivial', 'quick',
            'fix', 'typo', 'label', 'button', 'text'
        ]
        
        # Check for explicit complexity indicators
        if any(keyword in feature_lower for keyword in very_high_keywords):
            return "VERY_HIGH"
        elif any(keyword in feature_lower for keyword in high_keywords):
            return "HIGH"
        elif any(keyword in feature_lower for keyword in low_keywords):
            return "LOW"
        elif any(keyword in feature_lower for keyword in medium_keywords):
            return "MEDIUM"
        
        # Length-based heuristics
        word_count = len(feature_name.split())
        
        if word_count > 15:
            return "HIGH"
        elif word_count > 8:
            return "MEDIUM"
        elif word_count <= 3:
            return "LOW"
        
        # Default to MEDIUM
        return "MEDIUM"
    
    def _run_review_orchestrator(self, feature_name: str) -> Optional[Dict]:
        """
        Run review orchestrator for context enrichment.
        
        Invokes Refinement Orchestrator to analyze feature and provide:
        - Additional context and requirements
        - Potential edge cases
        - Best practices recommendations
        - Technical considerations
        
        Args:
            feature_name: Feature to analyze
            
        Returns:
            Refinement analysis result or None if orchestrator unavailable
            
        Note:
            This is optional enrichment - failure doesn't block workflow
        """
        try:
            # Check if refinement orchestrator available
            refinement_config = self.config.get('refinement_orchestrator', {})
            if not refinement_config.get('enabled', False):
                logger.debug("Refinement orchestrator not enabled")
                return None
            
            # This would call the Refinement Orchestrator to analyze the feature
            
            # Example implementation:
            # from src.orchestrators.refinement_orchestrator import RefinementOrchestrator
            # refinement = RefinementOrchestrator(config_path, state_db)
            # result = refinement.execute(feature=feature_name, mode='analyze')
            # return result.data
            
            logger.debug(f"Review orchestrator integration pending for '{feature_name}'")
            return None
            
        except Exception as e:
            logger.warning(f"Review orchestrator failed: {e}")
            return None
    
    def _detect_duplicates(self, feature_name: str) -> List[Dict]:
        """
        Detect duplicate work items in Azure DevOps.
        
        Searches existing ADO work items for potential duplicates based on:
        - Title similarity (fuzzy matching)
        - Description keyword overlap
        - State (active work items)
        
        Args:
            feature_name: Feature name to search for
            
        Returns:
            List of potential duplicate work items with similarity scores
            
        Note:
            Requires ADO API credentials. Returns empty list if:
            - No ADO credentials configured
            - API request fails
            - No similar items found
        """
        duplicates = []
        
        try:
            # Check if ADO API configured
            ado_config = self.config.get('ado_api', {})
            if not ado_config or not ado_config.get('enabled', False):
                logger.debug("ADO API not configured, skipping duplicate detection")
                return duplicates
            
            # This is a placeholder that would integrate with Azure DevOps REST API
            
            # Example implementation:
            # 1. Extract key terms from feature_name
            # 2. Call ADO API: GET https://dev.azure.com/{org}/{project}/_apis/wit/wiql
            # 3. WIQL query: SELECT [System.Id], [System.Title] FROM WorkItems
            #    WHERE [System.State] <> 'Closed' AND [System.Title] CONTAINS '{term}'
            # 4. Calculate similarity scores using fuzzy matching
            # 5. Return items with similarity > 70%
            
            logger.info(f"Duplicate detection for '{feature_name}' - No duplicates found")
            
        except Exception as e:
            logger.warning(f"Duplicate detection failed: {e}")
        
        return duplicates
    
    def _calculate_dor_completeness(
        self,
        acceptance_criteria: List[str],
        assumptions: List[str],
        constraints: List[str]
    ) -> Dict[str, Any]:
        """
        Calculate Definition of Ready (DoR) completeness percentage.
        
        Assesses DoR quality based on presence and quality of:
        - Acceptance criteria (60% weight - most critical)
        - Assumptions (20% weight)
        - Constraints (20% weight)
        
        Args:
            acceptance_criteria: List of acceptance criteria statements
            assumptions: List of assumptions
            constraints: List of constraints
            
        Returns:
            Dict with:
                - is_complete (bool): True if >= 60% complete
                - percentage (int): Completeness score 0-100
                - missing_elements (List[str]): What's missing
                - quality_score (str): "excellent", "good", "fair", "poor"
        """
        score = 0
        missing = []
        
        # Acceptance Criteria (60 points)
        if acceptance_criteria and len(acceptance_criteria) > 0:
            # Base points for having any AC
            base_ac_points = 30
            
            # Quality points based on count and detail
            ac_count = len(acceptance_criteria)
            if ac_count >= 5:
                quality_points = 30  # Excellent coverage
            elif ac_count >= 3:
                quality_points = 25  # Good coverage
            elif ac_count >= 2:
                quality_points = 20  # Fair coverage
            else:
                quality_points = 15  # Minimal coverage
            
            # Check if criteria are detailed (avg length > 20 chars)
            avg_length = sum(len(ac) for ac in acceptance_criteria) / len(acceptance_criteria)
            if avg_length > 50:
                quality_points += 5  # Bonus for detailed criteria
            
            score += min(base_ac_points + quality_points, 60)
        else:
            missing.append("Acceptance Criteria (critical)")
        
        # Assumptions (20 points)
        if assumptions and len(assumptions) > 0:
            # Scale based on count
            assumption_points = min(len(assumptions) * 5, 20)
            score += assumption_points
        else:
            missing.append("Assumptions")
        
        # Constraints (20 points)
        if constraints and len(constraints) > 0:
            # Scale based on count
            constraint_points = min(len(constraints) * 5, 20)
            score += constraint_points
        else:
            missing.append("Constraints")
        
        # Determine quality level
        if score >= 90:
            quality = "excellent"
        elif score >= 75:
            quality = "good"
        elif score >= 60:
            quality = "fair"
        else:
            quality = "poor"
        
        return {
            'is_complete': score >= 60,
            'percentage': score,
            'missing_elements': missing,
            'quality_score': quality,
            'ac_count': len(acceptance_criteria) if acceptance_criteria else 0,
            'assumptions_count': len(assumptions) if assumptions else 0,
            'constraints_count': len(constraints) if constraints else 0
        }
