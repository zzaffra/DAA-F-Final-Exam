"""
Dijkstra Algorithm Module
Implementation of Dijkstra's shortest path algorithm.
"""

import heapq
from typing import Dict, List, Tuple, Optional
from graph import Graph


class DijkstraResult:
    """Result of Dijkstra algorithm execution."""
    
    def __init__(self):
        self.path: List[Tuple[int, int]] = []
        self.path_length: float = float('inf')
        self.explored_nodes: int = 0
        self.visited_nodes: int = 0
        self.runtime: float = 0.0


class Dijkstra:
    """Dijkstra's shortest path algorithm implementation."""
    
    def __init__(self, graph: Graph):
        """
        Initialize Dijkstra solver.
        
        Args:
            graph: Graph instance
        """
        self.graph = graph
    
    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int]) -> DijkstraResult:
        """
        Find shortest path from start to goal using Dijkstra's algorithm.
        
        Args:
            start: Start position (x, y)
            goal: Goal position (x, y)
            
        Returns:
            DijkstraResult containing path and metrics
        """
        result = DijkstraResult()
        
        # Priority queue: (cost, node_id, position)
        # node_id used as tiebreaker to ensure consistent ordering
        pq = [(0, id(start), start)]
        
        # Track visited nodes
        visited = set()
        visited_order = []
        
        # Track distances and predecessors
        distances: Dict[Tuple[int, int], float] = {start: 0}
        predecessors: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {start: None}
        
        while pq:
            current_cost, _, current_pos = heapq.heappop(pq)
            
            # Skip if already visited
            if current_pos in visited:
                continue
            
            visited.add(current_pos)
            visited_order.append(current_pos)
            result.explored_nodes += 1
            
            # Goal found
            if current_pos == goal:
                result.path_length = current_cost
                result.path = self._reconstruct_path(predecessors, start, goal)
                result.visited_nodes = len(visited)
                return result
            
            # Explore neighbors
            for neighbor_pos in self.graph.get_neighbors(current_pos):
                if neighbor_pos not in visited:
                    edge_cost = self.graph.get_edge_cost(current_pos, neighbor_pos)
                    new_cost = current_cost + edge_cost
                    
                    # Update if shorter path found
                    if neighbor_pos not in distances or new_cost < distances[neighbor_pos]:
                        distances[neighbor_pos] = new_cost
                        predecessors[neighbor_pos] = current_pos
                        heapq.heappush(pq, (new_cost, id(neighbor_pos), neighbor_pos))
        
        # No path found
        result.visited_nodes = len(visited)
        return result
    
    @staticmethod
    def _reconstruct_path(
        predecessors: Dict[Tuple[int, int], Optional[Tuple[int, int]]],
        start: Tuple[int, int],
        goal: Tuple[int, int]
    ) -> List[Tuple[int, int]]:
        """
        Reconstruct path from goal to start using predecessors.
        
        Args:
            predecessors: Dictionary mapping positions to their predecessors
            start: Start position
            goal: Goal position
            
        Returns:
            List of positions from start to goal
        """
        path = []
        current = goal
        
        while current is not None:
            path.append(current)
            current = predecessors.get(current)
        
        path.reverse()
        
        # Verify path starts at start
        if path and path[0] == start:
            return path
        return []
