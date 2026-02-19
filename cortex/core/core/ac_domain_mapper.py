"""
AC-to-Domain Mapping Loader & Query Engine

Provides bidirectional lookup between Acceptance Criteria (ACs) and orchestrator domains.
Enables orchestrators to query which ACs they're responsible for, and supports
planning queries like "which orchestrator handles this AC?"
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import yaml

logger = logging.getLogger(__name__)


class DomainType(Enum):
    """Orchestrator domain types."""
    TDD = "tdd"
    PLANNING = "planning"
    ADO = "ado"
    INTERACTION = "interaction"


@dataclass
class ACMetadata:
    """Metadata about a single AC."""
    ac_id: str
    title: str
    description: str
    domain: str
    categories: List[str] = field(default_factory=list)
    severity: str = "MEDIUM"

    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            'ac_id': self.ac_id,
            'title': self.title,
            'description': self.description,
            'domain': self.domain,
            'categories': self.categories,
            'severity': self.severity,
        }


@dataclass
class DomainMetadata:
    """Metadata for a domain."""
    domain_id: str
    domain_name: str
    orchestrator: str
    tier_access: List[int]
    ac_count: int
    primary_rules: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            'domain_id': self.domain_id,
            'domain_name': self.domain_name,
            'orchestrator': self.orchestrator,
            'tier_access': self.tier_access,
            'ac_count': self.ac_count,
            'primary_rules': self.primary_rules,
        }


class ACDomainRegistry:
    """
    Central registry for AC-to-domain mappings.

    Provides:
    - ac_to_domain lookup (fast O(1) query)
    - domain_acs lookup (get all ACs for a domain)
    - orchestrator_acs lookup (get all ACs for an orchestrator)
    - category_acs lookup (get all ACs in a category)
    - statistics and analytics
    """

    _instance = None

    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize registry (only once)."""
        if self._initialized:
            return

        self.ac_to_domain: Dict[str, str] = {}
        self.domain_acs: Dict[str, List[ACMetadata]] = {}
        self.orchestrator_acs: Dict[str, List[ACMetadata]] = {}
        self.category_acs: Dict[str, List[ACMetadata]] = {}
        self.domain_metadata: Dict[str, DomainMetadata] = {}
        self.ac_metadata: Dict[str, ACMetadata] = {}
        self.all_categories: Set[str] = set()
        self._initialized = True

        logger.info("ACDomainRegistry initialized")

    def register_ac(self, ac_metadata: ACMetadata) -> None:
        """Register an AC with its domain."""
        self.ac_to_domain[ac_metadata.ac_id] = ac_metadata.domain
        self.ac_metadata[ac_metadata.ac_id] = ac_metadata

        # Index by domain
        if ac_metadata.domain not in self.domain_acs:
            self.domain_acs[ac_metadata.domain] = []
        self.domain_acs[ac_metadata.domain].append(ac_metadata)

        # Index by category
        for category in ac_metadata.categories:
            self.all_categories.add(category)
            if category not in self.category_acs:
                self.category_acs[category] = []
            self.category_acs[category].append(ac_metadata)

    def register_domain(self, domain_metadata: DomainMetadata) -> None:
        """Register domain metadata."""
        self.domain_metadata[domain_metadata.domain_id] = domain_metadata

        # Index by orchestrator
        if domain_metadata.orchestrator not in self.orchestrator_acs:
            self.orchestrator_acs[domain_metadata.orchestrator] = []

    def get_domain_for_ac(self, ac_id: str) -> Optional[str]:
        """
        Get the domain responsible for an AC.

        Args:
            ac_id: The AC-ID to look up

        Returns:
            Domain ID (e.g., 'tdd'), or None if not found
        """
        return self.ac_to_domain.get(ac_id)

    def get_acs_for_domain(self, domain_id: str) -> List[ACMetadata]:
        """
        Get all ACs assigned to a domain.

        Args:
            domain_id: The domain to query

        Returns:
            List of ACMetadata objects for that domain
        """
        return self.domain_acs.get(domain_id, [])

    def get_orchestrator_for_ac(self, ac_id: str) -> Optional[str]:
        """
        Get the orchestrator responsible for an AC.

        Args:
            ac_id: The AC-ID to look up

        Returns:
            Orchestrator class name (e.g., 'TDDOrchestrator'), or None if not found
        """
        domain = self.get_domain_for_ac(ac_id)
        if domain and domain in self.domain_metadata:
            return self.domain_metadata[domain].orchestrator
        return None

    def get_acs_for_orchestrator(self, orchestrator_name: str) -> List[ACMetadata]:
        """
        Get all ACs assigned to an orchestrator.

        Args:
            orchestrator_name: The orchestrator to query (e.g., 'TDDOrchestrator')

        Returns:
            List of ACMetadata objects for that orchestrator
        """
        # Find domain for this orchestrator
        for domain_id, metadata in self.domain_metadata.items():
            if metadata.orchestrator == orchestrator_name:
                return self.get_acs_for_domain(domain_id)
        return []

    def get_acs_for_category(self, category: str) -> List[ACMetadata]:
        """
        Get all ACs in a category.

        Args:
            category: The category to query

        Returns:
            List of ACMetadata objects in that category
        """
        return self.category_acs.get(category, [])

    def get_ac_metadata(self, ac_id: str) -> Optional[ACMetadata]:
        """
        Get metadata for a specific AC.

        Args:
            ac_id: The AC-ID to look up

        Returns:
            ACMetadata object, or None if not found
        """
        return self.ac_metadata.get(ac_id)

    def get_domain_metadata(self, domain_id: str) -> Optional[DomainMetadata]:
        """
        Get metadata for a domain.

        Args:
            domain_id: The domain to query

        Returns:
            DomainMetadata object, or None if not found
        """
        return self.domain_metadata.get(domain_id)

    def count_acs_for_domain(self, domain_id: str) -> int:
        """
        Count ACs assigned to a domain.

        Args:
            domain_id: The domain to query

        Returns:
            Number of ACs in that domain
        """
        return len(self.domain_acs.get(domain_id, []))

    def get_all_domains(self) -> List[str]:
        """Get list of all registered domains."""
        return list(self.domain_metadata.keys())

    def get_all_orchestrators(self) -> List[str]:
        """Get list of all registered orchestrators."""
        return list(self.orchestrator_acs.keys())

    def get_all_categories(self) -> List[str]:
        """Get list of all registered categories."""
        return sorted(list(self.all_categories))

    def get_domain_summary(self, domain_id: str) -> Dict:
        """
        Get comprehensive summary for a domain.

        Args:
            domain_id: The domain to summarize

        Returns:
            Dictionary with domain info and AC counts
        """
        metadata = self.get_domain_metadata(domain_id)
        acs = self.get_acs_for_domain(domain_id)
        categories = {}

        for ac in acs:
            for cat in ac.categories:
                categories[cat] = categories.get(cat, 0) + 1

        return {
            'domain': domain_id,
            'orchestrator': metadata.orchestrator if metadata else None,
            'ac_count': len(acs),
            'tier_access': metadata.tier_access if metadata else [],
            'categories': categories,
        }

    def get_statistics(self) -> Dict:
        """
        Get comprehensive statistics about all mappings.

        Returns:
            Dictionary with statistics
        """
        total_acs = len(self.ac_metadata)
        total_domains = len(self.domain_metadata)
        total_categories = len(self.all_categories)

        domain_breakdown = {}
        for domain_id in self.domain_metadata.keys():
            count = self.count_acs_for_domain(domain_id)
            domain_breakdown[domain_id] = {
                'ac_count': count,
                'percentage': (count / total_acs * 100) if total_acs > 0 else 0,
            }

        return {
            'total_acs': total_acs,
            'total_domains': total_domains,
            'total_categories': total_categories,
            'domains': domain_breakdown,
            'categories': {cat: len(self.category_acs.get(cat, [])) for cat in self.all_categories},
        }


