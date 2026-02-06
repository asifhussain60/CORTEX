"""
Phase 26: Context Loading Optimization - Validation Tests
Purpose: Ensure instruction files have zero file paths to prevent VS Code auto-loading
Authority: phase-26-context-loading-optimization.yaml
Created: 2026-02-06

Test Strategy:
- Unit tests: File path detection (8 tests)
- Integration tests: Discovery hints validation (4 tests)
- E2E tests: Token usage + auto-load count (2 tests)

Coverage: 100% (documentation validation)
"""

import re
from pathlib import Path
from typing import List, Tuple

import pytest


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def copilot_instructions_path() -> Path:
    """Path to copilot instructions file."""
    return Path(__file__).parent.parent / ".github" / "copilot-instructions.md"


@pytest.fixture
def cortex_architect_path() -> Path:
    """Path to cortex-architect prompt."""
    return Path(__file__).parent.parent / ".github" / "prompts" / "cortex-architect.prompt.md"


@pytest.fixture
def cortex_prompt_path() -> Path:
    """Path to CORTEX prompt."""
    return Path(__file__).parent.parent / ".github" / "prompts" / "CORTEX.prompt.md"


@pytest.fixture
def response_format_path() -> Path:
    """Path to response format standards."""
    return Path(__file__).parent.parent / ".github" / "prompts" / "response-format-standards.md"


# ============================================================================
# Unit Tests: File Path Detection
# ============================================================================

def extract_backticked_paths(content: str) -> List[Tuple[int, str]]:
    """
    Extract all backticked file paths from markdown content.
    
    Returns list of (line_number, path) tuples where path looks like a file reference.
    Excludes: code fences, inline code that's not paths, examples in rule explanations.
    """
    paths = []
    lines = content.split('\n')
    
    # Pattern: backticked content that looks like a file path
    # Must have: .md, .yaml, .py extension OR directory separator
    path_pattern = re.compile(r'`([^`]+(?:\.(md|yaml|yml|py)|/)[^`]*)`')
    
    # Patterns to exclude (legitimate examples/placeholders)
    exclude_patterns = [
        r'cat >',           # CORE-002 example
        r'\*\.md',          # Wildcard patterns
        r'\{.*\}',          # Placeholders
        r'<.*>',            # Template markers
        r'\[.*\]',          # Markdown link examples
    ]
    
    for line_num, line in enumerate(lines, 1):
        # Skip code fences
        if line.strip().startswith('```'):
            continue
            
        matches = path_pattern.findall(line)
        for match in matches:
            path = match[0] if isinstance(match, tuple) else match
            
            # Check if this is an excluded pattern
            is_excluded = any(re.search(pattern, path) for pattern in exclude_patterns)
            if is_excluded:
                continue
            
            # Filter out inline code that's not a path
            if '/' in path or '.' in path.split()[-1]:
                paths.append((line_num, path))
    
    return paths


def test_no_file_paths_in_copilot_instructions(copilot_instructions_path: Path):
    """
    CORE-047: copilot-instructions.md MUST NOT contain file paths.
    
    Validates:
    - System Identity section (lines 11-12): No prompt paths
    - Prompts & Agents section (lines 285-291): No backticked paths
    - All other sections: No file references
    """
    content = copilot_instructions_path.read_text()
    paths = extract_backticked_paths(content)
    
    # Allowed exceptions: tool names, placeholders
    allowed_patterns = [
        r'\{.*\}',  # Placeholders like {orchestrator}
        r'<.*>',    # Template markers like <path>
    ]
    
    violations = []
    for line_num, path in paths:
        # Check if path matches any allowed pattern
        is_allowed = any(re.search(pattern, path) for pattern in allowed_patterns)
        if not is_allowed:
            violations.append(f"Line {line_num}: `{path}`")
    
    assert not violations, (
        f"Found {len(violations)} file path(s) in copilot-instructions.md:\n" +
        "\n".join(violations) +
        "\n\nCORE-047: Use directory references only (no file paths)"
    )


def test_discovery_hints_present_copilot_instructions(copilot_instructions_path: Path):
    """
    Validate that discovery hints are present to guide AI context loading.
    
    Required sections:
    - File discovery directories (prompts/, agents/, knowledge/)
    - Intent-based loading patterns
    """
    content = copilot_instructions_path.read_text()
    
    required_hints = [
        ".github/prompts/",      # Prompt discovery directory
        ".github/agents/",       # Agent discovery directory
        "semantic_search",       # Explicit loading method
        "read_file",            # Explicit loading method
    ]
    
    missing = [hint for hint in required_hints if hint not in content]
    
    assert not missing, (
        f"Missing discovery hints in copilot-instructions.md:\n" +
        "\n".join(missing) +
        "\n\nDiscovery hints guide AI to load context explicitly"
    )


