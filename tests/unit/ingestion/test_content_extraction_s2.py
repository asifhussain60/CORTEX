"""
Phase 49 S2: Content Extraction Engine - Multi-Format Text Extraction

Tests for extracting text and structure from Word/Excel/PPT/PDF/Markdown.

Authority: phase-49-document-ingestion-pipeline.yaml
Acceptance Criteria:
  - AC-PHASE49-S2-001: Extracts plain text from all formats
  - AC-PHASE49-S2-002: Preserves heading hierarchy (H1/H2/H3)
  - AC-PHASE49-S2-003: Extracts tables as structured data
"""

import pytest
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class HeadingLevel(Enum):
    """Heading hierarchy levels."""
    H1 = 1
    H2 = 2
    H3 = 3
    H4 = 4
    H5 = 5


@dataclass
class HeadingElement:
    """Heading in document."""
    level: HeadingLevel
    text: str


@dataclass
class TableElement:
    """Table in document."""
    headers: List[str]
    rows: List[List[str]]
    
    def row_count(self) -> int:
        """Get row count."""
        return len(self.rows)
    
    def column_count(self) -> int:
        """Get column count."""
        return len(self.headers)


@dataclass
class ExtractedContent:
    """Extracted document content."""
    plain_text: str
    headings: List[HeadingElement]
    tables: List[TableElement]
    paragraphs: List[str]
    links: List[Dict[str, str]]
    images: List[str]
    metadata: Dict[str, Any]


class ExtractionEngine:
    """Abstract content extraction engine."""
    
    def extract_text(self, content: bytes) -> str:
        """Extract plain text."""
        raise NotImplementedError
    
    def extract_structure(self, content: bytes) -> ExtractedContent:
        """Extract structured content."""
        raise NotImplementedError


class WordExtractor(ExtractionEngine):
    """Word (.docx) content extractor."""
    
    def extract_text(self, content: bytes) -> str:
        """Extract plain text from Word document."""
        # Mock: simple extraction of words from mock format
        if b"WORD_DOCUMENT" in content:
            return content.decode('utf-8', errors='ignore').replace("WORD_DOCUMENT:", "")
        return ""
    
    def extract_structure(self, content: bytes) -> ExtractedContent:
        """Extract structured content from Word document."""
        text = self.extract_text(content)
        
        # Mock parsing: extract headings and paragraphs
        headings = []
        paragraphs = []
        
        lines = text.split("\n")
        for line in lines:
            if line.startswith("# "):
                headings.append(HeadingElement(HeadingLevel.H1, line[2:]))
            elif line.startswith("## "):
                headings.append(HeadingElement(HeadingLevel.H2, line[3:]))
            elif line.startswith("### "):
                headings.append(HeadingElement(HeadingLevel.H3, line[4:]))
            elif line.strip():
                paragraphs.append(line)
        
        return ExtractedContent(
            plain_text=text,
            headings=headings,
            tables=[],
            paragraphs=paragraphs,
            links=[],
            images=[],
            metadata={"format": "docx"}
        )


class ExcelExtractor(ExtractionEngine):
    """Excel (.xlsx) content extractor."""
    
    def extract_text(self, content: bytes) -> str:
        """Extract plain text from Excel document."""
        if b"EXCEL_SPREADSHEET" in content:
            return content.decode('utf-8', errors='ignore').replace("EXCEL_SPREADSHEET:", "")
        return ""
    
    def extract_structure(self, content: bytes) -> ExtractedContent:
        """Extract structured content from Excel document."""
        text = self.extract_text(content)
        
        # Mock: extract tables from Excel (each line is a row)
        tables = []
        lines = text.split("\n")
        
        if lines:
            # First line is headers
            headers = lines[0].split("|") if "|" in lines[0] else [lines[0]]
            rows = []
            
            for line in lines[1:]:
                if line.strip():
                    rows.append(line.split("|") if "|" in line else [line])
            
            if rows:
                tables.append(TableElement(headers=headers, rows=rows))
        
        return ExtractedContent(
            plain_text=text,
            headings=[],
            tables=tables,
            paragraphs=[],
            links=[],
            images=[],
            metadata={"format": "xlsx", "sheet_count": 1}
        )


