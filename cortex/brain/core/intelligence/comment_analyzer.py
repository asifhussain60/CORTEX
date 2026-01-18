# © 2025-2026 Asif Hussain. All rights reserved.
# AC-ID: IR-001-03 - Comment Analyzer
"""
Code Comment Intelligence - Comment Analyzer.

PHASE-07: Holistic Intent Router Intelligence
AC-ID: IR-001-03 - Code Comment Intelligence

Main analyzer for extracting and classifying code comments,
docstrings, and technical debt markers.
"""

import ast
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# =============================================================================
# DATA CLASSES
# =============================================================================


class DocstringStyle(Enum):
    """Docstring format styles."""
    GOOGLE = "google"
    NUMPY = "numpy"
    SPHINX = "sphinx"
    UNKNOWN = "unknown"


@dataclass
class ArgInfo:
    """Information about a function argument in a docstring."""
    name: str
    type_hint: Optional[str] = None
    description: str = ""


@dataclass
class RaisesInfo:
    """Information about a raised exception in a docstring."""
    exception: str
    description: str = ""


@dataclass
class ParsedDocstring:
    """Parsed docstring information."""
    raw: str
    style: str  # google, numpy, sphinx, unknown
    summary: str
    description: str
    function_name: str
    line_number: int
    args: List[ArgInfo] = field(default_factory=list)
    returns: Optional[str] = None
    raises: List[RaisesInfo] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    notes: Optional[str] = None
    see_also: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "raw": self.raw,
            "style": self.style,
            "summary": self.summary,
            "description": self.description,
            "function_name": self.function_name,
            "line_number": self.line_number,
            "args": [{"name": a.name, "type": a.type_hint, "description": a.description} for a in self.args],
            "returns": self.returns,
            "raises": [{"exception": r.exception, "description": r.description} for r in self.raises],
            "examples": self.examples,
            "notes": self.notes,
            "see_also": self.see_also,
        }


@dataclass
class InlineComment:
    """An inline comment in the source code."""
    text: str
    line_number: int
    category: str = "GENERAL"  # GENERAL, IMPORTANT, EXPLANATION, etc.
    is_trailing: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "text": self.text,
            "line_number": self.line_number,
            "category": self.category,
            "is_trailing": self.is_trailing,
        }


@dataclass
class TechDebtItem:
    """A technical debt marker (TODO, FIXME, HACK, etc.)."""
    marker: str  # TODO, FIXME, HACK, XXX, WARNING, NOTE
    text: str
    line_number: int
    assignee: Optional[str] = None
    priority: Optional[str] = None
    issue_ref: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "marker": self.marker,
            "text": self.text,
            "line_number": self.line_number,
            "assignee": self.assignee,
            "priority": self.priority,
            "issue_ref": self.issue_ref,
        }


@dataclass
class QualityIssue:
    """A comment quality issue."""
    type: str  # POTENTIAL_MISMATCH, STALE, MISSING, etc.
    message: str
    line_number: int
    severity: str = "WARNING"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "type": self.type,
            "message": self.message,
            "line_number": self.line_number,
            "severity": self.severity,
        }


@dataclass
class SearchMatch:
    """A search match in the comment index."""
    text: str
    line_number: int
    score: float
    context: str


class CommentIndex:
    """Searchable index of comments."""
    
    def __init__(self, items: List[Tuple[str, int, str]]):
        """Initialize with items (text, line_number, context)."""
        self._items = items
    
    def search(self, query: str) -> List[SearchMatch]:
        """Search for matches containing query."""
        query_lower = query.lower()
        matches = []
        
        for text, line_number, context in self._items:
            if query_lower in text.lower():
                # Simple scoring based on query position
                score = 1.0 - (text.lower().find(query_lower) / len(text))
                matches.append(SearchMatch(
                    text=text,
                    line_number=line_number,
                    score=score,
                    context=context,
                ))
        
        return sorted(matches, key=lambda m: m.score, reverse=True)


