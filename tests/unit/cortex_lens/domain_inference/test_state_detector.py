"""
Tests for State Machine Detector

Validates state machine extraction, transition graph building, and lifecycle detection.

Author: CORTEX Architect
Phase: Phase 66 S3
"""

import pytest
from pathlib import Path
from typing import List, Dict, Any


class TestStateDetector:
    """Test suite for state machine detection"""
    
    def test_state_enum_extraction(self):
        """Test extracting state enum from class definition"""
        from cortex_lens.domain_inference.state_detector import StateDetector
        
        # Mock AST for enum class
        enum_code = '''
class PhaseStatus(Enum):
    PLANNED = "planned"
    ACTIVE = "active"
    COMPLETED = "completed"
    DEPRECATED = "deprecated"
'''
        
        detector = StateDetector()
        states = detector.extract_states_from_enum(enum_code)
        
        assert len(states) == 4
        assert "PLANNED" in states
        assert "ACTIVE" in states
        assert "COMPLETED" in states
        assert "DEPRECATED" in states
    
    def test_state_transition_detection(self):
        """Test detecting state transitions from assignment patterns"""
        from cortex_lens.domain_inference.state_detector import StateDetector
        
        # Mock code with state transitions
        code = '''
def start_phase(phase):
    if phase.status == PhaseStatus.PLANNED:
        phase.status = PhaseStatus.ACTIVE
        
def complete_phase(phase):
    if phase.status == PhaseStatus.ACTIVE:
        phase.status = PhaseStatus.COMPLETED
'''
        
        detector = StateDetector()
        transitions = detector.extract_transitions(code, enum_name="PhaseStatus")
        
        assert len(transitions) >= 2
        assert any(t["from"] == "PLANNED" and t["to"] == "ACTIVE" for t in transitions)
        assert any(t["from"] == "ACTIVE" and t["to"] == "COMPLETED" for t in transitions)
    
    def test_transition_graph_building(self):
        """Test building directed graph from state transitions"""
        from cortex_lens.domain_inference.state_detector import StateDetector
        
        transitions = [
            {"from": "PLANNED", "to": "ACTIVE"},
            {"from": "ACTIVE", "to": "COMPLETED"},
            {"from": "ACTIVE", "to": "DEPRECATED"},
            {"from": "PLANNED", "to": "DEPRECATED"}
        ]
        
        detector = StateDetector()
        graph = detector.build_transition_graph(transitions)
        
        assert "PLANNED" in graph
        assert "ACTIVE" in graph["PLANNED"]
        assert "DEPRECATED" in graph["PLANNED"]
        
        assert "ACTIVE" in graph
        assert "COMPLETED" in graph["ACTIVE"]
        assert "DEPRECATED" in graph["ACTIVE"]
    
    def test_terminal_state_detection(self):
        """Test identifying terminal (final) states"""
        from cortex_lens.domain_inference.state_detector import StateDetector
        
        graph = {
            "PLANNED": ["ACTIVE", "CANCELED"],
            "ACTIVE": ["COMPLETED", "CANCELED"],
            "COMPLETED": [],  # Terminal state
            "CANCELED": []    # Terminal state
        }
        
        detector = StateDetector()
        terminal_states = detector.find_terminal_states(graph)
        
        assert len(terminal_states) == 2
        assert "COMPLETED" in terminal_states
        assert "CANCELED" in terminal_states
    
    def test_initial_state_detection(self):
        """Test identifying initial (entry) states"""
        from cortex_lens.domain_inference.state_detector import StateDetector
        
        graph = {
            "DRAFT": ["PENDING"],
            "PENDING": ["APPROVED", "REJECTED"],
            "APPROVED": ["COMPLETED"],
            "REJECTED": [],
            "COMPLETED": []
        }
        
        detector = StateDetector()
        initial_states = detector.find_initial_states(graph)
        
        assert len(initial_states) == 1
        assert "DRAFT" in initial_states  # No incoming edges
    
    def test_lifecycle_path_extraction(self):
        """Test extracting valid lifecycle paths"""
        from cortex_lens.domain_inference.state_detector import StateDetector
        
        graph = {
            "PLANNED": ["ACTIVE"],
            "ACTIVE": ["COMPLETED", "FAILED"],
            "COMPLETED": [],
            "FAILED": ["RETRY"],
            "RETRY": ["ACTIVE"]
        }
        
        detector = StateDetector()
        paths = detector.extract_lifecycle_paths(graph, start="PLANNED", end="COMPLETED")
        
        assert len(paths) >= 1
        # Main happy path: PLANNED → ACTIVE → COMPLETED
        assert any("PLANNED" in path and "ACTIVE" in path and "COMPLETED" in path for path in paths)
    
    def test_state_machine_validation(self):
        """Test validating state machine for common issues"""
        from cortex_lens.domain_inference.state_detector import StateDetector
        
        # Invalid: unreachable state
        invalid_graph = {
            "START": ["MIDDLE"],
            "MIDDLE": ["END"],
            "END": [],
            "ORPHAN": []  # Unreachable
        }
        
        detector = StateDetector()
        issues = detector.validate_state_machine(invalid_graph)
        
        assert len(issues) > 0
        assert any("unreachable" in issue.lower() or "isolated" in issue.lower() or "orphan" in issue.lower() for issue in issues)
    
    def test_cortex_phase_lifecycle_detection(self):
        """Test detecting CORTEX phase lifecycle states"""
        from cortex_lens.domain_inference.state_detector import StateDetector
        from pathlib import Path
        
        detector = StateDetector()
        
        # Analyze CORTEX models for phase status enum
        models_path = Path("/Users/asifhussain/PROJECTS/CORTEX/cortex/models")
        if models_path.exists():
            # Look for phase status enum
            for py_file in models_path.glob("*.py"):
                content = py_file.read_text()
                if "PhaseStatus" in content or "phase_status" in content:
                    states = detector.extract_states_from_enum(content)
                    
                    if states:
                        assert len(states) >= 2  # At least 2 states expected
                        break
    
    def test_state_confidence_scoring(self):
        """Test confidence scoring for state machine detection"""
        from cortex_lens.domain_inference.state_detector import StateDetector
        
        # Strong signals: clear enum + multiple transitions
        strong_signals = {
            "has_enum": True,
            "transition_count": 5,
            "has_validation": True,
            "naming_clarity": 0.9
        }
        
        detector = StateDetector()
        confidence = detector.calculate_confidence(strong_signals)
        
        assert confidence >= 0.8  # High confidence
        
        # Weak signals: no enum, few transitions
        weak_signals = {
            "has_enum": False,
            "transition_count": 1,
            "has_validation": False,
            "naming_clarity": 0.3
        }
        
        confidence_weak = detector.calculate_confidence(weak_signals)
        assert confidence_weak < 0.5  # Low confidence


