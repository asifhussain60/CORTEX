"""
Use Case Collector - Phase 7.6.1
Generates unified use case data model from code analysis

Features:
- Role inference (end_user, manager, admin, api_consumer)
- Domain classification (security, e-commerce, reporting, user mgmt)
- Process step extraction
- Confidence scoring
- Unified JSON output

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import re
from typing import Dict, List, Any, Optional
from pathlib import Path


class UseCaseCollector:
    """Collects and generates use cases from code analysis"""
    
    # Domain keyword mappings
    DOMAIN_KEYWORDS = {
        'security_authentication': ['auth', 'login', 'signin', 'authenticate', 'token', 'jwt', 'session', 'password'],
        'e_commerce': ['payment', 'order', 'cart', 'checkout', 'product', 'invoice', 'billing', 'stripe', 'transaction'],
        'reporting': ['report', 'analytics', 'dashboard', 'export', 'pdf', 'excel', 'chart', 'metrics'],
        'user_management': ['user', 'profile', 'account', 'registration', 'member']
    }
    
    # Business value keywords
    CRITICAL_KEYWORDS = ['auth', 'login', 'payment', 'checkout', 'transaction', 'billing']
    
    def __init__(self):
        """Initialize use case collector"""
        self.use_case_counter = 1
    
    def infer_role_from_endpoint(self, endpoint: str, method: str) -> str:
        """
        Infer user role from endpoint path and HTTP method
        
        Args:
            endpoint: API endpoint path (e.g., "POST /api/auth/login")
            method: HTTP method (GET, POST, PUT, DELETE)
            
        Returns:
            Role string (end_user, manager, admin, api_consumer)
        """
        endpoint_lower = endpoint.lower()
        
        # Admin endpoints
        if 'admin' in endpoint_lower or '/management/' in endpoint_lower:
            return 'admin'
        
        # Authentication endpoints are end_user (everyone needs to login)
        if '/auth/' in endpoint_lower or '/login' in endpoint_lower or '/signin' in endpoint_lower:
            return 'end_user'
        
        # API consumer - explicit API versioning
        if re.search(r'/api/v\d+/', endpoint_lower) and method == 'GET':
            return 'api_consumer'
        
        # Manager - write operations on business entities
        if method in ['POST', 'PUT', 'DELETE']:
            if any(keyword in endpoint_lower for keyword in ['orders', 'products', 'inventory', 'reports']):
                return 'manager'
        
        # End user - read operations or basic interactions
        if method == 'GET':
            return 'end_user'
        
        # Default for write ops not covered above
        if method in ['POST', 'PUT', 'DELETE']:
            return 'manager'
        
        return 'end_user'
    
    def infer_domain(self, files: List[str], methods: List[str]) -> str:
        """
        Infer business domain from file names and method names
        
        Args:
            files: List of file names
            methods: List of method names
            
        Returns:
            Domain identifier string
        """
        # Combine all text for analysis
        text = ' '.join(files + methods).lower()
        
        # Count keyword matches per domain
        domain_scores = {}
        for domain, keywords in self.DOMAIN_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                domain_scores[domain] = score
        
        # Return domain with highest score
        if domain_scores:
            return max(domain_scores, key=domain_scores.get)
        
        return 'general'
    
    def extract_process_steps(self, method_sequence: List[str]) -> List[str]:
        """
        Extract human-readable process steps from method sequence
        
        Args:
            method_sequence: List of method names in order
            
        Returns:
            List of formatted step descriptions
        """
        steps = []
        
        for method in method_sequence:
            # Convert camelCase to Title Case with spaces
            # validateCart -> Validate cart
            step = re.sub('([a-z])([A-Z])', r'\1 \2', method)
            step = step[0].upper() + step[1:].lower()
            steps.append(step)
        
        return steps
    
    def calculate_confidence(self, data: Dict[str, Any]) -> int:
        """
        Calculate confidence score (0-100) for use case inference
        
        Args:
            data: Use case data with endpoints, files, methods
            
        Returns:
            Confidence score 0-100
        """
        score = 0
        
        # Endpoints present (30 points)
        if data.get('endpoints'):
            score += 30
        
        # Multiple files (20 points)
        files = data.get('files', [])
        if len(files) >= 3:
            score += 20
        elif len(files) >= 2:
            score += 18
        elif len(files) >= 1:
            score += 10
        
        # Multiple methods (20 points)
        methods = data.get('methods', [])
        if len(methods) >= 4:
            score += 20
        elif len(methods) >= 3:
            score += 15
        elif len(methods) >= 2:
            score += 10
        
        # Complexity indicates implementation (15 points)
        if data.get('complexity', 0) > 10:
            score += 15
        elif data.get('complexity', 0) > 5:
            score += 10
        
        # Clear naming conventions (15 points)
        if any(keyword in str(files + methods).lower() for keyword in self.CRITICAL_KEYWORDS):
            score += 15
        
        return min(score, 100)
    
    def determine_business_value(self, domain: str, methods: List[str]) -> str:
        """
        Determine business value (critical, high, medium, low)
        
        Args:
            domain: Business domain
            methods: List of method names
            
        Returns:
            Business value tier
        """
        # Authentication and payment always critical
        if domain == 'security_authentication':
            return 'critical'
        
        if domain == 'e_commerce':
            # Payment/checkout critical, others high
            text = ' '.join(methods).lower()
            if any(keyword in text for keyword in ['payment', 'checkout', 'transaction', 'billing']):
                return 'critical'
            return 'high'
        
        if domain == 'reporting':
            return 'medium'
        
        if domain == 'user_management':
            return 'high'
        
        return 'medium'
    
    def generate_use_case(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a use case from analysis data
        
        Args:
            data: Dict with endpoints, files, methods, complexity
            
        Returns:
            Use case dict
        """
        # Extract data
        endpoints = data.get('endpoints', [])
        files = data.get('files', [])
        methods = data.get('methods', [])
        complexity = data.get('complexity', 0)
        
        # Infer properties
        domain = self.infer_domain(files, methods)
        
        # Infer roles from endpoints
        roles = set()
        endpoint_paths = []
        for endpoint in endpoints:
            if isinstance(endpoint, dict):
                path = endpoint.get('path', '')
                method = path.split()[0] if ' ' in path else 'GET'
                endpoint_path = path.split(maxsplit=1)[1] if ' ' in path else path
            else:
                path = endpoint
                method = 'GET'
                endpoint_path = path
            
            role = self.infer_role_from_endpoint(endpoint_path, method)
            roles.add(role)
            endpoint_paths.append(endpoint_path if ' ' not in path else path)
        
        if not roles:
            roles = {'end_user'}
        
        # Generate name from domain
        name_mapping = {
            'security_authentication': 'User Login',
            'e_commerce': 'Payment Processing' if any('payment' in m.lower() for m in methods) else 'Order Management',
            'reporting': 'Report Generation',
            'user_management': 'User Management'
        }
        name = name_mapping.get(domain, 'General Functionality')
        
        # Calculate scores
        confidence = self.calculate_confidence(data)
        business_value = self.determine_business_value(domain, methods)
        
        # Build use case
        use_case = {
            'id': f'uc-{str(self.use_case_counter).zfill(3)}',
            'name': name,
            'description': f"Handle {name.lower()} functionality",
            'roles': list(roles),
            'domain': domain,
            'endpoints': endpoint_paths,
            'files': files,
            'complexity': complexity,
            'business_value': business_value,
            'confidence': confidence
        }
        
        self.use_case_counter += 1
        return use_case
    
    def get_metadata(self) -> Dict[str, List[Dict[str, str]]]:
        """
        Get metadata structure for roles, domains, processes
        
        Returns:
            Metadata dict with roles, domains, processes
        """
        return {
            'roles': [
                {
                    'id': 'end_user',
                    'name': 'End User',
                    'description': 'Public users of the application'
                },
                {
                    'id': 'manager',
                    'name': 'Manager',
                    'description': 'Internal staff with write access to business entities'
                },
                {
                    'id': 'admin',
                    'name': 'Administrator',
                    'description': 'System administrators with full access'
                },
                {
                    'id': 'api_consumer',
                    'name': 'API Consumer',
                    'description': 'External integrations and API clients'
                }
            ],
            'domains': [
                {
                    'id': 'security_authentication',
                    'name': 'Security & Authentication',
                    'description': 'User authentication, authorization, and security'
                },
                {
                    'id': 'e_commerce',
                    'name': 'E-Commerce',
                    'description': 'Orders, payments, shopping cart, and transactions'
                },
                {
                    'id': 'reporting',
                    'name': 'Reporting & Analytics',
                    'description': 'Business intelligence, reports, and data exports'
                },
                {
                    'id': 'user_management',
                    'name': 'User Management',
                    'description': 'User profiles, accounts, and registration'
                }
            ],
            'processes': []  # Populated during analysis
        }
    
    def collect(self, all_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Collect use cases from all analysis data
        
        Args:
            all_data: Complete analysis data from dashboard collectors
            
        Returns:
            Unified use case data structure
        """
        use_cases = []
        
        # Handle empty data
        if not all_data:
            return {
                'use_cases': [],
                'metadata': self.get_metadata()
            }
        
        # Extract endpoints
        endpoints = all_data.get('endpoints', [])
        files = all_data.get('files', [])
        complexity_by_file = all_data.get('complexity_by_file', {})
        
        # Group endpoints by controller/domain
        endpoint_groups = {}
        for endpoint in endpoints:
            if isinstance(endpoint, dict):
                path = endpoint.get('path', '')
            else:
                path = endpoint
            
            # Extract controller from path (e.g., /api/auth/login -> auth)
            parts = path.split('/')
            controller = parts[2] if len(parts) > 2 else 'general'
            
            if controller not in endpoint_groups:
                endpoint_groups[controller] = {
                    'endpoints': [],
                    'files': [],
                    'methods': [],
                    'complexity': 0
                }
            
            endpoint_groups[controller]['endpoints'].append(endpoint)
        
        # Match files to controllers and generate use cases
        for controller, group_data in endpoint_groups.items():
            # Find matching files
            matching_files = [f for f in files if controller.lower() in f.lower()]
            group_data['files'] = matching_files[:3]  # Limit to 3 most relevant
            
            # Extract methods (simplified - would use AST in production)
            group_data['methods'] = [controller + 'Method']
            
            # Get complexity
            if matching_files:
                group_data['complexity'] = complexity_by_file.get(matching_files[0], 0)
            
            # Generate use case
            use_case = self.generate_use_case(group_data)
            use_cases.append(use_case)
        
        return {
            'use_cases': use_cases,
            'metadata': self.get_metadata()
        }
