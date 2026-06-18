"""
Benchmark Module
Comprehensive benchmarking of Dijkstra and A* algorithms.
"""

import time
import csv
import os
from typing import List, Dict, Tuple
from map_generator import BuildingMap
from graph import Graph
from dijkstra import Dijkstra
from astar import AStar
from visualization import Visualization


class BenchmarkConfig:
    """Configuration for benchmarks."""
    
    # Map sizes to test
    MAP_SIZES = [
        (50, 50),
        (100, 100),
        (200, 200),
        (300, 300),
        (500, 500)
    ]
    
    # Obstacle densities to test
    OBSTACLE_DENSITIES = [0.1, 0.2, 0.3]
    
    # Fixed seed for reproducibility
    RANDOM_SEED = 42


class BenchmarkResult:
    """Result of a single benchmark run."""
    
    def __init__(self, map_size_x: int, map_size_y: int, obstacle_density: float, algorithm: str):
        self.map_size_x = map_size_x
        self.map_size_y = map_size_y
        self.map_size = f"{map_size_x}x{map_size_y}"
        self.map_area = map_size_x * map_size_y
        self.obstacle_density = obstacle_density
        self.algorithm = algorithm
        
        # Metrics
        self.path_length = 0.0
        self.runtime = 0.0
        self.explored_nodes = 0
        self.visited_nodes = 0


