"""
Test configuration and fixtures for documentation tests
"""

import pytest
import tempfile
import shutil
from pathlib import Path


@pytest.fixture(scope='session')
def test_workspace_template():
    """Create a reusable test workspace template"""
    temp_dir = tempfile.mkdtemp(prefix='cortex_test_')
    workspace = Path(temp_dir)
    
    # Create directory structure
    dirs = [
        'src/tier0',
        'src/tier1', 
        'src/tier2',
        'src/plugins',
        'src/agents',
        'cortex-brain',
        'docs',
        'tests'
    ]
    
    for dir_path in dirs:
        (workspace / dir_path).mkdir(parents=True, exist_ok=True)
    
    # Create sample files
    (workspace / 'cortex-brain' / 'cortex-operations.yaml').write_text("""
operations:
  plan_feature:
    description: "Interactive feature planning with DoR validation"
    status: "active"
    category: "planning"
  
  test_code:
    description: "Run unit/integration tests with coverage"
    status: "active"
    category: "testing"
""", encoding='utf-8')
    
    (workspace / 'cortex-brain' / 'module-definitions.yaml').write_text("""
modules:
  tier0_brain_protector:
    description: "SKULL protection rules enforcement"
    status: "implemented"
  
  tier1_conversation_manager:
    description: "Conversation history and context tracking"
    status: "implemented"
""", encoding='utf-8')
    
    (workspace / 'src' / 'tier0' / 'brain_protector.py').write_text("""
class BrainProtector:
    '''Enforces SKULL protection rules'''
    
    def validate(self, operation):
        '''Validate operation against protection rules'''
        pass
""", encoding='utf-8')
    
    (workspace / 'src' / 'agents' / 'planner_agent.py').write_text("""
class PlannerAgent:
    '''Interactive feature planning agent with DoR validation'''
    
    def plan_feature(self, requirements):
        '''Create structured feature plan with zero ambiguity'''
        pass
""", encoding='utf-8')
    
    (workspace / 'src' / 'plugins' / 'git_monitor.py').write_text("""
class GitMonitorPlugin:
    '''Monitors git repository for changes'''
    
    def watch(self, repo_path):
        '''Watch repository for changes'''
        pass
""", encoding='utf-8')
    
    yield workspace
    
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def isolated_workspace(test_workspace_template):
    """Create isolated workspace copy for each test"""
    temp_dir = tempfile.mkdtemp(prefix='cortex_isolated_')
    workspace = Path(temp_dir)
    
    # Copy template
    shutil.copytree(test_workspace_template, workspace, dirs_exist_ok=True)
    
    yield workspace
    
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_capabilities():
    """Mock capabilities data"""
    return {
        'op:plan_feature': {
            'name': 'plan_feature',
            'type': 'operation',
            'description': 'Interactive feature planning',
            'status': 'active'
        },
        'mod:tier0_brain_protector': {
            'name': 'tier0_brain_protector',
            'type': 'module',
            'description': 'SKULL protection enforcement',
            'status': 'implemented'
        },
        'agent:planner': {
            'name': 'PlannerAgent',
            'type': 'agent',
            'description': 'Feature planning agent',
            'status': 'active'
        },
        'plugin:git_monitor': {
            'name': 'GitMonitorPlugin',
            'type': 'plugin',
            'description': 'Git repository monitoring',
            'status': 'active'
        }
    }


@pytest.fixture
def mock_registry():
    """Mock capability registry"""
    return {
        'generated_at': '2025-11-21T12:00:00Z',
        'total_capabilities': 4,
        'by_type': {
            'operation': 1,
            'module': 1,
            'agent': 1,
            'plugin': 1
        },
        'by_status': {
            'active': 3,
            'implemented': 1
        }
    }
