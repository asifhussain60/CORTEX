"""
Brain Tier Populator (AC-AR-013-01)

Loads domain-specific governance rules from Tier 0 YAML files
and populates the governance system.

This module implements:
- TierContentLoader: Loads YAML from tier folders
- DomainRuleRegistry: Manages domain-specific SKULL rules
- BrainPopulator: Orchestrates loading of all tiers
"""

import os
import yaml
import logging
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class DomainRule:
    """Represents a domain-specific governance rule"""
    rule_id: str
    domain: str
    category: str
    severity: str
    name: str
    description: str
    validation_criteria: List[str]
    enforcement_mode: str = "STRICT"
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert rule to dictionary"""
        return {
            "rule_id": self.rule_id,
            "domain": self.domain,
            "category": self.category,
            "severity": self.severity,
            "name": self.name,
            "description": self.description,
            "validation_criteria": self.validation_criteria,
            "enforcement_mode": self.enforcement_mode,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class DomainOrchestratorRequirements:
    """Orchestrator requirements for a domain"""
    orchestrator_id: str
    tier_access: Set[int]
    required_rules: List[str]
    mcp_tools: List[str]
    capabilities: List[str]
    performance_sla: Dict[str, int]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert requirements to dictionary"""
        return {
            "orchestrator_id": self.orchestrator_id,
            "tier_access": sorted(list(self.tier_access)),
            "required_rules": self.required_rules,
            "mcp_tools": self.mcp_tools,
            "capabilities": self.capabilities,
            "performance_sla": self.performance_sla,
        }


class TierContentLoader:
    """Loads YAML content from tier-specific folders"""
    
    def __init__(self, cortex_brain_path: str):
        """
        Initialize loader.
        
        Args:
            cortex_brain_path: Path to cortex_brain folder
        """
        self.cortex_brain_path = Path(cortex_brain_path)
        self.logger = logging.getLogger(f"{__name__}.TierContentLoader")
    
    def load_tier_yaml_file(self, tier: int, filename: str) -> Optional[Dict[str, Any]]:
        """
        Load a YAML file from tier folder.
        
        Args:
            tier: Tier number (0, 1, 2, 3)
            filename: Filename to load (e.g., "tdd-rules.yaml")
        
        Returns:
            Parsed YAML content or None if not found
        """
        file_path = self.cortex_brain_path / f"tier{tier}" / "governance" / filename
        
        if not file_path.exists():
            self.logger.warning(f"File not found: {file_path}")
            return None
        
        try:
            with open(file_path, 'r') as f:
                content = yaml.safe_load(f)
                self.logger.info(f"Loaded: {file_path}")
                return content
        except Exception as e:
            self.logger.error(f"Failed to load {file_path}: {e}")
            return None
    
    def load_all_tier_files(self, tier: int) -> Dict[str, Dict[str, Any]]:
        """
        Load all YAML files from tier folder.
        
        Args:
            tier: Tier number (0, 1, 2, 3)
        
        Returns:
            Dictionary of {filename: content}
        """
        tier_path = self.cortex_brain_path / f"tier{tier}" / "governance"
        files = {}
        
        if not tier_path.exists():
            self.logger.warning(f"Tier path not found: {tier_path}")
            return files
        
        for yaml_file in tier_path.glob("*.yaml"):
            if yaml_file.name.startswith("."):
                continue
            
            content = self.load_tier_yaml_file(tier, yaml_file.name)
            if content:
                files[yaml_file.name] = content
        
        return files


