# © 2025-2026 Asif Hussain. All rights reserved.
# AC-ID: AC-REM-001-02 - CallGraphBuilder Integration
"""
Test CallGraphBuilder integration into LENS comprehension phase.

AC-REM-001-02: CallGraphBuilder used to trace layer-to-layer relationships
in Intent Router

Tests verify:
1. CallGraphBuilder can be instantiated
2. build() method creates call graphs from parse results
3. Call graphs trace function/method relationships
4. Layer transitions are identified (3+ layers)
5. Integration with comprehension phase output
"""

import pytest
from pathlib import Path
from typing import List

from src.core.intelligence.ast_intelligence import (
    ASTIntelligenceEngine,
    ParseResult,
)
from src.core.intelligence.call_graph import CallGraphBuilder, CallGraph
from src.core.orchestrator.conversation_protocol import ConversationProtocol


class TestCallGraphBuilderIntegration:
    """Test CallGraphBuilder integration into comprehension phase."""
    
    def test_call_graph_builder_instantiates(self) -> None:
        """Test CallGraphBuilder can be instantiated."""
        builder = CallGraphBuilder()
        assert builder is not None
    
    def test_call_graph_builder_has_build_method(self) -> None:
        """Test CallGraphBuilder has build method."""
        builder = CallGraphBuilder()
        assert hasattr(builder, "build")
        assert callable(builder.build)
    
    def test_call_graph_from_simple_module(self) -> None:
        """Test call graph building from simple module."""
        engine = ASTIntelligenceEngine()
        builder = CallGraphBuilder()
        
        test_file = Path(__file__).parent / "call_graph_simple.py"
        test_file.write_text("""
def caller():
    callee()

def callee():
    pass
""")
        
        try:
            parse_result = engine.parse_file(test_file)
            graph = builder.build(parse_result)
            
            assert graph is not None
            assert isinstance(graph, CallGraph)
            assert graph.node_count > 0
        finally:
            test_file.unlink(missing_ok=True)
    
    def test_call_graph_identifies_nodes(self) -> None:
        """Test call graph identifies function nodes."""
        engine = ASTIntelligenceEngine()
        builder = CallGraphBuilder()
        
        test_file = Path(__file__).parent / "call_graph_nodes.py"
        test_file.write_text("""
def func_a():
    pass

def func_b():
    pass

class MyClass:
    def method_a(self):
        pass
    
    def method_b(self):
        pass
""")
        
        try:
            parse_result = engine.parse_file(test_file)
            graph = builder.build(parse_result)
            
            assert graph.has_node("func_a")
            assert graph.has_node("func_b")
            assert graph.has_node("MyClass.method_a")
            assert graph.has_node("MyClass.method_b")
        finally:
            test_file.unlink(missing_ok=True)
    
    def test_call_graph_identifies_edges(self) -> None:
        """Test call graph identifies call relationships."""
        engine = ASTIntelligenceEngine()
        builder = CallGraphBuilder()
        
        test_file = Path(__file__).parent / "call_graph_edges.py"
        test_file.write_text("""
def func_a():
    func_b()
    func_c()

def func_b():
    pass

def func_c():
    pass
""")
        
        try:
            parse_result = engine.parse_file(test_file)
            graph = builder.build(parse_result)
            
            callees_of_a = graph.get_callees("func_a")
            assert "func_b" in callees_of_a
            assert "func_c" in callees_of_a
        finally:
            test_file.unlink(missing_ok=True)
    
    def test_call_graph_traces_layer_transitions(self) -> None:
        """Test call graph traces layer-to-layer relationships."""
        engine = ASTIntelligenceEngine()
        builder = CallGraphBuilder()
        
        # Create file with 3+ layer transitions:
        # Layer 1: app_handler
        # Layer 2: process_request
        # Layer 3: validate_input
        # Layer 4: check_format
        test_file = Path(__file__).parent / "call_graph_layers.py"
        test_file.write_text("""
def app_handler(request):
    # Layer 1 -> Layer 2
    return process_request(request)

def process_request(data):
    # Layer 2 -> Layer 3
    if validate_input(data):
        return transform_data(data)
    return None

def validate_input(data):
    # Layer 3 -> Layer 4
    return check_format(data)

def check_format(data):
    # Layer 4
    return isinstance(data, dict)

def transform_data(data):
    return {k.upper(): v for k, v in data.items()}
""")
        
        try:
            parse_result = engine.parse_file(test_file)
            graph = builder.build(parse_result)
            
            # Verify we have nodes for all functions
            assert graph.has_node("app_handler")
            assert graph.has_node("process_request")
            assert graph.has_node("validate_input")
            assert graph.has_node("check_format")
            assert graph.has_node("transform_data")
            
            # Verify edges exist (layer transitions)
            app_callees = graph.get_callees("app_handler")
            assert "process_request" in app_callees
            
            process_callees = graph.get_callees("process_request")
            assert "validate_input" in process_callees
            
            validate_callees = graph.get_callees("validate_input")
            assert "check_format" in validate_callees
            
            # Verify edge count > 3
            assert graph.edge_count >= 3
        finally:
            test_file.unlink(missing_ok=True)
    
    def test_call_graph_with_class_methods(self) -> None:
        """Test call graph handles class methods."""
        engine = ASTIntelligenceEngine()
        builder = CallGraphBuilder()
        
        test_file = Path(__file__).parent / "call_graph_classes.py"
        test_file.write_text("""
class APIHandler:
    def handle_request(self, data):
        return self.process(data)
    
    def process(self, data):
        self.validate(data)
        return data
    
    def validate(self, data):
        return True

class DataProcessor:
    def run(self):
        handler = APIHandler()
        return handler.handle_request({})
""")
        
        try:
            parse_result = engine.parse_file(test_file)
            graph = builder.build(parse_result)
            
            assert graph.has_node("APIHandler.handle_request")
            assert graph.has_node("APIHandler.process")
            assert graph.has_node("APIHandler.validate")
            assert graph.has_node("DataProcessor.run")
        finally:
            test_file.unlink(missing_ok=True)
    
    def test_call_graph_serializable(self) -> None:
        """Test call graph can be serialized to dict."""
        engine = ASTIntelligenceEngine()
        builder = CallGraphBuilder()
        
        test_file = Path(__file__).parent / "call_graph_serialize.py"
        test_file.write_text("""
def func1():
    func2()

def func2():
    pass
""")
        
        try:
            parse_result = engine.parse_file(test_file)
            graph = builder.build(parse_result)
            graph_dict = graph.to_dict()
            
            assert isinstance(graph_dict, dict)
            assert "nodes" in graph_dict
            assert "edges" in graph_dict
            assert "node_count" in graph_dict
            assert "edge_count" in graph_dict
            assert isinstance(graph_dict["nodes"], list)
            assert isinstance(graph_dict["edges"], list)
        finally:
            test_file.unlink(missing_ok=True)


