"""
Graph Module
Represents the building map as a graph for pathfinding algorithms.
"""

from typing import Dict, List, Tuple, Set
from map_generator import BuildingMap


class Node:
    """Represents a node in the graph."""
    
    def __init__(self, pos: Tuple[int, int]):
        """
        Initialize a node.
        
        Args:
            pos: Tuple (x, y) representing position
        """
        self.pos = pos
        self.neighbors = []
    
    def __hash__(self):
        return hash(self.pos)
    
    def __eq__(self, other):
        return isinstance(other, Node) and self.pos == other.pos
    
    def __lt__(self, other):
        # For priority queue comparison
        return self.pos < other.pos
    
    def __repr__(self):
        return f"Node({self.pos})"


class Graph:
    """Represents building map as a graph."""
    
    def __init__(self, building_map: BuildingMap):
        """
        Initialize graph from building map.
        
        Args:
            building_map: BuildingMap instance
        """
        self.building_map = building_map
        self.nodes: Dict[Tuple[int, int], Node] = {}
        self.start_pos = building_map.start_pos
        self.exit_pos = building_map.exit_pos
        
        self._build_graph()
    
    def _build_graph(self):
        """Build graph from walkable cells."""
        # Create nodes for all walkable cells
        walkable = self.building_map.get_walkable_cells()
        for pos in walkable:
            self.nodes[pos] = Node(pos)
        
        # Connect neighbors
        for pos, node in self.nodes.items():
            x, y = pos
            for neighbor_pos in self.building_map.get_neighbors(x, y):
                if neighbor_pos in self.nodes:
                    node.neighbors.append(neighbor_pos)
    
    def get_node(self, pos: Tuple[int, int]) -> Node:
        """Get node at position."""
        return self.nodes.get(pos)
    
    def get_neighbors(self, pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Get neighbor positions of a cell."""
        if pos in self.nodes:
            return self.nodes[pos].neighbors
        return []
    
    def get_edge_cost(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """
        Get cost of edge between two positions.
        All edges have cost 1 (uniform cost).
        """
        return 1.0
    
    def node_count(self) -> int:
        """Get number of nodes in graph."""
        return len(self.nodes)
    
    def get_all_nodes(self) -> List[Tuple[int, int]]:
        """Get all node positions."""
        return list(self.nodes.keys())
    
    def manhattan_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """
        Calculate Manhattan distance between two positions.
        Used as heuristic for A*.
        """
        x1, y1 = pos1
        x2, y2 = pos2
        return abs(x1 - x2) + abs(y1 - y2)