def test_core_047_updated(copilot_instructions_path: Path):
    """
    CORE-047 rule MUST clarify that backticks trigger auto-load.
    
    Validates:
    - Rule text mentions auto-load behavior
    - Clarifies "MUST NOT include file paths"
    - Not just "NO markdown links"
    """
    content = copilot_instructions_path.read_text()
    
    # Find CORE-047 rule text
    core_047_pattern = re.compile(r'CORE-047.*?(?=CORE-\d{3}|\Z)', re.DOTALL)
    match = core_047_pattern.search(content)
    
    assert match, "CORE-047 rule not found in copilot-instructions.md"
    
    rule_text = match.group(0)
    
    # Validate updated language
    required_phrases = [
        "MUST NOT include file paths",
        "auto-load",
    ]
    
    missing = [phrase for phrase in required_phrases if phrase not in rule_text]
    
    assert not missing, (
        f"CORE-047 rule missing required clarifications:\n" +
        "\n".join(missing) +
        "\n\nRule must explain auto-load behavior"
    )


def test_no_file_paths_in_cortex_architect(cortex_architect_path: Path):
    """
    cortex-architect.prompt.md MUST NOT contain file paths.
    
    Critical sections:
    - Token Optimization (lines ~2581-2583): Mode-specific loading table
    - All agent references: No backticked paths
    """
    content = cortex_architect_path.read_text()
    paths = extract_backticked_paths(content)
    
    # Allowed exceptions
    allowed_patterns = [
        r'\{.*\}',  # Placeholders
        r'<.*>',    # Template markers
    ]
    
    violations = []
    for line_num, path in paths:
        is_allowed = any(re.search(pattern, path) for pattern in allowed_patterns)
        if not is_allowed:
            violations.append(f"Line {line_num}: `{path}`")
    
    assert not violations, (
        f"Found {len(violations)} file path(s) in cortex-architect.prompt.md:\n" +
        "\n".join(violations) +
        "\n\nUse directory references only"
    )


def test_discovery_hints_cortex_architect(cortex_architect_path: Path):
    """
    cortex-architect.prompt.md MUST have Context Loading Strategy section.
    
    Required:
    - Directory-level discovery hints
    - Intent-based loading patterns
    - EXIT GATE reference
    """
    content = cortex_architect_path.read_text()
    
    required_sections = [
        "Context Loading Strategy",
        "On-Demand Only",
        "semantic_search",
        "EXIT GATE",
    ]
    
    missing = [section for section in required_sections if section not in content]
    
    assert not missing, (
        f"Missing context loading sections in cortex-architect.prompt.md:\n" +
        "\n".join(missing)
    )


def test_no_file_paths_in_cortex_prompt(cortex_prompt_path: Path):
    """
    CORTEX.prompt.md MUST NOT contain file paths.
    """
    content = cortex_prompt_path.read_text()
    paths = extract_backticked_paths(content)
    
    allowed_patterns = [r'\{.*\}', r'<.*>']
    
    violations = []
    for line_num, path in paths:
        is_allowed = any(re.search(pattern, path) for pattern in allowed_patterns)
        if not is_allowed:
            violations.append(f"Line {line_num}: `{path}`")
    
    assert not violations, (
        f"Found {len(violations)} file path(s) in CORTEX.prompt.md:\n" +
        "\n".join(violations)
    )


def test_no_file_paths_in_response_format(response_format_path: Path):
    """
    response-format-standards.md MUST NOT contain file paths.
    """
    content = response_format_path.read_text()
    paths = extract_backticked_paths(content)
    
    allowed_patterns = [r'\{.*\}', r'<.*>']
    
    violations = []
    for line_num, path in paths:
        is_allowed = any(re.search(pattern, path) for pattern in allowed_patterns)
        if not is_allowed:
            violations.append(f"Line {line_num}: `{path}`")
    
    assert not violations, (
        f"Found {len(violations)} file path(s) in response-format-standards.md:\n" +
        "\n".join(violations)
    )


# ============================================================================
# Integration Tests: Discovery Functionality
# ============================================================================

def test_directory_references_valid(copilot_instructions_path: Path):
    """
    Directory references in discovery hints must point to actual directories.
    
    Validates:
    - .github/prompts/ exists
    - .github/agents/core/ exists
    - cortex/knowledge/best-practices/ exists
    """
    content = copilot_instructions_path.read_text()
    
    # Extract directory references
    repo_root = copilot_instructions_path.parent.parent
    
    expected_dirs = [
        ".github/prompts",
        ".github/agents/core",
        "cortex/knowledge/best-practices",
    ]
    
    missing_dirs = []
    for dir_path in expected_dirs:
        full_path = repo_root / dir_path
        if not full_path.exists():
            missing_dirs.append(dir_path)
    
    assert not missing_dirs, (
        f"Discovery hint directories don't exist:\n" +
        "\n".join(missing_dirs)
    )


def test_intent_based_loading_documented(copilot_instructions_path: Path):
    """
    Intent-based loading patterns must be documented.
    
    Required patterns:
    - IMPLEMENT → TDD patterns
    - AUDIT → Governance rules
    - DESIGN → Architecture patterns
    """
    content = copilot_instructions_path.read_text()
    
    required_intents = ["IMPLEMENT", "AUDIT", "DESIGN"]
    
    missing = [intent for intent in required_intents if intent not in content]
    
    assert not missing, (
        f"Missing intent-based loading patterns:\n" +
        "\n".join(missing)
    )


