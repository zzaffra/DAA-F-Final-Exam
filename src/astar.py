"""
A* Algorithm Module
Implementation of A* search algorithm with Manhattan distance heuristic.
"""

import heapq
from typing import Dict, List, Tuple, Optional, Callable
from graph import Graph


class AStarResult:
    """Result of A* algorithm execution."""
    
    def __init__(self):
        self.path: List[Tuple[int, int]] = []
        self.path_length: float = float('inf')
        self.explored_nodes: int = 0
        self.visited_nodes: int = 0
        self.runtime: float = 0.0


class AStar:
    """A* search algorithm implementation."""
    
    def __init__(self, graph: Graph, heuristic: Optional[Callable] = None):
        """
        Initialize A* solver.
        
        Args:
            graph: Graph instance
            heuristic: Optional heuristic function. Defaults to Manhattan distance.
        """
        self.graph = graph
        self.heuristic = heuristic or self.graph.manhattan_distance
    
    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int]) -> AStarResult:
        """
        Find shortest path from start to goal using A* algorithm.
        
        Args:
            start: Start position (x, y)
            goal: Goal position (x, y)
            
        Returns:
            AStarResult containing path and metrics
        """
        result = AStarResult()
        
        # Priority queue: (f_score, node_id, position)
        # f_score = g_score + h_score
        h_start = self.heuristic(start, goal)
        pq = [(h_start, id(start), start)]
        
        # Track visited nodes
        visited = set()
        visited_order = []
        
        # Track costs
        g_scores: Dict[Tuple[int, int], float] = {start: 0}
        f_scores: Dict[Tuple[int, int], float] = {start: h_start}
        predecessors: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {start: None}
        
        # Track nodes in open set
        open_set = {start}
        
        while pq:
            f_score, _, current_pos = heapq.heappop(pq)
            
            # Skip if already visited
            if current_pos in visited:
                continue
            
            # Mark as visited
            visited.add(current_pos)
            visited_order.append(current_pos)
            result.explored_nodes += 1
            open_set.discard(current_pos)
            
            # Goal found
            if current_pos == goal:
                result.path_length = g_scores[goal]
                result.path = self._reconstruct_path(predecessors, start, goal)
                result.visited_nodes = len(visited)
                return result
            
            # Explore neighbors
            for neighbor_pos in self.graph.get_neighbors(current_pos):
                if neighbor_pos not in visited:
                    edge_cost = self.graph.get_edge_cost(current_pos, neighbor_pos)
                    tentative_g = g_scores[current_pos] + edge_cost
                    
                    # If this path to neighbor is better than previously found
                    if neighbor_pos not in g_scores or tentative_g < g_scores[neighbor_pos]:
                        # This path is the best so far
                        predecessors[neighbor_pos] = current_pos
                        g_scores[neighbor_pos] = tentative_g
                        h_score = self.heuristic(neighbor_pos, goal)
                        f_score = tentative_g + h_score
                        f_scores[neighbor_pos] = f_score
                        
                        if neighbor_pos not in open_set:
                            open_set.add(neighbor_pos)
                            heapq.heappush(pq, (f_score, id(neighbor_pos), neighbor_pos))
        
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
