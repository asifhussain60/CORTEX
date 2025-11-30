"""
CORTEX Governance Module
Version: 1.0
Purpose: Documentation governance, duplicate prevention, canonical name enforcement

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

from .document_governance import DocumentGovernance, DocumentMetadata, DuplicateMatch

__all__ = [
    'DocumentGovernance',
    'DocumentMetadata',
    'DuplicateMatch'
]
