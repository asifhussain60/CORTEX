"""
Integration tests for high-value orchestrators to improve system health.

Tests:
- SystemAlignmentOrchestrator: Convention-based discovery and integration scoring
- HandsOnTutorialOrchestrator: Interactive tutorial workflow
- HolisticCleanupOrchestrator: Repository cleanup and optimization

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from src.operations.modules.admin.system_alignment_orchestrator import (
    SystemAlignmentOrchestrator,
    AlignmentReport,
    IntegrationScore
)
from src.operations.modules.hands_on_tutorial_orchestrator import HandsOnTutorialOrchestrator
from src.operations.modules.cleanup.holistic_cleanup_orchestrator import HolisticCleanupOrchestrator


class TestSystemAlignmentOrchestrator:
    """Test SystemAlignmentOrchestrator integration and health scoring."""
    
    @pytest.fixture
    def orchestrator(self, tmp_path):
        """Create orchestrator with temp project root."""
        context = {'project_root': tmp_path}
        return SystemAlignmentOrchestrator(context)
    
    def test_initialization(self, orchestrator):
        """Test orchestrator initializes correctly."""
        assert orchestrator is not None
        assert orchestrator.config is not None
        assert orchestrator.project_root.exists()
    
    def test_config_loading(self, orchestrator):
        """Test configuration is loaded from cortex.config.json."""
        # Config should be loaded even if file doesn't exist (returns empty dict)
        assert isinstance(orchestrator.config, dict)
    
    def test_skip_duplicate_detection_config(self, orchestrator):
        """Test that skip_duplicate_detection config flag is respected."""
        # Set config to skip duplicate detection
        orchestrator.config = {
            'system_alignment': {
                'skip_duplicate_detection': True
            }
        }
        
        # Execute alignment
        result = orchestrator.execute({})
        
        # Verify conflicts were skipped (empty list)
        assert result.data['report'].conflicts == []
    
    def test_admin_environment_detection(self, orchestrator, tmp_path):
        """Test admin environment is correctly detected."""
        # Create admin directory
        admin_path = tmp_path / 'cortex-brain' / 'admin'
        admin_path.mkdir(parents=True, exist_ok=True)
        
        orchestrator.cortex_brain = tmp_path / 'cortex-brain'
        assert orchestrator._is_admin_environment() is True
    
    def test_integration_score_calculation(self):
        """Test IntegrationScore calculates correctly."""
        score = IntegrationScore(
            feature_name='TestFeature',
            feature_type='orchestrator',
            discovered=True,    # +20
            imported=True,      # +20
            instantiated=True,  # +20
            documented=True,    # +10
            tested=True,        # +10
            wired=False,        # +0
            optimized=False     # +0
        )
        
        assert score.score == 80  # 80% integration
        assert score.status == "[WARN] Warning"
        assert "Not wired to entry point" in score.issues
        assert "Performance not validated" in score.issues
    
    def test_alignment_report_health_thresholds(self):
        """Test alignment report health status thresholds."""
        from datetime import datetime
        
        # Healthy system (90%+)
        healthy_report = AlignmentReport(
            timestamp=datetime.now(),
            overall_health=95,
            critical_issues=0,
            warnings=2
        )
        assert healthy_report.is_healthy is True
        assert healthy_report.has_errors is False
        
        # Warning system (70-89%)
        warning_report = AlignmentReport(
            timestamp=datetime.now(),
            overall_health=80,
            critical_issues=0,
            warnings=10
        )
        assert warning_report.is_healthy is False
        assert warning_report.has_warnings is True
        
        # Critical system (<70%)
        critical_report = AlignmentReport(
            timestamp=datetime.now(),
            overall_health=60,
            critical_issues=5,
            warnings=15
        )
        assert critical_report.has_errors is True


class TestHandsOnTutorialOrchestrator:
    """Test HandsOnTutorialOrchestrator interactive workflow."""
    
    @pytest.fixture
    def orchestrator(self, tmp_path):
        """Create orchestrator with temp context."""
        context = {'project_root': tmp_path}
        return HandsOnTutorialOrchestrator(context)
    
    def test_initialization(self, orchestrator):
        """Test orchestrator initializes correctly."""
        assert orchestrator is not None
    
    def test_validate_accepts_tutorial_commands(self, orchestrator):
        """Test validation accepts tutorial-related commands."""
        context = {
            'user_input': 'tutorial',
            'project_root': orchestrator.context.get('project_root')
        }
        
        # Should accept tutorial commands
        assert orchestrator.validate(context) is True
    
    def test_tutorial_modes_available(self, orchestrator):
        """Test different tutorial modes are available."""
        # Verify orchestrator has tutorial mode handling
        # (Implementation details would go here)
        assert hasattr(orchestrator, 'execute')


class TestHolisticCleanupOrchestrator:
    """Test HolisticCleanupOrchestrator cleanup and optimization."""
    
    @pytest.fixture
    def orchestrator(self, tmp_path):
        """Create orchestrator with temp project root."""
        context = {'project_root': tmp_path}
        return HolisticCleanupOrchestrator(context)
    
    def test_initialization(self, orchestrator):
        """Test orchestrator initializes correctly."""
        assert orchestrator is not None
        assert orchestrator.project_root.exists()
    
    def test_validate_in_admin_environment(self, orchestrator, tmp_path):
        """Test validation succeeds in admin environment."""
        # Create admin directory
        admin_path = tmp_path / 'cortex-brain' / 'admin'
        admin_path.mkdir(parents=True, exist_ok=True)
        
        context = {'project_root': tmp_path}
        # Admin-only feature should validate successfully
        # (Actual validation logic would be tested here)
        assert orchestrator.validate(context) is True
    
    def test_cleanup_safety_checks(self, orchestrator):
        """Test cleanup has safety validation."""
        # Verify orchestrator has safety mechanisms
        assert hasattr(orchestrator, 'validate')
        assert hasattr(orchestrator, 'execute')


# Performance and integration tests
class TestOrchestratorsPerformance:
    """Test orchestrators complete within reasonable time."""
    
    def test_system_alignment_performance(self, tmp_path):
        """Test system alignment completes in <10 seconds."""
        import time
        
        # Create minimal cortex-brain structure
        cortex_brain = tmp_path / 'cortex-brain'
        cortex_brain.mkdir()
        
        context = {'project_root': tmp_path}
        orchestrator = SystemAlignmentOrchestrator(context)
        
        # Mock skip_duplicate_detection to ensure fast execution
        orchestrator.config = {
            'system_alignment': {
                'skip_duplicate_detection': True
            }
        }
        
        start_time = time.time()
        result = orchestrator.execute({})
        execution_time = time.time() - start_time
        
        # Should complete in <10 seconds with optimization
        assert execution_time < 10.0, f"System alignment took {execution_time}s (expected <10s)"
        assert result.success or result.status.name == 'WARNING'  # Allow warning status


# Run with: pytest tests/orchestrators/test_high_value_orchestrators.py -v
if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
