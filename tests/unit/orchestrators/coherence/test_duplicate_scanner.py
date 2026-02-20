"""
Tests for DuplicateScanner.

AC_START: AC-ENH-101-007
Description: TDD tests for DuplicateScanner
Authority: ENH-101 Stage S3 - WAVE-10 Quality
Compliance: CORE-008 (tests first), Zero mocks for core logic
"""

import pytest

from cortex.orchestrators.validation.duplicate_scanner import (
    ConsolidationSuggestion,
    DuplicateScanner,
    ScanResult,
)
from cortex.orchestrators.validation.coherence_models import DuplicateMatch, Section, SectionType


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def scanner() -> DuplicateScanner:
    """Create a default scanner."""
    return DuplicateScanner()


@pytest.fixture
def scanner_low_threshold() -> DuplicateScanner:
    """Create a scanner with low similarity threshold."""
    return DuplicateScanner(similarity_threshold=0.5)


@pytest.fixture
def sample_sections() -> list[Section]:
    """Create sample sections for testing."""
    return [
        Section(
            name="Introduction",
            section_type=SectionType.MARKDOWN_H1,
            start_line=1,
            end_line=10,
            level=1,
            content="This is the introduction section.",
        ),
        Section(
            name="Installation",
            section_type=SectionType.MARKDOWN_H1,
            start_line=11,
            end_line=20,
            level=1,
            content="Install with pip install package.",
        ),
        Section(
            name="Usage",
            section_type=SectionType.MARKDOWN_H1,
            start_line=21,
            end_line=30,
            level=1,
            content="Use the package like this.",
        ),
    ]


@pytest.fixture
def duplicate_sections() -> list[Section]:
    """Create sections with duplicates."""
    return [
        Section(
            name="MCP Rules",
            section_type=SectionType.MARKDOWN_H2,
            start_line=1,
            end_line=10,
            level=1,
            content="MCP is mandatory.",
        ),
        Section(
            name="TDD Rules",
            section_type=SectionType.MARKDOWN_H2,
            start_line=11,
            end_line=20,
            level=1,
            content="TDD is required.",
        ),
        Section(
            name="MCP Rules",  # Exact duplicate name
            section_type=SectionType.MARKDOWN_H2,
            start_line=21,
            end_line=30,
            level=1,
            content="MCP is required for all operations.",
        ),
        Section(
            name="MCP Rules",  # Another duplicate
            section_type=SectionType.MARKDOWN_H2,
            start_line=31,
            end_line=40,
            level=1,
            content="MCP tools must be used.",
        ),
    ]


# =============================================================================
# TEST: INITIALIZATION
# =============================================================================

class TestDuplicateScannerInit:
    """Tests for DuplicateScanner initialization."""
    
    def test_default_threshold(self) -> None:
        """Default similarity threshold is 0.8."""
        scanner = DuplicateScanner()
        assert scanner._threshold == 0.8
    
    def test_custom_threshold(self) -> None:
        """Custom threshold is applied."""
        scanner = DuplicateScanner(similarity_threshold=0.6)
        assert scanner._threshold == 0.6
    
    def test_threshold_range(self) -> None:
        """Threshold can be any float from 0 to 1."""
        scanner_low = DuplicateScanner(similarity_threshold=0.0)
        scanner_high = DuplicateScanner(similarity_threshold=1.0)
        assert scanner_low._threshold == 0.0
        assert scanner_high._threshold == 1.0


# =============================================================================
# TEST: SCAN SECTIONS
# =============================================================================

