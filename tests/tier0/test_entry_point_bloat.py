"""
CORTEX Entry Point Bloat Prevention Test Harness

This SKULL test harness enforces strict token budget limits on the CORTEX entry point
to prevent regression back to bloated monolithic architecture.

SKULL Rule Enforced: SKULL-001 (Test Before Claim)
Protection Layer: Layer 2 (Token Budget Enforcement)

Token Limits:
- HARD LIMIT: 5,000 tokens (BLOCKING - tests fail if exceeded)
- WARNING LIMIT: 4,000 tokens (WARNING - generates alert)
- TARGET: 3,500 tokens (IDEAL - optimal performance)

Architecture Validation:
- Modular structure with #file: references
- No inline documentation (must be in shared modules)
- Response templates externalized to YAML
- Plugin documentation in separate files

Author: Asif Hussain
Created: 2025-11-10
CORTEX Version: 5.2
"""

import pytest
import os
from pathlib import Path
import re


# Token calculation constants
CHARS_PER_TOKEN = 4  # GPT-4 approximation

# Token budget limits (SKULL protection)
MAX_TOKENS_HARD_LIMIT = 5000  # BLOCKING
MAX_TOKENS_WARNING = 4000     # WARNING
TARGET_TOKENS = 3500          # IDEAL

# Architecture limits
MAX_LINES = 500
MAX_INLINE_DOCS = 100  # lines before requiring modularization


class TestEntryPointBloat:
    """Test suite for CORTEX entry point bloat prevention."""
    
    @pytest.fixture
    def entry_point_path(self):
        """Get path to CORTEX entry point."""
        cortex_root = os.environ.get('CORTEX_ROOT', Path(__file__).parent.parent.parent)
        return Path(cortex_root) / '.github' / 'prompts' / 'CORTEX.prompt.md'
    
    @pytest.fixture
    def entry_point_content(self, entry_point_path):
        """Read entry point file content."""
        assert entry_point_path.exists(), f"Entry point not found: {entry_point_path}"
        return entry_point_path.read_text(encoding='utf-8')
    
    def calculate_tokens(self, text: str) -> int:
        """Calculate approximate token count."""
        return len(text) // CHARS_PER_TOKEN
    
    def test_entry_point_exists(self, entry_point_path):
        """SKULL-001: Entry point file must exist."""
        assert entry_point_path.exists(), "Entry point file missing"
    
    def test_token_count_hard_limit(self, entry_point_content):
        """SKULL-001: Entry point MUST NOT exceed hard token limit (BLOCKING)."""
        tokens = self.calculate_tokens(entry_point_content)
        assert tokens <= MAX_TOKENS_HARD_LIMIT, (
            f"❌ BLOAT DETECTED: Entry point has {tokens} tokens "
            f"(HARD LIMIT: {MAX_TOKENS_HARD_LIMIT})\n"
            f"This is a BLOCKING failure. You must reduce token count before proceeding."
        )
    
    def test_token_count_warning(self, entry_point_content):
        """SKULL-001: Entry point should stay below warning threshold."""
        tokens = self.calculate_tokens(entry_point_content)
        if tokens > MAX_TOKENS_WARNING:
            pytest.warns(
                UserWarning,
                match=f"Entry point approaching token limit: {tokens}/{MAX_TOKENS_HARD_LIMIT}"
            )
    
    def test_token_count_target(self, entry_point_content):
        """SKULL-001: Entry point should aim for target token count (IDEAL)."""
        tokens = self.calculate_tokens(entry_point_content)
        percentage_of_target = (tokens / TARGET_TOKENS) * 100
        
        # This is informational, not blocking
        if tokens > TARGET_TOKENS:
            print(f"\n⚠️  INFO: Entry point is {percentage_of_target:.1f}% of target ({tokens}/{TARGET_TOKENS} tokens)")
        else:
            print(f"\n✅ OPTIMAL: Entry point is {percentage_of_target:.1f}% of target ({tokens}/{TARGET_TOKENS} tokens)")
    
    def test_line_count_limit(self, entry_point_content):
        """SKULL-001: Entry point should not exceed line count limit."""
        lines = entry_point_content.count('\n') + 1
        assert lines <= MAX_LINES, (
            f"Entry point has {lines} lines (MAX: {MAX_LINES}). "
            f"Consider modularizing large sections."
        )
    
    def test_references_valid_files(self, entry_point_content, entry_point_path):
        """SKULL-001: All #file: references must point to existing files."""
        # Extract all #file: references
        pattern = r'#file:([^\s\)`\)]+)'
        references = re.findall(pattern, entry_point_content)
        
        # Paths in entry point are relative to .github/prompts/ directory
        entry_point_dir = entry_point_path.parent
        missing_files = []
        
        for ref in references:
            # Resolve the path relative to entry point directory
            file_path = (entry_point_dir / ref).resolve()
            if not file_path.exists():
                missing_files.append(ref)
        
        assert not missing_files, (
            f"Broken #file: references found:\n" +
            "\n".join(f"  - {ref}" for ref in missing_files)
        )
    
    def test_no_excessive_inline_docs(self, entry_point_content):
        """SKULL-001: Excessive inline documentation should be modularized."""
        # Count lines that look like documentation (markdown headings, lists, paragraphs)
        doc_lines = 0
        for line in entry_point_content.split('\n'):
            stripped = line.strip()
            if stripped.startswith('#') or stripped.startswith('-') or stripped.startswith('*'):
                doc_lines += 1
        
        if doc_lines > MAX_INLINE_DOCS:
            pytest.warns(
                UserWarning,
                match=f"High inline documentation count: {doc_lines} lines"
            )
    
    def test_modular_architecture_present(self, entry_point_content):
        """SKULL-001: Entry point must use modular architecture (#file: references)."""
        # Must have at least 5 #file: references for proper modularization
        pattern = r'#file:([^\s\)`\)]+)'
        references = re.findall(pattern, entry_point_content)
        
        assert len(references) >= 5, (
            f"Insufficient modularization: only {len(references)} #file: references found. "
            f"Entry point should delegate to modular documentation."
        )
    
    def test_response_templates_externalized(self, entry_point_content):
        """SKULL-001: Response templates must be externalized to YAML."""
        assert 'response-templates.yaml' in entry_point_content, (
            "Entry point must reference response-templates.yaml for template-based responses"
        )
    
    def test_no_python_execution_for_help(self, entry_point_content):
        """SKULL-001: Help command should use templates, not Python execution."""
        # Entry point should mention template-based responses
        assert 'NO Python execution' in entry_point_content or 'template-based' in entry_point_content.lower(), (
            "Entry point should document template-based response system (no Python execution needed)"
        )
    
    def test_version_documented(self, entry_point_content):
        """SKULL-001: Entry point must document version number."""
        assert re.search(r'\*\*Version:\*\*\s+[\d.]+', entry_point_content), (
            "Entry point must include version number"
        )
    
    def test_status_documented(self, entry_point_content):
        """SKULL-001: Entry point must document production status."""
        assert 'PRODUCTION' in entry_point_content or 'Status:' in entry_point_content, (
            "Entry point must document production status"
        )
    
    def test_copyright_present(self, entry_point_content):
        """SKULL-001: Entry point must include copyright notice."""
        assert '©' in entry_point_content or 'Copyright' in entry_point_content, (
            "Entry point must include copyright notice"
        )
    
    def test_performance_metrics(self, entry_point_content):
        """SKULL-001: Log performance metrics for tracking."""
        tokens = self.calculate_tokens(entry_point_content)
        lines = entry_point_content.count('\n') + 1
        chars = len(entry_point_content)
        
        token_usage = (tokens / MAX_TOKENS_HARD_LIMIT) * 100
        line_usage = (lines / MAX_LINES) * 100
        
        print(f"\n{'='*60}")
        print(f"CORTEX Entry Point Performance Metrics")
        print(f"{'='*60}")
        print(f"Token Budget:")
        print(f"  Current:      {tokens:>6} tokens")
        print(f"  Target:       {TARGET_TOKENS:>6} tokens ({tokens/TARGET_TOKENS*100:.1f}%)")
        print(f"  Warning:      {MAX_TOKENS_WARNING:>6} tokens ({tokens/MAX_TOKENS_WARNING*100:.1f}%)")
        print(f"  Hard Limit:   {MAX_TOKENS_HARD_LIMIT:>6} tokens ({token_usage:.1f}%)")
        print(f"\nFile Metrics:")
        print(f"  Lines:        {lines:>6} / {MAX_LINES} ({line_usage:.1f}%)")
        print(f"  Characters:   {chars:>6}")
        print(f"  Words:        {len(entry_point_content.split()):>6}")
        print(f"\nArchitecture:")
        pattern = r'#file:([^\s\)`\)]+)'
        references = re.findall(pattern, entry_point_content)
        print(f"  Modular Refs: {len(references):>6} files")
        print(f"{'='*60}\n")


