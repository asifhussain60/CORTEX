# -*- coding: utf-8 -*-
"""
Tests for Token Optimization (Phase 15)

Tests compression strategies for master plan generation.
TDD: RED → GREEN → REFACTOR
"""

import pytest
from pathlib import Path
import tempfile
import shutil
import tiktoken

from src.operations.modules.planning.unified_plan_generator import UnifiedPlanGenerator


class TestTokenOptimization:
    """Test token compression strategies."""
    
    @pytest.fixture
    def encoding(self):
        """Get tiktoken encoding."""
        return tiktoken.get_encoding('cl100k_base')
    
    @pytest.fixture
    def generator(self):
        """Create generator instance."""
        return UnifiedPlanGenerator()
    
    @pytest.fixture
    def sample_phases(self):
        """Sample phases for testing."""
        return [
            {'id': '1', 'name': 'Setup', 'status': 'COMPLETE', 'tasks': []},
            {'id': '2', 'name': 'Implementation', 'status': 'IN PROGRESS', 'tasks': []},
            {'id': '3', 'name': 'Testing', 'status': 'PENDING', 'tasks': []}
        ]
    
    @pytest.fixture
    def metadata(self):
        """Sample metadata."""
        return {
            'title': 'Test Plan',
            'version': '3.1.0',
            'created_date': '2025-12-15',
            'author': 'Asif Hussain'
        }
    
    def count_tokens(self, text: str, encoding) -> int:
        """Count tokens in text."""
        return len(encoding.encode(text))
    
    def test_compressed_header_reduces_tokens(self, generator, sample_phases, metadata, encoding):
        """Header should be under 25 tokens (target: 40% reduction from 33)."""
        plan = generator.generate_master_plan(
            plan_id='test-plan',
            phases=sample_phases,
            metadata=metadata,
            compressed=True  # New parameter
        )
        
        lines = plan.split('\n')
        header_end = next((i for i, line in enumerate(lines) if '---' in line), 10)
        header = '\n'.join(lines[:header_end])
        header_tokens = self.count_tokens(header, encoding)
        
        assert header_tokens <= 25, f"Header has {header_tokens} tokens, expected <= 25"
    
    def test_compressed_continuation_prompt_reduces_tokens(self, generator, sample_phases, metadata, encoding):
        """Continuation prompt should be under 40 tokens (target: 60% reduction from 79)."""
        plan = generator.generate_master_plan(
            plan_id='test-plan',
            phases=sample_phases,
            metadata=metadata,
            compressed=True
        )
        
        lines = plan.split('\n')
        cont_start = next((i for i, line in enumerate(lines) if 'Continuation' in line), 0)
        cont_end = next((i for i, line in enumerate(lines[cont_start+1:], start=cont_start+1) if '---' in line), len(lines))
        
        cont_section = '\n'.join(lines[cont_start:cont_end])
        cont_tokens = self.count_tokens(cont_section, encoding)
        
        assert cont_tokens <= 40, f"Continuation has {cont_tokens} tokens, expected <= 40"
    
    def test_compressed_visual_tracker_reduces_tokens(self, generator, sample_phases, metadata, encoding):
        """Visual tracker should be under 70 tokens (target: 45% reduction from 101)."""
        plan = generator.generate_master_plan(
            plan_id='test-plan',
            phases=sample_phases,
            metadata=metadata,
            compressed=True
        )
        
        lines = plan.split('\n')
        tracker_start = next((i for i, line in enumerate(lines) if 'Progress' in line), 0)
        tracker_end = next((i for i, line in enumerate(lines[tracker_start+1:], start=tracker_start+1) if '---' in line), len(lines))
        
        tracker_section = '\n'.join(lines[tracker_start:tracker_end])
        tracker_tokens = self.count_tokens(tracker_section, encoding)
        
        assert tracker_tokens <= 70, f"Tracker has {tracker_tokens} tokens, expected <= 70"
    
    def test_total_plan_under_target_budget(self, generator, sample_phases, metadata, encoding):
        """Total plan should be under 320 tokens (40% reduction from 533 average)."""
        plan = generator.generate_master_plan(
            plan_id='test-plan',
            phases=sample_phases,
            metadata=metadata,
            compressed=True
        )
        
        total_tokens = self.count_tokens(plan, encoding)
        
        assert total_tokens <= 320, f"Plan has {total_tokens} tokens, expected <= 320"
    
    def test_compressed_mode_flag_works(self, generator, sample_phases, metadata, encoding):
        """Compressed mode should produce fewer tokens than verbose mode."""
        verbose_plan = generator.generate_master_plan(
            plan_id='test-plan',
            phases=sample_phases,
            metadata=metadata,
            compressed=False
        )
        
        compressed_plan = generator.generate_master_plan(
            plan_id='test-plan',
            phases=sample_phases,
            metadata=metadata,
            compressed=True
        )
        
        verbose_tokens = self.count_tokens(verbose_plan, encoding)
        compressed_tokens = self.count_tokens(compressed_plan, encoding)
        
        reduction_pct = ((verbose_tokens - compressed_tokens) / verbose_tokens) * 100
        
        assert compressed_tokens < verbose_tokens, "Compressed mode should use fewer tokens"
        assert reduction_pct >= 30, f"Expected >= 30% reduction, got {reduction_pct:.1f}%"
    
    def test_abbreviated_status_indicators(self, generator, sample_phases, metadata):
        """Status indicators should use single characters in compressed mode."""
        plan = generator.generate_master_plan(
            plan_id='test-plan',
            phases=sample_phases,
            metadata=metadata,
            compressed=True
        )
        
        # Compressed mode should not have verbose status strings
        assert 'COMPLETE' not in plan or plan.count('COMPLETE') <= 1
        assert 'PENDING' not in plan or plan.count('PENDING') <= 1
        assert 'IN PROGRESS' not in plan or plan.count('IN PROGRESS') <= 1
        
        # Should have emojis
        assert '✅' in plan
        assert '⏸️' in plan or '⏸' in plan
    
    def test_minimal_phase_table_format(self, generator, sample_phases, metadata):
        """Phase table should use abbreviated column headers in compressed mode."""
        plan = generator.generate_master_plan(
            plan_id='test-plan',
            phases=sample_phases,
            metadata=metadata,
            compressed=True
        )
        
        # Check for abbreviated headers
        lines = plan.split('\n')
        table_header = next((line for line in lines if '|' in line and 'Phase' in line), '')
        
        # Compressed headers should be short
        if table_header:
            assert len(table_header) < 60, f"Table header too long: {len(table_header)} chars"


class TestPhaseNameCompression:
    """Test phase name abbreviation."""
    
    def test_common_abbreviations(self):
        """Common terms should have abbreviations."""
        from src.operations.modules.planning.unified_plan_generator import PHASE_NAME_ABBREVIATIONS
        
        # Test common terms
        assert 'Integration' in PHASE_NAME_ABBREVIATIONS
        assert 'Implementation' in PHASE_NAME_ABBREVIATIONS
        assert 'Enhancement' in PHASE_NAME_ABBREVIATIONS
        assert 'Orchestrator' in PHASE_NAME_ABBREVIATIONS
        assert 'Architecture' in PHASE_NAME_ABBREVIATIONS
    
    def test_abbreviation_reduces_length(self):
        """Abbreviations should be shorter than originals."""
        from src.operations.modules.planning.unified_plan_generator import PHASE_NAME_ABBREVIATIONS
        
        for full, abbrev in PHASE_NAME_ABBREVIATIONS.items():
            assert len(abbrev) < len(full), f"{abbrev} not shorter than {full}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
