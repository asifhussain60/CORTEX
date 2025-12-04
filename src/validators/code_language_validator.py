"""
Code Language Validator (Task 3.3)
Enforces English-only code and comments in templates
"""
from typing import List, Optional, Set
from dataclasses import dataclass
import re
from pathlib import Path
import yaml


@dataclass
class Violation:
    """Represents a code language violation"""
    line_number: int
    snippet: str
    language: str
    message: str


@dataclass
class ValidationResult:
    """Result of code language validation"""
    is_valid: bool
    violations: List[Violation]
    
    @property
    def violation_count(self) -> int:
        """Get count of violations"""
        return len(self.violations)
    
    @property
    def summary(self) -> str:
        """Get summary of validation result"""
        if self.is_valid:
            return "All code blocks use English"
        return f"Found {self.violation_count} language violation(s)"


class CodeLanguageValidator:
    """
    Validator for ensuring English-only code and comments in templates.
    
    Features:
    - Detect non-English comments in code blocks
    - Validate variable/function names in strict mode
    - Support multiple programming languages
    - Extract and validate code blocks from templates
    - Line number tracking for violations
    
    Usage:
        validator = CodeLanguageValidator()
        result = validator.validate_code_block(code, language='python')
        if not result.is_valid:
            for violation in result.violations:
                print(f"Line {violation.line_number}: {violation.message}")
    """
    
    # Common non-English words/phrases in different languages
    NON_ENGLISH_PATTERNS = {
        'Spanish': [
            r'\b(hacer|esto|aquí|función|método|clase|retornar|devolver|procesar|'
            r'datos|resultado|valor|número|números|suma|total|calcular|crear|eliminar|uno|dos|tres)\b',
            r'[áéíóúñ]',  # Spanish accents
        ],
        'French': [
            r'\b(faire|ceci|ici|fonction|méthode|classe|retourner|traiter|'
            r'données|résultat|valeur|nombre|nombres|somme|calculer|créer|supprimer|'
            r'corriger|cela|cette|celui)\b',
            r'[àâæçéèêëïîôùûü]',  # French accents
        ],
        'German': [
            r'\b(machen|dies|hier|funktion|methode|klasse|zurück|verarbeiten|'
            r'daten|ergebnis|wert|zahl|summe|berechnen|erstellen|löschen)\b',
            r'[äöüß]',  # German special chars
        ],
        'Portuguese': [
            r'\b(fazer|isto|aqui|função|método|classe|retornar|processar|'
            r'dados|resultado|valor|número|soma|calcular|criar|remover)\b',
            r'[ãõâêôàáéíóú]',  # Portuguese accents
        ],
        'Italian': [
            r'\b(fare|questo|qui|funzione|metodo|classe|ritornare|elaborare|'
            r'dati|risultato|valore|numero|somma|calcolare|creare|rimuovere)\b',
            r'[àèéìíîòóùú]',  # Italian accents
        ],
        'Chinese': [
            r'[\u4e00-\u9fff]',  # Chinese characters
        ],
        'Japanese': [
            r'[\u3040-\u309f\u30a0-\u30ff]',  # Hiragana and Katakana
        ],
        'Korean': [
            r'[\uac00-\ud7af]',  # Korean characters
        ],
        'Arabic': [
            r'[\u0600-\u06ff]',  # Arabic characters
        ],
        'Russian': [
            r'[\u0400-\u04ff]',  # Cyrillic characters
        ],
    }
    
    # Programming language comment patterns
    COMMENT_PATTERNS = {
        'python': [r'#.*$'],
        'javascript': [r'//.*$', r'/\*.*?\*/'],
        'java': [r'//.*$', r'/\*.*?\*/'],
        'c': [r'//.*$', r'/\*.*?\*/'],
        'cpp': [r'//.*$', r'/\*.*?\*/'],
        'csharp': [r'//.*$', r'/\*.*?\*/'],
        'ruby': [r'#.*$'],
        'php': [r'//.*$', r'#.*$', r'/\*.*?\*/'],
        'go': [r'//.*$', r'/\*.*?\*/'],
        'rust': [r'//.*$', r'/\*.*?\*/'],
    }
    
    # Python/programming keywords and common English words that might look like other languages
    CODE_KEYWORDS = {
        'del', 'def', 'class', 'return', 'import', 'from', 'as', 'if', 'else',
        'for', 'while', 'try', 'except', 'with', 'pass', 'break', 'continue',
        'and', 'or', 'not', 'in', 'is', 'lambda', 'yield', 'async', 'await',
        # Common English words
        'calculate', 'total', 'price', 'the', 'to', 'of', 'a', 'an', 'this',
        'that', 'use', 'get', 'set', 'add', 'remove', 'delete', 'update',
        'create', 'process', 'data', 'value', 'number', 'sum', 'result',
    }
    
    def __init__(self):
        """Initialize code language validator"""
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for performance"""
        self._compiled_patterns = {}
        for lang, patterns in self.NON_ENGLISH_PATTERNS.items():
            self._compiled_patterns[lang] = [
                re.compile(pattern, re.IGNORECASE | re.MULTILINE)
                for pattern in patterns
            ]
    
    def validate_code_block(
        self,
        code: str,
        language: str = 'python',
        strict_mode: bool = False
    ) -> ValidationResult:
        """
        Validate a code block for English-only content.
        
        Args:
            code: Code block to validate
            language: Programming language (python, javascript, etc.)
            strict_mode: If True, also validate identifiers (function/variable names)
        
        Returns:
            ValidationResult with validation status and violations
        """
        if not code or not code.strip():
            return ValidationResult(is_valid=True, violations=[])
        
        violations = []
        lines = code.split('\n')
        
        # Extract comments
        comments = self._extract_comments(code, language)
        
        # Check each comment for non-English content
        for line_num, comment in comments:
            detected_lang = self._detect_language(comment)
            if detected_lang and detected_lang != 'English':
                violations.append(Violation(
                    line_number=line_num,
                    snippet=comment.strip()[:80],  # First 80 chars
                    language=detected_lang,
                    message=f"Non-English ({detected_lang}) detected in comment"
                ))
        
        # In strict mode, also check identifiers
        if strict_mode:
            identifier_violations = self._check_identifiers(code, lines)
            violations.extend(identifier_violations)
        
        return ValidationResult(
            is_valid=len(violations) == 0,
            violations=violations
        )
    
    def _extract_comments(self, code: str, language: str) -> List[tuple]:
        """
        Extract comments from code with line numbers.
        
        Args:
            code: Source code
            language: Programming language
        
        Returns:
            List of (line_number, comment_text) tuples
        """
        comments = []
        lines = code.split('\n')
        
        comment_patterns = self.COMMENT_PATTERNS.get(language, self.COMMENT_PATTERNS['python'])
        
        for line_num, line in enumerate(lines, start=1):
            for pattern in comment_patterns:
                matches = re.finditer(pattern, line)
                for match in matches:
                    comment_text = match.group(0)
                    comments.append((line_num, comment_text))
        
        return comments
    
    def _detect_language(self, text: str) -> Optional[str]:
        """
        Detect if text contains non-English content.
        
        Args:
            text: Text to analyze
        
        Returns:
            Detected language name or 'English' if no non-English detected
        """
        # Create a copy for analysis, preserve original for pattern matching
        text_for_analysis = text.lower()
        
        # Remove common English words that might interfere, but keep the rest
        common_words = ['todo', 'fixme', 'note', 'hack', 'bug', 'fix', 'issue']
        for word in common_words:
            text_for_analysis = text_for_analysis.replace(word, '')
        
        # Don't remove code keywords from the actual text being analyzed
        # Just use them for post-filtering
        
        # Check against non-English patterns on the original text
        for lang, patterns in self._compiled_patterns.items():
            for pattern in patterns:
                if pattern.search(text.lower()):
                    # Double check it's not just a code keyword
                    match_text = pattern.search(text.lower()).group(0)
                    if match_text not in self.CODE_KEYWORDS:
                        return lang
        
        return 'English'
    
    def _check_identifiers(self, code: str, lines: List[str]) -> List[Violation]:
        """
        Check function/variable names for non-English content (strict mode).
        
        Args:
            code: Source code
            lines: Code split into lines
        
        Returns:
            List of violations for non-English identifiers
        """
        violations = []
        
        # Pattern for function/variable names (simplified)
        identifier_pattern = re.compile(r'\b([a-z_][a-z0-9_]{3,})\b', re.IGNORECASE)
        
        for line_num, line in enumerate(lines, start=1):
            # Skip comments
            if '#' in line:
                line = line[:line.index('#')]
            
            matches = identifier_pattern.findall(line)
            for identifier in matches:
                # Skip keywords
                if identifier.lower() in self.CODE_KEYWORDS:
                    continue
                
                # Check if identifier contains non-English
                detected_lang = self._detect_language(identifier)
                if detected_lang != 'English':
                    violations.append(Violation(
                        line_number=line_num,
                        snippet=identifier,
                        language=detected_lang,
                        message=f"Non-English identifier detected: {identifier}"
                    ))
        
        return violations
    
    def validate_template(self, template_content: str) -> ValidationResult:
        """
        Validate entire template with embedded code blocks.
        
        Args:
            template_content: Template content with markdown code blocks
        
        Returns:
            ValidationResult for all code blocks in template
        """
        violations = []
        
        # Extract code blocks (markdown format)
        code_block_pattern = re.compile(
            r'```(\w+)\n(.*?)```',
            re.DOTALL | re.MULTILINE
        )
        
        matches = code_block_pattern.finditer(template_content)
        
        for match in matches:
            language = match.group(1)
            code = match.group(2)
            
            # Get line number where code block starts
            start_pos = match.start()
            line_num = template_content[:start_pos].count('\n') + 1
            
            # Validate this code block
            result = self.validate_code_block(code, language=language)
            
            # Adjust line numbers to template line numbers
            for violation in result.violations:
                violation.line_number += line_num
                violations.append(violation)
        
        return ValidationResult(
            is_valid=len(violations) == 0,
            violations=violations
        )
    
    def validate_template_file(self, file_path: str) -> ValidationResult:
        """
        Validate code blocks in a template file (YAML or Markdown).
        
        Args:
            file_path: Path to template file
        
        Returns:
            ValidationResult for entire file
        """
        path = Path(file_path)
        
        if not path.exists():
            return ValidationResult(
                is_valid=False,
                violations=[Violation(
                    line_number=0,
                    snippet="",
                    language="",
                    message=f"File not found: {file_path}"
                )]
            )
        
        content = path.read_text(encoding='utf-8')
        
        # For YAML files, extract template content fields
        if path.suffix in ['.yaml', '.yml']:
            try:
                data = yaml.safe_load(content)
                return self._validate_yaml_templates(data)
            except yaml.YAMLError:
                pass
        
        # For markdown or plain text, validate directly
        return self.validate_template(content)
    
    def _validate_yaml_templates(self, data: dict) -> ValidationResult:
        """
        Validate code blocks in YAML template data.
        
        Args:
            data: Parsed YAML data
        
        Returns:
            ValidationResult for YAML templates
        """
        violations = []
        
        def check_value(value, path=""):
            """Recursively check YAML values for code blocks"""
            if isinstance(value, str):
                # Check if string contains code blocks
                result = self.validate_template(value)
                violations.extend(result.violations)
            elif isinstance(value, dict):
                for k, v in value.items():
                    check_value(v, f"{path}.{k}")
            elif isinstance(value, list):
                for item in value:
                    check_value(item, path)
        
        check_value(data)
        
        return ValidationResult(
            is_valid=len(violations) == 0,
            violations=violations
        )
    
    def get_supported_languages(self) -> List[str]:
        """
        Get list of supported programming languages.
        
        Returns:
            List of programming language names
        """
        return list(self.COMMENT_PATTERNS.keys())