class ACDomainLoader:
    """Loads AC-to-domain mappings from YAML file."""

    def __init__(self, tier1_path: Path):
        """
        Initialize loader.

        Args:
            tier1_path: Path to tier1 directory
        """
        self.tier1_path = Path(tier1_path)
        self.mappings_file = self.tier1_path / 'acceptance-criteria' / 'ac-domain-mappings.yaml'

    def load_mappings(self) -> ACDomainRegistry:
        """
        Load AC-to-domain mappings from YAML file.

        Returns:
            Populated ACDomainRegistry instance

        Raises:
            FileNotFoundError: If mappings file not found
            yaml.YAMLError: If YAML parsing fails
        """
        if not self.mappings_file.exists():
            raise FileNotFoundError(f"Mappings file not found: {self.mappings_file}")

        try:
            with open(self.mappings_file, 'r') as f:
                content = yaml.safe_load(f)
        except yaml.YAMLError as e:
            logger.error(f"YAML parsing error in {self.mappings_file}: {e}")
            return ACDomainRegistry()

        registry = ACDomainRegistry()

        # Register domains and their ACs
        if 'domains' in content:
            for domain_id, domain_data in content['domains'].items():
                # Register domain metadata
                metadata = DomainMetadata(
                    domain_id=domain_id,
                    domain_name=domain_data.get('domain_name', ''),
                    orchestrator=domain_data.get('orchestrator', ''),
                    tier_access=domain_data.get('tier_access', []),
                    ac_count=domain_data.get('ac_count', 0),
                    primary_rules=domain_data.get('primary_rules', []),
                )
                registry.register_domain(metadata)

                # Register all ACs for this domain
                if 'acceptance_criteria' in domain_data:
                    for ac_data in domain_data['acceptance_criteria']:
                        ac_metadata = ACMetadata(
                            ac_id=ac_data.get('ac_id', ''),
                            title=ac_data.get('title', ''),
                            description=ac_data.get('description', ''),
                            domain=domain_id,
                            categories=ac_data.get('categories', []),
                            severity=ac_data.get('severity', 'MEDIUM'),
                        )
                        registry.register_ac(ac_metadata)

        logger.info(f"Loaded {len(registry.ac_metadata)} ACs across {len(registry.domain_metadata)} domains")
        return registry


