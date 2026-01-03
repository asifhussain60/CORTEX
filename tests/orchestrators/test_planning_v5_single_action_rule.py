"""
Tests for Planning Orchestrator v5 Single Action Rule compliance.

Validates that Planning v5 generates plans compliant with Response Architecture v4.0.4:
- Plans end with EXACTLY ONE next step
- No multiple options presented
- Clear action with value/benefit justification
"""

import pytest
import re
from pathlib import Path
from unittest.mock import Mock, patch
import tempfile
import shutil

from src.orchestrators.planning.planning_orchestrator_v5 import PlanningOrchestratorV5
from src.database.planning_state_db import PlanningStateDB


class TestPlanningV5SingleActionRule:
    """Test suite for Single Action Rule compliance in Planning v5."""
    
    def test_plan_template_single_action_compliance(self):
        """Test that Planning v5 plan template follows Single Action Rule."""
        # Read the orchestrator source code
        orchestrator_path = Path("src/orchestrators/planning/planning_orchestrator_v5.py")
        
        if not orchestrator_path.exists():
            pytest.skip("Planning Orchestrator v5 not found")
        
        source_code = orchestrator_path.read_text()
        
        # Find the plan generation template
        plan_template_match = re.search(
            r'plan_content = f"""(.*?)"""',
            source_code,
            re.DOTALL
        )
        
        assert plan_template_match, "Plan template not found in source code"
        
        plan_template = plan_template_match.group(1)
        
        # Check for Single Action Rule compliance
        assert "## 📝 Next Step" in plan_template, \
            "Plan template must have 'Next Step' section (singular)"
        assert "## 📝 Next Steps" not in plan_template, \
            "Plan template must NOT have 'Next Steps' section (plural)"
        
        # Check for compliance marker
        assert "Single Action Rule v4.0.4" in plan_template, \
            "Plan template must include 'Single Action Rule v4.0.4' compliance marker"
        
        # Check for forbidden numbered list in Next Step section
        next_step_section = re.search(
            r'## 📝 Next Step(.*?)(?=\n##|\Z)',
            plan_template,
            re.DOTALL
        )
        
        if next_step_section:
            next_step_text = next_step_section.group(1)
            
            # Should not have numbered lists
            numbered_list_pattern = r'^\s*\d+\.\s+(Begin|Create|Write|Update)'
            numbered_lists = re.findall(numbered_list_pattern, next_step_text, re.MULTILINE)
            
            assert len(numbered_lists) == 0, \
                f"Next Step section must not contain numbered task lists. Found: {numbered_lists}"
            
            # Should have **Next:** format
            assert "**Next:**" in next_step_text, \
                "Next Step section must use **Next:** format"
    
    def test_no_multiple_options_in_template(self):
        """Test that plan template doesn't present multiple options."""
        orchestrator_path = Path("src/orchestrators/planning/planning_orchestrator_v5.py")
        
        if not orchestrator_path.exists():
            pytest.skip("Planning Orchestrator v5 not found")
        
        source_code = orchestrator_path.read_text()
        
        # Find the plan generation template
        plan_template_match = re.search(
            r'plan_content = f"""(.*?)"""',
            source_code,
            re.DOTALL
        )
        
        assert plan_template_match, "Plan template not found in source code"
        
        plan_template = plan_template_match.group(1)
        
        # Extract Next Step section
        next_step_section = re.search(
            r'## 📝 Next Step(.*?)(?=\n##|\Z)',
            plan_template,
            re.DOTALL
        )
        
        if next_step_section:
            next_step_text = next_step_section.group(1)
            
            # Check for forbidden patterns (case-insensitive)
            forbidden_patterns = [
                r'\b(option|choice)\s+\d+',  # Option 1, Choice 2
                r'\d+\.\s+\w+.*\n.*\d+\.',   # Numbered lists
            ]
            
            for pattern in forbidden_patterns:
                matches = re.search(pattern, next_step_text, re.IGNORECASE)
                assert not matches, \
                    f"Next Step contains forbidden pattern: {pattern} -> {matches.group(0) if matches else ''}"


class TestSingleActionRuleValidation:
    """Test Single Action Rule validation logic."""
    
    def test_valid_single_action_patterns(self):
        """Test detection of valid single action patterns."""
        valid_patterns = [
            "**Next:** Run tests (validates implementation)",
            "Say `continue` to proceed",
            "✅ All work complete!",
            "**Next:** Deploy to staging (unblocks QA team)"
        ]
        
        # Pattern from response-templates-v4.yaml
        valid_pattern_regex = r'^(\*\*Next:\*\*.*\(.*\)|Say |✅)'
        
        for text in valid_patterns:
            assert re.match(valid_pattern_regex, text, re.MULTILINE), \
                f"Valid pattern not recognized: {text}"
    
    def test_forbidden_multiple_option_patterns(self):
        """Test detection of forbidden multiple option patterns."""
        # Each pattern and its specific regex
        test_cases = [
            ("To continue: Say X or Y", r'\bor\b'),
            ("You can either A or B", r'\beither\b.*\bor\b'),
            ("Option 1: ... Option 2: ...", r'Option\s+\d+.*Option\s+\d+'),
            ("Choose one: implement OR test", r'\bchoose\b.*\bor\b'),
        ]
        
        for text, pattern in test_cases:
            assert re.search(pattern, text, re.IGNORECASE), \
                f"Forbidden pattern '{pattern}' not detected in: {text}"
    
    def test_numbered_list_detection(self):
        """Test detection of numbered lists in next steps."""
        texts_with_numbered_lists = [
            "1. Begin Phase 1\n2. Create files\n3. Write tests",
            "Next steps:\n1. Implementation\n2. Testing",
        ]
        
        numbered_list_pattern = r'^\s*\d+\.\s+\w+'
        
        for text in texts_with_numbered_lists:
            matches = re.findall(numbered_list_pattern, text, re.MULTILINE)
            assert len(matches) > 0, f"Numbered list not detected in: {text}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
