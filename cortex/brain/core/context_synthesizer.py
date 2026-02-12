"""
Context Synthesizer (ENH-046 Phase 3)

Purpose: Per-orchestrator-type intelligent summarization
Architecture: Type-specific compression strategies

Compression strategies:
1. Agent files: Extract purpose + key methods (99.8% reduction)
2. YAML rules: Filter by intent + prioritize (97% reduction)
3. Source code: AST summary - signatures only (98% reduction)

Author: CORTEX AI | TDD: RED→GREEN→REFACTOR
"""

import ast
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import yaml

# ═══════════════════════════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════════════════════════

class SynthesisStrategy(str, Enum):
    """Synthesis strategy types"""
    AGENT_FILE = "agent"
    YAML_RULES = "yaml"
    FILE_CONTENT = "file"
    GENERIC = "generic"


# ═══════════════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class SynthesisResult:
    """Result of content synthesis"""
    content: str
    original_size: int
    compressed_size: int
    compression_ratio: float
    strategy: str
    metadata: Dict[str, Any]
    warnings: List[str]


# ═══════════════════════════════════════════════════════════════════════════════
# CONTEXT SYNTHESIZER
# ═══════════════════════════════════════════════════════════════════════════════

class ContextSynthesizer:
    """
    Intelligent content synthesizer with per-type compression strategies.

    Strategies:
    - Agent files: Purpose + key method signatures (99.8% compression)
    - YAML rules: Filter by intent + limit to top 15 (97% compression)
    - Source code: AST extraction - signatures only (98% compression)

    Usage:
        synthesizer = ContextSynthesizer()

        # Agent file
        result = synthesizer.synthesize_agent_files(content, "agent.md")

        # YAML rules
        result = synthesizer.synthesize_yaml_rules(content, intent_type="IMPLEMENT")

        # Source code
        result = synthesizer.synthesize_file_content(content, "code.py")

        # Auto-detect
        result = synthesizer.synthesize_all(content, "file.ext")
    """

    def __init__(self):
        """Initialize synthesizer"""
        self.default_max_rules = 15

    # ═══════════════════════════════════════════════════════════════════════════
    # AGENT FILE SYNTHESIS (99.8% compression)
    # ═══════════════════════════════════════════════════════════════════════════

    def synthesize_agent_files(
        self,
        content: str,
        filename: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> SynthesisResult:
        """
        Synthesize agent file to purpose + key methods.

        Extraction:
        - Purpose/description from comments/docstrings
        - Key method signatures (not implementation)

        Target: 99.8% compression (1903 lines → 3 lines)

        Args:
            content: Agent file content
            filename: Agent filename
            metadata: Additional metadata

        Returns:
            SynthesisResult with compressed content
        """
        original_size = len(content)
        warnings = []

        # Extract purpose
        purpose = self._extract_purpose(content, filename)

        # Extract key methods
        methods = self._extract_methods(content)

        # Build compressed summary
        lines = [f"{filename}:"]
        if purpose:
            lines.append(f"  Purpose: {purpose}")
        if methods:
            lines.append(f"  Methods: {', '.join(methods[:5])}")  # Top 5 methods

        compressed_content = "\n".join(lines)
        compressed_size = len(compressed_content)

        compression_ratio = 1.0 - (compressed_size / original_size) if original_size > 0 else 0.0

        return SynthesisResult(
            content=compressed_content,
            original_size=original_size,
            compressed_size=compressed_size,
            compression_ratio=compression_ratio,
            strategy=SynthesisStrategy.AGENT_FILE,
            metadata=metadata or {"filename": filename},
            warnings=warnings
        )

    def synthesize_agent_files_batch(
        self,
        files: Dict[str, str]
    ) -> Dict[str, SynthesisResult]:
        """
        Synthesize multiple agent files in batch.

        Args:
            files: Dict of {filename: content}

        Returns:
            Dict of {filename: SynthesisResult}
        """
        results = {}
        for filename, content in files.items():
            results[filename] = self.synthesize_agent_files(content, filename)
        return results

    def _extract_purpose(self, content: str, filename: str) -> str:
        """Extract purpose from comments/docstrings"""
        # Look for Purpose: or Description: in comments
        purpose_match = re.search(r'#\s*Purpose:\s*(.+)', content, re.IGNORECASE)
        if purpose_match:
            return purpose_match.group(1).strip()

        # Look for class docstring
        class_doc_match = re.search(r'class\s+\w+.*?:\s*["\']([^"\']+)', content, re.DOTALL)
        if class_doc_match:
            return class_doc_match.group(1).strip()[:100]  # First 100 chars

        # Fallback: Use filename hint
        name_hint = filename.replace("_", " ").replace("-", " ").replace(".py", "").replace(".md", "")
        return f"Module: {name_hint}"

    def _extract_methods(self, content: str) -> List[str]:
        """Extract method names from content"""
        methods = []

        # Try AST parsing first
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    methods.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            methods.append(item.name)
        except (SyntaxError, ValueError):
            # Fallback: Regex
            method_matches = re.findall(r'def\s+(\w+)\s*\(', content)
            methods.extend(method_matches)

        # Remove private methods and duplicates
        methods = [m for m in methods if not m.startswith('_')]
        return list(dict.fromkeys(methods))  # Deduplicate while preserving order

    # ═══════════════════════════════════════════════════════════════════════════
    # YAML RULE SYNTHESIS (97% compression)
    # ═══════════════════════════════════════════════════════════════════════════

    def synthesize_yaml_rules(
        self,
        content: str,
        intent_type: Optional[str] = None,
        max_rules: int = 15,
        metadata: Optional[Dict[str, Any]] = None
    ) -> SynthesisResult:
        """
        Synthesize YAML rules by filtering and prioritizing.

        Filtering:
        - By intent type (IMPLEMENT, AUDIT, etc)
        - By priority (P0 > P1 > P2 > P3)
        - Limit to top N rules (default 15)

        Target: 97% compression (500 rules → 15 applicable)

        Args:
            content: YAML content
            intent_type: Filter by intent (optional)
            max_rules: Maximum rules to return
            metadata: Additional metadata

        Returns:
            SynthesisResult with filtered rules
        """
        original_size = len(content)
        warnings = []

        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            warnings.append(f"YAML parse error: {e}")
            return SynthesisResult(
                content=content,
                original_size=original_size,
                compressed_size=original_size,
                compression_ratio=0.0,
                strategy=SynthesisStrategy.YAML_RULES,
                metadata=metadata or {},
                warnings=warnings
            )

        # Extract and filter rules
        rules = self._extract_yaml_rules(data, intent_type)

        # Prioritize and limit
        rules = self._prioritize_rules(rules)[:max_rules]

        # Build compressed content
        if rules:
            compressed_content = f"Filtered to {intent_type or 'all'} intent: {len(rules)} rules\n"
            for rule in rules:
                compressed_content += f"  - {rule}\n"
        else:
            compressed_content = "No matching rules"

        compressed_size = len(compressed_content)
        compression_ratio = 1.0 - (compressed_size / original_size) if original_size > 0 else 0.0

        return SynthesisResult(
            content=compressed_content,
            original_size=original_size,
            compressed_size=compressed_size,
            compression_ratio=compression_ratio,
            strategy=SynthesisStrategy.YAML_RULES,
            metadata=metadata or {},
            warnings=warnings
        )

    def _extract_yaml_rules(self, data: Any, intent_type: Optional[str]) -> List[str]:
        """Extract rules from YAML data structure"""
        rules = []

        def extract_recursive(obj, path=""):
            if isinstance(obj, dict):
                # Check if this is a rule entry
                if 'id' in obj:
                    rule_id = obj['id']
                    # Filter by intent if specified
                    if intent_type is None or obj.get('intent') == intent_type or obj.get('status') == intent_type:
                        priority = obj.get('priority', 'P3')
                        rules.append((rule_id, priority, obj))

                # Recurse into dict
                for key, value in obj.items():
                    extract_recursive(value, f"{path}.{key}" if path else key)

            elif isinstance(obj, list):
                for item in obj:
                    extract_recursive(item, path)

        extract_recursive(data)

        # Return just the rule IDs with descriptions
        return [f"{r[0]} ({r[1]}): {r[2].get('description', r[2].get('title', 'No description'))[:50]}"
                for r in rules]

    def _prioritize_rules(self, rules: List[str]) -> List[str]:
        """Sort rules by priority (P0 > P1 > P2 > P3)"""
        def priority_key(rule: str) -> int:
            if "P0" in rule:
                return 0
            elif "P1" in rule:
                return 1
            elif "P2" in rule:
                return 2
            else:
                return 3

        return sorted(rules, key=priority_key)

    # ═══════════════════════════════════════════════════════════════════════════
    # FILE CONTENT SYNTHESIS (98% compression via AST)
    # ═══════════════════════════════════════════════════════════════════════════

    def synthesize_file_content(
        self,
        content: str,
        filename: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> SynthesisResult:
        """
        Synthesize source code file via AST extraction.

        Extraction:
        - Class/function signatures
        - Docstrings
        - NO implementation details

        Target: 98% compression (250 lines → 5 lines)

        Args:
            content: Source code content
            filename: Source filename
            metadata: Additional metadata

        Returns:
            SynthesisResult with AST summary
        """
        original_size = len(content)
        warnings = []

        # Try AST extraction
        try:
            tree = ast.parse(content)
            signatures = self._extract_ast_signatures(tree)

            compressed_content = f"{filename}:\n"
            for sig in signatures:
                compressed_content += f"  - {sig}\n"

        except SyntaxError as e:
            warnings.append(f"Syntax error: {e}")
            # Fallback: Regex extraction
            compressed_content = self._extract_signatures_regex(content, filename)

        compressed_size = len(compressed_content)
        compression_ratio = 1.0 - (compressed_size / original_size) if original_size > 0 else 0.0

        return SynthesisResult(
            content=compressed_content,
            original_size=original_size,
            compressed_size=compressed_size,
            compression_ratio=compression_ratio,
            strategy=SynthesisStrategy.FILE_CONTENT,
            metadata=metadata or {"filename": filename},
            warnings=warnings
        )

    def _extract_ast_signatures(self, tree: ast.AST) -> List[str]:
        """Extract signatures from AST"""
        signatures = []
        seen_functions = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                signatures.append(f"class {node.name}")
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        sig = self._format_function_signature(item, indent=True)
                        signatures.append(sig)
                        seen_functions.add(item.name)

        # Module-level functions (not in classes)
        for node in tree.body if hasattr(tree, 'body') else []:
            if isinstance(node, ast.FunctionDef) and node.name not in seen_functions:
                sig = self._format_function_signature(node)
                signatures.append(sig)

        return signatures

    def _format_function_signature(self, node: ast.FunctionDef, indent: bool = False) -> str:
        """Format function signature from AST node"""
        args = []
        for arg in node.args.args:
            arg_str = arg.arg
            if arg.annotation:
                arg_str += f": {ast.unparse(arg.annotation)}"
            args.append(arg_str)

        prefix = "  " if indent else ""
        sig = f"{prefix}def {node.name}({', '.join(args)})"

        if node.returns:
            sig += f" -> {ast.unparse(node.returns)}"

        # Add docstring if present
        docstring = ast.get_docstring(node)
        if docstring:
            sig += f" # {docstring[:50]}"

        return sig

    def _extract_signatures_regex(self, content: str, filename: str) -> str:
        """Fallback: Extract signatures using regex"""
        signatures = []

        # Extract class definitions
        class_matches = re.findall(r'class\s+(\w+).*?:', content)
        for cls in class_matches:
            signatures.append(f"class {cls}")

        # Extract function definitions
        func_matches = re.findall(r'def\s+(\w+)\s*\([^)]*\)', content)
        for func in func_matches:
            signatures.append(f"def {func}(...)")

        result = f"{filename}:\n"
        for sig in signatures[:10]:  # Limit to 10
            result += f"  - {sig}\n"

        return result

    # ═══════════════════════════════════════════════════════════════════════════
    # UNIFIED SYNTHESIS INTERFACE
    # ═══════════════════════════════════════════════════════════════════════════

    def synthesize_all(
        self,
        content: str,
        filename: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> SynthesisResult:
        """
        Auto-detect content type and apply appropriate synthesis strategy.

        Detection:
        - .py files → FILE_CONTENT (AST)
        - .yaml/.yml files → YAML_RULES
        - .md files with "agent" → AGENT_FILE
        - Others → GENERIC (pass through)

        Args:
            content: Content to synthesize
            filename: Filename for type detection
            metadata: Additional metadata

        Returns:
            SynthesisResult from appropriate strategy
        """
        if not content:
            return SynthesisResult(
                content="",
                original_size=0,
                compressed_size=0,
                compression_ratio=0.0,
                strategy=SynthesisStrategy.GENERIC,
                metadata=metadata or {},
                warnings=[]
            )

        # Detect type
        if filename.endswith('.py'):
            return self.synthesize_file_content(content, filename, metadata)

        elif filename.endswith(('.yaml', '.yml')):
            intent = metadata.get('intent') if metadata else None
            return self.synthesize_yaml_rules(content, intent_type=intent, metadata=metadata)

        elif filename.endswith('.md') or 'agent' in filename.lower() or 'orchestrator' in filename.lower():
            return self.synthesize_agent_files(content, filename, metadata)

        else:
            # Generic pass-through
            return SynthesisResult(
                content=content,
                original_size=len(content),
                compressed_size=len(content),
                compression_ratio=0.0,
                strategy=SynthesisStrategy.GENERIC,
                metadata=metadata or {},
                warnings=["Unknown file type, no compression applied"]
            )

    def synthesize_all_batch(
        self,
        files: Dict[str, str],
        metadata: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> Dict[str, SynthesisResult]:
        """
        Synthesize multiple files in batch with auto-detection.

        Args:
            files: Dict of {filename: content}
            metadata: Optional dict of {filename: metadata}

        Returns:
            Dict of {filename: SynthesisResult}
        """
        results = {}
        for filename, content in files.items():
            file_metadata = metadata.get(filename) if metadata else None
            results[filename] = self.synthesize_all(content, filename, file_metadata)
        return results
