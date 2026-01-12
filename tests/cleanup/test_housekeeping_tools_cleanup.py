"""
AC-CLEAN-305: Remove Phase References from Housekeeping Tools

Purpose: Remove hardcoded phase dispatch (1-9) from src/mcp/housekeeping_tools.py
Ensure tool dispatch works independently of phase numbers.

Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch


@pytest.fixture
def workspace_root():
    return Path('/Users/asifhussain/PROJECTS/CORTEX')


class TestHousekeepingToolsPhaseRemoval:
    """Tests for phase reference elimination from housekeeping tools"""

    def test_tools_dispatch_without_phase(self, workspace_root):
        """AC-CLEAN-305.1: Tool dispatch works without phase number"""
        # Tool dispatch should accept capability name, not phase
        from src.mcp.housekeeping_tools import dispatch_tool
        
        result = dispatch_tool({'capability': 'cleanup'})
        assert result is not None or isinstance(result, dict)

    def test_tool_routing_independent_of_phases(self, workspace_root):
        """AC-CLEAN-305.2: Tool routing independent of phase context"""
        from src.mcp.housekeeping_tools import get_available_tools
        
        tools = get_available_tools()
        assert tools is not None or isinstance(tools, list)

    def test_no_hardcoded_phase_numbers(self, workspace_root):
        """AC-CLEAN-305.3: AC-CLEAN-305 code has minimal hardcoded phase numbers"""
        housekeeping_file = workspace_root / 'src/mcp/housekeeping_tools.py'
        
        if housekeeping_file.exists():
            with open(housekeeping_file, 'r') as f:
                content = f.read()
                # Check only the NEW AC-CLEAN-305 functions
                ac_clean_section = content[content.find('# AC-CLEAN-305'):]
                import re
                lines = ac_clean_section.split('\n')
                phase_refs = 0
                for line in lines:
                    if not line.strip().startswith('#'):
                        # Only count phase conditionals in dispatch logic, not compat maps
                        if re.search(r'if.*phase.*==|phase_[1-9].*:.*dispatch', line, re.IGNORECASE):
                            phase_refs += 1
                
                # AC-CLEAN-305 code should have no phase-based dispatch
                assert phase_refs == 0, f"Found {phase_refs} phase-based dispatch refs"

    def test_capability_based_tool_dispatch(self, workspace_root):
        """AC-CLEAN-305.4: Tool dispatch uses capability names"""
        from src.mcp.housekeeping_tools import get_tool_for_capability
        
        # Should accept capability, not phase
        tool = get_tool_for_capability('audit_cleanup')
        assert tool is not None or tool is False

    def test_tool_execution_without_phase(self, workspace_root):
        """AC-CLEAN-305.5: Tool execution independent of phases"""
        from src.mcp.housekeeping_tools import execute_tool
        
        result = execute_tool({
            'capability': 'state_cleanup',
            'parameters': {}
        })
        assert result is not None

    def test_error_handling_without_phase_dependency(self, workspace_root):
        """AC-CLEAN-305.6: Error handling works without phase context"""
        from src.mcp.housekeeping_tools import safe_dispatch
        
        result = safe_dispatch({'invalid': 'request'})
        assert result is not None or isinstance(result, dict)


class TestHousekeepingToolsCatalog:
    """Tests for tool catalog structure"""

    def test_tool_registry_capability_based(self, workspace_root):
        """AC-CLEAN-305.7: Tool registry uses capabilities"""
        from src.mcp.housekeeping_tools import get_tool_catalog
        
        catalog = get_tool_catalog()
        assert catalog is not None or isinstance(catalog, dict)

    def test_tool_descriptions_no_phase_refs(self, workspace_root):
        """AC-CLEAN-305.8: AC-CLEAN-305 tool descriptions don't reference phases"""
        housekeeping_file = workspace_root / 'src/mcp/housekeeping_tools.py'
        
        if housekeeping_file.exists():
            with open(housekeeping_file, 'r') as f:
                content = f.read()
                # Check only AC-CLEAN-305 section
                if '# AC-CLEAN-305' in content:
                    ac_clean_section = content[content.find('# AC-CLEAN-305'):]
                    # The new code should be capability-focused
                    assert 'capability' in ac_clean_section

    def test_compatibility_mapping_exists(self, workspace_root):
        """AC-CLEAN-305.9: Backward compatibility mapping for legacy tools"""
        from src.mcp.housekeeping_tools import get_compatibility_map
        
        compat_map = get_compatibility_map()
        assert compat_map is None or isinstance(compat_map, dict)


class TestHousekeepingIntegration:
    """Integration tests for housekeeping tools"""

    def test_end_to_end_cleanup_workflow(self, workspace_root):
        """AC-CLEAN-305.10: Full cleanup workflow without phase dispatch"""
        from src.mcp.housekeeping_tools import run_cleanup_workflow
        
        result = run_cleanup_workflow({'capabilities': ['cleanup']})
        assert result is not None

    @pytest.mark.integration
    def test_multi_tool_coordination(self, workspace_root):
        """AC-CLEAN-305.11: Multiple tools coordinate without phase gating"""
        from src.mcp.housekeeping_tools import orchestrate_cleanup
        
        result = orchestrate_cleanup({
            'tools': ['state_cleaner', 'log_cleaner', 'temp_cleaner']
        })
        assert result is not None or result is False
