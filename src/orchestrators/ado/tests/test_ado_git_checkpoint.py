"""
Task 7 (RED Phase): Git Checkpoint & Learning Tests
Tests for git checkpoint creation, Tier 2 knowledge graph updates, and execution metrics.

Test Coverage:
1. Git Checkpoint Creation
2. Checkpoint Metadata
3. Tier 2 Knowledge Graph Updates
4. ADO Pattern Learning
5. Execution Metrics Logging
6. Checkpoint Verification

Expected Methods:
- _create_git_checkpoint(message: str, tags: List[str]) → Dict
- _build_checkpoint_metadata(work_items: List[Dict], execution_time: float) → Dict
- _update_tier2_knowledge(patterns: Dict) → bool
- _extract_ado_patterns(hierarchy: Dict, api_calls: List[Dict]) → Dict
- _log_execution_metrics(metrics: Dict) → None
- _verify_checkpoint_integrity(checkpoint_id: str) → bool
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime
from src.orchestrators.ado.ado_orchestrator import ADOOrchestrator


class TestGitCheckpointCreation:
    """Test git checkpoint creation after ADO work item generation."""

    @patch('subprocess.run')
    def test_create_git_checkpoint_success(self, mock_subprocess):
        """Test successful git checkpoint creation with commit and tags."""
        orchestrator = ADOOrchestrator()
        
        # Mock successful git operations
        mock_subprocess.return_value = Mock(
            returncode=0,
            stdout='abc123\n',  # Git commit hash
            stderr=''
        )
        
        result = orchestrator._create_git_checkpoint(
            message='ADO work items created: 5 items',
            tags=['ado-checkpoint', 'task-6-complete']
        )
        
        assert result['success'] is True
        assert result['commit_hash'] == 'abc123'
        assert result['tags'] == ['ado-checkpoint', 'task-6-complete']
        assert 'timestamp' in result
        
        # Verify git add, commit, and tag commands were called
        assert mock_subprocess.call_count >= 3

    @patch('subprocess.run')
    def test_create_git_checkpoint_failure(self, mock_subprocess):
        """Test git checkpoint creation failure handling."""
        orchestrator = ADOOrchestrator()
        
        # Mock git failure
        mock_subprocess.return_value = Mock(
            returncode=1,
            stdout='',
            stderr='fatal: not a git repository'
        )
        
        result = orchestrator._create_git_checkpoint(
            message='Test checkpoint',
            tags=['test']
        )
        
        assert result['success'] is False
        assert 'error' in result
        assert 'not a git repository' in result['error']

    @patch('subprocess.run')
    def test_create_git_checkpoint_with_metadata(self, mock_subprocess):
        """Test checkpoint includes metadata in commit message."""
        orchestrator = ADOOrchestrator()
        
        mock_subprocess.return_value = Mock(returncode=0, stdout='abc123\n')
        
        result = orchestrator._create_git_checkpoint(
            message='ADO: 3 epics, 5 features, 12 stories',
            tags=['ado-v1.0']
        )
        
        # Verify commit message passed to git commit
        commit_calls = [call for call in mock_subprocess.call_args_list 
                       if 'commit' in str(call)]
        assert len(commit_calls) > 0


class TestCheckpointMetadata:
    """Test checkpoint metadata building."""

    def test_build_checkpoint_metadata_complete(self):
        """Test building complete checkpoint metadata."""
        orchestrator = ADOOrchestrator()
        
        work_items = [
            {'id': 101, 'type': 'Epic', 'title': 'User Management'},
            {'id': 102, 'type': 'Feature', 'title': 'Login'},
            {'id': 103, 'type': 'Story', 'title': 'Username/Password'}
        ]
        
        metadata = orchestrator._build_checkpoint_metadata(
            work_items=work_items,
            execution_time=45.3
        )
        
        assert metadata['work_item_count'] == 3
        assert metadata['execution_time'] == 45.3
        assert metadata['timestamp'] is not None
        assert 'work_item_types' in metadata
        assert metadata['work_item_types']['Epic'] == 1
        assert metadata['work_item_types']['Feature'] == 1
        assert metadata['work_item_types']['Story'] == 1

    def test_build_checkpoint_metadata_with_story_points(self):
        """Test metadata includes story point totals."""
        orchestrator = ADOOrchestrator()
        
        work_items = [
            {'id': 101, 'type': 'Story', 'story_points': 5},
            {'id': 102, 'type': 'Story', 'story_points': 8},
            {'id': 103, 'type': 'Task', 'story_points': 2}
        ]
        
        metadata = orchestrator._build_checkpoint_metadata(
            work_items=work_items,
            execution_time=30.0
        )
        
        assert metadata['total_story_points'] == 15
        assert metadata['average_story_points'] == 5.0


class TestTier2KnowledgeUpdate:
    """Test Tier 2 knowledge graph updates."""

    def test_update_tier2_knowledge_success(self):
        """Test successful knowledge graph update with ADO patterns."""
        # Create mock KG before importing method
        with patch('src.brain.tier2.knowledge_graph.KnowledgeGraph') as mock_kg_class, \
             patch('pathlib.Path.mkdir') as mock_mkdir:
            mock_kg_instance = MagicMock()
            mock_kg_instance.store_pattern.return_value = 'pattern-123'
            mock_kg_class.return_value = mock_kg_instance
            # Ensure mkdir doesn't fail
            mock_mkdir.return_value = None
            
            orchestrator = ADOOrchestrator()
            orchestrator.config = {'workspace_root': '/test/workspace'}
            orchestrator.logger = MagicMock()  # Mock logger to avoid issues
            
            patterns = {
                'complexity_level': 'HIGH',
                'ado_api_version': '7.1',
                'authentication_method': 'PAT_token',
                'work_item_hierarchy': ['Epic', 'Feature', 'Story', 'Task'],
                'story_point_mapping': 'Fibonacci',
                'parent_child_linking': 'System.LinkTypes.Hierarchy-Reverse'
            }
            
            result = orchestrator._update_tier2_knowledge(patterns)
            
            assert result is True
            mock_kg_instance.store_pattern.assert_called_once()

    def test_update_tier2_knowledge_failure(self):
        """Test knowledge graph update failure handling."""
        # Create mock KG with failure
        with patch('src.brain.tier2.knowledge_graph.KnowledgeGraph') as mock_kg_class:
            mock_kg_instance = MagicMock()
            mock_kg_instance.store_pattern.side_effect = Exception('Database connection failed')
            mock_kg_class.return_value = mock_kg_instance
            
            orchestrator = ADOOrchestrator()
            orchestrator.config = {'workspace_root': '/test/workspace'}
            orchestrator.logger = MagicMock()  # Mock logger
            
            patterns = {'test_pattern': 'value'}
            result = orchestrator._update_tier2_knowledge(patterns)
            
            assert result is False


class TestADOPatternExtraction:
    """Test ADO pattern extraction from execution."""

    def test_extract_ado_patterns_from_hierarchy(self):
        """Test pattern extraction from work item hierarchy."""
        orchestrator = ADOOrchestrator()
        
        hierarchy = {
            'complexity': 'HIGH',
            'work_items': [
                {'type': 'Epic', 'story_points': 21},
                {'type': 'Feature', 'story_points': 8},
                {'type': 'Story', 'story_points': 3}
            ]
        }
        
        api_calls = [
            {'method': 'POST', 'endpoint': '/workitems/$Epic', 'status': 200},
            {'method': 'POST', 'endpoint': '/workitems/$Feature', 'status': 200},
            {'method': 'PATCH', 'endpoint': '/workitems/102', 'status': 200}
        ]
        
        patterns = orchestrator._extract_ado_patterns(hierarchy, api_calls)
        
        assert patterns['complexity_level'] == 'HIGH'
        assert patterns['hierarchy_depth'] == 3
        assert patterns['api_calls_made'] == 3
        assert patterns['success_rate'] == 100.0
        assert 'work_item_types_used' in patterns

    def test_extract_ado_patterns_with_failures(self):
        """Test pattern extraction includes failure metrics."""
        orchestrator = ADOOrchestrator()
        
        hierarchy = {'complexity': 'MEDIUM', 'work_items': []}
        api_calls = [
            {'method': 'POST', 'status': 200},
            {'method': 'POST', 'status': 400},
            {'method': 'POST', 'status': 200}
        ]
        
        patterns = orchestrator._extract_ado_patterns(hierarchy, api_calls)
        
        assert patterns['success_rate'] == 66.67  # 2 out of 3 successful
        assert patterns['failure_count'] == 1


class TestExecutionMetricsLogging:
    """Test execution metrics logging."""

    def test_log_execution_metrics_complete(self):
        """Test logging complete execution metrics."""
        orchestrator = ADOOrchestrator()
        
        metrics = {
            'total_execution_time': 120.5,
            'work_items_created': 15,
            'api_calls_made': 18,
            'git_checkpoint_created': True,
            'knowledge_graph_updated': True,
            'phase_timings': {
                'DISCOVERY': 10.2,
                'VALIDATION': 5.8,
                'GENERATION': 45.3,
                'APPROVAL': 30.1,
                'EXECUTION': 25.6,
                'COMPLETION': 3.5
            }
        }
        
        # Should not raise exception
        result = orchestrator._log_execution_metrics(metrics)
        
        assert result is None  # Logging methods typically return None

    def test_log_execution_metrics_writes_to_file(self):
        """Test metrics are written to metrics file."""
        orchestrator = ADOOrchestrator()
        
        with patch('builtins.open', create=True) as mock_open:
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file
            
            metrics = {'test_metric': 123}
            orchestrator._log_execution_metrics(metrics)
            
            # Verify file was opened for writing
            mock_open.assert_called_once()
            # Verify write was called
            assert mock_file.write.called or mock_file.writelines.called


class TestCheckpointVerification:
    """Test checkpoint integrity verification."""

    @patch('subprocess.run')
    def test_verify_checkpoint_integrity_success(self, mock_subprocess):
        """Test successful checkpoint verification."""
        orchestrator = ADOOrchestrator()
        
        # Mock git show command success
        mock_subprocess.return_value = Mock(
            returncode=0,
            stdout='commit abc123\nAuthor: Test\nDate: 2024-12-20\n\nADO checkpoint',
            stderr=''
        )
        
        result = orchestrator._verify_checkpoint_integrity('abc123')
        
        assert result is True

    @patch('subprocess.run')
    def test_verify_checkpoint_integrity_failure(self, mock_subprocess):
        """Test checkpoint verification with invalid commit hash."""
        orchestrator = ADOOrchestrator()
        
        # Mock git show command failure
        mock_subprocess.return_value = Mock(
            returncode=1,
            stdout='',
            stderr='fatal: bad object abc123'
        )
        
        result = orchestrator._verify_checkpoint_integrity('abc123')
        
        assert result is False
