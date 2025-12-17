"""
Test token display enhancements (K/M formatting, clarity, continuation removal, manifest refs).

Tests:
- K/M suffix formatting
- "saved" label clarity
- Continuation prompt removal for completed plans
- Shortened labels in verbose mode
- Ultra-compact continuation prompt with manifest reference
"""

import pytest
import tiktoken
from src.operations.modules.planning.unified_plan_generator import UnifiedPlanGenerator
from src.operations.modules.planning.token_reduction_tracker import TokenReductionTracker


class TestTokenDisplayEnhancements:
    """Test suite for token display improvements."""
    
    @pytest.fixture
    def generator(self):
        """Create generator instance."""
        return UnifiedPlanGenerator()
    
    @pytest.fixture
    def tracker(self):
        """Create tracker instance."""
        return TokenReductionTracker()
    
    def test_k_suffix_formatting(self, tracker):
        """Test tokens display with K suffix (1,000-999,999)."""
        assert tracker.format_tokens(1000) == "1.0K"
        assert tracker.format_tokens(1584) == "1.6K"
        assert tracker.format_tokens(50000) == "50.0K"
        assert tracker.format_tokens(106349) == "106.3K"
    
    def test_m_suffix_formatting(self, tracker):
        """Test tokens display with M suffix (1,000,000+)."""
        assert tracker.format_tokens(1000000) == "1.0M"
        assert tracker.format_tokens(1500000) == "1.5M"
        assert tracker.format_tokens(6705880) == "6.7M"
    
    def test_small_numbers_no_suffix(self, tracker):
        """Test small numbers display without suffix (<1000)."""
        assert tracker.format_tokens(0) == "0"
        assert tracker.format_tokens(500) == "500"
        assert tracker.format_tokens(999) == "999"
    
    def test_saved_label_optional(self, tracker):
        """Test optional 'saved' label for clarity."""
        # Without label
        assert tracker.format_tokens(1584, include_label=False) == "1.6K"
        
        # With label
        assert tracker.format_tokens(1584, include_label=True) == "1.6K saved"
        assert tracker.format_tokens(106349, include_label=True) == "106.3K saved"
        assert tracker.format_tokens(6705880, include_label=True) == "6.7M saved"
    
    def test_continuation_prompt_present_when_incomplete(self, generator):
        """Test continuation prompt appears for incomplete plans."""
        phases = [
            {'id': 1, 'status': 'complete', 'actual': '1h', 'elapsed': '1.5h'},
            {'id': 2, 'status': 'pending', 'actual': '-', 'elapsed': '-'}
        ]
        
        metadata = {
            'title': 'Test', 'date': '2025-12-15', 'complexity_tier': '2',
            'baseline_tokens': 1000, 'current_tokens': 500, 'total_files': 10
        }
        
        plan = generator.generate_master_plan('test-plan', phases, metadata, compressed=False)
        
        assert '## 🔄 Continuation Prompt' in plan
    
    def test_continuation_prompt_removed_when_complete(self, generator):
        """Test continuation prompt removed for 100% complete plans."""
        phases = [
            {'id': 1, 'status': 'complete', 'actual': '1h', 'elapsed': '1.5h'},
            {'id': 2, 'status': 'complete', 'actual': '2h', 'elapsed': '2.5h'}
        ]
        
        metadata = {
            'title': 'Test', 'date': '2025-12-15', 'complexity_tier': '2',
            'baseline_tokens': 1000, 'current_tokens': 500, 'total_files': 10
        }
        
        plan = generator.generate_master_plan('test-plan', phases, metadata, compressed=False)
        
        # Should NOT contain continuation prompt
        assert '## 🔄 Continuation Prompt' not in plan
        assert '## 🔄 Continue' not in plan
    
    def test_verbose_mode_uses_saved_label(self, generator):
        """Test verbose mode displays 'X saved' format."""
        phases = [{'id': 1, 'status': 'complete', 'actual': '1h', 'elapsed': '1.5h'}]
        
        metadata = {
            'title': 'Test', 'date': '2025-12-15', 'complexity_tier': '2',
            'baseline_tokens': 100000, 'current_tokens': 50000, 'total_files': 100
        }
        
        plan = generator.generate_master_plan('test-plan', phases, metadata, compressed=False)
        
        # Should contain "50.0K saved" format
        assert '50.0K saved' in plan or '50000 saved' in plan
    
    def test_compressed_mode_uses_saved_label(self, generator):
        """Test compressed mode displays 'Saved:' with label."""
        phases = [{'id': 1, 'status': 'complete', 'actual': '1h', 'elapsed': '1.5h'}]
        
        metadata = {
            'title': 'Test', 'date': '2025-12-15', 'complexity_tier': '2',
            'baseline_tokens': 100000, 'current_tokens': 50000, 'total_files': 100
        }
        
        plan = generator.generate_master_plan('test-plan', phases, metadata, compressed=True)
        
        # Should use "Saved:" instead of "Tokens:"
        assert '**Saved:**' in plan
        assert '50.0K saved' in plan
    
    def test_verbose_mode_shortened_labels(self, generator):
        """Test verbose mode uses shortened labels."""
        phases = [{'id': 1, 'status': 'complete', 'actual': '1h', 'elapsed': '1.5h'}]
        
        metadata = {
            'title': 'Test', 'date': '2025-12-15', 'complexity_tier': '2',
            'baseline_tokens': 100000, 'current_tokens': 50000, 'total_files': 100
        }
        
        plan = generator.generate_master_plan('test-plan', phases, metadata, compressed=False)
        
        # Should use "Token Reduction:" not "Overall Token Reduction:"
        assert 'Token Reduction:' in plan
        
        # Should use "Baseline:" not "Baseline established:"
        assert '*Baseline:' in plan
    
    def test_empty_plan_continuation_removed(self, generator):
        """Test empty/all-complete plan has no continuation prompt."""
        phases = []  # Empty plan
        
        metadata = {
            'title': 'Test', 'date': '2025-12-15', 'complexity_tier': '2',
            'baseline_tokens': 1000, 'current_tokens': 1000, 'total_files': 10
        }
        
        plan = generator.generate_master_plan('test-plan', phases, metadata, compressed=False)
        
        # Empty plan should not have continuation
        assert '## 🔄' not in plan
    
    def test_ultra_compact_continuation_prompt(self, generator):
        """Test ultra-compact continuation prompt (<20 tokens without manifest)."""
        prompt = generator.generate_continuation_prompt(
            plan_id='test-plan',
            completed_phases=2,
            total_phases=5,
            next_phase_number=3,
            next_phase_name='Implementation',
            progress_percentage=40,
            manifest_path=None
        )
        
        enc = tiktoken.get_encoding('cl100k_base')
        tokens = len(enc.encode(prompt))
        
        # Should be ultra-compact (< 20 tokens target)
        assert tokens < 20
        assert 'test-plan' in prompt
        assert '40%' in prompt
        assert 'Phase 3' in prompt
    
    def test_continuation_with_manifest_reference(self, generator):
        """Test continuation prompt includes manifest path for rich context."""
        prompt = generator.generate_continuation_prompt(
            plan_id='cortex-rearchitecture-v1',
            completed_phases=6,
            total_phases=17,
            next_phase_number=2,
            next_phase_name='Semantic Folder Organization',
            progress_percentage=35,
            manifest_path='cortex-brain/manifests/orchestrators/planning-system-3.0-manifest.yaml'
        )
        
        # Should include manifest reference
        assert 'Manifest:' in prompt
        assert 'planning-system-3.0-manifest.yaml' in prompt
        
        enc = tiktoken.get_encoding('cl100k_base')
        tokens = len(enc.encode(prompt))
        
        # With manifest should be < 50 tokens (still compact)
        assert tokens < 50
    
    def test_manifest_token_tradeoff(self, generator):
        """Test manifest adds minimal tokens for massive context gain."""
        enc = tiktoken.get_encoding('cl100k_base')
        
        # Without manifest
        prompt_no_manifest = generator.generate_continuation_prompt(
            'test', 1, 5, 2, 'Phase', 20, manifest_path=None
        )
        tokens_no_manifest = len(enc.encode(prompt_no_manifest))
        
        # With manifest
        prompt_with_manifest = generator.generate_continuation_prompt(
            'test', 1, 5, 2, 'Phase', 20, 
            manifest_path='cortex-brain/manifests/orchestrators/planning-system-3.0-manifest.yaml'
        )
        tokens_with_manifest = len(enc.encode(prompt_with_manifest))
        
        token_increase = tokens_with_manifest - tokens_no_manifest
        
        # Should add ~20-30 tokens for path
        assert 15 < token_increase < 35
        
        # But gives access to full manifest (400+ lines, DoR/DoD/TDD/phases)
        # This is the benefit: +25 tokens = access to ~15K tokens of context
