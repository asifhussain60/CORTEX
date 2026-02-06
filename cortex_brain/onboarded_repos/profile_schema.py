"""
Repository Profile Schema for External Repository Onboarding (Phase 28)

This module defines the data models for repository profiles that enable
loose-coupled interaction with external repositories. Profiles are stored
in CORTEX (cortex_brain/onboarded_repos/) to maintain deletion safety.

Authority: phase-28-repository-onboarding-system.yaml
Created: 2026-02-06
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import BaseModel, Field, field_validator


class TechStack(BaseModel):
    """Technology stack information for a repository."""
    
    primary_language: Optional[str] = None
    languages: List[str] = Field(default_factory=list)
    frameworks: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)


class RepositoryStructure(BaseModel):
    """Repository structure metadata."""
    
    has_company_domains: bool = False
    company_domains_path: Optional[str] = None
    domains_detected: List[str] = Field(default_factory=list)
    has_tests: bool = False
    test_framework: Optional[str] = None
    test_coverage: Optional[str] = None
    has_docs: bool = False
    doc_format: Optional[str] = None


class Standards(BaseModel):
    """Repository coding and operational standards."""
    
    coding_style: Optional[str] = None
    security_baseline: Optional[str] = None
    test_patterns: Optional[str] = None
    api_patterns: Optional[str] = None


class SecurityMetadata(BaseModel):
    """Security configuration and scan results."""
    
    secrets_management: Optional[str] = None
    auth_pattern: Optional[str] = None
    vulnerabilities_detected: int = 0
    last_scan: Optional[datetime] = None


class LooseCoupling(BaseModel):
    """Loose coupling metadata for deletion safety."""
    
    referenced_by_cortex: bool = True
    deletion_safe: bool = True
    fallback_strategy: str = "use_cached_profile"


class RepositoryProfile(BaseModel):
    """
    Complete profile for an onboarded external repository.
    
    This profile enables CORTEX to interact with external repositories
    in a loosely-coupled manner, ensuring that repository deletion does
    not break CORTEX operations.
    
    Attributes:
        name: Repository name (unique identifier)
        path: Absolute path to repository
        onboarded_at: Timestamp of initial onboarding
        last_validated: Timestamp of last validation
        exists: Whether repository currently exists (updated on validation)
        tech_stack: Technology stack information
        structure: Repository structure metadata
        standards: Coding and operational standards
        security: Security configuration and scan results
        loose_coupling: Loose coupling metadata
    """
    
    name: str = Field(..., description="Repository name (unique identifier)")
    path: str = Field(..., description="Absolute path to repository")
    onboarded_at: datetime = Field(..., description="Initial onboarding timestamp")
    last_validated: Optional[datetime] = Field(
        default=None,
        description="Last validation timestamp"
    )
    exists: bool = Field(
        default=True,
        description="Whether repository currently exists"
    )
    
    tech_stack: TechStack = Field(default_factory=TechStack)
    structure: RepositoryStructure = Field(default_factory=RepositoryStructure)
    standards: Standards = Field(default_factory=Standards)
    security: SecurityMetadata = Field(default_factory=SecurityMetadata)
    loose_coupling: LooseCoupling = Field(default_factory=LooseCoupling)
    
    @field_validator('path')
    @classmethod
    def validate_path_format(cls, v: str) -> str:
        """Validate that path is absolute."""
        if not Path(v).is_absolute():
            raise ValueError(f"Path must be absolute, got: {v}")
        return v
    
    def to_yaml(self) -> str:
        """
        Serialize profile to YAML string.
        
        Returns:
            YAML string representation of profile
        """
        data = self.model_dump(mode='json', exclude_none=False)
        
        # Convert datetime objects to ISO format strings
        if 'onboarded_at' in data and data['onboarded_at']:
            data['onboarded_at'] = self.onboarded_at.isoformat()
        if 'last_validated' in data and data['last_validated'] and self.last_validated:
            data['last_validated'] = self.last_validated.isoformat()
        if 'security' in data and data['security'].get('last_scan') and self.security.last_scan:
            data['security']['last_scan'] = self.security.last_scan.isoformat()
        
        return yaml.dump(data, default_flow_style=False, sort_keys=False)
    
    @classmethod
    def from_yaml(cls, yaml_content: str) -> RepositoryProfile:
        """
        Deserialize profile from YAML string.
        
        Args:
            yaml_content: YAML string representation
            
        Returns:
            RepositoryProfile instance
        """
        data = yaml.safe_load(yaml_content)
        
        # Convert ISO format strings back to datetime objects
        if 'onboarded_at' in data and isinstance(data['onboarded_at'], str):
            data['onboarded_at'] = datetime.fromisoformat(data['onboarded_at'])
        if 'last_validated' in data and isinstance(data['last_validated'], str):
            data['last_validated'] = datetime.fromisoformat(data['last_validated'])
        if 'security' in data and isinstance(data['security'].get('last_scan'), str):
            data['security']['last_scan'] = datetime.fromisoformat(
                data['security']['last_scan']
            )
        
        return cls(**data)
    
    def validate_exists(self) -> bool:
        """
        Check if repository path currently exists.
        
        Returns:
            True if path exists, False otherwise
        """
        path = Path(self.path)
        self.exists = path.exists() and path.is_dir()
        self.last_validated = datetime.now()
        return self.exists