class TestScanSections:
    """Tests for scan_sections method."""
    
    def test_no_duplicates(
        self,
        scanner: DuplicateScanner,
        sample_sections: list[Section],
    ) -> None:
        """No duplicates found when all sections are unique."""
        result = scanner.scan_sections(sample_sections)
        
        assert isinstance(result, ScanResult)
        assert not result.has_duplicates
        assert result.total_count == 0
        assert len(result.exact_duplicates) == 0
        assert len(result.near_duplicates) == 0
    
    def test_exact_duplicates_found(
        self,
        scanner: DuplicateScanner,
        duplicate_sections: list[Section],
    ) -> None:
        """Exact duplicates are detected by name."""
        result = scanner.scan_sections(duplicate_sections)
        
        assert result.has_duplicates
        assert len(result.exact_duplicates) == 2  # 3 "MCP Rules" = 2 duplicates
        
        for dup in result.exact_duplicates:
            assert dup.is_exact
            assert dup.similarity == 1.0
            assert dup.original_section.name.lower() == "mcp rules"
    
    def test_near_duplicates_found(
        self,
        scanner_low_threshold: DuplicateScanner,
    ) -> None:
        """Near duplicates are detected by similar names."""
        sections = [
            Section(
                name="Installation Guide",
                section_type=SectionType.MARKDOWN_H2,
                start_line=1,
                end_line=10,
                level=1,
            ),
            Section(
                name="Installation Instructions",
                section_type=SectionType.MARKDOWN_H2,
                start_line=11,
                end_line=20,
                level=1,
            ),
        ]
        
        result = scanner_low_threshold.scan_sections(sections)
        
        assert result.has_duplicates
        assert len(result.near_duplicates) >= 1
        assert not result.near_duplicates[0].is_exact
    
    def test_empty_sections_list(self, scanner: DuplicateScanner) -> None:
        """Empty section list returns empty result."""
        result = scanner.scan_sections([])
        
        assert not result.has_duplicates
        assert result.total_count == 0
    
    def test_consolidation_suggestions_generated(
        self,
        scanner: DuplicateScanner,
        duplicate_sections: list[Section],
    ) -> None:
        """Consolidation suggestions are generated for duplicates."""
        result = scanner.scan_sections(duplicate_sections)
        
        assert len(result.consolidation_suggestions) > 0
        
        suggestion = result.consolidation_suggestions[0]
        assert isinstance(suggestion, ConsolidationSuggestion)
        assert suggestion.action in ("keep_first", "merge")
        assert suggestion.recommended_location >= 1


# =============================================================================
# TEST: CALCULATE SIMILARITY
# =============================================================================

class TestCalculateSimilarity:
    """Tests for calculate_similarity method."""
    
    def test_identical_strings(self, scanner: DuplicateScanner) -> None:
        """Identical strings have similarity of 1.0."""
        similarity = scanner.calculate_similarity(
            "Hello World",
            "Hello World",
        )
        assert similarity == 1.0
    
    def test_completely_different(self, scanner: DuplicateScanner) -> None:
        """Completely different strings have low similarity."""
        similarity = scanner.calculate_similarity(
            "abc xyz",
            "123 456",
        )
        assert similarity < 0.3
    
    def test_similar_strings(self, scanner: DuplicateScanner) -> None:
        """Similar strings have high similarity."""
        similarity = scanner.calculate_similarity(
            "Installation Guide",
            "Installation Instructions",
        )
        assert similarity > 0.5
    
    def test_case_insensitive(self, scanner: DuplicateScanner) -> None:
        """Similarity is case insensitive."""
        similarity = scanner.calculate_similarity(
            "HELLO WORLD",
            "hello world",
        )
        assert similarity == 1.0
    
    def test_whitespace_normalized(self, scanner: DuplicateScanner) -> None:
        """Whitespace is normalized before comparison."""
        similarity = scanner.calculate_similarity(
            "Hello    World",
            "Hello World",
        )
        assert similarity == 1.0
    
    def test_empty_strings(self, scanner: DuplicateScanner) -> None:
        """Empty strings return 0.0 similarity."""
        assert scanner.calculate_similarity("", "") == 0.0
        assert scanner.calculate_similarity("hello", "") == 0.0
        assert scanner.calculate_similarity("", "world") == 0.0


# =============================================================================
# TEST: SCAN FOR PATTERN
# =============================================================================

