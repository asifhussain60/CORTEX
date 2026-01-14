"""
Company Brain Plugin System for CORTEX MCP.

Provides company-specific brain isolation, domain plugin architecture,
and cross-company coordination.

Author: Asif Hussain
Version: 1.0.0
Created: 2026-01-08
Correlation ID: FEAT06-P3
"""

import logging
import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from abc import ABC, abstractmethod


logger = logging.getLogger("cortex.mcp.company_brain")


@dataclass
class CompanyBrain:
    """Company brain metadata."""
    company: str
    path: Path
    brain_path: Path
    domain: str
    plugins: List[str] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)


class CompanyBrainRegistry:
    """
    Company brain registration and discovery system.
    
    Discovers and manages multiple company-specific CORTEX brains.
    """
    
    def __init__(self, workspace_root: Optional[Path] = None):
        self.workspace_root = Path(workspace_root) if workspace_root else Path.cwd()
        self.brains: List[CompanyBrain] = []
        logger.info(f"CompanyBrainRegistry initialized for {self.workspace_root}")
    
    def discover(self):
        """Discover all company brains in workspace."""
        from src.mcp.multi_repo_manager import RepoDiscovery
        
        discovery = RepoDiscovery(self.workspace_root)
        repos = discovery.discover_repos(max_depth=2)
        
        for repo in repos:
            if repo.is_cortex_enabled and "company" in repo.config:
                brain = CompanyBrain(
                    company=repo.config.get("company", repo.name),
                    path=repo.path,
                    brain_path=repo.brain_path,
                    domain=repo.config.get("domain", "general"),
                    plugins=repo.config.get("plugins", []),
                    config=repo.config
                )
                self.brains.append(brain)
                logger.info(f"Discovered company brain: {brain.company} (domain: {brain.domain})")
        
        logger.info(f"Discovered {len(self.brains)} company brains")
    
    def list_brains(self) -> List[CompanyBrain]:
        """List all discovered company brains."""
        return self.brains
    
    def get_brain(self, company: str) -> Optional[CompanyBrain]:
        """
        Get company brain by company name.
        
        Args:
            company: Company name
            
        Returns:
            CompanyBrain or None if not found
        """
        return next((b for b in self.brains if b.company == company), None)
    
    def filter_by_domain(self, domain: str) -> List[CompanyBrain]:
        """
        Filter brains by domain.
        
        Args:
            domain: Domain name
            
        Returns:
            List of brains in the specified domain
        """
        return [b for b in self.brains if b.domain == domain]


class DomainPlugin(ABC):
    """
    Base class for domain-specific plugins.
    
    Subclass this to create custom domain plugins.
    """
    
    name: str = "base_plugin"
    domain: str = "general"
    version: str = "1.0.0"
    
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute plugin with context.
        
        Args:
            context: Execution context
            
        Returns:
            Plugin execution result
        """
        pass
    
    def validate(self, context: Dict[str, Any]) -> bool:
        """
        Validate context before execution.
        
        Args:
            context: Execution context
            
        Returns:
            True if valid
        """
        return True


class DomainPluginManager:
    """
    Domain plugin loading and execution manager.
    
    Manages domain-specific plugins for company brains.
    """
    
    def __init__(self, workspace_root: Optional[Path] = None):
        self.workspace_root = Path(workspace_root) if workspace_root else Path.cwd()
        self.plugins: Dict[str, DomainPlugin] = {}
        self.plugins_by_domain: Dict[str, List[DomainPlugin]] = {}
        logger.info("DomainPluginManager initialized")
    
    def initialize(self):
        """Initialize plugin manager."""
        logger.info("DomainPluginManager initialization complete")
    
    def register_plugin(self, plugin: DomainPlugin):
        """
        Register a domain plugin.
        
        Args:
            plugin: DomainPlugin instance
        """
        self.plugins[plugin.name] = plugin
        
        # Add to domain index
        if plugin.domain not in self.plugins_by_domain:
            self.plugins_by_domain[plugin.domain] = []
        self.plugins_by_domain[plugin.domain].append(plugin)
        
        logger.info(f"Registered plugin: {plugin.name} (domain: {plugin.domain})")
    
    def get_plugins_for_domain(self, domain: str) -> List[DomainPlugin]:
        """
        Get all plugins for a domain.
        
        Args:
            domain: Domain name
            
        Returns:
            List of plugins for the domain
        """
        return self.plugins_by_domain.get(domain, [])
    
    def execute_plugin(
        self,
        plugin_name: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a plugin.
        
        Args:
            plugin_name: Name of plugin to execute
            context: Execution context
            
        Returns:
            Plugin execution result
            
        Raises:
            ValueError: If plugin not found or validation fails
        """
        plugin = self.plugins.get(plugin_name)
        if not plugin:
            raise ValueError(f"Plugin not found: {plugin_name}")
        
        if not plugin.validate(context):
            raise ValueError(f"Plugin validation failed: {plugin_name}")
        
        logger.info(f"Executing plugin: {plugin_name}")
        return plugin.execute(context)


