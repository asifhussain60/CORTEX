"""
Knowledge Graph Query Engine

Provides high-level query API for graph traversal and pattern matching.

Author: CORTEX Architect
Phase: Phase 66 S2
"""

import logging
from typing import List, Dict, Set, Optional, Tuple
from pathlib import Path

from cortex_lens.knowledge_graph.graph_storage import GraphStorage
from cortex_lens.knowledge_graph.graph_schema import Node, Edge, NodeType, EdgeType

logger = logging.getLogger(__name__)


class GraphQuery:
    """
    High-level query engine for knowledge graph traversal.
    
    Provides intuitive API for common traversal patterns:
    - Multi-hop traversal with edge type filtering
    - Path finding between nodes
    - Pattern matching for architectural queries
    
    Example:
        query = GraphQuery(storage)
        
        # Find all classes that import a module
        importers = query.traverse(
            start_node_id=module_id,
            edge_types=["imports"],
            direction="incoming",
            max_depth=1
        )
        
        # Find call path from function A to function B
        path = query.find_path(
            start_node_id=func_a_id,
            end_node_id=func_b_id,
            edge_types=["calls"]
        )
    """
    
    def __init__(self, storage: GraphStorage):
        """
        Initialize query engine.
        
        Args:
            storage: GraphStorage instance for data access
        """
        self.storage = storage
        logger.debug("Initialized GraphQuery engine")
    
    def traverse(
        self,
        start_node_id: int,
        edge_types: Optional[List[str]] = None,
        direction: str = "outgoing",
        max_depth: int = 1,
        node_type_filter: Optional[List[str]] = None
    ) -> List[Node]:
        """
        Traverse graph from starting node.
        
        Args:
            start_node_id: Node to start traversal from
            edge_types: Filter by edge types (None = all types)
            direction: "outgoing" or "incoming"
            max_depth: Maximum traversal depth (1 = direct neighbors)
            node_type_filter: Filter results by node types (None = all types)
        
        Returns:
            List of nodes reachable within max_depth
        
        Example:
            # Find all functions called by function_id (1-hop)
            called_functions = query.traverse(
                start_node_id=function_id,
                edge_types=["calls"],
                direction="outgoing",
                max_depth=1,
                node_type_filter=["function"]
            )
        """
        logger.debug(
            f"Traversing from node {start_node_id}: "
            f"depth={max_depth}, edge_types={edge_types}, direction={direction}"
        )
        
        visited: Set[int] = set()
        current_level: Set[int] = {start_node_id}
        result_nodes: List[Node] = []
        
        for depth in range(max_depth):
            next_level: Set[int] = set()
            
            for node_id in current_level:
                if node_id in visited:
                    continue
                
                visited.add(node_id)
                
                # Get neighbors at current depth
                # Note: query_neighbors only supports single edge_type
                edge_type = edge_types[0] if edge_types else None
                neighbors = self.storage.query_neighbors(
                    node_id=node_id,
                    edge_type=edge_type,
                    depth=1  # Single hop per iteration
                )
                
                for neighbor in neighbors:
                    neighbor_id = neighbor["id"]
                    
                    # Apply node type filter
                    if node_type_filter and neighbor["node_type"] not in node_type_filter:
                        continue
                    
                    # Add to results
                    node = Node(
                        id=neighbor_id,
                        node_type=neighbor["node_type"],
                        name=neighbor["name"],
                        properties=neighbor.get("properties", {})
                    )
                    result_nodes.append(node)
                    
                    # Queue for next level
                    if depth < max_depth - 1:
                        next_level.add(neighbor_id)
            
            current_level = next_level
        
        logger.debug(f"Traversal found {len(result_nodes)} nodes")
        return result_nodes
    
    def find_path(
        self,
        start_node_id: int,
        end_node_id: int,
        edge_types: Optional[List[str]] = None,
        max_depth: int = 5
    ) -> Optional[List[Tuple[Node, str]]]:
        """
        Find shortest path between two nodes.
        
        Uses breadth-first search to find shortest path.
        
        Args:
            start_node_id: Starting node ID
            end_node_id: Target node ID
            edge_types: Filter by edge types (None = all types)
            max_depth: Maximum search depth (prevents infinite loops)
        
        Returns:
            List of (node, edge_type) tuples representing path, or None if no path found.
            First element is start node with empty edge_type.
        
        Example:
            # Find how function A calls function B
            path = query.find_path(
                start_node_id=function_a_id,
                end_node_id=function_b_id,
                edge_types=["calls"],
                max_depth=3
            )
            
            if path:
                print("Call chain:")
                for node, edge in path:
                    if edge:
                        print(f"  → {node.name} ({edge})")
                    else:
                        print(f"  {node.name}")
        """
        logger.debug(f"Finding path: {start_node_id} → {end_node_id}")
        
        if start_node_id == end_node_id:
            start_node_data = self.storage.get_node(start_node_id)
            if start_node_data:
                start_node = Node(
                    id=start_node_data["id"],
                    node_type=start_node_data["node_type"],
                    name=start_node_data["name"],
                    properties=start_node_data.get("properties", {})
                )
                return [(start_node, "")]
            return None
        
        # BFS with path tracking
        visited: Set[int] = set()
        queue: List[Tuple[int, List[Tuple[int, str]]]] = [(start_node_id, [])]
        
        while queue:
            current_id, path = queue.pop(0)
            
            if current_id in visited:
                continue
            
            visited.add(current_id)
            
            # Check depth limit
            if len(path) >= max_depth:
                continue
            
            # Get neighbors
            edge_type = edge_types[0] if edge_types else None
            neighbors = self.storage.query_neighbors(
                node_id=current_id,
                edge_type=edge_type,
                depth=1
            )
            
            for neighbor in neighbors:
                neighbor_id = neighbor["id"]
                edge_type = neighbor.get("edge_type", "unknown")
                
                # Build path to this neighbor
                new_path = path + [(current_id, edge_type)]
                
                # Check if we found target
                if neighbor_id == end_node_id:
                    # Convert path to (Node, edge_type) format
                    result_path: List[Tuple[Node, str]] = []
                    
                    # Add start node
                    start_node_data = self.storage.get_node(start_node_id)
                    if start_node_data:
                        start_node = Node(
                            id=start_node_data["id"],
                            node_type=start_node_data["node_type"],
                            name=start_node_data["name"],
                            properties=start_node_data.get("properties", {})
                        )
                        result_path.append((start_node, ""))
                    
                    # Add intermediate nodes
                    for node_id, edge_type in new_path:
                        if node_id != start_node_id:
                            node_data = self.storage.get_node(node_id)
                            if node_data:
                                node = Node(
                                    id=node_data["id"],
                                    node_type=node_data["node_type"],
                                    name=node_data["name"],
                                    properties=node_data.get("properties", {})
                                )
                                result_path.append((node, edge_type))
                    
                    # Add end node
                    end_node_data = self.storage.get_node(end_node_id)
                    if end_node_data:
                        end_node = Node(
                            id=end_node_data["id"],
                            node_type=end_node_data["node_type"],
                            name=end_node_data["name"],
                            properties=end_node_data.get("properties", {})
                        )
                        result_path.append((end_node, edge_type))
                    
                    logger.debug(f"Path found: {len(result_path)} nodes")
                    return result_path
                
                # Continue search
                if neighbor_id not in visited:
                    queue.append((neighbor_id, new_path))
        
        logger.debug("No path found")
        return None
    
    def find_all_paths(
        self,
        start_node_id: int,
        end_node_id: int,
        edge_types: Optional[List[str]] = None,
        max_depth: int = 5,
        max_paths: int = 10
    ) -> List[List[Tuple[Node, str]]]:
        """
        Find all paths between two nodes (up to max_paths).
        
        Uses depth-first search to enumerate paths.
        
        Args:
            start_node_id: Starting node ID
            end_node_id: Target node ID
            edge_types: Filter by edge types (None = all types)
            max_depth: Maximum path length
            max_paths: Maximum number of paths to return (prevents combinatorial explosion)
        
        Returns:
            List of paths, where each path is List[Tuple[Node, str]]
        
        Example:
            # Find all ways module A depends on module B
            paths = query.find_all_paths(
                start_node_id=module_a_id,
                end_node_id=module_b_id,
                edge_types=["imports", "calls"],
                max_depth=3,
                max_paths=5
            )
            
            print(f"Found {len(paths)} dependency paths")
            for i, path in enumerate(paths):
                print(f"Path {i+1}:")
                for node, edge in path:
                    if edge:
                        print(f"  → {node.name} ({edge})")
        """
        logger.debug(f"Finding all paths: {start_node_id} → {end_node_id} (max: {max_paths})")
        
        all_paths: List[List[Tuple[Node, str]]] = []
        
        def dfs(
            current_id: int,
            visited: Set[int],
            path: List[Tuple[int, str]]
        ):
            # Stop if we found enough paths
            if len(all_paths) >= max_paths:
                return
            
            # Stop if depth exceeded
            if len(path) >= max_depth:
                return
            
            # Found target
            if current_id == end_node_id:
                # Convert path to (Node, edge_type) format
                result_path: List[Tuple[Node, str]] = []
                
                for node_id, edge_type in path:
                    node_data = self.storage.get_node(node_id)
                    if node_data:
                        node = Node(
                            id=node_data["id"],
                            node_type=node_data["node_type"],
                            name=node_data["name"],
                            properties=node_data.get("properties", {})
                        )
                        result_path.append((node, edge_type))
                
                # Add end node
                end_node_data = self.storage.get_node(end_node_id)
                if end_node_data:
                    end_node = Node(
                        id=end_node_data["id"],
                        node_type=end_node_data["node_type"],
                        name=end_node_data["name"],
                        properties=end_node_data.get("properties", {})
                    )
                    result_path.append((end_node, ""))
                
                all_paths.append(result_path)
                return
            
            # Explore neighbors
            edge_type = edge_types[0] if edge_types else None
            neighbors = self.storage.query_neighbors(
                node_id=current_id,
                edge_type=edge_type,
                depth=1
            )
            
            for neighbor in neighbors:
                neighbor_id = neighbor["id"]
                
                if neighbor_id not in visited:
                    edge_type = neighbor.get("edge_type", "unknown")
                    
                    visited.add(neighbor_id)
                    path.append((neighbor_id, edge_type))
                    
                    dfs(neighbor_id, visited, path)
                    
                    path.pop()
                    visited.remove(neighbor_id)
        
        # Start DFS
        start_node = self.storage.get_node(start_node_id)
        if start_node:
            dfs(start_node_id, {start_node_id}, [(start_node_id, "")])
        
        logger.debug(f"Found {len(all_paths)} paths")
        return all_paths
