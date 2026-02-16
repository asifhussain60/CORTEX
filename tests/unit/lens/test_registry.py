"""Unit Tests for Analyzer Registry System

Tests registry-based self-wiring with decorator pattern.

Author: CORTEX Framework
Phase: PHASE-97 S3
CORE Rules: CORE-008 (TDD)
"""

import pytest
from typing import Any

from cortex.lens.registry import (
    AnalyzerCapability,
    AnalyzerMetadata,
    AnalyzerRegistry,
    LanguageSupport,
    analyzer_capabilities,
    get_analyzer_registry,
)


class TestAnalyzerMetadata:
    """Test suite for AnalyzerMetadata."""
    
    def test_metadata_creation(self) -> None:
        """Test creating analyzer metadata."""
        metadata = AnalyzerMetadata(
            name="TestAnalyzer",
            capabilities={AnalyzerCapability.AST_ANALYSIS},
            languages={LanguageSupport.PYTHON},
            priority=10,
            description="Test analyzer",
            module_path="test.analyzer",
        )
        
        assert metadata.name == "TestAnalyzer"
        assert AnalyzerCapability.AST_ANALYSIS in metadata.capabilities
        assert LanguageSupport.PYTHON in metadata.languages
        assert metadata.priority == 10


class TestAnalyzerRegistry:
    """Test suite for AnalyzerRegistry."""
    
    @pytest.fixture
    def registry(self) -> AnalyzerRegistry:
        """Create fresh registry instance.
        
        Returns:
            AnalyzerRegistry instance
        """
        return AnalyzerRegistry()
    
    @pytest.fixture
    def sample_metadata(self) -> AnalyzerMetadata:
        """Create sample analyzer metadata.
        
        Returns:
            AnalyzerMetadata instance
        """
        return AnalyzerMetadata(
            name="SampleAnalyzer",
            capabilities={AnalyzerCapability.CODE_QUALITY},
            languages={LanguageSupport.PYTHON},
            priority=50,
        )
    
    def test_register_analyzer(
        self, registry: AnalyzerRegistry, sample_metadata: AnalyzerMetadata
    ) -> None:
        """Test registering analyzer.
        
        Args:
            registry: Analyzer registry
            sample_metadata: Sample metadata
        """
        registry.register(sample_metadata)
        
        retrieved = registry.get("SampleAnalyzer")
        assert retrieved is not None
        assert retrieved.name == "SampleAnalyzer"
    
    def test_find_by_capability(
        self, registry: AnalyzerRegistry, sample_metadata: AnalyzerMetadata
    ) -> None:
        """Test finding analyzers by capability.
        
        Args:
            registry: Analyzer registry
            sample_metadata: Sample metadata
        """
        registry.register(sample_metadata)
        
        results = registry.find_by_capability(AnalyzerCapability.CODE_QUALITY)
        assert len(results) == 1
        assert results[0].name == "SampleAnalyzer"
    
    def test_find_by_language(
        self, registry: AnalyzerRegistry, sample_metadata: AnalyzerMetadata
    ) -> None:
        """Test finding analyzers by language.
        
        Args:
            registry: Analyzer registry
            sample_metadata: Sample metadata
        """
        registry.register(sample_metadata)
        
        results = registry.find_by_language(LanguageSupport.PYTHON)
        assert len(results) == 1
        assert results[0].name == "SampleAnalyzer"
    
    def test_find_by_language_includes_agnostic(
        self, registry: AnalyzerRegistry
    ) -> None:
        """Test that language search includes agnostic analyzers.
        
        Args:
            registry: Analyzer registry
        """
        # Register language-specific analyzer
        python_metadata = AnalyzerMetadata(
            name="PythonAnalyzer",
            capabilities={AnalyzerCapability.AST_ANALYSIS},
            languages={LanguageSupport.PYTHON},
        )
        registry.register(python_metadata)
        
        # Register agnostic analyzer
        agnostic_metadata = AnalyzerMetadata(
            name="AgnosticAnalyzer",
            capabilities={AnalyzerCapability.GIT_HISTORY},
            languages={LanguageSupport.AGNOSTIC},
        )
        registry.register(agnostic_metadata)
        
        results = registry.find_by_language(LanguageSupport.PYTHON)
        assert len(results) == 2
        names = {r.name for r in results}
        assert "PythonAnalyzer" in names
        assert "AgnosticAnalyzer" in names
    
    def test_priority_sorting(self, registry: AnalyzerRegistry) -> None:
        """Test that results are sorted by priority.
        
        Args:
            registry: Analyzer registry
        """
        # Register high priority analyzer
        high_priority = AnalyzerMetadata(
            name="HighPriority",
            capabilities={AnalyzerCapability.SECURITY},
            languages={LanguageSupport.PYTHON},
            priority=10,
        )
        registry.register(high_priority)
        
        # Register low priority analyzer
        low_priority = AnalyzerMetadata(
            name="LowPriority",
            capabilities={AnalyzerCapability.SECURITY},
            languages={LanguageSupport.PYTHON},
            priority=100,
        )
        registry.register(low_priority)
        
        results = registry.find_by_capability(AnalyzerCapability.SECURITY)
        assert len(results) == 2
        assert results[0].name == "HighPriority"
        assert results[1].name == "LowPriority"
    
    def test_get_all(self, registry: AnalyzerRegistry) -> None:
        """Test getting all analyzers.
        
        Args:
            registry: Analyzer registry
        """
        metadata1 = AnalyzerMetadata(
            name="Analyzer1",
            capabilities={AnalyzerCapability.AST_ANALYSIS},
            languages={LanguageSupport.PYTHON},
        )
        metadata2 = AnalyzerMetadata(
            name="Analyzer2",
            capabilities={AnalyzerCapability.SECURITY},
            languages={LanguageSupport.CSHARP},
        )
        
        registry.register(metadata1)
        registry.register(metadata2)
        
        all_analyzers = registry.get_all()
        assert len(all_analyzers) == 2
        names = {a.name for a in all_analyzers}
        assert "Analyzer1" in names
        assert "Analyzer2" in names