class TestScanForPattern:
    """Tests for scan_for_pattern method."""
    
    def test_pattern_found(self, scanner: DuplicateScanner) -> None:
        """Pattern matches are returned with line numbers."""
        content = """Line 1: Hello
Line 2: World
Line 3: Hello again
Line 4: Goodbye"""
        
        matches = scanner.scan_for_pattern(content, r"Hello")
        
        assert len(matches) == 2
        assert matches[0][0] == 1  # Line 1
        assert matches[1][0] == 3  # Line 3
        assert "Hello" in matches[0][1]
        assert "Hello" in matches[1][1]
    
    def test_pattern_not_found(self, scanner: DuplicateScanner) -> None:
        """Empty list when pattern not found."""
        content = "No matches here"
        
        matches = scanner.scan_for_pattern(content, r"xyz")
        
        assert len(matches) == 0
    
    def test_regex_pattern(self, scanner: DuplicateScanner) -> None:
        """Regex patterns work correctly."""
        content = """GAP-001: First gap
GAP-002: Second gap
ISSUE-001: First issue"""
        
        matches = scanner.scan_for_pattern(content, r"GAP-\d+")
        
        assert len(matches) == 2
        assert "GAP-001" in matches[0][1]
        assert "GAP-002" in matches[1][1]
    
    def test_case_insensitive_search(self, scanner: DuplicateScanner) -> None:
        """Pattern search is case insensitive."""
        content = """MCP Rules
mcp rules
MCP RULES"""
        
        matches = scanner.scan_for_pattern(content, r"mcp rules")
        
        assert len(matches) == 3


# =============================================================================
# TEST: CONTENT DUPLICATES
# =============================================================================

class TestFindContentDuplicates:
    """Tests for find_content_duplicates method."""
    
    def test_exact_content_match(self, scanner: DuplicateScanner) -> None:
        """Sections with identical content are marked as exact duplicates."""
        sections = [
            Section(
                name="Section A",
                section_type=SectionType.MARKDOWN_H2,
                start_line=1,
                end_line=10,
                level=1,
                content="This is the exact same content.",
            ),
            Section(
                name="Section B",
                section_type=SectionType.MARKDOWN_H2,
                start_line=11,
                end_line=20,
                level=1,
                content="This is the exact same content.",
            ),
        ]
        
        duplicates = scanner.find_content_duplicates(sections)
        
        assert len(duplicates) == 1
        assert duplicates[0].is_exact
        assert duplicates[0].similarity >= 0.99
    
    def test_similar_content(
        self,
        scanner_low_threshold: DuplicateScanner,
    ) -> None:
        """Sections with similar content are detected as near-duplicates."""
        sections = [
            Section(
                name="Section A",
                section_type=SectionType.MARKDOWN_H2,
                start_line=1,
                end_line=10,
                level=1,
                content="MCP tools are mandatory for all operations.",
            ),
            Section(
                name="Section B",
                section_type=SectionType.MARKDOWN_H2,
                start_line=11,
                end_line=20,
                level=1,
                content="MCP tools are required for all operations.",
            ),
        ]
        
        duplicates = scanner_low_threshold.find_content_duplicates(sections)
        
        assert len(duplicates) == 1
        assert duplicates[0].similarity > 0.5
    
    def test_no_content_duplicates(self, scanner: DuplicateScanner) -> None:
        """Different content sections are not marked as duplicates."""
        sections = [
            Section(
                name="Section A",
                section_type=SectionType.MARKDOWN_H2,
                start_line=1,
                end_line=10,
                level=1,
                content="ABC XYZ 123",
            ),
            Section(
                name="Section B",
                section_type=SectionType.MARKDOWN_H2,
                start_line=11,
                end_line=20,
                level=1,
                content="Completely different content here.",
            ),
        ]
        
        duplicates = scanner.find_content_duplicates(sections)
        
        assert len(duplicates) == 0
    
    def test_empty_content_skipped(self, scanner: DuplicateScanner) -> None:
        """Sections without content are skipped."""
        sections = [
            Section(
                name="Section A",
                section_type=SectionType.MARKDOWN_H2,
                start_line=1,
                end_line=10,
                level=1,
                content="",
            ),
            Section(
                name="Section B",
                section_type=SectionType.MARKDOWN_H2,
                start_line=11,
                end_line=20,
                level=1,
                content="Some content",
            ),
        ]
        
        duplicates = scanner.find_content_duplicates(sections)
        
        assert len(duplicates) == 0