class DomainRuleRegistry:
    """Central registry for domain-specific governance rules"""
    
    def __init__(self):
        """Initialize registry"""
        self.rules: Dict[str, DomainRule] = {}
        self.by_domain: Dict[str, List[str]] = {}
        self.by_category: Dict[str, List[str]] = {}
        self.orch_requirements: Dict[str, DomainOrchestratorRequirements] = {}
        self.logger = logging.getLogger(f"{__name__}.DomainRuleRegistry")
    
    def register_rule(self, rule: DomainRule) -> bool:
        """
        Register a domain rule.
        
        Args:
            rule: DomainRule to register
        
        Returns:
            True if registered, False if duplicate
        """
        if rule.rule_id in self.rules:
            self.logger.warning(f"Rule already registered: {rule.rule_id}")
            return False
        
        self.rules[rule.rule_id] = rule
        
        # Index by domain
        if rule.domain not in self.by_domain:
            self.by_domain[rule.domain] = []
        self.by_domain[rule.domain].append(rule.rule_id)
        
        # Index by category
        if rule.category not in self.by_category:
            self.by_category[rule.category] = []
        self.by_category[rule.category].append(rule.rule_id)
        
        self.logger.debug(f"Registered rule: {rule.rule_id}")
        return True
    
    def register_orchestrator_requirements(
        self,
        domain: str,
        requirements: DomainOrchestratorRequirements
    ) -> bool:
        """
        Register orchestrator requirements for a domain.
        
        Args:
            domain: Domain name
            requirements: DomainOrchestratorRequirements
        
        Returns:
            True if registered
        """
        key = f"{domain}_orchestrator"
        if key in self.orch_requirements:
            self.logger.warning(f"Requirements already registered: {key}")
            return False
        
        self.orch_requirements[key] = requirements
        self.logger.debug(f"Registered orchestrator requirements: {key}")
        return True
    
    def get_rules_for_domain(self, domain: str) -> List[DomainRule]:
        """Get all rules for a domain"""
        rule_ids = self.by_domain.get(domain, [])
        return [self.rules[rid] for rid in rule_ids if rid in self.rules]
    
    def get_orchestrator_requirements(self, domain: str) -> Optional[DomainOrchestratorRequirements]:
        """Get orchestrator requirements for domain"""
        key = f"{domain}_orchestrator"
        return self.orch_requirements.get(key)
    
    def get_rules_by_category(self, category: str) -> List[DomainRule]:
        """Get all rules for a category"""
        rule_ids = self.by_category.get(category, [])
        return [self.rules[rid] for rid in rule_ids if rid in self.rules]
    
    def get_rule(self, rule_id: str) -> Optional[DomainRule]:
        """Get a specific rule by ID"""
        return self.rules.get(rule_id)
    
    def count_rules(self) -> int:
        """Get total rule count"""
        return len(self.rules)
    
    def get_domain_summary(self) -> Dict[str, int]:
        """Get rule count per domain"""
        return {domain: len(rules) for domain, rules in self.by_domain.items()}


class BrainPopulator:
    """Populates brain tiers with governance content"""
    
    def __init__(self, cortex_brain_path: str):
        """
        Initialize populator.
        
        Args:
            cortex_brain_path: Path to cortex_brain folder
        """
        self.loader = TierContentLoader(cortex_brain_path)
        self.registry = DomainRuleRegistry()
        self.logger = logging.getLogger(f"{__name__}.BrainPopulator")
    
    def populate_tier0_domain_rules(self) -> int:
        """
        Load domain rules from Tier 0.
        
        Returns:
            Number of rules loaded
        """
        self.logger.info("Loading Tier 0 domain rules...")
        
        # Load all YAML files from tier0/governance
        files = self.loader.load_all_tier_files(0)
        
        rules_loaded = 0
        
        for filename, content in files.items():
            if filename == "core-rules.yaml":
                # Skip core rules (handled separately)
                continue
            
            if "rules" not in content:
                self.logger.warning(f"No 'rules' section in {filename}")
                continue
            
            domain = content.get("domain", "unknown")
            
            # Parse rules
            for rule_data in content["rules"]:
                try:
                    rule = DomainRule(
                        rule_id=rule_data["rule_id"],
                        domain=domain,
                        category=rule_data.get("category", "general"),
                        severity=rule_data.get("severity", "high"),
                        name=rule_data.get("name", ""),
                        description=rule_data.get("description", ""),
                        validation_criteria=rule_data.get("validation", []),
                        enforcement_mode=content.get("enforcement_mode", "STRICT"),
                    )
                    
                    if self.registry.register_rule(rule):
                        rules_loaded += 1
                
                except Exception as e:
                    self.logger.error(f"Failed to parse rule from {filename}: {e}")
            
            # Parse orchestrator requirements
            orch_key = list(content.keys())
            orch_key = [k for k in orch_key if k.endswith("_orchestrator_requirements")]
            
            if orch_key:
                req_data = content[orch_key[0]]
                try:
                    requirements = DomainOrchestratorRequirements(
                        orchestrator_id=req_data.get("id", domain),
                        tier_access=set(req_data.get("tier_access", [])),
                        required_rules=req_data.get("required_rules", []),
                        mcp_tools=req_data.get("mcp_tools", []),
                        capabilities=req_data.get("capabilities", []),
                        performance_sla=req_data.get("performance_sla", {}),
                    )
                    
                    self.registry.register_orchestrator_requirements(domain, requirements)
                
                except Exception as e:
                    self.logger.error(f"Failed to parse orchestrator requirements from {filename}: {e}")
        
        self.logger.info(f"Loaded {rules_loaded} Tier 0 domain rules")
        return rules_loaded
    
    def get_registry(self) -> DomainRuleRegistry:
        """Get the domain rule registry"""
        return self.registry
    
    def get_populated_domains(self) -> List[str]:
        """Get list of populated domains"""
        return list(self.registry.by_domain.keys())
    
    def get_rules_summary(self) -> Dict[str, Any]:
        """Get summary of loaded rules"""
        summary = self.registry.get_domain_summary()
        
        return {
            "total_rules": self.registry.count_rules(),
            "domains": list(summary.keys()),
            "rules_by_domain": summary,
            "categories": list(self.registry.by_category.keys()),
            "orchestrator_requirements": len(self.registry.orch_requirements),
        }
