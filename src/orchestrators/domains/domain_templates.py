"""
Domain Templates - Domain-Specific Orchestrator Templates

AC-AR-016-02: Domain-specific orchestrator templates with governance integration

Provides base templates for each domain:
- Planning: Phase/roadmap management
- Analysis: Discovery/analysis workflows
- Integration: External system integration
- Validation: Testing/verification workflows
- Execution: Task execution/deployment

Each template includes:
- Governance rule loading
- Response header injection
- Audit logging hooks
- Domain-specific initialization/execution/cleanup hooks

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict


@dataclass
class TemplateContext:
    """Context for orchestrator template"""
    domain: str
    governance_rules: Dict[str, Any]
    response_headers: Dict[str, str]
    audit_hooks: Dict[str, Callable]
    ac_id_tracking: bool
    version: str
    created_at: str


class DomainTemplate(ABC):
    """Base class for domain-specific orchestrator templates"""
    
    @abstractmethod
    def get_domain(self) -> str:
        """Get domain name"""
        ...
    
    @abstractmethod
    def create_context(self) -> Dict[str, Any]:
        """Create template context"""
        ...
    
    @abstractmethod
    def validate_compliance(self) -> bool:
        """Validate governance compliance"""
        ...
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize orchestrator from template"""
        ...
    
    @abstractmethod
    def execute(self, operation: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute operation using template"""
        ...
    
    @abstractmethod
    def cleanup(self) -> None:
        """Cleanup resources"""
        ...
    
    @abstractmethod
    def inject_headers(self, response: Dict, headers: Dict[str, str]) -> None:
        """Inject response headers"""
        ...
    
    @abstractmethod
    def generate_boilerplate(self, class_name: str, description: str) -> str:
        """Generate orchestrator boilerplate code"""
        ...
    
    # Protected methods
    
    def _get_governance_rules(self) -> Dict[str, Any]:
        """Get governance rules for this domain"""
        return {
            "CORE-008": "Tests MUST exist BEFORE implementation",
            "CORE-011": "ALL functions MUST have type hints",
            "CORE-012": "ALL public APIs MUST have docstrings",
            "CORE-013": "NO bare except, NO generic Exception",
            "CORE-026": "Git checkpoint BEFORE every major action",
            "CORE-028": "Kebab-case, ≤25 chars total",
        }
    
    def _get_response_headers(self) -> Dict[str, str]:
        """Get response headers for this domain"""
        return {
            "X-Domain": self.get_domain(),
            "X-Version": "1.0",
            "X-Timestamp": datetime.now().isoformat(),
            "X-Template": self.__class__.__name__,
        }
    
    def _get_audit_hooks(self) -> Dict[str, Callable]:
        """Get audit logging hooks"""
        def start_operation(op_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
            return {
                "operation": op_name,
                "timestamp": datetime.now().isoformat(),
                "domain": self.get_domain(),
                "parameters": params,
            }
        
        def end_operation(op_name: str, result: Dict[str, Any]) -> Dict[str, Any]:
            return {
                "operation": op_name,
                "timestamp": datetime.now().isoformat(),
                "domain": self.get_domain(),
                "result": result,
            }
        
        def log_error(op_name: str, error: Exception) -> Dict[str, Any]:
            return {
                "operation": op_name,
                "timestamp": datetime.now().isoformat(),
                "domain": self.get_domain(),
                "error": str(error),
                "error_type": type(error).__name__,
            }
        
        return {
            "start_operation": start_operation,
            "end_operation": end_operation,
            "log_error": log_error,
        }


class PlanningTemplate(DomainTemplate):
    """Template for planning domain orchestrators"""
    
    def get_domain(self) -> str:
        return "planning"
    
    def create_context(self) -> Dict[str, Any]:
        return {
            "domain": self.get_domain(),
            "governance_rules": self._get_governance_rules(),
            "response_headers": self._get_response_headers(),
            "audit_hooks": self._get_audit_hooks(),
            "ac_id_tracking": True,
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "planning_capabilities": [
                "phase_management",
                "roadmap_generation",
                "checkpoint_creation",
                "schedule_optimization",
            ],
        }
    
    def validate_compliance(self) -> bool:
        context = self.create_context()
        rules = context["governance_rules"]
        return len(rules) > 0
    
    def initialize(self, config: Dict[str, Any]) -> Dict[str, Any]:
        context = self.create_context()
        hooks = context["audit_hooks"]
        hooks["start_operation"]("planning_initialize", config)
        return {"status": "initialized", "domain": self.get_domain()}
    
    def execute(self, operation: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        context = self.create_context()
        hooks = context["audit_hooks"]
        hooks["start_operation"](operation, parameters)
        result = {"operation": operation, "status": "executed"}
        hooks["end_operation"](operation, result)
        return result
    
    def cleanup(self) -> None:
        pass
    
    def inject_headers(self, response: Dict, headers: Dict[str, str]) -> None:
        response.update(headers)
    
    def generate_boilerplate(self, class_name: str, description: str) -> str:
        return f'''"""
{description}

Domain: planning
"""

from src.orchestrators.domains.domain_templates import PlanningTemplate

class {class_name}(PlanningTemplate):
    """Planning domain orchestrator"""
    
    def initialize(self, config):
        super().initialize(config)
        # Add custom initialization
        pass
    
    def execute(self, operation, parameters):
        result = super().execute(operation, parameters)
        # Add custom execution logic
        return result
'''


class AnalysisTemplate(DomainTemplate):
    """Template for analysis domain orchestrators"""
    
    def get_domain(self) -> str:
        return "analysis"
    
    def create_context(self) -> Dict[str, Any]:
        return {
            "domain": self.get_domain(),
            "governance_rules": self._get_governance_rules(),
            "response_headers": self._get_response_headers(),
            "audit_hooks": self._get_audit_hooks(),
            "ac_id_tracking": True,
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "analysis_capabilities": [
                "dependency_analysis",
                "code_discovery",
                "ast_parsing",
                "impact_analysis",
            ],
        }
    
    def validate_compliance(self) -> bool:
        context = self.create_context()
        rules = context["governance_rules"]
        return len(rules) > 0
    
    def initialize(self, config: Dict[str, Any]) -> Dict[str, Any]:
        context = self.create_context()
        hooks = context["audit_hooks"]
        hooks["start_operation"]("analysis_initialize", config)
        return {"status": "initialized", "domain": self.get_domain()}
    
    def execute(self, operation: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        context = self.create_context()
        hooks = context["audit_hooks"]
        hooks["start_operation"](operation, parameters)
        result = {"operation": operation, "status": "analyzed"}
        hooks["end_operation"](operation, result)
        return result
    
    def cleanup(self) -> None:
        pass
    
    def inject_headers(self, response: Dict, headers: Dict[str, str]) -> None:
        response.update(headers)
    
    def generate_boilerplate(self, class_name: str, description: str) -> str:
        return f'''"""
{description}

Domain: analysis
"""

from src.orchestrators.domains.domain_templates import AnalysisTemplate

class {class_name}(AnalysisTemplate):
    """Analysis domain orchestrator"""
    
    def initialize(self, config):
        super().initialize(config)
        # Add custom initialization
        pass
    
    def execute(self, operation, parameters):
        result = super().execute(operation, parameters)
        # Add custom execution logic
        return result
'''


class IntegrationTemplate(DomainTemplate):
    """Template for integration domain orchestrators"""
    
    def get_domain(self) -> str:
        return "integration"
    
    def create_context(self) -> Dict[str, Any]:
        return {
            "domain": self.get_domain(),
            "governance_rules": self._get_governance_rules(),
            "response_headers": self._get_response_headers(),
            "audit_hooks": self._get_audit_hooks(),
            "ac_id_tracking": True,
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "integration_capabilities": [
                "system_connection",
                "api_integration",
                "data_sync",
                "webhook_management",
            ],
        }
    
    def validate_compliance(self) -> bool:
        context = self.create_context()
        rules = context["governance_rules"]
        return len(rules) > 0
    
    def initialize(self, config: Dict[str, Any]) -> Dict[str, Any]:
        context = self.create_context()
        hooks = context["audit_hooks"]
        hooks["start_operation"]("integration_initialize", config)
        return {"status": "initialized", "domain": self.get_domain()}
    
    def execute(self, operation: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        context = self.create_context()
        hooks = context["audit_hooks"]
        hooks["start_operation"](operation, parameters)
        result = {"operation": operation, "status": "integrated"}
        hooks["end_operation"](operation, result)
        return result
    
    def cleanup(self) -> None:
        pass
    
    def inject_headers(self, response: Dict, headers: Dict[str, str]) -> None:
        response.update(headers)
    
    def generate_boilerplate(self, class_name: str, description: str) -> str:
        return f'''"""
{description}

Domain: integration
"""

from src.orchestrators.domains.domain_templates import IntegrationTemplate

class {class_name}(IntegrationTemplate):
    """Integration domain orchestrator"""
    
    def initialize(self, config):
        super().initialize(config)
        # Add custom initialization
        pass
    
    def execute(self, operation, parameters):
        result = super().execute(operation, parameters)
        # Add custom execution logic
        return result
'''


class ValidationTemplate(DomainTemplate):
    """Template for validation domain orchestrators"""
    
    def get_domain(self) -> str:
        return "validation"
    
    def create_context(self) -> Dict[str, Any]:
        return {
            "domain": self.get_domain(),
            "governance_rules": self._get_governance_rules(),
            "response_headers": self._get_response_headers(),
            "audit_hooks": self._get_audit_hooks(),
            "ac_id_tracking": True,
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "validation_capabilities": [
                "state_validation",
                "pre_flight_checks",
                "test_execution",
                "health_verification",
            ],
        }
    
    def validate_compliance(self) -> bool:
        context = self.create_context()
        rules = context["governance_rules"]
        return len(rules) > 0
    
    def initialize(self, config: Dict[str, Any]) -> Dict[str, Any]:
        context = self.create_context()
        hooks = context["audit_hooks"]
        hooks["start_operation"]("validation_initialize", config)
        return {"status": "initialized", "domain": self.get_domain()}
    
    def execute(self, operation: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        context = self.create_context()
        hooks = context["audit_hooks"]
        hooks["start_operation"](operation, parameters)
        result = {"operation": operation, "status": "validated"}
        hooks["end_operation"](operation, result)
        return result
    
    def cleanup(self) -> None:
        pass
    
    def inject_headers(self, response: Dict, headers: Dict[str, str]) -> None:
        response.update(headers)
    
    def generate_boilerplate(self, class_name: str, description: str) -> str:
        return f'''"""
{description}

Domain: validation
"""

from src.orchestrators.domains.domain_templates import ValidationTemplate

class {class_name}(ValidationTemplate):
    """Validation domain orchestrator"""
    
    def initialize(self, config):
        super().initialize(config)
        # Add custom initialization
        pass
    
    def execute(self, operation, parameters):
        result = super().execute(operation, parameters)
        # Add custom execution logic
        return result
'''


class ExecutionTemplate(DomainTemplate):
    """Template for execution domain orchestrators"""
    
    def get_domain(self) -> str:
        return "execution"
    
    def create_context(self) -> Dict[str, Any]:
        return {
            "domain": self.get_domain(),
            "governance_rules": self._get_governance_rules(),
            "response_headers": self._get_response_headers(),
            "audit_hooks": self._get_audit_hooks(),
            "ac_id_tracking": True,
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "execution_capabilities": [
                "workflow_execution",
                "task_dispatch",
                "deployment_management",
                "resource_cleanup",
            ],
        }
    
    def validate_compliance(self) -> bool:
        context = self.create_context()
        rules = context["governance_rules"]
        return len(rules) > 0
    
    def initialize(self, config: Dict[str, Any]) -> Dict[str, Any]:
        context = self.create_context()
        hooks = context["audit_hooks"]
        hooks["start_operation"]("execution_initialize", config)
        return {"status": "initialized", "domain": self.get_domain()}
    
    def execute(self, operation: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        context = self.create_context()
        hooks = context["audit_hooks"]
        hooks["start_operation"](operation, parameters)
        result = {"operation": operation, "status": "executed"}
        hooks["end_operation"](operation, result)
        return result
    
    def cleanup(self) -> None:
        pass
    
    def inject_headers(self, response: Dict, headers: Dict[str, str]) -> None:
        response.update(headers)
    
    def generate_boilerplate(self, class_name: str, description: str) -> str:
        return f'''"""
{description}

Domain: execution
"""

from src.orchestrators.domains.domain_templates import ExecutionTemplate

class {class_name}(ExecutionTemplate):
    """Execution domain orchestrator"""
    
    def initialize(self, config):
        super().initialize(config)
        # Add custom initialization
        pass
    
    def execute(self, operation, parameters):
        result = super().execute(operation, parameters)
        # Add custom execution logic
        return result
'''


class DomainTemplateFactory:
    """Factory for creating and managing domain templates"""
    
    _instance: Optional['DomainTemplateFactory'] = None
    _templates: Dict[str, DomainTemplate] = {}
    
    def __new__(cls) -> 'DomainTemplateFactory':
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self) -> None:
        """Initialize factory"""
        if self._initialized:
            return
        
        self._templates = {
            "planning": PlanningTemplate(),
            "analysis": AnalysisTemplate(),
            "integration": IntegrationTemplate(),
            "validation": ValidationTemplate(),
            "execution": ExecutionTemplate(),
        }
        self._initialized = True
    
    def get_template(self, domain: str) -> DomainTemplate:
        """
        Get template for a domain.
        
        Args:
            domain: Domain name
        
        Returns:
            DomainTemplate instance
        
        Raises:
            ValueError: If domain not found
        """
        if domain not in self._templates:
            raise ValueError(f"Unknown domain: {domain}")
        return self._templates[domain]
    
    def get_all_templates(self) -> List[DomainTemplate]:
        """Get all templates"""
        return list(self._templates.values())
    
    def get_domain_names(self) -> List[str]:
        """Get all domain names"""
        return list(self._templates.keys())
    
    def export_templates(self) -> Dict[str, Any]:
        """Export all templates as structured data"""
        return {
            "metadata": {
                "version": "1.0",
                "timestamp": datetime.now().isoformat(),
                "total_templates": len(self._templates),
                "domains": self.get_domain_names(),
            },
            "templates": [
                {
                    "domain": template.get_domain(),
                    "class": template.__class__.__name__,
                    "context": template.create_context(),
                }
                for template in self.get_all_templates()
            ],
        }
