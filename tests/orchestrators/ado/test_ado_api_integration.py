"""
Task 6 (RED Phase): ADO API Integration Tests
Tests for Azure DevOps REST API integration methods.

Test Coverage:
1. Authentication & Configuration
2. Single Work Item Creation
3. Batch Work Item Creation
4. Parent-Child Relationship Linking
5. Error Handling & Retry Logic
6. API Response Parsing

Expected Methods:
- _authenticate_ado() → Dict[str, str]
- _create_single_work_item(work_item: Dict) → Dict
- _create_work_items_batch(work_items: List[Dict]) → Dict
- _link_parent_child_relationships(parent_id: int, child_id: int, relation_type: str) → bool
- _handle_api_errors(response: requests.Response) → Dict
- _parse_ado_response(response: requests.Response) → Dict
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.orchestrators.ado.ado_orchestrator import ADOOrchestrator


class TestADOAuthentication:
    """Test Azure DevOps authentication and configuration."""

    def test_authenticate_ado_success(self):
        """Test successful ADO authentication with PAT token."""
        orchestrator = ADOOrchestrator()
        
        # Mock configuration
        with patch.object(orchestrator, 'config', {
            'ado_organization': 'test-org',
            'ado_project': 'test-project',
            'ado_pat_token': 'test-pat-token'
        }):
            auth_result = orchestrator._authenticate_ado()
            
            assert auth_result['authenticated'] is True
            assert auth_result['organization'] == 'test-org'
            assert auth_result['project'] == 'test-project'
            assert 'headers' in auth_result
            assert 'Authorization' in auth_result['headers']
            assert auth_result['headers']['Authorization'].startswith('Basic ')

    def test_authenticate_ado_missing_credentials(self):
        """Test authentication failure with missing PAT token."""
        orchestrator = ADOOrchestrator()
        
        with patch.object(orchestrator, 'config', {
            'ado_organization': 'test-org',
            'ado_project': 'test-project',
            'ado_pat_token': None
        }):
            auth_result = orchestrator._authenticate_ado()
            
            assert auth_result['authenticated'] is False
            assert 'error' in auth_result
            assert 'missing' in auth_result['error'].lower()

    def test_authenticate_ado_base64_encoding(self):
        """Test PAT token is properly base64 encoded in Authorization header."""
        orchestrator = ADOOrchestrator()
        
        with patch.object(orchestrator, 'config', {
            'ado_organization': 'test-org',
            'ado_project': 'test-project',
            'ado_pat_token': 'my-secret-token'
        }):
            auth_result = orchestrator._authenticate_ado()
            
            # Authorization header should be "Basic <base64(':my-secret-token')>"
            import base64
            expected_encoded = base64.b64encode(b':my-secret-token').decode('utf-8')
            assert auth_result['headers']['Authorization'] == f'Basic {expected_encoded}'


class TestSingleWorkItemCreation:
    """Test single work item creation via ADO REST API."""

    @patch('requests.post')
    def test_create_single_work_item_success(self, mock_post):
        """Test successful single work item creation."""
        orchestrator = ADOOrchestrator()
        
        # Mock configuration
        orchestrator.config = {
            'ado_organization': 'test-org',
            'ado_project': 'test-project',
            'ado_pat_token': 'test-pat-token'
        }
        
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': 12345,
            'fields': {
                'System.Title': 'Test Work Item',
                'System.State': 'New',
                'System.WorkItemType': 'Task'
            }
        }
        mock_post.return_value = mock_response
        
        work_item = {
            'title': 'Test Work Item',
            'work_item_type': 'Task',
            'description': 'Test description',
            'story_points': 3
        }
        
        result = orchestrator._create_single_work_item(work_item)
        
        assert result['success'] is True
        assert result['work_item_id'] == 12345
        assert result['title'] == 'Test Work Item'
        assert result['state'] == 'New'
        
        # Verify API call was made correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert 'test-org' in call_args[0][0]  # URL contains organization
        assert 'test-project' in call_args[0][0]  # URL contains project

    @patch('requests.post')
    def test_create_single_work_item_with_fields(self, mock_post):
        """Test work item creation with all ADO fields properly formatted."""
        orchestrator = ADOOrchestrator()
        
        # Mock configuration
        orchestrator.config = {
            'ado_organization': 'test-org',
            'ado_project': 'test-project',
            'ado_pat_token': 'test-pat-token'
        }
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'id': 12345}
        mock_post.return_value = mock_response
        
        work_item = {
            'title': 'Login Feature',
            'work_item_type': 'Feature',
            'description': 'User login functionality',
            'story_points': 8,
            'acceptance_criteria': ['AC1', 'AC2'],
            'assigned_to': 'john.doe@example.com'
        }
        
        result = orchestrator._create_single_work_item(work_item)
        
        # Verify request payload structure
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        
        # ADO API expects array of operations with op, path, value
        assert isinstance(payload, list)
        assert any(item['path'] == '/fields/System.Title' for item in payload)
        assert any(item['path'] == '/fields/System.Description' for item in payload)
        assert any(item['path'] == '/fields/Microsoft.VSTS.Scheduling.StoryPoints' for item in payload)


class TestBatchWorkItemCreation:
    """Test batch work item creation via ADO REST API."""

    @patch('requests.post')
    def test_create_work_items_batch_success(self, mock_post):
        """Test successful batch creation of multiple work items."""
        orchestrator = ADOOrchestrator()
        
        # Mock configuration
        orchestrator.config = {
            'ado_organization': 'test-org',
            'ado_project': 'test-project',
            'ado_pat_token': 'test-pat-token'
        }
        
        # Mock batch API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'count': 3,
            'value': [
                {'id': 101, 'fields': {'System.Title': 'Epic 1'}},
                {'id': 102, 'fields': {'System.Title': 'Feature 1'}},
                {'id': 103, 'fields': {'System.Title': 'Story 1'}}
            ]
        }
        mock_post.return_value = mock_response
        
        work_items = [
            {'title': 'Epic 1', 'work_item_type': 'Epic'},
            {'title': 'Feature 1', 'work_item_type': 'Feature'},
            {'title': 'Story 1', 'work_item_type': 'User Story'}
        ]
        
        result = orchestrator._create_work_items_batch(work_items)
        
        assert result['success'] is True
        assert result['created_count'] == 3
        assert len(result['work_item_ids']) == 3
        assert result['work_item_ids'] == [101, 102, 103]

    @patch('requests.post')
    def test_create_work_items_batch_partial_failure(self, mock_post):
        """Test batch creation with some failures (rollback behavior)."""
        orchestrator = ADOOrchestrator()
        
        # Mock configuration
        orchestrator.config = {
            'ado_organization': 'test-org',
            'ado_project': 'test-project',
            'ado_pat_token': 'test-pat-token'
        }
        
        # Mock partial failure response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            'count': 2,
            'value': [
                {'id': 101, 'fields': {'System.Title': 'Epic 1'}},
                {'error': 'Invalid field value', 'details': 'Story points must be numeric'}
            ]
        }
        mock_post.return_value = mock_response
        
        work_items = [
            {'title': 'Epic 1', 'work_item_type': 'Epic'},
            {'title': 'Feature 1', 'work_item_type': 'Feature', 'story_points': 'invalid'}
        ]
        
        result = orchestrator._create_work_items_batch(work_items)
        
        assert result['success'] is False
        assert result['created_count'] == 1
        assert result['failed_count'] == 1
        assert 'errors' in result
        assert len(result['errors']) == 1


class TestParentChildLinking:
    """Test parent-child relationship linking between work items."""

    @patch('requests.patch')
    def test_link_parent_child_success(self, mock_patch):
        """Test successful parent-child relationship creation."""
        orchestrator = ADOOrchestrator()
        
        # Mock configuration
        orchestrator.config = {
            'ado_organization': 'test-org',
            'ado_project': 'test-project',
            'ado_pat_token': 'test-pat-token'
        }
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': 102,
            'relations': [
                {
                    'rel': 'System.LinkTypes.Hierarchy-Reverse',
                    'url': 'https://dev.azure.com/test-org/test-project/_apis/wit/workItems/101'
                }
            ]
        }
        mock_patch.return_value = mock_response
        
        result = orchestrator._link_parent_child_relationships(
            parent_id=101,
            child_id=102,
            relation_type='Parent'
        )
        
        assert result is True
        
        # Verify PATCH request was made
        mock_patch.assert_called_once()
        call_args = mock_patch.call_args
        assert '102' in call_args[0][0]  # URL contains child work item ID

    @patch('requests.patch')
    def test_link_parent_child_invalid_ids(self, mock_patch):
        """Test linking with invalid work item IDs."""
        orchestrator = ADOOrchestrator()
        
        # Mock configuration
        orchestrator.config = {
            'ado_organization': 'test-org',
            'ado_project': 'test-project',
            'ado_pat_token': 'test-pat-token'
        }
        
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {'error': 'Work item not found'}
        mock_patch.return_value = mock_response
        
        result = orchestrator._link_parent_child_relationships(
            parent_id=99999,
            child_id=88888,
            relation_type='Parent'
        )
        
        assert result is False


class TestAPIErrorHandling:
    """Test API error handling and retry logic."""

    def test_handle_api_errors_rate_limit(self):
        """Test handling of rate limit errors (429 status)."""
        orchestrator = ADOOrchestrator()
        
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {'Retry-After': '60'}
        mock_response.json.return_value = {'error': 'Rate limit exceeded'}
        
        result = orchestrator._handle_api_errors(mock_response)
        
        assert result['error_type'] == 'rate_limit'
        assert result['retry_after'] == 60
        assert result['should_retry'] is True

    def test_handle_api_errors_authentication_failure(self):
        """Test handling of authentication errors (401 status)."""
        orchestrator = ADOOrchestrator()
        
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {'error': 'Unauthorized'}
        
        result = orchestrator._handle_api_errors(mock_response)
        
        assert result['error_type'] == 'authentication'
        assert result['should_retry'] is False
        assert 'Unauthorized' in result['message']

    def test_handle_api_errors_server_error(self):
        """Test handling of server errors (500 status)."""
        orchestrator = ADOOrchestrator()
        
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {'error': 'Internal server error'}
        
        result = orchestrator._handle_api_errors(mock_response)
        
        assert result['error_type'] == 'server_error'
        assert result['should_retry'] is True
        assert result['retry_count'] == 0


class TestAPIResponseParsing:
    """Test ADO API response parsing."""

    def test_parse_ado_response_success(self):
        """Test parsing successful ADO API response."""
        orchestrator = ADOOrchestrator()
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': 12345,
            'fields': {
                'System.Title': 'Test Work Item',
                'System.State': 'New',
                'System.WorkItemType': 'Task',
                'Microsoft.VSTS.Scheduling.StoryPoints': 5
            },
            '_links': {
                'html': {'href': 'https://dev.azure.com/test-org/test-project/_workitems/edit/12345'}
            }
        }
        
        result = orchestrator._parse_ado_response(mock_response)
        
        assert result['success'] is True
        assert result['work_item_id'] == 12345
        assert result['title'] == 'Test Work Item'
        assert result['state'] == 'New'
        assert result['work_item_type'] == 'Task'
        assert result['story_points'] == 5
        assert result['url'] == 'https://dev.azure.com/test-org/test-project/_workitems/edit/12345'

    def test_parse_ado_response_error(self):
        """Test parsing ADO API error response."""
        orchestrator = ADOOrchestrator()
        
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            'error': {
                'message': 'Invalid field value',
                'details': 'Story points must be a number'
            }
        }
        
        result = orchestrator._parse_ado_response(mock_response)
        
        assert result['success'] is False
        assert result['error'] == 'Invalid field value'
        assert 'Story points must be a number' in result['details']