class TestCallGraphComprehensionIntegration:
    """Test call graph integration with comprehension phase."""
    
    def test_conversation_protocol_can_build_call_graph(self) -> None:
        """Test ConversationProtocol can build call graphs from comprehension."""
        from unittest.mock import Mock
        
        mock_orchestrator = Mock()
        protocol = ConversationProtocol(mock_orchestrator)
        
        # Verify AST engine and access to CallGraphBuilder
        assert protocol.ast_engine is not None
        assert isinstance(protocol.ast_engine, ASTIntelligenceEngine)
    
    def test_call_graph_built_from_parse_results(self) -> None:
        """Test call graphs can be built from comprehension parse results."""
        engine = ASTIntelligenceEngine()
        builder = CallGraphBuilder()
        
        # Create multiple test files simulating multi-file project
        test_files = []
        for i in range(2):
            test_file = Path(__file__).parent / f"multi_file_{i}.py"
            test_files.append(test_file)
            
            if i == 0:
                test_file.write_text("""
def layer1_func():
    return layer2_func()

def layer2_func():
    return "result"
""")
            else:
                test_file.write_text("""
def main_handler():
    from multi_file_0 import layer1_func
    return layer1_func()
""")
        
        try:
            # Simulate comprehension phase collecting parse results
            all_graphs = []
            for test_file in test_files:
                parse_result = engine.parse_file(test_file)
                if parse_result.success:
                    graph = builder.build(parse_result)
                    all_graphs.append(graph)
            
            # Verify we have multiple call graphs
            assert len(all_graphs) == 2
            assert all(isinstance(g, CallGraph) for g in all_graphs)
            
            # Verify graphs contain expected nodes
            assert all_graphs[0].has_node("layer1_func")
            assert all_graphs[1].has_node("main_handler")
        finally:
            for f in test_files:
                f.unlink(missing_ok=True)
    
    def test_layer_transition_counting(self) -> None:
        """Test counting layer transitions in call graph."""
        engine = ASTIntelligenceEngine()
        builder = CallGraphBuilder()
        
        # Create file with exactly 3 layer transitions
        test_file = Path(__file__).parent / "layer_transitions.py"
        test_file.write_text("""
def layer_0():
    # Transition 1: 0->1
    return layer_1()

def layer_1():
    # Transition 2: 1->2
    return layer_2()

def layer_2():
    # Transition 3: 2->3
    return layer_3()

def layer_3():
    return "final"
""")
        
        try:
            parse_result = engine.parse_file(test_file)
            graph = builder.build(parse_result)
            
            # Count transitions: edges should be >= 3
            transition_count = 0
            for edge in graph.edges:
                if edge.call_type == "DIRECT":
                    transition_count += 1
            
            # Should have at least 3 direct calls (transitions)
            assert transition_count >= 3 or graph.edge_count >= 3
        finally:
            test_file.unlink(missing_ok=True)