# =============================================================================
# TEST: CONSOLIDATION SUGGESTIONS
# =============================================================================

class TestConsolidationSuggestions:
    """Tests for suggest_consolidation method."""
    
    def test_exact_duplicates_suggest_keep_first(
        self,
        scanner: DuplicateScanner,
    ) -> None:
        """Exact duplicates suggest 'keep_first' action."""
        original = Section(
            name="MCP Rules",
            section_type=SectionType.MARKDOWN_H2,
            start_line=1,
            end_line=10,
            level=1,
        )
        duplicate = Section(
            name="MCP Rules",
            section_type=SectionType.MARKDOWN_H2,
            start_line=50,
            end_line=60,
            level=1,
        )
        
        duplicates = [
            DuplicateMatch(
                original_section=original,
                duplicate_section=duplicate,
                similarity=1.0,
                is_exact=True,
            ),
        ]
        
        suggestions = scanner.suggest_consolidation(duplicates)
        
        assert len(suggestions) == 1
        assert suggestions[0].action == "keep_first"
        assert suggestions[0].recommended_location == 1
    
    def test_near_duplicates_suggest_merge(
        self,
        scanner: DuplicateScanner,
    ) -> None:
        """Near duplicates suggest 'merge' action."""
        original = Section(
            name="Installation",
            section_type=SectionType.MARKDOWN_H2,
            start_line=10,
            end_line=20,
            level=1,
        )
        duplicate = Section(
            name="Installation Guide",
            section_type=SectionType.MARKDOWN_H2,
            start_line=30,
            end_line=40,
            level=1,
        )
        
        duplicates = [
            DuplicateMatch(
                original_section=original,
                duplicate_section=duplicate,
                similarity=0.85,
                is_exact=False,
            ),
        ]
        
        suggestions = scanner.suggest_consolidation(duplicates)
        
        assert len(suggestions) == 1
        assert suggestions[0].action == "merge"
    
    def test_empty_duplicates_no_suggestions(
        self,
        scanner: DuplicateScanner,
    ) -> None:
        """Empty duplicates list returns no suggestions."""
        suggestions = scanner.suggest_consolidation([])
        
        assert len(suggestions) == 0


# =============================================================================
# TEST: SCAN RESULT DATA CLASS
# =============================================================================

class TestScanResult:
    """Tests for ScanResult data class."""
    
    def test_has_duplicates_true(self) -> None:
        """has_duplicates is True when duplicates exist."""
        result = ScanResult(
            exact_duplicates=[],
            near_duplicates=[],
            all_duplicates=[
                DuplicateMatch(
                    original_section=Section(
                        name="A",
                        section_type=SectionType.MARKDOWN_H2,
                        start_line=1,
                        end_line=10,
                        level=1,
                    ),
                    duplicate_section=Section(
                        name="A",
                        section_type=SectionType.MARKDOWN_H2,
                        start_line=11,
                        end_line=20,
                        level=1,
                    ),
                    similarity=1.0,
                    is_exact=True,
                ),
            ],
        )
        
        assert result.has_duplicates
    
    def test_has_duplicates_false(self) -> None:
        """has_duplicates is False when no duplicates."""
        result = ScanResult()
        
        assert not result.has_duplicates
    
    def test_total_count(self) -> None:
        """total_count returns length of all_duplicates."""
        result = ScanResult(
            all_duplicates=[
                DuplicateMatch(
                    original_section=Section(
                        name="A",
                        section_type=SectionType.MARKDOWN_H2,
                        start_line=1,
                        end_line=10,
                        level=1,
                    ),
                    duplicate_section=Section(
                        name="A",
                        section_type=SectionType.MARKDOWN_H2,
                        start_line=11,
                        end_line=20,
                        level=1,
                    ),
                    similarity=1.0,
                    is_exact=True,
                ),
            ] * 3,
        )
        
        assert result.total_count == 3


# AC_COMPLETE: AC-ENH-101-007 ✅ DuplicateScanner tests
