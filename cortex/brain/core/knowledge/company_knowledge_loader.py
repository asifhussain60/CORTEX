# AC-ID: KN-005-01 - Company Knowledge Override Layer
"""
Company Knowledge Loader with Precedence Override (KN-005-01).

PHASE: 7.x - Knowledge Enhancement
AC-ID: KN-005-01 - Company Knowledge Override Implementation

This module provides company-specific knowledge loading with proper
precedence to ensure company policies override generic CORTEX knowledge.

Precedence Order (highest to lowest):
1. company/domains/{company-name}/compliance/  - Company-specific overrides
2. company/domains/compliance-standards/       - Generic industry standards
3. cortex_brain/tier3/knowledge/               - CORTEX base knowledge

Core Responsibilities:
1. Load company-specific knowledge YAMLs from company/domains/
2. Merge with CORTEX knowledge using deep merge strategy
3. Enforce precedence: higher layer overrides lower
4. Support lazy loading for performance
5. Detect applicable compliance standards from code context

Integration Points:
- KnowledgeRepository: Extended to query company knowledge
- SynthesisEngine: Uses merged knowledge for synthesis
- IntentRouter: Queries compliance standards during classification

CORE Governance:
  - CORE-008: TDD (tests first)
  - CORE-011: Type hints mandatory
  - CORE-012: Google-style docstrings
  - CORE-013: Specific exception handling
  - CORE-035: Single canonical implementation
"""

from __future__ import annotations

import logging
import re
import yaml
from dataclasses import dataclass, field
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


logger = logging.getLogger(__name__)


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class ComplianceMatch:
    """
    Represents a detected compliance standard match.
    
    Attributes:
        standard_id: Identifier of the compliance standard (e.g., 'pci-dss')
        confidence: Confidence score of the match (0.0 to 1.0)
        triggers: List of patterns that triggered the match
        source_path: Path to the compliance standard YAML
    """
    standard_id: str
    confidence: float
    triggers: List[str]
    source_path: str


@dataclass
class KnowledgeLayer:
    """
    Represents a layer in the knowledge precedence stack.
    
    Attributes:
        name: Layer name (e.g., 'company-override', 'compliance-standards', 'cortex-base')
        precedence: Priority level (1 = highest, 3 = lowest)
        path: Path to knowledge directory
        entries: Loaded knowledge entries
        loaded: Whether the layer has been loaded
    """
    name: str
    precedence: int
    path: Path
    entries: Dict[str, Any] = field(default_factory=dict)
    loaded: bool = False


@dataclass
class MergedKnowledgeResult:
    """
    Result of merging knowledge from multiple layers.
    
    Attributes:
        merged_content: The merged knowledge content
        source_layers: List of layers that contributed to the merge
        override_count: Number of overrides applied
        merge_timestamp: When the merge was performed
    """
    merged_content: Dict[str, Any]
    source_layers: List[str]
    override_count: int
    merge_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


# =============================================================================
# COMPLIANCE DETECTION PATTERNS
# =============================================================================

