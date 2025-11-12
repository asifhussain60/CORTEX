"""
ChangeGovernor Agent

Enforces governance rules and performs risk assessment for changes.
Checks compliance with CORTEX governance rules before executing
potentially risky operations.

The ChangeGovernor ensures all changes follow project governance
policies and architectural standards.
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
from src.cortex_agents.base_agent import BaseAgent, AgentRequest, AgentResponse
from src.cortex_agents.agent_types import IntentType, RiskLevel
from src.cortex_agents.utils import extract_file_paths


class ChangeGovernor(BaseAgent):
    """
    Enforces governance rules and assesses change risk.
    
    The ChangeGovernor validates proposed changes against governance
    rules (documented in governance/rules.md) and performs risk
    assessment to protect system integrity.
    
    Features:
    - Governance rule compliance checking
    - Risk level assessment (LOW, MEDIUM, HIGH, CRITICAL)
    - Multi-rule validation
    - Protected file detection
    - Test requirement validation
    - Change impact analysis
    
    Example:
        governor = ChangeGovernor(name="Governor", tier1_api, tier2_kg, tier3_context)
        
        request = AgentRequest(
            intent="check_governance",
            context={
                "files": ["src/core/database.py"],
                "operation": "delete"
            },
            user_message="Delete database module"
        )
        
        response = governor.execute(request)
        # Returns: {
        #   "allowed": False,
        #   "risk_level": "CRITICAL",
        #   "violations": ["Rule #3: Delete protected system file"],
        #   "requires_tests": True
        # }
    """
    
    def __init__(self, name: str, tier1_api, tier2_kg, tier3_context):
        """
        Initialize ChangeGovernor.
        
        Args:
            name: Agent name
            tier1_api: Tier 1 conversation manager API
            tier2_kg: Tier 2 knowledge graph API
            tier3_context: Tier 3 context intelligence API
        """
        super().__init__(name, tier1_api, tier2_kg, tier3_context)
        self.supported_intents = [
            "check_governance",
            "assess_risk",
            "validate_change"
        ]
        
        # Protected paths (Tier 0 - cannot be deleted/modified without high scrutiny)
        self.protected_paths = [
            "governance/rules.md",
            "CORTEX/src/tier0/",
            "CORTEX/src/tier1/",
            "CORTEX/src/tier2/",
            "CORTEX/src/tier3/",
            "CORTEX/src/cortex_agents/base_agent.py",
            "cortex-brain/",
        ]
    
    def can_handle(self, request: AgentRequest) -> bool:
        """
        Check if this agent can handle the request.
        
        Args:
            request: The agent request to evaluate
            
        Returns:
            True if intent is governance check, False otherwise
        """
        return request.intent in self.supported_intents
    
    def execute(self, request: AgentRequest) -> AgentResponse:
        """
        Check governance compliance and assess risk.
        
        Args:
            request: Agent request with change details in context
            
        Returns:
            AgentResponse with compliance check and risk assessment
        """
        start_time = datetime.now()
        
        try:
            # Extract change details
            files = self._get_files(request)
            operation = request.context.get("operation", "modify")
            
            # Perform governance checks
            violations = self._check_governance_rules(files, operation, request)
            
            # Assess risk level
            risk_level = self._assess_risk(files, operation, violations)
            
            # Check if tests are required
            requires_tests = self._requires_tests(files, operation)
            
            # Determine if change is allowed
            # Only block for CRITICAL violations (Rule #22, Rule #3)
            critical_violations = [
                v for v in violations
                if "Rule #22" in v or "Rule #3" in v
            ]
            allowed = len(critical_violations) == 0
            
            # Build response
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            return AgentResponse(
                success=True,
                result={
                    "allowed": allowed,
                    "risk_level": risk_level,
                    "violations": violations,
                    "requires_tests": requires_tests,
                    "files_affected": files,
                    "operation": operation
                },
                message=self._build_message(allowed, risk_level, violations),
                agent_name=self.name,
                duration_ms=duration_ms,
                next_actions=self._suggest_actions(allowed, risk_level, requires_tests)
            )
            
        except Exception as e:
            self.logger.error(f"Governance check failed: {e}", exc_info=True)
            return self._error_response(str(e), start_time)
    
    def _get_files(self, request: AgentRequest) -> List[str]:
        """
        Extract file list from request.
        
        Args:
            request: Agent request
            
        Returns:
            List of file paths
        """
        # Check context.files first
        files = request.context.get("files", [])
        if files:
            return files if isinstance(files, list) else [files]
        
        # Extract from user message
        files = extract_file_paths(request.user_message)
        return files
    
    def _check_governance_rules(
        self, 
        files: List[str], 
        operation: str, 
        request: AgentRequest
    ) -> List[str]:
        """
        Check compliance with governance rules.
        
        Args:
            files: List of files affected
            operation: Operation type (create, modify, delete)
            request: Original request for context
            
        Returns:
            List of rule violations
        """
        violations = []
        
        # Rule #3: Delete Over Archive
        if operation == "archive":
            violations.append("Rule #3: Use delete instead of archive")
        
        # Rule #20: Definition of DONE (requires tests)
        if operation in ["create", "modify"] and files:
            has_test_files = any("test_" in f or "_test" in f or "/tests/" in f for f in files)
            has_code_files = any(f.endswith(".py") and "test" not in f for f in files)
            
            # Only flag if there are code files but NO test files
            if has_code_files and not has_test_files:
                violations.append("Rule #20: Code changes require corresponding tests (TDD)")
        
        # Rule #22: Brain Protection (protect tier databases and brain files)
        protected_violations = self._check_protected_files(files, operation)
        violations.extend(protected_violations)
        
        # Rule #23: Incremental File Creation
        if operation == "create" and request.context.get("file_size_estimate", 0) > 100:
            estimated_lines = request.context.get("file_size_estimate", 0)
            if estimated_lines > 150:
                violations.append(
                    f"Rule #23: Large file ({estimated_lines} lines) must be created incrementally (max 150 lines/chunk)"
                )
        
        return violations
    
    def _check_protected_files(self, files: List[str], operation: str) -> List[str]:
        """
        Check if any protected files are being modified/deleted.
        
        Args:
            files: List of files
            operation: Operation type
            
        Returns:
            List of protection violations
        """
        violations = []
        
        for file in files:
            for protected_path in self.protected_paths:
                if protected_path in file:
                    if operation == "delete":
                        violations.append(
                            f"Rule #22: Cannot delete protected file: {file}"
                        )
                    elif operation == "modify":
                        # Modifications allowed but flagged as high risk
                        self.logger.warning(f"Modifying protected file: {file}")
        
        return violations
    
    def _assess_risk(
        self, 
        files: List[str], 
        operation: str, 
        violations: List[str]
    ) -> str:
        """
        Assess risk level of proposed change.
        
        Args:
            files: Files affected
            operation: Operation type
            violations: Governance violations
            
        Returns:
            Risk level (LOW, MEDIUM, HIGH, CRITICAL)
        """
        # CRITICAL: Serious governance violations (not including TDD warnings)
        critical_violations = [
            v for v in violations
            if "Rule #22" in v or "Rule #3" in v  # Brain protection, archive forbidden
        ]
        if len(critical_violations) > 0:
            return RiskLevel.CRITICAL.value
        
        # HIGH: Deleting files or modifying protected paths
        if operation == "delete":
            return RiskLevel.HIGH.value
        
        is_protected = any(
            any(protected in f for protected in self.protected_paths)
            for f in files
        )
        if is_protected:
            return RiskLevel.HIGH.value
        
        # MEDIUM: Multiple files affected or TDD violations
        if len(files) > 5:
            return RiskLevel.MEDIUM.value
        
        # TDD violations are important but not CRITICAL
        # (They're more like "required process" than "dangerous operation")
        tdd_violations = [v for v in violations if "Rule #20" in v or "Rule #23" in v]
        if len(tdd_violations) > 0 and len(violations) == len(tdd_violations):
            # Only TDD/incremental violations, not CRITICAL
            return RiskLevel.MEDIUM.value if len(files) > 1 else RiskLevel.LOW.value
        
        # LOW: Simple modifications
        return RiskLevel.LOW.value
    
    def _requires_tests(self, files: List[str], operation: str) -> bool:
        """
        Determine if tests are required for this change.
        
        Args:
            files: Files affected
            operation: Operation type
            
        Returns:
            True if tests required
        """
        # Tests required for code creation/modification
        if operation in ["create", "modify"]:
            has_code = any(
                f.endswith(".py") and "test" not in f
                for f in files
            )
            return has_code
        
        return False
    
    def _build_message(
        self, 
        allowed: bool, 
        risk_level: str, 
        violations: List[str]
    ) -> str:
        """
        Build human-readable message.
        
        Args:
            allowed: Whether change is allowed
            risk_level: Risk level
            violations: List of violations
            
        Returns:
            Message string
        """
        if not allowed:
            return f"Change BLOCKED: {len(violations)} governance violations found"
        
        if len(violations) > 0:
            return f"Change allowed with {len(violations)} warnings (Risk: {risk_level})"
        
        return f"Change approved (Risk: {risk_level})"
    
    def _suggest_actions(
        self, 
        allowed: bool, 
        risk_level: str, 
        requires_tests: bool
    ) -> List[str]:
        """
        Suggest next actions based on assessment.
        
        Args:
            allowed: Whether change is allowed
            risk_level: Risk level
            requires_tests: Whether tests are required
            
        Returns:
            List of suggested actions
        """
        actions = []
        
        if not allowed:
            actions.append("Fix governance violations before proceeding")
            actions.append("Review governance/rules.md for requirements")
            return actions
        
        if requires_tests:
            actions.append("Write tests before implementing changes (TDD)")
        
        if risk_level in [RiskLevel.HIGH.value, RiskLevel.CRITICAL.value]:
            actions.append("Create checkpoint before proceeding (Rule #19)")
            actions.append("Validate with HealthValidator after changes")
        
        actions.append("Proceed with change")
        
        return actions
    
    def _error_response(self, error_msg: str, start_time: datetime) -> AgentResponse:
        """
        Create error response.
        
        Args:
            error_msg: Error message
            start_time: Request start time
            
        Returns:
            AgentResponse with error details
        """
        duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        return AgentResponse(
            success=False,
            result={
                "allowed": False,
                "risk_level": RiskLevel.CRITICAL.value,
                "violations": [f"Governance check error: {error_msg}"]
            },
            message=f"Governance check failed: {error_msg}",
            agent_name=self.name,
            duration_ms=duration_ms,
            metadata={"error": error_msg}
        )
