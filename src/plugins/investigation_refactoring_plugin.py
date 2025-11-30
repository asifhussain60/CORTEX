"""
Investigation Refactoring Plugin for CORTEX 3.0

Intelligent refactoring analysis plugin that integrates with InvestigationRouter
to identify code improvement opportunities without heavy AST parsing.

Features:
- SOLID principle violation detection
- Design pattern recommendations
- Code smell identification
- Complexity reduction suggestions
- Maintainability improvements
- Performance optimization opportunities
- Token-budget efficient analysis

Integration with InvestigationRouter:
- Lightweight pattern-based analysis
- Respects token budget constraints
- Provides actionable refactoring suggestions
- Prioritizes improvements by impact

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum
import re
import logging
from datetime import datetime

from src.plugins.base_plugin import (
    BasePlugin,
    PluginMetadata,
    PluginCategory,
    PluginPriority,
    HookPoint
)

logger = logging.getLogger(__name__)


class RefactoringType(Enum):
    """Types of refactoring opportunities"""
    EXTRACT_METHOD = "extract_method"
    EXTRACT_CLASS = "extract_class"
    MOVE_METHOD = "move_method"
    RENAME_VARIABLE = "rename_variable"
    SIMPLIFY_CONDITION = "simplify_condition"
    REMOVE_DUPLICATION = "remove_duplication"
    REDUCE_COMPLEXITY = "reduce_complexity"
    IMPROVE_NAMING = "improve_naming"
    APPLY_DESIGN_PATTERN = "apply_design_pattern"
    BREAK_LARGE_CLASS = "break_large_class"
    BREAK_LONG_METHOD = "break_long_method"
    REMOVE_DEAD_CODE = "remove_dead_code"
    OPTIMIZE_IMPORTS = "optimize_imports"
    IMPROVE_ERROR_HANDLING = "improve_error_handling"
    ADD_TYPE_HINTS = "add_type_hints"


class RefactoringPriority(Enum):
    """Priority levels for refactoring suggestions"""
    CRITICAL = "critical"  # Blocking issues, major maintainability problems
    HIGH = "high"         # Significant improvements, moderate effort
    MEDIUM = "medium"     # Good to have improvements
    LOW = "low"          # Minor improvements, cosmetic changes
    OPTIONAL = "optional" # Nice-to-have suggestions


class CodeSmell(Enum):
    """Common code smells that indicate refactoring opportunities"""
    LONG_METHOD = "long_method"
    LARGE_CLASS = "large_class"
    LONG_PARAMETER_LIST = "long_parameter_list"
    DUPLICATE_CODE = "duplicate_code"
    DEAD_CODE = "dead_code"
    COMPLEX_CONDITIONAL = "complex_conditional"
    MAGIC_NUMBERS = "magic_numbers"
    POOR_NAMING = "poor_naming"
    GOD_CLASS = "god_class"
    FEATURE_ENVY = "feature_envy"
    DATA_CLUMPS = "data_clumps"
    SWITCH_STATEMENTS = "switch_statements"
    LAZY_CLASS = "lazy_class"


@dataclass
class RefactoringSuggestion:
    """A specific refactoring suggestion"""
    type: RefactoringType
    priority: RefactoringPriority
    title: str
    description: str
    file_path: str
    line_number: int
    code_snippet: Optional[str] = None
    suggested_refactoring: Optional[str] = None
    benefits: List[str] = None
    effort_estimate: str = "Medium"  # Low, Medium, High
    confidence: float = 1.0
    code_smell: Optional[CodeSmell] = None
    
    def __post_init__(self):
        if self.benefits is None:
            self.benefits = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for investigation router"""
        return {
            "type": "refactoring_suggestion",
            "refactoring_type": self.type.value,
            "priority": self.priority.value,
            "title": self.title,
            "description": self.description,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "code_snippet": self.code_snippet,
            "suggested_refactoring": self.suggested_refactoring,
            "benefits": self.benefits,
            "effort_estimate": self.effort_estimate,
            "confidence": self.confidence,
            "code_smell": self.code_smell.value if self.code_smell else None,
            "timestamp": datetime.now().isoformat()
        }