COMPLIANCE_PATTERNS: Dict[str, List[str]] = {
    "pci-dss": [
        r"payment|credit.?card|PAN|CVV|cardholder|card.?number",
        r"primary.?account.?number|magnetic.?stripe|track.?data",
    ],
    "pii-protection": [
        r"personal.?data|PII|privacy|consent|data.?subject",
        r"social.?security|SSN|date.?of.?birth|DOB",
    ],
    "hipaa": [
        r"health|medical|PHI|HIPAA|patient|healthcare",
        r"protected.?health|medical.?record|diagnosis",
    ],
    "hsa-fsa": [
        r"HSA|FSA|health.?savings|flexible.?spending",
        r"health.?account|medical.?expense|benefit.?account",
    ],
    "gdpr": [
        r"GDPR|european|EU.?resident|data.?protection",
        r"right.?to.?erasure|data.?portability|consent.?withdrawal",
    ],
    "ccpa": [
        r"CCPA|California|consumer.?privacy|opt.?out",
        r"do.?not.?sell|personal.?information.?sale",
    ],
    "financial-services": [
        r"SOX|financial.?report|internal.?control|audit.?trail",
        r"GLBA|financial.?privacy|PSD2|payment.?services",
    ],
    "soc2": [
        r"SOC.?2|trust.?service|security.?control|availability",
        r"processing.?integrity|confidentiality.?control",
    ],
    "iso27001": [
        r"ISO.?27001|ISMS|information.?security.?management",
        r"security.?objective|risk.?treatment|asset.?inventory",
    ],
    "nist-800-53": [
        r"NIST|800-53|federal.?security|security.?control",
        r"control.?family|baseline.?control",
    ],
    "fedramp": [
        r"FedRAMP|federal.?cloud|government.?cloud|ATO",
        r"authority.?to.?operate|federal.?agency",
    ],
    "wcag": [
        r"accessibility|WCAG|a11y|screen.?reader|assistive",
        r"perceivable|operable|understandable|robust",
    ],
}


# =============================================================================
# COMPANY KNOWLEDGE LOADER
# =============================================================================

