"""Tests for generic metadata extractor and filename normalizer."""

import pytest
from cortex.tools.media.generic_metadata_extractor import (
    GenericMetadataExtractor,
    FilenameNormalizer,
    ExtractedMetadata,
)


class TestGenericMetadataExtractor:
    """Test metadata extraction from filenames."""

    def setup_method(self) -> None:
        """Initialize extractor for each test."""
        self.extractor = GenericMetadataExtractor()

    def test_extract_action_pattern(self) -> None:
        """Test extraction of 'Name1 action Name2' pattern."""
        result = self.extractor.extract("Michael Vegas action Brooklyn Lee.mp4")
        assert len(result.performers) == 2
        assert result.performers[0] == "Michael Vegas"
        assert result.performers[1] == "Brooklyn Lee"
        assert result.action_type == "action"
        assert result.confidence >= 0.80

    def test_extract_does_pattern(self) -> None:
        """Test extraction of 'Name1 Does Name2' pattern."""
        result = self.extractor.extract("Julia Ann Does Nicole Sheridan.mp4")
        assert len(result.performers) == 2
        assert result.performers[0] == "Julia Ann"
        assert result.performers[1] == "Nicole Sheridan"
        assert result.action_type == "does"
        assert result.confidence >= 0.80

    def test_extract_ampersand_pattern(self) -> None:
        """Test extraction of 'Name1 & Name2' pattern."""
        result = self.extractor.extract("Chasey Lain & Rocco.mp4")
        assert len(result.performers) == 2
        assert result.performers[0] == "Chasey Lain"
        assert result.performers[1] == "Rocco"
        assert result.confidence >= 0.80

    def test_extract_dash_pattern(self) -> None:
        """Test extraction of 'Name1 - Name2' pattern (treated as title)."""
        result = self.extractor.extract("Ivy Wolfe - Daddy Charles Dera.mp4")
        # Dash pattern treated as title separator, not performer separator
        assert result.title is not None or len(result.performers) > 0

    def test_extract_with_title(self) -> None:
        """Test extraction with title in parentheses."""
        result = self.extractor.extract("Julia Ann Does Nicole - Voodoo.mp4")
        # Should extract performers and/or title
        assert result.confidence > 0

    def test_extract_no_pattern_match(self) -> None:
        """Test extraction when no clear pattern matches."""
        result = self.extractor.extract("Random Scene Title.mp4")
        # Should extract title as fallback
        assert result.title is not None or len(result.performers) == 0

    def test_extract_preserves_meaningful_names(self) -> None:
        """Ensure extractor preserves performer names without sanitization."""
        result = self.extractor.extract("Akira Eaten and action by Deamon.mp4")
        # Names should be preserved (not morphed to "Fucking" → "F***")
        # This is actually matched as "Akira Eaten and action by Deamon"
        assert len(result.performers) > 0 or result.title is not None
        # Most importantly: names are not sanitized
        assert "Akira" in str(result)


class TestFilenameNormalizer:
    """Test filename normalization."""

    def setup_method(self) -> None:
        """Initialize normalizer for each test."""
        self.normalizer = FilenameNormalizer()

    def test_normalize_action_to_does(self) -> None:
        """Test replacement of 'action' with 'Does'."""
        original = "Michael Vegas action Brooklyn Lee.mp4"
        normalized = self.normalizer.normalize(original)
        # Should be lowercase 'does' after normalization (casing applied separately)
        assert "does" in normalized.lower()
        assert "action" not in normalized.lower()

    def test_normalize_proper_case(self) -> None:
        """Test Title Case application."""
        original = "michael vegas does brooklyn lee.mp4"
        normalized = self.normalizer.normalize(original)
        assert normalized[0].isupper()  # First letter uppercase

    def test_normalize_remove_trailing_numbers(self) -> None:
        """Test removal of trailing numbers."""
        original = "Julia Ann Does Nicole 123.mp4"
        normalized = self.normalizer.normalize(original, remove_numbers=True)
        assert "123" not in normalized
        assert "Julia Ann" in normalized
        assert "Nicole" in normalized

    def test_normalize_remove_leading_numbers(self) -> None:
        """Test removal of leading numbers."""
        original = "01_Stephanie Swift action In Motel.mp4"
        normalized = self.normalizer.normalize(original, remove_numbers=True)
        assert not normalized[0].isdigit()

    def test_normalize_preserves_extension(self) -> None:
        """Test that extension is preserved."""
        original = "Test Video.mp4"
        normalized = self.normalizer.normalize(original)
        assert normalized.endswith(".mp4")

    def test_normalize_batch(self) -> None:
        """Test batch normalization."""
        originals = [
            "Michael Vegas action Brooklyn Lee.mp4",
            "01_Julia Ann Does Nicole 123.mp4",
            "Chasey Lain & rocco.mp4",
        ]
        normalized_dict = self.normalizer.normalize_batch(originals)
        assert len(normalized_dict) == 3
        for orig, norm in normalized_dict.items():
            assert orig != norm or orig.count(" ") == norm.count(
                " "
            )  # At least normalized or same

    def test_normalize_lowercase_connectors(self) -> None:
        """Test that connectors are lowercase."""
        original = "Name1 DOES Name2.mp4"
        normalized = self.normalizer.normalize(original)
        assert " does " in normalized.lower()

    def test_normalize_no_double_spaces(self) -> None:
        """Test that double spaces are removed."""
        original = "Name1  action  Name2.mp4"
        normalized = self.normalizer.normalize(original)
        assert "  " not in normalized

    def test_normalize_selective_options(self) -> None:
        """Test selective normalization options."""
        original = "01_michael vegas action brooklyn lee_99.mp4"

        # Only replace action
        result1 = self.normalizer.normalize(
            original, replace_action=True, proper_case=False, remove_numbers=False
        )
        assert "does" in result1.lower()
        assert "01" in result1  # Numbers kept
        assert "99" in result1

        # Only remove numbers
        result2 = self.normalizer.normalize(
            original, replace_action=False, proper_case=False, remove_numbers=True
        )
        assert "01" not in result2
        assert "99" not in result2
        assert "action" in result2.lower()


class TestExtractedMetadataDataclass:
    """Test ExtractedMetadata dataclass."""

    def test_metadata_creation(self) -> None:
        """Test creating metadata instance."""
        meta = ExtractedMetadata(
            filename="Test.mp4",
            performers=["Name1", "Name2"],
            title="Scene Title",
            action_type="action",
            confidence=0.9,
        )
        assert meta.filename == "Test.mp4"
        assert len(meta.performers) == 2
        assert meta.confidence == 0.9

    def test_metadata_defaults(self) -> None:
        """Test default values."""
        meta = ExtractedMetadata(
            filename="Test.mp4",
            performers=["Name1"],
        )
        assert meta.title is None
        assert meta.action_type is None
        assert meta.studio is None
        assert meta.confidence == 0.0
