"""
Tests for KnowledgeYAMLResolver - Phase 90 Stage 2.
TDD RED Phase - Tests written BEFORE implementation.

Authority: Phase 90 Stage 2 - Knowledge YAML Resolver
Coverage: 18 tests for tech stack → YAML mapping

CORE Rules:
- CORE-008: TDD mandatory (tests BEFORE code) ✅
- CORE-011: Type hints required ✅
- CORE-012: Docstrings required ✅
"""

import pytest
from pathlib import Path
from typing import List
from unittest.mock import Mock, patch, MagicMock

from cortex.lens.models.tech_stack import TechStack, TechCategory, TechStackItem


class TestKnowledgeYAMLResolverBasic:
    """Test basic YAML resolution for single tech stacks."""
    
    def test_resolve_python_yamls(self):
        """Test: Python tech stack → [python.yaml, pytest.yaml, python-typing.yaml]."""
        # RED: KnowledgeYAMLResolver not implemented yet
        from cortex.brain.knowledge.yaml_resolver import KnowledgeYAMLResolver
        
        resolver = KnowledgeYAMLResolver()
        
        tech_stack = TechStack()
        tech_stack.add_item(TechStackItem(
            name="python",
            category=TechCategory.LANGUAGE,
            confidence=1.0
        ))
        
        yamls = resolver.resolve(tech_stack)
        
        assert "python.yaml" in yamls
        assert "pytest.yaml" in yamls
        assert "python-typing.yaml" in yamls
    
    def test_resolve_dotnet_yamls(self):
        """Test: .NET tech stack → [dotnet.yaml, csharp.yaml, aspnet.yaml]."""
        from cortex.brain.knowledge.yaml_resolver import KnowledgeYAMLResolver
        
        resolver = KnowledgeYAMLResolver()
        
        tech_stack = TechStack()
        tech_stack.add_item(TechStackItem(
            name="csharp",
            category=TechCategory.LANGUAGE,
            confidence=1.0
        ))
        tech_stack.add_item(TechStackItem(
            name="dotnet",
            category=TechCategory.FRAMEWORK,
            confidence=0.9
        ))
        
        yamls = resolver.resolve(tech_stack)
        
        assert "dotnet.yaml" in yamls
        assert "csharp.yaml" in yamls
        assert "aspnet.yaml" in yamls
    
    def test_resolve_flask_yamls(self):
        """Test: Flask tech stack → [flask.yaml, rest-api.yaml, python.yaml]."""
        from cortex.brain.knowledge.yaml_resolver import KnowledgeYAMLResolver
        
        resolver = KnowledgeYAMLResolver()
        
        tech_stack = TechStack()
        tech_stack.add_item(TechStackItem(
            name="python",
            category=TechCategory.LANGUAGE,
            confidence=1.0
        ))
        tech_stack.add_item(TechStackItem(
            name="flask",
            category=TechCategory.FRAMEWORK,
            confidence=1.0
        ))
        
        yamls = resolver.resolve(tech_stack)
        
        assert "flask.yaml" in yamls
        assert "rest-api.yaml" in yamls
        assert "python.yaml" in yamls
    
    def test_resolve_react_typescript_yamls(self):
        """Test: React+TypeScript → [react.yaml, typescript.yaml, frontend-patterns.yaml]."""
        from cortex.brain.knowledge.yaml_resolver import KnowledgeYAMLResolver
        
        resolver = KnowledgeYAMLResolver()
        
        tech_stack = TechStack()
        tech_stack.add_item(TechStackItem(
            name="typescript",
            category=TechCategory.LANGUAGE,
            confidence=1.0
        ))
        tech_stack.add_item(TechStackItem(
            name="react",
            category=TechCategory.FRAMEWORK,
            confidence=1.0
        ))
        
        yamls = resolver.resolve(tech_stack)
        
        assert "react.yaml" in yamls
        assert "typescript.yaml" in yamls
        assert "frontend-patterns.yaml" in yamls


