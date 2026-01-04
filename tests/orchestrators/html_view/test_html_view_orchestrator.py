"""
Tests for HTML View Orchestrator.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.orchestrators.html_view.html_view_orchestrator import (
    HTMLViewOrchestrator,
    detect_html_view_command
)
from src.orchestrators.base.base_orchestrator_v4_1 import (
    OrchestratorStatus,
    OrchestratorResult
)


@pytest.fixture
def mock_state_db():
    """Mock PlanningStateDB."""
    db = Mock()
    db.create_plan.return_value = "test-plan-123"
    db.complete_plan.return_value = None
    db.save_phase_result.return_value = None
    return db


@pytest.fixture
def temp_html_file(tmp_path):
    """Create temporary HTML file for testing."""
    html_file = tmp_path / "test.html"
    html_file.write_text("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test HTML</title>
        <style>
            .tier-card { padding: 1rem; }
        </style>
    </head>
    <body>
        <h1>Test Page</h1>
        <p>This is a test paragraph.</p>
        <p>Another paragraph here.</p>
        <div class="tier-card">Card content</div>
    </body>
    </html>
    """)
    return html_file


@pytest.fixture
def temp_learning_system(tmp_path):
    """Create temporary learning system file."""
    import yaml
    
    learning_dir = tmp_path / "cortex-brain" / "tier2"
    learning_dir.mkdir(parents=True, exist_ok=True)
    
    learning_file = learning_dir / "html-view-requirements.yaml"
    learning_data = {
        'schema_version': '1.0',
        'last_updated': datetime.now().isoformat(),
        'visual_patterns': {
            'patterns': [
                {
                    'id': 'VP001',
                    'name': 'Test Pattern',
                    'created': '2026-01-04',
                    'visual_impact': 'high'
                }
            ]
        },
        'spacing_rules': {
            'rules': []
        }
    }
    
    with open(learning_file, 'w') as f:
        yaml.dump(learning_data, f)
    
    return learning_file


