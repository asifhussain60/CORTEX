"""
Orchestrator Scaffolder - Team Extensibility for Custom Domain Orchestrators

Enables domain teams to create custom orchestrators that leverage CORTEX 
governance intelligence. ALL scaffolded orchestrators route through 
MasterOrchestrator - this is NEVER bypassed.

CRITICAL DESIGN PRINCIPLE:
- MasterOrchestrator is IN CHARGE
- Scaffolded orchestrators register with MasterOrchestrator on initialization
- Orchestrators receive requests ONLY through MasterOrchestrator routing
- Cannot execute independently without registration

AC-IDs: AC-SCAFFOLD-001 through AC-SCAFFOLD-007

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import os
import sys
import json
import yaml
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("cortex.scaffolder")


@dataclass
class OrchestratorSpec:
    """Specification for a new orchestrator."""
    name: str
    domain: str
    category: str
    description: str
    owner: str
    team: str = ""
    version: str = "1.0.0"
    routing_patterns: List[str] = field(default_factory=list)
    integrations: List[str] = field(default_factory=list)
    tier3_patterns: Dict[str, Any] = field(default_factory=dict)


class OrchestratorScaffolder:
    """
    Scaffolder for creating domain-specific orchestrators.
    
    CRITICAL: All generated orchestrators MUST:
    1. Extend BaseOrchestratorV4
    2. Register with MasterOrchestrator via @register_with_master
    3. Include manifest that follows manifest-schema.yaml
    4. Have 4-tier governance hooks injected
    
    MasterOrchestrator is IN CHARGE - this is NEVER bypassed.
    """
    
    def __init__(self, workspace_root: Optional[Path] = None):
        """Initialize scaffolder with workspace root."""
        self.workspace_root = workspace_root or Path.cwd()
        self.templates_dir = self.workspace_root / "src" / "tools" / "scaffolder_templates"
        self.manifests_dir = self.workspace_root / "cortex-brain" / "manifests" / "orchestrators"
        self.orchestrators_dir = self.workspace_root / "src" / "orchestrators"
        self.tier3_dir = self.workspace_root / "cortex-brain" / "tier3" / "domains"
        self.tests_dir = self.workspace_root / "tests" / "orchestrators"
        
        # Load manifest schema for validation
        self.manifest_schema_path = self.manifests_dir / "manifest-schema.yaml"
        
    def scaffold(self, spec: OrchestratorSpec) -> Dict[str, Any]:
        """
        Scaffold a new orchestrator from specification.
        
        CRITICAL: Generated orchestrator MUST register with MasterOrchestrator.
        This ensures MasterOrchestrator remains IN CHARGE of all operations.
        
        Args:
            spec: OrchestratorSpec with orchestrator details
            
        Returns:
            Dict with created file paths and status
        """
        logger.info(f"\n🚀 Scaffolding orchestrator: {spec.name}")
        logger.info(f"   Domain: {spec.domain}")
        logger.info(f"   Category: {spec.category}")
        
        created_files = []
        
        # 1. Create orchestrator directory
        orch_dir = self._create_orchestrator_directory(spec)
        created_files.append(str(orch_dir))
        
        # 2. Generate orchestrator Python class (AC-SCAFFOLD-001)
        orch_file = self._generate_orchestrator_class(spec, orch_dir)
        created_files.append(str(orch_file))
        
        # 3. Generate manifest YAML (AC-SCAFFOLD-005)
        manifest_file = self._generate_manifest(spec)
        created_files.append(str(manifest_file))
        
        # 4. Generate domain tier3 knowledge (AC-SCAFFOLD-004)
        tier3_file = self._generate_tier3_domain(spec)
        created_files.append(str(tier3_file))
        
        # 5. Generate test stubs
        test_file = self._generate_tests(spec)
        created_files.append(str(test_file))
        
        # 6. Update orchestrator relationship graph (AC-SCAFFOLD-006)
        self._update_relationship_graph(spec)
        
        # 7. Generate registration snippet (AC-SCAFFOLD-003)
        registration_info = self._generate_registration_info(spec)
        
        return {
            "success": True,
            "orchestrator_name": spec.name,
            "domain": spec.domain,
            "created_files": created_files,
            "registration": registration_info,
            "next_steps": self._get_next_steps(spec)
        }
    
    def _create_orchestrator_directory(self, spec: OrchestratorSpec) -> Path:
        """Create orchestrator directory structure."""
        # Sanitize name for directory
        dir_name = spec.name.lower().replace(" ", "_").replace("-", "_")
        orch_dir = self.orchestrators_dir / dir_name
        orch_dir.mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py
        init_file = orch_dir / "__init__.py"
        init_content = f'''"""
{spec.name} - {spec.description}

