"""
Business Domain Inference Engine

Automatically infers business domains and capabilities from code structure.
Analyzes class names, namespaces, API paths, and database table patterns.

Part of Phase 1 Task 1.3 - Business Domain Inference Engine

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import re
from pathlib import Path
from typing import List, Dict, Set, Any
from collections import Counter
from dataclasses import dataclass
import logging


@dataclass
class DomainEntity:
    """Represents a discovered business domain"""
    name: str
    confidence: str  # "high", "medium", "low"
    frequency: int
    sources: List[str]  # Where domain was found (class, api, table, namespace)
    capabilities: List[str]  # Inferred capabilities
    examples: List[str]  # Example code artifacts


class BusinessDomainInferenceEngine:
    """
    Infers business domains from code structure patterns.
    
    Pattern matching strategies:
    1. Class/Service/Controller names: {Domain}Controller, {Domain}Service
    2. Namespace patterns: Company.Product.Domain.Feature
    3. API endpoint paths: /api/parking/*, /api/rewards/*
    4. Database table names: tbl_Parking_Transactions
    """
    
    # Generic terms to filter out
    GENERIC_TERMS = {
        'base', 'helper', 'utility', 'common', 'shared', 'abstract',
        'generic', 'default', 'standard', 'custom', 'manager', 'handler',
        'provider', 'factory', 'builder', 'adapter', 'wrapper', 'proxy',
        'service', 'controller', 'repository', 'model', 'view', 'api',
        'data', 'info', 'item', 'object', 'entity', 'type', 'class'
    }
    
    # Class name patterns
    CLASS_PATTERNS = [
        re.compile(r'(?:class|interface)\s+(\w+)Controller', re.IGNORECASE),
        re.compile(r'(?:class|interface)\s+(\w+)Service', re.IGNORECASE),
        re.compile(r'(?:class|interface)\s+I?(\w+)Repository', re.IGNORECASE),
        re.compile(r'(?:class|interface)\s+(\w+)Manager', re.IGNORECASE),
        re.compile(r'(?:class|interface)\s+(\w+)Handler', re.IGNORECASE),
        re.compile(r'(?:class|interface)\s+(\w+)Provider', re.IGNORECASE),
        re.compile(r'(?:class|interface)\s+(\w+)Validator', re.IGNORECASE),
        re.compile(r'(?:class|interface)\s+(\w+)Processor', re.IGNORECASE),
    ]
    
    # Namespace patterns (C#, Java style)
    NAMESPACE_PATTERNS = [
        re.compile(r'namespace\s+\w+\.(\w+)\.(\w+)', re.IGNORECASE),
        re.compile(r'package\s+\w+\.(\w+)\.(\w+)', re.IGNORECASE),
    ]
    
    # API endpoint patterns
    API_PATTERNS = [
        re.compile(r'/api/(\w+)/'),
        re.compile(r'@Route\s*\(\s*["\']\/api\/(\w+)\/', re.IGNORECASE),
        re.compile(r'@GetMapping\s*\(\s*["\']\/api\/(\w+)\/', re.IGNORECASE),
        re.compile(r'@app\.route\s*\(\s*["\']\/api\/(\w+)\/', re.IGNORECASE),
    ]
    
    # Database table patterns
    TABLE_PATTERNS = [
        re.compile(r'tbl_(\w+)_', re.IGNORECASE),
        re.compile(r'Table\s*\(\s*["\'](\w+)_', re.IGNORECASE),
        re.compile(r'CREATE TABLE\s+(\w+)_', re.IGNORECASE),
    ]
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.domain_frequencies = Counter()
        self.domain_sources = {}  # domain -> set of sources
        self.domain_examples = {}  # domain -> list of examples
    
    def analyze_repository(self, repo_path: Path) -> List[DomainEntity]:
        """
        Analyze entire repository to infer business domains.
        
        Args:
            repo_path: Path to repository root
            
        Returns:
            List of discovered DomainEntity objects sorted by confidence
        """
        if not repo_path.exists():
            raise FileNotFoundError(f"Repository not found: {repo_path}")
        
        self.logger.info(f"Analyzing repository: {repo_path}")
        
        # Reset state
        self.domain_frequencies = Counter()
        self.domain_sources = {}
        self.domain_examples = {}
        
        # Scan code files
        code_extensions = ['.py', '.cs', '.js', '.ts', '.java', '.cfc', '.cfm', '.sql']
        code_files = []
        for ext in code_extensions:
            code_files.extend(repo_path.rglob(f"*{ext}"))
        
        self.logger.info(f"Found {len(code_files)} code files")
        
        # Analyze each file
        for file_path in code_files:
            try:
                self._analyze_file(file_path)
            except Exception as e:
                self.logger.warning(f"Failed to analyze {file_path}: {e}")
        
        # Build domain entities
        domains = self._build_domain_entities()
        
        self.logger.info(f"Discovered {len(domains)} business domains")
        
        return domains
    
    def _analyze_file(self, file_path: Path):
        """Analyze single file for domain patterns"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception:
            return
        
        # Extract domains from class names
        for pattern in self.CLASS_PATTERNS:
            for match in pattern.finditer(content):
                domain = match.group(1)
                self._record_domain(domain, 'class', str(file_path))
        
        # Extract domains from namespaces
        for pattern in self.NAMESPACE_PATTERNS:
            for match in pattern.finditer(content):
                # Get both namespace parts
                for group_idx in range(1, match.lastindex + 1):
                    domain = match.group(group_idx)
                    self._record_domain(domain, 'namespace', str(file_path))
        
        # Extract domains from API endpoints
        for pattern in self.API_PATTERNS:
            for match in pattern.finditer(content):
                domain = match.group(1)
                self._record_domain(domain, 'api', str(file_path))
        
        # Extract domains from table names
        for pattern in self.TABLE_PATTERNS:
            for match in pattern.finditer(content):
                domain = match.group(1)
                self._record_domain(domain, 'table', str(file_path))
    
    def _record_domain(self, domain: str, source_type: str, file_path: str):
        """Record a discovered domain with its source"""
        # Normalize domain name first (remove underscores, capitalize)
        domain = domain.strip('_').capitalize()
        
        # Filter out generic terms
        if domain.lower() in self.GENERIC_TERMS:
            return
        
        # Filter out very short names (likely abbreviations)
        if len(domain) < 4:
            return
        
        # Update frequency
        self.domain_frequencies[domain] += 1
        
        # Track sources
        if domain not in self.domain_sources:
            self.domain_sources[domain] = set()
        self.domain_sources[domain].add(source_type)
        
        # Track examples (limit to 5 per domain)
        if domain not in self.domain_examples:
            self.domain_examples[domain] = []
        if len(self.domain_examples[domain]) < 5:
            example = f"{source_type}:{Path(file_path).name}"
            if example not in self.domain_examples[domain]:
                self.domain_examples[domain].append(example)
    
    def _build_domain_entities(self) -> List[DomainEntity]:
        """Build DomainEntity objects from collected data"""
        entities = []
        
        for domain, frequency in self.domain_frequencies.most_common():
            sources = list(self.domain_sources[domain])
            examples = self.domain_examples.get(domain, [])
            
            # Calculate confidence based on frequency and source diversity
            source_count = len(sources)
            if source_count >= 3 or frequency >= 5:
                confidence = "high"
            elif source_count >= 2 or frequency >= 2:
                confidence = "medium"
            else:
                confidence = "low"
            
            # Infer capabilities from sources
            capabilities = self._infer_capabilities(domain, sources)
            
            entity = DomainEntity(
                name=domain,
                confidence=confidence,
                frequency=frequency,
                sources=sources,
                capabilities=capabilities,
                examples=examples
            )
            
            entities.append(entity)
        
        # Sort by confidence (high > medium > low) then frequency
        confidence_order = {"high": 3, "medium": 2, "low": 1}
        entities.sort(
            key=lambda e: (confidence_order[e.confidence], e.frequency),
            reverse=True
        )
        
        return entities
    
    def _infer_capabilities(self, domain: str, sources: List[str]) -> List[str]:
        """Infer business capabilities from domain and sources"""
        capabilities = []
        
        if 'class' in sources:
            capabilities.append(f"Implements {domain.lower()} business logic")
        
        if 'api' in sources:
            capabilities.append(f"Exposes {domain.lower()} REST API")
        
        if 'table' in sources:
            capabilities.append(f"Persists {domain.lower()} data")
        
        if 'namespace' in sources:
            capabilities.append(f"Organizes {domain.lower()} features")
        
        # Generic capability if no specific sources
        if not capabilities:
            capabilities.append(f"Manages {domain.lower()} operations")
        
        return capabilities
    
    def generate_summary(self, domains: List[DomainEntity]) -> str:
        """
        Generate human-readable summary of business domains.
        
        Args:
            domains: List of discovered domains
            
        Returns:
            Natural language summary string
        """
        if not domains:
            return "No business domains detected."
        
        # Get top domains
        high_confidence = [d for d in domains if d.confidence == "high"]
        medium_confidence = [d for d in domains if d.confidence == "medium"]
        
        summary_parts = []
        
        # High confidence domains
        if high_confidence:
            domain_names = [d.name for d in high_confidence[:5]]
            if len(domain_names) > 1:
                domains_str = ", ".join(domain_names[:-1]) + f", and {domain_names[-1]}"
            else:
                domains_str = domain_names[0]
            summary_parts.append(
                f"This application primarily manages {domains_str.lower()} operations."
            )
        
        # Medium confidence domains
        if medium_confidence:
            domain_names = [d.name for d in medium_confidence[:3]]
            domains_str = ", ".join(domain_names).lower()
            summary_parts.append(
                f"It also includes functionality for {domains_str}."
            )
        
        # Total domains
        summary_parts.append(
            f"In total, {len(domains)} business domain{'s' if len(domains) > 1 else ''} identified "
            f"({len(high_confidence)} high confidence, {len(medium_confidence)} medium confidence)."
        )
        
        return " ".join(summary_parts)


def analyze_repository(repo_path: Path) -> Dict[str, Any]:
    """
    Convenience function to analyze repository and return formatted results.
    
    Args:
        repo_path: Path to repository root
        
    Returns:
        Dictionary with domains, summary, and statistics
    """
    engine = BusinessDomainInferenceEngine()
    domains = engine.analyze_repository(repo_path)
    summary = engine.generate_summary(domains)
    
    return {
        'domains': [
            {
                'name': d.name,
                'confidence': d.confidence,
                'frequency': d.frequency,
                'sources': d.sources,
                'capabilities': d.capabilities,
                'examples': d.examples
            }
            for d in domains
        ],
        'summary': summary,
        'statistics': {
            'total_domains': len(domains),
            'high_confidence': len([d for d in domains if d.confidence == "high"]),
            'medium_confidence': len([d for d in domains if d.confidence == "medium"]),
            'low_confidence': len([d for d in domains if d.confidence == "low"])
        }
    }