class PDFExtractor(ExtractionEngine):
    """PDF content extractor."""
    
    def extract_text(self, content: bytes) -> str:
        """Extract plain text from PDF document."""
        if b"PDF_DOCUMENT" in content:
            return content.decode('utf-8', errors='ignore').replace("PDF_DOCUMENT:", "")
        return ""
    
    def extract_structure(self, content: bytes) -> ExtractedContent:
        """Extract structured content from PDF document."""
        text = self.extract_text(content)
        
        # Mock: parse PDF structure
        headings = []
        paragraphs = []
        
        lines = text.split("\n")
        for line in lines:
            if line.startswith("HEADING:"):
                heading_text = line.replace("HEADING:", "").strip()
                headings.append(HeadingElement(HeadingLevel.H1, heading_text))
            elif line.strip():
                paragraphs.append(line)
        
        return ExtractedContent(
            plain_text=text,
            headings=headings,
            tables=[],
            paragraphs=paragraphs,
            links=[],
            images=[],
            metadata={"format": "pdf", "page_count": 1}
        )


class MarkdownExtractor(ExtractionEngine):
    """Markdown content extractor."""
    
    def extract_text(self, content: bytes) -> str:
        """Extract plain text from Markdown document."""
        return content.decode('utf-8', errors='ignore')
    
    def extract_structure(self, content: bytes) -> ExtractedContent:
        """Extract structured content from Markdown document."""
        text = self.extract_text(content)
        
        # Parse Markdown structure
        headings = []
        paragraphs = []
        links = []
        
        lines = text.split("\n")
        current_paragraph = []
        
        for line in lines:
            if line.startswith("# "):
                if current_paragraph:
                    paragraphs.append(" ".join(current_paragraph))
                    current_paragraph = []
                headings.append(HeadingElement(HeadingLevel.H1, line[2:]))
            elif line.startswith("## "):
                if current_paragraph:
                    paragraphs.append(" ".join(current_paragraph))
                    current_paragraph = []
                headings.append(HeadingElement(HeadingLevel.H2, line[3:]))
            elif line.startswith("### "):
                if current_paragraph:
                    paragraphs.append(" ".join(current_paragraph))
                    current_paragraph = []
                headings.append(HeadingElement(HeadingLevel.H3, line[4:]))
            elif "[" in line and "](" in line:
                # Extract links
                import re
                matches = re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', line)
                for text_part, url in matches:
                    links.append({"text": text_part, "url": url})
                current_paragraph.append(line)
            elif line.strip():
                current_paragraph.append(line)
        
        if current_paragraph:
            paragraphs.append(" ".join(current_paragraph))
        
        return ExtractedContent(
            plain_text=text,
            headings=headings,
            tables=[],
            paragraphs=paragraphs,
            links=links,
            images=[],
            metadata={"format": "markdown"}
        )


class PowerPointExtractor(ExtractionEngine):
    """PowerPoint (.pptx) content extractor."""
    
    def extract_text(self, content: bytes) -> str:
        """Extract plain text from PowerPoint document."""
        if b"POWERPOINT_DOCUMENT" in content:
            return content.decode('utf-8', errors='ignore').replace("POWERPOINT_DOCUMENT:", "")
        return ""
    
    def extract_structure(self, content: bytes) -> ExtractedContent:
        """Extract structured content from PowerPoint document."""
        text = self.extract_text(content)
        
        # Mock: extract slide content
        headings = []
        paragraphs = []
        
        slides = text.split("SLIDE:")
        for slide in slides[1:]:  # Skip first empty split
            lines = slide.strip().split("\n")
            if lines:
                # First line is slide title
                headings.append(HeadingElement(HeadingLevel.H1, lines[0]))
                # Rest are content
                for line in lines[1:]:
                    if line.strip():
                        paragraphs.append(line)
        
        return ExtractedContent(
            plain_text=text,
            headings=headings,
            tables=[],
            paragraphs=paragraphs,
            links=[],
            images=[],
            metadata={"format": "pptx", "slide_count": len(slides) - 1}
        )


# ============================================================================
# TESTS: Plain Text Extraction (AC-PHASE49-S2-001)
# ============================================================================

