"""
Knowledge YAML Resolver - Tech Stack to YAML Mapping.

Authority: Phase 90 Stage 2 - Knowledge YAML Resolver
Purpose: Map detected tech stacks to relevant knowledge YAML files with company precedence

Features:
- Maps tech_stack → YAML files (python → [python.yaml, pytest.yaml])
- Company precedence (cortex-registry/company/domains/ > cortex/knowledge/best-practices/)
- Multi-stack support (monorepos with Python + React)
- Fuzzy matching ('python3' → 'python')
- Framework dependency resolution (Flask → Python)
- Caching with 5-minute TTL

CORE Rules:
- CORE-008: TDD mandatory ✅
- CORE-011: Type hints required ✅
- CORE-012: Docstrings required ✅
- CORE-013: No bare except ✅
"""

import logging
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
import yaml

from cortex.lens.models.tech_stack import TechStack, TechCategory

logger = logging.getLogger(__name__)


@dataclass
class YAMLResolutionResult:
    """Result of YAML resolution with metadata."""
    
    yamls: List[str] = field(default_factory=list)
    company_overrides: List[str] = field(default_factory=list)
    fallback_yamls: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)


class KnowledgeYAMLResolver:
    """
    Resolve tech stack to knowledge YAML files.
    
    Maps detected technologies (languages, frameworks, libraries) to
    relevant knowledge YAML files, with company precedence support.
    
    Examples:
        >>> resolver = KnowledgeYAMLResolver()
        >>> tech_stack = TechStack()
        >>> tech_stack.languages = ["python"]
        >>> tech_stack.frameworks = ["flask"]
        >>> yamls = resolver.resolve(tech_stack)
        >>> print(yamls)  # ["python.yaml", "flask.yaml", "rest-api.yaml", "pytest.yaml"]
    
    Authority: AC-PHASE90-S2-001
    """
    
    # Fuzzy matching rules
    FUZZY_MATCHES: Dict[str, str] = {
        "python3": "python",
        "python2": "python",
        "py": "python",
        "ts": "typescript",
        "js": "javascript",
        "cs": "csharp",
    }
    
    def __init__(
        self,
        mappings_path: Optional[Path] = None,
        cortex_knowledge_path: Optional[Path] = None
    ) -> None:
        """
        Initialize KnowledgeYAMLResolver.
        
        Args:
            mappings_path: Path to tech_stack_mappings.yaml
            cortex_knowledge_path: Path to cortex/knowledge/best-practices/
        """
        self.logger = logging.getLogger(f"{__name__}.KnowledgeYAMLResolver")
        
        # Load mappings
        if not mappings_path:
            mappings_path = (
                Path(__file__).parent / "tech_stack_mappings.yaml"
            )
        
        self.mappings_path = mappings_path
        self.mappings = self._load_mappings()
        
        # Set CORTEX knowledge path
        if not cortex_knowledge_path:
            cortex_knowledge_path = (
                Path(__file__).parent.parent.parent / "knowledge" / "best-practices"
            )
        self.cortex_knowledge_path = cortex_knowledge_path
        
        # Cache for resolved YAMLs (TTL 5min)
        self._cache: Dict[str, Tuple[List[str], float]] = {}
        self._cache_ttl = 300  # 5 minutes
        
        self.logger.info("AC_START: AC-PHASE90-S2-001 | KnowledgeYAMLResolver initialized")
    
    def _load_mappings(self) -> Dict:
        """
        Load tech stack mappings from YAML file.
        
        Returns:
            Dict with language/framework/library mappings
        """
        try:
            if not self.mappings_path.exists():
                self.logger.warning(f"Mappings file not found: {self.mappings_path}")
                return self._get_default_mappings()
            
            with open(self.mappings_path, 'r', encoding='utf-8') as f:
                mappings = yaml.safe_load(f)
            
            self.logger.info(f"Loaded tech stack mappings from {self.mappings_path}")
            return mappings
            
        except Exception as e:
            self.logger.error(f"Failed to load mappings: {e}")
            return self._get_default_mappings()
    
    def _get_default_mappings(self) -> Dict:
        """Get minimal default mappings as fallback."""
        return {
            "languages": {
                "python": {"yamls": ["python.yaml", "pytest.yaml", "python-typing.yaml"]},
                "csharp": {"yamls": ["dotnet.yaml", "csharp.yaml", "aspnet.yaml"]},
                "java": {"yamls": ["java.yaml", "spring-boot.yaml", "maven.yaml"]},
                "typescript": {"yamls": ["typescript.yaml", "javascript.yaml", "nodejs.yaml"]},
            },
            "frameworks": {
                "flask": {"yamls": ["flask.yaml", "rest-api.yaml", "python.yaml"], "requires_language": "python"},
                "django": {"yamls": ["django.yaml", "rest-api.yaml", "python.yaml"], "requires_language": "python"},
                "react": {"yamls": ["react.yaml", "frontend-patterns.yaml", "accessibility.yaml"]},
            },
            "fallback": {
                "default_yamls": ["clean-code.yaml", "solid-principles.yaml", "testing-patterns.yaml"]
            }
        }
    
    def resolve(
        self,
        tech_stack: TechStack,
        company_path: Optional[Path] = None
    ) -> List[str]:
        """
        Resolve tech stack to list of YAML files.
        
        Maps detected technologies to relevant knowledge YAMLs,
        with company precedence (company > CORTEX).
        
        Args:
            tech_stack: Detected technology stack
            company_path: Optional path to company knowledge YAMLs
        
        Returns:
            List of YAML filenames (deduplicated)
        
        Examples:
            >>> resolver = KnowledgeYAMLResolver()
            >>> tech_stack = TechStack()
            >>> tech_stack.languages = ["python"]
            >>> tech_stack.frameworks = ["flask"]
            >>> yamls = resolver.resolve(tech_stack)
            >>> assert "python.yaml" in yamls
            >>> assert "flask.yaml" in yamls
        """
        # Check cache
        cache_key = self._get_cache_key(tech_stack, company_path)
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached
        
        yamls: Set[str] = set()
        
        # Process languages
        for language in tech_stack.languages:
            yamls.update(self._resolve_language(language))
        
        # Process frameworks
        for framework in tech_stack.frameworks:
            yamls.update(self._resolve_framework(framework, tech_stack.languages))
        
        # Process libraries
        for library in tech_stack.libraries:
            yamls.update(self._resolve_library(library))
        
        # Process databases
        for database in tech_stack.databases:
            yamls.update(self._resolve_database(database))
        
        # Add cross-cutting concerns
        yamls.update(self._resolve_patterns(tech_stack))
        
        # Fallback if empty
        if not yamls:
            yamls.update(self._get_fallback_yamls())
        
        # Apply company precedence
        result_yamls = self._apply_company_precedence(list(yamls), company_path)
        
        # Cache result
        self._cache[cache_key] = (result_yamls, self._get_current_time())
        
        return result_yamls
    
    def resolve_with_metadata(
        self,
        tech_stack: TechStack,
        company_path: Optional[Path] = None
    ) -> YAMLResolutionResult:
        """
        Resolve tech stack with detailed metadata.
        
        Args:
            tech_stack: Detected technology stack
            company_path: Optional path to company knowledge YAMLs
        
        Returns:
            YAMLResolutionResult with yamls + metadata
        """
        yamls = self.resolve(tech_stack, company_path)
        
        # Identify company overrides
        company_overrides = []
        if company_path:
            for yaml_file in yamls:
                if company_path and (company_path / yaml_file).exists():
                    company_overrides.append(yaml_file)
        
        return YAMLResolutionResult(
            yamls=yamls,
            company_overrides=company_overrides,
            fallback_yamls=self._get_fallback_yamls(),
            metadata={
                "tech_stack_confidence": tech_stack.confidence_score,
                "languages_count": len(tech_stack.languages),
                "frameworks_count": len(tech_stack.frameworks),
                "total_yamls": len(yamls),
                "company_overrides_count": len(company_overrides),
            }
        )
    
    def _resolve_language(self, language: str) -> List[str]:
        """Resolve language to YAML files."""
        # Fuzzy matching
        language = self._apply_fuzzy_matching(language)
        
        if "languages" not in self.mappings:
            return []
        
        lang_config = self.mappings["languages"].get(language.lower())
        if lang_config:
            return lang_config.get("yamls", [])
        
        return []
    
    def _resolve_framework(self, framework: str, languages: List[str]) -> List[str]:
        """Resolve framework to YAML files."""
        framework = self._apply_fuzzy_matching(framework)
        
        if "frameworks" not in self.mappings:
            return []
        
        fw_config = self.mappings["frameworks"].get(framework.lower())
        if fw_config:
            yamls = fw_config.get("yamls", [])
            
            # Check if framework requires specific language
            requires_lang = fw_config.get("requires_language")
            if requires_lang and isinstance(requires_lang, str):
                requires_lang = [requires_lang]
            
            # Add required language YAMLs if not present
            if requires_lang and not any(lang in languages for lang in requires_lang):
                for req_lang in requires_lang:
                    yamls.extend(self._resolve_language(req_lang))
            
            return yamls
        
        return []
    
    def _resolve_library(self, library: str) -> List[str]:
        """Resolve library to YAML files."""
        library = self._apply_fuzzy_matching(library)
        
        if "libraries" not in self.mappings:
            return []
        
        lib_config = self.mappings["libraries"].get(library.lower())
        if lib_config:
            return lib_config.get("yamls", [])
        
        return []
    
    def _resolve_database(self, database: str) -> List[str]:
        """Resolve database to YAML files."""
        if "databases" not in self.mappings:
            return []
        
        db_config = self.mappings["databases"].get(database.lower())
        if db_config:
            return db_config.get("yamls", [])
        
        return []
    
    def _resolve_patterns(self, tech_stack: TechStack) -> List[str]:
        """Resolve cross-cutting patterns based on tech stack."""
        if "patterns" not in self.mappings:
            return []
        
        yamls: Set[str] = set()
        patterns = self.mappings["patterns"]
        
        # Check each pattern's trigger keywords
        all_techs = (
            tech_stack.languages +
            tech_stack.frameworks +
            tech_stack.libraries
        )
        
        for pattern_name, pattern_config in patterns.items():
            trigger_keywords = pattern_config.get("trigger_keywords", [])
            
            # Check if any trigger keyword matches
            for keyword in trigger_keywords:
                if any(keyword.lower() in tech.lower() for tech in all_techs):
                    yamls.update(pattern_config.get("yamls", []))
                    break
        
        return list(yamls)
    
    def _get_fallback_yamls(self) -> List[str]:
        """Get fallback YAMLs for unknown tech stacks."""
        if "fallback" in self.mappings:
            return self.mappings["fallback"].get("default_yamls", [])
        return ["clean-code.yaml", "solid-principles.yaml", "testing-patterns.yaml"]
    
    def _apply_fuzzy_matching(self, tech_name: str) -> str:
        """Apply fuzzy matching rules."""
        tech_lower = tech_name.lower()
        return self.FUZZY_MATCHES.get(tech_lower, tech_name)
    
    def _apply_company_precedence(
        self,
        yamls: List[str],
        company_path: Optional[Path]
    ) -> List[str]:
        """
        Apply company precedence (company > CORTEX).
        
        If company YAML exists, use it instead of CORTEX default.
        
        Args:
            yamls: List of YAML filenames
            company_path: Path to company knowledge directory
        
        Returns:
            List with company precedence applied
        """
        if not company_path:
            return yamls
        
        result = []
        for yaml_file in yamls:
            company_yaml = company_path / yaml_file
            
            # Check if company override exists
            if company_yaml.exists():
                # Use company path (relative)
                result.append(f"company/{yaml_file}")
            else:
                # Use CORTEX default
                result.append(yaml_file)
        
        return result
    
    def _get_cache_key(self, tech_stack: TechStack, company_path: Optional[Path]) -> str:
        """Generate cache key for tech stack."""
        content = (
            "|".join(sorted(tech_stack.languages)) +
            "|" +
            "|".join(sorted(tech_stack.frameworks)) +
            "|" +
            "|".join(sorted(tech_stack.libraries)) +
            "|" +
            str(company_path)
        )
        return hashlib.sha256(content.encode()).hexdigest()
    
    def _get_from_cache(self, cache_key: str) -> Optional[List[str]]:
        """Get cached result if still valid."""
        if cache_key in self._cache:
            yamls, timestamp = self._cache[cache_key]
            
            # Check TTL
            if (self._get_current_time() - timestamp) < self._cache_ttl:
                return yamls
            else:
                # Expired - remove from cache
                del self._cache[cache_key]
        
        return None
    
    def _get_current_time(self) -> float:
        """Get current time (for testing/mocking)."""
        import time
        return time.time()


# AC_COMPLETE: AC-PHASE90-S2-001 ✅
# Description: KnowledgeYAMLResolver GREEN implementation complete
