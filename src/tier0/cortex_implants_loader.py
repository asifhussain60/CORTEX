"""
CORTEX Implants Loader

Loads and validates repository-specific governance rules from .cortex-implants/ folders.
Each repository maintains its own implants with strict isolation.

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
Version: 1.0.0
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class EnforcementLevel(Enum):
    """Company rule enforcement levels."""
    STRICT = "STRICT"          # Block violations
    MODERATE = "MODERATE"      # Warn on violations
    ADVISORY = "ADVISORY"      # Log violations only


class RepositoryType(Enum):
    """Repository types."""
    WEB_APPLICATION = "web-application"
    API_SERVICE = "api-service"
    MOBILE_APP = "mobile-app"
    LIBRARY = "library"
    MICROSERVICE = "microservice"
    DESKTOP_APP = "desktop-app"


@dataclass
class ImplantGovernance:
    """Implant governance configuration."""
    version: str
    company_name: str
    division: str
    contact: str
    repo_name: str
    repo_type: RepositoryType
    language: str
    framework: str
    enforcement_level: EnforcementLevel
    block_on_violation: bool
    require_approval_override: bool
    rules_enabled: List[str]
    integration_flags: Dict[str, bool]
    priority: str  # HIGH, MEDIUM, LOW
    
    def is_rule_enabled(self, rule_name: str) -> bool:
        """Check if a rule category is enabled."""
        return rule_name in self.rules_enabled


@dataclass
class CodingStandards:
    """Coding standards configuration."""
    naming_conventions: Dict[str, Any]
    file_organization: Dict[str, Any]
    code_style: Dict[str, Any]
    imports: Dict[str, Any]
    documentation: Dict[str, Any]


@dataclass
class ArchitecturePatterns:
    """Architecture patterns configuration."""
    required_patterns: List[Dict[str, Any]]
    anti_patterns: List[Dict[str, Any]]
    layer_boundaries: List[Dict[str, Any]]


@dataclass
class BusinessRules:
    """Business rules configuration."""
    domain_validations: List[Dict[str, Any]]
    workflow_rules: List[Dict[str, Any]]
    compliance: List[Dict[str, Any]]


@dataclass
class TechStack:
    """Tech stack configuration."""
    approved_libraries: Dict[str, List[Dict[str, Any]]]
    forbidden_libraries: List[Dict[str, Any]]
    language_features: Dict[str, Any]


@dataclass
class SecurityPolicy:
    """Security policy configuration."""
    authentication: Dict[str, Any]
    authorization: Dict[str, Any]
    data_protection: Dict[str, Any]
    input_validation: Dict[str, Any]
    secrets_management: Dict[str, Any]


@dataclass
class CortexImplants:
    """Complete cortex implants configuration."""
    governance: ImplantGovernance
    coding_standards: Optional[CodingStandards] = None
    architecture_patterns: Optional[ArchitecturePatterns] = None
    business_rules: Optional[BusinessRules] = None
    tech_stack: Optional[TechStack] = None
    security_policy: Optional[SecurityPolicy] = None
    repo_path: Path = field(default_factory=Path)
    
    def is_rule_enabled(self, rule_name: str) -> bool:
        """Check if a rule category is enabled."""
        return rule_name in self.governance.rules_enabled
    
    def get_priority(self) -> str:
        """Get priority level (HIGH/MEDIUM/LOW)."""
        return self.governance.priority


class CortexImplantsLoader:
    """
    Loads cortex implants from .cortex-implants/ folders.
    
    Features:
    - Auto-detection of .cortex-implants/ in repo root
    - Schema validation
    - Caching for performance
    - Repo boundary enforcement
    - Version compatibility checking
    
    Usage:
        loader = CortexImplantsLoader()
        implants = loader.load(repo_path)
        
        if implants.is_rule_enabled("CODING_STANDARDS"):
            standards = implants.coding_standards
    """
    
    CORTEX_IMPLANTS_FOLDER = ".cortex-implants"
    REQUIRED_FILES = ["governance.yaml"]
    OPTIONAL_FILES = [
        "coding-standards.yaml",
        "architecture-patterns.yaml",
        "business-rules.yaml",
        "tech-stack.yaml",
        "security-policy.yaml"
    ]
    
    def __init__(self, cache_enabled: bool = True):
        """
        Initialize company tier 0 loader.
        
        Args:
            cache_enabled: Enable in-memory caching
        """
        self.cache_enabled = cache_enabled
        self._cache: Dict[str, CortexImplants] = {}
    
    def load(self, repo_path: Path) -> Optional[CortexImplants]:
        """
        Load cortex implants from repository.
        
        Args:
            repo_path: Path to repository root
            
        Returns:
            CortexImplants object or None if not found
            
        Raises:
            FileNotFoundError: If required files missing
            ValueError: If schema validation fails
        """
        repo_path = Path(repo_path).resolve()
        
        # Check cache
        cache_key = str(repo_path)
        if self.cache_enabled and cache_key in self._cache:
            logger.debug(f"🎯 Cache hit: {repo_path}")
            return self._cache[cache_key]
        
        # Find .cortex-implants folder
        implants_dir = self._find_cortex_implants_dir(repo_path)
        if not implants_dir:
            logger.info(f"📁 No .cortex-implants found in {repo_path}")
            return None
        
        logger.info(f"📂 Loading cortex implants from {implants_dir}")
        
        # Validate structure
        self._validate_structure(implants_dir)
        
        # Load governance (required)
        governance_file = implants_dir / "governance.yaml"
        governance_data = self._load_yaml(governance_file)
        governance = self._parse_governance(governance_data)
        
        # Load optional files
        coding_standards = None
        architecture_patterns = None
        business_rules = None
        tech_stack = None
        security_policy = None
        
        if governance.is_rule_enabled("CODING_STANDARDS"):
            standards_file = implants_dir / "coding-standards.yaml"
            if standards_file.exists():
                coding_standards = self._parse_coding_standards(
                    self._load_yaml(standards_file)
                )
        
        if governance.is_rule_enabled("ARCHITECTURE_PATTERNS"):
            patterns_file = implants_dir / "architecture-patterns.yaml"
            if patterns_file.exists():
                architecture_patterns = self._parse_architecture_patterns(
                    self._load_yaml(patterns_file)
                )
        
        if governance.is_rule_enabled("BUSINESS_RULES"):
            rules_file = implants_dir / "business-rules.yaml"
            if rules_file.exists():
                business_rules = self._parse_business_rules(
                    self._load_yaml(rules_file)
                )
        
        if governance.is_rule_enabled("TECH_STACK_VALIDATION"):
            tech_file = implants_dir / "tech-stack.yaml"
            if tech_file.exists():
                tech_stack = self._parse_tech_stack(
                    self._load_yaml(tech_file)
                )
        
        if governance.is_rule_enabled("SECURITY_POLICY"):
            security_file = implants_dir / "security-policy.yaml"
            if security_file.exists():
                security_policy = self._parse_security_policy(
                    self._load_yaml(security_file)
                )
        
        # Build CortexImplants object
        implants = CortexImplants(
            governance=governance,
            coding_standards=coding_standards,
            architecture_patterns=architecture_patterns,
            business_rules=business_rules,
            tech_stack=tech_stack,
            security_policy=security_policy,
            repo_path=repo_path
        )
        
        # Cache result
        if self.cache_enabled:
            self._cache[cache_key] = implants
        
        logger.info(f"✅ Loaded cortex implants for {governance.repo_name}")
        return implants
    
    def _find_cortex_implants_dir(self, repo_path: Path) -> Optional[Path]:
        """Find .cortex-implants directory in repo."""
        implants_dir = repo_path / self.CORTEX_IMPLANTS_FOLDER
        if implants_dir.exists() and implants_dir.is_dir():
            return implants_dir
        
        # Try parent directories (up to 3 levels)
        for _ in range(3):
            repo_path = repo_path.parent
            implants_dir = repo_path / self.CORTEX_IMPLANTS_FOLDER
            if implants_dir.exists() and implants_dir.is_dir():
                return implants_dir
        
        return None
    
    def _validate_structure(self, implants_dir: Path) -> None:
        """Validate .cortex-implants structure."""
        # Check required files
        for required_file in self.REQUIRED_FILES:
            file_path = implants_dir / required_file
            if not file_path.exists():
                raise FileNotFoundError(
                    f"Required file missing: {required_file}"
                )
        
        # Check version marker
        version_file = implants_dir / ".cortex-company-version"
        if not version_file.exists():
            logger.warning(f"⚠️  Version marker missing: {version_file}")
    
    def _load_yaml(self, file_path: Path) -> Dict[str, Any]:
        """Load YAML file with error handling."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                if not data:
                    raise ValueError(f"Empty YAML file: {file_path}")
                return data
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in {file_path}: {e}")
    
    def _parse_governance(self, data: Dict[str, Any]) -> ImplantGovernance:
        """Parse governance.yaml into ImplantGovernance."""
        # Support both flat and nested structures
        if 'company_name' in data:
            # Flat structure (new format)
            return ImplantGovernance(
                version=data.get('version', '1.0'),
                company_name=data.get('company_name', 'Unknown'),
                division=data.get('division', ''),
                contact=data.get('contact', ''),
                repo_name=data.get('repo_name', 'Unknown'),
                repo_type=RepositoryType(data.get('repo_type', 'library')),
                language=data.get('language', 'Unknown'),
                framework=data.get('framework', ''),
                enforcement_level=EnforcementLevel(data.get('enforcement_level', 'MODERATE')),
                block_on_violation=data.get('block_on_violation', False),
                require_approval_override=data.get('require_approval_override', False),
                rules_enabled=data.get('rules_enabled', []),
                integration_flags=data.get('integration_flags', {}),
                priority=data.get('priority', 'MEDIUM')
            )
        else:
            # Nested structure (old format - for backward compatibility)
            company = data.get('company', {})
            repository = data.get('repository', {})
            enforcement = data.get('enforcement', {})
            integration = data.get('integration', {})
            
            return ImplantGovernance(
                version=data.get('version', '1.0'),
                company_name=company.get('name', 'Unknown'),
                division=company.get('division', ''),
                contact=company.get('contact', ''),
                repo_name=repository.get('name', 'Unknown'),
                repo_type=RepositoryType(repository.get('type', 'library')),
                language=repository.get('language', 'Unknown'),
                framework=repository.get('framework', ''),
                enforcement_level=EnforcementLevel(enforcement.get('level', 'MODERATE')),
                block_on_violation=enforcement.get('block_on_violation', False),
                require_approval_override=enforcement.get('require_approval_override', False),
                rules_enabled=data.get('rules_enabled', []),
                integration_flags=integration,
                priority=data.get('priority', 'MEDIUM')
            )
    
    def _parse_coding_standards(self, data: Dict[str, Any]) -> CodingStandards:
        """Parse coding-standards.yaml."""
        return CodingStandards(
            naming_conventions=data.get('naming_conventions', {}),
            file_organization=data.get('file_organization', {}),
            code_style=data.get('code_style', {}),
            imports=data.get('imports', {}),
            documentation=data.get('documentation', {})
        )
    
    def _parse_architecture_patterns(self, data: Dict[str, Any]) -> ArchitecturePatterns:
        """Parse architecture-patterns.yaml."""
        return ArchitecturePatterns(
            required_patterns=data.get('required_patterns', []),
            anti_patterns=data.get('anti_patterns', []),
            layer_boundaries=data.get('layer_boundaries', [])
        )
    
    def _parse_business_rules(self, data: Dict[str, Any]) -> BusinessRules:
        """Parse business-rules.yaml."""
        return BusinessRules(
            domain_validations=data.get('domain_validations', []),
            workflow_rules=data.get('workflow_rules', []),
            compliance=data.get('compliance', [])
        )
    
    def _parse_tech_stack(self, data: Dict[str, Any]) -> TechStack:
        """Parse tech-stack.yaml."""
        return TechStack(
            approved_libraries=data.get('approved_libraries', {}),
            forbidden_libraries=data.get('forbidden_libraries', []),
            language_features=data.get('language_features', {})
        )
    
    def _parse_security_policy(self, data: Dict[str, Any]) -> SecurityPolicy:
        """Parse security-policy.yaml."""
        return SecurityPolicy(
            authentication=data.get('authentication', {}),
            authorization=data.get('authorization', {}),
            data_protection=data.get('data_protection', {}),
            input_validation=data.get('input_validation', {}),
            secrets_management=data.get('secrets_management', {})
        )
    
    def clear_cache(self, repo_path: Optional[Path] = None) -> None:
        """
        Clear loader cache.
        
        Args:
            repo_path: Clear specific repo, or all if None
        """
        if repo_path:
            cache_key = str(Path(repo_path).resolve())
            self._cache.pop(cache_key, None)
            logger.debug(f"🗑️  Cleared cache for {repo_path}")
        else:
            self._cache.clear()
            logger.debug("🗑️  Cleared all cache")
    
    def get_all_repos_with_cortex_implants(
        self,
        workspace_root: Path
    ) -> List[CortexImplants]:
        """
        Find all repos with .cortex-implants in workspace.
        
        Args:
            workspace_root: VS Code workspace root
            
        Returns:
            List of CortexImplants objects
        """
        repos = []
        
        # Search for .cortex-implants folders
        for implants_dir in workspace_root.rglob(self.CORTEX_IMPLANTS_FOLDER):
            if implants_dir.is_dir():
                repo_path = implants_dir.parent
                try:
                    implants = self.load(repo_path)
                    if implants:
                        repos.append(implants)
                except Exception as e:
                    logger.error(f"❌ Failed to load {repo_path}: {e}")
        
        logger.info(f"📊 Found {len(repos)} repos with cortex implants")
        return repos


# Singleton instance
_loader_instance: Optional[CortexImplantsLoader] = None


def get_cortex_implants_loader() -> CortexImplantsLoader:
    """Get singleton loader instance."""
    global _loader_instance
    if _loader_instance is None:
        _loader_instance = CortexImplantsLoader()
    return _loader_instance


def load_cortex_implants(repo_path: Path) -> Optional[CortexImplants]:
    """
    Convenience function to load cortex implants.
    
    Args:
        repo_path: Path to repository
        
    Returns:
        CortexImplants or None
    """
    loader = get_cortex_implants_loader()
    return loader.load(repo_path)
