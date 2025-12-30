"""
Incremental AST Context Builder

Purpose: Build AST context incrementally per-turn instead of once at session start.
Author: Asif Hussain
Created: 2025-12-30
Version: 1.0.0

Gap Addressed: GAP 3 - Static AST Context (One-Time Discovery)
- Previous: AST discovery runs once when session starts
- New: Incremental per-turn context building focused on conversation

Features:
- Per-turn incremental AST building
- Conversation-aware discovery (focuses on what user mentions)
- Caching with invalidation on file changes
- Progressive expansion of context
- Relevance scoring for discovered symbols
"""

import logging
import hashlib
import ast
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


# ============================================================================
# Discovery Types
# ============================================================================

class DiscoverySource(Enum):
    """Source of symbol discovery."""
    USER_MENTION = "user_mention"       # User explicitly mentioned symbol
    IMPORT = "import"                    # Imported by mentioned file
    DEPENDENCY = "dependency"            # Dependency of mentioned symbol
    RELATED = "related"                  # Related by naming/proximity
    CACHED = "cached"                    # Retrieved from cache


@dataclass
class SymbolContext:
    """Context information for a discovered symbol."""
    name: str
    symbol_type: str  # "class", "function", "variable", "module"
    file_path: str
    line_number: int
    signature: Optional[str] = None
    docstring: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    relevance_score: float = 0.0
    source: DiscoverySource = DiscoverySource.RELATED
    discovered_at: datetime = field(default_factory=datetime.now)


@dataclass
class IncrementalContext:
    """Context accumulated across conversation turns."""
    symbols: Dict[str, SymbolContext] = field(default_factory=dict)
    files_analyzed: Set[str] = field(default_factory=set)
    turn_count: int = 0
    last_updated: datetime = field(default_factory=datetime.now)


# ============================================================================
# Incremental AST Builder
# ============================================================================

