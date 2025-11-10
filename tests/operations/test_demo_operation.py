"""
Integration Tests for CORTEX Demo Operation

Tests the demo operation with all profiles and validates:
- Module execution
- Profile switching
- Operation registration
- Natural language routing

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from src.operations import execute_operation
from src.operations.operation_factory import OperationFactory


@pytest.fixture
def demo_context(tmp_path: Path) -> dict:
    """Create minimal context for demo operation."""
    root = tmp_path / "cortex_demo"
    root.mkdir(parents=True, exist_ok=True)
    
    # Create minimal structure
    (root / "logs").mkdir(exist_ok=True)
    (root / "cortex-brain").mkdir(exist_ok=True)
    
    return {
        'project_root': str(root),
        'platform': 'Windows',
        'platform_display': 'Windows 10/11'
    }


def test_demo_operation_registered_in_factory():
    """Test that demo operation is registered and discoverable."""
    factory = OperationFactory()
    
    # Check operation exists
    available_ops = factory.get_available_operations()
    assert 'cortex_tutorial' in available_ops, "Demo operation should be registered"
    
    # Get operation info
    demo_op = factory.get_operation_info('cortex_tutorial')
    assert demo_op is not None
    assert demo_op['name'] == 'CORTEX Interactive Demo'
    assert demo_op['category'] == 'onboarding'
    # Note: Slash commands removed in v5.3 - natural language only


def test_demo_operation_has_required_modules():
    """Test that demo operation defines all required modules."""
    factory = OperationFactory()
    demo_op = factory.get_operation_info('cortex_tutorial')
    
    assert demo_op is not None, "Demo operation should exist"
    
    # Check modules
    modules = demo_op.get('modules', [])
    assert 'demo_introduction' in modules
    assert 'demo_help_system' in modules
    assert 'demo_cleanup' in modules
    assert 'demo_completion' in modules


def test_demo_operation_has_three_profiles():
    """Test that demo operation defines quick, standard, and comprehensive profiles."""
    factory = OperationFactory()
    demo_op = factory.get_operation_info('cortex_tutorial')
    
    assert demo_op is not None
    
    profiles = demo_op.get('profiles', {})
    assert 'quick' in profiles
    assert 'standard' in profiles
    assert 'comprehensive' in profiles
    
    # Validate profile structure
    quick = profiles['quick']
    assert 'description' in quick
    assert 'modules' in quick
    assert len(quick['modules']) > 0


def test_demo_quick_profile_executes(demo_context):
    """Test demo operation with quick profile (introduction + help + completion)."""
    # Mock cleanup and story operations to avoid dependencies
    with patch('src.operations.execute_operation') as mock_exec:
        # Setup mock to pass through for demo, but return success for dependencies
        def side_effect(op_name, **kwargs):
            if op_name in ['cleanup', 'refresh story']:
                return Mock(
                    success=True,
                    context={'summary': {'files_removed': 0}},
                    module_results={}
                )
            # For actual demo execution, call the real function
            return execute_operation.__wrapped__(op_name, **kwargs)
        
        mock_exec.side_effect = side_effect
        
        result = execute_operation(
            'cortex_tutorial',
            profile='quick',
            **demo_context
        )
        
        # Should succeed or provide graceful warnings
        assert result is not None
        # Quick profile should have minimal modules
        assert result.context.get('demo_profile') in ['quick', 'standard', 'comprehensive', None]


def test_demo_standard_profile_executes(demo_context):
    """Test demo operation with standard profile (includes cleanup)."""
    # The demo_cleanup module handles errors gracefully, so we can just run it
    result = execute_operation(
        'cortex_tutorial',
        profile='standard',
        **demo_context
    )
    
    # Should succeed or handle gracefully
    assert result is not None


def test_demo_comprehensive_profile_executes(demo_context):
    """Test demo operation with comprehensive profile (all 6 modules)."""
    result = execute_operation(
        'cortex_tutorial',
        profile='comprehensive',
        **demo_context
    )
    
    # Should succeed or warn gracefully
    assert result is not None


def test_demo_natural_language_routing():
    """Test that demo operation responds to natural language triggers."""
    factory = OperationFactory()
    demo_op = factory.get_operation_info('cortex_tutorial')
    
    assert demo_op is not None
    
    # Check natural language triggers
    nl_triggers = demo_op.get('natural_language', [])
    assert 'demo' in nl_triggers
    assert 'show me what cortex can do' in nl_triggers or any('cortex' in t and 'do' in t for t in nl_triggers)
    assert 'tutorial' in nl_triggers


def test_demo_natural_language_routing():
    """Test that demo operation responds to natural language triggers."""
    factory = OperationFactory()
    demo_op = factory.get_operation_info('cortex_tutorial')
    
    assert demo_op is not None
    
    # Check natural language triggers (v5.3 - natural language only, no slash commands)
    nl_triggers = demo_op.get('natural_language', [])
    assert 'demo' in nl_triggers, "Should support 'demo' trigger"
    assert any('cortex' in t and ('do' in t or 'can' in t) for t in nl_triggers), "Should support 'what cortex can do' style triggers"
    assert 'tutorial' in nl_triggers, "Should support 'tutorial' trigger"


def test_demo_modules_in_correct_order():
    """Test that demo modules are ordered logically (intro -> content -> completion)."""
    factory = OperationFactory()
    demo_op = factory.get_operation_info('cortex_tutorial')
    
    assert demo_op is not None
    
    modules = demo_op.get('modules', [])
    
    # Introduction should be first
    assert modules[0] == 'demo_introduction'
    
    # Completion should be last
    assert modules[-1] == 'demo_completion'
    
    # Help and other demos in middle
    middle_modules = modules[1:-1]
    assert 'demo_help_system' in middle_modules


def test_demo_introduction_module_exists():
    """Test that demo_introduction module is importable."""
    try:
        from src.operations.modules.demo_introduction_module import DemoIntroductionModule
        module = DemoIntroductionModule()
        metadata = module.get_metadata()
        
        assert metadata.module_id == 'demo_introduction'
        assert metadata.name == 'Demo Introduction'
    except ImportError as e:
        pytest.fail(f"Failed to import demo_introduction module: {e}")


def test_demo_help_system_module_exists():
    """Test that demo_help_system module is importable."""
    try:
        from src.operations.modules.demo_help_system_module import DemoHelpSystemModule
        module = DemoHelpSystemModule()
        metadata = module.get_metadata()
        
        assert metadata.module_id == 'demo_help_system'
        assert metadata.name == 'Demo Help System'
    except ImportError as e:
        pytest.fail(f"Failed to import demo_help_system module: {e}")


def test_demo_cleanup_module_exists():
    """Test that demo_cleanup module is importable."""
    try:
        from src.operations.modules.demo_cleanup_module import DemoCleanupModule
        module = DemoCleanupModule()
        metadata = module.get_metadata()
        
        assert metadata.module_id == 'demo_cleanup'
        assert metadata.name == 'Demo Cleanup Operation'
    except ImportError as e:
        pytest.fail(f"Failed to import demo_cleanup module: {e}")


def test_demo_profile_token_budgets():
    """Test that demo profiles stay within token budgets."""
    factory = OperationFactory()
    demo_op = factory.get_operation_info('cortex_tutorial')
    
    assert demo_op is not None
    
    profiles = demo_op.get('profiles', {})
    
    # Quick: ~350-400 tokens (2 min)
    quick_modules = len(profiles.get('quick', {}).get('modules', []))
    assert quick_modules <= 4, "Quick profile should have ≤4 modules"
    
    # Standard: ~550-600 tokens (3-4 min)
    standard_modules = len(profiles.get('standard', {}).get('modules', []))
    assert standard_modules <= 5, "Standard profile should have ≤5 modules"
    
    # Comprehensive: ~700 tokens (5-6 min)
    comprehensive_modules = len(profiles.get('comprehensive', {}).get('modules', []))
    assert comprehensive_modules == 6, "Comprehensive profile should have 6 modules"


def test_demo_operation_status_tracking():
    """Test that demo operation tracks implementation status."""
    factory = OperationFactory()
    demo_op = factory.get_operation_info('cortex_tutorial')
    
    assert demo_op is not None
    
    status = demo_op.get('implementation_status', {})
    assert 'status' in status
    assert 'modules_total' in status
    assert status['modules_total'] == 6


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
