"""
Universal Multi-Language AST Parser

Unified interface for 10+ languages using tree-sitter.
Supports C#, SQL, Python, JavaScript, HTML, CSS, and more.

Based on actual project analysis:
- Platform.Classic: 8,572 C# + 2,447 SQL
- luum-fresh: 5,375 C# + 4,829 SQL
- V5.ColdFusion: 2,694 CFM (regex fallback)

Copyright © 2025 Asif Hussain. All rights reserved.
"""

import logging
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from collections import defaultdict

logger = logging.getLogger(__name__)


class UniversalParser:
    """
    Multi-language AST parser using tree-sitter
    
    Supported Languages (via tree-sitter):
    - C# (.cs) - 14,459 files across projects
    - SQL (.sql) - 7,284 files across projects
    - Python (.py) - 1,940 files across projects
    - JavaScript (.js, .jsx, .mjs, .cjs)
    - TypeScript (.ts, .tsx)
    - HTML (.html, .htm)
    - CSS (.css, .scss)
    - JSON (.json)
    - YAML (.yaml, .yml)
    - Markdown (.md)
    
    Fallback Support (regex-based):
    - ColdFusion (.cfm, .cfc) - NO tree-sitter parser exists
    - Razor (.cshtml) - Hybrid HTML + C#
    """
    
    # Language detection by file extension
    EXTENSION_MAP = {
        # Primary languages (88% of codebase)
        '.cs': 'c_sharp',
        '.csx': 'c_sharp',
        '.sql': 'sql',
        '.py': 'python',
        '.pyw': 'python',
        
        # JavaScript ecosystem
        '.js': 'javascript',
        '.mjs': 'javascript',
        '.cjs': 'javascript',
        '.jsx': 'javascript',
        '.ts': 'typescript',
        '.tsx': 'tsx',
        
        # Web technologies
        '.html': 'html',
        '.htm': 'html',
        '.css': 'css',
        '.scss': 'css',
        
        # Data/Config formats
        '.json': 'json',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.md': 'markdown',
        
        # Future support (installed but low usage)
        '.java': 'java',
        '.kt': 'kotlin',
        '.kts': 'kotlin',
        
        # Fallback/Special cases
        '.cfm': 'coldfusion',  # Regex fallback
        '.cfc': 'coldfusion',  # Regex fallback
        '.cshtml': 'razor',    # Hybrid parser
    }
    
    def __init__(self):
        """Initialize universal parser with lazy-loaded parsers"""
        self.parsers = {}  # Lazy-load parsers
        self.languages = {}
        self.available_languages = self._detect_available_parsers()
        logger.info(f"✅ UniversalParser initialized: {len(self.available_languages)} languages available")
    
    def _detect_available_parsers(self) -> Set[str]:
        """Detect which tree-sitter parsers are installed"""
        available = set()
        
        # Test each language parser
        parser_modules = {
            'c_sharp': 'tree_sitter_c_sharp',
            'sql': 'tree_sitter_sql',
            'python': 'tree_sitter_python',
            'javascript': 'tree_sitter_javascript',
            'typescript': 'tree_sitter_typescript',
            'tsx': 'tree_sitter_typescript',  # TSX from typescript module
            'html': 'tree_sitter_html',
            'css': 'tree_sitter_css',
            'json': 'tree_sitter_json',
            'yaml': 'tree_sitter_yaml',
            'markdown': 'tree_sitter_markdown',
            'java': 'tree_sitter_java',
            'kotlin': 'tree_sitter_kotlin',
        }
        
        for lang, module_name in parser_modules.items():
            try:
                module = __import__(module_name, fromlist=['language'])
                available.add(lang)
                logger.debug(f"✅ {lang}: {module_name}")
            except ImportError:
                logger.debug(f"⚠️ {lang}: {module_name} not installed")
        
        return available
    
    def get_parser(self, language: str):
        """Get or create parser for language (lazy loading)"""
        if language not in self.available_languages:
            logger.warning(f"Parser not available for {language}")
            return None
        
        if language in self.parsers:
            return self.parsers[language], self.languages[language]
        
        try:
            # Import language module and get Language object
            import tree_sitter
            
            if language == 'c_sharp':
                from tree_sitter_c_sharp import language
                lang_obj = tree_sitter.Language(language())
            elif language == 'sql':
                from tree_sitter_sql import language
                lang_obj = tree_sitter.Language(language())
            elif language == 'python':
                from tree_sitter_python import language
                lang_obj = tree_sitter.Language(language())
            elif language == 'javascript':
                from tree_sitter_javascript import language
                lang_obj = tree_sitter.Language(language())
            elif language == 'typescript':
                from tree_sitter_typescript import language_typescript
                lang_obj = tree_sitter.Language(language_typescript())
            elif language == 'tsx':
                from tree_sitter_typescript import language_tsx
                lang_obj = tree_sitter.Language(language_tsx())
            elif language == 'html':
                from tree_sitter_html import language
                lang_obj = tree_sitter.Language(language())
            elif language == 'css':
                from tree_sitter_css import language
                lang_obj = tree_sitter.Language(language())
            elif language == 'json':
                from tree_sitter_json import language
                lang_obj = tree_sitter.Language(language())
            elif language == 'yaml':
                from tree_sitter_yaml import language
                lang_obj = tree_sitter.Language(language())
            elif language == 'markdown':
                from tree_sitter_markdown import language
                lang_obj = tree_sitter.Language(language())
            elif language == 'java':
                from tree_sitter_java import language
                lang_obj = tree_sitter.Language(language())
            elif language == 'kotlin':
                from tree_sitter_kotlin import language
                lang_obj = tree_sitter.Language(language())
            else:
                logger.error(f"Unknown language: {language}")
                return None
            
            # Create parser and set language (modern API)
            parser = tree_sitter.Parser()
            parser.language = lang_obj
            
            self.parsers[language] = parser
            self.languages[language] = lang_obj
            
            logger.debug(f"Loaded parser: {language}")
            return parser, lang_obj
            
        except Exception as e:
            logger.error(f"Failed to load parser for {language}: {e}")
            return None
    
    def parse_file(self, file_path: Path) -> Optional[Any]:
        """
        Parse file using appropriate language parser
        
        Args:
            file_path: Path to source file
            
        Returns:
            Tree-sitter tree object or None if parsing fails
        """
        # Detect language
        ext = file_path.suffix.lower()
        language = self.EXTENSION_MAP.get(ext)
        
        if not language:
            logger.debug(f"Unsupported file type: {ext}")
            return None
        
        # Handle special cases (ColdFusion, Razor)
        if language == 'coldfusion':
            return self._parse_coldfusion_fallback(file_path)
        elif language == 'razor':
            return self._parse_razor_fallback(file_path)
        
        # Get tree-sitter parser
        parser_data = self.get_parser(language)
        if not parser_data:
            return None
        
        parser, _ = parser_data
        
        # Read and parse file
        try:
            code = file_path.read_bytes()  # tree-sitter expects bytes
            tree = parser.parse(code)
            logger.debug(f"✅ Parsed {file_path.name} ({language})")
            return tree
        except Exception as e:
            logger.error(f"Parse failed for {file_path}: {e}")
            return None
    
    def extract_structure(self, tree, language: str, file_path: Path = None) -> Dict[str, Any]:
        """
        Extract high-level structure from AST
        
        Args:
            tree: Tree-sitter tree object (or fallback dict)
            language: Language name
            file_path: Optional file path for additional context
            
        Returns:
            {
                'functions': [...],
                'classes': [...],
                'imports': [...],
                'exports': [...],
            }
        """
        if not tree:
            return {}
        
        # Handle fallback results (dict instead of tree)
        if isinstance(tree, dict):
            return tree
        
        # Language-specific extractors
        extractors = {
            'python': self._extract_python,
            'javascript': self._extract_javascript,
            'typescript': self._extract_javascript,
            'tsx': self._extract_javascript,
            'c_sharp': self._extract_csharp,
            'java': self._extract_java,
            'kotlin': self._extract_kotlin,
            'sql': self._extract_sql,
            'html': self._extract_html,
            'css': self._extract_css,
        }
        
        extractor = extractors.get(language, self._extract_generic)
        return extractor(tree.root_node, language)
    
    def _extract_python(self, root, language: str) -> Dict[str, Any]:
        """Extract Python-specific constructs"""
        functions = []
        classes = []
        imports = []
        
        def traverse(node):
            if node.type == 'function_definition':
                name_node = node.child_by_field_name('name')
                if name_node:
                    functions.append(name_node.text.decode('utf-8'))
            elif node.type == 'class_definition':
                name_node = node.child_by_field_name('name')
                if name_node:
                    classes.append(name_node.text.decode('utf-8'))
            elif node.type in ('import_statement', 'import_from_statement'):
                imports.append(node.text.decode('utf-8').split('\n')[0][:100])
            
            for child in node.children:
                traverse(child)
        
        traverse(root)
        
        return {
            'functions': functions,
            'classes': classes,
            'imports': imports,
            'complexity_estimate': len(functions) + len(classes) * 2,
        }
    
    def _extract_javascript(self, root, language: str) -> Dict[str, Any]:
        """Extract JavaScript/TypeScript/TSX constructs"""
        functions = []
        classes = []
        imports = []
        exports = []
        components = []
        
        def traverse(node):
            if node.type in ('function_declaration', 'function'):
                name_node = node.child_by_field_name('name')
                if name_node:
                    functions.append(name_node.text.decode('utf-8'))
            elif node.type in ('class_declaration', 'class'):
                name_node = node.child_by_field_name('name')
                if name_node:
                    classes.append(name_node.text.decode('utf-8'))
            elif node.type == 'import_statement':
                imports.append(node.text.decode('utf-8')[:100])
            elif node.type == 'export_statement':
                exports.append(node.text.decode('utf-8')[:100])
            elif language == 'tsx' and node.type == 'jsx_element':
                # React component detection
                opening = node.child_by_field_name('opening_element')
                if opening:
                    name = opening.child(1)  # Get tag name
                    if name and name.text.decode('utf-8')[0].isupper():
                        components.append(name.text.decode('utf-8'))
            
            for child in node.children:
                traverse(child)
        
        traverse(root)
        
        result = {
            'functions': functions,
            'classes': classes,
            'imports': imports,
            'exports': exports,
        }
        
        if language == 'tsx':
            result['components'] = list(set(components))
        
        return result
    
    def _extract_csharp(self, root, language: str) -> Dict[str, Any]:
        """Extract C# constructs"""
        classes = []
        interfaces = []
        methods = []
        namespaces = []
        usings = []
        
        def traverse(node):
            if node.type == 'class_declaration':
                name_node = node.child_by_field_name('name')
                if name_node:
                    classes.append(name_node.text.decode('utf-8'))
            elif node.type == 'interface_declaration':
                name_node = node.child_by_field_name('name')
                if name_node:
                    interfaces.append(name_node.text.decode('utf-8'))
            elif node.type == 'method_declaration':
                name_node = node.child_by_field_name('name')
                if name_node:
                    methods.append(name_node.text.decode('utf-8'))
            elif node.type == 'namespace_declaration':
                name_node = node.child_by_field_name('name')
                if name_node:
                    namespaces.append(name_node.text.decode('utf-8'))
            elif node.type == 'using_directive':
                usings.append(node.text.decode('utf-8')[:100])
            
            for child in node.children:
                traverse(child)
        
        traverse(root)
        
        return {
            'classes': classes,
            'interfaces': interfaces,
            'methods': methods,
            'namespaces': list(set(namespaces)),
            'usings': usings,
            'complexity_estimate': len(classes) * 3 + len(methods),
        }
    
    def _extract_java(self, root, language: str) -> Dict[str, Any]:
        """Extract Java constructs"""
        classes = []
        interfaces = []
        methods = []
        packages = []
        imports = []
        
        def traverse(node):
            if node.type == 'class_declaration':
                name_node = node.child_by_field_name('name')
                if name_node:
                    classes.append(name_node.text.decode('utf-8'))
            elif node.type == 'interface_declaration':
                name_node = node.child_by_field_name('name')
                if name_node:
                    interfaces.append(name_node.text.decode('utf-8'))
            elif node.type == 'method_declaration':
                name_node = node.child_by_field_name('name')
                if name_node:
                    methods.append(name_node.text.decode('utf-8'))
            elif node.type == 'package_declaration':
                packages.append(node.text.decode('utf-8'))
            elif node.type == 'import_declaration':
                imports.append(node.text.decode('utf-8')[:100])
            
            for child in node.children:
                traverse(child)
        
        traverse(root)
        
        return {
            'classes': classes,
            'interfaces': interfaces,
            'methods': methods,
            'packages': packages,
            'imports': imports,
        }
    
    def _extract_kotlin(self, root, language: str) -> Dict[str, Any]:
        """Extract Kotlin constructs"""
        # Similar to Java but with Kotlin-specific features
        return self._extract_java(root, language)
    
    def _extract_sql(self, root, language: str) -> Dict[str, Any]:
        """Extract SQL constructs"""
        tables = []
        procedures = []
        functions = []
        
        def traverse(node):
            if node.type in ('create_table_statement', 'create_table'):
                # Find table name
                for child in node.children:
                    if child.type == 'identifier':
                        tables.append(child.text.decode('utf-8'))
                        break
            elif node.type in ('create_procedure', 'create_procedure_statement'):
                for child in node.children:
                    if child.type == 'identifier':
                        procedures.append(child.text.decode('utf-8'))
                        break
            elif node.type in ('create_function', 'create_function_statement'):
                for child in node.children:
                    if child.type == 'identifier':
                        functions.append(child.text.decode('utf-8'))
                        break
            
            for child in node.children:
                traverse(child)
        
        traverse(root)
        
        return {
            'tables': tables,
            'procedures': procedures,
            'functions': functions,
            'statement_count': len(root.children),
        }
    
    def _extract_html(self, root, language: str) -> Dict[str, Any]:
        """Extract HTML structure"""
        tags = []
        ids = []
        classes = []
        
        def traverse(node):
            if node.type == 'element':
                # Get tag name
                start_tag = node.child_by_field_name('start_tag')
                if start_tag:
                    tag_name = start_tag.child(1)
                    if tag_name:
                        tags.append(tag_name.text.decode('utf-8'))
            
            for child in node.children:
                traverse(child)
        
        traverse(root)
        
        return {
            'tags': list(set(tags)),
            'tag_count': len(tags),
        }
    
    def _extract_css(self, root, language: str) -> Dict[str, Any]:
        """Extract CSS selectors and rules"""
        selectors = []
        rules = 0
        
        def traverse(node):
            nonlocal rules
            if node.type == 'rule_set':
                rules += 1
            elif node.type == 'class_selector':
                selectors.append(node.text.decode('utf-8'))
            
            for child in node.children:
                traverse(child)
        
        traverse(root)
        
        return {
            'selectors': selectors[:50],  # Limit to first 50
            'rule_count': rules,
        }
    
    def _extract_generic(self, root, language: str) -> Dict[str, Any]:
        """Generic extraction for unsupported languages"""
        return {
            'node_count': root.child_count,
            'node_type': root.type,
            'language': language,
        }
    
    # ========================================================================
    # FALLBACK PARSERS (Regex-based for languages without tree-sitter)
    # ========================================================================
    
    def _parse_coldfusion_fallback(self, file_path: Path) -> Dict[str, Any]:
        """
        Fallback parser for ColdFusion (.cfm, .cfc)
        NO tree-sitter parser exists - using regex
        """
        try:
            code = file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            logger.error(f"Failed to read ColdFusion file {file_path}: {e}")
            return {'error': str(e)}
        
        # CFML component detection
        cfc_pattern = re.compile(r'<cfcomponent[^>]*>', re.IGNORECASE)
        function_pattern = re.compile(r'<cffunction\s+name="([^"]+)"', re.IGNORECASE)
        query_pattern = re.compile(r'<cfquery[^>]*>', re.IGNORECASE)
        
        components = cfc_pattern.findall(code)
        functions = function_pattern.findall(code)
        queries = query_pattern.findall(code)
        
        return {
            'type': 'coldfusion',
            'parser': 'regex_fallback',
            'components': len(components),
            'functions': functions,
            'query_count': len(queries),
            'warning': 'ColdFusion has no tree-sitter parser - regex-based parsing',
        }
    
    def _parse_razor_fallback(self, file_path: Path) -> Dict[str, Any]:
        """
        Fallback parser for Razor (.cshtml)
        Hybrid HTML + C# - parse sequentially
        """
        try:
            code = file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            logger.error(f"Failed to read Razor file {file_path}: {e}")
            return {'error': str(e)}
        
        # Extract C# code blocks
        csharp_block_pattern = re.compile(r'@\{([^}]+)\}', re.DOTALL)
        csharp_inline_pattern = re.compile(r'@[\w\.]+')
        
        code_blocks = csharp_block_pattern.findall(code)
        inline_expressions = csharp_inline_pattern.findall(code)
        
        return {
            'type': 'razor',
            'parser': 'hybrid_fallback',
            'csharp_blocks': len(code_blocks),
            'inline_expressions': len(inline_expressions),
            'warning': 'Razor is hybrid HTML+C# - using regex extraction',
        }


# Global singleton
_universal_parser = None


def get_universal_parser() -> UniversalParser:
    """Get singleton instance of universal parser"""
    global _universal_parser
    if _universal_parser is None:
        _universal_parser = UniversalParser()
    return _universal_parser


# Convenience function for quick file analysis
def analyze_file(file_path: Path) -> Dict[str, Any]:
    """
    Quick analysis of a single file
    
    Args:
        file_path: Path to file to analyze
        
    Returns:
        Structure dictionary with extracted elements
        
    Example:
        >>> result = analyze_file(Path('MyClass.cs'))
        >>> print(result['classes'])
        ['MyClass', 'Helper']
    """
    parser = get_universal_parser()
    tree = parser.parse_file(file_path)
    
    if tree is None:
        return {'error': 'Unsupported file type or parse failure'}
    
    ext = file_path.suffix.lower()
    language = parser.EXTENSION_MAP.get(ext)
    
    return parser.extract_structure(tree, language, file_path)
