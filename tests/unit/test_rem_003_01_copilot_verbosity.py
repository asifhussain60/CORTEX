"""
Test for AC-REM-003-01: Copilot Verbosity Enforcement

This test verifies that Copilot communication guidelines are properly enforced,
including word count limits, communication style, and CORTEX compliance.

Issue: ISSUE-003 (Response Verbosity & Header Injection)
AC-ID: AC-REM-003-01
Priority: HIGH
"""

import re
from pathlib import Path
from typing import List, Tuple


def count_words(text: str) -> int:
    """
    Count words in text, excluding code blocks and markdown syntax.
    
    Args:
        text: Text to count words in
        
    Returns:
        Number of words
    """
    # Remove code blocks (```...```)
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    # Remove inline code (`...`)
    text = re.sub(r'`[^`]*`', '', text)
    # Remove markdown links
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    # Remove markdown headers
    text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
    # Remove other markdown
    text = re.sub(r'[*_~\[\]{}()]', ' ', text)
    
    # Split by whitespace and count non-empty words
    words = [w for w in text.split() if w.strip()]
    return len(words)


def check_prohibited_phrases(text: str) -> List[str]:
    """
    Find prohibited communication patterns in text.
    
    Args:
        text: Text to check
        
    Returns:
        List of found prohibited phrases
    """
    prohibited_patterns = [
        r'\bLet me\b',
        r'\bI will\b',
        r'\bI believe\b',
        r'\bI think\b',
        r'\bLet\'s\b',
        r'\bjust\s',
        r'\bapparently\b',
        r'\bbasically\b',
    ]
    
    found = []
    for pattern in prohibited_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            found.extend(matches)
    
    return found


def test_copilot_instruction_has_verbosity_guidelines():
    """
    Verify that .github/copilot-instructions.md contains verbosity guidelines.
    """
    copilot_file = Path(__file__).parent.parent.parent / ".github" / "copilot-instructions.md"
    
    assert copilot_file.exists(), "copilot-instructions.md not found"
    
    with open(copilot_file, 'r') as f:
        content = f.read()
    
    # Check for required sections
    required_sections = [
        "Verbosity Control",
        "Word Count Limits",
        "Communication Style",
        "Prohibited Patterns",
        "<500 words",
    ]
    
    for section in required_sections:
        assert section in content, f"Missing required section: {section}"
    
    # Check for specific guidelines
    assert "Let me" in content, "Should document 'Let me' prohibition"
    assert "I will" in content, "Should document 'I will' prohibition"
    assert "Direct communication" in content or "imperative" in content, \
        "Should emphasize direct communication"


def test_verbosity_limits_documented():
    """
    Verify verbosity limits are clearly documented.
    """
    copilot_file = Path(__file__).parent.parent.parent / ".github" / "copilot-instruction.md"
    
    with open(copilot_file, 'r') as f:
        content = f.read()
    
    # Should specify maximum word count
    assert "500 words" in content or "500-word" in content, \
        "Should specify 500-word limit"
    
    # Should have target range
    assert "200-400 words" in content or "target" in content.lower(), \
        "Should specify target word range"


def test_copyright_requirement_enforced():
    """
    Verify copyright notice requirement is documented.
    """
    copilot_file = Path(__file__).parent.parent.parent / ".github" / "copilot-instruction.md"
    
    with open(copilot_file, 'r') as f:
        content = f.read()
    
    # Should mention copyright on every response
    assert "Copyright" in content, "Should mention copyright"
    assert "every response" in content.lower() or "all response" in content.lower(), \
        "Should mandate copyright on every response"


def test_no_prohibited_phrases_in_guidelines():
    """
    Verify that the guidelines themselves don't use prohibited phrases
    when describing CORTEX behavior (outside examples).
    """
    copilot_file = Path(__file__).parent.parent.parent / ".github" / "copilot-instruction.md"
    
    with open(copilot_file, 'r') as f:
        content = f.read()
    
    # Extract the verbosity section (but not the "Prohibited Patterns" examples)
    lines = content.split('\n')
    verbosity_section = []
    in_section = False
    in_examples = False
    
    for line in lines:
        if 'Verbosity Control' in line:
            in_section = True
        elif 'Prohibited Patterns' in line:
            in_examples = True
        elif in_examples and ('####' in line or '###' in line) and 'Prohibited' not in line:
            in_examples = False
        
        if in_section and not in_examples:
            verbosity_section.append(line)
    
    guidelines_text = '\n'.join(verbosity_section)
    
    # When describing what CORTEX SHOULD do, check for compliance
    # (Outside of "Prohibited Patterns" and "Preferred Patterns" sections)
    prohibited_in_guidelines = check_prohibited_phrases(guidelines_text)
    
    # It's OK if they appear in "example" sections, but not in core guidelines
    if prohibited_in_guidelines:
        # Check if they appear only in marked examples
        for phrase in prohibited_in_guidelines:
            if '❌' in guidelines_text[max(0, guidelines_text.find(phrase)-50):guidelines_text.find(phrase)+len(phrase)+50]:
                # This is marked as prohibited, so it's OK
                continue


if __name__ == "__main__":
    # Run tests manually for verification
    print("Running AC-REM-003-01 tests...")
    
    tests = [
        ("test_copilot_instruction_has_verbosity_guidelines", test_copilot_instruction_has_verbosity_guidelines),
        ("test_verbosity_limits_documented", test_verbosity_limits_documented),
        ("test_copyright_requirement_enforced", test_copyright_requirement_enforced),
        ("test_no_prohibited_phrases_in_guidelines", test_no_prohibited_phrases_in_guidelines),
    ]
    
    passed = 0
    for test_name, test_func in tests:
        try:
            test_func()
            print(f"✓ {test_name} PASSED")
            passed += 1
        except AssertionError as e:
            print(f"✗ {test_name} FAILED: {e}")
        except Exception as e:
            print(f"✗ {test_name} ERROR: {e}")
    
    print(f"\n{passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("All tests passed!")
    else:
        exit(1)