class TestPlainTextExtraction:
    """Test plain text extraction from all formats."""
    
    def test_extract_text_from_word(self):
        """Test extracting plain text from Word document."""
        word_content = b"WORD_DOCUMENT:This is a policy document. It contains compliance rules."
        extractor = WordExtractor()
        
        text = extractor.extract_text(word_content)
        
        assert "policy document" in text
        assert "compliance rules" in text
    
    def test_extract_text_from_excel(self):
        """Test extracting plain text from Excel document."""
        excel_content = b"EXCEL_SPREADSHEET:Compliance|Status\nPCI-DSS|Implemented\nHIPAA|Planned"
        extractor = ExcelExtractor()
        
        text = extractor.extract_text(excel_content)
        
        assert "Compliance" in text
        assert "PCI-DSS" in text
    
    def test_extract_text_from_pdf(self):
        """Test extracting plain text from PDF document."""
        pdf_content = b"PDF_DOCUMENT:Security Guidelines\n\nChapter 1: Access Control"
        extractor = PDFExtractor()
        
        text = extractor.extract_text(pdf_content)
        
        assert "Security Guidelines" in text
        assert "Access Control" in text
    
    def test_extract_text_from_markdown(self):
        """Test extracting plain text from Markdown document."""
        md_content = b"# Architecture\n\n## Overview\n\nMicroservices-based system."
        extractor = MarkdownExtractor()
        
        text = extractor.extract_text(md_content)
        
        assert "Architecture" in text
        assert "Microservices" in text
    
    def test_extract_text_from_powerpoint(self):
        """Test extracting plain text from PowerPoint document."""
        ppt_content = b"POWERPOINT_DOCUMENT:SLIDE:Enterprise Architecture\nEvent-driven design SLIDE:Security"
        extractor = PowerPointExtractor()
        
        text = extractor.extract_text(ppt_content)
        
        assert "Enterprise Architecture" in text


# ============================================================================
# TESTS: Heading Hierarchy (AC-PHASE49-S2-002)
# ============================================================================

class TestHeadingHierarchy:
    """Test preservation of heading hierarchy."""
    
    def test_preserve_heading_levels_word(self):
        """Test Word document heading levels are preserved."""
        word_content = b"WORD_DOCUMENT:# Main Title\n## Subsection\n## Another Subsection\n### Detail"
        extractor = WordExtractor()
        
        extracted = extractor.extract_structure(word_content)
        
        assert len(extracted.headings) == 4
        assert extracted.headings[0].level == HeadingLevel.H1
        assert extracted.headings[1].level == HeadingLevel.H2
        assert extracted.headings[2].level == HeadingLevel.H2
        assert extracted.headings[3].level == HeadingLevel.H3
    
    def test_preserve_heading_levels_markdown(self):
        """Test Markdown heading levels are preserved."""
        md_content = b"# Level 1\n## Level 2\n### Level 3\n## Another Level 2"
        extractor = MarkdownExtractor()
        
        extracted = extractor.extract_structure(md_content)
        
        assert len(extracted.headings) == 4
        assert extracted.headings[0].level == HeadingLevel.H1
        assert extracted.headings[1].level == HeadingLevel.H2
        assert extracted.headings[2].level == HeadingLevel.H3
        assert extracted.headings[3].level == HeadingLevel.H2
    
    def test_preserve_heading_levels_pdf(self):
        """Test PDF heading levels are preserved."""
        pdf_content = b"PDF_DOCUMENT:HEADING:Main Title\nContent here"
        extractor = PDFExtractor()
        
        extracted = extractor.extract_structure(pdf_content)
        
        assert len(extracted.headings) == 1
        assert extracted.headings[0].level == HeadingLevel.H1
        assert extracted.headings[0].text == "Main Title"
    
    def test_heading_extraction_with_special_characters(self):
        """Test heading extraction with special characters."""
        md_content = b"# Security & Compliance\n## GDPR/HIPAA Requirements"
        extractor = MarkdownExtractor()
        
        extracted = extractor.extract_structure(md_content)
        
        assert len(extracted.headings) == 2
        assert "Security & Compliance" in extracted.headings[0].text
        assert "GDPR/HIPAA" in extracted.headings[1].text


# ============================================================================
# TESTS: Table Extraction (AC-PHASE49-S2-003)
# ============================================================================

class TestTableExtraction:
    """Test extraction of tables as structured data."""
    
    def test_extract_table_from_excel(self):
        """Test extracting table from Excel document."""
        excel_content = b"EXCEL_SPREADSHEET:Domain|Owner|Status\nSecurity|Team A|Active\nCompliance|Team B|Active"
        extractor = ExcelExtractor()
        
        extracted = extractor.extract_structure(excel_content)
        
        assert len(extracted.tables) == 1
        table = extracted.tables[0]
        
        assert table.headers == ["Domain", "Owner", "Status"]
        assert table.row_count() == 2
        assert table.column_count() == 3
    
    def test_table_row_access(self):
        """Test accessing table rows."""
        excel_content = b"EXCEL_SPREADSHEET:Name|Type\nEncryption|Security\nLogging|Observability"
        extractor = ExcelExtractor()
        
        extracted = extractor.extract_structure(excel_content)
        
        table = extracted.tables[0]
        assert table.rows[0] == ["Encryption", "Security"]
        assert table.rows[1] == ["Logging", "Observability"]
    
    def test_empty_table_not_extracted(self):
        """Test empty spreadsheet doesn't create tables."""
        excel_content = b"EXCEL_SPREADSHEET:"
        extractor = ExcelExtractor()
        
        extracted = extractor.extract_structure(excel_content)
        
        assert len(extracted.tables) == 0


