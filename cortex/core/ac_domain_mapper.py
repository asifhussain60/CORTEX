"""COMPAT shim — cortex.core.ac_domain_mapper → cortex.core.core.ac_domain_mapper.

Phase 58: Canonical implementation lives in cortex/core/core/ac_domain_mapper.py.
This stub is kept for import-path compatibility.
"""
# noqa: F401
from cortex.core.core.ac_domain_mapper import DomainType, ACMetadata, DomainMetadata, ACDomainRegistry, ACDomainLoader, ACDomainPopulator

__all__ = ["DomainType", "ACMetadata", "DomainMetadata", "ACDomainRegistry", "ACDomainLoader", "ACDomainPopulator"]