class TestStateDetectorIntegration:
    """Integration tests for state detector with knowledge graph"""
    
    def test_state_machine_to_graph(self):
        """Test storing state machine in knowledge graph"""
        from cortex_lens.domain_inference.state_detector import StateDetector
        from cortex_lens.knowledge_graph.graph_storage import GraphStorage
        import tempfile
        
        # Create temporary graph
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = Path(tmp.name)
        
        storage = GraphStorage(db_path)
        storage.initialize_schema()
        
        # Create state machine
        detector = StateDetector()
        transitions = [
            {"from": "PLANNED", "to": "ACTIVE"},
            {"from": "ACTIVE", "to": "COMPLETED"}
        ]
        
        # Store in graph
        state_nodes = {}
        for state in ["PLANNED", "ACTIVE", "COMPLETED"]:
            node_id = storage.insert_node("State", state, {"entity": "Phase"})
            state_nodes[state] = node_id
        
        for trans in transitions:
            storage.insert_edge(
                state_nodes[trans["from"]],
                state_nodes[trans["to"]],
                "transitions_to",
                {}
            )
        
        # Query back
        planned_id = state_nodes["PLANNED"]
        neighbors = storage.query_neighbors(planned_id, edge_type="transitions_to", depth=1)
        
        assert len(neighbors) == 1
        assert neighbors[0]["name"] == "ACTIVE"
        
        # Cleanup
        db_path.unlink()
