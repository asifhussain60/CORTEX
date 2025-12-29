"""
Risk Narrator - Translate technical debt into business impact

Converts technical metrics (complexity, security vulnerabilities, outdated dependencies)
into business-focused risk narratives that product owners can prioritize.

Example:
    NOT: "Cyclomatic complexity CC=47 in PaymentProcessor.ProcessRefund()"
    BUT: "Payment refund logic is complex and difficult to maintain, increasing
         risk of defects that could impact customer satisfaction and revenue"

Author: Asif Hussain
"""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class RiskNarrator:
    """Translates technical risks into business impact language."""
    
    # Risk severity to business impact mapping
    IMPACT_MAPPING = {
        'CRITICAL': {
            'urgency': 'Immediate',
            'impact': 'High financial/operational risk',
            'action': 'Address within 1 week'
        },
        'HIGH': {
            'urgency': 'Short-term',
            'impact': 'Significant business risk',
            'action': 'Address within 1 month'
        },
        'MEDIUM': {
            'urgency': 'Medium-term',
            'impact': 'Moderate business impact',
            'action': 'Plan for next quarter'
        },
        'LOW': {
            'urgency': 'Long-term',
            'impact': 'Minor business impact',
            'action': 'Address when convenient'
        }
    }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize risk narrator."""
        self.config = config or {}
        logger.info("⚠️ RiskNarrator initialized")
    
    def narrate_risks(self, analysis_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Translate technical risks to business impact narratives.
        
        Args:
            analysis_data: Complete analysis with security, complexity, dependencies
        
        Returns:
            List of risks with business impact and ROI-based recommendations
        """
        logger.info("⚠️ Translating technical risks to business impact")
        
        risks = []
        
        # Security risks
        security_risks = self._narrate_security_risks(analysis_data)
        risks.extend(security_risks)
        
        # Complexity risks
        complexity_risks = self._narrate_complexity_risks(analysis_data)
        risks.extend(complexity_risks)
        
        # Dependency risks
        dependency_risks = self._narrate_dependency_risks(analysis_data)
        risks.extend(dependency_risks)
        
        # Sort by business impact (CRITICAL first)
        risks.sort(key=lambda r: self._impact_priority(r.get('severity', 'LOW')))
        
        logger.info(f"✅ Identified {len(risks)} business risks")
        return risks
    
    def _narrate_security_risks(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Translate security findings to business risks."""
        risks = []
        
        security = data.get('security', {})
        vulnerabilities = security.get('vulnerabilities', [])
        
        for vuln in vulnerabilities[:5]:  # Top 5 for MVP
            risk = {
                'category': 'Security',
                'technical_detail': vuln.get('description', 'Security vulnerability'),
                'business_impact': self._translate_security_impact(vuln),
                'severity': vuln.get('severity', 'MEDIUM'),
                'affected_area': vuln.get('file', 'Unknown'),
                'recommendation': self._generate_security_recommendation(vuln)
            }
            risks.append(risk)
        
        return risks
    
    def _narrate_complexity_risks(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Translate complexity metrics to maintenance risks."""
        risks = []
        
        complexity = data.get('complexity', {})
        hotspots = complexity.get('hotspots', [])
        
        for hotspot in hotspots[:3]:  # Top 3 for MVP
            complexity_value = hotspot.get('complexity', 0)
            if complexity_value > 15:  # Threshold for risk
                risk = {
                    'category': 'Maintainability',
                    'technical_detail': f"High complexity (CC={complexity_value}) in {hotspot.get('function', 'function')}",
                    'business_impact': self._translate_complexity_impact(hotspot),
                    'severity': self._complexity_to_severity(complexity_value),
                    'affected_area': hotspot.get('file', 'Unknown'),
                    'recommendation': self._generate_complexity_recommendation(complexity_value)
                }
                risks.append(risk)
        
        return risks
    
    def _narrate_dependency_risks(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Translate dependency issues to operational risks."""
        risks = []
        
        dependencies = data.get('dependencies', {})
        outdated = dependencies.get('outdated_packages', [])
        
        # Focus on critical outdated dependencies
        for dep in outdated[:3]:  # Top 3 for MVP
            risk = {
                'category': 'Dependencies',
                'technical_detail': f"Outdated dependency: {dep.get('name', 'package')}",
                'business_impact': "May contain security vulnerabilities or lack support, increasing operational risk",
                'severity': 'MEDIUM',
                'affected_area': 'Dependencies',
                'recommendation': f"Update to latest stable version to ensure security and support"
            }
            risks.append(risk)
        
        return risks
    
    def _translate_security_impact(self, vuln: Dict[str, Any]) -> str:
        """Translate security vulnerability to business impact."""
        vuln_type = vuln.get('type', '').lower()
        
        if 'sql injection' in vuln_type:
            return "Data breach risk: Attackers could access or modify sensitive database information"
        elif 'xss' in vuln_type or 'cross-site' in vuln_type:
            return "User security risk: Malicious scripts could compromise user accounts"
        elif 'secret' in vuln_type or 'credential' in vuln_type:
            return "Credential exposure risk: Hardcoded secrets could enable unauthorized access"
        elif 'command injection' in vuln_type:
            return "System compromise risk: Attackers could execute arbitrary commands"
        else:
            return "Security vulnerability that could be exploited by malicious actors"
    
    def _translate_complexity_impact(self, hotspot: Dict[str, Any]) -> str:
        """Translate complexity hotspot to business impact."""
        function_name = hotspot.get('function', 'function')
        
        # Infer business impact from function name
        if 'payment' in function_name.lower():
            return "Complex payment logic increases risk of defects that could impact revenue and customer trust"
        elif 'auth' in function_name.lower() or 'login' in function_name.lower():
            return "Complex authentication logic increases security risk and maintenance burden"
        elif 'order' in function_name.lower():
            return "Complex order processing increases risk of errors affecting customer satisfaction"
        else:
            return "High complexity increases maintenance costs and risk of bugs during changes"
    
    def _complexity_to_severity(self, complexity: int) -> str:
        """Map complexity value to severity."""
        if complexity > 30:
            return 'HIGH'
        elif complexity > 20:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _generate_security_recommendation(self, vuln: Dict[str, Any]) -> str:
        """Generate actionable security recommendation."""
        return "Review and remediate security vulnerability following secure coding practices"
    
    def _generate_complexity_recommendation(self, complexity: int) -> str:
        """Generate actionable complexity recommendation."""
        if complexity > 30:
            return "Refactor into smaller functions to improve maintainability and reduce defect risk"
        else:
            return "Consider refactoring to simplify logic and improve maintainability"
    
    def _impact_priority(self, severity: str) -> int:
        """Convert severity to priority number (lower = higher priority)."""
        priority_map = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        return priority_map.get(severity, 4)