@dataclass
class CommentAnalysisResult:
    """Result of comment analysis."""
    docstrings: List[ParsedDocstring] = field(default_factory=list)
    inline_comments: List[InlineComment] = field(default_factory=list)
    tech_debt: List[TechDebtItem] = field(default_factory=list)
    quality_issues: List[QualityIssue] = field(default_factory=list)
    
    def build_index(self) -> CommentIndex:
        """Build searchable index from analysis results."""
        items: List[Tuple[str, int, str]] = []
        
        # Add docstrings
        for doc in self.docstrings:
            items.append((doc.raw, doc.line_number, f"docstring:{doc.function_name}"))
        
        # Add inline comments
        for comment in self.inline_comments:
            items.append((comment.text, comment.line_number, "inline"))
        
        # Add tech debt
        for debt in self.tech_debt:
            items.append((debt.text, debt.line_number, f"tech_debt:{debt.marker}"))
        
        return CommentIndex(items)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "docstrings": [d.to_dict() for d in self.docstrings],
            "inline_comments": [c.to_dict() for c in self.inline_comments],
            "tech_debt": [t.to_dict() for t in self.tech_debt],
            "quality_issues": [q.to_dict() for q in self.quality_issues],
        }


# =============================================================================
# COMMENT ANALYZER
# =============================================================================


