#!/usr/bin/env python3
"""
Document Converter Utility

Universal document converter for Word (.docx, .doc) and PDF files to Markdown format.
Used across CORTEX for policy validation, ADO work items, planning documents, 
conversation imports, feedback attachments, and any document reading scenario.

Converter Priority:
1. pandoc (best quality, external tool)
2. pdftotext + python-docx (fallback, mixed approach)
3. PyPDF2 (pure Python, last resort)

Features:
- Hash-based caching (MD5 + mtime)
- 60-second timeout protection
- Platform-specific installation guidance
- Graceful fallback when converters missing

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import hashlib
import logging
import subprocess
import shutil
from pathlib import Path
from typing import Optional, Tuple
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ConversionResult:
    """Result of document conversion."""
    success: bool
    markdown_path: Optional[Path]
    original_path: Path
    converter_used: str  # pandoc, python-docx, pypdf2, pdftotext
    conversion_time: float
    error_message: Optional[str] = None
    cached: bool = False


class DocumentConverter:
    """Converts documents to Markdown format."""
    
    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Initialize DocumentConverter
        
        Args:
            cache_dir: Directory for caching converted files (default: .cache/conversions)
        """
        self.cache_dir = cache_dir or Path.cwd() / ".cache" / "conversions"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Check available converters
        self.has_pandoc = self._check_pandoc()
        self.has_pdftotext = self._check_pdftotext()
        self.has_python_docx = self._check_python_docx()
        self.has_pypdf2 = self._check_pypdf2()
        
        logger.info(f"Document Converter initialized:")
        logger.info(f"  pandoc: {'✅' if self.has_pandoc else '❌'}")
        logger.info(f"  pdftotext: {'✅' if self.has_pdftotext else '❌'}")
        logger.info(f"  python-docx: {'✅' if self.has_python_docx else '❌'}")
        logger.info(f"  PyPDF2: {'✅' if self.has_pypdf2 else '❌'}")
    
    def convert_to_markdown(self, file_path: Path) -> ConversionResult:
        """
        Convert document to Markdown
        
        Args:
            file_path: Path to Word or PDF document
        
        Returns:
            ConversionResult with success status and converted file path
        """
        start_time = datetime.now()
        file_path = Path(file_path)
        
        if not file_path.exists():
            return ConversionResult(
                success=False,
                markdown_path=None,
                original_path=file_path,
                converter_used="none",
                conversion_time=0.0,
                error_message=f"File not found: {file_path}"
            )
        
        # Check cache first
        cached_path = self._get_cached_path(file_path)
        if self._is_cache_valid(file_path, cached_path):
            elapsed = (datetime.now() - start_time).total_seconds()
            logger.info(f"✅ Using cached conversion: {cached_path}")
            return ConversionResult(
                success=True,
                markdown_path=cached_path,
                original_path=file_path,
                converter_used="cache",
                conversion_time=elapsed,
                cached=True
            )
        
        # Detect format and convert
        extension = file_path.suffix.lower()
        
        if extension in ['.docx', '.doc']:
            result = self._convert_word_to_markdown(file_path)
        elif extension == '.pdf':
            result = self._convert_pdf_to_markdown(file_path)
        else:
            return ConversionResult(
                success=False,
                markdown_path=None,
                original_path=file_path,
                converter_used="none",
                conversion_time=0.0,
                error_message=f"Unsupported format: {extension}"
            )
        
        elapsed = (datetime.now() - start_time).total_seconds()
        result.conversion_time = elapsed
        
        return result
    
    def _convert_word_to_markdown(self, file_path: Path) -> ConversionResult:
        """Convert Word document to Markdown."""
        # Try pandoc first (best quality)
        if self.has_pandoc:
            result = self._convert_with_pandoc(file_path)
            if result.success:
                return result
        
        # Fallback to python-docx
        if self.has_python_docx:
            result = self._convert_with_python_docx(file_path)
            if result.success:
                return result
        
        return ConversionResult(
            success=False,
            markdown_path=None,
            original_path=file_path,
            converter_used="none",
            conversion_time=0.0,
            error_message="No Word converter available. Install pandoc or python-docx."
        )
    
    def _convert_pdf_to_markdown(self, file_path: Path) -> ConversionResult:
        """Convert PDF document to Markdown."""
        # Try pdftotext first (fastest, best text extraction)
        if self.has_pdftotext:
            result = self._convert_with_pdftotext(file_path)
            if result.success:
                return result
        
        # Try pandoc (handles complex PDFs)
        if self.has_pandoc:
            result = self._convert_with_pandoc(file_path)
            if result.success:
                return result
        
        # Fallback to PyPDF2
        if self.has_pypdf2:
            result = self._convert_with_pypdf2(file_path)
            if result.success:
                return result
        
        return ConversionResult(
            success=False,
            markdown_path=None,
            original_path=file_path,
            converter_used="none",
            conversion_time=0.0,
            error_message="No PDF converter available. Install pdftotext, pandoc, or PyPDF2."
        )
    
    def _convert_with_pandoc(self, file_path: Path) -> ConversionResult:
        """Convert using pandoc."""
        try:
            output_path = self._get_cached_path(file_path)
            
            # Run pandoc
            cmd = [
                "pandoc",
                str(file_path),
                "-f", self._get_pandoc_format(file_path),
                "-t", "markdown",
                "-o", str(output_path),
                "--wrap=none",  # Don't wrap long lines
                "--extract-media", str(self.cache_dir / "media")  # Extract images
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0 and output_path.exists():
                logger.info(f"✅ Converted with pandoc: {output_path}")
                return ConversionResult(
                    success=True,
                    markdown_path=output_path,
                    original_path=file_path,
                    converter_used="pandoc",
                    conversion_time=0.0
                )
            else:
                error_msg = result.stderr or "Pandoc conversion failed"
                logger.warning(f"Pandoc failed: {error_msg}")
                return ConversionResult(
                    success=False,
                    markdown_path=None,
                    original_path=file_path,
                    converter_used="pandoc",
                    conversion_time=0.0,
                    error_message=error_msg
                )
        
        except subprocess.TimeoutExpired:
            return ConversionResult(
                success=False,
                markdown_path=None,
                original_path=file_path,
                converter_used="pandoc",
                conversion_time=0.0,
                error_message="Pandoc conversion timed out (>60s)"
            )
        except Exception as e:
            logger.error(f"Pandoc error: {e}")
            return ConversionResult(
                success=False,
                markdown_path=None,
                original_path=file_path,
                converter_used="pandoc",
                conversion_time=0.0,
                error_message=str(e)
            )
    
    def _convert_with_python_docx(self, file_path: Path) -> ConversionResult:
        """Convert Word document using python-docx."""
        try:
            from docx import Document
            
            doc = Document(file_path)
            output_path = self._get_cached_path(file_path)
            
            # Extract text with basic formatting
            markdown_lines = []
            for para in doc.paragraphs:
                text = para.text.strip()
                if not text:
                    continue
                
                # Detect headings by style
                if para.style.name.startswith('Heading'):
                    level = para.style.name.replace('Heading', '').strip()
                    try:
                        level_num = int(level)
                        markdown_lines.append(f"{'#' * level_num} {text}")
                    except:
                        markdown_lines.append(f"## {text}")
                else:
                    markdown_lines.append(text)
                
                markdown_lines.append("")  # Blank line
            
            # Write to file
            output_path.write_text('\n'.join(markdown_lines), encoding='utf-8')
            
            logger.info(f"✅ Converted with python-docx: {output_path}")
            return ConversionResult(
                success=True,
                markdown_path=output_path,
                original_path=file_path,
                converter_used="python-docx",
                conversion_time=0.0
            )
        
        except ImportError:
            return ConversionResult(
                success=False,
                markdown_path=None,
                original_path=file_path,
                converter_used="python-docx",
                conversion_time=0.0,
                error_message="python-docx not installed"
            )
        except Exception as e:
            logger.error(f"python-docx error: {e}")
            return ConversionResult(
                success=False,
                markdown_path=None,
                original_path=file_path,
                converter_used="python-docx",
                conversion_time=0.0,
                error_message=str(e)
            )
    
    def _convert_with_pdftotext(self, file_path: Path) -> ConversionResult:
        """Convert PDF using pdftotext."""
        try:
            output_path = self._get_cached_path(file_path)
            txt_path = output_path.with_suffix('.txt')
            
            # Run pdftotext
            cmd = ["pdftotext", "-layout", str(file_path), str(txt_path)]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0 and txt_path.exists():
                # Convert plain text to Markdown (basic)
                text = txt_path.read_text(encoding='utf-8', errors='ignore')
                markdown = self._text_to_markdown(text)
                output_path.write_text(markdown, encoding='utf-8')
                txt_path.unlink()  # Remove temp txt file
                
                logger.info(f"✅ Converted with pdftotext: {output_path}")
                return ConversionResult(
                    success=True,
                    markdown_path=output_path,
                    original_path=file_path,
                    converter_used="pdftotext",
                    conversion_time=0.0
                )
            else:
                error_msg = result.stderr or "pdftotext conversion failed"
                logger.warning(f"pdftotext failed: {error_msg}")
                return ConversionResult(
                    success=False,
                    markdown_path=None,
                    original_path=file_path,
                    converter_used="pdftotext",
                    conversion_time=0.0,
                    error_message=error_msg
                )
        
        except subprocess.TimeoutExpired:
            return ConversionResult(
                success=False,
                markdown_path=None,
                original_path=file_path,
                converter_used="pdftotext",
                conversion_time=0.0,
                error_message="pdftotext conversion timed out (>60s)"
            )
        except Exception as e:
            logger.error(f"pdftotext error: {e}")
            return ConversionResult(
                success=False,
                markdown_path=None,
                original_path=file_path,
                converter_used="pdftotext",
                conversion_time=0.0,
                error_message=str(e)
            )
    
    def _convert_with_pypdf2(self, file_path: Path) -> ConversionResult:
        """Convert PDF using PyPDF2."""
        try:
            from PyPDF2 import PdfReader
            
            reader = PdfReader(file_path)
            output_path = self._get_cached_path(file_path)
            
            # Extract text from all pages
            text_lines = []
            for page_num, page in enumerate(reader.pages, 1):
                text = page.extract_text()
                if text.strip():
                    text_lines.append(f"## Page {page_num}\n\n{text}\n")
            
            markdown = '\n'.join(text_lines)
            output_path.write_text(markdown, encoding='utf-8')
            
            logger.info(f"✅ Converted with PyPDF2: {output_path}")
            return ConversionResult(
                success=True,
                markdown_path=output_path,
                original_path=file_path,
                converter_used="pypdf2",
                conversion_time=0.0
            )
        
        except ImportError:
            return ConversionResult(
                success=False,
                markdown_path=None,
                original_path=file_path,
                converter_used="pypdf2",
                conversion_time=0.0,
                error_message="PyPDF2 not installed"
            )
        except Exception as e:
            logger.error(f"PyPDF2 error: {e}")
            return ConversionResult(
                success=False,
                markdown_path=None,
                original_path=file_path,
                converter_used="pypdf2",
                conversion_time=0.0,
                error_message=str(e)
            )
    
    def _text_to_markdown(self, text: str) -> str:
        """Convert plain text to Markdown with basic formatting detection."""
        lines = text.split('\n')
        markdown_lines = []
        
        for line in lines:
            stripped = line.strip()
            
            # Detect headings (ALL CAPS lines or lines with specific patterns)
            if stripped and stripped.isupper() and len(stripped) > 5:
                markdown_lines.append(f"## {stripped.title()}")
            elif stripped:
                markdown_lines.append(stripped)
            else:
                markdown_lines.append("")
        
        return '\n'.join(markdown_lines)
    
    def _get_cached_path(self, file_path: Path) -> Path:
        """Get cached Markdown path for document."""
        # Use hash of file path + modification time for cache key
        file_stat = file_path.stat()
        cache_key = hashlib.md5(
            f"{file_path}_{file_stat.st_mtime}".encode()
        ).hexdigest()
        
        return self.cache_dir / f"{file_path.stem}_{cache_key}.md"
    
    def _is_cache_valid(self, file_path: Path, cached_path: Path) -> bool:
        """Check if cached conversion is still valid."""
        if not cached_path.exists():
            return False
        
        # Cache valid if original file hasn't been modified since conversion
        original_mtime = file_path.stat().st_mtime
        cached_mtime = cached_path.stat().st_mtime
        
        return cached_mtime > original_mtime
    
    def _get_pandoc_format(self, file_path: Path) -> str:
        """Get pandoc input format for file."""
        extension = file_path.suffix.lower()
        
        format_map = {
            '.docx': 'docx',
            '.doc': 'doc',
            '.pdf': 'pdf',
            '.html': 'html',
            '.htm': 'html',
            '.rtf': 'rtf',
            '.odt': 'odt'
        }
        
        return format_map.get(extension, 'docx')
    
    def _check_pandoc(self) -> bool:
        """Check if pandoc is installed."""
        return shutil.which("pandoc") is not None
    
    def _check_pdftotext(self) -> bool:
        """Check if pdftotext is installed."""
        return shutil.which("pdftotext") is not None
    
    def _check_python_docx(self) -> bool:
        """Check if python-docx is installed."""
        try:
            import docx
            return True
        except ImportError:
            return False
    
    def _check_pypdf2(self) -> bool:
        """Check if PyPDF2 is installed."""
        try:
            import PyPDF2
            return True
        except ImportError:
            return False
    
    def get_installation_guide(self) -> str:
        """Get installation instructions for missing converters."""
        missing = []
        
        if not self.has_pandoc:
            missing.append("pandoc")
        if not self.has_pdftotext:
            missing.append("pdftotext (poppler-utils)")
        if not self.has_python_docx:
            missing.append("python-docx")
        if not self.has_pypdf2:
            missing.append("PyPDF2")
        
        if not missing:
            return "✅ All converters installed!"
        
        guide = "⚠️  Missing document converters:\n\n"
        
        for tool in missing:
            if tool == "pandoc":
                guide += "**pandoc** (recommended):\n"
                guide += "  • Windows: Download from https://pandoc.org/installing.html\n"
                guide += "  • Mac: brew install pandoc\n"
                guide += "  • Linux: apt-get install pandoc\n\n"
            
            elif tool == "pdftotext (poppler-utils)":
                guide += "**pdftotext** (for PDF support):\n"
                guide += "  • Windows: Download poppler from https://github.com/oschwartz10612/poppler-windows/releases\n"
                guide += "  • Mac: brew install poppler\n"
                guide += "  • Linux: apt-get install poppler-utils\n\n"
            
            elif tool == "python-docx":
                guide += "**python-docx** (fallback for Word):\n"
                guide += "  • pip install python-docx\n\n"
            
            elif tool == "PyPDF2":
                guide += "**PyPDF2** (fallback for PDF):\n"
                guide += "  • pip install PyPDF2\n\n"
        
        return guide


def main():
    """CLI entry point for testing."""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="Convert documents to Markdown")
    parser.add_argument("file", type=Path, help="Document to convert (.docx or .pdf)")
    parser.add_argument("--cache-dir", type=Path, help="Cache directory")
    parser.add_argument("--show-guide", action="store_true", help="Show installation guide")
    
    args = parser.parse_args()
    
    converter = DocumentConverter(args.cache_dir)
    
    if args.show_guide:
        print(converter.get_installation_guide())
        return 0
    
    if not args.file.exists():
        print(f"❌ File not found: {args.file}")
        return 1
    
    print(f"Converting: {args.file}")
    result = converter.convert_to_markdown(args.file)
    
    if result.success:
        print(f"✅ Success!")
        print(f"   Converter: {result.converter_used}")
        print(f"   Output: {result.markdown_path}")
        print(f"   Time: {result.conversion_time:.2f}s")
        if result.cached:
            print(f"   (Used cached conversion)")
        return 0
    else:
        print(f"❌ Conversion failed: {result.error_message}")
        print(f"\n{converter.get_installation_guide()}")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