class TestHTMLViewOrchestrator:
    """Test HTML View Orchestrator functionality."""
    
    def test_initialization(self, mock_state_db):
        """Test orchestrator initializes correctly."""
        orchestrator = HTMLViewOrchestrator(
            config_path="cortex-brain/manifests/orchestrators/html-view-orchestrator-manifest.yaml",
            state_db=mock_state_db
        )
        
        assert orchestrator is not None
        assert orchestrator.state_db == mock_state_db
        assert orchestrator.target_file is None
        assert orchestrator.mode == ""
        assert isinstance(orchestrator.issues_identified, list)
        assert isinstance(orchestrator.learning_system, dict)
    
    def test_loading_learning_system(self, mock_state_db, temp_learning_system, monkeypatch):
        """Test learning system loads from Tier 2."""
        # Monkeypatch the learning system path
        monkeypatch.setattr(
            'src.orchestrators.html_view.html_view_orchestrator.Path',
            lambda x: temp_learning_system.parent.parent.parent / x if 'cortex-brain' in str(x) else Path(x)
        )
        
        orchestrator = HTMLViewOrchestrator(
            config_path="cortex-brain/manifests/orchestrators/html-view-orchestrator-manifest.yaml",
            state_db=mock_state_db
        )
        
        # Should have loaded the test pattern
        assert 'visual_patterns' in orchestrator.learning_system
    
    def test_analyze_html_issues(self, mock_state_db, temp_html_file):
        """Test HTML issue analysis."""
        orchestrator = HTMLViewOrchestrator(
            config_path="cortex-brain/manifests/orchestrators/html-view-orchestrator-manifest.yaml",
            state_db=mock_state_db
        )
        
        # Read HTML content
        with open(temp_html_file, 'r') as f:
            html_content = f.read()
        
        # Analyze issues
        issues = orchestrator._analyze_html_issues(html_content)
        
        assert isinstance(issues, list)
        assert len(issues) >= 1  # Should find at least missing diagrams
        
        # Check issue structure
        if issues:
            issue = issues[0]
            assert 'name' in issue
            assert 'description' in issue
            assert 'solution' in issue
            assert 'impact' in issue
            assert 'effort' in issue
    
    def test_inventory_components(self, mock_state_db, temp_html_file):
        """Test component inventory."""
        orchestrator = HTMLViewOrchestrator(
            config_path="cortex-brain/manifests/orchestrators/html-view-orchestrator-manifest.yaml",
            state_db=mock_state_db
        )
        
        # Read HTML content
        with open(temp_html_file, 'r') as f:
            html_content = f.read()
        
        # Inventory components
        inventory = orchestrator._inventory_components(html_content)
        
        assert isinstance(inventory, dict)
        assert 'tier_cards' in inventory
        assert 'stat_badges' in inventory
        assert 'example_tiles' in inventory
        assert 'diagrams' in inventory
        assert inventory['tier_cards'] == 1  # One .tier-card in test HTML
    
    def test_identify_design_gaps(self, mock_state_db, temp_html_file):
        """Test design gap identification."""
        orchestrator = HTMLViewOrchestrator(
            config_path="cortex-brain/manifests/orchestrators/html-view-orchestrator-manifest.yaml",
            state_db=mock_state_db
        )
        
        # Read HTML content
        with open(temp_html_file, 'r') as f:
            html_content = f.read()
        
        # Identify gaps
        gaps = orchestrator._identify_design_gaps(html_content)
        
        assert isinstance(gaps, list)
        assert len(gaps) > 0  # Should find gaps in basic HTML
        assert any('glassmorphism' in gap.lower() for gap in gaps)
    
    def test_execute_fix_visual_issues_mode(self, mock_state_db, temp_html_file):
        """Test fix_visual_issues mode execution."""
        orchestrator = HTMLViewOrchestrator(
            config_path="cortex-brain/manifests/orchestrators/html-view-orchestrator-manifest.yaml",
            state_db=mock_state_db
        )
        
        # Execute with mock phases
        with patch.object(orchestrator, '_phase_discovery') as mock_discovery, \
             patch.object(orchestrator, '_phase_css_enhancement') as mock_css, \
             patch.object(orchestrator, '_phase_html_restructuring') as mock_html, \
             patch.object(orchestrator, '_phase_learning_capture') as mock_learning:
            
            result = orchestrator.execute(
                target_file=str(temp_html_file),
                mode="fix_visual_issues"
            )
            
            # Verify phases called
            mock_discovery.assert_called_once()
            mock_css.assert_called_once()
            mock_html.assert_called_once()
            mock_learning.assert_called_once()
            
            # Verify result
            assert isinstance(result, OrchestratorResult)
            assert result.orchestrator == "html_view_orchestrator"
            assert result.status == OrchestratorStatus.COMPLETED
            assert result.plan_id == "test-plan-123"
    
    def test_execute_full_workflow_mode(self, mock_state_db, temp_html_file):
        """Test full_workflow mode execution."""
        orchestrator = HTMLViewOrchestrator(
            config_path="cortex-brain/manifests/orchestrators/html-view-orchestrator-manifest.yaml",
            state_db=mock_state_db
        )
        
        # Execute with mock phases
        with patch.object(orchestrator, '_phase_discovery') as mock_discovery, \
             patch.object(orchestrator, '_phase_planning') as mock_planning, \
             patch.object(orchestrator, '_phase_css_enhancement') as mock_css, \
             patch.object(orchestrator, '_phase_html_restructuring') as mock_html, \
             patch.object(orchestrator, '_phase_validation') as mock_validation, \
             patch.object(orchestrator, '_phase_learning_capture') as mock_learning:
            
            result = orchestrator.execute(
                target_file=str(temp_html_file),
                mode="full_workflow"
            )
            
            # Verify all 6 phases called
            mock_discovery.assert_called_once()
            mock_planning.assert_called_once()
            mock_css.assert_called_once()
            mock_html.assert_called_once()
            mock_validation.assert_called_once()
            mock_learning.assert_called_once()
            
            # Verify result
            assert isinstance(result, OrchestratorResult)
            assert result.status == OrchestratorStatus.COMPLETED
    
    def test_execute_error_handling(self, mock_state_db):
        """Test error handling during execution."""
        orchestrator = HTMLViewOrchestrator(
            config_path="cortex-brain/manifests/orchestrators/html-view-orchestrator-manifest.yaml",
            state_db=mock_state_db
        )
        
        # Force error by using invalid mode
        result = orchestrator.execute(
            target_file="nonexistent.html",
            mode="invalid_mode"
        )
        
        # Verify failure result
        assert isinstance(result, OrchestratorResult)
        assert result.status == OrchestratorStatus.FAILED
        assert len(result.errors) > 0


