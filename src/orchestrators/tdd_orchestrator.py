"""
TDD Orchestrator - Incremental Test-Driven Development Execution

Implements incremental TDD workflow using IncrementalWorkExecutor protocol.
Breaks TDD cycles into small chunks (1 test, 1 method) with automatic
checkpoints after RED/GREEN/REFACTOR phases.

Part of CORTEX 3.2.1 - Incremental Work Management System
Author: Asif Hussain
"""

import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.orchestrators.base_incremental_orchestrator import (
    IncrementalWorkExecutor,
    WorkChunk,
    WorkCheckpoint
)

logger = logging.getLogger(__name__)


class TDDPhase(Enum):
    """TDD cycle phases"""
    RED = "red"  # Write failing test
    GREEN = "green"  # Implement minimal code to pass
    REFACTOR = "refactor"  # Improve code quality
    COMPLETE = "complete"  # Feature complete


@dataclass
class TDDWorkRequest:
    """
    TDD work request structure.
    
    Attributes:
        feature_name: Name of feature being implemented
        test_file_path: Path to test file
        implementation_file_path: Path to implementation file
        requirements: List of requirements/behaviors to implement
        existing_tests: Number of existing tests in file (for numbering)
        existing_methods: List of existing method names (avoid duplicates)
    """
    feature_name: str
    test_file_path: str
    implementation_file_path: str
    requirements: List[str]
    existing_tests: int = 0
    existing_methods: List[str] = None
    
    def __post_init__(self):
        if self.existing_methods is None:
            self.existing_methods = []


