"""
Threat Modeling Stage

Analyzes user request for security threats and risks using STRIDE model.

Author: CORTEX Development Team
Version: 1.0
"""

from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum

from src.workflows.workflow_pipeline import WorkflowStage, WorkflowState, StageResult, StageStatus


class ThreatCategory(Enum):
    """STRIDE threat categories"""
    SPOOFING = "Spoofing"
    TAMPERING = "Tampering"
    REPUDIATION = "Repudiation"
    INFORMATION_DISCLOSURE = "Information Disclosure"
    DENIAL_OF_SERVICE = "Denial of Service"
    ELEVATION_OF_PRIVILEGE = "Elevation of Privilege"


@dataclass
class Threat:
    """Identified threat"""
    category: ThreatCategory
    description: str
    likelihood: str  # "low", "medium", "high"
    impact: str      # "low", "medium", "high"
    mitigation: str
    
    @property
    def risk_score(self) -> int:
        """Calculate risk score (1-9)"""
        likelihood_map = {"low": 1, "medium": 2, "high": 3}
        impact_map = {"low": 1, "medium": 2, "high": 3}
        return likelihood_map[self.likelihood] * impact_map[self.impact]


class ThreatModelerStage:
    """
    Threat modeling workflow stage
    
    Analyzes user request for security threats using STRIDE:
    - Spoofing: Authentication vulnerabilities
    - Tampering: Data integrity issues
    - Repudiation: Logging/audit gaps
    - Information Disclosure: Data leakage
    - Denial of Service: Resource exhaustion
    - Elevation of Privilege: Access control issues
    """
    
    def execute(self, state: WorkflowState) -> StageResult:
        """
        Execute threat modeling
        
        Args:
            state: Workflow state with user_request
        
        Returns:
            StageResult with identified threats
        """
        user_request = state.user_request.lower()
        
        # Analyze request for threat indicators
        threats = self._identify_threats(user_request, state.context)
        
        # Calculate overall risk
        risk_level = self._calculate_risk_level(threats)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(threats)
        
        return StageResult(
            stage_id="threat_model",
            status=StageStatus.SUCCESS,
            duration_ms=0,  # Set by orchestrator
            output={
                "threats": [
                    {
                        "category": t.category.value,
                        "description": t.description,
                        "likelihood": t.likelihood,
                        "impact": t.impact,
                        "mitigation": t.mitigation,
                        "risk_score": t.risk_score
                    }
                    for t in threats
                ],
                "risk_level": risk_level,
                "recommendations": recommendations,
                "threat_count": len(threats),
                "high_risk_count": len([t for t in threats if t.risk_score >= 6])
            },
            metadata={
                "model": "STRIDE",
                "analysis_depth": "automated"
            }
        )
    
    def validate_input(self, state: WorkflowState) -> bool:
        """Validate state has user request"""
        return bool(state.user_request)
    
    def on_failure(self, state: WorkflowState, error: Exception):
        """Log threat modeling failure"""
        print(f"⚠️  Threat modeling failed: {error}")
        print(f"   Request: {state.user_request[:100]}...")
    
    def _identify_threats(self, request: str, context: Dict[str, Any]) -> List[Threat]:
        """
        Identify threats based on request keywords and context
        
        Args:
            request: Lowercased user request
            context: Workflow context (may contain project patterns)
        
        Returns:
            List of identified threats
        """
        threats = []
        
        # SPOOFING: Authentication/identity threats
        if any(word in request for word in ["login", "auth", "password", "token", "session"]):
            threats.append(Threat(
                category=ThreatCategory.SPOOFING,
                description="Authentication feature may be vulnerable to credential theft or bypass",
                likelihood="medium",
                impact="high",
                mitigation="Use strong password hashing (bcrypt), implement MFA, enforce session timeouts"
            ))
        
        # TAMPERING: Data integrity threats
        if any(word in request for word in ["update", "modify", "edit", "delete", "change"]):
            threats.append(Threat(
                category=ThreatCategory.TAMPERING,
                description="Data modification without validation could corrupt system state",
                likelihood="medium",
                impact="medium",
                mitigation="Validate all inputs, use parameterized queries, implement checksums/signatures"
            ))
        
        # REPUDIATION: Logging/audit threats
        if any(word in request for word in ["transaction", "payment", "order", "submit"]):
            threats.append(Threat(
                category=ThreatCategory.REPUDIATION,
                description="Actions may not be properly logged for audit trail",
                likelihood="low",
                impact="medium",
                mitigation="Log all sensitive operations with user ID, timestamp, and action details"
            ))
        
        # INFORMATION DISCLOSURE: Data leakage threats
        if any(word in request for word in ["export", "download", "share", "api", "email"]):
            threats.append(Threat(
                category=ThreatCategory.INFORMATION_DISCLOSURE,
                description="Sensitive data may be exposed through insecure channels",
                likelihood="medium",
                impact="high",
                mitigation="Encrypt data in transit (HTTPS), implement access controls, sanitize outputs"
            ))
        
        # DENIAL OF SERVICE: Resource exhaustion threats
        if any(word in request for word in ["upload", "import", "process", "calculate", "generate"]):
            threats.append(Threat(
                category=ThreatCategory.DENIAL_OF_SERVICE,
                description="Resource-intensive operations could exhaust system resources",
                likelihood="low",
                impact="medium",
                mitigation="Implement rate limiting, set resource quotas, add timeouts"
            ))
        
        # ELEVATION OF PRIVILEGE: Access control threats
        if any(word in request for word in ["admin", "permission", "role", "access", "privilege"]):
            threats.append(Threat(
                category=ThreatCategory.ELEVATION_OF_PRIVILEGE,
                description="Insufficient access controls could allow privilege escalation",
                likelihood="low",
                impact="high",
                mitigation="Implement least-privilege principle, validate permissions on every request"
            ))
        
        return threats
    
    def _calculate_risk_level(self, threats: List[Threat]) -> str:
        """
        Calculate overall risk level
        
        Args:
            threats: List of identified threats
        
        Returns:
            "low", "medium", "high", or "critical"
        """
        if not threats:
            return "low"
        
        # Find highest risk score
        max_score = max(t.risk_score for t in threats)
        
        if max_score >= 9:
            return "critical"
        elif max_score >= 6:
            return "high"
        elif max_score >= 4:
            return "medium"
        else:
            return "low"
    
    def _generate_recommendations(self, threats: List[Threat]) -> List[str]:
        """
        Generate security recommendations based on threats
        
        Args:
            threats: List of identified threats
        
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        # High-risk threats get priority recommendations
        high_risk = [t for t in threats if t.risk_score >= 6]
        
        if high_risk:
            recommendations.append(
                "⚠️  HIGH RISK: Address the following threats before implementation:"
            )
            for threat in high_risk:
                recommendations.append(f"  • {threat.category.value}: {threat.mitigation}")
        
        # General recommendations
        if any(t.category == ThreatCategory.SPOOFING for t in threats):
            recommendations.append("Consider security review for authentication logic")
        
        if any(t.category == ThreatCategory.INFORMATION_DISCLOSURE for t in threats):
            recommendations.append("Ensure data encryption and access controls are implemented")
        
        if len(threats) >= 3:
            recommendations.append("Multiple threats identified - consider security testing phase")
        
        return recommendations


# Factory function for orchestrator
def create_stage() -> WorkflowStage:
    """Create threat modeler stage instance"""
    return ThreatModelerStage()
