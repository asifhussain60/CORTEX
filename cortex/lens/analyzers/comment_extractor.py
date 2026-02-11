"""
Comment Extractor for CORTEX.

Extracts comments and docstrings from Python code for LENS intelligence cycle.
Supports inline comments, block comments, and various docstring styles.

Authority: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)
"""

import ast
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class Comment:
    """
    Represents a code comment.

    Attributes:
        line_number: Line number of the comment
        content: Comment text (without # prefix)
        comment_type: Type of comment ('inline' or 'block')
    """
    line_number: int
    content: str
    comment_type: str  # 'inline' or 'block'


@dataclass
class DocstringInfo:
    """
    Information about a docstring.

    Attributes:
        target_name: Name of the function/class/module
        target_type: Type of target ('function', 'class', 'module')
        content: Docstring content
        line_number: Starting line number
        style: Docstring style ('google', 'numpy', 'sphinx', 'plain')
    """
    target_name: str
    target_type: str
    content: str
    line_number: int
    style: str = "plain"


@dataclass
class CommentExtractionResult:
    """
    Result of comment extraction.

    Attributes:
        success: Whether extraction succeeded
        comments: List of comments found
        docstrings: List of docstrings found
        error: Error message if extraction failed
        metadata: Additional metadata about extraction
    """
    success: bool
    comments: List[Comment] = field(default_factory=list)
    docstrings: List[DocstringInfo] = field(default_factory=list)
    error: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class CommentExtractor:
    """
    Extracts comments and docstrings from Python code.

    Extracts:
    - Inline comments (# at end of line)
    - Block comments (# at start of line)
    - Function/method docstrings
    - Class docstrings
    - Module docstrings
    - Detects docstring styles (Google, NumPy, Sphinx)

    Example:
        ```python
        extractor = CommentExtractor()

        # Extract from code string
        result = extractor.extract_comments(code)
        for comment in result.comments:
            print(f"Line {comment.line_number}: {comment.content}")

        # Extract from file
        result = extractor.extract_from_file(Path("module.py"))
        for docstring in result.docstrings:
            print(f"{docstring.target_name}: {docstring.style} style")
        ```
    """

    def extract_comments(self, code: str) -> CommentExtractionResult:
        """
        Extract comments and docstrings from Python code.

        Args:
            code: Python source code

        Returns:
            CommentExtractionResult with extracted information
        """
        comments = []
        docstrings = []

        # Extract comments from raw text
        lines = code.splitlines()
        for line_num, line in enumerate(lines, start=1):
            # Skip empty lines
            if not line.strip():
                continue

            # Check for comments
            comment_match = re.search(r'#\s*(.*)', line)
            if comment_match:
                comment_text = comment_match.group(1).strip()

                # Determine if inline or block comment
                before_comment = line[:comment_match.start()].strip()
                comment_type = "inline" if before_comment else "block"

                comments.append(
                    Comment(
                        line_number=line_num,
                        content=comment_text,
                        comment_type=comment_type,
                    )
                )

        # Extract docstrings using AST
        try:
            tree = ast.parse(code)

            # Module docstring
            module_docstring = ast.get_docstring(tree)
            if module_docstring:
                docstrings.append(
                    DocstringInfo(
                        target_name="<module>",
                        target_type="module",
                        content=module_docstring,
                        line_number=1,
                        style=self._detect_docstring_style(module_docstring),
                    )
                )

            # Function and class docstrings
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                    docstring = ast.get_docstring(node)
                    if docstring:
                        docstrings.append(
                            DocstringInfo(
                                target_name=node.name,
                                target_type="function",
                                content=docstring,
                                line_number=node.lineno,
                                style=self._detect_docstring_style(docstring),
                            )
                        )

                elif isinstance(node, ast.ClassDef):
                    docstring = ast.get_docstring(node)
                    if docstring:
                        docstrings.append(
                            DocstringInfo(
                                target_name=node.name,
                                target_type="class",
                                content=docstring,
                                line_number=node.lineno,
                                style=self._detect_docstring_style(docstring),
                            )
                        )

        except SyntaxError:
            # If syntax error, still return comments we extracted
            pass

        # Calculate metadata
        inline_count = len([c for c in comments if c.comment_type == "inline"])
        block_count = len([c for c in comments if c.comment_type == "block"])

        return CommentExtractionResult(
            success=True,
            comments=comments,
            docstrings=docstrings,
            metadata={
                "inline_count": inline_count,
                "block_count": block_count,
                "docstring_count": len(docstrings),
                "total_comments": len(comments),
            },
        )

    def extract_from_file(self, file_path: Path) -> CommentExtractionResult:
        """
        Extract comments and docstrings from a Python file.

        Args:
            file_path: Path to Python file

        Returns:
            CommentExtractionResult with extracted information
        """
        try:
            if not file_path.exists():
                return CommentExtractionResult(
                    success=False,
                    error=f"File not found: {file_path}",
                )

            code = file_path.read_text(encoding="utf-8")
            result = self.extract_comments(code)

            # Add file path to metadata
            if result.success:
                result.metadata["file_path"] = str(file_path)

            return result

        except Exception as e:
            return CommentExtractionResult(
                success=False,
                error=f"Failed to read file: {str(e)}",
            )

    def _detect_docstring_style(self, docstring: str) -> str:
        """
        Detect the style of a docstring.

        Args:
            docstring: Docstring text

        Returns:
            Style name: 'google', 'numpy', 'sphinx', or 'plain'
        """
        # Google style: Args:, Returns:, Raises:
        if re.search(r'\b(Args|Returns|Yields|Raises|Note|Example):\s*$', docstring, re.MULTILINE):
            return "google"

        # NumPy style: Parameters, Returns with underlines
        if re.search(r'\b(Parameters|Returns|Yields|Raises)\s*\n\s*-+', docstring):
            return "numpy"

        # Sphinx style: :param, :type, :return, :rtype
        if re.search(r':(param|type|return|rtype|raises):', docstring):
            return "sphinx"

        return "plain"