class TestAnalyzerCapabilitiesDecorator:
    """Test suite for analyzer_capabilities decorator."""
    
    def test_decorator_registers_analyzer(self) -> None:
        """Test that decorator registers analyzer."""
        # Create fresh registry for test isolation
        from cortex.lens import registry as reg_module
        original_registry = reg_module._global_registry
        test_registry = AnalyzerRegistry()
        reg_module._global_registry = test_registry
        
        try:
            @analyzer_capabilities(
                capabilities=[AnalyzerCapability.CODE_QUALITY],
                languages=[LanguageSupport.PYTHON],
                priority=20,
                description="Test analyzer",
            )
            class TestAnalyzer:
                """Test analyzer class."""
                pass
            
            # Verify registration
            metadata = test_registry.get("TestAnalyzer")
            assert metadata is not None
            assert metadata.name == "TestAnalyzer"
            assert AnalyzerCapability.CODE_QUALITY in metadata.capabilities
            assert LanguageSupport.PYTHON in metadata.languages
            assert metadata.priority == 20
            
        finally:
            # Restore original registry
            reg_module._global_registry = original_registry
    
    def test_decorator_attaches_metadata(self) -> None:
        """Test that decorator attaches metadata to class."""
        @analyzer_capabilities(
            capabilities=[AnalyzerCapability.SECURITY],
            languages=[LanguageSupport.CSHARP],
        )
        class SecureAnalyzer:
            """Security analyzer."""
            pass
        
        assert hasattr(SecureAnalyzer, "__analyzer_metadata__")
        metadata = SecureAnalyzer.__analyzer_metadata__
        assert metadata.name == "SecureAnalyzer"
    
    def test_decorator_preserves_class(self) -> None:
        """Test that decorator doesn't modify class behavior."""
        @analyzer_capabilities(
            capabilities=[AnalyzerCapability.AST_ANALYSIS],
            languages=[LanguageSupport.PYTHON],
        )
        class FunctionalAnalyzer:
            """Functional analyzer."""
            
            def analyze(self, code: str) -> str:
                """Analyze code.
                
                Args:
                    code: Source code
                
                Returns:
                    Analysis result
                """
                return f"analyzed: {code}"
        
        instance = FunctionalAnalyzer()
        result = instance.analyze("test")
        assert result == "analyzed: test"


class TestGlobalRegistry:
    """Test suite for global registry access."""
    
    def test_get_global_registry(self) -> None:
        """Test getting global registry instance."""
        registry = get_analyzer_registry()
        
        assert isinstance(registry, AnalyzerRegistry)
