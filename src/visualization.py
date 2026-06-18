"""
Visualization Module
Generates plots and visualizations for algorithm comparison.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from typing import List, Dict, Tuple
from map_generator import BuildingMap, Cell


class Visualization:
    """Handles visualization of maps and algorithm results."""
    
    @staticmethod
    def plot_map(
        building_map: BuildingMap,
        path: List[Tuple[int, int]] = None,
        explored_cells: List[Tuple[int, int]] = None,
        title: str = "Evacuation Map",
        filename: str = None
    ):
        """
        Visualize a building map with optional path and explored cells.
        
        Args:
            building_map: BuildingMap instance
            path: Path from start to exit
            explored_cells: Cells explored by algorithm
            title: Plot title
            filename: If provided, save to file instead of showing
        """
        fig, ax = plt.subplots(figsize=(10, 10))
        
        # Draw grid background
        ax.set_xlim(-0.5, building_map.width - 0.5)
        ax.set_ylim(building_map.height - 0.5, -0.5)
        ax.set_aspect('equal')
        
        # Draw obstacles
        for y in range(building_map.height):
            for x in range(building_map.width):
                if building_map.grid[y][x] == Cell.OBSTACLE:
                    rect = patches.Rectangle((x - 0.5, y - 0.5), 1, 1, 
                                            linewidth=0.5, edgecolor='black', 
                                            facecolor='black')
                    ax.add_patch(rect)
        
        # Draw explored cells
        if explored_cells:
            for x, y in explored_cells:
                rect = patches.Rectangle((x - 0.5, y - 0.5), 1, 1,
                                        linewidth=0.5, edgecolor='gray',
                                        facecolor='lightblue', alpha=0.3)
                ax.add_patch(rect)
        
        # Draw path
        if path:
            path_x = [pos[0] for pos in path]
            path_y = [pos[1] for pos in path]
            ax.plot(path_x, path_y, 'r-', linewidth=2, label='Evacuation Path')
        
        # Draw start and exit
        start_x, start_y = building_map.start_pos
        exit_x, exit_y = building_map.exit_pos
        
        ax.plot(start_x, start_y, 'go', markersize=12, label='Start', zorder=5)
        ax.plot(exit_x, exit_y, 'r*', markersize=20, label='Exit', zorder=5)
        
        ax.set_xlabel('X Position')
        ax.set_ylabel('Y Position')
        ax.set_title(title)
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.2)
        
        if filename:
            plt.savefig(filename, dpi=150, bbox_inches='tight')
            plt.close()
        else:
            plt.show()
    
    @staticmethod
    def plot_runtime_comparison(
        results: Dict[str, Dict[int, float]],
        map_sizes: List[int],
        filename: str = None
    ):
        """
        Plot runtime comparison between algorithms across map sizes.
        
        Args:
            results: Dictionary with algorithm names as keys, containing size->runtime mapping
            map_sizes: List of map sizes tested
            filename: If provided, save to file
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        for algo_name, size_data in results.items():
            runtimes = [size_data.get(size, 0) for size in map_sizes]
            ax.plot(map_sizes, runtimes, marker='o', linewidth=2, label=algo_name)
        
        ax.set_xlabel('Map Size (width × height)', fontsize=12)
        ax.set_ylabel('Runtime (seconds)', fontsize=12)
        ax.set_title('Algorithm Runtime Comparison', fontsize=14, fontweight='bold')
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)
        
        # Use log scale if values vary widely
        if max(v for d in results.values() for v in d.values()) > 100:
            ax.set_yscale('log')
            ax.set_ylabel('Runtime (seconds, log scale)', fontsize=12)
        
        if filename:
            plt.savefig(filename, dpi=150, bbox_inches='tight')
            plt.close()
        else:
            plt.show()
    
    @staticmethod
    def plot_explored_nodes_comparison(
        results: Dict[str, Dict[int, int]],
        map_sizes: List[int],
        filename: str = None
    ):
        """
        Plot explored nodes comparison between algorithms across map sizes.
        
        Args:
            results: Dictionary with algorithm names as keys, containing size->explored_nodes mapping
            map_sizes: List of map sizes tested
            filename: If provided, save to file
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        for algo_name, size_data in results.items():
            nodes = [size_data.get(size, 0) for size in map_sizes]
            ax.plot(map_sizes, nodes, marker='s', linewidth=2, label=algo_name)
        
        ax.set_xlabel('Map Size (width × height)', fontsize=12)
        ax.set_ylabel('Number of Explored Nodes', fontsize=12)
        ax.set_title('Search Efficiency: Explored Nodes Comparison', fontsize=14, fontweight='bold')
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)
        
        # Use log scale for both axes
        ax.set_yscale('log')
        ax.set_xscale('log')
        
        if filename:
            plt.savefig(filename, dpi=150, bbox_inches='tight')
            plt.close()
        else:
            plt.show()
    
    @staticmethod
    def plot_obstacle_density_impact(
        results: Dict[str, Dict[float, float]],
        densities: List[float],
        filename: str = None,
        metric_name: str = "Runtime (seconds)"
    ):
        """
        Plot impact of obstacle density on algorithm performance.
        
        Args:
            results: Dictionary with algorithm names as keys, containing density->metric mapping
            densities: List of obstacle densities tested
            filename: If provided, save to file
            metric_name: Name of metric being plotted
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        for algo_name, density_data in results.items():
            metrics = [density_data.get(d, 0) for d in densities]
            ax.plot([d * 100 for d in densities], metrics, marker='D', linewidth=2, label=algo_name)
        
        ax.set_xlabel('Obstacle Density (%)', fontsize=12)
        ax.set_ylabel(metric_name, fontsize=12)
        ax.set_title(f'Impact of Obstacle Density on {metric_name}', fontsize=14, fontweight='bold')
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)
        ax.set_xticks([d * 100 for d in densities])
        
        if filename:
            plt.savefig(filename, dpi=150, bbox_inches='tight')
            plt.close()
        else:
            plt.show()
    
    @staticmethod
    def plot_path_length_comparison(
        results: Dict[str, Dict[int, float]],
        map_sizes: List[int],
        filename: str = None
    ):
        """
        Plot path length comparison between algorithms.
        
        Args:
            results: Dictionary with algorithm names as keys, containing size->path_length mapping
            map_sizes: List of map sizes tested
            filename: If provided, save to file
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        for algo_name, size_data in results.items():
            lengths = [size_data.get(size, 0) for size in map_sizes]
            ax.plot(map_sizes, lengths, marker='^', linewidth=2, label=algo_name)
        
        ax.set_xlabel('Map Size (width × height)', fontsize=12)
        ax.set_ylabel('Path Length', fontsize=12)
        ax.set_title('Path Length Comparison', fontsize=14, fontweight='bold')
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)
        
        if filename:
            plt.savefig(filename, dpi=150, bbox_inches='tight')
            plt.close()
        else:
            plt.show()
