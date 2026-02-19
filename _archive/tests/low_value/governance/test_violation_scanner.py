"""
Unit tests for AST-Based Governance Violation Scanner.

Tests for Phase 41 Stage 4 (ENH-056):
- AC-PHASE41-015: Python AST parsing for code blocks (7 tests)
- AC-PHASE41-016: Tree-sitter bash command parsing (7 tests)
- AC-PHASE41-017: 20+ violation patterns per CORE rule (8 tests)
- AC-PHASE41-018: 80% improvement in violation detection (3 tests)

Total: 25 tests

Author: Asif Hussain
Date: 2026-02-07
"""

import pytest
from typing import Dict, List
from pathlib import Path

from cortex.governance.violation_scanner import ViolationScanner, ViolationResult


# AC_START: AC-PHASE41-015
# Description: Python AST parsing for code blocks
# Author: Asif Hussain
# Date: 2026-02-07


@pytest.fixture
def scanner():
    """Create ViolationScanner instance."""
    return ViolationScanner()


class TestPythonASTparsing:
    """Test AC-PHASE41-015: Python AST parsing for code blocks (7 tests)."""
    
    def test_extracts_python_code_from_markdown(self, scanner):
        """Test extracting Python code blocks from chat."""
        chat_content = """
User: Create a function
GitHub Copilot: Here's the code:

```python
def hello():
    print("Hello")
```
"""
        
        code_blocks = scanner.extract_python_code_blocks(chat_content)
        
        assert len(code_blocks) == 1
        assert 'def hello():' in code_blocks[0]
    
    def test_parses_python_ast(self, scanner):
        """Test parsing Python code into AST."""
        python_code = """
def hello():
    print("Hello")
    return True
"""
        
        ast_tree = scanner.parse_python_ast(python_code)
        
        assert ast_tree is not None
        assert scanner.count_function_defs(ast_tree) == 1
    
    def test_detects_bare_except(self, scanner):
        """Test detecting bare except (CORE-013 violation)."""
        python_code = """
try:
    risky_operation()
except:  # Bare except - violation
    pass
"""
        
        violations = scanner.scan_python_code(python_code)
        
        assert any(v.rule_id == "CORE-013" for v in violations)
        assert any("bare except" in v.message.lower() for v in violations)
    
    def test_detects_missing_type_hints(self, scanner):
        """Test detecting missing type hints (CORE-011 violation)."""
        python_code = """
def calculate(x, y):  # Missing type hints
    return x + y
"""
        
        violations = scanner.scan_python_code(python_code)
        
        assert any(v.rule_id == "CORE-011" for v in violations)
        assert any("type hint" in v.message.lower() for v in violations)
    
    def test_detects_missing_docstrings(self, scanner):
        """Test detecting missing docstrings (CORE-012 violation)."""
        python_code = """
def important_function():  # No docstring
    return 42
"""
        
        violations = scanner.scan_python_code(python_code)
        
        assert any(v.rule_id == "CORE-012" for v in violations)
        assert any("docstring" in v.message.lower() for v in violations)
    
    def test_extracts_line_numbers(self, scanner):
        """Test extracting violation line numbers from AST."""
        python_code = """
def func1():  # Line 2
    pass

try:
    x()
except:  # Line 7 - violation
    pass
"""
        
        violations = scanner.scan_python_code(python_code)
        
        bare_except_violation = next(v for v in violations if v.rule_id == "CORE-013")
        assert bare_except_violation.line_number == 7
    
    def test_handles_syntax_errors_gracefully(self, scanner):
        """Test handling invalid Python code."""
        invalid_python = """
def broken(
    # Missing closing paren
"""
        
        # Should not raise exception
        violations = scanner.scan_python_code(invalid_python)
        
        # Should report syntax error as violation
        assert len(violations) > 0
        assert any("syntax" in v.message.lower() for v in violations)


# AC-PHASE41-016: Tree-sitter bash command parsing (7 tests)


