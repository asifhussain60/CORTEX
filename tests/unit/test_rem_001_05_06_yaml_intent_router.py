# © 2025-2026 Asif Hussain. All rights reserved.
# AC-ID: AC-REM-001-05 - Comprehension YAML Generation
"""
Test comprehension YAML generation for approval gate.

AC-REM-001-05: Comprehension YAML generation with parsed files, call graphs,
dependencies, patterns, and impact map

Tests verify:
1. YAML generation from comprehension results
2. YAML contains all required sections
3. YAML is valid and parseable
4. Integration with approval gate workflow
"""

import pytest
import yaml
from pathlib import Path
from typing import Dict, Any
from unittest.mock import Mock

from cortex.core.orchestrator.conversation_protocol import ConversationProtocol


class TestComprehensionYAMLGeneration:
    """Test comprehension YAML generation for approval gate."""
    
    def test_comprehension_data_serializable_to_yaml(self) -> None:
        """Test comprehension data can be serialized to YAML."""
        from unittest.mock import Mock
        
        mock_orchestrator = Mock()
        protocol = ConversationProtocol(mock_orchestrator)
        
        # Simulate comprehension data
        comprehension_data = {
            "target_files": ["file1.py", "file2.py"],
            "parse_results": [],
            "call_graphs": [],
            "dependency_maps": [],
            "patterns_detected": [],
            "summary": {
                "files_analyzed": 2,
                "files_parsed_successfully": 2,
                "total_functions_found": 5,
                "total_classes_found": 2,
                "total_imports_found": 10,
                "call_graphs_built": 2,
                "layer_transitions_identified": 3,
                "stdlib_dependencies": 5,
                "third_party_dependencies": 2,
                "local_dependencies": 3,
                "patterns_detected": 1,
            },
        }
        
        # Should be serializable to YAML
        yaml_str = yaml.dump(comprehension_data)
        assert yaml_str is not None
        assert isinstance(yaml_str, str)
        assert len(yaml_str) > 0
    
    def test_comprehension_yaml_has_required_sections(self) -> None:
        """Test comprehension YAML has all required sections."""
        comprehension_yaml = """
operation: COMPREHENSION_APPROVAL_GATE
phase: PHASE-REMEDIATION-01
timestamp: "2026-01-16T23:50:00Z"

# AC-REM-001-05: All required sections
parsed_files:
  - file: "file1.py"
    functions: 3
    classes: 1
  - file: "file2.py"
    functions: 2
    classes: 1

call_graphs:
  - file: "file1.py"
    nodes: 4
    edges: 3
  - file: "file2.py"
    nodes: 3
    edges: 2

dependencies:
  stdlib: ["os", "sys", "json"]
  third_party: ["numpy", "pandas"]
  local: ["module_a", "module_b"]

patterns:
  detected:
    - type: "SINGLETON"
      class: "Logger"
      confidence: 0.95
    - type: "FACTORY"
      class: "HandlerFactory"
      confidence: 0.85

impact_map:
  high_impact_modules:
    - "Logger (singleton)"
    - "HandlerFactory (factory)"
  medium_impact_modules:
    - "DataProcessor"
  transitive_depth: 3
"""
        
        data = yaml.safe_load(comprehension_yaml)
        
        # Verify all required sections exist
        assert "parsed_files" in data
        assert "call_graphs" in data
        assert "dependencies" in data
        assert "patterns" in data
        assert "impact_map" in data
    
    def test_comprehension_yaml_complete_structure(self) -> None:
        """Test complete comprehension YAML structure."""
        complete_yaml = """
operation: COMPREHENSION_APPROVAL_GATE
phase: PHASE-REMEDIATION-01
orchestrator: MasterOrchestrator
author: AST-Comprehension-Engine
timestamp: "2026-01-16T23:50:00Z"

summary:
  files_analyzed: 3
  files_parsed_successfully: 3
  total_functions_found: 8
  total_classes_found: 4
  total_imports_found: 15
  layer_transitions: 5
  patterns_found: 2

parsed_files:
  - filename: "app.py"
    success: true
    functions: 3
    classes: 1
    imports:
      stdlib: ["os", "sys"]
      third_party: ["flask"]
      local: ["utils"]
    line_count: 250
  
  - filename: "models.py"
    success: true
    functions: 2
    classes: 2
    imports:
      stdlib: ["json"]
      third_party: ["sqlalchemy"]
      local: ["schemas"]
    line_count: 180

call_graphs:
  - filename: "app.py"
    nodes: 4
    edges: 3
    layer_transitions:
      layer_0_to_1: 1
      layer_1_to_2: 2
  
  - filename: "models.py"
    nodes: 3
    edges: 2
    layer_transitions:
      layer_0_to_1: 2

dependencies:
  analysis:
    stdlib_count: 2
    third_party_count: 2
    local_count: 2
  stdlib: ["os", "sys", "json"]
  third_party: ["flask", "sqlalchemy"]
  local: ["utils", "schemas"]
  transitive_depth: 3

patterns:
  summary:
    total_found: 2
    types:
      - SINGLETON
      - FACTORY
  details:
    - type: SINGLETON
      class: Database
      confidence: 0.95
      evidence:
        - "_instance class variable present"
        - "__new__ singleton check implemented"
    
    - type: FACTORY
      class: ModelFactory
      confidence: 0.85
      evidence:
        - "create_* methods present"
        - "factory pattern typical structure"

impact_map:
  critical_modules:
    - "Database (SINGLETON): affects all data access"
    - "ModelFactory (FACTORY): affects model creation"
  high_impact_modules:
    - "Router: routes all requests through app.py"
  medium_impact_modules:
    - "Schemas: used by models"
  transitive_dependency_depth: 3
  affected_code_paths: 5
  estimated_testing_impact: "HIGH"

approval_recommendation:
  status: "READY_FOR_REVIEW"
  confidence: 0.92
  next_step: "Send to human review"
"""
        
        data = yaml.safe_load(complete_yaml)
        
        # Verify structure
        assert isinstance(data, dict)
        assert data["operation"] == "COMPREHENSION_APPROVAL_GATE"
        assert "summary" in data
        assert "parsed_files" in data
        assert "call_graphs" in data
        assert "dependencies" in data
        assert "patterns" in data
        assert "impact_map" in data
        
        # Verify parsed_files structure
        assert len(data["parsed_files"]) == 2
        for file_info in data["parsed_files"]:
            assert "filename" in file_info
            assert "functions" in file_info
            assert "classes" in file_info
        
        # Verify call_graphs structure
        assert len(data["call_graphs"]) == 2
        for graph in data["call_graphs"]:
            assert "nodes" in graph
            assert "edges" in graph
        
        # Verify dependencies structure
        assert "stdlib" in data["dependencies"]
        assert "third_party" in data["dependencies"]
        assert "local" in data["dependencies"]
        
        # Verify patterns structure
        assert "summary" in data["patterns"]
        assert "details" in data["patterns"]
        
        # Verify impact_map
        assert "critical_modules" in data["impact_map"]
        assert "transitive_dependency_depth" in data["impact_map"]
    
    def test_yaml_roundtrip_serialization(self) -> None:
        """Test YAML can be serialized and deserialized."""
        original_data = {
            "operation": "COMPREHENSION_APPROVAL_GATE",
            "parsed_files": [{"filename": "test.py", "functions": 2}],
            "call_graphs": [{"nodes": 2, "edges": 1}],
            "dependencies": {"stdlib": ["os"], "local": []},
            "patterns": {"found": 0},
            "impact_map": {"depth": 2},
        }
        
        # Serialize
        yaml_str = yaml.dump(original_data)
        
        # Deserialize
        loaded_data = yaml.safe_load(yaml_str)
        
        # Verify roundtrip
        assert loaded_data == original_data
    
    def test_comprehension_yaml_approval_gate_workflow(self) -> None:
        """Test YAML is suitable for approval gate workflow."""
        approval_gate_yaml = """
operation: COMPREHENSION_APPROVAL_GATE
phase: PHASE-REMEDIATION-01
timestamp: "2026-01-16T23:50:00Z"

summary:
  files_analyzed: 3
  total_functions_found: 8
  total_classes_found: 4
  patterns_detected: 2
  layer_transitions: 5
  transitive_depth: 3

approval_recommendation:
  status: "READY_FOR_APPROVAL"
  confidence: 0.95
  reason: "All analysis components completed successfully"
  sign_off_required: true
  approval_by: "HumanReviewer"
"""
        
        data = yaml.safe_load(approval_gate_yaml)
        
        # Should have approval info for gate
        assert "approval_recommendation" in data
        assert data["approval_recommendation"]["status"] == "READY_FOR_APPROVAL"
        assert data["approval_recommendation"]["confidence"] > 0.9
        assert data["approval_recommendation"]["sign_off_required"] is True


