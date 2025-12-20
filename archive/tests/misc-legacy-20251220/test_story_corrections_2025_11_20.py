"""
Test Story Corrections Applied 2025-11-20

Validates that the geographical corrections and disclaimer are present
in the generated "Awakening of CORTEX" story:
- Asif Codenstein lives in New Jersey, USA (his basement lab)
- Mrs. Codenstein lives in Lichfield, United Kingdom
- Long-distance relationship via video calls
- Asif receives the robot Copilot
- Humorous "USE AT YOUR OWN RISK" disclaimer present

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
import re


@pytest.fixture
def generated_story_path():
    """Path to generated story (orchestrator output)"""
    workspace_root = Path(__file__).parent.parent.parent
    return workspace_root / 'docs' / 'diagrams' / 'narratives' / 'THE-AWAKENING-OF-CORTEX.md'


@pytest.fixture
def master_story_path():
    """Path to master story source"""
    workspace_root = Path(__file__).parent.parent.parent
    return workspace_root / 'cortex-brain' / 'documents' / 'narratives' / 'THE-AWAKENING-OF-CORTEX-MASTER.md'


@pytest.fixture
def generated_story_content(generated_story_path):
    """Read generated story content"""
    if not generated_story_path.exists():
        pytest.skip(f"Generated story not found: {generated_story_path}")
    
    with open(generated_story_path, 'r', encoding='utf-8') as f:
        return f.read()


@pytest.fixture
def master_story_content(master_story_path):
    """Read master story content"""
    if not master_story_path.exists():
        pytest.skip(f"Master story not found: {master_story_path}")
    
    with open(master_story_path, 'r', encoding='utf-8') as f:
        return f.read()


class TestGeographicalCorrections:
    """Test geographical accuracy corrections from 2025-11-20"""
    
    def test_asif_in_new_jersey(self, generated_story_content):
        """Asif Codenstein should live in New Jersey, USA"""
        # Check for New Jersey references
        nj_patterns = [
            r'new jersey',
            r'nj',
            r'united states',
            r'\busa\b',
        ]
        
        matches = sum(1 for pattern in nj_patterns 
                     if re.search(pattern, generated_story_content, re.IGNORECASE))
        
        assert matches >= 1, "Story should mention Asif in New Jersey/USA"
    
    def test_asif_basement_lab(self, generated_story_content):
        """Asif's basement should be mentioned as his lab"""
        basement_patterns = [
            r'basement.*lab',
            r'lab.*basement',
            r'his.*basement',
            r'basement.*workspace',
        ]
        
        matches = sum(1 for pattern in basement_patterns 
                     if re.search(pattern, generated_story_content, re.IGNORECASE))
        
        assert matches >= 1, "Story should mention Asif's basement lab"
    
    def test_mrs_codenstein_in_lichfield_uk(self, generated_story_content):
        """Mrs. Codenstein should live in Lichfield, United Kingdom"""
        # Check for Lichfield + UK references
        uk_patterns = [
            r'lichfield',
            r'united kingdom',
            r'\buk\b',
            r'england',
        ]
        
        matches = sum(1 for pattern in uk_patterns 
                     if re.search(pattern, generated_story_content, re.IGNORECASE))
        
        assert matches >= 2, "Story should mention Lichfield, UK (multiple references expected)"
    
    def test_long_distance_relationship(self, generated_story_content):
        """Story should establish long-distance relationship"""
        distance_patterns = [
            r'video call',
            r'across.*atlantic',
            r'3,?500.*miles',
            r'ocean.*away',
            r'distance.*relationship',
            r'miles.*away',
        ]
        
        matches = sum(1 for pattern in distance_patterns 
                     if re.search(pattern, generated_story_content, re.IGNORECASE))
        
        assert matches >= 1, "Story should establish long-distance communication"
    
    def test_asif_receives_robot(self, generated_story_content):
        """Asif (not Mrs. Codenstein) should receive/have the robot"""
        # Check that robot/Copilot is in Asif's location (basement)
        # Mrs. Codenstein discovers it via video call, but it's in Asif's basement
        
        # Look for robot/Copilot in Asif's basement
        basement_robot_patterns = [
            r'robot.*basement',
            r'basement.*robot',
            r'copilot.*basement',
            r'basement.*copilot',
            r'his basement.*robot',
            r'robot.*his',
        ]
        
        matches = sum(1 for pattern in basement_robot_patterns 
                     if re.search(pattern, generated_story_content, re.IGNORECASE))
        
        # Should clearly show robot is in Asif's location
        assert matches >= 1, \
            "Story should show robot/Copilot is in Asif's basement (his possession)"
    
    def test_not_living_together(self, generated_story_content):
        """Story should NOT place them together in same location"""
        # Check that "their home" or "together" isn't used for residence
        problematic_patterns = [
            r'their home in lichfield',
            r'together in lichfield',
            r'living together',
        ]
        
        for pattern in problematic_patterns:
            assert not re.search(pattern, generated_story_content, re.IGNORECASE), \
                f"Story should not suggest they live together: {pattern}"


