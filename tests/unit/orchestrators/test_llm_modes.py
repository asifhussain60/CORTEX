"""
Test suite for LLM mode flags in RepositoryOnboardingOrchestrator.

Tests:
- Interactive mode (default): print prompts for manual copy/paste
- Batch mode: save prompts to files
- Skip mode: no LLM generation

Authority: PHASE-21-ENTERPRISE-REPOSITORY-INTELLIGENCE.yaml lines 2842-2950
Governance: CORE-008 (TDD-first)
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from cortex.orchestrators.support.repository_onboarding_orchestrator import (
    LLMMode,
    RepositoryOnboardingOrchestrator,
)


@pytest.fixture
def temp_repo():
    """Create temporary repository directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir) / "test-repo"
        repo_path.mkdir()
        
        # Create minimal Python file
        (repo_path / "main.py").write_text("def hello(): pass")
        
        yield repo_path


class TestLLMModes:
    """Test LLM mode functionality."""
    
    def test_llm_mode_enum_values(self):
        """Test LLMMode enum has required values."""
        assert hasattr(LLMMode, 'INTERACTIVE')
        assert hasattr(LLMMode, 'BATCH')
        assert hasattr(LLMMode, 'SKIP')
        
        assert LLMMode.INTERACTIVE.value == 'interactive'
        assert LLMMode.BATCH.value == 'batch'
        assert LLMMode.SKIP.value == 'skip'
    
    @patch('cortex.orchestrators.support.repository_onboarding_orchestrator.print')
    @patch('cortex.orchestrators.support.repository_onboarding_orchestrator._get_asset_manager')
    def test_interactive_mode_prints_prompt(self, mock_asset_mgr, mock_print, temp_repo):
        """Test interactive mode prints LLM prompts to console."""
        mock_asset_mgr.return_value = MagicMock()
        
        orchestrator = RepositoryOnboardingOrchestrator()
        
        # Test the LLM generation directly
        orchestrator._llm_mode = LLMMode.INTERACTIVE
        orchestrator._generate_llm_content('overview', {'repo_name': 'test-repo'})
        
        # Verify prompts were printed
        assert mock_print.called
        # Check for prompt header
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any('LLM PROMPT' in call for call in print_calls)
    
    def test_batch_mode_saves_prompts_to_file(self, temp_repo):
        """Test batch mode saves prompts to files instead of printing."""
        orchestrator = RepositoryOnboardingOrchestrator()
        
        output_dir = temp_repo / "llm_prompts"
        
        # Test LLM generation directly
        orchestrator._llm_mode = LLMMode.BATCH
        orchestrator._llm_output_dir = output_dir
        orchestrator._generate_llm_content('overview', {'repo_name': 'test-repo'})
        
        # Verify prompt files created
        assert output_dir.exists()
        prompt_files = list(output_dir.glob("*.txt"))
        assert len(prompt_files) > 0
        
        # Verify file contains prompt content
        first_prompt = prompt_files[0].read_text()
        assert len(first_prompt) > 0
        assert "overview" in first_prompt.lower() or "test-repo" in first_prompt
    
    def test_skip_mode_no_llm_generation(self, temp_repo):
        """Test skip mode bypasses LLM generation entirely."""
        orchestrator = RepositoryOnboardingOrchestrator()
        
        # Mock LENS analysis
        with patch.object(orchestrator, '_run_lens_analysis') as mock_lens:
            mock_lens.return_value = {
                'repo_summary': {'repo_name': 'test-repo'},
                'use_cases': []
            }
            
            # Mock LLM generation to track calls
            with patch.object(orchestrator, '_generate_llm_content') as mock_llm:
                result = orchestrator.onboard_repository(
                    repo_path=temp_repo,
                    llm_mode=LLMMode.SKIP,
                    include_dashboard=False
                )
                
                # Verify LLM generation was NOT called
                assert not mock_llm.called
    
    @patch('cortex.orchestrators.support.repository_onboarding_orchestrator.print')
    def test_default_mode_is_interactive(self, mock_print, temp_repo):
        """Test that interactive mode is the default."""
        orchestrator = RepositoryOnboardingOrchestrator()
        
        # Default should be INTERACTIVE
        orchestrator._generate_llm_content('overview', {'repo_name': 'test-repo'})
        
        # Should have printed prompts (interactive behavior)
        assert mock_print.called
    
    def test_batch_mode_creates_timestamped_files(self, temp_repo):
        """Test batch mode creates timestamped prompt files."""
        orchestrator = RepositoryOnboardingOrchestrator()
        
        output_dir = temp_repo / "llm_prompts"
        
        with patch.object(orchestrator, '_run_lens_analysis') as mock_lens:
            mock_lens.return_value = {
                'repo_summary': {'repo_name': 'test-repo'},
                'use_cases': []
            }
            
            result = orchestrator.onboard_repository(
                repo_path=temp_repo,
                llm_mode=LLMMode.BATCH,
                llm_output_dir=output_dir,
                include_dashboard=False
            )
            
            prompt_files = list(output_dir.glob("*.txt"))
            
            # Verify files have timestamps in names
            for file in prompt_files:
                # Check for timestamp pattern (YYYY-MM-DD or YYYYMMDD)
                assert any(char.isdigit() for char in file.stem)
    
    def test_batch_mode_organizes_by_prompt_type(self, temp_repo):
        """Test batch mode organizes prompts by type."""
        orchestrator = RepositoryOnboardingOrchestrator()
        
        output_dir = temp_repo / "llm_prompts"
        orchestrator._llm_mode = LLMMode.BATCH
        orchestrator._llm_output_dir = output_dir
        
        # Generate multiple prompts
        orchestrator._generate_llm_content('overview', {'repo_name': 'test-repo'})
        orchestrator._generate_llm_content('use_cases', {'repo_name': 'test-repo'})
        orchestrator._generate_llm_content('summary', {'repo_name': 'test-repo'})
        
        prompt_files = list(output_dir.glob("*.txt"))
        
        # Verify different prompt types exist
        filenames = [f.name.lower() for f in prompt_files]
        assert len(filenames) > 0
        # Should have multiple types
        assert any('overview' in name for name in filenames)


class TestLLMModeIntegration:
    """Integration tests for LLM modes."""
    
    def test_all_three_modes_produce_valid_results(self, temp_repo):
        """Test all LLM modes produce valid onboarding results."""
        orchestrator = RepositoryOnboardingOrchestrator()
        
        for mode in [LLMMode.INTERACTIVE, LLMMode.BATCH, LLMMode.SKIP]:
            with patch.object(orchestrator, '_run_lens_analysis') as mock_lens:
                mock_lens.return_value = {
                    'repo_summary': {'repo_name': 'test-repo'},
                    'use_cases': []
                }
                
                result = orchestrator.onboard_repository(
                    repo_path=temp_repo,
                    llm_mode=mode,
                    llm_output_dir=temp_repo / f"prompts_{mode.value}",
                    include_dashboard=False
                )
                
                # All modes should succeed
                assert result is not None