class CompanyKnowledgeLoader:
    """
    Loader for company-specific knowledge with precedence override.
    
    Implements a 3-layer knowledge stack:
    1. Company-specific overrides (highest precedence)
    2. Industry compliance standards (medium precedence)
    3. CORTEX base knowledge (lowest precedence)
    
    Usage:
        loader = CompanyKnowledgeLoader(project_root="/path/to/project")
        
        # Get merged knowledge for a domain
        knowledge = loader.get_merged_knowledge("SECURITY")
        
        # Detect applicable compliance standards
        matches = loader.detect_compliance_standards(code_content)
        
        # Load company-specific override
        company_knowledge = loader.load_company_knowledge("acme-corp")
    
    CORE Governance:
      - CORE-011: Type hints - all methods typed
      - CORE-012: Docstrings - Google style
      - CORE-013: Specific exception handling
    """
    
    # Default paths (relative to project root)
    COMPANY_DOMAINS_PATH = "company/domains"
    COMPLIANCE_STANDARDS_PATH = "company/domains/compliance-standards"
    CORTEX_KNOWLEDGE_PATH = "cortex_brain/tier3/knowledge"
    
    def __init__(
        self,
        project_root: Optional[str] = None,
        company_name: Optional[str] = None,
    ) -> None:
        """
        Initialize the Company Knowledge Loader.
        
        Args:
            project_root: Path to project root (auto-detected if None)
            company_name: Active company name for company-specific overrides
        """
        self._project_root = self._resolve_project_root(project_root)
        self._company_name = company_name
        self._layers: Dict[str, KnowledgeLayer] = {}
        self._compliance_cache: Dict[str, Dict[str, Any]] = {}
        self._merged_cache: Dict[str, MergedKnowledgeResult] = {}
        
        self._initialize_layers()
        logger.info(f"CompanyKnowledgeLoader initialized (root: {self._project_root})")
    
    def _resolve_project_root(self, provided_root: Optional[str]) -> Path:
        """
        Resolve the project root directory.
        
        Args:
            provided_root: User-provided root path or None
            
        Returns:
            Path to project root
        """
        if provided_root:
            return Path(provided_root)
        
        # Auto-detect: walk up from this file's location
        current = Path(__file__).resolve()
        for parent in [current] + list(current.parents):
            if (parent / "cortex_brain").exists() or (parent / "cortex").exists():
                return parent
        
        # Fallback to current working directory
        return Path.cwd()
    
    def _initialize_layers(self) -> None:
        """Initialize the knowledge layer stack."""
        # Layer 1: Company-specific overrides (highest precedence)
        if self._company_name:
            company_path = self._project_root / self.COMPANY_DOMAINS_PATH / self._company_name
            self._layers["company-override"] = KnowledgeLayer(
                name="company-override",
                precedence=1,
                path=company_path,
            )
        
        # Layer 2: Industry compliance standards (medium precedence)
        compliance_path = self._project_root / self.COMPLIANCE_STANDARDS_PATH
        self._layers["compliance-standards"] = KnowledgeLayer(
            name="compliance-standards",
            precedence=2,
            path=compliance_path,
        )
        
        # Layer 3: CORTEX base knowledge (lowest precedence)
        cortex_path = self._project_root / self.CORTEX_KNOWLEDGE_PATH
        self._layers["cortex-base"] = KnowledgeLayer(
            name="cortex-base",
            precedence=3,
            path=cortex_path,
        )
    
    def set_company(self, company_name: str) -> None:
        """
        Set or change the active company for overrides.
        
        Args:
            company_name: Company name to activate
        """
        self._company_name = company_name
        company_path = self._project_root / self.COMPANY_DOMAINS_PATH / company_name
        self._layers["company-override"] = KnowledgeLayer(
            name="company-override",
            precedence=1,
            path=company_path,
        )
        # Clear merged cache when company changes
        self._merged_cache.clear()
        logger.info(f"Company set to: {company_name}")
    
    def detect_compliance_standards(
        self,
        content: str,
        min_confidence: float = 0.3,
    ) -> List[ComplianceMatch]:
        """
        Detect applicable compliance standards from code/text content.
        
        Args:
            content: Code or text content to analyze
            min_confidence: Minimum confidence threshold (0.0 to 1.0)
            
        Returns:
            List of ComplianceMatch objects sorted by confidence
        """
        matches: List[ComplianceMatch] = []
        content_lower = content.lower()
        
        for standard_id, patterns in COMPLIANCE_PATTERNS.items():
            triggers: List[str] = []
            match_count = 0
            
            for pattern in patterns:
                regex = re.compile(pattern, re.IGNORECASE)
                found = regex.findall(content_lower)
                if found:
                    triggers.extend(found[:3])  # Limit triggers per pattern
                    match_count += len(found)
            
            if triggers:
                # Calculate confidence based on match density
                confidence = min(match_count / 10.0, 1.0)
                
                # Boost confidence for multiple pattern matches
                unique_patterns = len(set(triggers))
                confidence += min(unique_patterns * 0.1, 0.3)
                confidence = min(confidence, 1.0)
                
                if confidence >= min_confidence:
                    source_path = str(
                        self._project_root / self.COMPLIANCE_STANDARDS_PATH / f"{standard_id}.yaml"
                    )
                    matches.append(ComplianceMatch(
                        standard_id=standard_id,
                        confidence=confidence,
                        triggers=list(set(triggers))[:5],  # Unique triggers
                        source_path=source_path,
                    ))
        
        # Sort by confidence descending
        matches.sort(key=lambda m: m.confidence, reverse=True)
        return matches
    
    def load_compliance_standard(
        self,
        standard_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Load a specific compliance standard YAML.
        
        Args:
            standard_id: The compliance standard identifier (e.g., 'pci-dss')
            
        Returns:
            Dict containing the compliance standard content, or None if not found
        """
        # Check cache first
        if standard_id in self._compliance_cache:
            return self._compliance_cache[standard_id]
        
        yaml_path = self._project_root / self.COMPLIANCE_STANDARDS_PATH / f"{standard_id}.yaml"
        
        if not yaml_path.exists():
            logger.warning(f"Compliance standard not found: {yaml_path}")
            return None
        
        try:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                content = yaml.safe_load(f) or {}
            
            self._compliance_cache[standard_id] = content
            logger.debug(f"Loaded compliance standard: {standard_id}")
            return content
            
        except yaml.YAMLError as e:
            logger.error(f"YAML parse error for {standard_id}: {e}")
            return None
    
    def load_company_knowledge(
        self,
        domain: str,
        company_name: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Load company-specific knowledge for a domain.
        
        Args:
            domain: Knowledge domain (e.g., 'compliance', 'policies')
            company_name: Company name (uses active company if None)
            
        Returns:
            Dict containing company knowledge, or None if not found
        """
        company = company_name or self._company_name
        if not company:
            return None
        
        company_path = self._project_root / self.COMPANY_DOMAINS_PATH / company / domain
        
        if not company_path.exists():
            return None
        
        knowledge: Dict[str, Any] = {}
        
        # Load all YAMLs in the domain directory
        for yaml_file in company_path.glob("*.yaml"):
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    content = yaml.safe_load(f) or {}
                
                # Use filename (without extension) as key
                key = yaml_file.stem
                knowledge[key] = content
                
            except yaml.YAMLError as e:
                logger.error(f"YAML parse error for {yaml_file}: {e}")
        
        return knowledge if knowledge else None
    
    def load_layer(self, layer_name: str) -> Dict[str, Any]:
        """
        Load all knowledge from a specific layer.
        
        Args:
            layer_name: Name of the layer to load
            
        Returns:
            Dict containing all knowledge entries from the layer
            
        Raises:
            KeyError: If layer name is not valid
        """
        if layer_name not in self._layers:
            raise KeyError(f"Unknown layer: {layer_name}")
        
        layer = self._layers[layer_name]
        
        if layer.loaded:
            return layer.entries
        
        if not layer.path.exists():
            logger.debug(f"Layer path does not exist: {layer.path}")
            layer.loaded = True
            return {}
        
        # Load all YAMLs from the layer path
        for yaml_file in layer.path.glob("**/*.yaml"):
            # Skip hidden files and index files
            if yaml_file.name.startswith('.'):
                continue
            
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    content = yaml.safe_load(f) or {}
                
                # Use relative path as key
                rel_path = yaml_file.relative_to(layer.path)
                key = str(rel_path.with_suffix(''))
                layer.entries[key] = content
                
            except yaml.YAMLError as e:
                logger.error(f"YAML parse error for {yaml_file}: {e}")
        
        layer.loaded = True
        logger.info(f"Loaded layer '{layer_name}' with {len(layer.entries)} entries")
        return layer.entries
    
    def _deep_merge(
        self,
        base: Dict[str, Any],
        override: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Deep merge two dictionaries with override taking precedence.
        
        Args:
            base: Base dictionary (lower precedence)
            override: Override dictionary (higher precedence)
            
        Returns:
            Merged dictionary
        """
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                # Recursively merge nested dicts
                result[key] = self._deep_merge(result[key], value)
            else:
                # Override value
                result[key] = value
        
        return result
    
    def get_merged_knowledge(
        self,
        domain: str,
        include_compliance: Optional[List[str]] = None,
    ) -> MergedKnowledgeResult:
        """
        Get merged knowledge for a domain with precedence applied.
        
        Merges knowledge from all layers in precedence order:
        1. Company-specific (highest) overrides
        2. Compliance standards
        3. CORTEX base (lowest)
        
        Args:
            domain: Knowledge domain to query
            include_compliance: List of compliance standards to include
            
        Returns:
            MergedKnowledgeResult with merged content and metadata
        """
        cache_key = f"{domain}:{','.join(include_compliance or [])}"
        
        if cache_key in self._merged_cache:
            return self._merged_cache[cache_key]
        
        merged: Dict[str, Any] = {}
        source_layers: List[str] = []
        override_count = 0
        
        # Process layers in reverse precedence order (lowest first)
        sorted_layers = sorted(
            self._layers.values(),
            key=lambda l: l.precedence,
            reverse=True,  # Start with lowest precedence
        )
        
        for layer in sorted_layers:
            # Skip company layer if no company set
            if layer.name == "company-override" and not self._company_name:
                continue
            
            layer_entries = self.load_layer(layer.name)
            
            # Find matching entries for domain
            domain_lower = domain.lower()
            for key, content in layer_entries.items():
                key_lower = key.lower()
                if domain_lower in key_lower or key_lower in domain_lower:
                    old_keys = set(merged.keys())
                    merged = self._deep_merge(merged, content)
                    new_keys = set(merged.keys())
                    override_count += len(old_keys & new_keys)
                    
                    if layer.name not in source_layers:
                        source_layers.append(layer.name)
        
        # Add compliance standards if requested
        if include_compliance:
            for standard_id in include_compliance:
                standard = self.load_compliance_standard(standard_id)
                if standard:
                    old_keys = set(merged.keys())
                    merged = self._deep_merge(merged, standard)
                    new_keys = set(merged.keys())
                    override_count += len(old_keys & new_keys)
                    
                    if "compliance-standards" not in source_layers:
                        source_layers.append("compliance-standards")
        
        result = MergedKnowledgeResult(
            merged_content=merged,
            source_layers=source_layers,
            override_count=override_count,
        )
        
        self._merged_cache[cache_key] = result
        logger.debug(
            f"Merged knowledge for '{domain}': {len(merged)} entries, "
            f"{override_count} overrides from {source_layers}"
        )
        
        return result
    
    def get_applicable_compliance_standards(
        self,
        content: str,
        load_full: bool = True,
    ) -> Dict[str, Any]:
        """
        Get applicable compliance standards for code content.
        
        This is the primary integration point for IntentRouter and
        SynthesisEngine to get compliance-aware knowledge.
        
        Args:
            content: Code or text content to analyze
            load_full: Whether to load full standard content
            
        Returns:
            Dict with detected standards and optionally their content
        """
        matches = self.detect_compliance_standards(content)
        
        result: Dict[str, Any] = {
            "detected_standards": [],
            "total_matches": len(matches),
            "standards_content": {},
        }
        
        for match in matches:
            result["detected_standards"].append({
                "standard_id": match.standard_id,
                "confidence": match.confidence,
                "triggers": match.triggers,
            })
            
            if load_full:
                standard_content = self.load_compliance_standard(match.standard_id)
                if standard_content:
                    result["standards_content"][match.standard_id] = standard_content
        
        return result
    
    def clear_cache(self) -> None:
        """Clear all caches."""
        self._compliance_cache.clear()
        self._merged_cache.clear()
        for layer in self._layers.values():
            layer.entries.clear()
            layer.loaded = False
        logger.info("CompanyKnowledgeLoader cache cleared")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get loader metrics and statistics."""
        return {
            "project_root": str(self._project_root),
            "active_company": self._company_name,
            "layers": {
                name: {
                    "precedence": layer.precedence,
                    "path": str(layer.path),
                    "loaded": layer.loaded,
                    "entry_count": len(layer.entries),
                }
                for name, layer in self._layers.items()
            },
            "cached_compliance_standards": list(self._compliance_cache.keys()),
            "cached_merges": len(self._merged_cache),
        }


# =============================================================================
# SINGLETON ACCESS
# =============================================================================

_loader_instance: Optional[CompanyKnowledgeLoader] = None


def get_company_knowledge_loader(
    project_root: Optional[str] = None,
    company_name: Optional[str] = None,
    force_reload: bool = False,
) -> CompanyKnowledgeLoader:
    """
    Get the singleton CompanyKnowledgeLoader instance.
    
    Args:
        project_root: Path to project root (only used on first call)
        company_name: Active company name
        force_reload: Force reload of the loader
        
    Returns:
        CompanyKnowledgeLoader singleton instance
    """
    global _loader_instance
    
    if _loader_instance is None or force_reload:
        _loader_instance = CompanyKnowledgeLoader(
            project_root=project_root,
            company_name=company_name,
        )
    elif company_name and company_name != _loader_instance._company_name:
        _loader_instance.set_company(company_name)
    
    return _loader_instance


__all__ = [
    "CompanyKnowledgeLoader",
    "ComplianceMatch",
    "KnowledgeLayer",
    "MergedKnowledgeResult",
    "get_company_knowledge_loader",
    "COMPLIANCE_PATTERNS",
]