Domain: {spec.domain}
Owner: {spec.owner}
Team: {spec.team}

CRITICAL: This orchestrator routes through MasterOrchestrator.
MasterOrchestrator is IN CHARGE - direct execution is not permitted.

Author: {spec.owner}
Copyright © 2025-2026. All rights reserved.
"""

from .{dir_name}_orchestrator import {self._class_name(spec.name)}

__all__ = ["{self._class_name(spec.name)}"]
'''
        init_file.write_text(init_content, encoding="utf-8")
        
        return orch_dir
    
    def _generate_orchestrator_class(self, spec: OrchestratorSpec, orch_dir: Path) -> Path:
        """
        Generate orchestrator Python class.
        
        AC-SCAFFOLD-001: CLI generates complete orchestrator structure
        AC-SCAFFOLD-002: 4-tier governance hooks injected
        AC-SCAFFOLD-003: MasterOrchestrator registration included
        """
        dir_name = spec.name.lower().replace(" ", "_").replace("-", "_")
        class_name = self._class_name(spec.name)
        
        # Generate routing patterns
        patterns = spec.routing_patterns or [spec.domain.lower(), spec.name.lower()]
        patterns_str = ", ".join([f'"{p}"' for p in patterns])
        
        content = f'''"""
{spec.name} Orchestrator - {spec.description}

Domain: {spec.domain}
Category: {spec.category}
Version: {spec.version}

CRITICAL DESIGN:
- This orchestrator is registered with MasterOrchestrator
- MasterOrchestrator is IN CHARGE - all requests route through it
- Direct execution without MasterOrchestrator is BLOCKED
- 4-tier governance is automatically applied

Generated by: CORTEX Orchestrator Scaffolder
Generated on: {datetime.now().isoformat()}

Owner: {spec.owner}
Team: {spec.team}

