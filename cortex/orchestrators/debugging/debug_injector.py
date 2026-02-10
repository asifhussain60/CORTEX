"""
CORTEX Debug Injector
=====================

Language-aware debug marker injection system.
Supports JavaScript, TypeScript, Python, and extensible for other languages.

Author: CORTEX
Version: 1.0.0
Phase: Phase 21.5 - Universal Debugging

Injection Strategy:
- Function entry/exit tracing
- Async operation tracking
- DOM manipulation logging (JS/TS)
- Event handler registration
- Promise chain tracking
- Error boundary detection
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
import fnmatch
import json
import logging
import re
import shutil

logger = logging.getLogger(__name__)

# Marker prefix constant

# Default exclusion patterns
DEFAULT_EXCLUDE_PATTERNS = [
    "**/node_modules/**",
    "**/.git/**",
    "**/__pycache__/**",
    "**/.venv/**",
    "**/venv/**",
    "**/*.min.js",
    "**/*.min.css",
    "**/dist/**",
    "**/build/**",
    "**/.cortex-debug/**",
    "**/vendor/**",
]


@dataclass
class InjectionPoint:
    """Represents a single injection point in a file."""
    
    line_number: int
    column: int
    injection_type: str  # FUNC, ASYNC, DOM, EVENT, TIMER, PROMISE, ERROR
    original_code: str
    injected_code: str
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class InjectionResult:
    """Result of injecting into a single file."""
    
    file_path: Path
    original_content: str
    modified_content: str
    injection_points: List[InjectionPoint] = field(default_factory=list)
    success: bool = True
    error: Optional[str] = None


class LanguageInjector(ABC):
    """Abstract base class for language-specific injectors."""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
    
    @property
    @abstractmethod
    def file_extensions(self) -> Set[str]:
        """Return supported file extensions."""
        pass
    
    @property
    @abstractmethod
    def language_name(self) -> str:
        """Return the language name."""
        pass
    
    @abstractmethod
    def inject(self, content: str, file_name: str) -> InjectionResult:
        """Inject debug markers into file content."""
        pass
    
    def _create_marker(self, phase: str, file_name: str, line: int, message: str) -> str:
        """Create a standardized debug marker string."""


class JavaScriptInjector(LanguageInjector):
    """JavaScript/TypeScript debug marker injector."""
    
    @property
    def file_extensions(self) -> Set[str]:
        return {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}
    
    @property
    def language_name(self) -> str:
        return "JavaScript/TypeScript"
    
    def inject(self, content: str, file_name: str) -> InjectionResult:
        """Inject debug markers into JavaScript/TypeScript content."""
        result = InjectionResult(
            file_path=Path(file_name),
            original_content=content,
            modified_content=content,
        )
        
        lines = content.split('\n')
        modified_lines = []
        injection_points = []
        
        for i, line in enumerate(lines):
            line_num = i + 1
            modified_lines.append(line)
            
            # Skip if already has CORTEX marker
                continue
            
            # Skip comments
            stripped = line.strip()
            if stripped.startswith('//') or stripped.startswith('/*') or stripped.startswith('*'):
                continue
            
            # Get indentation
            indent_match = re.match(r'^(\s*)', line)
            indent = indent_match.group(1) if indent_match else ''
            inner_indent = indent + '    '
            
            # Pattern 1: Function declarations - function name() { or async function name() {
            func_match = re.match(r'^(\s*)(async\s+)?function\s+(\w+)\s*\([^)]*\)\s*\{?\s*$', line)
            if func_match:
                func_name = func_match.group(3)
                if func_name not in ('constructor', 'get', 'set'):
                    marker = self._create_marker('FUNC', file_name, line_num, f'ENTER {func_name}()')
                    modified_lines.append(f"{inner_indent}console.log('{marker}');")
                    injection_points.append(InjectionPoint(
                        line_number=line_num,
                        column=0,
                        injection_type='FUNC',
                        original_code=line,
                        injected_code=f"console.log('{marker}');",
                        context={'function_name': func_name}
                    ))
                continue
            
            # Pattern 2: Arrow functions assigned to const/let/var
            arrow_match = re.match(r'^(\s*)(const|let|var)\s+(\w+)\s*=\s*(async\s*)?\([^)]*\)\s*=>\s*\{?\s*$', line)
            if arrow_match:
                func_name = arrow_match.group(3)
                marker = self._create_marker('ARROW', file_name, line_num, f'ENTER {func_name}()')
                modified_lines.append(f"{inner_indent}console.log('{marker}');")
                injection_points.append(InjectionPoint(
                    line_number=line_num,
                    column=0,
                    injection_type='ARROW',
                    original_code=line,
                    injected_code=f"console.log('{marker}');",
                    context={'function_name': func_name}
                ))
                continue
            
            # Pattern 3: Class methods - methodName() { or async methodName() {
            method_match = re.match(r'^(\s*)(async\s+)?(\w+)\s*\([^)]*\)\s*\{\s*$', line)
            if method_match and not line.strip().startswith('if') and not line.strip().startswith('for') and not line.strip().startswith('while'):
                method_name = method_match.group(3)
                if method_name not in ('constructor', 'if', 'for', 'while', 'switch', 'catch', 'get', 'set'):
                    marker = self._create_marker('METHOD', file_name, line_num, f'ENTER {method_name}()')
                    modified_lines.append(f"{inner_indent}console.log('{marker}');")
                    injection_points.append(InjectionPoint(
                        line_number=line_num,
                        column=0,
                        injection_type='METHOD',
                        original_code=line,
                        injected_code=f"console.log('{marker}');",
                        context={'method_name': method_name}
                    ))
                continue
            
            # Pattern 4: Await expressions (insert before)
            if 'await ' in line and 'console.log' not in line:
                await_match = re.search(r'await\s+([\w.]+)', line)
                if await_match:
                    async_op = await_match.group(1)
                    marker = self._create_marker('ASYNC', file_name, line_num, f'AWAIT {async_op}')
                    # Insert before the current line
                    modified_lines.insert(-1, f"{indent}console.log('{marker}');")
                    injection_points.append(InjectionPoint(
                        line_number=line_num,
                        column=0,
                        injection_type='ASYNC',
                        original_code=line,
                        injected_code=f"console.log('{marker}');",
                        context={'async_operation': async_op}
                    ))
            
            # Pattern 5: DOM queries
            if 'getElementById' in line or 'querySelector' in line:
                dom_match = re.search(r'(getElementById|querySelector(?:All)?)\s*\(\s*[\'"`]([^\'"`]+)[\'"`]', line)
                if dom_match:
                    method = dom_match.group(1)
                    selector = dom_match.group(2)
                    marker = self._create_marker('DOM', file_name, line_num, f'{method}({selector})')
                    modified_lines.insert(-1, f"{indent}console.log('{marker}');")
                    injection_points.append(InjectionPoint(
                        line_number=line_num,
                        column=0,
                        injection_type='DOM',
                        original_code=line,
                        injected_code=f"console.log('{marker}');",
                        context={'method': method, 'selector': selector}
                    ))
            
            # Pattern 6: Event listeners
            if '.addEventListener' in line:
                event_match = re.search(r'(\w+)\.addEventListener\s*\(\s*[\'"`](\w+)[\'"`]', line)
                if event_match:
                    element = event_match.group(1)
                    event_type = event_match.group(2)
                    marker = self._create_marker('EVENT', file_name, line_num, f'LISTEN {element}.{event_type}')
                    modified_lines.insert(-1, f"{indent}console.log('{marker}');")
                    injection_points.append(InjectionPoint(
                        line_number=line_num,
                        column=0,
                        injection_type='EVENT',
                        original_code=line,
                        injected_code=f"console.log('{marker}');",
                        context={'element': element, 'event_type': event_type}
                    ))
            
            # Pattern 7: setTimeout/setInterval
            if 'setTimeout' in line or 'setInterval' in line:
                timer_match = re.search(r'(setTimeout|setInterval)\s*\(', line)
                if timer_match:
                    timer_type = timer_match.group(1)
                    marker = self._create_marker('TIMER', file_name, line_num, f'{timer_type.upper()} REGISTERED')
                    modified_lines.insert(-1, f"{indent}console.log('{marker}');")
                    injection_points.append(InjectionPoint(
                        line_number=line_num,
                        column=0,
                        injection_type='TIMER',
                        original_code=line,
                        injected_code=f"console.log('{marker}');",
                        context={'timer_type': timer_type}
                    ))
            
            # Pattern 8: Promise .then chains
            if '.then(' in line:
                marker = self._create_marker('PROMISE', file_name, line_num, 'THEN CHAIN')
                if '{' in line:
                    modified_lines.append(f"{inner_indent}console.log('{marker}');")
                    injection_points.append(InjectionPoint(
                        line_number=line_num,
                        column=0,
                        injection_type='PROMISE',
                        original_code=line,
                        injected_code=f"console.log('{marker}');",
                        context={}
                    ))
            
            # Pattern 9: Catch blocks
            if '.catch(' in line or 'catch (' in line or 'catch(' in line:
                marker = self._create_marker('ERROR', file_name, line_num, 'CATCH BLOCK')
                if '{' in line:
                    modified_lines.append(f"{inner_indent}console.error('{marker}', e || err || error || 'unknown');")
                    injection_points.append(InjectionPoint(
                        line_number=line_num,
                        column=0,
                        injection_type='ERROR',
                        original_code=line,
                        injected_code=f"console.error('{marker}');",
                        context={}
                    ))
        
        result.modified_content = '\n'.join(modified_lines)
        result.injection_points = injection_points
        
        return result


class PythonInjector(LanguageInjector):
    """Python debug marker injector."""
    
    @property
    def file_extensions(self) -> Set[str]:
        return {".py", ".pyw"}
    
    @property
    def language_name(self) -> str:
        return "Python"
    
    def inject(self, content: str, file_name: str) -> InjectionResult:
        """Inject debug markers into Python content."""
        result = InjectionResult(
            file_path=Path(file_name),
            original_content=content,
            modified_content=content,
        )
        
        lines = content.split('\n')
        modified_lines = []
        injection_points = []
        
        for i, line in enumerate(lines):
            line_num = i + 1
            modified_lines.append(line)
            
            # Skip if already has CORTEX marker
                continue
            
            # Skip comments and empty lines
            stripped = line.strip()
            if stripped.startswith('#') or not stripped:
                continue
            
            # Get indentation
            indent_match = re.match(r'^(\s*)', line)
            indent = indent_match.group(1) if indent_match else ''
            inner_indent = indent + '    '
            
            # Pattern 1: Function/method definitions
            func_match = re.match(r'^(\s*)(async\s+)?def\s+(\w+)\s*\([^)]*\)\s*(?:->.*)?:\s*$', line)
            if func_match:
                func_name = func_match.group(3)
                if func_name not in ('__init__', '__str__', '__repr__'):
                    marker = self._create_marker('FUNC', file_name, line_num, f'ENTER {func_name}()')
                    modified_lines.append(f'{inner_indent}print("{marker}")')
                    injection_points.append(InjectionPoint(
                        line_number=line_num,
                        column=0,
                        injection_type='FUNC',
                        original_code=line,
                        injected_code=f'print("{marker}")',
                        context={'function_name': func_name}
                    ))
                continue
            
            # Pattern 2: Class definitions
            class_match = re.match(r'^(\s*)class\s+(\w+)\s*(?:\([^)]*\))?\s*:\s*$', line)
            if class_match:
                class_name = class_match.group(2)
                marker = self._create_marker('CLASS', file_name, line_num, f'CLASS {class_name}')
                modified_lines.append(f'{inner_indent}print("{marker}")')
                injection_points.append(InjectionPoint(
                    line_number=line_num,
                    column=0,
                    injection_type='CLASS',
                    original_code=line,
                    injected_code=f'print("{marker}")',
                    context={'class_name': class_name}
                ))
                continue
            
            # Pattern 3: Await expressions
            if 'await ' in line and 'print(' not in line:
                await_match = re.search(r'await\s+([\w.]+)', line)
                if await_match:
                    async_op = await_match.group(1)
                    marker = self._create_marker('ASYNC', file_name, line_num, f'AWAIT {async_op}')
                    modified_lines.insert(-1, f'{indent}print("{marker}")')
                    injection_points.append(InjectionPoint(
                        line_number=line_num,
                        column=0,
                        injection_type='ASYNC',
                        original_code=line,
                        injected_code=f'print("{marker}")',
                        context={'async_operation': async_op}
                    ))
            
            # Pattern 4: Try blocks
            if stripped == 'try:':
                marker = self._create_marker('TRY', file_name, line_num, 'TRY BLOCK')
                modified_lines.append(f'{inner_indent}print("{marker}")')
                injection_points.append(InjectionPoint(
                    line_number=line_num,
                    column=0,
                    injection_type='TRY',
                    original_code=line,
                    injected_code=f'print("{marker}")',
                    context={}
                ))
            
            # Pattern 5: Except blocks
            except_match = re.match(r'^(\s*)except\s*(?:(\w+)(?:\s+as\s+(\w+))?)?\s*:\s*$', line)
            if except_match:
                exc_type = except_match.group(2) or 'Exception'
                exc_var = except_match.group(3) or 'e'
                marker = self._create_marker('EXCEPT', file_name, line_num, f'CAUGHT {exc_type}')
                modified_lines.append(f'{inner_indent}print("{marker}", {exc_var} if "{exc_var}" in dir() else "")')
                injection_points.append(InjectionPoint(
                    line_number=line_num,
                    column=0,
                    injection_type='EXCEPT',
                    original_code=line,
                    injected_code=f'print("{marker}")',
                    context={'exception_type': exc_type}
                ))
            
            # Pattern 6: With statements (context managers)
            if stripped.startswith('with ') and stripped.endswith(':'):
                with_match = re.search(r'with\s+([\w.]+)', line)
                if with_match:
                    context_mgr = with_match.group(1)
                    marker = self._create_marker('WITH', file_name, line_num, f'CONTEXT {context_mgr}')
                    modified_lines.append(f'{inner_indent}print("{marker}")')
                    injection_points.append(InjectionPoint(
                        line_number=line_num,
                        column=0,
                        injection_type='WITH',
                        original_code=line,
                        injected_code=f'print("{marker}")',
                        context={'context_manager': context_mgr}
                    ))
        
        result.modified_content = '\n'.join(modified_lines)
        result.injection_points = injection_points
        
        return result


class HTMLInjector(LanguageInjector):
    """HTML debug marker injector (inline scripts)."""
    
    @property
    def file_extensions(self) -> Set[str]:
        return {".html", ".htm"}
    
    @property
    def language_name(self) -> str:
        return "HTML"
    
    def inject(self, content: str, file_name: str) -> InjectionResult:
        """Inject debug markers into inline scripts in HTML."""
        result = InjectionResult(
            file_path=Path(file_name),
            original_content=content,
            modified_content=content,
        )
        
        # Find all inline script blocks and inject
        js_injector = JavaScriptInjector(self.session_id)
        
        def replace_script(match):
            script_content = match.group(2)
            if script_content.strip():
                js_result = js_injector.inject(script_content, file_name)
                return f'{match.group(1)}{js_result.modified_content}</script>'
            return match.group(0)
        
        modified = re.sub(
            r'(<script[^>]*>)(.*?)</script>',
            replace_script,
            content,
            flags=re.DOTALL
        )
        
        result.modified_content = modified
        
        return result


class DebugInjector:
    """
    Main debug injector that coordinates language-specific injectors.
    
    Features:
    - Auto-detects language from file extension
    - Creates backups before modification
    - Tracks all injection points for cleanup
    - Supports exclusion patterns
    """
    
    def __init__(
        self,
        session_id: str,
        repo_path: Path,
        output_dir: Path,
    ):
        self.session_id = session_id
        self.repo_path = Path(repo_path).resolve()
        self.output_dir = Path(output_dir)
        self.backup_dir = self.output_dir / "backups"
        
        # Initialize language-specific injectors
        self.injectors: Dict[str, LanguageInjector] = {}
        self._register_injector(JavaScriptInjector(session_id))
        self._register_injector(PythonInjector(session_id))
        self._register_injector(HTMLInjector(session_id))
        
        logger.info(f"DebugInjector initialized with {len(self.injectors)} language injectors")
    
    def _register_injector(self, injector: LanguageInjector):
        """Register a language-specific injector."""
        for ext in injector.file_extensions:
            self.injectors[ext] = injector
    
    def inject(
        self,
        file_patterns: Optional[List[str]] = None,
        languages: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Inject debug markers into matching files.
        
        Args:
            file_patterns: Glob patterns for files to inject
            languages: Language extensions to target
            exclude_patterns: Patterns to exclude
        
        Returns:
            Injection summary with file list and marker counts
        """
        # Set defaults
        if file_patterns is None:
            file_patterns = ["**/*.js", "**/*.ts", "**/*.py", "**/*.html"]
        
        exclude_patterns = exclude_patterns or DEFAULT_EXCLUDE_PATTERNS
        
        # Create backup directory
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Collect files to inject
        files_to_inject = self._collect_files(file_patterns, exclude_patterns)
        
        logger.info(f"Found {len(files_to_inject)} files to inject")
        
        results = {
            "session_id": self.session_id,
            "injected_files": [],
            "total_markers": 0,
            "by_language": {},
            "by_file": {},
            "backup_dir": str(self.backup_dir),
            "errors": [],
        }
        
        injection_map = {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "files": {},
        }
        
        for file_path in files_to_inject:
            try:
                rel_path = file_path.relative_to(self.repo_path)
                ext = file_path.suffix.lower()
                
                if ext not in self.injectors:
                    continue
                
                injector = self.injectors[ext]
                
                # Read file content
                content = file_path.read_text(encoding='utf-8')
                
                # Skip if already injected
                    logger.info(f"Skipping {rel_path} - already injected")
                    continue
                
                # Create backup
                backup_path = self.backup_dir / str(rel_path).replace('/', '_').replace('\\', '_')
                backup_path.write_text(content, encoding='utf-8')
                
                # Inject markers
                result = injector.inject(content, str(rel_path))
                
                if result.injection_points:
                    # Write modified content
                    file_path.write_text(result.modified_content, encoding='utf-8')
                    
                    # Track results
                    results["injected_files"].append(str(rel_path))
                    results["total_markers"] += len(result.injection_points)
                    results["by_file"][str(rel_path)] = len(result.injection_points)
                    
                    lang = injector.language_name
                    results["by_language"][lang] = results["by_language"].get(lang, 0) + len(result.injection_points)
                    
                    # Add to injection map
                    injection_map["files"][str(rel_path)] = {
                        "backup": str(backup_path),
                        "markers": len(result.injection_points),
                        "injection_points": [
                            {
                                "line": ip.line_number,
                                "type": ip.injection_type,
                                "context": ip.context,
                            }
                            for ip in result.injection_points
                        ]
                    }
                    
                    logger.info(f"Injected {len(result.injection_points)} markers into {rel_path}")
                
            except Exception as e:
                error_msg = f"Failed to inject {file_path}: {e}"
                logger.error(error_msg)
                results["errors"].append(error_msg)
        
        # Save injection map
        map_path = self.output_dir / "injection-map.json"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        with open(map_path, 'w') as f:
            json.dump(injection_map, f, indent=2)
        
        results["injection_map"] = str(map_path)
        
        logger.info(f"Injection complete: {results['total_markers']} markers in {len(results['injected_files'])} files")
        
        return results
    
    def _collect_files(
        self,
        patterns: List[str],
        exclude_patterns: List[str],
    ) -> List[Path]:
        """Collect files matching patterns, excluding exclusions."""
        files = set()
        
        for pattern in patterns:
            for file_path in self.repo_path.glob(pattern):
                if file_path.is_file():
                    # Check exclusions
                    rel_path = str(file_path.relative_to(self.repo_path))
                    excluded = False
                    for exclude in exclude_patterns:
                        if fnmatch.fnmatch(rel_path, exclude) or fnmatch.fnmatch(str(file_path), exclude):
                            excluded = True
                            break
                    
                    if not excluded:
                        files.add(file_path)
        
        return sorted(files)
