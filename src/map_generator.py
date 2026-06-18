"""
Map Generator Module
Generates random building maps with obstacles, start position, and emergency exits.
"""

import random
from typing import Tuple, List, Set

class Cell:
    """Represents a cell in the building map."""
    EMPTY = 0
    OBSTACLE = 1
    START = 2
    EXIT = 3
    
    @staticmethod
    def get_name(cell_type):
        """Get human-readable name for cell type."""
        names = {0: "Empty", 1: "Obstacle", 2: "Start", 3: "Exit"}
        return names.get(cell_type, "Unknown")


class BuildingMap:
    """Represents a building map as a 2D grid."""
    
    def __init__(self, width: int, height: int, obstacle_density: float = 0.2, seed: int = None):
        """
        Initialize building map.
        
        Args:
            width: Map width
            height: Map height
            obstacle_density: Proportion of cells that are obstacles (0.0 to 1.0)
            seed: Random seed for reproducibility
        """
        if seed is not None:
            random.seed(seed)
        
        self.width = width
        self.height = height
        self.obstacle_density = obstacle_density
        self.grid = [[Cell.EMPTY for _ in range(width)] for _ in range(height)]
        self.start_pos = None
        self.exit_pos = None
        
        self._generate_map()
    
    def _generate_map(self):
        """Generate random map with obstacles."""
        # Create a corridor from start to exit to ensure connectivity
        # Then add random obstacles around this corridor
        
        # First, mark a corridor path (roughly diagonal from top-left to bottom-right)
        corridor_cells = set()
        
        # Create main path
        for y in range(self.height):
            x = int((y / self.height) * self.width)
            # Add a thick corridor (5 cells wide)
            for dx in range(-2, 3):
                nx = x + dx
                if 0 <= nx < self.width:
                    corridor_cells.add((nx, y))
        
        # Generate obstacles, avoiding corridor
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) not in corridor_cells:
                    if random.random() < self.obstacle_density:
                        self.grid[y][x] = Cell.OBSTACLE
        
        # Place start in top-left area (within corridor if possible)
        self.start_pos = self._find_empty_cell(prefer_near=(0, 0))
        self.grid[self.start_pos[1]][self.start_pos[0]] = Cell.START
        
        # Place exit in bottom-right area (within corridor if possible)
        self.exit_pos = self._find_empty_cell(prefer_near=(self.width - 1, self.height - 1))
        self.grid[self.exit_pos[1]][self.exit_pos[0]] = Cell.EXIT
    
    def _find_empty_cell(self, prefer_near: Tuple[int, int] = None) -> Tuple[int, int]:
        """
        Find an empty cell, preferably near the given position.
        
        Args:
            prefer_near: Tuple (x, y) to search near
            
        Returns:
            Tuple (x, y) of empty cell
        """
        if prefer_near:
            x_pref, y_pref = prefer_near
            # Search in expanding radius from preferred position
            for radius in range(max(self.width, self.height)):
                candidates = []
                for x in range(max(0, x_pref - radius), min(self.width, x_pref + radius + 1)):
                    for y in range(max(0, y_pref - radius), min(self.height, y_pref + radius + 1)):
                        if self.grid[y][x] == Cell.EMPTY:
                            candidates.append((x, y))
                if candidates:
                    return random.choice(candidates)
        
        # Fallback: search entire grid
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == Cell.EMPTY:
                    return (x, y)
        
        raise RuntimeError("No empty cell found in map")
    
    def get_walkable_cells(self) -> Set[Tuple[int, int]]:
        """Get all walkable cells (non-obstacles)."""
        walkable = set()
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] != Cell.OBSTACLE:
                    walkable.add((x, y))
        return walkable
    
    def is_walkable(self, x: int, y: int) -> bool:
        """Check if cell is walkable."""
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False
        return self.grid[y][x] != Cell.OBSTACLE
    
    def get_neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        """Get walkable neighbors of a cell (4-directional)."""
        neighbors = []
        # Up, Down, Left, Right
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx, ny = x + dx, y + dy
            if self.is_walkable(nx, ny):
                neighbors.append((nx, ny))
        return neighbors
    
    def cell_count(self) -> int:
        """Get total number of cells."""
        return self.width * self.height
    
    def walkable_count(self) -> int:
        """Get number of walkable cells."""
        return len(self.get_walkable_cells())
    
    def obstacle_count(self) -> int:
        """Get number of obstacle cells."""
        return self.cell_count() - self.walkable_count()
    
    def __str__(self) -> str:
        """String representation of map."""
        symbols = {
            Cell.EMPTY: ".",
            Cell.OBSTACLE: "#",
            Cell.START: "S",
            Cell.EXIT: "E"
        }
        lines = []
        for row in self.grid:
            lines.append("".join(symbols[cell] for cell in row))
        return "\n".join(lines)