class ACDomainPopulator:
    """High-level interface for AC-to-domain mapping population."""

    def __init__(self, tier1_path: Path):
        """
        Initialize populator.

        Args:
            tier1_path: Path to tier1 directory
        """
        self.tier1_path = Path(tier1_path)
        self.loader = ACDomainLoader(tier1_path)
        self._registry = None

    def populate(self) -> ACDomainRegistry:
        """
        Populate AC-to-domain registry.

        Returns:
            Populated ACDomainRegistry
        """
        self._registry = self.loader.load_mappings()
        return self._registry

    def get_registry(self) -> ACDomainRegistry:
        """
        Get the populated registry.

        Returns:
            ACDomainRegistry instance

        Raises:
            RuntimeError: If populate() not called first
        """
        if self._registry is None:
            raise RuntimeError("Registry not populated. Call populate() first.")
        return self._registry

    def get_populated_domains(self) -> List[str]:
        """Get list of populated domains."""
        if self._registry is None:
            return []
        return self._registry.get_all_domains()

    def get_mappings_summary(self) -> Dict:
        """Get summary of loaded mappings."""
        if self._registry is None:
            return {}
        return self._registry.get_statistics()

    def query_domain_for_ac(self, ac_id: str) -> Optional[str]:
        """Query which domain handles an AC."""
        if self._registry is None:
            return None
        return self._registry.get_domain_for_ac(ac_id)

    def query_orchestrator_for_ac(self, ac_id: str) -> Optional[str]:
        """Query which orchestrator handles an AC."""
        if self._registry is None:
            return None
        return self._registry.get_orchestrator_for_ac(ac_id)

    def query_acs_for_domain(self, domain_id: str) -> List[ACMetadata]:
        """Query all ACs for a domain."""
        if self._registry is None:
            return []
        return self._registry.get_acs_for_domain(domain_id)

    def query_acs_for_orchestrator(self, orchestrator_name: str) -> List[ACMetadata]:
        """Query all ACs for an orchestrator."""
        if self._registry is None:
            return []
        return self._registry.get_acs_for_orchestrator(orchestrator_name)
