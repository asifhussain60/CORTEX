"""Template content library with use-cases, domains, and workflows."""

from typing import Any, Dict, List, Optional


class TemplateLibrary:
    """Manages comprehensive template library with hierarchical organization.
    
    Provides templates organized by:
    - Use-cases (API integration, monitoring, etc.)
    - Domains (Finance, Healthcare, E-commerce)
    - Workflows (Sequential, Parallel, Conditional patterns)
    """

    def __init__(self) -> None:
        """Initialize template library with predefined templates."""
        self.use_case_templates = self._init_use_case_templates()
        self.domain_templates = self._init_domain_templates()
        self.workflow_templates = self._init_workflow_templates()

    def _init_use_case_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize use-case templates."""
        return {
            "api_integration": {
                "name": "api_integration",
                "category": "use_case",
                "title": "API Integration",
                "content": """API Integration Template
{{ endpoint }}: Endpoint URL
{{ method }}: HTTP Method
{{ auth }}: Authentication Type
{{ payload }}: Request Payload
{{ timeout }}: Timeout in seconds""",
                "description": "Template for integrating with external APIs",
                "examples": [
                    {"description": "REST API call", "parameters": {"endpoint": "https://api.example.com/users", "method": "GET"}},
                    {"description": "GraphQL query", "parameters": {"endpoint": "https://graphql.example.com", "method": "POST"}}
                ],
                "documentation": "See examples for common integration patterns"
            },
            "workflow_orchestration": {
                "name": "workflow_orchestration",
                "category": "use_case",
                "title": "Workflow Orchestration",
                "content": "Workflow: {{ name }}\nSteps: {% for step in steps %}{{ step }} {% endfor %}",
                "description": "Template for orchestrating multi-step workflows"
            },
            "monitoring": {
                "name": "monitoring",
                "category": "use_case",
                "title": "Monitoring Setup",
                "content": "Monitor: {{ metric }}\nThreshold: {{ threshold }}\nAlert: {{ alert }}",
                "description": "Template for monitoring and alerting"
            },
            "data_pipeline": {
                "name": "data_pipeline",
                "category": "use_case",
                "title": "Data Pipeline",
                "content": "Pipeline: {{ name }}\nSource: {{ source }}\nTransforms: {% for t in transforms %}{{ t }} {% endfor %}",
                "description": "Template for ETL/data processing pipelines"
            },
            "event_handling": {
                "name": "event_handling",
                "category": "use_case",
                "title": "Event Handler",
                "content": "Event: {{ event_type }}\nHandler: {{ handler }}\nRetry: {{ retry_policy }}",
                "description": "Template for event-driven architecture"
            },
            "state_management": {
                "name": "state_management",
                "category": "use_case",
                "title": "State Manager",
                "content": "State: {{ name }}\nType: {{ type }}\nPersistence: {{ persistence }}",
                "description": "Template for managing application state"
            },
            "cache_strategy": {
                "name": "cache_strategy",
                "category": "use_case",
                "title": "Caching",
                "content": "Cache: {{ strategy }}\nTTL: {{ ttl }}\nInvalidation: {{ invalidation }}",
                "description": "Template for caching strategies"
            },
            "security_policy": {
                "name": "security_policy",
                "category": "use_case",
                "title": "Security Policy",
                "content": "Policy: {{ name }}\nRules: {% for rule in rules %}{{ rule }} {% endfor %}",
                "description": "Template for security and access control"
            },
            "error_handling": {
                "name": "error_handling",
                "category": "use_case",
                "title": "Error Handler",
                "content": "Error Type: {{ type }}\nRetry: {{ retry }}\nFallback: {{ fallback }}",
                "description": "Template for error handling strategies"
            },
            "logging": {
                "name": "logging",
                "category": "use_case",
                "title": "Logging",
                "content": "Logger: {{ name }}\nLevel: {{ level }}\nDestination: {{ destination }}",
                "description": "Template for logging configuration"
            },
            "performance_optimization": {
                "name": "performance_optimization",
                "category": "use_case",
                "title": "Performance Optimization",
                "content": "Metric: {{ metric }}\nTarget: {{ target }}\nStrategy: {{ strategy }}",
                "description": "Template for performance tuning"
            },
            "notification": {
                "name": "notification",
                "category": "use_case",
                "title": "Notifications",
                "content": "Channel: {{ channel }}\nTemplate: {{ template }}\nRecipients: {{ recipients }}",
                "description": "Template for notification systems"
            },
            "report_generation": {
                "name": "report_generation",
                "category": "use_case",
                "title": "Report Generation",
                "content": "Report: {{ name }}\nFormat: {{ format }}\nSchedule: {{ schedule }}",
                "description": "Template for automated reporting"
            },
            "testing": {
                "name": "testing",
                "category": "use_case",
                "title": "Testing",
                "content": "Test Suite: {{ name }}\nType: {{ type }}\nCoverage: {{ coverage }}",
                "description": "Template for test configuration"
            },
            "deployment": {
                "name": "deployment",
                "category": "use_case",
                "title": "Deployment",
                "content": "Service: {{ name }}\nEnvironment: {{ env }}\nRollout: {{ strategy }}",
                "description": "Template for deployment processes"
            },
            "configuration": {
                "name": "configuration",
                "category": "use_case",
                "title": "Configuration",
                "content": "Config: {{ name }}\nValues: {{ values }}\nEnvironment: {{ env }}",
                "description": "Template for configuration management"
            },
            "database_schema": {
                "name": "database_schema",
                "category": "use_case",
                "title": "Database Schema",
                "content": "Table: {{ name }}\nColumns: {% for col in columns %}{{ col }} {% endfor %}",
                "description": "Template for database design"
            },
            "integration_test": {
                "name": "integration_test",
                "category": "use_case",
                "title": "Integration Testing",
                "content": "Test: {{ name }}\nServices: {% for svc in services %}{{ svc }} {% endfor %}",
                "description": "Template for integration tests"
            },
            "migration": {
                "name": "migration",
                "category": "use_case",
                "title": "Data Migration",
                "content": "From: {{ source }}\nTo: {{ target }}\nStrategy: {{ strategy }}",
                "description": "Template for data migrations"
            },
            "compliance": {
                "name": "compliance",
                "category": "use_case",
                "title": "Compliance",
                "content": "Standard: {{ standard }}\nChecks: {% for check in checks %}{{ check }} {% endfor %}",
                "description": "Template for compliance verification"
            },
            "documentation": {
                "name": "documentation",
                "category": "use_case",
                "title": "Documentation",
                "content": "Title: {{ title }}\nSections: {% for section in sections %}{{ section }} {% endfor %}",
                "description": "Template for API and system documentation"
            }
        }

    def _init_domain_templates(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """Initialize domain-specific templates."""
        return {
            "finance": {f"finance_template_{i}": {"name": f"finance_template_{i}", "domain": "finance", "description": f"Finance template {i}"} for i in range(10)},
            "healthcare": {f"healthcare_template_{i}": {"name": f"healthcare_template_{i}", "domain": "healthcare", "description": f"Healthcare template {i}"} for i in range(10)},
            "ecommerce": {f"ecommerce_template_{i}": {"name": f"ecommerce_template_{i}", "domain": "ecommerce", "description": f"E-commerce template {i}"} for i in range(10)}
        }

    def _init_workflow_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize workflow pattern templates."""
        return {
            "sequential": {
                "name": "sequential",
                "category": "workflow",
                "title": "Sequential Workflow",
                "content": "Sequential steps: {% for step in steps %}{{ step }} → {% endfor %}",
                "description": "Template for sequential execution pattern"
            },
            "parallel": {
                "name": "parallel",
                "category": "workflow",
                "title": "Parallel Workflow",
                "content": "Parallel execution: {% for task in tasks %}{{ task }} (async) {% endfor %}",
                "description": "Template for parallel execution pattern"
            },
            "conditional": {
                "name": "conditional",
                "category": "workflow",
                "title": "Conditional Workflow",
                "content": "{% if condition %}{{ true_path }}{% else %}{{ false_path }}{% endif %}",
                "description": "Template for conditional branching"
            },
            "loop": {
                "name": "loop",
                "category": "workflow",
                "title": "Loop Pattern",
                "content": "{% for item in items %}Process: {{ item }}{% endfor %}",
                "description": "Template for iterative pattern"
            },
            "retry": {
                "name": "retry",
                "category": "workflow",
                "title": "Retry Pattern",
                "content": "Retry: {{ max_retries }} times, backoff: {{ backoff }}",
                "description": "Template for retry with backoff"
            },
            "fan_out_fan_in": {
                "name": "fan_out_fan_in",
                "category": "workflow",
                "title": "Fan-out/Fan-in",
                "content": "Fan-out: {% for task in tasks %}{{ task }} {% endfor %}\nFan-in: aggregate results",
                "description": "Template for scatter-gather pattern"
            },
            "try_catch": {
                "name": "try_catch",
                "category": "workflow",
                "title": "Try-Catch Pattern",
                "content": "Try: {{ operation }}\nCatch: {{ error_handler }}\nFinally: {{ cleanup }}",
                "description": "Template for exception handling"
            },
            "timeout": {
                "name": "timeout",
                "category": "workflow",
                "title": "Timeout Pattern",
                "content": "Operation: {{ operation }}\nTimeout: {{ timeout_seconds }}s",
                "description": "Template for timeout handling"
            },
            "circuit_breaker": {
                "name": "circuit_breaker",
                "category": "workflow",
                "title": "Circuit Breaker",
                "content": "Service: {{ service }}\nThreshold: {{ threshold }}\nFallback: {{ fallback }}",
                "description": "Template for circuit breaker pattern"
            },
            "queue": {
                "name": "queue",
                "category": "workflow",
                "title": "Queue Pattern",
                "content": "Queue: {{ name }}\nConsumers: {{ consumer_count }}\nRetry: {{ retry_policy }}",
                "description": "Template for queue-based processing"
            },
            "saga": {
                "name": "saga",
                "category": "workflow",
                "title": "Saga Pattern",
                "content": "Saga: {% for step in steps %}{{ step }} with compensate: {{ step }}_undo {% endfor %}",
                "description": "Template for distributed transaction"
            },
            "deadletter": {
                "name": "deadletter",
                "category": "workflow",
                "title": "Dead Letter Queue",
                "content": "Failed messages → {{ dlq_name }}\nProcessing: {{ processor }}",
                "description": "Template for handling failed messages"
            },
            "pipeline": {
                "name": "pipeline",
                "category": "workflow",
                "title": "Pipeline Pattern",
                "content": "Input → {% for stage in stages %}{{ stage }} → {% endfor %}Output",
                "description": "Template for pipeline/chain pattern"
            },
            "bulkhead": {
                "name": "bulkhead",
                "category": "workflow",
                "title": "Bulkhead Pattern",
                "content": "Thread Pool: {{ pool_name }}\nSize: {{ pool_size }}\nQueue: {{ queue_size }}",
                "description": "Template for resource isolation"
            },
            "async_response": {
                "name": "async_response",
                "category": "workflow",
                "title": "Async Response",
                "content": "Request: {{ request_id }}\nPolling: {{ poll_interval }}\nCallback: {{ callback_url }}",
                "description": "Template for asynchronous response patterns"
            }
        }

    def get_template(
        self,
        category: str,
        template_id: str,
        domain: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Get template by category and ID.
        
        Args:
            category: Template category (use_case, domain, workflow)
            template_id: Template identifier
            domain: Domain name (for domain category)
            
        Returns:
            Template dictionary or None
        """
        if category == "use_case":
            return self.use_case_templates.get(template_id)
        elif category == "workflow":
            return self.workflow_templates.get(template_id)
        elif category == "domain" and domain:
            domain_templates = self.domain_templates.get(domain, {})
            return domain_templates.get(template_id)
        return None

    def get_template_by_id(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get template by full ID string."""
        # Try to find in any category
        if template_id in self.use_case_templates:
            return self.use_case_templates[template_id]
        elif template_id in self.workflow_templates:
            return self.workflow_templates[template_id]
        
        # Try domain templates
        for domain_dict in self.domain_templates.values():
            if template_id in domain_dict:
                return domain_dict[template_id]
        
        return None

    def list_templates(
        self,
        category: str,
        domain: Optional[str] = None
    ) -> List[str]:
        """List template IDs in a category.
        
        Args:
            category: Template category
            domain: Domain name (for domain category)
            
        Returns:
            List of template identifiers
        """
        if category == "use_case":
            return list(self.use_case_templates.keys())
        elif category == "workflow":
            return list(self.workflow_templates.keys())
        elif category == "domain" and domain:
            return list(self.domain_templates.get(domain, {}).keys())
        return []

    def list_domains(self) -> List[str]:
        """List available domains.
        
        Returns:
            List of domain names
        """
        return list(self.domain_templates.keys())

    def list_all_templates(self) -> List[str]:
        """List all template IDs across all categories.
        
        Returns:
            List of all template identifiers
        """
        all_ids = []
        all_ids.extend(self.use_case_templates.keys())
        all_ids.extend(self.workflow_templates.keys())
        for domain_dict in self.domain_templates.values():
            all_ids.extend(domain_dict.keys())
        return all_ids

    def get_related_templates(
        self,
        template: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get templates related to given template.
        
        Args:
            template: Template dictionary
            
        Returns:
            List of related templates
        """
        related = []
        category = template.get("category", "")
        
        if category == "use_case":
            # Find workflows that might be used with this use-case
            for workflow in self.workflow_templates.values():
                related.append(workflow)
        
        return related


class TemplateDiscovery:
    """Discovers and searches templates."""

    def __init__(self) -> None:
        """Initialize template discovery."""
        self.library = TemplateLibrary()

    def search(self, keyword: str) -> List[Dict[str, Any]]:
        """Search templates by keyword.
        
        Args:
            keyword: Search keyword
            
        Returns:
            List of matching templates
        """
        results = []
        keyword_lower = keyword.lower()
        
        all_templates = self.library.list_all_templates()
        for template_id in all_templates:
            template = self.library.get_template_by_id(template_id)
            if template:
                # Search in name, title, description
                search_text = f"{template.get('name', '')} {template.get('title', '')} {template.get('description', '')}".lower()
                if keyword_lower in search_text:
                    results.append({"id": template_id, "name": template.get("name"), "title": template.get("title")})
        
        return results

    def search_by_domain(self, domain: str) -> List[Dict[str, Any]]:
        """Search templates by domain.
        
        Args:
            domain: Domain name
            
        Returns:
            List of templates in domain
        """
        templates = self.library.list_templates("domain", domain)
        return [{"id": t, "domain": domain} for t in templates]

    def search_by_use_case(self, use_case_keyword: str) -> List[Dict[str, Any]]:
        """Search use-case templates by keyword.
        
        Args:
            use_case_keyword: Use-case search term
            
        Returns:
            List of matching use-case templates
        """
        return self.search(use_case_keyword)


class TemplateValidator:
    """Validates templates."""

    def validate_template(self, template: Dict[str, Any]) -> List[str]:
        """Validate template structure.
        
        Args:
            template: Template to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        required_fields = ["name", "content", "description"]
        for field in required_fields:
            if field not in template:
                errors.append(f"Missing required field: {field}")
        
        # Check content is not empty
        if template.get("content", "").strip() == "":
            errors.append("Template content cannot be empty")
        
        return errors

    def validate_example(self, example: Dict[str, Any]) -> List[str]:
        """Validate template example.
        
        Args:
            example: Example to validate
            
        Returns:
            List of validation errors
        """
        errors = []
        
        if "description" not in example and "parameters" not in example:
            errors.append("Example must have description or parameters")
        
        return errors
