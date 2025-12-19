#!/usr/bin/env python3
"""
Test MkDocs UTF-8 Encoding Correctness

Validates that all MkDocs sites render UTF-8 characters correctly
without double-encoding artifacts.

Usage:
    python tests/test_mkdocs_encoding.py
"""

import pytest
from pathlib import Path
import re


class TestMkDocsEncoding:
    """Test suite for MkDocs UTF-8 encoding correctness."""
    
    # UTF-8 characters that should render correctly
    CORRECT_UTF8_CHARS = {
        '—': 'em dash',
        '✓': 'checkmark',
        '✅': 'check mark button emoji',
        '🎯': 'direct hit emoji',
        '…': 'ellipsis',
        '"': 'left double quote',
        '"': 'right double quote',
        ''': 'left single quote',
        ''': 'right single quote',
        '→': 'rightward arrow',
        '←': 'leftward arrow',
    }
    
    # Garbled patterns from double-encoding (UTF-8 → cp1252 → UTF-8)
    GARBLED_PATTERNS = {
        'ΓÇö': 'em dash garbled',
        'Γ£à': 'checkmark garbled',
        '≡ƒôï': 'emoji garbled',
        'ΓÇÖ': 'apostrophe garbled',
        'ΓÇô': 'en dash garbled',
        'Γäó': 'trademark garbled',
        'ΓÇª': 'ellipsis garbled',
        'ΓÇ£': 'left quote garbled',
        'ΓÇ¥': 'right quote garbled',
    }
    
    @pytest.fixture
    def site_dir(self):
        """Get the MkDocs site output directory."""
        return Path('site')
    
    @pytest.fixture
    def story_html(self, site_dir):
        """Get the main story HTML file."""
        story_file = site_dir / 'diagrams' / 'story' / 'The-CORTEX-Story' / 'index.html'
        if not story_file.exists():
            pytest.skip(f"Story file not found: {story_file}. Run 'mkdocs build' first.")
        return story_file
    
    def test_site_directory_exists(self, site_dir):
        """Test that MkDocs site has been built."""
        assert site_dir.exists(), (
            "MkDocs site directory not found. Run 'mkdocs build' first."
        )
    
    def test_html_has_utf8_charset(self, story_html):
        """Test that HTML files declare UTF-8 charset."""
        content = story_html.read_text(encoding='utf-8')
        
        # Check for charset declaration
        charset_pattern = r'<meta\s+charset=["\']?utf-8["\']?'
        assert re.search(charset_pattern, content, re.IGNORECASE), (
            "HTML missing UTF-8 charset declaration"
        )
    
    def test_no_garbled_text_in_story(self, story_html):
        """Test that story HTML has no garbled UTF-8 patterns."""
        content = story_html.read_text(encoding='utf-8')
        
        found_garbled = []
        for pattern, description in self.GARBLED_PATTERNS.items():
            if pattern in content:
                # Find context
                matches = [m.start() for m in re.finditer(re.escape(pattern), content)]
                for idx in matches[:3]:  # Show first 3 occurrences
                    context_start = max(0, idx - 50)
                    context_end = min(len(content), idx + 50)
                    context = content[context_start:context_end]
                    found_garbled.append(
                        f"\n  '{pattern}' ({description}):\n    ...{context}..."
                    )
        
        assert not found_garbled, (
            f"Found garbled UTF-8 patterns in {story_html}:"
            f"{''.join(found_garbled)}"
        )
    
    def test_correct_utf8_chars_present(self, story_html):
        """Test that correct UTF-8 characters are present."""
        content = story_html.read_text(encoding='utf-8')
        
        # We expect at least some UTF-8 chars to be present
        found_chars = []
        for char, description in self.CORRECT_UTF8_CHARS.items():
            if char in content:
                found_chars.append(f"{char} ({description})")
        
        # Should have at least a few UTF-8 characters
        assert len(found_chars) >= 3, (
            f"Expected to find UTF-8 characters in story, but only found: "
            f"{', '.join(found_chars) if found_chars else 'none'}"
        )
    
    def test_all_html_files_no_garbled(self, site_dir):
        """Test that all HTML files have no garbled text."""
        html_files = list(site_dir.rglob('*.html'))
        
        assert html_files, "No HTML files found in site directory"
        
        files_with_issues = []
        
        for html_file in html_files:
            try:
                content = html_file.read_text(encoding='utf-8')
                
                # Check for garbled patterns
                for pattern in self.GARBLED_PATTERNS.keys():
                    if pattern in content:
                        relative_path = html_file.relative_to(site_dir)
                        files_with_issues.append(str(relative_path))
                        break  # One issue per file is enough
            except Exception as e:
                pytest.fail(f"Error reading {html_file}: {e}")
        
        assert not files_with_issues, (
            f"Found garbled UTF-8 in {len(files_with_issues)} files:\n  " +
            '\n  '.join(files_with_issues[:10]) +  # Show first 10
            (f"\n  ... and {len(files_with_issues) - 10} more" 
             if len(files_with_issues) > 10 else "")
        )
    
    def test_python_encoding_environment(self):
        """Test that Python environment is configured for UTF-8."""
        import sys
        import os
        
        # Check default encoding
        assert sys.getdefaultencoding() == 'utf-8', (
            f"Python default encoding should be utf-8, got: {sys.getdefaultencoding()}"
        )
        
        # Check environment variables
        pythonutf8 = os.environ.get('PYTHONUTF8')
        if pythonutf8 is not None:
            assert pythonutf8 == '1', (
                f"PYTHONUTF8 should be '1', got: {pythonutf8}"
            )


class TestMkDocsEncodingIntegration:
    """Integration tests for MkDocs encoding across all sites."""
    
    def test_main_site_encoding(self):
        """Test main CORTEX site encoding."""
        site_dir = Path('site')
        if not site_dir.exists():
            pytest.skip("Main site not built")
        
        index_file = site_dir / 'index.html'
        if index_file.exists():
            content = index_file.read_text(encoding='utf-8')
            assert 'ΓÇö' not in content, "Main site has encoding issues"
    
    def test_diagrams_site_encoding(self):
        """Test diagrams sub-site encoding."""
        diagrams_site = Path('docs/diagrams/site')
        if not diagrams_site.exists():
            pytest.skip("Diagrams site not built")
        
        # Check a few HTML files
        for html_file in list(diagrams_site.rglob('*.html'))[:5]:
            content = html_file.read_text(encoding='utf-8')
            garbled = ['ΓÇö', 'Γ£à', '≡ƒôï']
            for pattern in garbled:
                assert pattern not in content, (
                    f"Diagrams site has encoding issues in {html_file.name}"
                )


if __name__ == '__main__':
    # Run tests
    pytest.main([__file__, '-v', '--tb=short'])
