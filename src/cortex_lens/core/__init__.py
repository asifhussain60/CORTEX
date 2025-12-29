"""
Core framework for CORTEX Lens.

Contains:
- RepoTypeClassifier: Auto-detects repository type from file patterns
- DataCollectionPipeline: Orchestrates collector execution
- UniversalSchema: Standardized JSON schema definitions
"""

from .classifier import RepoTypeClassifier
from .pipeline import DataCollectionPipeline
from .schema import UniversalSchema

__all__ = [
    'RepoTypeClassifier',
    'DataCollectionPipeline',
    'UniversalSchema',
]