class TestDisclaimer:
    """Test humorous disclaimer section from 2025-11-20"""
    
    def test_disclaimer_section_exists(self, generated_story_content):
        """Story should have disclaimer section"""
        disclaimer_headers = [
            r'use at your own risk',
            r'disclaimer',
            r'warning.*risk',
        ]
        
        matches = sum(1 for pattern in disclaimer_headers 
                     if re.search(pattern, generated_story_content, re.IGNORECASE))
        
        assert matches >= 1, "Story should have disclaimer section"
    
    def test_disclaimer_mentions_risk(self, generated_story_content):
        """Disclaimer should mention risk/warning"""
        risk_terms = [
            r'\brisk\b',
            r'\bwarning\b',
            r'\bdanger\b',
            r'\bcaution\b',
            r'own risk',
        ]
        
        matches = sum(1 for pattern in risk_terms 
                     if re.search(pattern, generated_story_content, re.IGNORECASE))
        
        assert matches >= 2, "Disclaimer should emphasize risk/warning"
    
    def test_disclaimer_is_humorous(self, generated_story_content):
        """Disclaimer should maintain CORTEX humor"""
        # Look for humor indicators
        humor_patterns = [
            r'😅',  # Emoji
            r'🤖',  # Robot emoji
            r'⚠️',  # Warning emoji
            r'\?!',  # Exclamation question
            r'mrs\.?\s+codenstein',  # Mrs. Codenstein mention (her influence)
        ]
        
        # Find disclaimer section
        disclaimer_match = re.search(
            r'(use at your own risk|disclaimer).{0,2000}',
            generated_story_content,
            re.IGNORECASE | re.DOTALL
        )
        
        if disclaimer_match:
            disclaimer_text = disclaimer_match.group(0)
            humor_count = sum(1 for pattern in humor_patterns 
                            if re.search(pattern, disclaimer_text, re.IGNORECASE))
            
            assert humor_count >= 1, "Disclaimer should include humorous elements"
        else:
            pytest.skip("Disclaimer section not found for humor validation")
    
    def test_disclaimer_substantial_content(self, generated_story_content):
        """Disclaimer should be substantial (2000-word request)"""
        # Find disclaimer section
        disclaimer_match = re.search(
            r'(##\s*use at your own risk|##\s*disclaimer).{0,15000}',
            generated_story_content,
            re.IGNORECASE | re.DOTALL
        )
        
        if disclaimer_match:
            disclaimer_text = disclaimer_match.group(0)
            word_count = len(disclaimer_text.split())
            
            # Should be substantial (user requested ~2000 words, allow range)
            assert word_count >= 500, \
                f"Disclaimer should be substantial (found {word_count} words, expected ≥500)"
        else:
            # Check if disclaimer exists anywhere with less strict pattern
            assert 'use at your own risk' in generated_story_content.lower(), \
                "Disclaimer section should exist"


class TestMasterSourceIntegrity:
    """Test that master source contains corrections (prevents regressions)"""
    
    def test_master_has_nj_references(self, master_story_content):
        """Master source should have New Jersey references"""
        assert 'new jersey' in master_story_content.lower() or \
               'nj' in master_story_content.lower(), \
               "Master source should mention New Jersey"
    
    def test_master_has_lichfield_uk(self, master_story_content):
        """Master source should have Lichfield, UK references"""
        assert 'lichfield' in master_story_content.lower(), \
               "Master source should mention Lichfield"
        assert 'united kingdom' in master_story_content.lower() or \
               'uk' in master_story_content.lower(), \
               "Master source should mention UK"
    
    def test_master_has_video_calls(self, master_story_content):
        """Master source should mention video calls"""
        assert 'video call' in master_story_content.lower(), \
               "Master source should mention video calls"
    
    def test_master_has_disclaimer(self, master_story_content):
        """Master source should have disclaimer section"""
        assert 'use at your own risk' in master_story_content.lower() or \
               'disclaimer' in master_story_content.lower(), \
               "Master source should have disclaimer section"