class Benchmark:
    """Benchmark suite for pathfinding algorithms."""
    
    def __init__(self, output_dir: str = "results"):
        """
        Initialize benchmark.
        
        Args:
            output_dir: Directory for output files
        """
        self.output_dir = output_dir
        self.results: List[BenchmarkResult] = []
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
    
    def run_all_benchmarks(self):
        """Run all benchmark configurations."""
        print("=" * 80)
        print("SMART EMERGENCY EVACUATION SYSTEM - PATHFINDING BENCHMARK")
        print("=" * 80)
        print()
        
        total_tests = len(BenchmarkConfig.MAP_SIZES) * len(BenchmarkConfig.OBSTACLE_DENSITIES) * 2
        current_test = 0
        
        for map_size in BenchmarkConfig.MAP_SIZES:
            for density in BenchmarkConfig.OBSTACLE_DENSITIES:
                width, height = map_size
                size_label = f"{width}x{height}"
                density_label = f"{int(density * 100)}%"
                
                print(f"Testing map size {size_label} with {density_label} obstacles...")
                
                # Generate map
                building_map = BuildingMap(
                    width, height,
                    obstacle_density=density,
                    seed=BenchmarkConfig.RANDOM_SEED
                )
                
                graph = Graph(building_map)
                start = building_map.start_pos
                goal = building_map.exit_pos
                
                print(f"  Map: {size_label}, Nodes: {graph.node_count()}, Obstacles: {building_map.obstacle_count()}")
                
                # Run Dijkstra
                current_test += 1
                print(f"  [{current_test}/{total_tests}] Running Dijkstra...")
                dijkstra_result = self._run_algorithm(
                    Dijkstra(graph), start, goal, 
                    building_map, density, "Dijkstra"
                )
                self.results.append(dijkstra_result)
                print(f"      Path length: {dijkstra_result.path_length}, "
                      f"Explored: {dijkstra_result.explored_nodes}, "
                      f"Time: {dijkstra_result.runtime:.4f}s")
                
                # Run A*
                current_test += 1
                print(f"  [{current_test}/{total_tests}] Running A*...")
                astar_result = self._run_algorithm(
                    AStar(graph), start, goal,
                    building_map, density, "A*"
                )
                self.results.append(astar_result)
                print(f"      Path length: {astar_result.path_length}, "
                      f"Explored: {astar_result.explored_nodes}, "
                      f"Time: {astar_result.runtime:.4f}s")
                
                # Verify both found optimal path
                if dijkstra_result.path_length != astar_result.path_length:
                    print(f"  WARNING: Path length mismatch! "
                          f"Dijkstra: {dijkstra_result.path_length}, "
                          f"A*: {astar_result.path_length}")
                
                print()
        
        print("=" * 80)
        print("BENCHMARK COMPLETE")
        print("=" * 80)
    
    def _run_algorithm(self, algorithm, start: Tuple[int, int], goal: Tuple[int, int],
                      building_map: BuildingMap, density: float, algo_name: str) -> BenchmarkResult:
        """
        Run a single algorithm and record results.
        
        Args:
            algorithm: Algorithm instance (Dijkstra or AStar)
            start: Start position
            goal: Goal position
            building_map: Building map
            density: Obstacle density
            algo_name: Algorithm name for labeling
            
        Returns:
            BenchmarkResult with metrics
        """
        # Measure runtime
        start_time = time.perf_counter()
        result = algorithm.find_path(start, goal)
        end_time = time.perf_counter()
        
        # Record result
        benchmark_result = BenchmarkResult(building_map.width, building_map.height, density, algo_name)
        benchmark_result.path_length = result.path_length
        benchmark_result.runtime = end_time - start_time
        benchmark_result.explored_nodes = result.explored_nodes
        benchmark_result.visited_nodes = result.visited_nodes
        
        return benchmark_result
    
    def save_results_csv(self, filename: str = None):
        """
        Save benchmark results to CSV.
        
        Args:
            filename: Output CSV filename (default: benchmark_results.csv)
        """
        if filename is None:
            filename = os.path.join(self.output_dir, "benchmark_results.csv")
        
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = [
                'Algorithm', 'Map_Size_X', 'Map_Size_Y', 'Map_Size', 'Map_Area', 
                'Obstacle_Density(%)', 'Path_Length', 'Runtime(s)', 'Explored_Nodes', 'Visited_Nodes'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for result in self.results:
                writer.writerow({
                    'Algorithm': result.algorithm,
                    'Map_Size_X': result.map_size_x,
                    'Map_Size_Y': result.map_size_y,
                    'Map_Size': result.map_size,
                    'Map_Area': result.map_area,
                    'Obstacle_Density(%)': int(result.obstacle_density * 100),
                    'Path_Length': round(result.path_length, 2),
                    'Runtime(s)': f"{result.runtime:.6f}",
                    'Explored_Nodes': result.explored_nodes,
                    'Visited_Nodes': result.visited_nodes
                })
        
        print(f"Results saved to: {filename}")
    
    def generate_visualizations(self):
        """Generate performance comparison visualizations."""
        print("Generating visualizations...")
        
        # Group results by algorithm and metric
        algorithms = set(r.algorithm for r in self.results)
        
        # Map sizes from results (use map_area for sorting to keep numeric)
        map_areas = sorted(set(r.map_area for r in self.results))
        
        # Runtime comparison
        runtime_data = {}
        for algo in algorithms:
            runtime_data[algo] = {}
            for area in map_areas:
                algo_results = [r for r in self.results if r.algorithm == algo and r.map_area == area]
                if algo_results:
                    # Average runtime across obstacle densities
                    avg_runtime = sum(r.runtime for r in algo_results) / len(algo_results)
                    runtime_data[algo][area] = avg_runtime
        
        Visualization.plot_runtime_comparison(
            runtime_data, map_areas,
            os.path.join(self.output_dir, "runtime_plot.png")
        )
        
        # Explored nodes comparison
        explored_data = {}
        for algo in algorithms:
            explored_data[algo] = {}
            for area in map_areas:
                algo_results = [r for r in self.results if r.algorithm == algo and r.map_area == area]
                if algo_results:
                    # Average explored nodes across obstacle densities
                    avg_explored = sum(r.explored_nodes for r in algo_results) / len(algo_results)
                    explored_data[algo][area] = int(avg_explored)
        
        Visualization.plot_explored_nodes_comparison(
            explored_data, map_areas,
            os.path.join(self.output_dir, "explored_nodes_plot.png")
        )
        
        # Path length comparison
        path_data = {}
        for algo in algorithms:
            path_data[algo] = {}
            for area in map_areas:
                algo_results = [r for r in self.results if r.algorithm == algo and r.map_area == area]
                if algo_results:
                    # Average path length
                    avg_path = sum(r.path_length for r in algo_results if r.path_length != float('inf')) / len([x for x in algo_results if x.path_length != float('inf')])
                    path_data[algo][area] = avg_path
        
        Visualization.plot_path_length_comparison(
            path_data, map_areas,
            os.path.join(self.output_dir, "path_length_plot.png")
        )
        
        # Obstacle density impact
        densities = sorted(set(r.obstacle_density for r in self.results))
        
        # Runtime vs density (fixed map size - largest)
        large_area = max(map_areas)
        runtime_vs_density = {}
        for algo in algorithms:
            runtime_vs_density[algo] = {}
            for density in densities:
                algo_results = [r for r in self.results 
                               if r.algorithm == algo and r.map_area == large_area and r.obstacle_density == density]
                if algo_results:
                    runtime_vs_density[algo][density] = algo_results[0].runtime
        
        Visualization.plot_obstacle_density_impact(
            runtime_vs_density, densities,
            os.path.join(self.output_dir, "obstacle_density_runtime.png"),
            metric_name="Runtime (seconds)"
        )
        
        # Explored nodes vs density
        explored_vs_density = {}
        for algo in algorithms:
            explored_vs_density[algo] = {}
            for density in densities:
                algo_results = [r for r in self.results 
                               if r.algorithm == algo and r.map_area == large_area and r.obstacle_density == density]
                if algo_results:
                    explored_vs_density[algo][density] = algo_results[0].explored_nodes
        
        Visualization.plot_obstacle_density_impact(
            explored_vs_density, densities,
            os.path.join(self.output_dir, "obstacle_density_explored.png"),
            metric_name="Explored Nodes"
        )
        
        print("Visualizations saved!")
    
    def generate_sample_maps(self):
        """Generate visualization of sample evacuation maps."""
        print("Generating sample map visualizations...")
        
        # Ensure sample_paths directory exists
        sample_paths_dir = os.path.join(self.output_dir, "sample_paths")
        os.makedirs(sample_paths_dir, exist_ok=True)
        
        # Generate maps for each density
        for density in BenchmarkConfig.OBSTACLE_DENSITIES:
            building_map = BuildingMap(
                100, 100,
                obstacle_density=density,
                seed=BenchmarkConfig.RANDOM_SEED
            )
            
            graph = Graph(building_map)
            start = building_map.start_pos
            goal = building_map.exit_pos
            
            # Run both algorithms
            dijkstra_algo = Dijkstra(graph)
            dijkstra_result = dijkstra_algo.find_path(start, goal)
            
            astar_algo = AStar(graph)
            astar_result = astar_algo.find_path(start, goal)
            
            # Visualize Dijkstra result
            density_label = f"{int(density * 100)}"
            filename = os.path.join(sample_paths_dir, 
                                   f"dijkstra_path_{density_label}percent.png")
            Visualization.plot_map(
                building_map,
                path=dijkstra_result.path,
                explored_cells=None,  # Could add explored cells visualization
                title=f"Dijkstra - {density_label}% Obstacles (Path length: {dijkstra_result.path_length:.0f})",
                filename=filename
            )
            
            # Visualize A* result
            filename = os.path.join(sample_paths_dir,
                                   f"astar_path_{density_label}percent.png")
            Visualization.plot_map(
                building_map,
                path=astar_result.path,
                explored_cells=None,
                title=f"A* - {density_label}% Obstacles (Path length: {astar_result.path_length:.0f})",
                filename=filename
            )
        
        print("Sample maps saved!")
    
    def print_summary(self):
        """Print summary statistics."""
        if not self.results:
            return
        
        print("\n" + "=" * 80)
        print("BENCHMARK SUMMARY")
        print("=" * 80)
        
        # Group by algorithm
        for algo in sorted(set(r.algorithm for r in self.results)):
            algo_results = [r for r in self.results if r.algorithm == algo]
            
            print(f"\n{algo} Algorithm:")
            print(f"  Total tests: {len(algo_results)}")
            print(f"  Avg runtime: {sum(r.runtime for r in algo_results) / len(algo_results):.6f}s")
            print(f"  Avg explored nodes: {sum(r.explored_nodes for r in algo_results) / len(algo_results):.0f}")
            print(f"  Total path length: {sum(r.path_length for r in algo_results):.0f}")
        
        # Comparison
        dijkstra_results = [r for r in self.results if r.algorithm == "Dijkstra"]
        astar_results = [r for r in self.results if r.algorithm == "A*"]
        
        if dijkstra_results and astar_results:
            dijkstra_avg_runtime = sum(r.runtime for r in dijkstra_results) / len(dijkstra_results)
            astar_avg_runtime = sum(r.runtime for r in astar_results) / len(astar_results)
            
            dijkstra_avg_explored = sum(r.explored_nodes for r in dijkstra_results) / len(dijkstra_results)
            astar_avg_explored = sum(r.explored_nodes for r in astar_results) / len(astar_results)
            
            print(f"\nComparison:")
            print(f"  A* is {dijkstra_avg_runtime / astar_avg_runtime:.2f}x faster on average")
            print(f"  A* explores {dijkstra_avg_explored / astar_avg_explored:.2f}x fewer nodes on average")
        
        print("=" * 80)


if __name__ == "__main__":
    benchmark = Benchmark(output_dir="../results")
    benchmark.run_all_benchmarks()
    benchmark.save_results_csv()
    benchmark.generate_visualizations()
    benchmark.generate_sample_maps()
    benchmark.print_summary()
