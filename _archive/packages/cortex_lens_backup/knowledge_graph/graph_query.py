"""
Knowledge Graph Query Engine

Provides high-level query API for graph traversal and pattern matching.

Author: CORTEX Architect
Phase: Phase 66 S2
"""

import json
import logging
from typing import List, Dict, Set, Optional, Tuple, Any
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
                
                # Get neighbors based on direction
                if direction == "incoming":
                    # For incoming edges, we need to query where this node is the TARGET
                    # Use get_edges_for_nodes or custom query
                    neighbors = self._query_incoming_neighbors(node_id, edge_types[0] if edge_types else None)
                else:
                    # Outgoing edges (default behavior)
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
    
    def find_callers(
        self,
        target_name: str,
        edge_type: str = "calls",
        max_depth: int = 2
    ) -> List[Node]:
        """
        Find all nodes that call/reference the target node by name.
        
        Args:
            target_name: Name of target node to find callers for
            edge_type: Edge type to traverse (default: "calls")
            max_depth: Maximum traversal depth
        
        Returns:
            List of nodes that reference the target
        
        Example:
            # Find all files that import UserRepository
            callers = query.find_callers("UserRepository", "imports", max_depth=2)
        """
        logger.debug(f"Finding callers of '{target_name}' via '{edge_type}' (depth={max_depth})")
        
        # Find target node by name
        target_nodes = self._find_nodes_by_name(target_name)
        
        if not target_nodes:
            logger.warning(f"No nodes found with name '{target_name}'")
            return []
        
        # For each target, find incoming edges
        all_callers: List[Node] = []
        visited_ids: Set[int] = set()
        
        for target_node in target_nodes:
            # Traverse incoming edges
            callers = self.traverse(
                start_node_id=target_node["id"],
                edge_types=[edge_type],
                direction="incoming",
                max_depth=max_depth
            )
            
            # Deduplicate by ID
            for caller in callers:
                if caller.id is not None and caller.id not in visited_ids:
                    all_callers.append(caller)
                    visited_ids.add(caller.id)
        
        logger.debug(f"Found {len(all_callers)} callers")
        return all_callers
    
    def _find_nodes_by_name(self, name: str) -> List[Dict[str, Any]]:
        """
        Find nodes by name (internal helper).
        
        Args:
            name: Node name to search for
        
        Returns:
            List of node dictionaries matching the name
        """
        conn = self.storage._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, node_type, name, properties
            FROM nodes
            WHERE name LIKE ?
        """, (f"%{name}%",))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "id": row["id"],
                "node_type": row["node_type"],
                "name": row["name"],
                "properties": json.loads(row["properties"]) if row["properties"] else {}
            })
        
        return results
    
    def _query_incoming_neighbors(self, node_id: int, edge_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Query incoming neighbors (nodes that point TO this node).
        
        Args:
            node_id: Target node ID
            edge_type: Filter by edge type (None = all types)
        
        Returns:
            List of source nodes that have edges pointing to node_id
        """
        conn = self.storage._get_connection()
        cursor = conn.cursor()
        
        # Query incoming edges (where this node is the TARGET)
        if edge_type:
            cursor.execute(
                """
                SELECT n.id, n.node_type, n.name, n.properties
                FROM edges e
                JOIN nodes n ON e.source_id = n.id
                WHERE e.target_id = ? AND e.edge_type = ?
                """,
                (node_id, edge_type)
            )
        else:
            cursor.execute(
                """
                SELECT n.id, n.node_type, n.name, n.properties
                FROM edges e
                JOIN nodes n ON e.source_id = n.id
                WHERE e.target_id = ?
                """,
                (node_id,)
            )
        
        neighbors = []
        for row in cursor.fetchall():
            neighbors.append({
                "id": row["id"],
                "node_type": row["node_type"],
                "name": row["name"],
                "properties": json.loads(row["properties"]) if row["properties"] else {}
            })
        
        return neighbors
    
    def get_edges_for_nodes(
        self,
        nodes: List[Node],
        edge_type: Optional[str] = None
    ) -> List[Edge]:
        """
        Get edges connecting the given nodes.
        
        Args:
            nodes: List of nodes to get edges for
            edge_type: Optional edge type filter
        
        Returns:
            List of edges between the nodes
        """
        if not nodes:
            return []
        
        node_ids = [node.id for node in nodes]
        conn = self.storage._get_connection()
        cursor = conn.cursor()
        
        if edge_type:
            cursor.execute("""
                SELECT id, source_id, target_id, edge_type, properties
                FROM edges
                WHERE source_id IN ({}) AND target_id IN ({}) AND edge_type = ?
            """.format(','.join('?' * len(node_ids)), ','.join('?' * len(node_ids))),
                (*node_ids, *node_ids, edge_type))
        else:
            cursor.execute("""
                SELECT id, source_id, target_id, edge_type, properties
                FROM edges
                WHERE source_id IN ({}) AND target_id IN ({})
            """.format(','.join('?' * len(node_ids)), ','.join('?' * len(node_ids))),
                (*node_ids, *node_ids))
        
        edges = []
        for row in cursor.fetchall():
            edges.append(Edge(
                id=row["id"],
                source_id=row["source_id"],
                target_id=row["target_id"],
                edge_type=row["edge_type"],
                properties=json.loads(row["properties"]) if row["properties"] else {}
            ))
        
        return edges