class TestEntryPointArchitecture:
    """Test suite for entry point architecture validation."""
    
    @pytest.fixture
    def entry_point_path(self):
        """Get path to CORTEX entry point."""
        cortex_root = os.environ.get('CORTEX_ROOT', Path(__file__).parent.parent.parent)
        return Path(cortex_root) / '.github' / 'prompts' / 'CORTEX.prompt.md'
    
    @pytest.fixture
    def entry_point_content(self, entry_point_path):
        """Read entry point file content."""
        return entry_point_path.read_text(encoding='utf-8')
    
    def test_quick_start_section(self, entry_point_content):
        """Entry point must have Quick Start section."""
        assert '## 🚀 Quick Start' in entry_point_content or '## Quick Start' in entry_point_content
    
    def test_help_command_documented(self, entry_point_content):
        """Entry point must document help command."""
        assert 'help' in entry_point_content.lower()
    
    def test_slash_commands_documented(self, entry_point_content):
        """Entry point must document available slash commands."""
        assert '/CORTEX' in entry_point_content or 'slash command' in entry_point_content.lower()
    
    def test_plugin_system_referenced(self, entry_point_content):
        """Entry point must reference plugin system."""
        assert 'plugin' in entry_point_content.lower()
    
    def test_tracking_system_referenced(self, entry_point_content):
        """Entry point must reference conversation tracking."""
        assert 'tracking' in entry_point_content.lower() or 'memory' in entry_point_content.lower()
    
    def test_brain_architecture_referenced(self, entry_point_content):
        """Entry point must reference brain tier architecture."""
        assert 'tier' in entry_point_content.lower() or 'brain' in entry_point_content.lower()


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
