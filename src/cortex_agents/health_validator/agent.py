"""HealthValidator Agent - Coordinator."""

from typing import Dict, Any
from datetime import datetime
from ..base_agent import BaseAgent, AgentRequest, AgentResponse
from ..agent_types import IntentType

from .validators import (
    DatabaseValidator,
    TestValidator,
    GitValidator,
    DiskValidator,
    PerformanceValidator
)
from .reporting import ResultAnalyzer, ReportFormatter


class HealthValidator(BaseAgent):
    """
    Validates system health before risky operations.
    
    The HealthValidator performs comprehensive health checks including:
    - Database integrity verification
    - Test suite pass rate validation
    - Git repository status
    - Disk space availability
    - Performance metric thresholds
    
    Features:
    - Multi-tier database checks
    - Test execution and validation
    - Git status monitoring
    - Resource availability checks
    - Risk level assessment
    
    Example:
        validator = HealthValidator(name="Validator", tier1_api, tier2_kg, tier3_context)
        
        request = AgentRequest(
            intent="health_check",
            context={},
            user_message="Check if system is ready for deployment"
        )
        
        response = validator.execute(request)
    """
    
    def __init__(self, name: str, tier1_api=None, tier2_kg=None, tier3_context=None):
        """Initialize HealthValidator with tier APIs and validators."""
        super().__init__(name, tier1_api, tier2_kg, tier3_context)
        
        # Initialize validators
        self.db_validator = DatabaseValidator(tier1_api, tier2_kg, tier3_context)
        self.test_validator = TestValidator()
        self.git_validator = GitValidator()
        self.disk_validator = DiskValidator()
        self.perf_validator = PerformanceValidator(tier3_context)
        
        # Initialize reporting components
        self.analyzer = ResultAnalyzer()
        self.formatter = ReportFormatter()
    
    def can_handle(self, request: AgentRequest) -> bool:
        """
        Check if this agent can handle the request.
        
        Args:
            request: The agent request
        
        Returns:
            True if intent is health_check or validate
        """
        valid_intents = [
            IntentType.HEALTH_CHECK.value,
            IntentType.VALIDATE.value,
            "health",
            "check",
            "validate"
        ]
        return request.intent.lower() in valid_intents
    
    def execute(self, request: AgentRequest) -> AgentResponse:
        """
        Perform system health validation.
        
        Args:
            request: The agent request
        
        Returns:
            AgentResponse with health status and check results
        """
        try:
            self.log_request(request)
            self.logger.info("Starting health validation")
            
            # Perform all health checks using validators
            check_results = {
                "databases": self.db_validator.check(),
                "tests": self.test_validator.check() if not request.context.get("skip_tests") else {"status": "skip"},
                "git": self.git_validator.check(),
                "disk_space": self.disk_validator.check(),
                "performance": self.perf_validator.check()
            }
            
            # Analyze results
            status, warnings, errors = self.analyzer.analyze_results(check_results)
            
            # Calculate overall risk
            risk_level = self.analyzer.calculate_risk(check_results, errors)
            
            # Format message
            message = self.formatter.format_message(status, warnings, errors, check_results)
            
            # Get action suggestions
            suggestions = self.formatter.suggest_actions(check_results, risk_level)
            
            # Log to Tier 1 if available
            if self.tier1 and request.conversation_id:
                self.tier1.process_message(
                    request.conversation_id,
                    "agent",
                    f"HealthValidator: System {status}, {len(errors)} errors, {len(warnings)} warnings"
                )
            
            response = AgentResponse(
                success=(status == "healthy"),
                result={
                    "status": status,
                    "checks": check_results,
                    "warnings": warnings,
                    "errors": errors,
                    "risk_level": risk_level,
                    "suggestions": suggestions,
                    "timestamp": datetime.now().isoformat()
                },
                message=message,
                agent_name=self.name,
                metadata={
                    "total_checks": len(check_results),
                    "passed": sum(1 for r in check_results.values() if r.get("status") == "pass"),
                    "failed": sum(1 for r in check_results.values() if r.get("status") == "fail"),
                    "warnings": sum(1 for r in check_results.values() if r.get("status") == "warn"),
                    "skipped": sum(1 for r in check_results.values() if r.get("status") == "skip")
                }
            )
            
            self.logger.info(f"Health validation complete: {status}")
            return response
            
        except Exception as e:
            self.logger.error(f"Health validation error: {str(e)}")
            return AgentResponse(
                success=False,
                result={},
                message=f"Health validation failed: {str(e)}",
                agent_name=self.name,
                error=str(e)
            )
