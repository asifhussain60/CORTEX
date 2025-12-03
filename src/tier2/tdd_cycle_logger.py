"""
TDD Cycle Logger - Capture patterns from TDD workflow cycles

Logs patterns from:
- RED phase: Test-first development (failing tests)
- GREEN phase: Minimal implementation (passing tests)
- REFACTOR phase: Code cleanup (tests still passing)

Integrates with Phase 3 TDD workflow for automatic pattern learning.

Author: Asif Hussain
"""

import hashlib
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path


class TDDCycleLogger:
    """Log and link TDD cycle patterns for learning"""
    
    def __init__(self, knowledge_graph):
        """
        Initialize TDD cycle logger
        
        Args:
            knowledge_graph: Tier 2 KnowledgeGraph instance
        """
        self.knowledge_graph = knowledge_graph
    
    def log_red_phase(
        self,
        test_file: str,
        test_name: str,
        test_content: str,
        intent: str
    ) -> str:
        """
        Log RED phase pattern (test-first)
        
        Args:
            test_file: Path to test file
            test_name: Name of test function/method
            test_content: Test code content
            intent: Purpose of the test
            
        Returns:
            Pattern ID
        """
        # Generate pattern ID
        pattern_id = self._generate_pattern_id("red", test_file, test_name)
        
        metadata = {
            'test_file': test_file,
            'test_name': test_name,
            'intent': intent,
            'phase': 'RED',
            'timestamp': datetime.now().isoformat()
        }
        
        result = self.knowledge_graph.store_pattern(
            pattern_id=pattern_id,
            title=f"RED: {test_name}",
            content=test_content,
            pattern_type="workflow",  # Use valid pattern_type
            confidence=0.8,
            metadata=metadata,
            namespaces=["tdd", "red-phase", "test-first"]
        )
        
        return result.get('pattern_id', pattern_id)
    
    def log_green_phase(
        self,
        impl_file: str,
        impl_content: str,
        test_file: str,
        test_passed: bool
    ) -> str:
        """
        Log GREEN phase pattern (implementation)
        
        Args:
            impl_file: Path to implementation file
            impl_content: Implementation code
            test_file: Related test file
            test_passed: Whether test passed after implementation
            
        Returns:
            Pattern ID
        """
        # Generate pattern ID
        pattern_id = self._generate_pattern_id("green", impl_file, test_file)
        
        metadata = {
            'impl_file': impl_file,
            'test_file': test_file,
            'test_passed': test_passed,
            'phase': 'GREEN',
            'timestamp': datetime.now().isoformat()
        }
        
        # Higher confidence if test passed
        confidence = 0.9 if test_passed else 0.5
        
        result = self.knowledge_graph.store_pattern(
            pattern_id=pattern_id,
            title=f"GREEN: {Path(impl_file).stem} implementation",
            content=impl_content,
            pattern_type="solution",  # Use valid pattern_type
            confidence=confidence,
            metadata=metadata,
            namespaces=["tdd", "green-phase", "implementation"]
        )
        
        return result.get('pattern_id', pattern_id)
    
    def log_refactor_phase(
        self,
        file_path: str,
        before_code: str,
        after_code: str,
        refactor_type: str,
        tests_still_passing: bool
    ) -> str:
        """
        Log REFACTOR phase pattern (code cleanup)
        
        Args:
            file_path: Path to refactored file
            before_code: Code before refactoring
            after_code: Code after refactoring
            refactor_type: Type of refactoring (extract_method, rename, etc.)
            tests_still_passing: Whether tests still pass after refactor
            
        Returns:
            Pattern ID
        """
        # Generate pattern ID
        pattern_id = self._generate_pattern_id("refactor", file_path, refactor_type)
        
        metadata = {
            'file_path': file_path,
            'refactor_type': refactor_type,
            'tests_still_passing': tests_still_passing,
            'before_code': before_code,
            'after_code': after_code,
            'phase': 'REFACTOR',
            'timestamp': datetime.now().isoformat()
        }
        
        # Build content showing the transformation
        content = f"Refactoring: {refactor_type}\n\nBefore:\n{before_code}\n\nAfter:\n{after_code}"
        
        # Higher confidence if tests still pass
        confidence = 0.85 if tests_still_passing else 0.4
        
        result = self.knowledge_graph.store_pattern(
            pattern_id=pattern_id,
            title=f"REFACTOR: {refactor_type} in {Path(file_path).name}",
            content=content,
            pattern_type="principle",  # Use valid pattern_type
            confidence=confidence,
            metadata=metadata,
            namespaces=["tdd", "refactor-phase", refactor_type]
        )
        
        return result.get('pattern_id', pattern_id)
    
    def link_cycle(
        self,
        red_pattern_id: str,
        green_pattern_id: str,
        refactor_pattern_id: Optional[str] = None,
        refactor_id: Optional[str] = None  # Alias for backward compatibility
    ) -> str:
        """
        Link RED→GREEN→REFACTOR patterns into complete TDD cycle
        
        Args:
            red_pattern_id: RED phase pattern ID
            green_pattern_id: GREEN phase pattern ID
            refactor_pattern_id: Optional REFACTOR phase pattern ID
            refactor_id: Alias for refactor_pattern_id (backward compatibility)
            
        Returns:
            Cycle pattern ID
        """
        # Support both parameter names
        if refactor_id is not None:
            refactor_pattern_id = refactor_id
        
        # Generate cycle ID
        cycle_id = self._generate_pattern_id("cycle", red_pattern_id, green_pattern_id)
        
        metadata = {
            'red_pattern_id': red_pattern_id,
            'green_pattern_id': green_pattern_id,
            'refactor_pattern_id': refactor_pattern_id,
            'cycle_type': 'RED→GREEN→REFACTOR' if refactor_pattern_id else 'RED→GREEN',
            'timestamp': datetime.now().isoformat()
        }
        
        # Get phase patterns for summary
        red_pattern = self.knowledge_graph.get_pattern(red_pattern_id)
        green_pattern = self.knowledge_graph.get_pattern(green_pattern_id)
        
        title = f"TDD Cycle: {red_pattern.get('title', 'Unknown')} → Implementation"
        
        content = f"""Complete TDD Cycle:
RED: {red_pattern.get('title', 'Test')}
GREEN: {green_pattern.get('title', 'Implementation')}
{"REFACTOR: Applied" if refactor_pattern_id else ""}"""
        
        result = self.knowledge_graph.store_pattern(
            pattern_id=cycle_id,
            title=title,
            content=content,
            pattern_type="workflow",  # Use valid pattern_type
            confidence=0.95,
            metadata=metadata,
            namespaces=["tdd", "complete-cycle", "workflow"]
        )
        
        return result.get('pattern_id', cycle_id)
    
    def _generate_pattern_id(self, phase: str, *components: str) -> str:
        """Generate pattern ID from phase and components"""
        data = f"{phase}_{'_'.join(components)}"
        hash_suffix = hashlib.md5(data.encode()).hexdigest()[:12]
        return f"tdd_{phase}_{hash_suffix}"
