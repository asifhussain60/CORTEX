"""
CompanyDomainLoader - Dynamic YAML domain knowledge loader.

Loads company-specific domain knowledge from company/domains/**/*.yaml at runtime.
Provides domain-specific patterns, compliance standards, and best practices to orchestrators.

AC-ID: AC-LENS-V2-COMPANY-DOMAIN-001
Authority: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import logging
import yaml

logger = logging.getLogger(__name__)


@dataclass
class DomainKnowledge:
    """Domain knowledge from YAML file."""
    domain_name: str
    file_path: str
    data: Dict[str, Any] = field(default_factory=dict)
    version: Optional[str] = None
    description: Optional[str] = None


@dataclass
class CompanyDomainResult:
    """Result of company domain loading."""
    success: bool
    domains_loaded: List[DomainKnowledge] = field(default_factory=list)
    total_files: int = 0
    error: str = ""
    load_time_ms: float = 0.0


class CompanyDomainLoader:
    """
    Dynamic loader for company domain knowledge YAMLs.
    
    Scans company/domains/**/*.yaml and loads domain-specific:
    - Compliance standards (PCI-DSS, HIPAA, SOC2, etc.)
    - Coding patterns and anti-patterns
    - Architecture guidelines
    - Security policies
    - Testing strategies
    
    Example:
        >>> loader = CompanyDomainLoader()
        >>> result = loader.load_all_domains()
        >>> print(f"Loaded {len(result.domains_loaded)} domains")
        >>> 
        >>> # Get specific domain
        >>> pci_domain = loader.get_domain("pci-dss")
        >>> if pci_domain:
        ...     print(f"PCI-DSS rules: {pci_domain.data.get('rules', [])}")
    """
    
    def __init__(self, company_domains_path: Optional[Path] = None):
        """
        Initialize CompanyDomainLoader.
        
        Args:
            company_domains_path: Path to company/domains directory
                                  (defaults to ./company/domains)
        """
        self.company_domains_path = company_domains_path or Path("company/domains")
        self._domains_cache: Dict[str, DomainKnowledge] = {}
    
    def load_all_domains(self, force_reload: bool = False) -> CompanyDomainResult:
        """
        Load all domain YAMLs from company/domains/**/*.yaml.
        
        Args:
            force_reload: Force reload even if cached
        
        Returns:
            CompanyDomainResult with loaded domains and metadata
        
        Example:
            >>> loader = CompanyDomainLoader()
            >>> result = loader.load_all_domains()
            >>> for domain in result.domains_loaded:
            ...     print(f"{domain.domain_name}: {domain.description}")
        """
        import time
        start_time = time.time()
        
        # Return cached if available
        if self._domains_cache and not force_reload:
            return CompanyDomainResult(
                success=True,
                domains_loaded=list(self._domains_cache.values()),
                total_files=len(self._domains_cache),
                load_time_ms=0.0  # From cache
            )
        
        result = CompanyDomainResult(success=True)
        
        try:
            if not self.company_domains_path.exists():
                return CompanyDomainResult(
                    success=False,
                    error=f"Company domains path not found: {self.company_domains_path}"
                )
            
            # Find all YAML files
            yaml_files = list(self.company_domains_path.rglob("*.yaml")) + \
                        list(self.company_domains_path.rglob("*.yml"))
            
            result.total_files = len(yaml_files)
            
            for yaml_file in yaml_files:
                try:
                    domain_knowledge = self._load_domain_file(yaml_file)
                    if domain_knowledge:
                        result.domains_loaded.append(domain_knowledge)
                        # Cache by domain name
                        self._domains_cache[domain_knowledge.domain_name] = domain_knowledge
                
                except Exception as e:
                    logger.warning(f"Failed to load domain file {yaml_file}: {e}")
                    continue
            
            result.load_time_ms = (time.time() - start_time) * 1000
            
        except Exception as e:
            logger.error(f"Domain loading failed: {e}", exc_info=True)
            result.success = False
            result.error = str(e)
        
        return result
    
    def get_domain(self, domain_name: str) -> Optional[DomainKnowledge]:
        """
        Get specific domain by name.
        
        Args:
            domain_name: Domain name (e.g., "pci-dss", "hipaa", "solid-principles")
        
        Returns:
            DomainKnowledge if found, None otherwise
        
        Example:
            >>> loader = CompanyDomainLoader()
            >>> loader.load_all_domains()
            >>> pci = loader.get_domain("pci-dss")
            >>> if pci:
            ...     print(f"PCI rules: {len(pci.data.get('rules', []))}")
        """
        # Load if not already loaded
        if not self._domains_cache:
            self.load_all_domains()
        
        return self._domains_cache.get(domain_name)
    
    def get_domains_by_category(self, category: str) -> List[DomainKnowledge]:
        """
        Get all domains matching a category.
        
        Args:
            category: Category name (e.g., "compliance", "security", "architecture")
        
        Returns:
            List of DomainKnowledge objects matching category
        
        Example:
            >>> loader = CompanyDomainLoader()
            >>> loader.load_all_domains()
            >>> compliance_domains = loader.get_domains_by_category("compliance")
            >>> print(f"Found {len(compliance_domains)} compliance domains")
        """
        if not self._domains_cache:
            self.load_all_domains()
        
        matching_domains = []
        for domain in self._domains_cache.values():
            domain_category = domain.data.get("category", "")
            if category.lower() in domain_category.lower():
                matching_domains.append(domain)
        
        return matching_domains
    
    def search_domains(self, query: str) -> List[DomainKnowledge]:
        """
        Search domains by name or description.
        
        Args:
            query: Search query string
        
        Returns:
            List of matching DomainKnowledge objects
        
        Example:
            >>> loader = CompanyDomainLoader()
            >>> loader.load_all_domains()
            >>> results = loader.search_domains("security")
            >>> for domain in results:
            ...     print(f"Found: {domain.domain_name}")
        """
        if not self._domains_cache:
            self.load_all_domains()
        
        query_lower = query.lower()
        matching_domains = []
        
        for domain in self._domains_cache.values():
            # Search in name
            if query_lower in domain.domain_name.lower():
                matching_domains.append(domain)
                continue
            
            # Search in description
            if domain.description and query_lower in domain.description.lower():
                matching_domains.append(domain)
                continue
            
            # Search in data keys/values (shallow)
            for key, value in domain.data.items():
                if query_lower in str(key).lower() or query_lower in str(value).lower():
                    matching_domains.append(domain)
                    break
        
        return matching_domains
    
    def get_all_domain_names(self) -> List[str]:
        """
        Get list of all loaded domain names.
        
        Returns:
            List of domain names
        
        Example:
            >>> loader = CompanyDomainLoader()
            >>> loader.load_all_domains()
            >>> names = loader.get_all_domain_names()
            >>> print(f"Available domains: {', '.join(names)}")
        """
        if not self._domains_cache:
            self.load_all_domains()
        
        return sorted(self._domains_cache.keys())
    
    def reload_domain(self, domain_name: str) -> Optional[DomainKnowledge]:
        """
        Reload a specific domain from disk.
        
        Args:
            domain_name: Domain name to reload
        
        Returns:
            Updated DomainKnowledge if successful, None otherwise
        
        Example:
            >>> loader = CompanyDomainLoader()
            >>> loader.load_all_domains()
            >>> # ... domain file was updated ...
            >>> updated = loader.reload_domain("pci-dss")
            >>> print(f"Reloaded: {updated.domain_name}")
        """
        # Find the file path from cache
        if domain_name in self._domains_cache:
            file_path = Path(self._domains_cache[domain_name].file_path)
            if file_path.exists():
                domain_knowledge = self._load_domain_file(file_path)
                if domain_knowledge:
                    self._domains_cache[domain_name] = domain_knowledge
                    return domain_knowledge
        
        return None
    
    def _load_domain_file(self, yaml_file: Path) -> Optional[DomainKnowledge]:
        """Load a single domain YAML file."""
        try:
            content = yaml_file.read_text(encoding="utf-8")
            data = yaml.safe_load(content)
            
            if not data:
                return None
            
            # Extract domain name from file path or data
            domain_name = data.get("domain_name") or yaml_file.stem
            version = data.get("version")
            description = data.get("description", "")
            
            return DomainKnowledge(
                domain_name=domain_name,
                file_path=str(yaml_file),
                data=data,
                version=version,
                description=description
            )
        
        except yaml.YAMLError as e:
            logger.error(f"YAML parse error in {yaml_file}: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to load {yaml_file}: {e}")
            return None


# Singleton instance
_company_domain_loader = None


def get_company_domain_loader(company_domains_path: Optional[Path] = None) -> CompanyDomainLoader:
    """Get or create singleton CompanyDomainLoader instance."""
    global _company_domain_loader
    if _company_domain_loader is None:
        _company_domain_loader = CompanyDomainLoader(company_domains_path=company_domains_path)
    return _company_domain_loader