class CodeMetrics:
    """Lightweight code metrics calculator"""
    
    @staticmethod
    def calculate_method_length(lines: List[str], start_line: int) -> int:
        """Calculate method length starting from given line"""
        method_lines = 0
        indent_level = None
        
        for i in range(start_line, len(lines)):
            line = lines[i].rstrip()
            if not line or line.strip().startswith('#'):
                continue
                
            current_indent = len(line) - len(line.lstrip())
            
            if indent_level is None:
                if line.strip():
                    indent_level = current_indent
            else:
                # Method ends when we reach a line with less or equal indentation
                if line.strip() and current_indent <= indent_level:
                    break
                    
            method_lines += 1
        
        return method_lines
    
    @staticmethod
    def calculate_class_metrics(content: str, class_name: str) -> Dict[str, int]:
        """Calculate basic class metrics"""
        lines = content.split('\n')
        metrics = {
            "method_count": 0,
            "line_count": 0,
            "complexity_estimate": 0
        }
        
        in_class = False
        class_indent = 0
        
        for line in lines:
            if f"class {class_name}" in line:
                in_class = True
                class_indent = len(line) - len(line.lstrip())
                continue
            
            if in_class:
                current_indent = len(line) - len(line.lstrip())
                
                # End of class
                if line.strip() and current_indent <= class_indent:
                    break
                
                metrics["line_count"] += 1
                
                # Count methods
                if re.match(r'\s*def\s+\w+', line):
                    metrics["method_count"] += 1
                
                # Estimate complexity (if/for/while/try statements)
                if re.search(r'\s*(if|for|while|try|except|elif|else)[\s:]', line):
                    metrics["complexity_estimate"] += 1
        
        return metrics
    
    @staticmethod
    def count_parameters(method_signature: str) -> int:
        """Count parameters in method signature"""
        # Extract parameters from method definition
        match = re.search(r'def\s+\w+\s*\((.*?)\)', method_signature)
        if not match:
            return 0
        
        params = match.group(1).strip()
        if not params:
            return 0
        
        # Simple parameter count (split by comma, exclude self)
        param_list = [p.strip() for p in params.split(',') if p.strip()]
        param_list = [p for p in param_list if p != 'self']
        
        return len(param_list)


