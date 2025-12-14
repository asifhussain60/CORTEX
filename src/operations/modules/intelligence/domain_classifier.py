"""
Domain Classifier - Identifies code criticality for risk assessment.

Classifies code modules by business domain and criticality level
to enable domain-aware analysis and risk prioritization.

Copyright © 2025 Asif Hussain. All rights reserved.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class Criticality(Enum):
    """Domain criticality levels."""
    CRITICAL = "critical"  # Payment, auth, data loss
    HIGH = "high"  # Business logic, core features
    MEDIUM = "medium"  # Supporting features
    LOW = "low"  # UI, utilities, logging


@dataclass
class DomainClassification:
    """Domain classification result."""
    file_path: str
    domain_type: str  # "payment", "authentication", "data_storage", etc.
    criticality: Criticality
    confidence: float  # 0.0-1.0
    indicators: List[str]  # Keywords/patterns that led to classification


class DomainClassifier:
    """Classify code modules by business domain and criticality."""
    
    def __init__(self):
        """Initialize domain classifier with domain patterns."""
        # Domain patterns: (domain_name, criticality, keywords)
        self.patterns = [
            # CRITICAL domains
            ("payment", Criticality.CRITICAL, [
                'payment', 'billing', 'charge', 'invoice', 'transaction',
                'stripe', 'paypal', 'credit_card', 'purchase'
            ]),
            ("authentication", Criticality.CRITICAL, [
                'auth', 'login', 'password', 'credential', 'token',
                'jwt', 'oauth', 'session', 'user_auth'
            ]),
            ("data_storage", Criticality.CRITICAL, [
                'database', 'persist', 'save', 'store', 'commit',
                'transaction', 'rollback', 'backup'
            ]),
            ("security", Criticality.CRITICAL, [
                'security', 'encrypt', 'decrypt', 'hash', 'salt',
                'permission', 'access_control', 'vulnerability'
            ]),
            
            # HIGH criticality domains
            ("business_logic", Criticality.HIGH, [
                'calculate', 'process', 'validate', 'workflow',
                'business_rule', 'policy', 'decision'
            ]),
            ("core_feature", Criticality.HIGH, [
                'core', 'main', 'primary', 'essential', 'critical_path'
            ]),
            
            # MEDIUM criticality domains
            ("api", Criticality.MEDIUM, [
                'api', 'endpoint', 'route', 'controller', 'handler'
            ]),
            ("integration", Criticality.MEDIUM, [
                'integration', 'external', 'third_party', 'webhook'
            ]),
            
            # LOW criticality domains
            ("ui", Criticality.LOW, [
                'ui', 'view', 'template', 'component', 'widget',
                'frontend', 'display', 'render'
            ]),
            ("utility", Criticality.LOW, [
                'util', 'helper', 'tool', 'common', 'shared'
            ]),
            ("logging", Criticality.LOW, [
                'log', 'logger', 'debug', 'trace', 'monitor'
            ]),
        ]
        
    def classify(self, file_path: Path) -> DomainClassification:
        """
        Classify file by business domain and criticality.
        
        Args:
            file_path: Path to file to classify
            
        Returns:
            DomainClassification result
        """
        file_str = str(file_path).lower()
        file_name = file_path.name.lower()
        
        # Try to read file content for better classification
        content = ""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(5000).lower()  # First 5KB
        except Exception as e:
            logger.debug(f"Could not read {file_path} for classification: {e}")
            
        # Score each domain pattern
        scores = []
        for domain_name, criticality, keywords in self.patterns:
            matches = []
            score = 0.0
            
            for keyword in keywords:
                # Check file path/name
                if keyword in file_str:
                    score += 0.3
                    matches.append(f"path: {keyword}")
                if keyword in file_name:
                    score += 0.5
                    matches.append(f"filename: {keyword}")
                    
                # Check content
                if keyword in content:
                    occurrences = content.count(keyword)
                    score += min(occurrences * 0.1, 1.0)
                    matches.append(f"content: {keyword}")
                    
            if score > 0:
                scores.append((domain_name, criticality, score, matches[:5]))
                
        # No matches - default to low criticality unknown domain
        if not scores:
            return DomainClassification(
                file_path=str(file_path),
                domain_type="unknown",
                criticality=Criticality.LOW,
                confidence=0.0,
                indicators=["No domain indicators found"]
            )
            
        # Return highest scoring domain, or unknown if no strong match
        scores.sort(key=lambda x: x[2], reverse=True)
        domain_name, criticality, score, indicators = scores[0]
        
        # If score is too low, classify as unknown
        # Require at least filename or strong content match (threshold 0.5)
        if score < 0.5:
            return DomainClassification(
                file_path=str(file_path),
                domain_type="unknown",
                criticality=Criticality.LOW,
                confidence=0.0,
                indicators=["No strong domain indicators found"]
            )
        
        return DomainClassification(
            file_path=str(file_path),
            domain_type=domain_name,
            criticality=criticality,
            confidence=min(score, 1.0),
            indicators=indicators
        )
        
    def classify_bulk(self, file_paths: List[Path]) -> List[DomainClassification]:
        """
        Classify multiple files.
        
        Args:
            file_paths: List of file paths to classify
            
        Returns:
            List of classifications
        """
        return [self.classify(fp) for fp in file_paths]
        
    def get_critical_files(self, file_paths: List[Path]) -> List[Path]:
        """
        Filter files to only critical/high criticality ones.
        
        Args:
            file_paths: List of file paths to check
            
        Returns:
            List of critical/high criticality files
        """
        critical_files = []
        
        for fp in file_paths:
            classification = self.classify(fp)
            if classification.criticality in [Criticality.CRITICAL, Criticality.HIGH]:
                critical_files.append(fp)
                
        return critical_files