@dataclass
class BrainIsolationContext:
    """Isolation context for company brain."""
    company: str
    domain: str
    brain_path: Path
    is_isolated: bool = True


class BrainIsolation:
    """
    Company brain isolation system.
    
    Ensures operations in one company brain don't affect others.
    """
    
    def __init__(self, workspace_root: Optional[Path] = None):
        self.workspace_root = Path(workspace_root) if workspace_root else Path.cwd()
        self.registry: Optional[CompanyBrainRegistry] = None
        self.brain_contexts: Dict[str, BrainIsolationContext] = {}
        logger.info("BrainIsolation initialized")
    
    def initialize(self):
        """Initialize and discover company brains."""
        self.registry = CompanyBrainRegistry(self.workspace_root)
        self.registry.discover()
        logger.info(f"BrainIsolation initialized with {len(self.registry.brains)} brains")
    
    def create_brain_context(self, company: str) -> BrainIsolationContext:
        """
        Create isolation context for company brain.
        
        Args:
            company: Company name
            
        Returns:
            BrainIsolationContext
            
        Raises:
            ValueError: If brain not found
        """
        brain = self.registry.get_brain(company)
        if not brain:
            raise ValueError(f"Company brain not found: {company}")
        
        context = BrainIsolationContext(
            company=brain.company,
            domain=brain.domain,
            brain_path=brain.brain_path
        )
        
        self.brain_contexts[company] = context
        return context
    
    def execute_in_brain(
        self,
        company: str,
        operation: Callable[[BrainIsolationContext], Any]
    ) -> Any:
        """
        Execute operation in isolated brain context.
        
        Args:
            company: Company name
            operation: Callable to execute with context
            
        Returns:
            Operation result
        """
        context = self.create_brain_context(company)
        return operation(context)
    
    def get_brain_env(self, company: str) -> Dict[str, str]:
        """
        Get isolated environment variables for brain.
        
        Args:
            company: Company name
            
        Returns:
            Environment dictionary
        """
        brain = self.registry.get_brain(company)
        if not brain:
            raise ValueError(f"Company brain not found: {company}")
        
        env = os.environ.copy()
        env["CORTEX_COMPANY"] = brain.company
        env["CORTEX_DOMAIN"] = brain.domain
        env["CORTEX_BRAIN_PATH"] = str(brain.brain_path)
        
        return env


# Convenience function for getting global registry
_registry: Optional[CompanyBrainRegistry] = None


def get_company_brain_registry(workspace_root: Optional[Path] = None) -> CompanyBrainRegistry:
    """Get global CompanyBrainRegistry instance."""
    global _registry
    if _registry is None:
        _registry = CompanyBrainRegistry(workspace_root)
        _registry.discover()
    return _registry