class TestCommandDetection:
    """Test command pattern detection."""
    
    def test_build_html_view_pattern(self):
        """Test 'build html view for X' pattern."""
        result = detect_html_view_command("build html view for four-tier brain")
        
        assert result is not None
        assert result['mode'] == 'full_workflow'
        assert 'four-tier brain' in result['target_file']
    
    def test_fix_visual_issues_pattern(self):
        """Test 'fix visual issues in X' pattern."""
        result = detect_html_view_command("fix visual issues in tier details tab")
        
        assert result is not None
        assert result['mode'] == 'fix_visual_issues'
        assert 'tier details tab' in result['target_file']
    
    def test_standardize_glassmorphism_pattern(self):
        """Test 'standardize X to glassmorphism' pattern."""
        result = detect_html_view_command("standardize dashboard to glassmorphism")
        
        assert result is not None
        assert result['mode'] == 'standardize_glassmorphism'
        assert 'dashboard' in result['target_file']
    
    def test_add_diagram_pattern(self):
        """Test 'add diagram to X showing Y' pattern."""
        result = detect_html_view_command("add diagram to Tier 0 showing SKULL rules")
        
        assert result is not None
        assert result['mode'] == 'add_diagram'
        assert 'Tier 0' in result['target_file']
        assert result['diagram_content'] == 'SKULL rules'
    
    def test_make_responsive_pattern(self):
        """Test 'make X responsive' pattern."""
        result = detect_html_view_command("make tier cards responsive")
        
        assert result is not None
        assert result['mode'] == 'make_responsive'
        assert 'tier cards' in result['target_file']
    
    def test_no_match(self):
        """Test input that doesn't match any pattern."""
        result = detect_html_view_command("this is not a valid command")
        
        assert result is None


class TestBrainIntegration:
    """Test brain tier integrations."""
    
    def test_tier0_skull_rules_reference(self, mock_state_db):
        """Test that orchestrator references Tier 0 SKULL rules."""
        orchestrator = HTMLViewOrchestrator(
            config_path="cortex-brain/manifests/orchestrators/html-view-orchestrator-manifest.yaml",
            state_db=mock_state_db
        )
        
        # Check config has brain_protection section
        assert 'brain_protection' in orchestrator.config
        assert 'rules' in orchestrator.config['brain_protection']
    
    def test_tier1_state_tracking(self, mock_state_db):
        """Test Tier 1 state tracking via PlanningStateDB."""
        orchestrator = HTMLViewOrchestrator(
            config_path="cortex-brain/manifests/orchestrators/html-view-orchestrator-manifest.yaml",
            state_db=mock_state_db
        )
        
        # Execute should create plan
        with patch.object(orchestrator, '_execute_fix_visual_issues'):
            orchestrator.execute(
                target_file="test.html",
                mode="fix_visual_issues"
            )
        
        # Verify state DB called
        mock_state_db.create_plan.assert_called_once()
        mock_state_db.complete_plan.assert_called_once()
    
    def test_tier2_learning_system_integration(self, mock_state_db):
        """Test Tier 2 learning system saves patterns."""
        orchestrator = HTMLViewOrchestrator(
            config_path="cortex-brain/manifests/orchestrators/html-view-orchestrator-manifest.yaml",
            state_db=mock_state_db
        )
        
        # Add a pattern to capture
        orchestrator.patterns_captured = [
            {
                'id': 'VP999',
                'name': 'Test Pattern',
                'created': datetime.now().isoformat()
            }
        ]
        
        # Mock file operations
        with patch('builtins.open', create=True) as mock_open:
            orchestrator._save_learning_system()
        
        # Verify file was written (open called with 'w' mode)
        mock_open.assert_called()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