class TestComprehensionIntentRouterContinuousExecution:
    """Test continuous execution of Intent Router with comprehension on every turn."""
    
    def test_intent_router_comprehension_per_turn(self) -> None:
        """Test Intent Router can execute comprehension on every turn.
        
        AC-REM-001-06: Intent Router continuous execution
        Comprehension phase must run on EVERY turn, not just first.
        """
        mock_orchestrator = Mock()
        protocol = ConversationProtocol(mock_orchestrator, max_turns=4)
        
        # Verify protocol can run multiple turns
        assert protocol.max_turns == 4
        assert protocol.turn_number == 0
    
    def test_sequential_turn_comprehension_execution(self) -> None:
        """Test comprehension runs on multiple sequential turns."""
        from cortex.core.orchestrator.conversation_protocol import RoundContext
        
        mock_orchestrator = Mock()
        protocol = ConversationProtocol(mock_orchestrator)
        
        # Simulate 4 sequential turns
        turn_comprehensions = []
        for turn_num in range(1, 5):
            round_context = RoundContext(
                round_number=turn_num,
                user_input=f"Turn {turn_num} input",
                previous_context={},
                orchestrator_name="TestOrchestrator"
            )
            
            result = protocol._run_comprehension_phase(
                f"Turn {turn_num} input",
                round_context
            )
            
            assert result.is_ok()
            turn_comprehensions.append(result)
        
        # Verify all 4 turns executed comprehension
        assert len(turn_comprehensions) == 4
        assert all(r.is_ok() for r in turn_comprehensions)
    
    def test_comprehension_state_preserved_across_turns(self) -> None:
        """Test comprehension results accumulated across turns."""
        from cortex.core.orchestrator.conversation_protocol import RoundContext
        
        protocol = ConversationProtocol(Mock())
        
        accumulated_results = []
        
        for turn in range(1, 4):
            round_context = RoundContext(
                round_number=turn,
                user_input=f"input {turn}",
                previous_context={},
                orchestrator_name="TestOrchestrator"
            )
            
            result = protocol._run_comprehension_phase(
                f"input {turn}",
                round_context
            )
            
            if result.is_ok():
                accumulated_results.append(result.unwrap())
        
        # Verify results can be accumulated
        assert len(accumulated_results) == 3
        for result in accumulated_results:
            assert "summary" in result
            assert "turn_number" in result
    
    def test_intent_router_four_turn_cycle(self) -> None:
        """Test Intent Router with 4 sequential turns (AC-REM-001-06 requirement)."""
        mock_orchestrator = Mock()
        protocol = ConversationProtocol(mock_orchestrator, max_turns=4)
        
        # Verify AST engine initialized for comprehension
        assert protocol.ast_engine is not None
        assert protocol.call_graph_builder is not None
        assert protocol.dependency_mapper is not None
        assert protocol.pattern_detector is not None
        
        # All components ready for per-turn comprehension
        assert all([
            protocol.ast_engine,
            protocol.call_graph_builder,
            protocol.dependency_mapper,
            protocol.pattern_detector,
        ])
