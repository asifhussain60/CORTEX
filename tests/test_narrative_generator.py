"""Tests for narrative_generator.py - Context-aware code explanations."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock
from src.operations.modules.intelligence.narrative_generator import (
    NarrativeGenerator,
    CodeNarrative
)


class TestNarrativeGenerator:
    """Test suite for NarrativeGenerator class."""
    
    @pytest.fixture
    def mock_ast_engine(self):
        """Create mock AST engine."""
        engine = MagicMock()
        engine.get_architecture_insights.return_value = {
            'dependencies': [
                {'from': 'module_a.py', 'to': 'module_b.py'},
                {'from': 'module_b.py', 'to': 'module_c.py'}
            ]
        }
        return engine
        
    @pytest.fixture
    def mock_analyzers(self):
        """Create mock analyzers."""
        return {
            'deduplication': MagicMock(
                analyze=MagicMock(return_value={
                    'duplicate_groups': [
                        {'files': ['a.py', 'b.py'], 'similarity': 0.92}
                    ]
                })
            ),
            'architecture': MagicMock(
                analyze=MagicMock(return_value={
                    'violations': [
                        {'type': 'layer_violation', 'severity': 'high'}
                    ]
                })
            ),
            'code_smell': MagicMock(
                analyze=MagicMock(return_value={
                    'smells': [
                        {'type': 'long_method', 'severity': 'medium'}
                    ]
                })
            )
        }
        
    @pytest.fixture
    def generator(self, mock_ast_engine, mock_analyzers):
        """Create NarrativeGenerator instance."""
        return NarrativeGenerator(mock_ast_engine, mock_analyzers)
        
    def test_initialization(self, generator, mock_ast_engine, mock_analyzers):
        """Test generator initialization."""
        assert generator.ast_engine == mock_ast_engine
        assert generator.analyzers == mock_analyzers
        assert len(generator.templates) == 4
        assert 'architecture_change' in generator.templates
        
    def test_generate_architecture_change_narrative_high_level(self, generator):
        """Test architecture change narrative generation - high level."""
        context = {
            'changes': [
                {'file': 'auth.py', 'type': 'layer_move'},
                {'file': 'user.py', 'type': 'refactor'}
            ],
            'affected_modules': ['auth', 'user', 'api']
        }
        
        narrative = generator.generate_narrative(
            'architecture_change',
            context,
            depth='high-level'
        )
        
        assert isinstance(narrative, CodeNarrative)
        assert 'Architecture Change' in narrative.title
        assert '2 files modified' in narrative.summary
        assert narrative.technical_depth == 'high-level'
        assert len(narrative.details) == 0  # High-level has no details
        
    def test_generate_architecture_change_narrative_detailed(self, generator):
        """Test architecture change narrative generation - detailed."""
        context = {
            'changes': [{'file': 'auth.py', 'type': 'layer_move'}],
            'affected_modules': ['auth', 'user']
        }
        
        narrative = generator.generate_narrative(
            'architecture_change',
            context,
            depth='detailed'
        )
        
        assert len(narrative.details) == 3
        assert '**Files Modified:** 1' in narrative.details
        assert '**Modules Affected:** auth, user' in narrative.details
        assert '**Architecture Violations:** 1 detected' in narrative.details
        
    def test_generate_architecture_change_narrative_deep_dive(self, generator):
        """Test architecture change narrative generation - deep dive."""
        context = {
            'changes': [
                {'file': 'auth.py', 'type': 'layer_move'},
                {'file': 'user.py', 'type': 'refactor'}
            ],
            'affected_modules': ['auth']
        }
        
        narrative = generator.generate_narrative(
            'architecture_change',
            context,
            depth='deep-dive'
        )
        
        # Deep-dive includes detailed changes section
        assert any('Detailed Changes' in d for d in narrative.details)
        assert any('auth.py: layer_move' in d for d in narrative.details)
        
    def test_generate_refactor_explanation_narrative(self, generator):
        """Test refactor explanation narrative generation."""
        context = {
            'refactor_type': 'extract_method',
            'original_file': 'service.py',
            'new_structure': ['service.py', 'helpers.py', 'utils.py']
        }
        
        narrative = generator.generate_narrative(
            'refactor_explanation',
            context,
            depth='detailed'
        )
        
        assert 'Method Extraction Refactor' in narrative.title
        assert 'service.py' in narrative.summary
        assert '3 focused modules' in narrative.summary
        assert '**Refactor Type:** extract_method' in narrative.details
        assert '**Duplicates Removed:** 1' in narrative.details
        
    def test_generate_refactor_explanation_deep_dive(self, generator):
        """Test refactor explanation with deep dive depth."""
        context = {
            'refactor_type': 'extract_class',
            'original_file': 'monolith.py',
            'new_structure': ['domain.py', 'service.py']
        }
        
        narrative = generator.generate_narrative(
            'refactor_explanation',
            context,
            depth='deep-dive'
        )
        
        # Check for new structure details
        assert any('New Structure:' in d for d in narrative.details)
        assert any('domain.py' in d for d in narrative.details)
        
    def test_generate_code_explanation_narrative(self, generator):
        """Test code explanation narrative generation."""
        context = {
            'file': 'orchestrator.py',
            'function': 'execute_plan',
            'line_range': [45, 120]
        }
        
        narrative = generator.generate_narrative(
            'code_explanation',
            context,
            depth='detailed'
        )
        
        assert 'Code Explanation: execute_plan' in narrative.title
        assert 'execute_plan' in narrative.summary
        assert 'orchestrator.py' in narrative.summary
        assert '**Function:** execute_plan' in narrative.details
        assert any('**Key Operations:**' in d for d in narrative.details)
        
    def test_generate_impact_analysis_narrative(self, generator):
        """Test impact analysis narrative generation."""
        context = {
            'changed_files': ['router.py', 'analyzer.py'],
            'change_type': 'modification'
        }
        
        narrative = generator.generate_narrative(
            'impact_analysis',
            context,
            depth='detailed'
        )
        
        assert 'Impact Analysis' in narrative.title
        assert '2 files' in narrative.summary
        assert '**Changed Files:** router.py, analyzer.py' in narrative.details
        assert '**Change Type:** modification' in narrative.details
        
    def test_generate_impact_analysis_breaking_change(self, generator):
        """Test impact analysis for breaking change."""
        context = {
            'changed_files': ['api.py'],
            'change_type': 'breaking_change'
        }
        
        narrative = generator.generate_narrative(
            'impact_analysis',
            context,
            depth='detailed'
        )
        
        # Breaking changes should have warning in recommendations
        assert any('⚠️ BREAKING CHANGE' in rec for rec in narrative.recommendations)
        assert 'HIGH RISK' in narrative.impact_analysis
        
    def test_generate_impact_analysis_deep_dive(self, generator):
        """Test impact analysis with deep dive showing affected modules."""
        context = {
            'changed_files': ['core.py'],
            'change_type': 'modification'
        }
        
        narrative = generator.generate_narrative(
            'impact_analysis',
            context,
            depth='deep-dive'
        )
        
        # Deep-dive should show downstream impact
        assert any('Downstream Impact:' in d for d in narrative.details)
        
    def test_unknown_narrative_type_raises_error(self, generator):
        """Test that unknown narrative type raises ValueError."""
        with pytest.raises(ValueError, match="Unknown narrative type"):
            generator.generate_narrative(
                'unknown_type',
                {},
                depth='detailed'
            )
            
    def test_generate_change_summary_empty(self, generator):
        """Test change summary with no changes."""
        summary = generator._generate_change_summary([])
        assert summary == "No changes detected"
        
    def test_generate_change_summary_with_changes(self, generator):
        """Test change summary with changes."""
        changes = [
            {'file': 'a.py', 'type': 'refactor'},
            {'file': 'b.py', 'type': 'refactor'},
            {'file': 'c.py', 'type': 'new_feature'}
        ]
        summary = generator._generate_change_summary(changes)
        
        assert '3 files modified' in summary
        assert 'refactor' in summary or 'new_feature' in summary
        
    def test_analyze_downstream_impact_none(self, generator):
        """Test downstream impact analysis with no affected modules."""
        impact = generator._analyze_downstream_impact([])
        assert impact == "No downstream impact detected"
        
    def test_analyze_downstream_impact_limited(self, generator):
        """Test downstream impact analysis with few modules."""
        impact = generator._analyze_downstream_impact(['module_a', 'module_b'])
        assert 'Limited impact' in impact
        assert 'module_a, module_b' in impact
        
    def test_analyze_downstream_impact_moderate(self, generator):
        """Test downstream impact analysis with many modules."""
        modules = [f'module_{i}' for i in range(10)]
        impact = generator._analyze_downstream_impact(modules)
        assert 'Moderate impact' in impact
        assert '10 modules' in impact
        
    def test_refactor_type_to_title_known_types(self, generator):
        """Test refactor type conversion for known types."""
        assert generator._refactor_type_to_title('extract_method') == 'Method Extraction Refactor'
        assert generator._refactor_type_to_title('extract_class') == 'Class Extraction Refactor'
        assert generator._refactor_type_to_title('rename') == 'Rename Refactor'
        
    def test_refactor_type_to_title_unknown_type(self, generator):
        """Test refactor type conversion for unknown type."""
        title = generator._refactor_type_to_title('custom_refactor')
        assert 'Refactor: Custom Refactor' in title
        
    def test_find_dependent_modules(self, generator, mock_ast_engine):
        """Test finding dependent modules."""
        arch = {
            'dependencies': [
                {'from': 'module_a.py', 'to': 'module_b.py'},
                {'from': 'module_a.py', 'to': 'module_c.py'},
                {'from': 'module_x.py', 'to': 'module_y.py'}
            ]
        }
        
        changed_files = ['module_a.py']
        dependents = generator._find_dependent_modules(changed_files, arch)
        
        assert 'module_b.py' in dependents
        assert 'module_c.py' in dependents
        assert 'module_y.py' not in dependents
        assert len(dependents) == 2
        
    def test_calculate_risk_level_breaking_change(self, generator):
        """Test risk calculation for breaking change."""
        risk = generator._calculate_risk_level('breaking_change', 5)
        assert '🔴 HIGH RISK' in risk
        assert 'Breaking change' in risk
        
    def test_calculate_risk_level_wide_impact(self, generator):
        """Test risk calculation for wide impact non-breaking change."""
        risk = generator._calculate_risk_level('modification', 15)
        assert '🟡 MEDIUM RISK' in risk
        assert '15 modules' in risk
        
    def test_calculate_risk_level_low_risk(self, generator):
        """Test risk calculation for localized change."""
        risk = generator._calculate_risk_level('modification', 3)
        assert '🟢 LOW RISK' in risk
        assert 'Localized change' in risk


class TestCodeNarrative:
    """Test suite for CodeNarrative dataclass."""
    
    def test_code_narrative_creation(self):
        """Test CodeNarrative dataclass creation."""
        narrative = CodeNarrative(
            title="Test Narrative",
            summary="This is a test",
            details=["Detail 1", "Detail 2"],
            impact_analysis="Low impact",
            recommendations=["Do this", "Do that"],
            technical_depth="detailed"
        )
        
        assert narrative.title == "Test Narrative"
        assert narrative.summary == "This is a test"
        assert len(narrative.details) == 2
        assert narrative.impact_analysis == "Low impact"
        assert len(narrative.recommendations) == 2
        assert narrative.technical_depth == "detailed"
