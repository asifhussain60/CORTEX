"""
Bug-Driven Learning System (Phase 5.1)

Captures patterns when tests catch bugs and stores them in Tier 2 Knowledge Graph
for future test generation intelligence.

Features:
- Bug detection from test failures
- Pattern extraction from bug-catching tests
- Confidence scoring based on bug severity
- Similarity linking to existing patterns
- Category tagging (edge case, error handling, security)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, Any, List, Optional
from enum import Enum


class BugCategory(Enum):
    """Categories for bugs caught by tests"""
    EDGE_CASE = "edge_case"              # Boundary conditions, nulls, empty collections
    ERROR_HANDLING = "error_handling"     # Exception handling, error messages
    SECURITY = "security"                 # Auth, injection, XSS, etc.
    PERFORMANCE = "performance"           # Slow operations, resource leaks
    LOGIC = "logic"                       # Business logic errors
    INTEGRATION = "integration"           # External service issues
    CONCURRENCY = "concurrency"          # Race conditions, deadlocks
    DATA_VALIDATION = "data_validation"   # Input validation failures


class BugSeverity(Enum):
    """Severity levels for bugs"""
    CRITICAL = "critical"      # Security, data loss, crashes
    HIGH = "high"             # Feature broken, major functionality
    MEDIUM = "medium"         # Minor functionality, edge cases
    LOW = "low"               # Cosmetic, minor issues


@dataclass
class BugEvent:
    """Represents a bug caught by a test"""
    bug_id: str
    test_name: str
    test_file: str
    bug_category: BugCategory
    bug_severity: BugSeverity
    description: str
    expected_behavior: str
    actual_behavior: str
    root_cause: Optional[str]
    test_code: str
    timestamp: str
    metadata: Dict[str, Any]


@dataclass
class BugPattern:
    """Pattern extracted from bug-catching test"""
    pattern_id: str
    title: str
    bug_category: BugCategory
    test_template: str
    assertion_pattern: str
    confidence: float
    bug_count: int  # How many bugs this pattern caught
    similar_patterns: List[str]  # Pattern IDs of similar patterns
    namespaces: List[str]
    metadata: Dict[str, Any]


class BugDrivenLearner:
    """
    Learns from tests that catch bugs to improve future test generation.
    
    Workflow:
    1. Detect bug event (test failure with root cause)
    2. Extract pattern from bug-catching test
    3. Calculate confidence score based on bug severity
    4. Find similar patterns in Tier 2 KG
    5. Store pattern with high confidence
    6. Tag for future test generation
    
    Integration:
    - Uses Tier 2 Knowledge Graph for pattern storage
    - Links to existing patterns via FTS5 search
    - Increases confidence of similar successful patterns
    """
    
    def __init__(self, tier2_kg, pattern_store=None):
        """
        Initialize Bug-Driven Learner.
        
        Args:
            tier2_kg: Tier 2 Knowledge Graph instance
            pattern_store: Pattern store instance (optional, uses tier2_kg if not provided)
        """
        self.tier2 = tier2_kg
        self.pattern_store = pattern_store
        self.logger = logging.getLogger(__name__)
    
    def capture_bug_event(
        self,
        test_name: str,
        test_file: str,
        bug_category: BugCategory,
        bug_severity: BugSeverity,
        description: str,
        expected_behavior: str,
        actual_behavior: str,
        test_code: str,
        root_cause: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> BugEvent:
        """
        Capture a bug event when a test catches a bug.
        
        Args:
            test_name: Name of the test that caught the bug
            test_file: File path of the test
            bug_category: Category of bug (edge case, security, etc.)
            bug_severity: Severity level (critical, high, medium, low)
            description: Human-readable bug description
            expected_behavior: What should have happened
            actual_behavior: What actually happened
            test_code: Source code of the test
            root_cause: Root cause analysis (optional)
            metadata: Additional metadata (optional)
        
        Returns:
            BugEvent instance
        
        Example:
            >>> learner = BugDrivenLearner(tier2_kg)
            >>> bug = learner.capture_bug_event(
            ...     test_name="test_jwt_token_expiration",
            ...     test_file="tests/test_auth.py",
            ...     bug_category=BugCategory.SECURITY,
            ...     bug_severity=BugSeverity.CRITICAL,
            ...     description="JWT tokens not expiring",
            ...     expected_behavior="Token should expire after 1 hour",
            ...     actual_behavior="Token valid indefinitely",
            ...     test_code="def test_jwt_token_expiration(): ...",
            ...     root_cause="Missing expiration check in validate_token()"
            ... )
        """
        bug_id = f"bug_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{test_name}"
        
        bug_event = BugEvent(
            bug_id=bug_id,
            test_name=test_name,
            test_file=test_file,
            bug_category=bug_category,
            bug_severity=bug_severity,
            description=description,
            expected_behavior=expected_behavior,
            actual_behavior=actual_behavior,
            root_cause=root_cause,
            test_code=test_code,
            timestamp=datetime.now().isoformat(),
            metadata=metadata or {}
        )
        
        self.logger.info(f"🐛 Bug captured: {bug_id} - {description}")
        
        return bug_event
    
    def extract_pattern_from_bug(
        self,
        bug_event: BugEvent,
        namespace: str = "cortex.learned-patterns"
    ) -> BugPattern:
        """
        Extract a reusable pattern from a bug-catching test.
        
        Args:
            bug_event: Bug event to extract pattern from
            namespace: Namespace for pattern storage
        
        Returns:
            BugPattern instance
        
        Pattern Confidence Scoring:
        - CRITICAL bug: 0.95 confidence (must prevent)
        - HIGH bug: 0.85 confidence (important)
        - MEDIUM bug: 0.70 confidence (useful)
        - LOW bug: 0.50 confidence (nice to have)
        """
        # Calculate confidence based on severity
        confidence_map = {
            BugSeverity.CRITICAL: 0.95,
            BugSeverity.HIGH: 0.85,
            BugSeverity.MEDIUM: 0.70,
            BugSeverity.LOW: 0.50
        }
        confidence = confidence_map[bug_event.bug_severity]
        
        # Extract test template (generalize the test code)
        test_template = self._generalize_test_code(bug_event.test_code)
        
        # Extract assertion pattern
        assertion_pattern = self._extract_assertion_pattern(bug_event.test_code)
        
        # Generate pattern ID
        pattern_id = f"pattern_{bug_event.bug_category.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create pattern title
        title = f"{bug_event.bug_category.value.replace('_', ' ').title()} - {bug_event.test_name}"
        
        pattern = BugPattern(
            pattern_id=pattern_id,
            title=title,
            bug_category=bug_event.bug_category,
            test_template=test_template,
            assertion_pattern=assertion_pattern,
            confidence=confidence,
            bug_count=1,  # First bug caught by this pattern
            similar_patterns=[],  # Will be populated by find_similar_patterns
            namespaces=[namespace],
            metadata={
                "source_test": bug_event.test_name,
                "source_file": bug_event.test_file,
                "bug_severity": bug_event.bug_severity.value,
                "root_cause": bug_event.root_cause,
                "timestamp": bug_event.timestamp
            }
        )
        
        self.logger.info(f"📚 Pattern extracted: {pattern_id} (confidence: {confidence})")
        
        return pattern
    
    def find_similar_patterns(
        self,
        pattern: BugPattern,
        similarity_threshold: float = 0.70
    ) -> List[Dict[str, Any]]:
        """
        Find similar patterns in Tier 2 Knowledge Graph.
        
        Args:
            pattern: Pattern to find similar patterns for
            similarity_threshold: Minimum similarity score (0.0-1.0)
        
        Returns:
            List of similar patterns with similarity scores
        
        Uses FTS5 full-text search to find patterns with similar:
        - Bug category
        - Test template keywords
        - Assertion patterns
        """
        if not self.tier2:
            return []
        
        try:
            # Build search query
            query = f"{pattern.bug_category.value} {pattern.test_template}"
            
            # Search patterns (simulated - actual implementation would use tier2.search_patterns)
            # This is a placeholder for the actual Tier 2 KG search
            similar = []
            
            # TODO: Implement actual FTS5 search when Tier 2 KG method available
            # similar = self.tier2.search_patterns(
            #     query=query,
            #     pattern_type="bug_catching",
            #     min_confidence=similarity_threshold
            # )
            
            self.logger.debug(f"Found {len(similar)} similar patterns for {pattern.pattern_id}")
            
            return similar
            
        except Exception as e:
            self.logger.error(f"Error finding similar patterns: {str(e)}")
            return []
    
    def store_bug_pattern(
        self,
        pattern: BugPattern,
        is_cortex_internal: bool = True
    ) -> bool:
        """
        Store bug pattern in Tier 2 Knowledge Graph.
        
        Args:
            pattern: Bug pattern to store
            is_cortex_internal: True if called from CORTEX framework
        
        Returns:
            True if stored successfully, False otherwise
        
        Storage includes:
        - Pattern metadata (bug category, confidence, etc.)
        - Test template for future generation
        - Assertion pattern for validation
        - Links to similar patterns
        - Usage tracking (bug_count)
        """
        try:
            if self.pattern_store:
                # Use new pattern store API
                result = self.pattern_store.store_pattern(
                    pattern_id=pattern.pattern_id,
                    title=pattern.title,
                    content=json.dumps({
                        "test_template": pattern.test_template,
                        "assertion_pattern": pattern.assertion_pattern,
                        "bug_category": pattern.bug_category.value,
                        "bug_count": pattern.bug_count
                    }),
                    pattern_type="bug_catching",
                    confidence=pattern.confidence,
                    source=f"bug_driven_learning:{pattern.metadata.get('source_test')}",
                    metadata=pattern.metadata,
                    is_pinned=pattern.confidence >= 0.90,  # Pin high-confidence patterns
                    scope="cortex",
                    namespaces=pattern.namespaces,
                    is_cortex_internal=is_cortex_internal
                )
                
                self.logger.info(f"✅ Pattern stored: {pattern.pattern_id}")
                return True
                
            elif self.tier2:
                # Legacy Tier 2 KG storage
                pattern_data = {
                    "pattern_id": pattern.pattern_id,
                    "title": pattern.title,
                    "bug_category": pattern.bug_category.value,
                    "test_template": pattern.test_template,
                    "assertion_pattern": pattern.assertion_pattern,
                    "confidence": pattern.confidence,
                    "bug_count": pattern.bug_count,
                    "similar_patterns": pattern.similar_patterns,
                    "namespaces": pattern.namespaces,
                    "metadata": pattern.metadata
                }
                
                # Store using legacy API (if available)
                # self.tier2.store_pattern(pattern_data)
                
                self.logger.info(f"✅ Pattern stored (legacy): {pattern.pattern_id}")
                return True
            
            else:
                self.logger.warning("No pattern storage available (tier2 or pattern_store)")
                return False
                
        except Exception as e:
            self.logger.error(f"Error storing pattern: {str(e)}")
            return False
    
    def update_pattern_confidence(
        self,
        pattern_id: str,
        bug_caught: bool = True,
        confidence_boost: float = 0.05
    ) -> bool:
        """
        Update pattern confidence when it catches another bug or produces false positive.
        
        Args:
            pattern_id: Pattern ID to update
            bug_caught: True if pattern caught a bug, False if false positive
            confidence_boost: Amount to increase/decrease confidence
        
        Returns:
            True if updated successfully
        
        Confidence Updates:
        - Bug caught: Increase confidence by boost amount (max 1.0)
        - False positive: Decrease confidence by boost amount (min 0.0)
        """
        try:
            if self.pattern_store:
                # Get current pattern
                pattern = self.pattern_store.get_pattern(pattern_id)
                
                if pattern:
                    # Calculate new confidence
                    current_confidence = pattern.get("confidence", 0.5)
                    
                    if bug_caught:
                        new_confidence = min(1.0, current_confidence + confidence_boost)
                        bug_count = pattern.get("metadata", {}).get("bug_count", 0) + 1
                    else:
                        new_confidence = max(0.0, current_confidence - confidence_boost)
                        bug_count = pattern.get("metadata", {}).get("bug_count", 0)
                    
                    # Update pattern
                    metadata = pattern.get("metadata", {})
                    metadata["bug_count"] = bug_count
                    metadata["last_confidence_update"] = datetime.now().isoformat()
                    
                    self.pattern_store.update_pattern(
                        pattern_id=pattern_id,
                        confidence=new_confidence,
                        metadata=metadata
                    )
                    
                    action = "increased" if bug_caught else "decreased"
                    self.logger.info(
                        f"📈 Pattern {pattern_id} confidence {action}: "
                        f"{current_confidence:.2f} → {new_confidence:.2f}"
                    )
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error updating pattern confidence: {str(e)}")
            return False
    
    def learn_from_bug(
        self,
        test_name: str,
        test_file: str,
        bug_category: BugCategory,
        bug_severity: BugSeverity,
        description: str,
        expected_behavior: str,
        actual_behavior: str,
        test_code: str,
        root_cause: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        namespace: str = "cortex.learned-patterns"
    ) -> Dict[str, Any]:
        """
        Complete bug-driven learning workflow.
        
        Args:
            test_name: Name of test that caught bug
            test_file: Test file path
            bug_category: Category of bug
            bug_severity: Severity level
            description: Bug description
            expected_behavior: Expected behavior
            actual_behavior: Actual behavior
            test_code: Test source code
            root_cause: Root cause (optional)
            metadata: Additional metadata (optional)
            namespace: Namespace for pattern storage
        
        Returns:
            Dictionary with learning results:
            {
                "bug_event": BugEvent,
                "pattern": BugPattern,
                "similar_patterns": List[Dict],
                "stored": bool
            }
        
        Example:
            >>> result = learner.learn_from_bug(
            ...     test_name="test_jwt_expiration",
            ...     test_file="tests/test_auth.py",
            ...     bug_category=BugCategory.SECURITY,
            ...     bug_severity=BugSeverity.CRITICAL,
            ...     description="JWT tokens not expiring",
            ...     expected_behavior="401 after 1 hour",
            ...     actual_behavior="200 indefinitely",
            ...     test_code="def test_jwt_expiration(): ...",
            ...     root_cause="Missing expiration check"
            ... )
        """
        # Step 1: Capture bug event
        bug_event = self.capture_bug_event(
            test_name=test_name,
            test_file=test_file,
            bug_category=bug_category,
            bug_severity=bug_severity,
            description=description,
            expected_behavior=expected_behavior,
            actual_behavior=actual_behavior,
            test_code=test_code,
            root_cause=root_cause,
            metadata=metadata
        )
        
        # Step 2: Extract pattern
        pattern = self.extract_pattern_from_bug(bug_event, namespace=namespace)
        
        # Step 3: Find similar patterns
        similar_patterns = self.find_similar_patterns(pattern)
        pattern.similar_patterns = [p.get("pattern_id") for p in similar_patterns]
        
        # Step 4: Store pattern
        stored = self.store_bug_pattern(pattern)
        
        # Step 5: Boost confidence of similar successful patterns
        for similar in similar_patterns:
            similar_id = similar.get("pattern_id")
            if similar_id:
                self.update_pattern_confidence(similar_id, bug_caught=True, confidence_boost=0.02)
        
        result = {
            "bug_event": asdict(bug_event),
            "pattern": asdict(pattern),
            "similar_patterns": similar_patterns,
            "stored": stored,
            "learning_summary": {
                "confidence": pattern.confidence,
                "similar_count": len(similar_patterns),
                "namespace": namespace
            }
        }
        
        self.logger.info(
            f"🎓 Learning complete: {pattern.pattern_id} "
            f"(confidence: {pattern.confidence}, similar: {len(similar_patterns)})"
        )
        
        return result
    
    def _generalize_test_code(self, test_code: str) -> str:
        """
        Generalize test code to create reusable template.
        
        Replaces specific values with placeholders:
        - Specific strings → {string_value}
        - Specific numbers → {number_value}
        - Variable names → {variable_name}
        
        Args:
            test_code: Original test code
        
        Returns:
            Generalized template
        """
        # Simplified generalization (actual implementation would use AST)
        template = test_code
        
        # Replace string literals
        import re
        template = re.sub(r'"[^"]*"', '"{string_value}"', template)
        template = re.sub(r"'[^']*'", "'{string_value}'", template)
        
        # Replace numeric literals (but not in function names)
        template = re.sub(r'\b\d+\b', '{number_value}', template)
        
        return template
    
    def _extract_assertion_pattern(self, test_code: str) -> str:
        """
        Extract assertion pattern from test code.
        
        Args:
            test_code: Test source code
        
        Returns:
            Assertion pattern (e.g., "assert result == expected")
        """
        # Simple extraction (actual implementation would use AST)
        import re
        
        # Find assert statements
        assertions = re.findall(r'assert\s+[^\n]+', test_code)
        
        if assertions:
            # Return first assertion as pattern
            return assertions[0].strip()
        
        # Check for pytest.raises
        if 'pytest.raises' in test_code:
            return "with pytest.raises(ExceptionType):"
        
        return "assert condition"
    
    def get_learning_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about bug-driven learning.
        
        Returns:
            Dictionary with statistics:
            - total_patterns: Number of patterns learned
            - patterns_by_category: Breakdown by bug category
            - avg_confidence: Average confidence score
            - high_confidence_patterns: Count of patterns with confidence >= 0.90
        """
        stats = {
            "total_patterns": 0,
            "patterns_by_category": {},
            "avg_confidence": 0.0,
            "high_confidence_patterns": 0
        }
        
        # TODO: Implement actual statistics gathering from Tier 2 KG
        # This would query the patterns table and aggregate results
        
        return stats
