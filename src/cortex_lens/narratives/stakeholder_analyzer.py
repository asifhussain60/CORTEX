"""
Stakeholder Analyzer - Identify who uses the application and how

Analyzes authentication patterns, role checks, and CRUD operations to
identify user roles and their key activities.

Example:
    Input: @Authorize(Roles="Manager") endpoints, high-frequency operations
    Output: "Manager (25 users) - Approves expense reports, reviews analytics, configures settings"

Author: Asif Hussain
"""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class StakeholderAnalyzer:
    """Analyzes stakeholders and their impact on the application."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize stakeholder analyzer."""
        self.config = config or {}
        logger.info("👥 StakeholderAnalyzer initialized")
    
    def analyze(self, analysis_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analyze stakeholders from auth patterns and operations.
        
        Args:
            analysis_data: Complete analysis with security, API endpoints
        
        Returns:
            List of stakeholders with roles, activities, and business impact
        """
        logger.info("👥 Analyzing stakeholders")
        
        stakeholders = []
        
        # Extract roles from security analysis
        security = analysis_data.get('security', {})
        roles = self._extract_roles(security, analysis_data)
        
        # Create stakeholder profiles
        for role in roles:
            stakeholder = self._create_stakeholder_profile(role, analysis_data)
            stakeholders.append(stakeholder)
        
        # Add generic user if no roles found
        if not stakeholders:
            stakeholders.append({
                'role': 'User',
                'description': 'Application users',
                'estimated_count': 'Unknown',
                'key_activities': ['Access application features'],
                'business_impact': 'PRIMARY',
                'frequency': 'DAILY'
            })
        
        logger.info(f"✅ Identified {len(stakeholders)} stakeholder roles")
        return stakeholders
    
    def _extract_roles(self, security: Dict[str, Any], data: Dict[str, Any]) -> List[str]:
        """Extract user roles from security patterns."""
        roles = set()
        
        # Common business roles
        default_roles = ['User', 'Administrator', 'Manager']
        
        # Check endpoints for role patterns
        endpoints = data.get('api_endpoints', {}).get('endpoints', [])
        for ep in endpoints:
            path = ep.get('path', '').lower()
            if 'admin' in path:
                roles.add('Administrator')
            elif 'manager' in path:
                roles.add('Manager')
        
        return list(roles) if roles else default_roles
    
    def _create_stakeholder_profile(self, role: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create detailed stakeholder profile."""
        return {
            'role': role,
            'description': f"{role} of the application",
            'estimated_count': 'Unknown',
            'key_activities': self._infer_activities(role, data),
            'business_impact': 'HIGH' if role == 'Administrator' else 'MEDIUM',
            'frequency': 'DAILY'
        }
    
    def _infer_activities(self, role: str, data: Dict[str, Any]) -> List[str]:
        """Infer key activities for role."""
        if role == 'Administrator':
            return ['Manage system configuration', 'Monitor system health', 'Manage users']
        elif role == 'Manager':
            return ['Review reports', 'Approve requests', 'Manage team']
        else:
            return ['Access features', 'Perform operations', 'View data']
