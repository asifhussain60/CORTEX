"""
Use Case Discoverer - Extract business workflows from code

Transforms API endpoints, UI routes, and method call sequences into
user-facing use cases with actors, triggers, flows, and outcomes.

Example:
    Input: POST /api/expenses/submit endpoint
    Output: "Employee Reimbursement Submission" use case with 6-step workflow

Author: Asif Hussain
"""

from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
import re
import logging

logger = logging.getLogger(__name__)


@dataclass
class UseCase:
    """Business use case extracted from code."""
    id: str
    title: str
    description: str
    actors: List[str] = field(default_factory=list)
    trigger: str = ""
    steps: List[str] = field(default_factory=list)
    outcome: str = ""
    endpoints: List[str] = field(default_factory=list)
    evidence: Dict[str, Any] = field(default_factory=dict)
    business_value: str = ""
    frequency: str = "UNKNOWN"  # HIGH/MEDIUM/LOW/UNKNOWN


class UseCaseDiscoverer:
    """
    Discovers business use cases from code analysis.
    
    Analyzes API endpoints, routes, method names, and comments to identify
    what users can actually DO with the application. Maps technical endpoints
    to business workflows with clear actors, steps, and outcomes.
    
    Strategy:
        1. Group related endpoints by domain (e.g., /expenses/*, /reports/*)
        2. Identify CRUD operations and workflow sequences
        3. Extract actors from auth patterns and role checks
        4. Synthesize steps from endpoint sequences and method names
        5. Generate business-focused titles and descriptions
    
    Example:
        >>> discoverer = UseCaseDiscoverer()
        >>> use_cases = discoverer.discover({
        ...     'api_endpoints': {
        ...         'endpoints': [
        ...             {'path': '/expenses/submit', 'method': 'POST'},
        ...             {'path': '/expenses/{id}/approve', 'method': 'PUT'}
        ...         ]
        ...     }
        ... })
        >>> print(use_cases[0]['title'])
        'Expense Submission and Approval Workflow'
    """
    
    # Common business domains and their keywords
    DOMAINS = {
        'authentication': ['login', 'logout', 'auth', 'signin', 'signup', 'register'],
        'user_management': ['user', 'profile', 'account', 'member'],
        'payment': ['payment', 'checkout', 'purchase', 'transaction', 'order'],
        'reporting': ['report', 'analytics', 'dashboard', 'metrics', 'stats'],
        'content': ['post', 'article', 'page', 'content', 'blog'],
        'messaging': ['message', 'notification', 'email', 'chat', 'alert'],
        'administration': ['admin', 'settings', 'config', 'manage'],
        'workflow': ['submit', 'approve', 'reject', 'review', 'process']
    }
    
    # Business action verbs
    ACTION_VERBS = {
        'create': ['Create', 'Submit', 'Add', 'Register', 'Initialize'],
        'read': ['View', 'Browse', 'Search', 'List', 'Retrieve'],
        'update': ['Update', 'Modify', 'Edit', 'Change', 'Revise'],
        'delete': ['Delete', 'Remove', 'Cancel', 'Archive', 'Disable'],
        'approve': ['Approve', 'Accept', 'Confirm', 'Authorize', 'Validate'],
        'reject': ['Reject', 'Decline', 'Deny', 'Refuse', 'Disapprove']
    }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize use case discoverer with optional configuration."""
        self.config = config or {}
        self.min_endpoints_for_usecase = self.config.get('min_endpoints', 1)
        logger.info("🔍 UseCaseDiscoverer initialized")
    
    def discover(self, analysis_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Discover use cases from analysis data.
        
        Args:
            analysis_data: Complete analysis with api_endpoints, architecture, comments
        
        Returns:
            List of use cases with actors, flows, and business value
        """
        logger.info("🔍 Discovering use cases from code analysis")
        
        use_cases = []
        
        # Extract endpoint data
        endpoints = self._extract_endpoints(analysis_data)
        if not endpoints:
            logger.warning("⚠️ No API endpoints found, use case discovery limited")
            return use_cases
        
        # Group endpoints by domain
        grouped = self._group_by_domain(endpoints)
        logger.info(f"📂 Grouped endpoints into {len(grouped)} domains")
        
        # Generate use cases for each domain
        for domain, domain_endpoints in grouped.items():
            domain_use_cases = self._generate_domain_use_cases(
                domain,
                domain_endpoints,
                analysis_data
            )
            use_cases.extend(domain_use_cases)
        
        # Enrich with evidence and business value
        for uc in use_cases:
            self._enrich_use_case(uc, analysis_data)
        
        logger.info(f"✅ Discovered {len(use_cases)} use cases")
        return [self._serialize(uc) for uc in use_cases]
    
    def _extract_endpoints(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract API endpoints from analysis data."""
        api_data = data.get('api_endpoints', {})
        return api_data.get('endpoints', [])
    
    def _group_by_domain(self, endpoints: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group endpoints by business domain.
        
        Examples:
            /api/expenses/submit -> 'expenses'
            /users/{id}/profile -> 'users'
            /reports/weekly -> 'reports'
        """
        groups = {}
        
        for endpoint in endpoints:
            path = endpoint.get('path', '')
            domain = self._extract_domain_from_path(path)
            
            if domain not in groups:
                groups[domain] = []
            groups[domain].append(endpoint)
        
        return groups
    
    def _extract_domain_from_path(self, path: str) -> str:
        """
        Extract domain name from API path.
        
        Examples:
            /api/expenses/submit -> expenses
            /users/{id} -> users
            /v2/reports/weekly -> reports
        """
        # Remove version prefix, api prefix, query params
        cleaned = re.sub(r'^/(api|v\d+)/', '', path)
        cleaned = cleaned.split('?')[0]
        
        # Extract first meaningful segment
        parts = [p for p in cleaned.split('/') if p and not p.startswith('{')]
        return parts[0] if parts else 'general'
    
    def _generate_domain_use_cases(
        self,
        domain: str,
        endpoints: List[Dict[str, Any]],
        analysis_data: Dict[str, Any]
    ) -> List[UseCase]:
        """Generate use cases for a specific domain."""
        use_cases = []
        
        # Identify CRUD workflows
        crud_workflow = self._identify_crud_workflow(domain, endpoints)
        if crud_workflow:
            use_cases.append(crud_workflow)
        
        # Identify approval workflows (submit -> approve/reject pattern)
        approval_workflow = self._identify_approval_workflow(domain, endpoints)
        if approval_workflow:
            use_cases.append(approval_workflow)
        
        # Identify search/browse workflows
        search_workflow = self._identify_search_workflow(domain, endpoints)
        if search_workflow:
            use_cases.append(search_workflow)
        
        return use_cases
    
    def _identify_crud_workflow(self, domain: str, endpoints: List[Dict[str, Any]]) -> Optional[UseCase]:
        """Identify Create-Read-Update-Delete workflow."""
        methods = {ep.get('method', '').upper() for ep in endpoints}
        
        # Need at least create or read
        if not ('POST' in methods or 'GET' in methods):
            return None
        
        # Build use case
        uc = UseCase(
            id=f"crud_{domain}",
            title=f"{domain.title()} Management",
            description=f"Create, view, update, and manage {domain} records"
        )
        
        # Map HTTP methods to business steps
        if 'POST' in methods:
            uc.steps.append(f"Create new {domain} record")
        if 'GET' in methods:
            uc.steps.append(f"View {domain} details")
        if 'PUT' in methods or 'PATCH' in methods:
            uc.steps.append(f"Update {domain} information")
        if 'DELETE' in methods:
            uc.steps.append(f"Delete {domain} record")
        
        uc.actors = self._infer_actors(domain, endpoints)
        uc.trigger = f"User needs to manage {domain}"
        uc.outcome = f"{domain.title()} records are maintained"
        uc.endpoints = [ep.get('path', '') for ep in endpoints]
        uc.business_value = f"Enables {domain} lifecycle management"
        
        return uc
    
    def _identify_approval_workflow(self, domain: str, endpoints: List[Dict[str, Any]]) -> Optional[UseCase]:
        """Identify submission-approval workflow (common in business apps)."""
        paths = [ep.get('path', '').lower() for ep in endpoints]
        
        # Look for submit + approve/reject pattern
        has_submit = any('submit' in p for p in paths)
        has_approve = any('approve' in p or 'accept' in p for p in paths)
        has_reject = any('reject' in p or 'decline' in p for p in paths)
        
        if not (has_submit and (has_approve or has_reject)):
            return None
        
        uc = UseCase(
            id=f"approval_{domain}",
            title=f"{domain.title()} Submission and Approval",
            description=f"Submit {domain} for review and approval workflow"
        )
        
        uc.steps = [
            f"User submits {domain} for review",
            f"System validates {domain} data",
            f"Reviewer receives notification",
            f"Reviewer approves or rejects {domain}",
            f"User receives approval decision",
            f"System processes approved {domain}"
        ]
        
        uc.actors = ["Submitter", "Reviewer", "System"]
        uc.trigger = f"User completes {domain} and needs approval"
        uc.outcome = f"Approved {domain} is processed, rejected items return to submitter"
        uc.endpoints = [ep.get('path', '') for ep in endpoints if any(kw in ep.get('path', '').lower() for kw in ['submit', 'approve', 'reject'])]
        uc.business_value = f"Ensures {domain} quality through approval workflow"
        uc.frequency = "HIGH"  # Approval workflows are typically frequent
        
        return uc
    
    def _identify_search_workflow(self, domain: str, endpoints: List[Dict[str, Any]]) -> Optional[UseCase]:
        """Identify search/browse workflow."""
        paths = [ep.get('path', '').lower() for ep in endpoints]
        methods = {ep.get('method', '').upper() for ep in endpoints}
        
        # Look for search, list, or GET with query params
        has_search = any('search' in path or 'query' in path for path in paths)
        has_list = any('list' in path or (ep.get('method') == 'GET' and not '{' in ep.get('path', '')) for ep, path in zip(endpoints, paths))
        
        if not (has_search or has_list):
            return None
        
        uc = UseCase(
            id=f"search_{domain}",
            title=f"Search and Browse {domain.title()}",
            description=f"Find and view {domain} using search and filters"
        )
        
        uc.steps = [
            f"User enters search criteria for {domain}",
            f"System queries {domain} database",
            f"Results are displayed with relevant details",
            f"User can filter or sort results",
            f"User selects item for detailed view"
        ]
        
        uc.actors = self._infer_actors(domain, endpoints)
        uc.trigger = f"User needs to find specific {domain}"
        uc.outcome = f"User locates and views desired {domain}"
        uc.endpoints = [ep.get('path', '') for ep in endpoints if 'GET' in ep.get('method', '')]
        uc.business_value = f"Enables efficient {domain} discovery"
        
        return uc
    
    def _infer_actors(self, domain: str, endpoints: List[Dict[str, Any]]) -> List[str]:
        """
        Infer actors from domain name and endpoint patterns.
        
        Uses heuristics:
        - admin paths -> Administrator
        - user paths -> User
        - manager paths -> Manager
        - Common business roles based on domain
        """
        actors = set()
        
        # Check paths for role indicators
        for ep in endpoints:
            path = ep.get('path', '').lower()
            if 'admin' in path:
                actors.add("Administrator")
            elif 'manager' in path:
                actors.add("Manager")
            elif 'user' in path:
                actors.add("User")
        
        # Domain-specific actors
        if domain in ['expenses', 'reimbursement']:
            actors.update(["Employee", "Manager", "Finance Team"])
        elif domain in ['orders', 'purchases']:
            actors.update(["Customer", "Sales Representative"])
        elif domain in ['reports', 'analytics']:
            actors.update(["Analyst", "Executive", "Manager"])
        
        # Default actor if none identified
        if not actors:
            actors.add("User")
        
        return sorted(actors)
    
    def _enrich_use_case(self, use_case: UseCase, analysis_data: Dict[str, Any]) -> None:
        """Enrich use case with additional evidence and context from analysis."""
        # Add code evidence
        use_case.evidence['endpoint_count'] = len(use_case.endpoints)
        
        # Check for comments that mention this domain
        comments = analysis_data.get('comments', {})
        if comments:
            # This would search comments for domain-related business context
            # For now, placeholder
            use_case.evidence['has_business_documentation'] = comments.get('total_comments', 0) > 0
        
        # Check complexity to assess implementation maturity
        complexity = analysis_data.get('complexity', {})
        if complexity:
            avg_complexity = complexity.get('average_complexity', 0)
            use_case.evidence['implementation_maturity'] = (
                'MATURE' if avg_complexity < 10 else
                'MODERATE' if avg_complexity < 20 else 'NEEDS_REFACTORING'
            )
    
    def _serialize(self, use_case: UseCase) -> Dict[str, Any]:
        """Convert UseCase dataclass to dictionary."""
        return {
            'id': use_case.id,
            'title': use_case.title,
            'description': use_case.description,
            'actors': use_case.actors,
            'trigger': use_case.trigger,
            'steps': use_case.steps,
            'outcome': use_case.outcome,
            'endpoints': use_case.endpoints,
            'evidence': use_case.evidence,
            'business_value': use_case.business_value,
            'frequency': use_case.frequency
        }