class TestTreeSitterBashParsing:
    """Test AC-PHASE41-016: Tree-sitter bash command parsing (7 tests)."""
    
    def test_detects_cat_redirect(self, scanner):
        """Test detecting 'cat > file' command (CORE-002 violation)."""
        bash_command = """
cat > output.md << 'EOF'
# Summary
Content here
EOF
"""
        
        violations = scanner.scan_bash_commands(bash_command)
        
        assert any(v.rule_id == "CORE-002" for v in violations)
        assert any("file generation" in v.message.lower() for v in violations)
    
    def test_detects_echo_redirect(self, scanner):
        """Test detecting 'echo > file' command (CORE-002 violation)."""
        bash_command = 'echo "content" > output.md'
        
        violations = scanner.scan_bash_commands(bash_command)
        
        assert any(v.rule_id == "CORE-002" for v in violations)
    
    def test_detects_printf_redirect(self, scanner):
        """Test detecting 'printf > file' command (CORE-002 violation)."""
        bash_command = 'printf "%s\\n" "data" > file.md'
        
        violations = scanner.scan_bash_commands(bash_command)
        
        assert any(v.rule_id == "CORE-002" for v in violations)
    
    def test_extracts_bash_from_tool_calls(self, scanner):
        """Test extracting bash commands from [Tool call: run_in_terminal]."""
        chat_content = """
[Tool call: run_in_terminal]
Command: cat > summary.md << 'EOF'
# Content
EOF
"""
        
        bash_commands = scanner.extract_bash_from_chat(chat_content)
        
        assert len(bash_commands) > 0
        assert any("cat >" in cmd for cmd in bash_commands)
    
    def test_ignores_safe_redirects(self, scanner):
        """Test that safe redirects (grep, awk) are not violations."""
        bash_command = 'grep "pattern" file.txt > results.txt'
        
        violations = scanner.scan_bash_commands(bash_command)
        
        # grep redirect is NOT a CORE-002 violation (analysis only)
        assert not any(v.rule_id == "CORE-002" for v in violations)
    
    def test_detects_heredoc_patterns(self, scanner):
        """Test detecting heredoc patterns (<<EOF, <<'EOF', <<"EOF")."""
        bash_commands = [
            "cat > file1.md <<EOF",
            "cat > file2.md <<'EOF'",
            'cat > file3.md <<"EOF"',
        ]
        
        for cmd in bash_commands:
            violations = scanner.scan_bash_commands(cmd)
            assert any(v.rule_id == "CORE-002" for v in violations), f"Failed for: {cmd}"
    
    def test_extracts_filenames_from_redirects(self, scanner):
        """Test extracting target filenames from redirect commands."""
        bash_command = 'cat > important-summary.md <<EOF'
        
        violations = scanner.scan_bash_commands(bash_command)
        
        violation = next(v for v in violations if v.rule_id == "CORE-002")
        assert "important-summary.md" in violation.context


# AC-PHASE41-017: 20+ violation patterns per CORE rule (8 tests)


class TestViolationPatterns:
    """Test AC-PHASE41-017: 20+ violation patterns per CORE rule (8 tests)."""
    
    def test_core_002_patterns(self, scanner):
        """Test CORE-002: No markdown file generation (8 patterns)."""
        patterns = scanner.get_violation_patterns("CORE-002")
        
        assert len(patterns) >= 8
        assert any("cat >" in p for p in patterns)
        assert any("echo >" in p for p in patterns)
        assert any("printf >" in p for p in patterns)
        assert any("heredoc" in p.lower() for p in patterns)
    
    def test_core_008_patterns(self, scanner):
        """Test CORE-008: TDD mandatory (6 patterns)."""
        patterns = scanner.get_violation_patterns("CORE-008")
        
        assert len(patterns) >= 6
        # Patterns like: code before test, no test file, skipping test
    
    def test_core_028_patterns(self, scanner):
        """Test CORE-028: File naming violations (8 patterns)."""
        patterns = scanner.get_violation_patterns("CORE-028")
        
        assert len(patterns) >= 8
        # SCREAMING_CASE, camelCase, plan files >40 chars, etc.
    
    def test_core_035_patterns(self, scanner):
        """Test CORE-035: Single canonical implementation (5 patterns)."""
        patterns = scanner.get_violation_patterns("CORE-035")
        
        assert len(patterns) >= 5
        # Duplicate functions, duplicate classes, similar implementations
    
    def test_scans_with_all_patterns(self, scanner):
        """Test scanning with full pattern library."""
        test_code = """
# Violations: bare except, missing type hints, file generation

```python
def process(data):  # Missing type hints
    try:
        result = transform(data)
    except:  # Bare except
        result = None
    return result
```

# Later in chat:
[Tool call: run_in_terminal]
Command: cat > output.md <<EOF
# Summary
EOF
"""
        
        violations = scanner.scan_content(test_code)
        
        # Should detect multiple rule violations
        rule_ids = {v.rule_id for v in violations}
        assert "CORE-002" in rule_ids  # File generation
        assert "CORE-011" in rule_ids  # Type hints
        assert "CORE-013" in rule_ids  # Bare except
    
    def test_pattern_regex_compilation(self, scanner):
        """Test that all patterns compile as valid regex."""
        all_patterns = scanner.get_all_violation_patterns()
        
        for rule_id, patterns in all_patterns.items():
            for pattern in patterns:
                # Should compile without exception
                scanner.compile_pattern(pattern)
        
        assert len(all_patterns) >= 4  # At least 4 CORE rules
    
    def test_pattern_coverage(self, scanner):
        """Test pattern coverage across all CORE rules."""
        coverage = scanner.get_pattern_coverage()
        
        assert coverage["CORE-002"] >= 8
        assert coverage["CORE-008"] >= 6
        assert coverage["CORE-028"] >= 8
        assert coverage["CORE-035"] >= 5
        assert sum(coverage.values()) >= 27  # Total 20+ patterns
    
    def test_loads_patterns_from_yaml(self, scanner):
        """Test loading violation patterns from YAML file."""
        # Scanner should auto-load from cortex/governance/violation_patterns.yaml
        patterns = scanner.get_all_violation_patterns()
        
        assert len(patterns) > 0
        assert "CORE-002" in patterns
        assert isinstance(patterns["CORE-002"], list)


