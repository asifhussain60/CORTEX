"""
Failure Analyzer for CI/CD Self-Healing

Analyzes build failures using pattern matching and LLM integration.

Author: Asif Hussain
Version: 1.0
"""

import logging
import re
import time
from typing import List, Dict, Any, Optional

from .schemas import FailureCategory, FailureAnalysis, FixStrategy


class FailureAnalyzer:
    """
    Analyzes build failures to determine root cause and suggest fixes.
    
    Uses pattern matching for known issues and LLM for complex analysis.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None, use_llm: bool = True):
        """
        Initialize failure analyzer.
        
        Args:
            logger: Optional logger instance
            use_llm: Whether to use LLM for advanced analysis
        """
        self.logger = logger or logging.getLogger(__name__)
        self.use_llm = use_llm
        
        # Pattern matchers for known issues
        self._init_patterns()
    
    def _init_patterns(self) -> None:
        """Initialize regex patterns for known failure types"""
        self.patterns = {
            FailureCategory.DEPENDENCY_CONFLICT: [
                r"Could not resolve dependencies",
                r"CONFLICT.*dependency",
                r"version conflict",
                r"incompatible version",
                r"npm ERR.*peer dep",
                r"pip.*VersionConflict",
            ],
            FailureCategory.TEST_FAILURE: [
                r"(\d+) test[s]? failed",
                r"AssertionError",
                r"Test.*FAILED",
                r"FAIL:.*test_",
                r"✗.*test",
                r"Expected.*but got",
            ],
            FailureCategory.CONFIGURATION_ERROR: [
                r"missing.*environment variable",
                r"configuration.*not found",
                r"Invalid configuration",
                r"Config.*error",
                r"Missing required.*config",
            ],
            FailureCategory.SYNTAX_ERROR: [
                r"SyntaxError:",
                r"syntax error",
                r"unexpected token",
                r"ParseError",
                r"IndentationError",
                r"linting.*failed",
            ],
            FailureCategory.SECURITY_ISSUE: [
                r"security vulnerability",
                r"CVE-\d{4}-\d+",
                r"vulnerable package",
                r"security audit.*failed",
                r"high severity",
            ],
            FailureCategory.TIMEOUT: [
                r"timeout",
                r"timed out",
                r"exceeded.*time limit",
                r"operation.*too long",
            ],
            FailureCategory.RESOURCE_LIMIT: [
                r"out of memory",
                r"OOM",
                r"resource limit",
                r"disk space",
                r"quota exceeded",
            ],
        }
    
    async def analyze(self, build_log, context: Dict[str, Any]) -> FailureAnalysis:
        """
        Analyze build failure from log.
        
        Args:
            build_log: Build log content (str or list of strings)
            context: Analysis context
            
        Returns:
            FailureAnalysis with root cause and suggested fixes
        """
        start_time = time.time()
        
        self.logger.info(f"🔍 Analyzing failure for run: {context}")
        
        # Normalize build_log to string
        if isinstance(build_log, list):
            build_log = "\n".join(build_log)
        
        # Extract error messages
        error_messages = self._extract_errors(build_log)
        
        # Pattern-based classification
        category, confidence, matches = self._classify_by_patterns(build_log)
        
        # Extract affected files and dependencies
        affected_files = self._extract_affected_files(build_log)
        affected_deps = self._extract_dependencies(build_log)
        
        # Determine root cause
        root_cause = self._determine_root_cause(category, matches, error_messages)
        
        # LLM-based analysis for low confidence or unknown category
        if (confidence < 0.7 or category == FailureCategory.UNKNOWN) and self.use_llm:
            llm_result = await self._llm_analyze(build_log, error_messages)
            if llm_result:
                category = llm_result["category"]
                root_cause = llm_result["root_cause"]
                confidence = llm_result["confidence"]
        
        # Suggest fixes based on category
        suggested_fixes = self._suggest_fixes(category, root_cause, affected_deps)
        
        # Determine if auto-fixable
        auto_fixable = self._is_auto_fixable(category, confidence)
        requires_human = confidence < 0.5 or category == FailureCategory.UNKNOWN
        
        analysis_time_ms = (time.time() - start_time) * 1000
        
        self.logger.info(
            f"✅ Analysis complete: {category.value} "
            f"(confidence={confidence:.2f}, auto_fixable={auto_fixable})"
        )
        
        return FailureAnalysis(
            category=category,
            root_cause=root_cause,
            confidence=confidence,
            affected_files=affected_files,
            affected_dependencies=affected_deps,
            error_messages=error_messages[:10],  # Limit to 10
            suggested_fixes=suggested_fixes,
            auto_fixable=auto_fixable,
            requires_human=requires_human,
            analysis_time_ms=analysis_time_ms
        )
    
    def _extract_errors(self, log: str) -> List[str]:
        """Extract error messages from log"""
        errors = []
        for line in log.split("\n"):
            lower_line = line.lower()
            if any(keyword in lower_line for keyword in ["error", "failed", "failure"]):
                errors.append(line.strip())
        
        return errors[:20]  # Limit to 20
    
    def _classify_by_patterns(self, log: str) -> tuple:
        """
        Classify failure using regex patterns.
        
        Returns:
            (category, confidence, matching_patterns)
        """
        matches_by_category = {}
        
        for category, patterns in self.patterns.items():
            matches = []
            for pattern in patterns:
                if re.search(pattern, log, re.IGNORECASE):
                    matches.append(pattern)
            
            if matches:
                matches_by_category[category] = matches
        
        if not matches_by_category:
            return FailureCategory.UNKNOWN, 0.3, []
        
        # Category with most matches wins
        best_category = max(matches_by_category, key=lambda k: len(matches_by_category[k]))
        match_count = len(matches_by_category[best_category])
        
        # Confidence based on match count
        confidence = min(0.6 + (match_count * 0.1), 0.95)
        
        return best_category, confidence, matches_by_category[best_category]
    
    def _extract_affected_files(self, log: str) -> List[str]:
        """Extract file paths from log"""
        files = []
        
        # Common file path patterns
        patterns = [
            r"(?:File|at)\s+\"?([^\s\"]+\.[a-z]{2,4})\"?",
            r"([a-zA-Z0-9_/\\]+\.[a-z]{2,4}):\d+",
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, log)
            files.extend(matches)
        
        # Remove duplicates and system files
        files = list(set(f for f in files if not f.startswith("/usr") and not f.startswith("C:\\")))
        
        return files[:20]  # Limit to 20
    
    def _extract_dependencies(self, log: str) -> List[str]:
        """Extract dependency names from log"""
        deps = []
        
        # Dependency name patterns
        patterns = [
            r"(?:package|module|dependency)\s+['\"]?([a-zA-Z0-9_-]+)['\"]?",
            r"npm install\s+([a-zA-Z0-9_-]+)",
            r"pip install\s+([a-zA-Z0-9_-]+)",
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, log, re.IGNORECASE)
            deps.extend(matches)
        
        return list(set(deps))[:15]  # Limit to 15
    
    def _determine_root_cause(
        self,
        category: FailureCategory,
        matches: List[str],
        errors: List[str]
    ) -> str:
        """Determine root cause description"""
        if category == FailureCategory.DEPENDENCY_CONFLICT:
            return "Dependency version conflict detected"
        elif category == FailureCategory.TEST_FAILURE:
            return "One or more tests failed during execution"
        elif category == FailureCategory.CONFIGURATION_ERROR:
            return "Configuration error or missing required settings"
        elif category == FailureCategory.SYNTAX_ERROR:
            return "Syntax or linting errors in code"
        elif category == FailureCategory.SECURITY_ISSUE:
            return "Security vulnerability detected in dependencies"
        elif category == FailureCategory.TIMEOUT:
            return "Operation exceeded time limit"
        elif category == FailureCategory.RESOURCE_LIMIT:
            return "Resource limit exceeded (memory, disk space, etc.)"
        else:
            return "Unknown failure - manual investigation required"
    
    def _suggest_fixes(
        self,
        category: FailureCategory,
        root_cause: str,
        dependencies: List[str]
    ) -> List[FixStrategy]:
        """Suggest fix strategies based on failure category"""
        fixes = []
        
        if category == FailureCategory.DEPENDENCY_CONFLICT:
            fixes.extend([
                FixStrategy.DEPENDENCY_UPDATE,
                FixStrategy.DEPENDENCY_ROLLBACK
            ])
        
        elif category == FailureCategory.TEST_FAILURE:
            fixes.extend([
                FixStrategy.TEST_RETRY,
                FixStrategy.TEST_ISOLATION
            ])
        
        elif category == FailureCategory.CONFIGURATION_ERROR:
            fixes.extend([
                FixStrategy.CONFIG_FIX,
                FixStrategy.ENV_VAR_ADD
            ])
        
        elif category == FailureCategory.SYNTAX_ERROR:
            fixes.append(FixStrategy.CODE_FIX)
        
        elif category == FailureCategory.TIMEOUT:
            fixes.append(FixStrategy.TIMEOUT_INCREASE)
        
        elif category == FailureCategory.RESOURCE_LIMIT:
            fixes.append(FixStrategy.RESOURCE_INCREASE)
        
        elif category == FailureCategory.SECURITY_ISSUE:
            fixes.extend([
                FixStrategy.DEPENDENCY_UPDATE,
                FixStrategy.MANUAL_INTERVENTION
            ])
        
        else:
            fixes.append(FixStrategy.MANUAL_INTERVENTION)
        
        return fixes
    
    def _is_auto_fixable(self, category: FailureCategory, confidence: float) -> bool:
        """Determine if failure can be auto-fixed"""
        # High confidence required for auto-fix
        if confidence < 0.6:
            return False
        
        # Only certain categories are auto-fixable
        auto_fixable_categories = {
            FailureCategory.DEPENDENCY_CONFLICT,
            FailureCategory.TEST_FAILURE,
            FailureCategory.CONFIGURATION_ERROR,
            FailureCategory.TIMEOUT,
        }
        
        return category in auto_fixable_categories
    
    async def _llm_analyze(
        self,
        log: str,
        error_messages: List[str]
    ) -> Optional[Dict[str, Any]]:
        """
        Use LLM for advanced failure analysis.
        
        Args:
            log: Full build log
            error_messages: Extracted error messages
            
        Returns:
            Dict with category, root_cause, confidence (or None if LLM unavailable)
        """
        # TODO: Integrate with Phase 5 LLM infrastructure
        # For now, return None (pattern-based analysis only)
        self.logger.debug("LLM analysis not yet implemented")
        return None
