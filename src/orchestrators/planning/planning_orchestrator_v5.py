"""
Planning Orchestrator v5 - Pure Autonomous Planning System.

First orchestrator built on BaseOrchestrator v4.1 with complete Master Orchestrator
integration. Generates structured plans with folder hierarchy, context discovery,
and database state tracking.

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
        config_path: str,
        state_db: Optional[PlanningStateDB] = None,
        plan_id: Optional[str] = None,
        template_dir: Optional[str] = None
    ):
        """Initialize Planning Orchestrator v5."""
        # Initialize database if not provided
        if state_db is None:
            db_path = "cortex-brain/database/planning_state.db"
            state_db = PlanningStateDB(db_path=db_path)
        
        super().__init__(config_path, state_db, plan_id, template_dir)
        
        # Initialize governance and knowledge graph integrations (Phase 4 enhancement)
        self.governance = GovernanceIntegrator()
        self.knowledge_graph = KnowledgeGraphQuery()
        
        self.logger.info("PlanningOrchestratorV5 initialized with governance + knowledge graph")
    
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
            # Phase 0: Parse request and create plan
            feature_name = self._extract_feature_name(user_request)
            plan_data = self._create_plan_metadata(feature_name, user_request)
            
            # Create plan in database
            self.plan_id = self.state_db.create_plan(
                feature_name=feature_name,
                metadata=plan_data
            )
            
            self.logger.info(f"Created plan: {self.plan_id}")
            
            # Phase -1: Knowledge Library (Governance Consultation)
            # Execute BEFORE Phase 0 to consult Tier 0/2 governance
            governance_result = self.execute_phase(
                -1,
                {'name': 'Knowledge Library', 'description': 'Consult governance and knowledge graph'},
                feature_name=feature_name,
                user_request=user_request
            )
            
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
            context_result = self.execute_phase(
                0,
                {'name': 'Context Discovery', 'description': 'Search workspace'},
                feature_name=feature_name,
                governance_context=governance_result
            )
            
            # Phase 2: Architecture Analysis
            analysis_result = self.execute_phase(
                1,
                {'name': 'Architecture Analysis', 'description': 'Parse codebase'},
                feature_name=feature_name,
                context=context_result
            )
            
            # Phase 3: Plan Generation
            generation_result = self.execute_phase(
                2,
                {'name': 'Plan Generation', 'description': 'Create plan document'},
                feature_name=feature_name,
                analysis=analysis_result
            )
            
            # Phase 4: Folder Structure Creation
            folder_result = self.execute_phase(
                3,
                {'name': 'Folder Creation', 'description': 'Create directory structure'},
                feature_name=feature_name
            )
            
            # Phase 5: Validation
            validation_result = self.execute_phase(
                4,
                {'name': 'Validation', 'description': 'Validate plan structure'},
                feature_name=feature_name
            )
            
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
            # Folder Creation
            return self._create_folder_structure(**kwargs)
        
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
    
    def _generate_master_plan_filename(self, feature_name: str) -> str:
        """
        Generate meaningful master plan filename.
        
        Args:
            feature_name: Full feature name (kebab-case)
        
        Returns:
            Master plan filename (00-{short-name}.md, <=25 chars total)
        
        Example:
            feature_name="glassmorphism-css-standardization"
            returns="00-glassmorphism.md" (17 chars)
        """
        # Extract meaningful short name (max 22 chars to fit "00-" prefix + ".md" suffix)
        max_name_length = 22 - 3 - 3  # 22 total - "00-" - ".md" = 16 chars
        
        # Split on hyphens and take meaningful parts
        parts = feature_name.split('-')
        
        # Strategy: Take first significant word + version/type suffix if exists
        short_name = parts[0]
        
        # Check for version/type indicators in remaining parts
        for part in parts[1:]:
            if part in ['v1', 'v2', 'v3', 'v4', 'v5', 'migration', 'refactor', 'system']:
                # Add significant suffix if it fits
                if len(short_name + '-' + part) <= max_name_length:
                    short_name = f"{short_name}-{part}"
                break
        
        # Truncate if still too long
        if len(short_name) > max_name_length:
            short_name = short_name[:max_name_length].rstrip('-')
        
        return f"00-{short_name}.md"
    
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
        return {
            'feature_name': feature_name,
            'user_request': user_request,
            'created_at': datetime.now().isoformat(),
            'orchestrator': 'planning_v5',
            'version': self.version,
            'complexity_tier': self._estimate_complexity(user_request),
            'estimated_days': 0,  # To be calculated during analysis
            'folder_path': f'cortex-brain/documents/planning/active/{feature_name}'
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
        
        plan_dir = Path(f"cortex-brain/documents/planning/active/{feature_name}")
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
        
        plan_dir = Path(f"cortex-brain/documents/planning/active/{feature_name}")
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
        
        plan_dir = Path(f"cortex-brain/documents/planning/active/{feature_name}")
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
    
    def _create_folder_structure(
        self,
        feature_name: str,
        **kwargs
    ) -> List[str]:
        """
        Create plan folder structure.
        
        Args:
            feature_name: Feature being planned
            **kwargs: Additional parameters
        
        Returns:
            List of folder paths created
        """
        self.logger.info("Creating folder structure...")
        
        plan_dir = Path(f"cortex-brain/documents/planning/active/{feature_name}")
        
        folders = [
            plan_dir / "context",
            plan_dir / "artifacts",
            plan_dir / "reports",
            plan_dir / "tracking"
        ]
        
        for folder in folders:
            folder.mkdir(parents=True, exist_ok=True)
            # Create .gitkeep
            (folder / ".gitkeep").touch()
        
        # Create progress tracker
        progress_content = {
            "plan_id": self.plan_id,
            "feature_name": feature_name,
            "created_at": datetime.now().isoformat(),
            "status": "active",
            "progress": {
                "overall_percent": 0,
                "current_phase": 1,
                "total_phases": 4
            }
        }
        
        import json
        tracker_path = plan_dir / "tracking" / "progress-tracker.json"
        tracker_path.write_text(json.dumps(progress_content, indent=2))
        
        return [str(f) for f in folders]
    
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
        Validate generated plan.
        
        Args:
            feature_name: Feature being planned
            **kwargs: Additional parameters
        
        Returns:
            List of validation report paths
        """
        self.logger.info("Validating plan...")
        
        plan_dir = Path(f"cortex-brain/documents/planning/active/{feature_name}")
        
        # Check required files
        required_files = [
            "00-master-plan.md",
            "README.md",
            "tracking/progress-tracker.json"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not (plan_dir / file_path).exists():
                missing_files.append(file_path)
        
        # Check required folders
        required_folders = ["context", "artifacts", "reports", "tracking"]
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

### Required Files
{self._format_file_list(required_files, missing_files)}

### Required Folders
{self._format_folder_list(required_folders, missing_folders)}

### Summary
- Total checks: {len(required_files) + len(required_folders)}
- Passed: {len(required_files) + len(required_folders) - len(missing_files) - len(missing_folders)}
- Failed: {len(missing_files) + len(missing_folders)}

{self._format_validation_issues(missing_files, missing_folders)}
"""
        
        report_path = plan_dir / "reports" / "validation-report.md"
        
        self.create_artifact(
            path=str(report_path),
            content=report_content,
            artifact_type="report"
        )
        
        if not validation_passed:
            raise ValueError(f"Plan validation failed: {len(missing_files + missing_folders)} issues found")
        
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