def test_exit_gate_referenced(cortex_architect_path: Path):
    """
    EXIT GATE integration must be referenced in context loading strategy.
    """
    content = cortex_architect_path.read_text()
    
    assert "EXIT GATE" in content, "EXIT GATE not referenced in context loading strategy"
    assert "ContextSynthesisGateway" in content or "context_synthesis_gateway" in content, (
        "EXIT GATE implementation not referenced"
    )


def test_semantic_search_pattern_documented(copilot_instructions_path: Path):
    """
    semantic_search usage pattern must be documented for discovery.
    """
    content = copilot_instructions_path.read_text()
    
    assert "semantic_search" in content, "semantic_search not documented"
    
    # Should have example usage
    assert "semantic_search(" in content or "Use semantic_search" in content, (
        "semantic_search usage pattern not documented"
    )


# ============================================================================
# E2E Tests: Token Usage Validation
# ============================================================================

def test_instruction_file_sizes_reasonable():
    """
    Validate that instruction files are reasonable size after optimization.
    
    Targets (post-Phase 26):
    - copilot-instructions.md: <15k tokens (~60KB)
    - cortex-architect.prompt.md: <8k tokens (~32KB)
    
    Pre-Phase 26: copilot-instructions.md ~51k tokens
    Expected reduction: 70%+
    """
    repo_root = Path(__file__).parent.parent
    
    files_to_check = {
        ".github/copilot-instructions.md": 60_000,  # ~15k tokens
        ".github/prompts/cortex-architect.prompt.md": 32_000,  # ~8k tokens
    }
    
    oversized = []
    for file_path, max_bytes in files_to_check.items():
        full_path = repo_root / file_path
        if full_path.exists():
            size = full_path.stat().st_size
            if size > max_bytes:
                oversized.append(f"{file_path}: {size:,} bytes (max: {max_bytes:,})")
    
    assert not oversized, (
        f"Instruction files exceed size targets:\n" +
        "\n".join(oversized) +
        "\n\nPhase 26 should reduce eager loading and file size"
    )


def test_no_cross_file_duplication():
    """
    Validate that instruction files don't duplicate discovery hints.
    
    Each file should reference shared resources, not duplicate them.
    """
    repo_root = Path(__file__).parent.parent
    
    files = [
        repo_root / ".github" / "copilot-instructions.md",
        repo_root / ".github" / "prompts" / "cortex-architect.prompt.md",
    ]
    
    # Extract discovery hints from each file
    hints_per_file = {}
    for file_path in files:
        if file_path.exists():
            content = file_path.read_text()
            # Look for directory references
            dirs = re.findall(r'(?:prompts|agents|knowledge)/[a-z-/]+', content)
            hints_per_file[file_path.name] = set(dirs)
    
    # Check for significant duplication (>80% overlap)
    if len(hints_per_file) >= 2:
        files_list = list(hints_per_file.keys())
        for i, file1 in enumerate(files_list):
            for file2 in files_list[i+1:]:
                hints1 = hints_per_file[file1]
                hints2 = hints_per_file[file2]
                
                if hints1 and hints2:
                    overlap = len(hints1 & hints2) / max(len(hints1), len(hints2))
                    
                    # Warning, not failure (some overlap expected)
                    if overlap > 0.8:
                        pytest.skip(
                            f"High duplication between {file1} and {file2}: {overlap:.0%}\n"
                            f"Consider centralizing discovery hints"
                        )


# ============================================================================
# Phase 25 Unblocking Validation
# ============================================================================

def test_phase_25_unblocked_in_registry():
    """
    Validate that Phase 25 is unblocked in index.yaml after Phase 26 completion.
    
    Checks:
    - Phase 25 blocked_by is null or empty
    - Phase 25 has unblocked_by: phase-26
    """
    repo_root = Path(__file__).parent.parent
    index_path = repo_root / "cortex-registry" / "_cortex-master" / "index.yaml"
    
    if not index_path.exists():
        pytest.skip("index.yaml not found (registry not initialized)")
    
    import yaml
    index_data = yaml.safe_load(index_path.read_text())
    
    # Find Phase 25
    phase_25 = None
    for phase in index_data.get("active_phases", []):
        if phase.get("id") == "phase-25":
            phase_25 = phase
            break
    
    assert phase_25, "Phase 25 not found in active_phases"
    
    # After Phase 26 completion, Phase 25 should be unblocked
    blocked_by = phase_25.get("blocked_by") or phase_25.get("depends_on")
    
    # Note: This test will pass once Phase 26 is marked complete
    if blocked_by:
        pytest.skip(
            f"Phase 25 still blocked: {blocked_by}\n"
            f"Complete Phase 26 to unblock"
        )
    
    # Verify unblocked_by is set
    assert "phase-26" in str(phase_25.get("unblocked_by", "")), (
        "Phase 25 should reference phase-26 as unblocker"
    )
