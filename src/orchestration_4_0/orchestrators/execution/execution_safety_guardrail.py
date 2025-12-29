"""
Safety Guardrails for Execution Orchestrator

Execution safety checks and risk assessment.

Author: Asif Hussain
Version: 1.0
"""

from typing import Dict, Any, List
import json
import logging

from .schemas import Risk, RiskSeverity, SafetyCheck


class ExecutionSafetyGuardrail:
    """
    Safety checks for execution workflows.
    
    Features:
    - Detect destructive operations
    - Check resource limits
    - Detect data exposure risks
    - Assess production environment risks
    - Calculate overall risk level
    """
    
    def __init__(self, logger: logging.Logger = None):
        """
        Initialize safety guardrail.
        
        Args:
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        
        # Risk severity ordering
        self.severity_order = {
            RiskSeverity.CRITICAL: 4,
            RiskSeverity.HIGH: 3,
            RiskSeverity.MEDIUM: 2,
            RiskSeverity.LOW: 1,
        }
    
    async def check_execution_safety(
        self,
        execution_plan: Dict[str, Any],
        context: Dict[str, Any]
    ) -> SafetyCheck:
        """
        Check execution safety before running.
        
        Args:
            execution_plan: Plan to execute
            context: Execution context
            
        Returns:
            SafetyCheck with risks and recommendations
        """
        self.logger.debug("🛡️ Checking execution safety...")
        
        risks: List[Risk] = []
        
        # Check for destructive operations
        risks.extend(self._check_destructive_operations(execution_plan))
        
        # Check for resource exhaustion
        risks.extend(self._check_resource_limits(execution_plan, context))
        
        # Check for data exposure
        risks.extend(self._check_data_exposure(context))
        
        # Check for production environment
        risks.extend(self._check_production_risk(context))
        
        # Calculate overall risk
        max_risk = self._calculate_max_risk(risks)
        
        # Determine if approval required
        requires_approval = max_risk in [RiskSeverity.HIGH, RiskSeverity.CRITICAL]
        
        # Determine if safe to proceed
        safe = max_risk not in [RiskSeverity.CRITICAL]
        
        safety_check = SafetyCheck(
            safe=safe,
            risks=risks,
            max_risk=max_risk,
            requires_approval=requires_approval
        )
        
        if not safe:
            self.logger.warning(f"⚠️ Safety check FAILED: {max_risk} risk detected")
        elif requires_approval:
            self.logger.info(f"⚠️ Safety check: {max_risk} risk - approval required")
        else:
            self.logger.info(f"✅ Safety check passed ({max_risk} risk)")
        
        return safety_check
    
    def _check_destructive_operations(
        self,
        execution_plan: Dict[str, Any]
    ) -> List[Risk]:
        """
        Check for destructive operations.
        
        Args:
            execution_plan: Plan to check
            
        Returns:
            List of detected risks
        """
        risks = []
        
        # Destructive patterns with severity
        destructive_patterns = [
            ('delete', RiskSeverity.CRITICAL, 'Deletion operation'),
            ('drop', RiskSeverity.CRITICAL, 'Drop operation'),
            ('truncate', RiskSeverity.HIGH, 'Truncate operation'),
            ('remove', RiskSeverity.HIGH, 'Removal operation'),
            ('purge', RiskSeverity.CRITICAL, 'Purge operation'),
            ('destroy', RiskSeverity.CRITICAL, 'Destroy operation'),
            ('wipe', RiskSeverity.CRITICAL, 'Wipe operation'),
        ]
        
        # Convert plan to searchable string
        plan_str = json.dumps(execution_plan).lower()
        
        for pattern, severity, description in destructive_patterns:
            if pattern in plan_str:
                risks.append(Risk(
                    severity=severity,
                    category='Destructive Operation',
                    message=f'{description} detected in execution plan',
                    recommendation='Ensure backup exists before proceeding'
                ))
                self.logger.warning(f"🚨 Detected destructive operation: {pattern}")
        
        return risks
    
    def _check_resource_limits(
        self,
        execution_plan: Dict[str, Any],
        context: Dict[str, Any]
    ) -> List[Risk]:
        """
        Check for resource exhaustion.
        
        Args:
            execution_plan: Plan to check
            context: Execution context
            
        Returns:
            List of detected risks
        """
        risks = []
        
        # Check parallelism
        parallelism = execution_plan.get('parallelism', 1)
        if parallelism > 10:
            risks.append(Risk(
                severity=RiskSeverity.HIGH,
                category='Resource Exhaustion',
                message=f'High parallelism ({parallelism} threads) may exhaust resources',
                recommendation='Reduce parallelism or increase resource limits'
            ))
        elif parallelism > 50:
            risks.append(Risk(
                severity=RiskSeverity.CRITICAL,
                category='Resource Exhaustion',
                message=f'Extreme parallelism ({parallelism} threads) will exhaust resources',
                recommendation='Reduce parallelism to <10 threads'
            ))
        
        # Check timeout
        timeout = execution_plan.get('timeout_seconds', 300)
        if timeout > 3600:
            risks.append(Risk(
                severity=RiskSeverity.MEDIUM,
                category='Long-Running Operation',
                message=f'Execution timeout is {timeout}s (>1 hour)',
                recommendation='Consider breaking into smaller operations'
            ))
        
        # Check memory requirements
        memory_mb = execution_plan.get('memory_mb', 0)
        if memory_mb > 8192:  # >8GB
            risks.append(Risk(
                severity=RiskSeverity.HIGH,
                category='Resource Exhaustion',
                message=f'High memory requirement ({memory_mb}MB)',
                recommendation='Ensure sufficient memory available'
            ))
        
        return risks
    
    def _check_data_exposure(self, context: Dict[str, Any]) -> List[Risk]:
        """
        Check for sensitive data exposure.
        
        Args:
            context: Execution context to check
            
        Returns:
            List of detected risks
        """
        risks = []
        
        # Sensitive keys
        sensitive_keys = [
            'password', 'api_key', 'token', 'secret', 'private_key',
            'access_key', 'auth_token', 'credentials', 'apikey'
        ]
        
        # Check for credentials in context
        for key in context.keys():
            key_lower = key.lower()
            for sensitive in sensitive_keys:
                if sensitive in key_lower:
                    risks.append(Risk(
                        severity=RiskSeverity.CRITICAL,
                        category='Data Exposure',
                        message=f'Sensitive data "{key}" in execution context',
                        recommendation='Use secret management instead of passing in context'
                    ))
                    self.logger.warning(f"🚨 Sensitive data in context: {key}")
                    break
        
        # Check for PII patterns in string values
        pii_patterns = [
            ('email', r'[\w\.-]+@[\w\.-]+\.\w+'),
            ('ssn', r'\d{3}-\d{2}-\d{4}'),
            ('credit_card', r'\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}'),
        ]
        
        import re
        for key, value in context.items():
            if isinstance(value, str):
                for pii_type, pattern in pii_patterns:
                    if re.search(pattern, value):
                        risks.append(Risk(
                            severity=RiskSeverity.HIGH,
                            category='PII Exposure',
                            message=f'Possible {pii_type} detected in context field "{key}"',
                            recommendation='Mask or remove PII from execution context'
                        ))
        
        return risks
    
    def _check_production_risk(self, context: Dict[str, Any]) -> List[Risk]:
        """
        Check for production environment risks.
        
        Args:
            context: Execution context
            
        Returns:
            List of detected risks
        """
        risks = []
        
        # Check environment indicators
        environment = context.get('environment', '').lower()
        
        production_indicators = ['prod', 'production', 'live']
        is_production = any(ind in environment for ind in production_indicators)
        
        if is_production:
            risks.append(Risk(
                severity=RiskSeverity.HIGH,
                category='Production Environment',
                message='Execution targets production environment',
                recommendation='Verify changes in staging first, ensure rollback plan exists'
            ))
            self.logger.warning("🚨 Production environment detected")
        
        # Check for production URLs
        url = context.get('url', '').lower()
        if any(ind in url for ind in production_indicators):
            risks.append(Risk(
                severity=RiskSeverity.HIGH,
                category='Production Environment',
                message=f'Production URL detected: {context.get("url")}',
                recommendation='Use staging URL for testing'
            ))
        
        return risks
    
    def _calculate_max_risk(self, risks: List[Risk]) -> RiskSeverity:
        """
        Calculate maximum risk severity.
        
        Args:
            risks: List of risks
            
        Returns:
            Maximum severity level
        """
        if not risks:
            return RiskSeverity.LOW
        
        max_severity = RiskSeverity.LOW
        max_order = self.severity_order[RiskSeverity.LOW]
        
        for risk in risks:
            order = self.severity_order[risk.severity]
            if order > max_order:
                max_severity = risk.severity
                max_order = order
        
        return max_severity