class TestOrchestratorConsistency:
    """Test that orchestrator preserves corrections during generation"""
    
    def test_generated_matches_master_geography(self, master_story_content, generated_story_content):
        """Generated story should preserve master's geographical corrections"""
        # Key terms should appear in both
        key_terms = ['new jersey', 'lichfield', 'video call']
        
        for term in key_terms:
            master_has = term in master_story_content.lower()
            generated_has = term in generated_story_content.lower()
            
            if master_has:
                assert generated_has, \
                    f"Orchestrator should preserve '{term}' from master source"
    
    def test_generated_matches_master_disclaimer(self, master_story_content, generated_story_content):
        """Generated story should preserve master's disclaimer"""
        master_has_disclaimer = 'use at your own risk' in master_story_content.lower()
        generated_has_disclaimer = 'use at your own risk' in generated_story_content.lower()
        
        if master_has_disclaimer:
            assert generated_has_disclaimer, \
                "Orchestrator should preserve disclaimer from master source"


class TestRegressionPrevention:
    """Test that prevents regression to old incorrect geography"""
    
    def test_no_both_in_lichfield(self, generated_story_content):
        """Story should NOT place both characters in Lichfield"""
        # Check for problematic patterns that suggest both live in Lichfield
        problematic = [
            r'their.*home.*lichfield',
            r'both.*lichfield',
            r'together.*lichfield',
        ]
        
        for pattern in problematic:
            assert not re.search(pattern, generated_story_content, re.IGNORECASE), \
                f"Story should not suggest both live in Lichfield: {pattern}"
    
    def test_no_mrs_receives_robot(self, generated_story_content):
        """Story should NOT suggest Mrs. Codenstein receives robot"""
        # Check context around robot receipt
        robot_patterns = [
            r'mrs.*codenstein.{0,100}(receive|got|given|find|discover|found)',
            r'(receive|got|given|find|discover|found).{0,100}mrs.*codenstein',
        ]
        
        # These patterns are OK if they're about her knowing about it, not receiving it
        # Just check the most direct patterns
        direct_receipt = re.search(
            r'mrs.*codenstein.{0,50}(received|got)\s+(the\s+)?robot',
            generated_story_content,
            re.IGNORECASE
        )
        
        assert not direct_receipt, \
            "Story should not suggest Mrs. Codenstein received the robot"
    
    def test_no_lichfield_as_asifs_location(self, generated_story_content):
        """Story should NOT place Asif in Lichfield"""
        asif_in_lichfield = re.search(
            r'asif.{0,100}lichfield',
            generated_story_content,
            re.IGNORECASE
        )
        
        # If there is a match, check context - it might be about visiting or video calls
        if asif_in_lichfield:
            context = asif_in_lichfield.group(0).lower()
            # Allow mentions of video calls, visiting, etc.
            allowed_contexts = ['video', 'call', 'visit', 'across']
            has_allowed = any(allowed in context for allowed in allowed_contexts)
            
            assert has_allowed, \
                "If Asif and Lichfield mentioned together, should be about video calls/visits"


# Integration test
class TestStoryCorrectionsIntegration:
    """High-level integration test for all corrections"""
    
    def test_all_corrections_applied(self, generated_story_content):
        """All corrections should be present in generated story"""
        corrections = [
            ('New Jersey reference', r'new jersey|nj'),
            ('Lichfield reference', r'lichfield'),
            ('UK reference', r'united kingdom|uk'),
            ('Long-distance indicator', r'video call|miles|atlantic'),
            ('Disclaimer section', r'use at your own risk|disclaimer'),
        ]
        
        results = []
        for name, pattern in corrections:
            found = bool(re.search(pattern, generated_story_content, re.IGNORECASE))
            results.append((name, found))
        
        # Report all results
        failures = [name for name, found in results if not found]
        
        assert len(failures) == 0, \
            f"Missing corrections: {', '.join(failures)}"
    
    def test_orchestrator_executed_successfully(self, generated_story_path):
        """Generated story file should exist (orchestrator ran)"""
        assert generated_story_path.exists(), \
            "Generated story should exist (orchestrator should have run)"
    
    def test_generated_story_not_empty(self, generated_story_content):
        """Generated story should have substantial content"""
        assert len(generated_story_content) > 5000, \
            "Generated story should be substantial (>5000 chars)"
    
    def test_master_source_unchanged_except_corrections(self, master_story_content):
        """Master source should be intact (not corrupted during edits)"""
        # Basic integrity checks
        assert len(master_story_content) > 5000, "Master should be substantial"
        assert '# The Awakening' in master_story_content, "Master should have title"
        assert 'CORTEX' in master_story_content, "Master should mention CORTEX"