# ============================================================================
# TESTS: Document Format Metadata
# ============================================================================

class TestMetadataExtraction:
    """Test metadata extraction from documents."""
    
    def test_format_metadata_recorded(self):
        """Test document format is recorded."""
        extractors = [
            (WordExtractor(), b"WORD_DOCUMENT:Content", "docx"),
            (ExcelExtractor(), b"EXCEL_SPREADSHEET:Content", "xlsx"),
            (PDFExtractor(), b"PDF_DOCUMENT:Content", "pdf"),
            (MarkdownExtractor(), b"# Content", "markdown"),
            (PowerPointExtractor(), b"POWERPOINT_DOCUMENT:Content", "pptx"),
        ]
        
        for extractor, content, expected_format in extractors:
            extracted = extractor.extract_structure(content)
            assert extracted.metadata["format"] == expected_format
    
    def test_page_count_metadata_pdf(self):
        """Test PDF page count metadata."""
        pdf_content = b"PDF_DOCUMENT:Page 1"
        extractor = PDFExtractor()
        
        extracted = extractor.extract_structure(pdf_content)
        
        assert "page_count" in extracted.metadata
        assert extracted.metadata["page_count"] >= 1
    
    def test_slide_count_metadata_ppt(self):
        """Test PowerPoint slide count metadata."""
        ppt_content = b"POWERPOINT_DOCUMENT:SLIDE:Title\nContent SLIDE:Slide 2"
        extractor = PowerPointExtractor()
        
        extracted = extractor.extract_structure(ppt_content)
        
        assert "slide_count" in extracted.metadata


# ============================================================================
# TESTS: Link Extraction
# ============================================================================

class TestLinkExtraction:
    """Test extraction of links from documents."""
    
    def test_extract_links_from_markdown(self):
        """Test extracting links from Markdown document."""
        md_content = b"# Documentation\n\nSee [policy](https://example.com/policy) for details.\n\n[compliance](https://example.com/compliance)"
        extractor = MarkdownExtractor()
        
        extracted = extractor.extract_structure(md_content)
        
        assert len(extracted.links) >= 1
        # Check at least one link exists
        link_texts = [link.get("text") for link in extracted.links if link.get("text")]
        assert any("policy" in t.lower() for t in link_texts)


# ============================================================================
# TESTS: Paragraph Extraction
# ============================================================================

class TestParagraphExtraction:
    """Test extraction of paragraphs from documents."""
    
    def test_extract_paragraphs_from_word(self):
        """Test extracting paragraphs from Word document."""
        word_content = b"WORD_DOCUMENT:# Title\nFirst paragraph content.\nSecond paragraph here."
        extractor = WordExtractor()
        
        extracted = extractor.extract_structure(word_content)
        
        assert len(extracted.paragraphs) >= 1
        assert any("paragraph" in p.lower() for p in extracted.paragraphs)
    
    def test_extract_paragraphs_from_markdown(self):
        """Test extracting paragraphs from Markdown document."""
        md_content = b"# Title\n\nIntroduction paragraph.\n\nSecond paragraph here."
        extractor = MarkdownExtractor()
        
        extracted = extractor.extract_structure(md_content)
        
        assert len(extracted.paragraphs) >= 1


# ============================================================================
# TESTS: Extraction Engine Consistency
# ============================================================================

class TestExtractionConsistency:
    """Test consistency across different extractors."""
    
    def test_all_extractors_return_same_type(self):
        """Test all extractors return ExtractedContent."""
        extractors = [
            (WordExtractor(), b"WORD_DOCUMENT:Content"),
            (ExcelExtractor(), b"EXCEL_SPREADSHEET:Content"),
            (PDFExtractor(), b"PDF_DOCUMENT:Content"),
            (MarkdownExtractor(), b"# Content"),
            (PowerPointExtractor(), b"POWERPOINT_DOCUMENT:Content"),
        ]
        
        for extractor, content in extractors:
            result = extractor.extract_structure(content)
            assert isinstance(result, ExtractedContent)
            assert isinstance(result.plain_text, str)
            assert isinstance(result.headings, list)
            assert isinstance(result.tables, list)
            assert isinstance(result.paragraphs, list)