class TDDOrchestrator(IncrementalWorkExecutor):
    """
    TDD Orchestrator with Incremental Execution.
    
    Implements RED→GREEN→REFACTOR cycle as incremental chunks:
    - Each test is a separate chunk (RED phase)
    - Each implementation method is a separate chunk (GREEN phase)
    - Refactoring suggestions are separate chunks (REFACTOR phase)
    - Automatic checkpoints after each phase
    
    Chunk Types:
    - 'test': Individual test method (RED phase)
    - 'method': Individual implementation method (GREEN phase)
    - 'phase': Phase transition checkpoint
    
    Example Workflow for 1 requirement:
    1. Chunk: Write test skeleton (test file creation)
    2. Chunk: Write failing test for requirement (RED)
    3. Checkpoint: Verify test fails
    4. Chunk: Implement minimal method (GREEN)
    5. Checkpoint: Verify test passes
    6. Chunk: Suggest refactoring (REFACTOR)
    7. Checkpoint: Review refactoring suggestions
    """
    
    # TDD-specific constants
    MAX_TEST_TOKENS = 300  # Maximum tokens per test chunk
    MAX_METHOD_TOKENS = 400  # Maximum tokens per method chunk
    
    def __init__(self, brain_path: Optional[Path] = None):
        """
        Initialize TDD orchestrator.
        
        Args:
            brain_path: Path to CORTEX brain directory
        """
        super().__init__(brain_path)
        self.current_phase = TDDPhase.RED
        self.current_requirement_index = 0
        
        # Initialize tier connections for Phase 3 tier feeding
        if brain_path:
            tier1_db = brain_path / "tier1" / "working_memory.db"
            tier2_db = brain_path / "tier2" / "knowledge_graph.db"
            tier3_db = brain_path / "tier3" / "development_context.db"
            
            # Import tier modules
            from src.tier1.working_memory import WorkingMemory
            from src.tier2.knowledge_graph import KnowledgeGraph
            from src.tier3.context_intelligence import ContextIntelligence
            
            # Create tier instances
            tier1_db.parent.mkdir(parents=True, exist_ok=True)
            tier2_db.parent.mkdir(parents=True, exist_ok=True)
            tier3_db.parent.mkdir(parents=True, exist_ok=True)
            
            self.tier1 = WorkingMemory(db_path=tier1_db)
            self.tier2 = KnowledgeGraph(db_path=str(tier2_db))
            self.tier3 = ContextIntelligence(db_path=str(tier3_db))
            self.tier_feeding_enabled = True
        else:
            self.tier1 = None
            self.tier2 = None
            self.tier3 = None
            self.tier_feeding_enabled = False
        
        logger.info("✨ TDD Orchestrator initialized with incremental execution")
    
    def break_into_chunks(self, work_request: Dict[str, Any]) -> List[WorkChunk]:
        """
        Break TDD work into RED→GREEN→REFACTOR chunks.
        
        Chunking Strategy:
        1. File Setup Chunk: Create test file skeleton (if needed)
        2. For each requirement:
           a. RED Chunk: Write one failing test
           b. GREEN Chunk: Implement minimal method to pass test
           c. REFACTOR Chunk: Suggest code improvements
        3. Phase boundaries create automatic checkpoints
        
        Args:
            work_request: Dictionary with TDDWorkRequest structure
        
        Returns:
            List of WorkChunk objects for incremental TDD execution
        """
        try:
            # Parse work request into TDDWorkRequest
            tdd_request = TDDWorkRequest(
                feature_name=work_request.get("feature_name", "Feature"),
                test_file_path=work_request.get("test_file_path", "tests/test_feature.py"),
                implementation_file_path=work_request.get("implementation_file_path", "src/feature.py"),
                requirements=work_request.get("requirements", []),
                existing_tests=work_request.get("existing_tests", 0),
                existing_methods=work_request.get("existing_methods", [])
            )
            
            chunks = []
            chunk_counter = 1
            
            # Chunk 1: Test file skeleton (if new file)
            if tdd_request.existing_tests == 0:
                chunks.append(WorkChunk(
                    chunk_id=f"chunk-{chunk_counter}",
                    chunk_type="skeleton",
                    description=f"Create test file skeleton for {tdd_request.feature_name}",
                    estimated_tokens=150,
                    metadata={
                        "phase": TDDPhase.RED.value,
                        "file_path": tdd_request.test_file_path,
                        "action": "create_skeleton"
                    }
                ))
                chunk_counter += 1
            
            for req_index, requirement in enumerate(tdd_request.requirements, 1):
                test_number = tdd_request.existing_tests + req_index
                
                # RED Phase: Write failing test
                red_chunk_id = f"chunk-{chunk_counter}"
                chunks.append(WorkChunk(
                    chunk_id=red_chunk_id,
                    chunk_type="test",
                    description=f"Write test {test_number}: {requirement[:50]}...",
                    estimated_tokens=self.MAX_TEST_TOKENS,
                    dependencies=[f"chunk-{chunk_counter-1}"] if chunk_counter > 1 else [],
                    metadata={
                        "phase": TDDPhase.RED.value,
                        "requirement": requirement,
                        "test_number": test_number,
                        "file_path": tdd_request.test_file_path,
                        "feature_name": tdd_request.feature_name
                    }
                ))
                chunk_counter += 1
                
                # RED → GREEN checkpoint marker (phase boundary)
                checkpoint_chunk_id = f"chunk-{chunk_counter}"
                chunks.append(WorkChunk(
                    chunk_id=checkpoint_chunk_id,
                    chunk_type="phase",
                    description=f"Checkpoint: Verify test {test_number} fails (RED→GREEN)",
                    estimated_tokens=50,
                    dependencies=[red_chunk_id],
                    metadata={
                        "phase": "checkpoint",
                        "transition": "RED_TO_GREEN",
                        "test_number": test_number
                    }
                ))
                chunk_counter += 1
                
                # GREEN Phase: Implement minimal method
                green_chunk_id = f"chunk-{chunk_counter}"
                chunks.append(WorkChunk(
                    chunk_id=green_chunk_id,
                    chunk_type="method",
                    description=f"Implement method for test {test_number} (minimal GREEN)",
                    estimated_tokens=self.MAX_METHOD_TOKENS,
                    dependencies=[checkpoint_chunk_id],
                    metadata={
                        "phase": TDDPhase.GREEN.value,
                        "requirement": requirement,
                        "test_number": test_number,
                        "file_path": tdd_request.implementation_file_path,
                        "feature_name": tdd_request.feature_name
                    }
                ))
                chunk_counter += 1
                
                # GREEN → REFACTOR checkpoint marker
                checkpoint_chunk_id_2 = f"chunk-{chunk_counter}"
                chunks.append(WorkChunk(
                    chunk_id=checkpoint_chunk_id_2,
                    chunk_type="phase",
                    description=f"Checkpoint: Verify test {test_number} passes (GREEN→REFACTOR)",
                    estimated_tokens=50,
                    dependencies=[green_chunk_id],
                    metadata={
                        "phase": "checkpoint",
                        "transition": "GREEN_TO_REFACTOR",
                        "test_number": test_number
                    }
                ))
                chunk_counter += 1
                
                # REFACTOR Phase: Suggest improvements
                refactor_chunk_id = f"chunk-{chunk_counter}"
                chunks.append(WorkChunk(
                    chunk_id=refactor_chunk_id,
                    chunk_type="section",
                    description=f"Suggest refactoring for test {test_number}",
                    estimated_tokens=200,
                    dependencies=[checkpoint_chunk_id_2],
                    metadata={
                        "phase": TDDPhase.REFACTOR.value,
                        "requirement": requirement,
                        "test_number": test_number,
                        "file_path": tdd_request.implementation_file_path,
                        "feature_name": tdd_request.feature_name
                    }
                ))
                chunk_counter += 1
            
            logger.info(f"📦 TDD workflow broken into {len(chunks)} chunks for {len(tdd_request.requirements)} requirements")
            return chunks
            
        except Exception as e:
            logger.error(f"❌ Failed to break TDD work into chunks: {e}")
            # Return minimal skeleton chunk to allow graceful degradation
            return [
                WorkChunk(
                    chunk_id="chunk-1",
                    chunk_type="skeleton",
                    description="Create basic test structure",
                    estimated_tokens=150,
                    metadata={"phase": "error", "error": str(e)}
                )
            ]
    
    def execute_chunk(self, chunk: WorkChunk) -> Dict[str, Any]:
        """
        Execute a single TDD chunk.
        
        Execution varies by chunk type:
        - skeleton: Create test file structure
        - test: Generate test method (RED)
        - method: Generate implementation method (GREEN)
        - section: Generate refactoring suggestions (REFACTOR)
        - phase: Create checkpoint for user verification
        
        Args:
            chunk: WorkChunk to execute
        
        Returns:
            Execution result dictionary
        """
        try:
            chunk.status = "in-progress"
            
            phase = chunk.metadata.get("phase", "unknown")
            logger.info(f"🔧 Executing {chunk.chunk_type} chunk in {phase.upper()} phase: {chunk.description}")
            
            # Route to appropriate handler based on chunk type
            if chunk.chunk_type == "skeleton":
                output = self._create_test_skeleton(chunk)
            elif chunk.chunk_type == "test":
                output = self._generate_test(chunk)
            elif chunk.chunk_type == "method":
                output = self._generate_method(chunk)
            elif chunk.chunk_type == "section":
                output = self._generate_refactoring(chunk)
            elif chunk.chunk_type == "phase":
                output = self._create_phase_checkpoint(chunk)
            else:
                output = f"# Chunk type '{chunk.chunk_type}' not yet implemented"
            
            chunk.status = "complete"
            
            return {
                "success": True,
                "chunk_id": chunk.chunk_id,
                "output": output,
                "token_count": len(output.split()) * 1.3,  # Approximate token count
                "phase": phase
            }
            
        except Exception as e:
            logger.error(f"❌ Chunk execution failed: {e}")
            chunk.status = "failed"
            return {
                "success": False,
                "chunk_id": chunk.chunk_id,
                "error": str(e),
                "phase": chunk.metadata.get("phase", "unknown")
            }
    
    def _create_test_skeleton(self, chunk: WorkChunk) -> str:
        """Create test file skeleton structure"""
        feature_name = chunk.metadata.get("feature_name", "Feature")
        file_path = chunk.metadata.get("file_path", "test_feature.py")
        
        # Extract class name from file path
        file_stem = Path(file_path).stem.replace("test_", "")
        class_name = "".join(word.title() for word in file_stem.split("_"))
        
        skeleton = f"""# Test file: {file_path}
# Generated by CORTEX TDD Orchestrator

import pytest
from pathlib import Path
import sys

# Add source to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from {file_stem} import {class_name}


class Test{class_name}:
    \"\"\"Test suite for {feature_name}\"\"\"
    
    @pytest.fixture
    def instance(self):
        \"\"\"Create test instance\"\"\"
        return {class_name}()
"""
        return skeleton
    
    def _generate_test(self, chunk: WorkChunk) -> str:
        """Generate individual test method (RED phase)"""
        requirement = chunk.metadata.get("requirement", "Feature requirement")
        test_number = chunk.metadata.get("test_number", 1)
        
        # Phase 3: Feed Tier 1 with test intent during RED phase
        if self.tier_feeding_enabled and self.tier1:
            feature_name = chunk.metadata.get("feature_name", "Unknown Feature")
            self.tier1.store_test_intent(
                feature_name=feature_name,
                requirement=requirement,
                test_phase='RED',
                edge_cases=[requirement],  # Store requirement as edge case
                metadata={
                    'test_number': test_number,
                    'chunk_id': chunk.chunk_id
                }
            )
        
        # Generate test method name from requirement
        method_name = self._requirement_to_test_name(requirement, test_number)
        
        test_code = f"""
    def {method_name}(self, instance):
        \"\"\"
        Test: {requirement}
        
        This test should FAIL initially (RED phase).
        Run pytest to verify failure before implementing.
        \"\"\"
        # Arrange
        
        # Act
        result = None  # Replace with actual method call
        
        # Assert
        assert result is not None, "{requirement}"
"""
        return test_code
    
    def _generate_method(self, chunk: WorkChunk) -> str:
        """Generate implementation method (GREEN phase)"""
        requirement = chunk.metadata.get("requirement", "Feature requirement")
        test_number = chunk.metadata.get("test_number", 1)
        file_path = chunk.metadata.get("file_path", "src/feature.py")
        
        # Phase 3: Feed Tier 2 with implementation pattern during GREEN phase
        if self.tier_feeding_enabled and self.tier2:
            feature_name = chunk.metadata.get("feature_name", "Unknown Feature")
            self.tier2.store_pattern(
                title=f"{feature_name} - Implementation",
                pattern_type='implementation',
                confidence=0.6,
                context={
                    'requirement': requirement,
                    'implementation_approach': 'minimal_then_extend',
                    'dependencies': [],
                    'source': 'tdd_green_phase'
                },
                scope='application',
                namespaces=['tdd', 'implementation']
            )
        
        # Phase 3: Feed Tier 3 with code metrics during GREEN phase
        if self.tier_feeding_enabled and self.tier3:
            # Store initial metrics (simplified - real metrics would use radon or similar)
            self.tier3.store_code_metrics(
                file_path=file_path,
                cyclomatic_complexity=1,  # Minimal implementation = low complexity
                cognitive_complexity=1,
                lines_of_code=10,
                source='tdd_green_phase'
            )
            # Track file as hotspot
            self.tier3.increment_hotspot(file_path)
        
        # Generate method name from requirement
        method_name = self._requirement_to_method_name(requirement)
        
        method_code = f"""
    def {method_name}(self):
        \"\"\"
        {requirement}
        
        Minimal implementation to pass test (GREEN phase).
        Will be refactored in next phase.
        \"\"\"
        return None  # Replace with actual implementation
"""
        return method_code
    
    def _generate_refactoring(self, chunk: WorkChunk) -> str:
        """Generate refactoring suggestions (REFACTOR phase)"""
        requirement = chunk.metadata.get("requirement", "Feature requirement")
        test_number = chunk.metadata.get("test_number", 1)
        file_path = chunk.metadata.get("file_path", "src/feature.py")
        
        # Phase 3: Feed Tier 3 with refactoring improvements during REFACTOR phase
        if self.tier_feeding_enabled and self.tier3:
            # Simulate refactoring - complexity should improve
            before_complexity = 1  # From GREEN phase
            after_complexity = 1   # Minimal change for now
            
            # Store updated metrics after refactoring
            self.tier3.store_code_metrics(
                file_path=file_path,
                cyclomatic_complexity=after_complexity,
                cognitive_complexity=after_complexity,
                lines_of_code=12,  # Slightly more after refactoring comments/docs
                source='tdd_refactor_phase'
            )
        
        suggestions = f"""
## 🔄 Refactoring Suggestions for Test {test_number}

**Requirement:** {requirement}

### Potential Improvements:
1. **Error Handling:** Add validation and error handling
2. **Edge Cases:** Consider boundary conditions
3. **Performance:** Optimize algorithm if needed
4. **Code Quality:** Extract complex logic into helper methods
5. **Documentation:** Add comprehensive docstrings
6. **Type Hints:** Add type annotations for clarity

### Next Steps:
- Review suggestions above
- Apply refactoring while keeping tests green
- Run tests after each change to ensure nothing breaks
"""
        return suggestions
    
    def _create_phase_checkpoint(self, chunk: WorkChunk) -> str:
        """Create checkpoint message for phase transitions"""
        transition = chunk.metadata.get("transition", "UNKNOWN")
        test_number = chunk.metadata.get("test_number", 0)
        
        if transition == "RED_TO_GREEN":
            message = f"""
## 🔴 RED Phase Complete - Test {test_number}

**Action Required:** Run pytest to verify test FAILS

```bash
pytest -xvs tests/test_*.py::*test_{test_number}*
```

**Expected:** Test should FAIL (this confirms we wrote a valid test)

✅ Once verified, respond "test fails" to proceed to GREEN phase
"""
        elif transition == "GREEN_TO_REFACTOR":
            message = f"""
## 🟢 GREEN Phase Complete - Test {test_number}

**Action Required:** Run pytest to verify test PASSES

```bash
pytest -xvs tests/test_*.py::*test_{test_number}*
```

**Expected:** Test should PASS (minimal implementation works)

✅ Once verified, respond "test passes" to proceed to REFACTOR phase
"""
        else:
            message = f"""
## ⚪ Checkpoint - Test {test_number}

**Action Required:** Review code and run tests

✅ Respond "continue" to proceed to next phase
"""
        
        return message
    
    def _requirement_to_test_name(self, requirement: str, test_number: int) -> str:
        """Convert requirement to test method name"""
        # Simplistic conversion - in production, use NLP or LLM
        words = requirement.lower().split()[:5]  # First 5 words
        name = "_".join(w for w in words if w.isalnum())
        return f"test_{test_number}_{name}"
    
    def _requirement_to_method_name(self, requirement: str) -> str:
        """Convert requirement to implementation method name"""
        # Extract action verb from requirement
        words = requirement.lower().split()
        # Find first verb-like word (simple heuristic)
        action = words[0] if words else "process"
        return f"{action}_data"
    
    def _is_checkpoint_boundary(
        self,
        chunk: WorkChunk,
        all_chunks: List[WorkChunk]
    ) -> bool:
        """
        Determine checkpoint boundaries for TDD workflow.
        
        TDD-specific checkpoints:
        - After every phase transition chunk (RED→GREEN, GREEN→REFACTOR)
        - After completing all requirements (final checkpoint)
        
        Args:
            chunk: Current chunk that just completed
            all_chunks: All chunks in the workflow
        
        Returns:
            True if checkpoint should be created
        """
        # Always checkpoint at phase boundaries
        if chunk.chunk_type == "phase":
            return True
        
        # Checkpoint after refactoring (end of TDD cycle for one requirement)
        if chunk.chunk_type == "section" and chunk.metadata.get("phase") == TDDPhase.REFACTOR.value:
            return True
        
        # Checkpoint at the very end
        chunk_index = all_chunks.index(chunk)
        if chunk_index == len(all_chunks) - 1:
            return True
        
        return False

    def disable_tier_feeding(self):
        """Disable tier feeding for performance testing"""
        self.tier_feeding_enabled = False
    
    def enable_tier_feeding(self):
        """Enable tier feeding"""
        self.tier_feeding_enabled = True