Copyright © 2025-2026. All rights reserved.
"""

import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

from src.orchestrators.base.base_orchestrator_v4 import (
    BaseOrchestratorV4,
    PhaseResult,
    PhaseStatus
)
from src.orchestrators.base.base_orchestrator import (
    OrchestratorResult,
    OrchestratorStatus
)

# CRITICAL: Import registration decorator
# This ensures MasterOrchestrator is IN CHARGE
from src.orchestrators.core.master_registration import (
    register_with_master,
    require_master_routing
)


@register_with_master(
    name="{spec.name}",
    domain="{spec.domain}",
    category="{spec.category}",
    routing_patterns=[{patterns_str}],
    version="{spec.version}"
)
class {class_name}(BaseOrchestratorV4):
    """
    {spec.description}
    
    GOVERNANCE INTEGRATION:
    - Tier 0 (SKULL): Core protection rules enforced via middleware
    - Tier 1 (Business): Company compliance from tier1/ loaded at init
    - Tier 2 (Engineering): Standards from tier2/ applied to all code
    - Tier 3 (Domain): {spec.domain}-specific patterns from tier3/domains/
    
    MASTER ORCHESTRATOR CONTROL:
    - Registered via @register_with_master decorator
    - Requests ONLY come through MasterOrchestrator routing
    - Results return TO MasterOrchestrator for audit/state
    - Direct execution raises MasterBypassError
    """
    
    # Domain configuration
    DOMAIN = "{spec.domain}"
    CATEGORY = "{spec.category}"
    VERSION = "{spec.version}"
    OWNER = "{spec.owner}"
    TEAM = "{spec.team or 'unassigned'}"
    
    # Routing patterns (MasterOrchestrator uses these)
    ROUTING_PATTERNS = [{patterns_str}]
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize {spec.name} orchestrator.
        
        CRITICAL: Do not instantiate directly. Use MasterOrchestrator routing.
        """
        # Default config path
        if config_path is None:
            config_path = str(
                Path(__file__).parent.parent.parent.parent / 
                "cortex-brain" / "manifests" / "orchestrators" / 
                "{dir_name}-manifest.yaml"
            )
        
        super().__init__(config_path)
        
        self.logger = logging.getLogger(f"cortex.orchestrators.{spec.domain.lower()}.{dir_name}")
        
        # Load domain-specific tier3 knowledge
        self._load_domain_knowledge()
        
        # Define phases
        self.phases = [
            "discovery",
            "planning", 
            "execution",
            "validation"
        ]
        
    def _load_domain_knowledge(self) -> None:
        """
        Load domain-specific tier3 patterns.
        
        AC-SCAFFOLD-004: Domain knowledge integration
        """
        tier3_path = (
            Path(__file__).parent.parent.parent.parent /
            "cortex-brain" / "tier3" / "domains" /
            f"{self.DOMAIN.lower()}-patterns.yaml"
        )
        
        self.domain_patterns = {{}}
        if tier3_path.exists():
            import yaml
            with open(tier3_path, "r", encoding="utf-8") as f:
                self.domain_patterns = yaml.safe_load(f) or {{}}
            self.logger.debug(f"Loaded domain patterns from {{tier3_path}}")
    
    @require_master_routing
    def execute(self, context: Dict[str, Any]) -> OrchestratorResult:
        """
        Execute the orchestrator.
        
        CRITICAL: This method is decorated with @require_master_routing.
        Direct calls without MasterOrchestrator context will raise MasterBypassError.
        
        Args:
            context: Execution context from MasterOrchestrator containing:
                - request: Original user request
                - correlation_id: Audit trail ID
                - governance_rules: Merged 4-tier rules
                - todo_id: Associated todo from TodoManager
                
        Returns:
            OrchestratorResult with execution status
        """
        # Validate context comes from MasterOrchestrator
        if "_master_routed" not in context:
            from src.orchestrators.core.master_registration import MasterBypassError
            raise MasterBypassError(
                f"{{self.__class__.__name__}} must be invoked through MasterOrchestrator. "
                "Direct execution is not permitted."
            )
        
        self.logger.info(f"Executing {{self.__class__.__name__}}")
        self.logger.info(f"Correlation ID: {{context.get('correlation_id', 'N/A')}}")
        
        try:
            results = []
            
            for phase in self.phases:
                self.current_phase = phase
                phase_result = self.execute_phase(phase, context)
                results.append(phase_result)
                
                if phase_result.status == PhaseStatus.FAILED:
                    return OrchestratorResult(
                        success=False,
                        status=OrchestratorStatus.FAILURE,
                        message=f"Phase {{phase}} failed: {{phase_result.message}}",
                        data={{"phase_results": [r.__dict__ for r in results]}}
                    )
            
            return OrchestratorResult(
                success=True,
                status=OrchestratorStatus.SUCCESS,
                message=f"{{self.__class__.__name__}} completed successfully",
                data={{
                    "phase_results": [r.__dict__ for r in results],
                    "domain": self.DOMAIN,
                    "correlation_id": context.get("correlation_id")
                }}
            )
            
        except Exception as e:
            self.logger.error(f"Execution failed: {{e}}")
            return OrchestratorResult(
                success=False,
                status=OrchestratorStatus.FAILURE,
                message=str(e),
                data={{"error": str(e)}}
            )
    
    def execute_phase(self, phase_id: str, context: Dict[str, Any]) -> PhaseResult:
        """
        Execute a single phase.
        
        Override this method to implement domain-specific logic.
        
        Args:
            phase_id: Phase identifier
            context: Execution context
            
        Returns:
            PhaseResult with phase status
        """
        phase_handlers = {{
            "discovery": self._phase_discovery,
            "planning": self._phase_planning,
            "execution": self._phase_execution,
            "validation": self._phase_validation
        }}
        
        handler = phase_handlers.get(phase_id, self._phase_default)
        return handler(context)
    
    def _phase_discovery(self, context: Dict[str, Any]) -> PhaseResult:
        """
        Discovery phase - analyze request and gather context.
        
        TODO: Implement domain-specific discovery logic.
        """
        self.logger.info("Phase: Discovery")
        
        return PhaseResult(
            phase_id="discovery",
            status=PhaseStatus.COMPLETE,
            message="Discovery phase completed",
            data={{"discovered": True}}
        )
    
    def _phase_planning(self, context: Dict[str, Any]) -> PhaseResult:
        """
        Planning phase - create execution plan.
        
        TODO: Implement domain-specific planning logic.
        """
        self.logger.info("Phase: Planning")
        
        return PhaseResult(
            phase_id="planning",
            status=PhaseStatus.COMPLETE,
            message="Planning phase completed",
            data={{"plan_created": True}}
        )
    
    def _phase_execution(self, context: Dict[str, Any]) -> PhaseResult:
        """
        Execution phase - perform the main work.
        
        TODO: Implement domain-specific execution logic.
        """
        self.logger.info("Phase: Execution")
        
        return PhaseResult(
            phase_id="execution",
            status=PhaseStatus.COMPLETE,
            message="Execution phase completed",
            data={{"executed": True}}
        )
    
    def _phase_validation(self, context: Dict[str, Any]) -> PhaseResult:
        """
        Validation phase - verify results.
        
        TODO: Implement domain-specific validation logic.
        """
        self.logger.info("Phase: Validation")
        
        return PhaseResult(
            phase_id="validation",
            status=PhaseStatus.COMPLETE,
            message="Validation phase completed",
            data={{"validated": True}}
        )
    
    def _phase_default(self, context: Dict[str, Any]) -> PhaseResult:
        """Default handler for unknown phases."""
        return PhaseResult(
            phase_id="unknown",
            status=PhaseStatus.SKIPPED,
            message="Unknown phase skipped",
            data={{}}
        )
