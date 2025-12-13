"""
Business Flow Mapper - Transform technical call chains into business processes

Maps endpoint sequences and method calls into user-facing workflow descriptions.

Example:
    Input: OrderController.create() -> PaymentService.process() -> InventoryService.reserve()
    Output: "When customer completes checkout, system processes payment and reserves inventory"

Author: Asif Hussain
"""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class BusinessFlowMapper:
    """Maps technical code flows to business process narratives."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize business flow mapper."""
        self.config = config or {}
        logger.info("🔄 BusinessFlowMapper initialized")
    
    def map_flows(self, analysis_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Map technical flows to business processes.
        
        Args:
            analysis_data: Complete analysis with API endpoints, call chains
        
        Returns:
            List of business flows with steps and decision points
        """
        logger.info("🔄 Mapping business flows from code")
        
        flows = []
        
        # Extract API endpoint sequences
        endpoints = analysis_data.get('api_endpoints', {}).get('endpoints', [])
        
        # Group related endpoints into workflows
        # For MVP, create basic flow from endpoints
        for endpoint in endpoints[:5]:  # Limit to top 5 for MVP
            flow = self._create_flow_from_endpoint(endpoint)
            if flow:
                flows.append(flow)
        
        logger.info(f"✅ Mapped {len(flows)} business flows")
        return flows
    
    def _create_flow_from_endpoint(self, endpoint: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create business flow from single endpoint."""
        path = endpoint.get('path', '')
        method = endpoint.get('method', '')
        
        if not path:
            return None
        
        # Extract action from path
        parts = path.split('/')
        action = parts[-1] if parts else 'operation'
        
        # Map HTTP method to business action
        action_map = {
            'POST': 'creates',
            'GET': 'retrieves',
            'PUT': 'updates',
            'DELETE': 'removes',
            'PATCH': 'modifies'
        }
        
        verb = action_map.get(method, 'processes')
        
        return {
            'id': f"flow_{action}",
            'title': f"{action.title()} Workflow",
            'trigger': f"User initiates {action}",
            'steps': [
                f"User {verb} {action}",
                "System validates request",
                f"System processes {action}",
                "System returns confirmation"
            ],
            'outcome': f"{action.title()} completed successfully",
            'endpoints': [path],
            'decision_points': []
        }