class CommentAnalyzer:
    """Analyzer for code comments, docstrings, and tech debt markers."""
    
    # Tech debt marker patterns
    TECH_DEBT_MARKERS = {
        "TODO": r"#\s*TODO\s*(?:\(([^)]+)\))?\s*:?\s*(.*)",
        "FIXME": r"#\s*FIXME\s*(?:\(([^)]+)\))?\s*:?\s*(.*)",
        "HACK": r"#\s*HACK\s*(?:\(([^)]+)\))?\s*:?\s*(.*)",
        "XXX": r"#\s*XXX\s*(?:\(([^)]+)\))?\s*:?\s*(.*)",
        "WARNING": r"#\s*WARNING\s*(?:\(([^)]+)\))?\s*:?\s*(.*)",
        "NOTE": r"#\s*NOTE\s*(?:\(([^)]+)\))?\s*:?\s*(.*)",
    }
    
    # Issue reference pattern
    ISSUE_REF_PATTERN = r"#(\d+)"
    
    # Priority pattern
    PRIORITY_PATTERN = r"Priority:\s*(\w+)"
    
    def __init__(self):
        """Initialize the comment analyzer."""
        pass
    
    def analyze_file(self, file_path: Path) -> CommentAnalysisResult:
        """Analyze comments in a file.
        
        Args:
            file_path: Path to the Python file to analyze.
            
        Returns:
            CommentAnalysisResult containing all extracted comment data.
        """
        content = file_path.read_text(encoding="utf-8")
        return self.analyze_string(content)
    
    def analyze_string(self, source: str) -> CommentAnalysisResult:
        """Analyze comments in source code string.
        
        Args:
            source: Python source code as string.
            
        Returns:
            CommentAnalysisResult containing all extracted comment data.
        """
        result = CommentAnalysisResult()
        
        # Parse AST for docstrings
        try:
            tree = ast.parse(source)
            result.docstrings = self._extract_docstrings(tree, source)
        except SyntaxError:
            pass
        
        # Extract inline comments
        result.inline_comments = self._extract_inline_comments(source)
        
        # Extract tech debt markers
        result.tech_debt = self._extract_tech_debt(source)
        
        # Check for quality issues
        result.quality_issues = self._analyze_quality(tree if 'tree' in dir() else None, source, result)
        
        return result
    
    def _extract_docstrings(
        self, tree: ast.AST, source: str
    ) -> List[ParsedDocstring]:
        """Extract and parse docstrings from AST.
        
        Args:
            tree: Parsed AST.
            source: Original source code.
            
        Returns:
            List of parsed docstrings.
        """
        docstrings = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
                docstring = ast.get_docstring(node)
                if docstring:
                    # Determine name
                    if isinstance(node, ast.Module):
                        name = "__module__"
                    else:
                        name = node.name
                    
                    # Get line number
                    line_number = getattr(node, 'lineno', 1)
                    
                    # Parse the docstring
                    parsed = self._parse_docstring(docstring, name, line_number)
                    docstrings.append(parsed)
        
        return docstrings
    
    def _parse_docstring(
        self, docstring: str, function_name: str, line_number: int
    ) -> ParsedDocstring:
        """Parse a docstring and extract structured information.
        
        Args:
            docstring: Raw docstring text.
            function_name: Name of the function/class.
            line_number: Line number of the definition.
            
        Returns:
            ParsedDocstring with extracted information.
        """
        # Detect style
        style = self._detect_docstring_style(docstring)
        
        # Extract summary (first line)
        lines = docstring.strip().split('\n')
        summary = lines[0] if lines else ""
        
        # Parse based on style
        if style == "google":
            return self._parse_google_docstring(docstring, function_name, line_number, summary)
        elif style == "numpy":
            return self._parse_numpy_docstring(docstring, function_name, line_number, summary)
        elif style == "sphinx":
            return self._parse_sphinx_docstring(docstring, function_name, line_number, summary)
        else:
            return ParsedDocstring(
                raw=docstring,
                style=style,
                summary=summary,
                description=docstring,
                function_name=function_name,
                line_number=line_number,
            )
    
    def _detect_docstring_style(self, docstring: str) -> str:
        """Detect the docstring style.
        
        Args:
            docstring: Raw docstring text.
            
        Returns:
            Style name: 'google', 'numpy', 'sphinx', or 'unknown'.
        """
        # Check for NumPy style (has underlined sections)
        if re.search(r'\n\s*Parameters\s*\n\s*-+', docstring):
            return "numpy"
        
        # Check for Sphinx style (:param, :type, :returns)
        if re.search(r':param\s+\w+:', docstring) or re.search(r':type\s+\w+:', docstring):
            return "sphinx"
        
        # Check for Google style (Args:, Returns:, Raises:)
        if re.search(r'\n\s*Args:\s*\n', docstring) or re.search(r'\n\s*Returns:\s*\n', docstring):
            return "google"
        
        return "unknown"
    
    def _parse_google_docstring(
        self, docstring: str, function_name: str, line_number: int, summary: str
    ) -> ParsedDocstring:
        """Parse Google-style docstring.
        
        Args:
            docstring: Raw docstring text.
            function_name: Name of the function.
            line_number: Line number.
            summary: First line summary.
            
        Returns:
            ParsedDocstring with extracted information.
        """
        args = []
        raises = []
        returns = None
        examples = []
        notes = None
        see_also = []
        
        # Extract Args section
        args_match = re.search(r'\n\s*Args:\s*\n(.*?)(?=\n\s*(?:Returns|Raises|Example|Note|See Also):|$)', 
                               docstring, re.DOTALL | re.IGNORECASE)
        if args_match:
            args_text = args_match.group(1)
            # Parse individual args
            for match in re.finditer(r'(\w+):\s*(.+?)(?=\n\s*\w+:|$)', args_text, re.DOTALL):
                arg_name = match.group(1)
                arg_desc = match.group(2).strip()
                args.append(ArgInfo(name=arg_name, description=arg_desc))
        
        # Extract Returns section
        returns_match = re.search(r'\n\s*Returns:\s*\n\s*(.*?)(?=\n\s*(?:Raises|Example|Note|See Also):|$)',
                                   docstring, re.DOTALL | re.IGNORECASE)
        if returns_match:
            returns = returns_match.group(1).strip()
        
        # Extract Raises section
        raises_match = re.search(r'\n\s*Raises:\s*\n(.*?)(?=\n\s*(?:Example|Note|See Also):|$)',
                                  docstring, re.DOTALL | re.IGNORECASE)
        if raises_match:
            raises_text = raises_match.group(1)
            for match in re.finditer(r'(\w+(?:Error|Exception)?)\s*:\s*(.+?)(?=\n\s*\w+:|$)', 
                                     raises_text, re.DOTALL):
                exc_name = match.group(1)
                exc_desc = match.group(2).strip()
                raises.append(RaisesInfo(exception=exc_name, description=exc_desc))
        
        # Extract Note section
        note_match = re.search(r'\n\s*Note:\s*\n\s*(.*?)(?=\n\s*(?:See Also):|$)',
                                docstring, re.DOTALL | re.IGNORECASE)
        if note_match:
            notes = note_match.group(1).strip()
        
        # Extract See Also section
        see_also_match = re.search(r'\n\s*See Also:\s*\n\s*(.*?)$',
                                    docstring, re.DOTALL | re.IGNORECASE)
        if see_also_match:
            see_also = [s.strip() for s in see_also_match.group(1).strip().split('\n') if s.strip()]
        
        return ParsedDocstring(
            raw=docstring,
            style="google",
            summary=summary,
            description=docstring,
            function_name=function_name,
            line_number=line_number,
            args=args,
            returns=returns,
            raises=raises,
            examples=examples,
            notes=notes,
            see_also=see_also,
        )
    
    def _parse_numpy_docstring(
        self, docstring: str, function_name: str, line_number: int, summary: str
    ) -> ParsedDocstring:
        """Parse NumPy-style docstring.
        
        Args:
            docstring: Raw docstring text.
            function_name: Name of the function.
            line_number: Line number.
            summary: First line summary.
            
        Returns:
            ParsedDocstring with extracted information.
        """
        args = []
        raises = []
        returns = None
        notes = None
        
        # Extract Parameters section
        params_match = re.search(r'\n\s*Parameters\s*\n\s*-+\s*\n(.*?)(?=\n\s*\w+\s*\n\s*-+|$)',
                                  docstring, re.DOTALL)
        if params_match:
            params_text = params_match.group(1)
            # Parse individual parameters
            for match in re.finditer(r'(\w+)\s*:\s*([^\n]+)\n\s*(.*?)(?=\n\s*\w+\s*:|$)', 
                                     params_text, re.DOTALL):
                param_name = match.group(1)
                param_type = match.group(2).strip()
                param_desc = match.group(3).strip()
                args.append(ArgInfo(name=param_name, type_hint=param_type, description=param_desc))
        
        # Extract Returns section
        returns_match = re.search(r'\n\s*Returns\s*\n\s*-+\s*\n(.*?)(?=\n\s*\w+\s*\n\s*-+|$)',
                                   docstring, re.DOTALL)
        if returns_match:
            returns = returns_match.group(1).strip()
        
        # Extract Raises section
        raises_match = re.search(r'\n\s*Raises\s*\n\s*-+\s*\n(.*?)(?=\n\s*\w+\s*\n\s*-+|$)',
                                  docstring, re.DOTALL)
        if raises_match:
            raises_text = raises_match.group(1)
            for match in re.finditer(r'(\w+(?:Error|Exception)?)\s*\n\s*(.*?)(?=\n\s*\w+\s*\n|$)', 
                                     raises_text, re.DOTALL):
                exc_name = match.group(1)
                exc_desc = match.group(2).strip()
                raises.append(RaisesInfo(exception=exc_name, description=exc_desc))
        
        # Extract Notes section
        notes_match = re.search(r'\n\s*Notes\s*\n\s*-+\s*\n(.*?)(?=\n\s*\w+\s*\n\s*-+|$)',
                                 docstring, re.DOTALL)
        if notes_match:
            notes = notes_match.group(1).strip()
        
        return ParsedDocstring(
            raw=docstring,
            style="numpy",
            summary=summary,
            description=docstring,
            function_name=function_name,
            line_number=line_number,
            args=args,
            returns=returns,
            raises=raises,
            notes=notes,
        )
    
    def _parse_sphinx_docstring(
        self, docstring: str, function_name: str, line_number: int, summary: str
    ) -> ParsedDocstring:
        """Parse Sphinx-style docstring.
        
        Args:
            docstring: Raw docstring text.
            function_name: Name of the function.
            line_number: Line number.
            summary: First line summary.
            
        Returns:
            ParsedDocstring with extracted information.
        """
        args = []
        raises = []
        returns = None
        
        # Extract :param and :type pairs
        param_types = {}
        for match in re.finditer(r':type\s+(\w+):\s*(.+)', docstring):
            param_types[match.group(1)] = match.group(2).strip()
        
        for match in re.finditer(r':param\s+(\w+):\s*(.+)', docstring):
            param_name = match.group(1)
            param_desc = match.group(2).strip()
            param_type = param_types.get(param_name)
            args.append(ArgInfo(name=param_name, type_hint=param_type, description=param_desc))
        
        # Extract :returns
        returns_match = re.search(r':returns:\s*(.+)', docstring)
        if returns_match:
            returns = returns_match.group(1).strip()
        
        # Extract :raises
        for match in re.finditer(r':raises\s+(\w+(?:Error|Exception)?):\s*(.+)', docstring):
            exc_name = match.group(1)
            exc_desc = match.group(2).strip()
            raises.append(RaisesInfo(exception=exc_name, description=exc_desc))
        
        return ParsedDocstring(
            raw=docstring,
            style="sphinx",
            summary=summary,
            description=docstring,
            function_name=function_name,
            line_number=line_number,
            args=args,
            returns=returns,
            raises=raises,
        )
    
    def _extract_inline_comments(self, source: str) -> List[InlineComment]:
        """Extract inline comments from source code.
        
        Args:
            source: Python source code.
            
        Returns:
            List of InlineComment objects.
        """
        comments = []
        lines = source.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Skip docstrings (lines starting/containing triple quotes)
            if '"""' in line or "'''" in line:
                continue
            
            # Check for comment
            comment_match = re.search(r'#(.+)$', line)
            if comment_match:
                comment_text = comment_match.group(1).strip()
                
                # Skip if it's a shebang or encoding declaration
                if i == 1 and (comment_text.startswith('!') or 'coding' in comment_text):
                    continue
                
                # Determine if trailing (has code before #)
                code_before = line[:comment_match.start()].strip()
                is_trailing = len(code_before) > 0
                
                # Classify comment
                category = self._classify_comment(comment_text)
                
                comments.append(InlineComment(
                    text=comment_text,
                    line_number=i,
                    category=category,
                    is_trailing=is_trailing,
                ))
        
        return comments
    
    def _classify_comment(self, comment_text: str) -> str:
        """Classify a comment into categories.
        
        Args:
            comment_text: The comment text (without #).
            
        Returns:
            Category string.
        """
        upper_text = comment_text.upper()
        
        if "IMPORTANT" in upper_text:
            return "IMPORTANT"
        elif any(m in upper_text for m in ["TODO", "FIXME", "HACK", "XXX", "WARNING"]):
            return "TECH_DEBT"
        elif "NOTE" in upper_text:
            return "NOTE"
        else:
            return "GENERAL"
    
    def _extract_tech_debt(self, source: str) -> List[TechDebtItem]:
        """Extract tech debt markers (TODO, FIXME, etc.) from source.
        
        Args:
            source: Python source code.
            
        Returns:
            List of TechDebtItem objects.
        """
        tech_debt = []
        lines = source.split('\n')
        
        for i, line in enumerate(lines, 1):
            for marker, pattern in self.TECH_DEBT_MARKERS.items():
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    assignee = match.group(1) if match.lastindex >= 1 else None
                    text = match.group(2) if match.lastindex >= 2 else ""
                    text = text.strip()
                    
                    # Check for issue reference
                    issue_match = re.search(self.ISSUE_REF_PATTERN, line)
                    issue_ref = issue_match.group(1) if issue_match else None
                    
                    # Check for priority (might be on next line too)
                    priority_match = re.search(self.PRIORITY_PATTERN, source[source.find(line):], re.IGNORECASE)
                    priority = priority_match.group(1) if priority_match else None
                    
                    tech_debt.append(TechDebtItem(
                        marker=marker,
                        text=text,
                        line_number=i,
                        assignee=assignee,
                        priority=priority,
                        issue_ref=issue_ref,
                    ))
                    break  # One marker per line
        
        return tech_debt
    
    def _analyze_quality(
        self, tree: Optional[ast.AST], source: str, result: CommentAnalysisResult
    ) -> List[QualityIssue]:
        """Analyze comment quality and detect issues.
        
        Args:
            tree: Parsed AST (may be None).
            source: Source code.
            result: Current analysis result.
            
        Returns:
            List of QualityIssue objects.
        """
        issues = []
        
        if tree is None:
            return issues
        
        # Check for docstring-code mismatches
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                docstring = ast.get_docstring(node)
                if docstring:
                    # Check for common mismatches
                    docstring_lower = docstring.lower()
                    func_name_lower = node.name.lower()
                    
                    # Detect "add" vs "subtract" type mismatches
                    mismatch_pairs = [
                        ("add", "subtract"),
                        ("create", "delete"),
                        ("get", "set"),
                        ("read", "write"),
                        ("open", "close"),
                        ("start", "stop"),
                    ]
                    
                    for word1, word2 in mismatch_pairs:
                        if (word1 in func_name_lower and word2 in docstring_lower) or \
                           (word2 in func_name_lower and word1 in docstring_lower):
                            issues.append(QualityIssue(
                                type="POTENTIAL_MISMATCH",
                                message=f"Docstring may not match function '{node.name}'",
                                line_number=node.lineno,
                                severity="WARNING",
                            ))
                            break
        
        return issues


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    "CommentAnalyzer",
    "CommentAnalysisResult",
    "ParsedDocstring",
    "InlineComment",
    "TechDebtItem",
    "QualityIssue",
    "CommentIndex",
    "ArgInfo",
    "RaisesInfo",
]