'''
        
        file_path = orch_dir / f"{dir_name}_orchestrator.py"
        file_path.write_text(content, encoding="utf-8")
        
        return file_path
    
    def _generate_manifest(self, spec: OrchestratorSpec) -> Path:
        """
        Generate orchestrator manifest YAML.
        
        AC-SCAFFOLD-005: Manifest contract validation
        """
        dir_name = spec.name.lower().replace(" ", "_").replace("-", "_")
        
        # Generate routing patterns
        patterns = spec.routing_patterns or [spec.domain.lower(), spec.name.lower()]
        
        manifest = {
            "schema_version": "1.0",
            "metadata": {
                "orchestrator_name": spec.name,
                "version": spec.version,
                "description": spec.description,
                "category": spec.category,
                "domain": spec.domain,
                "deployment_tier": "user",
                "status": "draft",
                "last_updated": datetime.now().strftime("%Y-%m-%d"),
                "maintainer": spec.owner,
                "team": spec.team,
                "related_orchestrators": [],
                "documentation_path": f"docs/orchestrators/{dir_name}.md"
            },
            "master_orchestrator_integration": {
                "critical": True,
                "description": "MasterOrchestrator is IN CHARGE - this orchestrator MUST be routed through it",
                "registration": {
                    "decorator": "@register_with_master",
                    "routing_patterns": patterns,
                    "bypass_protection": "@require_master_routing"
                },
                "enforcement": "MANDATORY - orchestrator will not function without MasterOrchestrator routing"
            },
            "requirements": [
                {
                    "requirement_id": "REQ-001",
                    "name": "MasterOrchestrator Registration",
                    "description": "Orchestrator must register with MasterOrchestrator on initialization",
                    "priority": "critical",
                    "status": "implemented",
                    "validation_method": "decorator_check",
                    "validation_criteria": "@register_with_master decorator present"
                },
                {
                    "requirement_id": "REQ-002",
                    "name": "Master Routing Enforcement",
                    "description": "Execute method must require MasterOrchestrator routing",
                    "priority": "critical",
                    "status": "implemented",
                    "validation_method": "decorator_check",
                    "validation_criteria": "@require_master_routing decorator on execute()"
                },
                {
                    "requirement_id": "REQ-003",
                    "name": "4-Tier Governance Compliance",
                    "description": "Orchestrator must respect 4-tier governance rules",
                    "priority": "high",
                    "status": "implemented",
                    "validation_method": "runtime_check",
                    "validation_criteria": "Governance rules loaded from context"
                },
                {
                    "requirement_id": "REQ-004",
                    "name": "Domain Knowledge Loading",
                    "description": "Load tier3 domain patterns on initialization",
                    "priority": "medium",
                    "status": "implemented",
                    "validation_method": "method_exists",
                    "validation_criteria": "_load_domain_knowledge() method present"
                }
            ],
            "integrations": [
                {
                    "integration_id": "INT-001",
                    "target_component": "MasterOrchestrator",
                    "integration_type": "required",
                    "trigger_condition": "always",
                    "expected_behavior": "Receive all requests through MasterOrchestrator routing",
                    "validation_method": "runtime_check"
                },
                {
                    "integration_id": "INT-002",
                    "target_component": "GovernanceMerger",
                    "integration_type": "required",
                    "trigger_condition": "on_request",
                    "expected_behavior": "Receive merged governance rules in context",
                    "validation_method": "context_check"
                },
                {
                    "integration_id": "INT-003",
                    "target_component": "TodoManager",
                    "integration_type": "required",
                    "trigger_condition": "on_execution",
                    "expected_behavior": "Todo created and tracked for orchestrator execution",
                    "validation_method": "todo_exists"
                },
                {
                    "integration_id": "INT-004",
                    "target_component": "EnterpriseAuditLogger",
                    "integration_type": "required",
                    "trigger_condition": "on_complete",
                    "expected_behavior": "Execution results logged with correlation_id",
                    "validation_method": "audit_entry_check"
                }
            ],
            "quality_gates": [
                {
                    "gate_id": "GATE-001",
                    "name": "Master Registration Validation",
                    "gate_type": "validation",
                    "trigger_point": "initialization",
                    "blocking": True,
                    "validation_criteria": "Orchestrator registered with MasterOrchestrator",
                    "bypass_conditions": []
                },
                {
                    "gate_id": "GATE-002",
                    "name": "Governance Compliance",
                    "gate_type": "compliance",
                    "trigger_point": "before_execution",
                    "blocking": True,
                    "validation_criteria": "All SKULL rules satisfied",
                    "bypass_conditions": []
                }
            ],
            "workflows": [
                {
                    "workflow_id": "WF-001",
                    "name": "Standard Execution",
                    "phases": [
                        {"phase_id": "discovery", "name": "Discovery", "sequence": 1, "required": True},
                        {"phase_id": "planning", "name": "Planning", "sequence": 2, "required": True},
                        {"phase_id": "execution", "name": "Execution", "sequence": 3, "required": True},
                        {"phase_id": "validation", "name": "Validation", "sequence": 4, "required": True}
                    ]
                }
            ],
            "compliance_rules": [
                {"rule_id": "CORE-001", "enforcement_level": "mandatory", "validation_method": "incremental_check"},
                {"rule_id": "CORE-008", "enforcement_level": "mandatory", "validation_method": "tdd_check"},
                {"rule_id": "CORE-017", "enforcement_level": "mandatory", "validation_method": "governance_check"},
                {"rule_id": "CORE-019", "enforcement_level": "mandatory", "validation_method": "tdd_master_check"}
            ],
            "domain_specific": {
                "domain": spec.domain,
                "tier3_patterns_path": f"cortex-brain/tier3/domains/{spec.domain.lower()}-patterns.yaml",
                "custom_phases": [],
                "domain_constraints": []
            },
            "generated_by": {
                "tool": "CORTEX Orchestrator Scaffolder",
                "version": "1.0.0",
                "timestamp": datetime.now().isoformat(),
                "ac_ids": ["AC-SCAFFOLD-001", "AC-SCAFFOLD-005"]
            }
        }
        
        manifest_path = self.manifests_dir / f"{dir_name}-manifest.yaml"
        
        with open(manifest_path, "w", encoding="utf-8") as f:
            yaml.dump(manifest, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        
        return manifest_path
    
    def _generate_tier3_domain(self, spec: OrchestratorSpec) -> Path:
        """
        Generate domain-specific tier3 knowledge file.
        
        AC-SCAFFOLD-004: Domain knowledge integration
        """
        self.tier3_dir.mkdir(parents=True, exist_ok=True)
        
        domain_patterns = {
            "schema_version": "1.0",
            "domain": spec.domain,
            "description": f"Tier 3 knowledge patterns for {spec.domain} domain",
            "owner": spec.owner,
            "team": spec.team,
            "created": datetime.now().strftime("%Y-%m-%d"),
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "governance_tier": 3,
            "precedence": "LOW",
            "terminology": {
                "description": "Domain-specific terms and their meanings",
                "terms": {
                    "example_term": {
                        "definition": "Replace with domain-specific terminology",
                        "aliases": [],
                        "related_terms": []
                    }
                }
            },
            "patterns": {
                "description": "Learned patterns specific to this domain",
                "coding_patterns": [],
                "architecture_patterns": [],
                "integration_patterns": []
            },
            "constraints": {
                "description": "Domain-specific constraints and rules",
                "must_have": [],
                "must_not_have": [],
                "preferences": []
            },
            "context_keywords": {
                "description": "Keywords that help identify this domain in requests",
                "primary": [spec.domain.lower()],
                "secondary": spec.routing_patterns or []
            },
            "integrations": {
                "description": "Common integrations in this domain",
                "external_systems": [],
                "internal_components": []
            },
            "quality_standards": {
                "description": "Domain-specific quality requirements",
                "code_coverage_minimum": 80,
                "documentation_required": True,
                "review_required": True
            },
            "generated_by": {
                "tool": "CORTEX Orchestrator Scaffolder",
                "ac_id": "AC-SCAFFOLD-004",
                "timestamp": datetime.now().isoformat()
            }
        }
        
        # Merge any provided tier3 patterns
        if spec.tier3_patterns:
            domain_patterns.update(spec.tier3_patterns)
        
        tier3_path = self.tier3_dir / f"{spec.domain.lower()}-patterns.yaml"
        
        with open(tier3_path, "w", encoding="utf-8") as f:
            yaml.dump(domain_patterns, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        
        return tier3_path
    
    def _generate_tests(self, spec: OrchestratorSpec) -> Path:
        """Generate test stubs for the orchestrator."""
        dir_name = spec.name.lower().replace(" ", "_").replace("-", "_")
        class_name = self._class_name(spec.name)
        
        test_dir = self.tests_dir / dir_name
        test_dir.mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py
        (test_dir / "__init__.py").write_text("", encoding="utf-8")
        
        test_content = f'''"""
Tests for {spec.name} Orchestrator

AC-IDs: AC-SCAFFOLD-001 through AC-SCAFFOLD-007

These tests verify:
1. MasterOrchestrator registration (CRITICAL)
2. Master routing enforcement (CRITICAL)
3. 4-tier governance compliance
4. Domain knowledge loading
5. Phase execution

Author: {spec.owner}
Copyright © 2025-2026. All rights reserved.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from src.orchestrators.{dir_name}.{dir_name}_orchestrator import {class_name}
from src.orchestrators.base.base_orchestrator import OrchestratorStatus


class Test{class_name}Registration:
    """
    Test MasterOrchestrator registration.
    
    CRITICAL: These tests verify the orchestrator cannot bypass MasterOrchestrator.
    """
    
    def test_has_register_with_master_decorator(self):
        """Verify @register_with_master decorator is present."""
        # Check class has registration metadata
        assert hasattr({class_name}, "_master_registration")
        
    def test_registration_includes_domain(self):
        """Verify registration includes domain information."""
        registration = getattr({class_name}, "_master_registration", {{}})
        assert registration.get("domain") == "{spec.domain}"
        
    def test_registration_includes_routing_patterns(self):
        """Verify registration includes routing patterns."""
        registration = getattr({class_name}, "_master_registration", {{}})
        assert "routing_patterns" in registration
        assert len(registration["routing_patterns"]) > 0


class Test{class_name}MasterRouting:
    """
    Test master routing enforcement.
    
    CRITICAL: Direct execution without MasterOrchestrator must fail.
    """
    
    def test_direct_execution_raises_error(self):
        """Verify direct execution without master routing fails."""
        orchestrator = {class_name}()
        
        # Context without _master_routed flag should raise
        with pytest.raises(Exception) as exc_info:
            orchestrator.execute({{"request": "test"}})
        
        assert "MasterOrchestrator" in str(exc_info.value)
        
    def test_master_routed_execution_succeeds(self):
        """Verify execution with master routing succeeds."""
        orchestrator = {class_name}()
        
        # Context with _master_routed flag should work
        result = orchestrator.execute({{
            "request": "test",
            "_master_routed": True,
            "correlation_id": "test-123"
        }})
        
        assert result.success is True
        assert result.status == OrchestratorStatus.SUCCESS


class Test{class_name}Governance:
    """Test 4-tier governance integration."""
    
    def test_loads_domain_knowledge(self):
        """Verify domain tier3 patterns are loaded."""
        orchestrator = {class_name}()
        
        # Should have domain_patterns attribute
        assert hasattr(orchestrator, "domain_patterns")
        
    def test_domain_attribute_set(self):
        """Verify domain is correctly set."""
        assert {class_name}.DOMAIN == "{spec.domain}"
        
    def test_category_attribute_set(self):
        """Verify category is correctly set."""
        assert {class_name}.CATEGORY == "{spec.category}"


class Test{class_name}Phases:
    """Test phase execution."""
    
    def test_has_required_phases(self):
        """Verify all required phases are defined."""
        orchestrator = {class_name}()
        
        required_phases = ["discovery", "planning", "execution", "validation"]
        for phase in required_phases:
            assert phase in orchestrator.phases
            
    def test_phase_execution_order(self):
        """Verify phases execute in correct order."""
        orchestrator = {class_name}()
        
        context = {{
            "request": "test",
            "_master_routed": True,
            "correlation_id": "test-123"
        }}
        
        result = orchestrator.execute(context)
        
        # Should have results for all phases
        phase_results = result.data.get("phase_results", [])
        assert len(phase_results) == 4
'''
        
        test_file = test_dir / f"test_{dir_name}_orchestrator.py"
        test_file.write_text(test_content, encoding="utf-8")
        
        return test_file
    
    def _update_relationship_graph(self, spec: OrchestratorSpec) -> None:
        """
        Update orchestrator relationship graph.
        
        AC-SCAFFOLD-006: Orchestrator relationship graph
        """
        graph_path = self.workspace_root / "cortex-brain" / "tier1" / "orchestrator-graph.yaml"
        
        # Load existing graph or create new
        graph = {"orchestrators": {}, "relationships": []}
        if graph_path.exists():
            with open(graph_path, "r", encoding="utf-8") as f:
                graph = yaml.safe_load(f) or graph
        
        dir_name = spec.name.lower().replace(" ", "_").replace("-", "_")
        
        # Add orchestrator node
        graph["orchestrators"][dir_name] = {
            "name": spec.name,
            "domain": spec.domain,
            "category": spec.category,
            "owner": spec.owner,
            "team": spec.team,
            "routing_patterns": spec.routing_patterns or [spec.domain.lower()],
            "created": datetime.now().strftime("%Y-%m-%d")
        }
        
        # Add mandatory MasterOrchestrator relationship
        graph["relationships"].append({
            "from": "master_orchestrator",
            "to": dir_name,
            "type": "routes_to",
            "mandatory": True,
            "description": "MasterOrchestrator routes requests to this orchestrator"
        })
        
        # Add integration relationships
        for integration in spec.integrations:
            graph["relationships"].append({
                "from": dir_name,
                "to": integration.lower().replace(" ", "_"),
                "type": "integrates_with",
                "mandatory": False
            })
        
        # Save graph
        graph_path.parent.mkdir(parents=True, exist_ok=True)
        with open(graph_path, "w", encoding="utf-8") as f:
            yaml.dump(graph, f, default_flow_style=False, sort_keys=False)
    
    def _generate_registration_info(self, spec: OrchestratorSpec) -> Dict[str, Any]:
        """Generate registration information for MasterOrchestrator."""
        dir_name = spec.name.lower().replace(" ", "_").replace("-", "_")
        patterns = spec.routing_patterns or [spec.domain.lower(), spec.name.lower()]
        
        return {
            "module": f"src.orchestrators.{dir_name}",
            "class": self._class_name(spec.name),
            "routing_patterns": patterns,
            "registration_code": f'''
# Add to MasterOrchestrator routing table
from src.orchestrators.{dir_name} import {self._class_name(spec.name)}

# The @register_with_master decorator automatically registers on import.
# Ensure the module is imported in src/orchestrators/__init__.py:
# from .{dir_name} import {self._class_name(spec.name)}
'''
        }
    
    def _get_next_steps(self, spec: OrchestratorSpec) -> List[str]:
        """Get next steps for the user."""
        dir_name = spec.name.lower().replace(" ", "_").replace("-", "_")
        class_name = self._class_name(spec.name)
        
        return [
            f"1. Review generated orchestrator: src/orchestrators/{dir_name}/",
            f"2. Customize domain logic in {dir_name}_orchestrator.py",
            f"3. Update tier3 domain patterns: cortex-brain/tier3/domains/{spec.domain.lower()}-patterns.yaml",
            f"4. Add routing import to src/orchestrators/__init__.py: from .{dir_name} import {class_name}",
            f"5. Run tests: pytest tests/orchestrators/{dir_name}/ -v",
            "6. CRITICAL: Verify MasterOrchestrator registration is working"
        ]
    
    def _class_name(self, name: str) -> str:
        """Convert name to PascalCase class name."""
        words = name.replace("-", " ").replace("_", " ").split()
        return "".join(word.capitalize() for word in words) + "Orchestrator"
    
    def validate_manifest(self, manifest_path: Path) -> Dict[str, Any]:
        """
        Validate manifest against schema.
        
        AC-SCAFFOLD-005: Manifest contract validation
        """
        issues = []
        
        if not manifest_path.exists():
            return {"valid": False, "issues": ["Manifest file not found"]}
        
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = yaml.safe_load(f)
        
        # Check required sections
        required_sections = ["metadata", "requirements", "integrations", "quality_gates", "compliance_rules"]
        for section in required_sections:
            if section not in manifest:
                issues.append(f"Missing required section: {section}")
        
        # Check MasterOrchestrator integration
        if "master_orchestrator_integration" not in manifest:
            issues.append("CRITICAL: Missing master_orchestrator_integration section")
        
        # Check critical requirements
        if "requirements" in manifest:
            has_master_reg = any(
                r.get("name") == "MasterOrchestrator Registration"
                for r in manifest["requirements"]
            )
            if not has_master_reg:
                issues.append("CRITICAL: Missing MasterOrchestrator Registration requirement")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues
        }


def cli_create_orchestrator():
    """CLI entry point for creating orchestrators."""
    parser = argparse.ArgumentParser(
        description="CORTEX Orchestrator Scaffolder - Create domain-specific orchestrators"
    )
    
    parser.add_argument("--name", "-n", required=True, help="Orchestrator name")
    parser.add_argument("--domain", "-d", required=True, help="Domain (e.g., 'finance', 'healthcare')")
    parser.add_argument("--category", "-c", default="execution", 
                       choices=["planning", "execution", "analysis", "deployment", "maintenance"],
                       help="Orchestrator category")
    parser.add_argument("--description", default="", help="Orchestrator description")
    parser.add_argument("--owner", "-o", required=True, help="Owner name/email")
    parser.add_argument("--team", "-t", default="", help="Team name")
    parser.add_argument("--patterns", "-p", nargs="*", default=[], help="Routing patterns")
    parser.add_argument("--workspace", "-w", default=".", help="Workspace root path")
    
    args = parser.parse_args()
    
    spec = OrchestratorSpec(
        name=args.name,
        domain=args.domain,
        category=args.category,
        description=args.description or f"{args.name} orchestrator for {args.domain} domain",
        owner=args.owner,
        team=args.team,
        routing_patterns=args.patterns
    )
    
    scaffolder = OrchestratorScaffolder(Path(args.workspace))
    result = scaffolder.scaffold(spec)
    
    if result["success"]:
        print("\n✅ Orchestrator scaffolded successfully!")
        print(f"\n📁 Created files:")
        for f in result["created_files"]:
            print(f"   - {f}")
        print(f"\n🔗 Registration info:")
        print(result["registration"]["registration_code"])
        print("\n📋 Next steps:")
        for step in result["next_steps"]:
            print(f"   {step}")
    else:
        print("\n❌ Scaffolding failed")
        sys.exit(1)


if __name__ == "__main__":
    cli_create_orchestrator()