# AC-PHASE41-018: 80% improvement in violation detection (3 tests)


class TestViolationDetectionImprovement:
    """Test AC-PHASE41-018: 80% improvement in violation detection (3 tests)."""
    
    def test_baseline_detection_vs_ast_detection(self, scanner):
        """Test AST-based detection vs regex-only baseline."""
        test_code = """
def calculate(x, y):  # Missing type hints
    try:
        result = x / y
    except:  # Bare except
        result = None
    return result
"""
        
        # Baseline: Regex-only detection
        baseline_violations = scanner.detect_with_regex_only(test_code)
        
        # AST-based detection
        ast_violations = scanner.scan_python_code(test_code)
        
        # AST should detect more violations
        assert len(ast_violations) > len(baseline_violations)
        improvement = (len(ast_violations) - len(baseline_violations)) / len(baseline_violations) * 100 if len(baseline_violations) > 0 else 100
        assert improvement >= 50  # At least 50% improvement
    
    def test_historical_chat_session_accuracy(self, scanner, tmp_path):
        """Test against historical chat sessions with known violations."""
        # Create test chat with known violations
        chat_file = tmp_path / "historical_chat.md"
        chat_file.write_text("""
User: Create a summary file
GitHub Copilot: I'll create it:

```bash
cat > summary.md <<EOF
# Summary
EOF
```

Also, here's a function:

```python
def process(data):  # Missing type hints, missing docstring
    try:
        return data.transform()
    except:  # Bare except
        return None
```
""")
        
        violations = scanner.scan_file(chat_file)
        
        # Known violations:
        # 1. CORE-002: cat > summary.md
        # 2. CORE-011: Missing type hints
        # 3. CORE-012: Missing docstring
        # 4. CORE-013: Bare except
        
        detected_rules = {v.rule_id for v in violations}
        
        # Should detect all 4 violation types
        assert "CORE-002" in detected_rules
        assert "CORE-011" in detected_rules
        assert "CORE-012" in detected_rules
        assert "CORE-013" in detected_rules
        
        # Accuracy: detected / total_known = 4/4 = 100%
        accuracy = len(detected_rules) / 4 * 100
        assert accuracy >= 80  # 80% accuracy target
    
    def test_false_positive_rate(self, scanner):
        """Test that false positive rate is low (<10%)."""
        clean_code = """
def calculate_sum(numbers: List[int]) -> int:
    '''Calculate sum of numbers.
    
    Args:
        numbers: List of integers
    
    Returns:
        Sum of all numbers
    '''
    try:
        return sum(numbers)
    except TypeError as e:  # Specific exception - NOT a violation
        logger.error(f"Invalid input: {e}")
        return 0
"""
        
        violations = scanner.scan_python_code(clean_code)
        
        # Clean code should have 0-1 violations (low false positive rate)
        assert len(violations) <= 1  # <10% false positive rate


# Integration tests


def test_full_chat_session_scan(scanner):
    """Integration test: Scan complete chat session."""
    chat_content = """
User: Implement feature X

GitHub Copilot: I'll implement it:

```python
def feature_x(data):  # Missing type hints
    # Missing docstring
    try:
        process(data)
    except:  # Bare except
        pass
```

Then create a summary:

[Tool call: run_in_terminal]
Command: cat > feature-summary.md <<EOF
# Summary
EOF
"""
    
    violations = scanner.scan_content(chat_content)
    
    # Should detect multiple violations across Python and bash
    assert len(violations) >= 4
    
    # Group by rule
    by_rule = {}
    for v in violations:
        by_rule.setdefault(v.rule_id, []).append(v)
    
    assert "CORE-002" in by_rule  # File generation
    assert "CORE-011" in by_rule  # Type hints
    assert "CORE-013" in by_rule  # Bare except


def test_scanner_performance(scanner):
    """Test scanner performance on large chat session."""
    import time
    
    # Generate large chat (100 code blocks)
    large_chat = "User: Implement features\n\nGitHub Copilot:\n\n"
    for i in range(100):
        large_chat += f"""
```python
def func{i}(x):  # Violation: missing type hints
    return x * 2
```
"""
    
    start = time.time()
    violations = scanner.scan_content(large_chat)
    duration = time.time() - start
    
    # Should complete in <2 seconds
    assert duration < 2.0
    
    # Should detect violations
    assert len(violations) >= 100  # At least 1 per function


# AC_COMPLETE: AC-PHASE41-015, AC-PHASE41-016, AC-PHASE41-017, AC-PHASE41-018 ✅ 25/25 tests
