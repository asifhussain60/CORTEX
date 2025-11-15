"""
CORTEX 3.0 Track B: Proactive Warnings
======================================

Proactive warning system that analyzes development patterns and provides
real-time alerts about potential issues before they become problems.

Key Features:
- Real-time code quality monitoring
- Pattern-based issue detection
- Integration with file monitoring for immediate feedback
- Learning from past issues to improve predictions
- macOS-optimized notifications

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
"""

import logging
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from enum import Enum


class WarningSeverity(Enum):
    """Warning severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class WarningCategory(Enum):
    """Categories of warnings."""
    CODE_QUALITY = "code_quality"
    SECURITY = "security"
    PERFORMANCE = "performance"
    MAINTAINABILITY = "maintainability"
    BEST_PRACTICES = "best_practices"
    ARCHITECTURE = "architecture"
    DEPENDENCIES = "dependencies"
    TESTING = "testing"


@dataclass
class ProactiveWarning:
    """Represents a proactive warning."""
    id: str
    severity: WarningSeverity
    category: WarningCategory
    title: str
    message: str
    file_path: Optional[Path]
    line_number: Optional[int]
    timestamp: datetime
    suggestions: List[str]
    auto_fixable: bool = False
    context: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}


class ProactiveWarnings:
    """
    Proactive warning system for CORTEX Track B
    
    Monitors development activity and provides real-time warnings
    about potential issues and code quality concerns.
    """
    
    def __init__(self, workspace_path: Path):
        self.workspace_path = workspace_path
        self.logger = logging.getLogger("cortex.track_b.proactive_warnings")
        
        self.active_warnings: Dict[str, ProactiveWarning] = {}
        self.warning_history: List[ProactiveWarning] = []
        self.max_history_size = 1000
        
        # Warning rules and patterns
        self.warning_rules = self._initialize_warning_rules()
        
        # File type specific rules
        self.file_rules = self._initialize_file_rules()
        
        # Pattern learning data
        self.issue_patterns: Dict[str, int] = {}
        self.false_positive_patterns: Set[str] = set()
    
    def _initialize_warning_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize warning rules and patterns."""
        return {
            'large_function': {
                'pattern': r'def\s+\w+\([^)]*\):',
                'severity': WarningSeverity.WARNING,
                'category': WarningCategory.MAINTAINABILITY,
                'threshold': 50,  # lines
                'message': 'Function is too large and may be difficult to maintain'
            },
            'no_docstring': {
                'pattern': r'def\s+\w+\([^)]*\):\s*\n(?!\s*""")',
                'severity': WarningSeverity.INFO,
                'category': WarningCategory.BEST_PRACTICES,
                'message': 'Function lacks documentation'
            },
            'hardcoded_credentials': {
                'pattern': r'(?:password|api_key|secret|token)\s*=\s*["\'][^"\']{8,}["\']',
                'severity': WarningSeverity.CRITICAL,
                'category': WarningCategory.SECURITY,
                'message': 'Potential hardcoded credentials detected'
            },
            'sql_injection_risk': {
                'pattern': r'execute\s*\(\s*["\'].*%.*["\']',
                'severity': WarningSeverity.ERROR,
                'category': WarningCategory.SECURITY,
                'message': 'Potential SQL injection vulnerability'
            },
            'unused_import': {
                'pattern': r'^import\s+(\w+)',
                'severity': WarningSeverity.INFO,
                'category': WarningCategory.CODE_QUALITY,
                'message': 'Import may be unused'
            },
            'long_line': {
                'threshold': 120,
                'severity': WarningSeverity.INFO,
                'category': WarningCategory.CODE_QUALITY,
                'message': 'Line is too long for optimal readability'
            },
            'complex_condition': {
                'pattern': r'if\s+.*(?:and|or).*(?:and|or).*:',
                'severity': WarningSeverity.WARNING,
                'category': WarningCategory.MAINTAINABILITY,
                'message': 'Complex condition may be difficult to understand'
            },
            'missing_error_handling': {
                'pattern': r'(?:open\(|requests\.get|subprocess\.)',
                'severity': WarningSeverity.WARNING,
                'category': WarningCategory.BEST_PRACTICES,
                'message': 'Operation should include error handling'
            },
            'print_statement': {
                'pattern': r'print\s*\(',
                'severity': WarningSeverity.INFO,
                'category': WarningCategory.BEST_PRACTICES,
                'message': 'Consider using logging instead of print statements'
            },
            'todo_comment': {
                'pattern': r'#\s*(?:TODO|FIXME|HACK)',
                'severity': WarningSeverity.INFO,
                'category': WarningCategory.MAINTAINABILITY,
                'message': 'TODO/FIXME comment found'
            }
        }
    
    def _initialize_file_rules(self) -> Dict[str, List[str]]:
        """Initialize file-type specific rules."""
        return {
            '.py': [
                'large_function', 'no_docstring', 'hardcoded_credentials',
                'sql_injection_risk', 'unused_import', 'long_line',
                'complex_condition', 'missing_error_handling', 'print_statement',
                'todo_comment'
            ],
            '.js': [
                'hardcoded_credentials', 'long_line', 'complex_condition',
                'missing_error_handling', 'todo_comment'
            ],
            '.ts': [
                'hardcoded_credentials', 'long_line', 'complex_condition',
                'missing_error_handling', 'todo_comment'
            ],
            '.java': [
                'large_function', 'hardcoded_credentials', 'long_line',
                'complex_condition', 'todo_comment'
            ],
            '.cpp': [
                'large_function', 'hardcoded_credentials', 'long_line',
                'missing_error_handling', 'todo_comment'
            ],
            '.c': [
                'large_function', 'hardcoded_credentials', 'long_line',
                'missing_error_handling', 'todo_comment'
            ]
        }
    
    def analyze_file_change(self, file_path: Path, content: str) -> List[ProactiveWarning]:
        """Analyze a file change and generate proactive warnings."""
        warnings = []
        
        try:
            if not self._should_analyze_file(file_path):
                return warnings
            
            self.logger.debug(f"Analyzing file for warnings: {file_path.name}")
            
            # Get applicable rules for this file type
            applicable_rules = self._get_applicable_rules(file_path)
            
            # Analyze content with each rule
            for rule_name in applicable_rules:
                rule = self.warning_rules[rule_name]
                file_warnings = self._apply_rule(file_path, content, rule_name, rule)
                warnings.extend(file_warnings)
            
            # Apply meta-analysis warnings
            meta_warnings = self._apply_meta_analysis(file_path, content)
            warnings.extend(meta_warnings)
            
            # Filter out false positives
            warnings = self._filter_false_positives(warnings)
            
            # Store warnings
            for warning in warnings:
                self.active_warnings[warning.id] = warning
                self.warning_history.append(warning)
            
            # Limit history size
            if len(self.warning_history) > self.max_history_size:
                self.warning_history = self.warning_history[-self.max_history_size:]
            
            if warnings:
                self.logger.info(f"Generated {len(warnings)} warnings for {file_path.name}")
            
        except Exception as e:
            self.logger.error(f"Error analyzing file for warnings: {e}")
        
        return warnings
    
    def _should_analyze_file(self, file_path: Path) -> bool:
        """Check if file should be analyzed for warnings."""
        # Skip files outside workspace
        try:
            file_path.relative_to(self.workspace_path)
        except ValueError:
            return False
        
        # Skip certain directories
        exclude_dirs = {'.git', '__pycache__', 'node_modules', '.cortex-temp'}
        if any(part in exclude_dirs for part in file_path.parts):
            return False
        
        # Only analyze supported file types
        return file_path.suffix in self.file_rules
    
    def _get_applicable_rules(self, file_path: Path) -> List[str]:
        """Get rules applicable to a specific file type."""
        return self.file_rules.get(file_path.suffix, [])
    
    def _apply_rule(self, file_path: Path, content: str, rule_name: str, rule: Dict[str, Any]) -> List[ProactiveWarning]:
        """Apply a single warning rule to file content."""
        warnings = []
        
        try:
            if 'pattern' in rule:
                warnings.extend(self._apply_pattern_rule(file_path, content, rule_name, rule))
            elif 'threshold' in rule:
                warnings.extend(self._apply_threshold_rule(file_path, content, rule_name, rule))
        except Exception as e:
            self.logger.error(f"Error applying rule {rule_name}: {e}")
        
        return warnings
    
    def _apply_pattern_rule(self, file_path: Path, content: str, rule_name: str, rule: Dict[str, Any]) -> List[ProactiveWarning]:
        """Apply a pattern-based warning rule."""
        warnings = []
        pattern = rule['pattern']
        
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            matches = re.findall(pattern, line, re.IGNORECASE)
            
            if matches:
                # Special handling for specific rules
                if rule_name == 'large_function':
                    warning = self._check_function_size(file_path, content, line_num, rule)
                    if warning:
                        warnings.append(warning)
                elif rule_name == 'unused_import':
                    warning = self._check_unused_import(file_path, content, line, line_num, rule)
                    if warning:
                        warnings.append(warning)
                elif rule_name == 'missing_error_handling':
                    warning = self._check_error_handling(file_path, content, line_num, rule)
                    if warning:
                        warnings.append(warning)
                else:
                    # Generic pattern warning
                    warning_id = f"{rule_name}_{file_path.name}_{line_num}"
                    warning = ProactiveWarning(
                        id=warning_id,
                        severity=rule['severity'],
                        category=rule['category'],
                        title=rule_name.replace('_', ' ').title(),
                        message=rule['message'],
                        file_path=file_path,
                        line_number=line_num,
                        timestamp=datetime.now(),
                        suggestions=self._get_suggestions_for_rule(rule_name),
                        context={'line_content': line.strip(), 'matches': matches}
                    )
                    warnings.append(warning)
        
        return warnings
    
    def _apply_threshold_rule(self, file_path: Path, content: str, rule_name: str, rule: Dict[str, Any]) -> List[ProactiveWarning]:
        """Apply a threshold-based warning rule."""
        warnings = []
        threshold = rule['threshold']
        
        if rule_name == 'long_line':
            lines = content.split('\n')
            for line_num, line in enumerate(lines, 1):
                if len(line) > threshold:
                    warning_id = f"long_line_{file_path.name}_{line_num}"
                    warning = ProactiveWarning(
                        id=warning_id,
                        severity=rule['severity'],
                        category=rule['category'],
                        title="Long Line",
                        message=f"Line {line_num} has {len(line)} characters (max: {threshold})",
                        file_path=file_path,
                        line_number=line_num,
                        timestamp=datetime.now(),
                        suggestions=["Consider breaking the line into multiple lines", "Extract complex expressions into variables"],
                        context={'line_length': len(line), 'threshold': threshold}
                    )
                    warnings.append(warning)
        
        return warnings
    
    def _check_function_size(self, file_path: Path, content: str, start_line: int, rule: Dict[str, Any]) -> Optional[ProactiveWarning]:
        """Check if a function is too large."""
        try:
            lines = content.split('\n')
            
            # Find function end (simplified - assumes proper indentation)
            function_lines = 0
            base_indent = None
            
            for i in range(start_line - 1, len(lines)):
                line = lines[i]
                
                if not line.strip():
                    continue
                
                current_indent = len(line) - len(line.lstrip())
                
                if base_indent is None:
                    base_indent = current_indent
                
                # Function ends when we return to base indentation or less
                if current_indent <= base_indent and i > start_line - 1:
                    break
                
                function_lines += 1
            
            if function_lines > rule.get('threshold', 50):
                warning_id = f"large_function_{file_path.name}_{start_line}"
                return ProactiveWarning(
                    id=warning_id,
                    severity=rule['severity'],
                    category=rule['category'],
                    title="Large Function",
                    message=f"Function has {function_lines} lines (recommended max: {rule.get('threshold', 50)})",
                    file_path=file_path,
                    line_number=start_line,
                    timestamp=datetime.now(),
                    suggestions=[
                        "Consider breaking the function into smaller functions",
                        "Extract complex logic into helper functions",
                        "Use early returns to reduce nesting"
                    ],
                    context={'function_lines': function_lines}
                )
        except Exception as e:
            self.logger.error(f"Error checking function size: {e}")
        
        return None
    
    def _check_unused_import(self, file_path: Path, content: str, import_line: str, line_num: int, rule: Dict[str, Any]) -> Optional[ProactiveWarning]:
        """Check if an import is actually used."""
        try:
            # Extract module name from import statement
            match = re.search(r'import\s+(\w+)', import_line)
            if not match:
                return None
            
            module_name = match.group(1)
            
            # Check if module is used elsewhere in the file
            usage_pattern = rf'\b{module_name}\.'
            if not re.search(usage_pattern, content):
                warning_id = f"unused_import_{file_path.name}_{line_num}"
                return ProactiveWarning(
                    id=warning_id,
                    severity=rule['severity'],
                    category=rule['category'],
                    title="Unused Import",
                    message=f"Import '{module_name}' appears to be unused",
                    file_path=file_path,
                    line_number=line_num,
                    timestamp=datetime.now(),
                    suggestions=[
                        "Remove the unused import",
                        "Check if the import is used in a different way"
                    ],
                    auto_fixable=True,
                    context={'module_name': module_name}
                )
        except Exception as e:
            self.logger.error(f"Error checking unused import: {e}")
        
        return None
    
    def _check_error_handling(self, file_path: Path, content: str, line_num: int, rule: Dict[str, Any]) -> Optional[ProactiveWarning]:
        """Check if risky operations have proper error handling."""
        try:
            lines = content.split('\n')
            line = lines[line_num - 1]
            
            # Check if operation is wrapped in try-catch
            # Look backwards to see if we're in a try block
            in_try_block = False
            for i in range(line_num - 2, max(0, line_num - 10), -1):
                check_line = lines[i].strip()
                if check_line.startswith('try:'):
                    in_try_block = True
                    break
                elif check_line and not check_line.startswith('#'):
                    break
            
            if not in_try_block:
                warning_id = f"missing_error_handling_{file_path.name}_{line_num}"
                return ProactiveWarning(
                    id=warning_id,
                    severity=rule['severity'],
                    category=rule['category'],
                    title="Missing Error Handling",
                    message="Risky operation should be wrapped in try-except block",
                    file_path=file_path,
                    line_number=line_num,
                    timestamp=datetime.now(),
                    suggestions=[
                        "Wrap the operation in a try-except block",
                        "Handle specific exceptions appropriately",
                        "Consider using context managers for resource management"
                    ],
                    context={'operation': line.strip()}
                )
        except Exception as e:
            self.logger.error(f"Error checking error handling: {e}")
        
        return None
    
    def _apply_meta_analysis(self, file_path: Path, content: str) -> List[ProactiveWarning]:
        """Apply meta-analysis warnings based on overall file characteristics."""
        warnings = []
        
        try:
            lines = content.split('\n')
            non_empty_lines = [line for line in lines if line.strip()]
            
            # Check file size
            if len(non_empty_lines) > 500:
                warning_id = f"large_file_{file_path.name}"
                warnings.append(ProactiveWarning(
                    id=warning_id,
                    severity=WarningSeverity.WARNING,
                    category=WarningCategory.MAINTAINABILITY,
                    title="Large File",
                    message=f"File has {len(non_empty_lines)} lines and may be difficult to maintain",
                    file_path=file_path,
                    line_number=None,
                    timestamp=datetime.now(),
                    suggestions=[
                        "Consider splitting the file into multiple modules",
                        "Extract related functionality into separate files"
                    ],
                    context={'line_count': len(non_empty_lines)}
                ))
            
            # Check comment ratio
            comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
            if non_empty_lines and comment_lines / len(non_empty_lines) < 0.1:
                warning_id = f"low_comments_{file_path.name}"
                warnings.append(ProactiveWarning(
                    id=warning_id,
                    severity=WarningSeverity.INFO,
                    category=WarningCategory.BEST_PRACTICES,
                    title="Low Comment Ratio",
                    message="File has very few comments and may be difficult to understand",
                    file_path=file_path,
                    line_number=None,
                    timestamp=datetime.now(),
                    suggestions=[
                        "Add comments to explain complex logic",
                        "Add docstrings to functions and classes"
                    ],
                    context={'comment_ratio': comment_lines / len(non_empty_lines)}
                ))
                
        except Exception as e:
            self.logger.error(f"Error in meta-analysis: {e}")
        
        return warnings
    
    def _filter_false_positives(self, warnings: List[ProactiveWarning]) -> List[ProactiveWarning]:
        """Filter out known false positives."""
        filtered = []
        
        for warning in warnings:
            # Create pattern key for this warning
            pattern_key = f"{warning.category.value}_{warning.title}_{warning.file_path.suffix}"
            
            # Skip if this pattern is known to be a false positive
            if pattern_key in self.false_positive_patterns:
                continue
            
            filtered.append(warning)
        
        return filtered
    
    def _get_suggestions_for_rule(self, rule_name: str) -> List[str]:
        """Get suggestions for a specific rule."""
        suggestions_map = {
            'hardcoded_credentials': [
                "Move credentials to environment variables",
                "Use a secure configuration management system",
                "Consider using a secrets management service"
            ],
            'sql_injection_risk': [
                "Use parameterized queries",
                "Validate and sanitize user input",
                "Use an ORM with built-in protection"
            ],
            'complex_condition': [
                "Break complex condition into multiple if statements",
                "Extract condition logic into a separate function",
                "Use intermediate variables for readability"
            ],
            'print_statement': [
                "Replace print with logging.info() or logging.debug()",
                "Use structured logging for better debugging",
                "Remove debug print statements before commit"
            ],
            'todo_comment': [
                "Create a ticket or issue for this TODO",
                "Set a deadline for resolving this item",
                "Convert to proper documentation if not actionable"
            ]
        }
        
        return suggestions_map.get(rule_name, ["Review and address this issue"])
    
    def mark_false_positive(self, warning_id: str):
        """Mark a warning as a false positive to prevent future occurrences."""
        try:
            if warning_id in self.active_warnings:
                warning = self.active_warnings[warning_id]
                pattern_key = f"{warning.category.value}_{warning.title}_{warning.file_path.suffix}"
                self.false_positive_patterns.add(pattern_key)
                
                del self.active_warnings[warning_id]
                self.logger.debug(f"Marked warning as false positive: {warning_id}")
        except Exception as e:
            self.logger.error(f"Error marking false positive: {e}")
    
    def resolve_warning(self, warning_id: str):
        """Mark a warning as resolved."""
        try:
            if warning_id in self.active_warnings:
                del self.active_warnings[warning_id]
                self.logger.debug(f"Resolved warning: {warning_id}")
        except Exception as e:
            self.logger.error(f"Error resolving warning: {e}")
    
    def get_active_warnings(self, severity: Optional[WarningSeverity] = None) -> List[ProactiveWarning]:
        """Get currently active warnings, optionally filtered by severity."""
        warnings = list(self.active_warnings.values())
        
        if severity:
            warnings = [w for w in warnings if w.severity == severity]
        
        return sorted(warnings, key=lambda w: (w.severity.value, w.timestamp), reverse=True)
    
    def get_warning_stats(self) -> Dict[str, Any]:
        """Get statistics about warnings."""
        active = list(self.active_warnings.values())
        
        severity_counts = {}
        category_counts = {}
        
        for warning in active:
            severity_counts[warning.severity.value] = severity_counts.get(warning.severity.value, 0) + 1
            category_counts[warning.category.value] = category_counts.get(warning.category.value, 0) + 1
        
        return {
            'total_active': len(active),
            'total_history': len(self.warning_history),
            'severity_distribution': severity_counts,
            'category_distribution': category_counts,
            'false_positive_patterns': len(self.false_positive_patterns),
            'auto_fixable': sum(1 for w in active if w.auto_fixable)
        }