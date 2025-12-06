"""
Tier 3 Privacy Module

Centralized privacy protection and anonymization for adoption analytics.
Enforces SKULL_PRIVACY_PROTECTION rules with SHA-256 hashing and PII detection.
"""

from .anonymizer import Anonymizer, AnonymizationResult, PIIDetectionResult

__all__ = ['Anonymizer', 'AnonymizationResult', 'PIIDetectionResult']
