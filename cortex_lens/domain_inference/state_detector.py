"""
State Machine Detector

Detects state machines, extracts transitions, and builds lifecycle graphs.

Author: CORTEX Architect
Phase: Phase 66 S3
"""

import logging
import re
import ast
from typing import List, Dict, Set, Any, Optional, Tuple
from collections import defaultdict

logger = logging.getLogger(__name__)


class StateDetector:
    """
    Detects state machines and state transitions in code.
    
    Capabilities:
    - Extract states from Enum classes
    - Detect state transitions from assignment patterns
    - Build directed transition graphs
    - Identify initial and terminal states
    - Extract valid lifecycle paths
    - Validate state machines for common issues
    
    Example:
        detector = StateDetector()
        
        # Extract states from enum
        states = detector.extract_states_from_enum(enum_code)
        # Returns: ["PLANNED", "ACTIVE", "COMPLETED"]
        
        # Build transition graph
        transitions = [{"from": "PLANNED", "to": "ACTIVE"}, ...]
        graph = detector.build_transition_graph(transitions)
        # Returns: {"PLANNED": ["ACTIVE"], "ACTIVE": ["COMPLETED"]}
    """
    
    def __init__(self):
        """Initialize state detector"""
        self.state_patterns = [
            r'class\s+(\w+Status)\s*\(',  # FooStatus enum
            r'class\s+(\w+State)\s*\(',   # FooState enum
            r'(\w+)\.status\s*=',          # foo.status = assignment
            r'state\s*=\s*["\'](\w+)["\']'  # state = "value"
        ]
        logger.debug("Initialized StateDetector")
    
    def extract_states_from_enum(self, code: str) -> List[str]:
        """
        Extract state values from Enum class definition.
        
        Args:
            code: Python code containing Enum class
        
        Returns:
            List of state names
        
        Example:
            code = '''
            class Status(Enum):
                PENDING = "pending"
                ACTIVE = "active"
            '''
            Returns: ["PENDING", "ACTIVE"]
        """
        logger.debug("Extracting states from enum")
        
        states = []
        
        try:
            # Parse code to AST
            tree = ast.parse(code)
            
            # Find Enum class definitions
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check if inherits from Enum
                    is_enum = any(
                        (isinstance(base, ast.Name) and base.id == "Enum") or
                        (isinstance(base, ast.Attribute) and base.attr == "Enum")
                        for base in node.bases
                    )
                    
                    if is_enum or "Status" in node.name or "State" in node.name:
                        # Extract member names
                        for item in node.body:
                            if isinstance(item, ast.Assign):
                                for target in item.targets:
                                    if isinstance(target, ast.Name):
                                        # Skip private members
                                        if not target.id.startswith("_"):
                                            states.append(target.id)
        
        except SyntaxError as e:
            logger.warning(f"Failed to parse code: {e}")
            
            # Fallback: regex extraction
            pattern = r'^\s*([A-Z_]+)\s*='
            states = re.findall(pattern, code, re.MULTILINE)
        
        logger.debug(f"Extracted {len(states)} states")
        return states
    
    def extract_transitions(
        self, 
        code: str, 
        enum_name: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Extract state transitions from code.
        
        Looks for patterns like:
        - if foo.status == OLD: foo.status = NEW
        - foo.status = NEW (after OLD check)
        
        Args:
            code: Python code to analyze
            enum_name: Optional enum class name for filtering
        
        Returns:
            List of transition dictionaries with 'from' and 'to' keys
        
        Example:
            code = '''
            if phase.status == Status.PLANNED:
                phase.status = Status.ACTIVE
            '''
            Returns: [{"from": "PLANNED", "to": "ACTIVE", "context": "..."}]
        """
        logger.debug(f"Extracting transitions (enum: {enum_name})")
        
        transitions = []
        
        try:
            tree = ast.parse(code)
            
            # Look for if statements with status assignments
            for node in ast.walk(tree):
                if isinstance(node, ast.If):
                    # Check condition for status comparison
                    old_state = self._extract_state_from_comparison(node.test, enum_name)
                    
                    if old_state:
                        # Look for status assignments in body
                        for stmt in ast.walk(node):
                            if isinstance(stmt, ast.Assign):
                                new_state = self._extract_state_from_assignment(stmt, enum_name)
                                
                                if new_state and new_state != old_state:
                                    transitions.append({
                                        "from": old_state,
                                        "to": new_state,
                                        "context": ast.unparse(node) if hasattr(ast, 'unparse') else ""
                                    })
        
        except SyntaxError as e:
            logger.warning(f"Failed to parse code: {e}")
            
            # Fallback: regex extraction
            # Pattern: if status == OLD: ... status = NEW
            pattern = r'if.*status.*==.*["\']?(\w+)["\']?.*:\s*.*status\s*=\s*["\']?(\w+)["\']?'
            matches = re.findall(pattern, code, re.DOTALL)
            
            for old_state, new_state in matches:
                if old_state != new_state:
                    transitions.append({
                        "from": old_state,
                        "to": new_state,
                        "context": ""
                    })
        
        logger.debug(f"Extracted {len(transitions)} transitions")
        return transitions
    
    def _extract_state_from_comparison(
        self, 
        node: ast.expr, 
        enum_name: Optional[str]
    ) -> Optional[str]:
        """Extract state from comparison node (ast.Compare)"""
        if isinstance(node, ast.Compare):
            # Check for various comparison patterns
            for comp in node.comparators:
                # Status.VALUE or EnumName.VALUE
                if isinstance(comp, ast.Attribute):
                    # Check if it's an enum attribute (e.g., PhaseStatus.PLANNED)
                    if isinstance(comp.value, ast.Name):
                        if enum_name is None or comp.value.id == enum_name:
                            return comp.attr
                    return comp.attr
                # Direct string comparison: "value"
                elif isinstance(comp, ast.Constant):
                    return str(comp.value).upper()
        
        return None
    
    def _extract_state_from_assignment(
        self, 
        node: ast.Assign, 
        enum_name: Optional[str]
    ) -> Optional[str]:
        """Extract state from assignment node"""
        for target in node.targets:
            if isinstance(target, ast.Attribute):
                if target.attr in ["status", "state"]:
                    # Found status assignment - extract value
                    if isinstance(node.value, ast.Attribute):
                        # Check if it's an enum attribute (e.g., PhaseStatus.ACTIVE)
                        if isinstance(node.value.value, ast.Name):
                            if enum_name is None or node.value.value.id == enum_name:
                                return node.value.attr
                        return node.value.attr
                    elif isinstance(node.value, ast.Constant):
                        return str(node.value.value).upper()
        
        return None
    
    def build_transition_graph(
        self, 
        transitions: List[Dict[str, str]]
    ) -> Dict[str, List[str]]:
        """
        Build directed graph from state transitions.
        
        Args:
            transitions: List of transition dictionaries
        
        Returns:
            Adjacency list mapping state to list of next states
        
        Example:
            transitions = [
                {"from": "A", "to": "B"},
                {"from": "B", "to": "C"},
                {"from": "A", "to": "C"}
            ]
            Returns: {"A": ["B", "C"], "B": ["C"], "C": []}
        """
        logger.debug(f"Building transition graph from {len(transitions)} transitions")
        
        graph: Dict[str, Set[str]] = defaultdict(set)
        all_states: Set[str] = set()
        
        for trans in transitions:
            from_state = trans["from"]
            to_state = trans["to"]
            
            all_states.add(from_state)
            all_states.add(to_state)
            graph[from_state].add(to_state)
        
        # Ensure all states are in graph (even terminal ones)
        for state in all_states:
            if state not in graph:
                graph[state] = set()
        
        # Convert sets to lists
        result = {state: list(next_states) for state, next_states in graph.items()}
        
        logger.debug(f"Built graph with {len(result)} states")
        return result
    
    def find_terminal_states(self, graph: Dict[str, List[str]]) -> List[str]:
        """
        Find terminal (final) states with no outgoing edges.
        
        Args:
            graph: Transition graph (adjacency list)
        
        Returns:
            List of terminal state names
        """
        terminals = [state for state, next_states in graph.items() if not next_states]
        logger.debug(f"Found {len(terminals)} terminal states")
        return terminals
    
    def find_initial_states(self, graph: Dict[str, List[str]]) -> List[str]:
        """
        Find initial (entry) states with no incoming edges.
        
        Args:
            graph: Transition graph (adjacency list)
        
        Returns:
            List of initial state names
        """
        # Build reverse graph to find states with no incoming edges
        has_incoming: Set[str] = set()
        
        for state, next_states in graph.items():
            for next_state in next_states:
                has_incoming.add(next_state)
        
        initials = [state for state in graph.keys() if state not in has_incoming]
        logger.debug(f"Found {len(initials)} initial states")
        return initials
    
    def extract_lifecycle_paths(
        self, 
        graph: Dict[str, List[str]], 
        start: str, 
        end: str,
        max_paths: int = 10
    ) -> List[List[str]]:
        """
        Extract valid lifecycle paths from start to end state.
        
        Uses DFS to find all paths (up to max_paths).
        
        Args:
            graph: Transition graph
            start: Starting state
            end: Target state
            max_paths: Maximum paths to return
        
        Returns:
            List of paths, where each path is list of states
        """
        logger.debug(f"Extracting paths: {start} → {end}")
        
        paths: List[List[str]] = []
        
        def dfs(current: str, visited: Set[str], path: List[str]):
            if len(paths) >= max_paths:
                return
            
            if current == end:
                paths.append(path.copy())
                return
            
            for next_state in graph.get(current, []):
                if next_state not in visited:
                    visited.add(next_state)
                    path.append(next_state)
                    
                    dfs(next_state, visited, path)
                    
                    path.pop()
                    visited.remove(next_state)
        
        dfs(start, {start}, [start])
        
        logger.debug(f"Found {len(paths)} paths")
        return paths
    
    def validate_state_machine(self, graph: Dict[str, List[str]]) -> List[str]:
        """
        Validate state machine for common issues.
        
        Checks for:
        - Unreachable states (no path from initial states)
        - Dead-end states (no path to terminal states)
        - Isolated states (no incoming or outgoing edges)
        
        Args:
            graph: Transition graph
        
        Returns:
            List of issue descriptions
        """
        logger.debug("Validating state machine")
        
        issues = []
        
        # Find initial and terminal states
        initial_states = self.find_initial_states(graph)
        terminal_states = self.find_terminal_states(graph)
        
        if not initial_states:
            issues.append("No initial states found (all states have incoming edges)")
        
        if not terminal_states:
            issues.append("No terminal states found (all states have outgoing edges)")
        
        # Find states with incoming edges
        has_incoming: Set[str] = set()
        for state, next_states in graph.items():
            for next_state in next_states:
                has_incoming.add(next_state)
        
        # Check for isolated states (no incoming AND no outgoing, and not part of main flow)
        all_states = set(graph.keys())
        isolated_states = [
            state
            for state in all_states
            if not graph.get(state, [])  # No outgoing
            and state not in has_incoming  # No incoming
            and len(all_states) > 1  # Not the only state
        ]
        
        if isolated_states:
            issues.append(f"Isolated states (disconnected from state machine): {', '.join(sorted(isolated_states))}")
        
        # Find reachable states from meaningful initial states (exclude isolated ones)
        meaningful_initials = [s for s in initial_states if s not in isolated_states]
        reachable: Set[str] = set()
        
        def mark_reachable(state: str):
            if state in reachable:
                return
            reachable.add(state)
            for next_state in graph.get(state, []):
                mark_reachable(next_state)
        
        for initial in meaningful_initials:
            mark_reachable(initial)
        
        # Check for unreachable states (not reachable from meaningful initial states)
        unreachable = all_states - reachable - set(meaningful_initials) - set(isolated_states)
        
        if unreachable:
            issues.append(f"Unreachable states: {', '.join(sorted(unreachable))}")
        
        logger.debug(f"Validation complete: {len(issues)} issues found")
        return issues
    
    def calculate_confidence(self, signals: Dict[str, Any]) -> float:
        """
        Calculate confidence score for state machine detection.
        
        Weighted signals:
        - Has enum: 0.3
        - Transition count: 0.05 per transition (max 0.4)
        - Has validation: 0.2
        - Naming clarity: 0.1
        
        Args:
            signals: Dictionary of detection signals
        
        Returns:
            Confidence score in [0.0, 1.0]
        """
        score = 0.0
        
        # Enum presence
        if signals.get("has_enum"):
            score += 0.3
        
        # Transition count
        transition_count = signals.get("transition_count", 0)
        score += min(transition_count * 0.05, 0.4)
        
        # Validation logic
        if signals.get("has_validation"):
            score += 0.2
        
        # Naming clarity
        naming_clarity = signals.get("naming_clarity", 0.0)
        score += naming_clarity * 0.1
        
        # Clamp to [0.0, 1.0]
        confidence = max(0.0, min(1.0, score))
        
        logger.debug(f"Calculated confidence: {confidence:.2f}")
        return confidence
