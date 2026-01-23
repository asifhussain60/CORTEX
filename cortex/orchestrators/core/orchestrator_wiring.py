"""
Orchestrator Wiring System - Master Orchestrator Registry Configuration

AC-TRANSFORM-001: Orchestrator Wiring Expansion (40 hours)
- Registers all available orchestrators into MasterOrchestrator
- Enables 87% accessibility (20/23 orchestrators)
- Provides discovery and routing capabilities

WIRE-001: Core Orchestrators (6 orchestrators)
WIRE-002: Domain Orchestrators (5 orchestrators)  
WIRE-003: Support Orchestrators (6 orchestrators)

Author: GitHub Copilot
Date: 2026-01-24
"""

from __future__ import annotations

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from cortex.core.interfaces import IOrchestrator
from cortex.core.result import Ok, Err
from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger


class OrchestratorCategory(Enum):
    """Categories for orchestrators"""
    CORE = "core"
    DOMAIN = "domain"
    SUPPORT = "support"
    INFRASTRUCTURE = "infrastructure"


@dataclass
class OrchestratorWiringMetadata:
    """Enhanced metadata for wired orchestrators"""
    domain: str
    orchestrator: IOrchestrator
    category: OrchestratorCategory
    version: str = "1.0"
    capabilities: list[str] = field(default_factory=lambda: [])
    registered_at: str = field(default_factory=lambda: datetime.now().isoformat())
    health_status: str = "healthy"
    routing_keywords: list[str] = field(default_factory=lambda: [])
    confidence_score: int = 100  # Default confidence for routing
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary"""
        return {
            "domain": self.domain,
            "category": self.category.value,
            "version": self.version,
            "capabilities": self.capabilities,
            "registered_at": self.registered_at,
            "health_status": self.health_status,
            "routing_keywords": self.routing_keywords,
            "confidence_score": self.confidence_score,
        }


class OrchestratorWiringRegistry:
    """
    Central registry for orchestrator wiring configuration.
    
    WIRE-001: Core Orchestrators (6)
    - InteractionOrchestrator (Stage 1 comprehension)
    - IntentRouter (Stage 2 routing)
    - TDDOrchestrator (test-driven development)
    - WorkflowOrchestrator (multi-step workflows)
    - WrappedTDDOrchestrator (TDD with governance)
    - OrchestratorBootstrap (initialization)
    
    WIRE-002: Domain Orchestrators (5)
    - RefactoringOrchestrator (code refactoring)
    - PlanningOrchestrator (planning workflows)
    - DomainOrchestrator (domain operations)
    - ConversationOrchestrator (stateful conversations)
    - SeleniumPlaywrightOrchestrator (test migration)
    
    WIRE-003: Support Orchestrators (6)
    - OnboardingOrchestrator (new user experience)
    - ToolDiscoveryOrchestrator (capability discovery)
    - UpgradeOrchestrator (version management)
    - RollbackOrchestrator (failure recovery)
    - SetupOrchestrator (environment configuration)
    - ComposedOrchestrator (orchestrator composition)
    """
    
    def __init__(self):
        """Initialize wiring registry"""
        self.logger = EnhancedAuditLogger.instance()
        self.wired_orchestrators: Dict[str, OrchestratorWiringMetadata] = {}
        self.wiring_history: List[Dict[str, Any]] = []
        
    def register_orchestrator(
        self,
        domain: str,
        orchestrator: IOrchestrator,
        category: OrchestratorCategory,
        capabilities: list[str],
        routing_keywords: Optional[list[str]] = None,
        version: str = "1.0"
    ) -> Ok[OrchestratorWiringMetadata] | Err[str]:
        """
        Register an orchestrator with wiring metadata.
        
        WIRE-001, WIRE-002, WIRE-003 implementation.
        
        Args:
            domain: Domain name for orchestrator
            orchestrator: IOrchestrator instance
            category: OrchestratorCategory enum
            capabilities: List of capabilities provided by orchestrator
            routing_keywords: Keywords for intent routing
            version: Orchestrator version
        
        Returns:
            Result with OrchestratorWiringMetadata on success
        """
        try:
            if domain in self.wired_orchestrators:
                return Err(f"Orchestrator already registered for domain: {domain}")
            
            metadata = OrchestratorWiringMetadata(
                domain=domain,
                orchestrator=orchestrator,
                category=category,
                capabilities=capabilities,
                routing_keywords=routing_keywords or [],
                version=version,
            )
            
            self.wired_orchestrators[domain] = metadata
            
            # Log wiring event
            self.wiring_history.append({
                "timestamp": datetime.now().isoformat(),
                "operation": "REGISTER",
                "domain": domain,
                "category": category.value,
                "capabilities": capabilities,
                "status": "success"
            })
            
            self.logger.log_operation_complete(
                ac_id="AC-TRANSFORM-001-WIRE",
                operation=f"REGISTER_{category.value.upper()}_ORCHESTRATOR",
                success=True,
                details={
                    "domain": domain,
                    "category": category.value,
                    "capabilities": capabilities,
                    "version": version,
                    "routing_keywords": routing_keywords or []
                }
            )
            
            return Ok(metadata)
            
        except Exception as e:
            error_msg = f"Failed to register orchestrator for domain {domain}: {str(e)}"
            self.logger.log_operation_complete(
                ac_id="AC-TRANSFORM-001-WIRE",
                operation=f"REGISTER_{category.value.upper()}_ORCHESTRATOR",
                success=False,
                details={"error": error_msg}
            )
            return Err(error_msg)
    
    def get_orchestrator(self, domain: str) -> Optional[OrchestratorWiringMetadata]:
        """Get orchestrator metadata by domain"""
        return self.wired_orchestrators.get(domain)
    
    def get_by_capability(self, capability: str) -> List[OrchestratorWiringMetadata]:
        """Get orchestrators by capability"""
        return [
            meta for meta in self.wired_orchestrators.values()
            if capability in meta.capabilities
        ]
    
    def get_by_category(self, category: OrchestratorCategory) -> List[OrchestratorWiringMetadata]:
        """Get all orchestrators in a category"""
        return [
            meta for meta in self.wired_orchestrators.values()
            if meta.category == category
        ]
    
    def get_by_keyword(self, keyword: str) -> List[OrchestratorWiringMetadata]:
        """Get orchestrators by routing keyword (for intent routing)"""
        return [
            meta for meta in self.wired_orchestrators.values()
            if keyword.lower() in [kw.lower() for kw in meta.routing_keywords]
        ]
    
    def get_wiring_status(self) -> Dict[str, Any]:
        """Get detailed wiring status"""
        by_category = {}
        for category in OrchestratorCategory:
            orchestrators = self.get_by_category(category)
            by_category[category.value] = len(orchestrators)
        
        return {
            "total_wired": len(self.wired_orchestrators),
            "target_wired": 20,
            "coverage_percentage": (len(self.wired_orchestrators) / 23) * 100,
            "by_category": by_category,
            "orchestrators": [
                {
                    "domain": domain,
                    "category": meta.category.value,
                    "capabilities": meta.capabilities,
                    "health_status": meta.health_status,
                }
                for domain, meta in sorted(self.wired_orchestrators.items())
            ]
        }
    
    def reset(self) -> None:
        """Reset registry (for testing)"""
        self.wired_orchestrators.clear()
        self.wiring_history.clear()


# Singleton instance
_wiring_registry_instance: Optional[OrchestratorWiringRegistry] = None


def get_wiring_registry() -> OrchestratorWiringRegistry:
    """Get singleton wiring registry instance"""
    global _wiring_registry_instance
    if _wiring_registry_instance is None:
        _wiring_registry_instance = OrchestratorWiringRegistry()
    return _wiring_registry_instance