class RefactoringPatternAnalyzer:
    """Analyzes code patterns for refactoring opportunities"""
    
    def __init__(self):
        self.logger = logging.getLogger("refactoring.analyzer")
        self.metrics = CodeMetrics()
    
    def analyze_file(self, file_path: str, content: str) -> List[RefactoringSuggestion]:
        """Analyze file for refactoring opportunities"""
        suggestions = []
        lines = content.split('\n')
        
        # Detect programming language
        language = self._detect_language(file_path)
        
        if language == "python":
            suggestions.extend(self._analyze_python_patterns(file_path, content, lines))
        elif language == "javascript":
            suggestions.extend(self._analyze_javascript_patterns(file_path, content, lines))
        elif language == "csharp":
            suggestions.extend(self._analyze_csharp_patterns(file_path, content, lines))
        
        return suggestions
    
    def _analyze_python_patterns(self, file_path: str, content: str, lines: List[str]) -> List[RefactoringSuggestion]:
        """Analyze Python-specific refactoring patterns"""
        suggestions = []
        
        for line_num, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Long method detection
            if line_stripped.startswith('def '):
                method_length = self.metrics.calculate_method_length(lines, line_num - 1)
                if method_length > 30:  # Arbitrary threshold
                    suggestions.append(RefactoringSuggestion(
                        type=RefactoringType.BREAK_LONG_METHOD,
                        priority=RefactoringPriority.HIGH,
                        title="Long Method Detected",
                        description=f"Method has {method_length} lines. Consider breaking into smaller methods.",
                        file_path=file_path,
                        line_number=line_num,
                        code_snippet=line.strip(),
                        suggested_refactoring="Break method into smaller, focused functions. Extract logical blocks into separate methods.",
                        benefits=["Improved readability", "Easier testing", "Better maintainability"],
                        effort_estimate="Medium",
                        code_smell=CodeSmell.LONG_METHOD,
                        confidence=0.9
                    ))
                
                # Long parameter list detection
                param_count = self.metrics.count_parameters(line)
                if param_count > 5:  # Arbitrary threshold
                    suggestions.append(RefactoringSuggestion(
                        type=RefactoringType.EXTRACT_CLASS,
                        priority=RefactoringPriority.MEDIUM,
                        title="Long Parameter List",
                        description=f"Method has {param_count} parameters. Consider parameter object pattern.",
                        file_path=file_path,
                        line_number=line_num,
                        code_snippet=line.strip(),
                        suggested_refactoring="Create a parameter object class or use dataclass to group related parameters.",
                        benefits=["Cleaner method signatures", "Better parameter management", "Reduced coupling"],
                        effort_estimate="Medium",
                        code_smell=CodeSmell.LONG_PARAMETER_LIST,
                        confidence=0.8
                    ))
            
            # Large class detection
            elif line_stripped.startswith('class '):
                class_name = re.search(r'class\s+(\w+)', line_stripped)
                if class_name:
                    class_name = class_name.group(1)
                    metrics = self.metrics.calculate_class_metrics(content, class_name)
                    
                    if metrics["method_count"] > 15:  # Arbitrary threshold
                        suggestions.append(RefactoringSuggestion(
                            type=RefactoringType.BREAK_LARGE_CLASS,
                            priority=RefactoringPriority.HIGH,
                            title="Large Class Detected",
                            description=f"Class '{class_name}' has {metrics['method_count']} methods. Consider splitting responsibilities.",
                            file_path=file_path,
                            line_number=line_num,
                            code_snippet=line.strip(),
                            suggested_refactoring="Identify distinct responsibilities and extract them into separate classes.",
                            benefits=["Better separation of concerns", "Easier testing", "Improved maintainability"],
                            effort_estimate="High",
                            code_smell=CodeSmell.LARGE_CLASS,
                            confidence=0.8
                        ))
                    
                    if metrics["complexity_estimate"] > 20:  # High complexity
                        suggestions.append(RefactoringSuggestion(
                            type=RefactoringType.REDUCE_COMPLEXITY,
                            priority=RefactoringPriority.HIGH,
                            title="High Class Complexity",
                            description=f"Class '{class_name}' has high complexity ({metrics['complexity_estimate']} decision points).",
                            file_path=file_path,
                            line_number=line_num,
                            code_snippet=line.strip(),
                            suggested_refactoring="Simplify conditional logic, extract complex operations into methods.",
                            benefits=["Reduced cognitive load", "Easier debugging", "Better testability"],
                            effort_estimate="Medium",
                            code_smell=CodeSmell.COMPLEX_CONDITIONAL,
                            confidence=0.7
                        ))
            
            # Magic numbers detection
            elif re.search(r'\b\d{2,}\b', line_stripped) and not line_stripped.strip().startswith('#'):
                # Skip common acceptable numbers
                if not re.search(r'\b(0|1|2|10|100|1000)\b', line_stripped):
                    suggestions.append(RefactoringSuggestion(
                        type=RefactoringType.EXTRACT_METHOD,
                        priority=RefactoringPriority.LOW,
                        title="Magic Number Detected",
                        description="Consider extracting magic numbers into named constants.",
                        file_path=file_path,
                        line_number=line_num,
                        code_snippet=line.strip(),
                        suggested_refactoring="Define constants with descriptive names for numeric literals.",
                        benefits=["Improved code clarity", "Easier maintenance", "Reduced errors"],
                        effort_estimate="Low",
                        code_smell=CodeSmell.MAGIC_NUMBERS,
                        confidence=0.6
                    ))
            
            # Complex conditional detection
            elif re.search(r'\b(if|elif)\b.*(\band\b|\bor\b).*(\band\b|\bor\b)', line_stripped):
                suggestions.append(RefactoringSuggestion(
                    type=RefactoringType.SIMPLIFY_CONDITION,
                    priority=RefactoringPriority.MEDIUM,
                    title="Complex Conditional Expression",
                    description="Complex boolean logic detected. Consider simplifying.",
                    file_path=file_path,
                    line_number=line_num,
                    code_snippet=line.strip(),
                    suggested_refactoring="Extract complex conditions into well-named boolean functions.",
                    benefits=["Improved readability", "Easier testing", "Better maintainability"],
                    effort_estimate="Low",
                    code_smell=CodeSmell.COMPLEX_CONDITIONAL,
                    confidence=0.8
                ))
            
            # Missing type hints detection (Python 3.5+)
            elif line_stripped.startswith('def ') and '->' not in line:
                suggestions.append(RefactoringSuggestion(
                    type=RefactoringType.ADD_TYPE_HINTS,
                    priority=RefactoringPriority.LOW,
                    title="Missing Type Hints",
                    description="Consider adding type hints for better code documentation.",
                    file_path=file_path,
                    line_number=line_num,
                    code_snippet=line.strip(),
                    suggested_refactoring="Add type hints for parameters and return values.",
                    benefits=["Better IDE support", "Improved documentation", "Early error detection"],
                    effort_estimate="Low",
                    confidence=0.5
                ))
            
            # Poor variable naming detection
            elif re.search(r'\b(data|temp|tmp|x|y|i|j|k)\s*=', line_stripped):
                suggestions.append(RefactoringSuggestion(
                    type=RefactoringType.IMPROVE_NAMING,
                    priority=RefactoringPriority.LOW,
                    title="Poor Variable Naming",
                    description="Consider using more descriptive variable names.",
                    file_path=file_path,
                    line_number=line_num,
                    code_snippet=line.strip(),
                    suggested_refactoring="Use descriptive names that explain the variable's purpose.",
                    benefits=["Better code readability", "Self-documenting code", "Easier maintenance"],
                    effort_estimate="Low",
                    code_smell=CodeSmell.POOR_NAMING,
                    confidence=0.6
                ))
        
        return suggestions
    
    def _analyze_javascript_patterns(self, file_path: str, content: str, lines: List[str]) -> List[RefactoringSuggestion]:
        """Analyze JavaScript-specific refactoring patterns"""
        suggestions = []
        
        for line_num, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Long function detection
            if re.search(r'function\s+\w+|const\s+\w+\s*=.*=>|\w+:\s*function', line_stripped):
                # Simple heuristic: count lines until next function or end
                func_length = 0
                for i in range(line_num, len(lines)):
                    if lines[i].strip():
                        func_length += 1
                    if re.search(r'^\s*}', lines[i]) and func_length > 1:
                        break
                
                if func_length > 25:
                    suggestions.append(RefactoringSuggestion(
                        type=RefactoringType.BREAK_LONG_METHOD,
                        priority=RefactoringPriority.HIGH,
                        title="Long Function Detected",
                        description=f"Function has approximately {func_length} lines. Consider breaking it down.",
                        file_path=file_path,
                        line_number=line_num,
                        code_snippet=line.strip(),
                        suggested_refactoring="Extract logical blocks into separate functions.",
                        benefits=["Better readability", "Easier testing", "Improved reusability"],
                        effort_estimate="Medium",
                        code_smell=CodeSmell.LONG_METHOD,
                        confidence=0.7
                    ))
            
            # Callback hell detection
            elif 'function(' in line and line_stripped.count('function(') > 1:
                suggestions.append(RefactoringSuggestion(
                    type=RefactoringType.APPLY_DESIGN_PATTERN,
                    priority=RefactoringPriority.HIGH,
                    title="Potential Callback Hell",
                    description="Nested callbacks detected. Consider using Promises or async/await.",
                    file_path=file_path,
                    line_number=line_num,
                    code_snippet=line.strip(),
                    suggested_refactoring="Refactor to use Promises or async/await pattern.",
                    benefits=["Better error handling", "Improved readability", "Easier debugging"],
                    effort_estimate="Medium",
                    confidence=0.8
                ))
            
            # Magic numbers in JavaScript
            elif re.search(r'\b\d{3,}\b', line_stripped) and not line_stripped.strip().startswith('//'):
                suggestions.append(RefactoringSuggestion(
                    type=RefactoringType.EXTRACT_METHOD,
                    priority=RefactoringPriority.LOW,
                    title="Magic Number in JavaScript",
                    description="Consider extracting magic numbers into named constants.",
                    file_path=file_path,
                    line_number=line_num,
                    code_snippet=line.strip(),
                    suggested_refactoring="Use const declarations with descriptive names.",
                    benefits=["Improved maintainability", "Better code clarity"],
                    effort_estimate="Low",
                    code_smell=CodeSmell.MAGIC_NUMBERS,
                    confidence=0.6
                ))
        
        return suggestions
    
    def _analyze_csharp_patterns(self, file_path: str, content: str, lines: List[str]) -> List[RefactoringSuggestion]:
        """Analyze C#-specific refactoring patterns"""
        suggestions = []
        
        for line_num, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Long method detection in C#
            if re.search(r'(public|private|protected|internal).*\w+\s*\([^)]*\)', line_stripped):
                # Count method length (simplified)
                method_lines = 0
                brace_count = 0
                for i in range(line_num, len(lines)):
                    current_line = lines[i].strip()
                    if '{' in current_line:
                        brace_count += current_line.count('{')
                    if '}' in current_line:
                        brace_count -= current_line.count('}')
                    if brace_count <= 0 and method_lines > 1:
                        break
                    method_lines += 1
                
                if method_lines > 30:
                    suggestions.append(RefactoringSuggestion(
                        type=RefactoringType.BREAK_LONG_METHOD,
                        priority=RefactoringPriority.HIGH,
                        title="Long Method in C#",
                        description=f"Method has approximately {method_lines} lines.",
                        file_path=file_path,
                        line_number=line_num,
                        code_snippet=line.strip(),
                        suggested_refactoring="Extract logical blocks into private methods.",
                        benefits=["Better maintainability", "Easier unit testing"],
                        effort_estimate="Medium",
                        code_smell=CodeSmell.LONG_METHOD,
                        confidence=0.8
                    ))
        
        return suggestions
    
    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file path"""
        ext = Path(file_path).suffix.lower()
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.cs': 'csharp',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c'
        }
        return language_map.get(ext, 'unknown')


class InvestigationRefactoringPlugin(BasePlugin):
    """Refactoring analysis plugin for investigation router"""
    
    def __init__(self):
        super().__init__()
        self.analyzer = RefactoringPatternAnalyzer()
    
    def _get_metadata(self) -> PluginMetadata:
        """Get plugin metadata"""
        return PluginMetadata(
            plugin_id="investigation_refactoring",
            name="Investigation Refactoring Analyzer",
            version="1.0.0",
            category=PluginCategory.ANALYSIS,
            priority=PluginPriority.MEDIUM,
            description="Code refactoring analysis for investigation router",
            author="Asif Hussain",
            dependencies=[],
            hooks=[HookPoint.ON_INVESTIGATION_ANALYSIS.value],
            natural_language_patterns=[
                "refactoring suggestions",
                "code improvements",
                "refactor opportunities",
                "code quality analysis",
                "improvement recommendations"
            ]
        )
    
    def initialize(self) -> bool:
        """Initialize refactoring plugin"""
        try:
            self.logger.info("Initializing Investigation Refactoring Plugin")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize refactoring plugin: {e}")
            return False
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute refactoring analysis during investigation
        
        Args:
            context: Investigation context
            
        Returns:
            Refactoring analysis results
        """
        try:
            # Extract investigation context
            target_entity = context.get('target_entity')
            entity_type = context.get('entity_type', 'unknown')
            budget_remaining = context.get('budget_remaining', 0)
            
            # Estimate token cost for refactoring analysis
            estimated_tokens = self._estimate_refactoring_cost(target_entity, entity_type)
            
            if estimated_tokens > budget_remaining:
                return {
                    "success": False,
                    "error": "Insufficient budget for refactoring analysis",
                    "estimated_tokens": estimated_tokens,
                    "budget_remaining": budget_remaining
                }
            
            # Perform refactoring analysis
            suggestions = self._analyze_refactoring_opportunities(target_entity, entity_type, context)
            
            return {
                "success": True,
                "plugin_id": self.metadata.plugin_id,
                "analysis_type": "refactoring",
                "target_entity": target_entity,
                "suggestions": [s.to_dict() for s in suggestions],
                "tokens_consumed": estimated_tokens,
                "summary": self._generate_refactoring_summary(suggestions)
            }
            
        except Exception as e:
            self.logger.error(f"Refactoring analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "plugin_id": self.metadata.plugin_id
            }
    
    def cleanup(self) -> bool:
        """Cleanup refactoring plugin"""
        try:
            self.logger.info("Cleaning up Investigation Refactoring Plugin")
            return True
        except Exception as e:
            self.logger.error(f"Failed to cleanup refactoring plugin: {e}")
            return False
    
    def _estimate_refactoring_cost(self, target_entity: str, entity_type: str) -> int:
        """Estimate token cost for refactoring analysis"""
        base_cost = 150
        
        if entity_type == 'file':
            return base_cost + 250
        elif entity_type == 'component':
            return base_cost + 400
        else:
            return base_cost + 200
    
    def _analyze_refactoring_opportunities(self, target_entity: str, entity_type: str, context: Dict[str, Any]) -> List[RefactoringSuggestion]:
        """Analyze refactoring opportunities"""
        suggestions = []
        
        if entity_type == 'file':
            # Get file content from context
            file_content = context.get('file_content', '')
            if file_content:
                suggestions = self.analyzer.analyze_file(target_entity, file_content)
        
        elif entity_type == 'component':
            # Component analysis would examine multiple files
            suggestions.append(RefactoringSuggestion(
                type=RefactoringType.EXTRACT_CLASS,
                priority=RefactoringPriority.MEDIUM,
                title=f"Component Analysis Required",
                description=f"Component '{target_entity}' requires detailed refactoring analysis",
                file_path=f"component:{target_entity}",
                line_number=0,
                suggested_refactoring="Analyze component architecture for improvement opportunities",
                benefits=["Better code organization", "Improved maintainability"],
                confidence=0.5
            ))
        
        return suggestions
    
    def _generate_refactoring_summary(self, suggestions: List[RefactoringSuggestion]) -> Dict[str, Any]:
        """Generate summary of refactoring suggestions"""
        if not suggestions:
            return {
                "total_suggestions": 0,
                "priority_breakdown": {},
                "main_recommendations": ["Code appears to be well-structured. No major refactoring opportunities identified."]
            }
        
        priority_counts = {}
        for suggestion in suggestions:
            priority = suggestion.priority.value
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        # Generate main recommendations
        recommendations = []
        critical_high = [s for s in suggestions if s.priority in [RefactoringPriority.CRITICAL, RefactoringPriority.HIGH]]
        
        if critical_high:
            recommendations.append(f"🔧 {len(critical_high)} high-priority refactoring opportunities identified")
        
        # Group by refactoring type
        type_counts = {}
        for suggestion in suggestions:
            ref_type = suggestion.type.value
            type_counts[ref_type] = type_counts.get(ref_type, 0) + 1
        
        top_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        for ref_type, count in top_types:
            if count > 1:
                recommendations.append(f"📋 {count} opportunities for {ref_type.replace('_', ' ')}")
        
        if not recommendations:
            recommendations = ["✅ Code quality is good. Minor improvements available."]
        
        return {
            "total_suggestions": len(suggestions),
            "priority_breakdown": priority_counts,
            "refactoring_type_breakdown": type_counts,
            "main_recommendations": recommendations
        }


def register() -> BasePlugin:
    """Register the investigation refactoring plugin"""
    return InvestigationRefactoringPlugin()