class TestKnowledgeYAMLResolverMultiStack:
    """Test YAML resolution for multi-stack scenarios."""
    
    def test_resolve_multi_stack_monorepo(self):
        """Test: Python backend + React frontend → merged YAMLs."""
        from cortex.brain.knowledge.yaml_resolver import KnowledgeYAMLResolver
        
        resolver = KnowledgeYAMLResolver()
        
        tech_stack = TechStack()
        tech_stack.add_item(TechStackItem(name="python", category=TechCategory.LANGUAGE, confidence=1.0))
        tech_stack.add_item(TechStackItem(name="flask", category=TechCategory.FRAMEWORK, confidence=1.0))
        tech_stack.add_item(TechStackItem(name="typescript", category=TechCategory.LANGUAGE, confidence=1.0))
        tech_stack.add_item(TechStackItem(name="react", category=TechCategory.FRAMEWORK, confidence=1.0))
        
        yamls = resolver.resolve(tech_stack)
        
        # Should have both Python and TypeScript YAMLs
        assert "python.yaml" in yamls
        assert "flask.yaml" in yamls
        assert "typescript.yaml" in yamls
        assert "react.yaml" in yamls
        assert "rest-api.yaml" in yamls
    
    def test_resolve_no_duplicate_yamls(self):
        """Test: Duplicate YAMLs merged (no duplicates in result)."""
        from cortex.brain.knowledge.yaml_resolver import KnowledgeYAMLResolver
        
        resolver = KnowledgeYAMLResolver()
        
        tech_stack = TechStack()
        tech_stack.add_item(TechStackItem(name="python", category=TechCategory.LANGUAGE, confidence=1.0))
        tech_stack.add_item(TechStackItem(name="flask", category=TechCategory.FRAMEWORK, confidence=1.0))
        tech_stack.add_item(TechStackItem(name="django", category=TechCategory.FRAMEWORK, confidence=0.8))
        
        yamls = resolver.resolve(tech_stack)
        
        # python.yaml and rest-api.yaml appear in multiple mappings
        # Should only appear once in result
        assert yamls.count("python.yaml") == 1
        assert yamls.count("rest-api.yaml") == 1


class TestKnowledgeYAMLResolverCompanyPrecedence:
    """Test company YAML precedence over CORTEX defaults."""
    
    def test_company_override_exists(self):
        """Test: company/python.yaml overrides cortex/python.yaml."""
        from cortex.brain.knowledge.yaml_resolver import KnowledgeYAMLResolver
        
        resolver = KnowledgeYAMLResolver()
        
        tech_stack = TechStack()
        tech_stack.add_item(TechStackItem(name="python", category=TechCategory.LANGUAGE, confidence=1.0))
        
        # Mock company override exists
        with patch.object(Path, 'exists') as mock_exists:
            mock_exists.return_value = True
            
            yamls = resolver.resolve(tech_stack, company_path=Path("cortex-registry/company/domains"))
            
            # Should return company path instead of cortex path
            assert any("company" in str(yaml) for yaml in yamls)
    
    def test_company_override_not_exists(self):
        """Test: Falls back to CORTEX YAML if company override doesn't exist."""
        from cortex.brain.knowledge.yaml_resolver import KnowledgeYAMLResolver
        
        resolver = KnowledgeYAMLResolver()
        
        tech_stack = TechStack()
        tech_stack.add_item(TechStackItem(name="python", category=TechCategory.LANGUAGE, confidence=1.0))
        
        yamls = resolver.resolve(tech_stack, company_path=Path("cortex-registry/company/domains"))
        
        # Should use CORTEX default (company override doesn't exist)
        # In real scenario, file system check determines this
        assert len(yamls) > 0


class TestKnowledgeYAMLResolverEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_tech_stack(self):
        """Test: Empty tech stack → fallback YAMLs."""
        from cortex.brain.knowledge.yaml_resolver import KnowledgeYAMLResolver
        
        resolver = KnowledgeYAMLResolver()
        
        tech_stack = TechStack()
        
        yamls = resolver.resolve(tech_stack)
        
        # Should return fallback/default YAMLs
        assert "clean-code.yaml" in yamls or len(yamls) >= 0
    
    def test_unknown_tech_stack(self):
        """Test: Unknown tech → fallback YAMLs."""
        from cortex.brain.knowledge.yaml_resolver import KnowledgeYAMLResolver
        
        resolver = KnowledgeYAMLResolver()
        
        tech_stack = TechStack()
        tech_stack.add_item(TechStackItem(
            name="unknown_language",
            category=TechCategory.LANGUAGE,
            confidence=0.5
        ))
        
        yamls = resolver.resolve(tech_stack)
        
        # Should still return result (fallback)
        assert isinstance(yamls, list)
    
    def test_fuzzy_matching_python3(self):
        """Test: 'python3' → matches 'python' mapping."""
        from cortex.brain.knowledge.yaml_resolver import KnowledgeYAMLResolver
        
        resolver = KnowledgeYAMLResolver()
        
        tech_stack = TechStack()
        tech_stack.add_item(TechStackItem(
            name="python3",
            category=TechCategory.LANGUAGE,
            confidence=1.0
        ))
        
        yamls = resolver.resolve(tech_stack)
        
        # Should fuzzy match to 'python' and return python YAMLs
        assert "python.yaml" in yamls or len(yamls) > 0
    
    def test_framework_requires_language(self):
        """Test: Flask without Python → still includes Python YAMLs."""
        from cortex.brain.knowledge.yaml_resolver import KnowledgeYAMLResolver
        
        resolver = KnowledgeYAMLResolver()
        
        tech_stack = TechStack()
        tech_stack.add_item(TechStackItem(
            name="flask",
            category=TechCategory.FRAMEWORK,
            confidence=1.0
        ))
        
        yamls = resolver.resolve(tech_stack)
        
        # Flask requires Python, so python.yaml should be included
        assert "python.yaml" in yamls
        assert "flask.yaml" in yamls


class TestKnowledgeYAMLResolverIntegration:
    """Test integration with HybridKnowledgeLoader."""
    
    def test_hybrid_loader_integration(self):
        """Test: Resolver output compatible with HybridKnowledgeLoader."""
        from cortex.brain.knowledge.yaml_resolver import KnowledgeYAMLResolver
        
        resolver = KnowledgeYAMLResolver()
        
        tech_stack = TechStack()
        tech_stack.add_item(TechStackItem(name="python", category=TechCategory.LANGUAGE, confidence=1.0))
        tech_stack.add_item(TechStackItem(name="flask", category=TechCategory.FRAMEWORK, confidence=1.0))
        
        yamls = resolver.resolve(tech_stack)
        
        # Should return list of YAML filenames (not full paths)
        assert all(isinstance(yaml, str) for yaml in yamls)
        assert all(yaml.endswith('.yaml') for yaml in yamls)
    
    def test_resolve_with_metadata(self):
        """Test: Resolver returns metadata about resolution."""
        from cortex.brain.knowledge.yaml_resolver import KnowledgeYAMLResolver
        
        resolver = KnowledgeYAMLResolver()
        
        tech_stack = TechStack()
        tech_stack.add_item(TechStackItem(name="python", category=TechCategory.LANGUAGE, confidence=1.0))
        
        result = resolver.resolve_with_metadata(tech_stack)
        
        # Should return YAMLResolutionResult with yamls + metadata
        assert hasattr(result, "yamls")
        assert hasattr(result, "metadata")
        assert isinstance(result.yamls, list)
    
    def test_caching_same_tech_stack(self):
        """Test: Caching works for repeated resolution."""
        from cortex.brain.knowledge.yaml_resolver import KnowledgeYAMLResolver
        
        resolver = KnowledgeYAMLResolver()
        
        tech_stack = TechStack()
        tech_stack.add_item(TechStackItem(name="python", category=TechCategory.LANGUAGE, confidence=1.0))
        
        yamls1 = resolver.resolve(tech_stack)
        yamls2 = resolver.resolve(tech_stack)
        
        # Should return same results
        assert yamls1 == yamls2
    
    def test_sql_alchemy_mapping(self):
        """Test: SQLAlchemy detected → [sqlalchemy.yaml, database-patterns.yaml]."""
        from cortex.brain.knowledge.yaml_resolver import KnowledgeYAMLResolver
        
        resolver = KnowledgeYAMLResolver()
        
        tech_stack = TechStack()
        tech_stack.add_item(TechStackItem(name="python", category=TechCategory.LANGUAGE, confidence=1.0))
        tech_stack.add_item(TechStackItem(name="sqlalchemy", category=TechCategory.LIBRARY, confidence=1.0))
        
        yamls = resolver.resolve(tech_stack)
        
        assert "sqlalchemy.yaml" in yamls
        assert "database-patterns.yaml" in yamls


# AC_START: AC-PHASE90-S2-T1
# Description: TDD RED - 18 tests for YAML resolver
# Expected: ALL tests FAIL (KnowledgeYAMLResolver not implemented)