class IncrementalASTBuilder:
    """
    Builds AST context incrementally based on conversation.
    
    Instead of analyzing entire codebase at session start, this builder:
    1. Extracts mentioned symbols from user message
    2. Discovers relevant context for those symbols
    3. Progressively expands context as conversation continues
    4. Caches results for efficiency
    
    Usage:
        builder = IncrementalASTBuilder(workspace_root="/path/to/project")
        
        # First turn
        context = builder.build_incremental_context(
            user_message="How does AuthService handle tokens?",
            turn_number=1
        )
        
        # Second turn - builds on previous context
        context = builder.build_incremental_context(
            user_message="What about the TokenValidator?",
            turn_number=2
        )
    """
    
    # Symbol extraction patterns
    SYMBOL_PATTERNS = [
        r'\b([A-Z][a-zA-Z0-9]+(?:Service|Controller|Manager|Handler|Factory|Builder|Repository|Client))\b',  # Common class patterns
        r'\b([A-Z][a-zA-Z0-9]+(?:Config|Settings|Options|Context|State))\b',  # Config classes
        r'\b([a-z_][a-z0-9_]*)\(\)',  # Function calls
        r'`([a-zA-Z_][a-zA-Z0-9_]*)`',  # Backtick-quoted symbols
        r'class\s+([A-Z][a-zA-Z0-9]+)',  # Class definitions
        r'def\s+([a-z_][a-z0-9_]*)',  # Function definitions
        r'import\s+([a-zA-Z_][a-zA-Z0-9_.]*)',  # Imports
        r'from\s+([a-zA-Z_][a-zA-Z0-9_.]*)\s+import',  # From imports
    ]
    
    # Cache TTL
    CACHE_TTL_MINUTES = 30
    
    # Max symbols per turn
    MAX_SYMBOLS_PER_TURN = 20

    def __init__(
        self,
        workspace_root: str,
        file_extensions: Optional[List[str]] = None,
        max_depth: int = 3,
        enable_caching: bool = True
    ):
        """
        Initialize incremental AST builder.
        
        Args:
            workspace_root: Root directory of the workspace
            file_extensions: File extensions to analyze (default: .py)
            max_depth: Max dependency depth to traverse
            enable_caching: Enable symbol caching
        """
        self.workspace_root = Path(workspace_root)
        self.file_extensions = file_extensions or [".py"]
        self.max_depth = max_depth
        self.enable_caching = enable_caching
        
        # Accumulated context across turns
        self._context = IncrementalContext()
        
        # Cache for parsed ASTs
        self._ast_cache: Dict[str, Tuple[ast.AST, str]] = {}  # path -> (ast, hash)
        
        # File modification tracking
        self._file_hashes: Dict[str, str] = {}
        
        logger.info(
            f"📊 Incremental AST Builder initialized: "
            f"workspace={workspace_root}, depth={max_depth}"
        )

    def build_incremental_context(
        self,
        user_message: str,
        turn_number: int,
        previous_context: Optional[Dict[str, Any]] = None
    ) -> IncrementalContext:
        """
        Build context incrementally for current turn.
        
        Args:
            user_message: User's message for this turn
            turn_number: Current conversation turn number
            previous_context: Optional context from previous turns
            
        Returns:
            IncrementalContext with accumulated symbol information
        """
        self._context.turn_count = turn_number
        self._context.last_updated = datetime.now()
        
        # Step 1: Extract mentioned symbols from user message
        mentioned_symbols = self._extract_symbols_from_message(user_message)
        
        logger.info(
            f"🔍 Turn {turn_number}: Extracted {len(mentioned_symbols)} symbols "
            f"from user message"
        )
        
        # Step 2: Discover context for each mentioned symbol
        for symbol_name in mentioned_symbols[:self.MAX_SYMBOLS_PER_TURN]:
            self._discover_symbol_context(symbol_name, DiscoverySource.USER_MENTION)
        
        # Step 3: Expand context with dependencies (up to max_depth)
        self._expand_dependencies(depth=1)
        
        # Step 4: Calculate relevance scores
        self._calculate_relevance_scores(mentioned_symbols)
        
        return self._context

    def get_relevant_context(
        self,
        min_relevance: float = 0.3,
        max_symbols: int = 50
    ) -> List[SymbolContext]:
        """
        Get relevant context symbols above relevance threshold.
        
        Args:
            min_relevance: Minimum relevance score (0-1)
            max_symbols: Maximum symbols to return
            
        Returns:
            List of SymbolContext sorted by relevance
        """
        relevant = [
            s for s in self._context.symbols.values()
            if s.relevance_score >= min_relevance
        ]
        
        # Sort by relevance
        relevant.sort(key=lambda s: s.relevance_score, reverse=True)
        
        return relevant[:max_symbols]

    def invalidate_file_cache(self, file_path: str) -> None:
        """
        Invalidate cache for a specific file.
        
        Called when file changes are detected.
        """
        path_str = str(Path(file_path).resolve())
        
        if path_str in self._ast_cache:
            del self._ast_cache[path_str]
            logger.debug(f"Cache invalidated: {file_path}")
        
        # Remove symbols from this file
        to_remove = [
            name for name, symbol in self._context.symbols.items()
            if symbol.file_path == path_str
        ]
        for name in to_remove:
            del self._context.symbols[name]

    def reset_context(self) -> None:
        """Reset accumulated context for new conversation."""
        self._context = IncrementalContext()
        logger.info("Context reset for new conversation")

    # ========================================================================
    # Private Methods
    # ========================================================================

    def _extract_symbols_from_message(self, message: str) -> List[str]:
        """Extract potential symbol names from user message."""
        symbols = set()
        
        for pattern in self.SYMBOL_PATTERNS:
            matches = re.findall(pattern, message, re.IGNORECASE)
            symbols.update(matches)
        
        # Also extract CamelCase words
        camel_case = re.findall(r'\b([A-Z][a-z]+(?:[A-Z][a-z]+)+)\b', message)
        symbols.update(camel_case)
        
        # Filter out common words
        common_words = {
            "What", "How", "Where", "When", "Why", "Which", "This", "That",
            "Does", "Should", "Would", "Could", "Please", "Thanks", "Help"
        }
        symbols = {s for s in symbols if s not in common_words}
        
        return list(symbols)

    def _discover_symbol_context(
        self,
        symbol_name: str,
        source: DiscoverySource
    ) -> Optional[SymbolContext]:
        """Discover context for a specific symbol."""
        # Check cache first
        if symbol_name in self._context.symbols:
            cached = self._context.symbols[symbol_name]
            if self._is_cache_valid(cached):
                cached.source = DiscoverySource.CACHED
                return cached
        
        # Search workspace files for symbol
        for py_file in self._iter_workspace_files():
            try:
                tree = self._get_ast(py_file)
                if tree is None:
                    continue
                
                symbol_context = self._find_symbol_in_ast(
                    tree, symbol_name, str(py_file), source
                )
                
                if symbol_context:
                    self._context.symbols[symbol_name] = symbol_context
                    self._context.files_analyzed.add(str(py_file))
                    return symbol_context
                    
            except Exception as e:
                logger.debug(f"Error analyzing {py_file}: {e}")
        
        return None

    def _find_symbol_in_ast(
        self,
        tree: ast.AST,
        symbol_name: str,
        file_path: str,
        source: DiscoverySource
    ) -> Optional[SymbolContext]:
        """Find a symbol in an AST tree."""
        for node in ast.walk(tree):
            # Check classes
            if isinstance(node, ast.ClassDef) and node.name == symbol_name:
                return SymbolContext(
                    name=node.name,
                    symbol_type="class",
                    file_path=file_path,
                    line_number=node.lineno,
                    signature=self._get_class_signature(node),
                    docstring=ast.get_docstring(node),
                    dependencies=self._extract_class_dependencies(node),
                    source=source
                )
            
            # Check functions
            if isinstance(node, ast.FunctionDef) and node.name == symbol_name:
                return SymbolContext(
                    name=node.name,
                    symbol_type="function",
                    file_path=file_path,
                    line_number=node.lineno,
                    signature=self._get_function_signature(node),
                    docstring=ast.get_docstring(node),
                    dependencies=self._extract_function_dependencies(node),
                    source=source
                )
            
            # Check async functions
            if isinstance(node, ast.AsyncFunctionDef) and node.name == symbol_name:
                return SymbolContext(
                    name=node.name,
                    symbol_type="async_function",
                    file_path=file_path,
                    line_number=node.lineno,
                    signature=self._get_function_signature(node),
                    docstring=ast.get_docstring(node),
                    dependencies=self._extract_function_dependencies(node),
                    source=source
                )
        
        return None

    def _expand_dependencies(self, depth: int = 1) -> None:
        """Expand context by discovering dependencies."""
        if depth > self.max_depth:
            return
        
        # Collect dependencies to discover
        deps_to_discover = set()
        
        for symbol in list(self._context.symbols.values()):
            for dep in symbol.dependencies:
                if dep not in self._context.symbols:
                    deps_to_discover.add(dep)
        
        # Discover each dependency
        for dep_name in list(deps_to_discover)[:self.MAX_SYMBOLS_PER_TURN]:
            self._discover_symbol_context(dep_name, DiscoverySource.DEPENDENCY)

    def _calculate_relevance_scores(self, mentioned_symbols: List[str]) -> None:
        """Calculate relevance scores for all discovered symbols."""
        mentioned_set = set(s.lower() for s in mentioned_symbols)
        
        for name, symbol in self._context.symbols.items():
            score = 0.0
            
            # Direct mention = highest relevance
            if name.lower() in mentioned_set:
                score = 1.0
            # User mention source
            elif symbol.source == DiscoverySource.USER_MENTION:
                score = 0.9
            # Dependency of mentioned symbol
            elif symbol.source == DiscoverySource.DEPENDENCY:
                score = 0.6
            # Related by other means
            elif symbol.source == DiscoverySource.RELATED:
                score = 0.3
            # Cached (from previous turns)
            elif symbol.source == DiscoverySource.CACHED:
                score = 0.5
            
            # Boost for recent discovery
            age = datetime.now() - symbol.discovered_at
            if age < timedelta(minutes=5):
                score *= 1.1
            
            symbol.relevance_score = min(score, 1.0)

    def _get_ast(self, file_path: Path) -> Optional[ast.AST]:
        """Get AST for file, using cache if available."""
        path_str = str(file_path.resolve())
        
        # Calculate file hash
        try:
            content = file_path.read_text(encoding='utf-8')
            file_hash = hashlib.md5(content.encode()).hexdigest()
        except Exception:
            return None
        
        # Check cache
        if self.enable_caching and path_str in self._ast_cache:
            cached_ast, cached_hash = self._ast_cache[path_str]
            if cached_hash == file_hash:
                return cached_ast
        
        # Parse file
        try:
            tree = ast.parse(content)
            
            # Cache result
            if self.enable_caching:
                self._ast_cache[path_str] = (tree, file_hash)
            
            return tree
            
        except SyntaxError:
            return None

    def _iter_workspace_files(self):
        """Iterate over workspace files with target extensions."""
        for ext in self.file_extensions:
            for py_file in self.workspace_root.rglob(f"*{ext}"):
                # Skip common directories
                path_str = str(py_file)
                if any(skip in path_str for skip in [
                    "__pycache__", ".git", "node_modules", ".venv", "venv",
                    "build", "dist", ".egg-info"
                ]):
                    continue
                yield py_file

    def _is_cache_valid(self, symbol: SymbolContext) -> bool:
        """Check if cached symbol is still valid."""
        age = datetime.now() - symbol.discovered_at
        return age < timedelta(minutes=self.CACHE_TTL_MINUTES)

    def _get_class_signature(self, node: ast.ClassDef) -> str:
        """Extract class signature string."""
        bases = [
            (b.id if isinstance(b, ast.Name) else ast.dump(b))
            for b in node.bases
        ]
        bases_str = f"({', '.join(bases)})" if bases else ""
        return f"class {node.name}{bases_str}"

    def _get_function_signature(self, node) -> str:
        """Extract function signature string."""
        args = []
        
        for arg in node.args.args:
            arg_str = arg.arg
            if arg.annotation:
                arg_str += f": {ast.unparse(arg.annotation)}"
            args.append(arg_str)
        
        args_str = ", ".join(args)
        prefix = "async " if isinstance(node, ast.AsyncFunctionDef) else ""
        
        return_annotation = ""
        if node.returns:
            return_annotation = f" -> {ast.unparse(node.returns)}"
        
        return f"{prefix}def {node.name}({args_str}){return_annotation}"

    def _extract_class_dependencies(self, node: ast.ClassDef) -> List[str]:
        """Extract class dependencies (bases, used types)."""
        deps = []
        
        # Base classes
        for base in node.bases:
            if isinstance(base, ast.Name):
                deps.append(base.id)
        
        # Types used in methods
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                deps.extend(self._extract_function_dependencies(item))
        
        return list(set(deps))

    def _extract_function_dependencies(self, node) -> List[str]:
        """Extract function dependencies (called functions, used types)."""
        deps = []
        
        for child in ast.walk(node):
            # Function calls
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    deps.append(child.func.id)
                elif isinstance(child.func, ast.Attribute):
                    deps.append(child.func.attr)
            
            # Type annotations
            if isinstance(child, ast.Name) and child.id[0].isupper():
                deps.append(child.id)
        
        return list(set(deps))

    def get_statistics(self) -> Dict[str, Any]:
        """Get builder statistics."""
        return {
            "total_symbols": len(self._context.symbols),
            "files_analyzed": len(self._context.files_analyzed),
            "turn_count": self._context.turn_count,
            "cache_size": len(self._ast_cache),
            "symbols_by_type": self._count_symbols_by_type(),
            "symbols_by_source": self._count_symbols_by_source()
        }

    def _count_symbols_by_type(self) -> Dict[str, int]:
        """Count symbols by type."""
        counts: Dict[str, int] = {}
        for symbol in self._context.symbols.values():
            counts[symbol.symbol_type] = counts.get(symbol.symbol_type, 0) + 1
        return counts

    def _count_symbols_by_source(self) -> Dict[str, int]:
        """Count symbols by discovery source."""
        counts: Dict[str, int] = {}
        for symbol in self._context.symbols.values():
            source_name = symbol.source.value
            counts[source_name] = counts.get(source_name, 0) + 1
        return counts


# ============================================================================
# Integration Helper
# ============================================================================

def create_incremental_ast_builder(
    workspace_root: str,
    max_depth: int = 3
) -> IncrementalASTBuilder:
    """
    Factory function to create incremental AST builder.
    
    Args:
        workspace_root: Root directory of workspace
        max_depth: Max dependency traversal depth
        
    Returns:
        Configured IncrementalASTBuilder instance
    """
    return IncrementalASTBuilder(
        workspace_root=workspace_root,
        max_depth=max_depth
    )
