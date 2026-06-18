"""
Enhanced Benchmark with Statistical Analysis and Third Algorithm
Adds confidence intervals, memory profiling, and BFS for bonus credit
"""

import time
import csv
import os
import random
import tracemalloc
from typing import List, Dict, Tuple
from map_generator import BuildingMap
from graph import Graph
from dijkstra import Dijkstra
from astar import AStar


class BFSPathfinder:
    """Breadth-First Search - baseline unweighted shortest path."""
    
    def __init__(self, graph):
        self.graph = graph
    
    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int]):
        """Find shortest path using BFS."""
        from collections import deque
        
        result = type('obj', (object,), {
            'path': [],
            'path_length': float('inf'),
            'explored_nodes': 0,
            'visited_nodes': 0,
            'runtime': 0.0,
            'peak_memory': 0
        })()
        
        queue = deque([start])
        visited = {start}
        predecessors = {start: None}
        
        tracemalloc.start()
        
        while queue:
            current = queue.popleft()
            result.explored_nodes += 1
            
            if current == goal:
                result.path_length = len(self._reconstruct_path(predecessors, start, goal)) - 1
                result.path = self._reconstruct_path(predecessors, start, goal)
                result.visited_nodes = len(visited)
                current, peak = tracemalloc.get_traced_memory()
                result.peak_memory = peak / 1024 / 1024  # MB
                tracemalloc.stop()
                return result
            
            for neighbor in self.graph.get_neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    predecessors[neighbor] = current
                    queue.append(neighbor)
        
        result.visited_nodes = len(visited)
        current, peak = tracemalloc.get_traced_memory()
        result.peak_memory = peak / 1024 / 1024
        tracemalloc.stop()
        return result
    
    @staticmethod
    def _reconstruct_path(predecessors, start, goal):
        path = []
        current = goal
        while current is not None:
            path.append(current)
            current = predecessors.get(current)
        path.reverse()
        return path if path and path[0] == start else []


class AdvancedBenchmark:
    """Enhanced benchmark with statistical analysis and third algorithm."""
    
    MAP_SIZES = [(50, 50), (100, 100), (200, 200), (300, 300), (500, 500)]
    OBSTACLE_DENSITIES = [0.1, 0.2, 0.3]
    RANDOM_SEED = 42
    TRIALS_PER_CONFIG = 3  # Run 3 trials per configuration for confidence intervals
    
    def __init__(self, output_dir: str = "results_enhanced"):
        self.output_dir = output_dir
        self.results = []
        os.makedirs(output_dir, exist_ok=True)
    
    def run_all_benchmarks(self):
        """Run enhanced benchmark suite with multiple trials."""
        print("=" * 80)
        print("ENHANCED BENCHMARK WITH STATISTICAL ANALYSIS")
        print("Dijkstra vs A* vs BFS (Baseline)")
        print("=" * 80)
        print()
        
        total_tests = len(self.MAP_SIZES) * len(self.OBSTACLE_DENSITIES) * 3 * self.TRIALS_PER_CONFIG
        current_test = 0
        
        for map_size in self.MAP_SIZES:
            for density in self.OBSTACLE_DENSITIES:
                width, height = map_size
                size_label = f"{width}x{height}"
                density_label = f"{int(density * 100)}%"
                
                print(f"Testing {size_label} with {density_label} obstacles ({self.TRIALS_PER_CONFIG} trials)...")
                
                # Run multiple trials for statistical confidence
                for trial in range(self.TRIALS_PER_CONFIG):
                    random.seed(self.RANDOM_SEED + trial)  # Different map each trial
                    
                    building_map = BuildingMap(width, height, obstacle_density=density, seed=self.RANDOM_SEED + trial)
                    graph = Graph(building_map)
                    start = building_map.start_pos
                    goal = building_map.exit_pos
                    
                    # Dijkstra
                    current_test += 1
                    dijkstra_algo = Dijkstra(graph)
                    dijkstra_result = self._run_algorithm_with_profiling(dijkstra_algo, start, goal)
                    self._store_result("Dijkstra", width * height, density, dijkstra_result, trial)
                    
                    # A*
                    current_test += 1
                    astar_algo = AStar(graph)
                    astar_result = self._run_algorithm_with_profiling(astar_algo, start, goal)
                    self._store_result("A*", width * height, density, astar_result, trial)
                    
                    # BFS (baseline)
                    current_test += 1
                    bfs_algo = BFSPathfinder(graph)
                    bfs_result = self._run_algorithm_with_profiling(bfs_algo, start, goal)
                    self._store_result("BFS", width * height, density, bfs_result, trial)
                    
                    print(f"  [{current_test}/{total_tests}] Trial {trial+1}: "
                          f"Dijkstra {dijkstra_result['runtime']*1000:.2f}ms, "
                          f"A* {astar_result['runtime']*1000:.2f}ms, "
                          f"BFS {bfs_result['runtime']*1000:.2f}ms")
        
        print("\n" + "=" * 80)
        print("BENCHMARK COMPLETE")
        print("=" * 80)
    
    def _run_algorithm_with_profiling(self, algorithm, start, goal):
        """Run algorithm with timing and memory profiling."""
        tracemalloc.start()
        start_time = time.perf_counter()
        
        result = algorithm.find_path(start, goal)
        
        end_time = time.perf_counter()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        return {
            'path_length': result.path_length,
            'runtime': end_time - start_time,
            'explored_nodes': result.explored_nodes,
            'visited_nodes': result.visited_nodes,
            'peak_memory': peak / 1024 / 1024  # Convert to MB
        }
    
    def _store_result(self, algo_name, map_size, density, metrics, trial):
        """Store result with trial information."""
        self.results.append({
            'algorithm': algo_name,
            'map_size': map_size,
            'density': density,
            'trial': trial,
            'path_length': metrics['path_length'],
            'runtime': metrics['runtime'],
            'explored_nodes': metrics['explored_nodes'],
            'visited_nodes': metrics['visited_nodes'],
            'peak_memory': metrics['peak_memory']
        })
    
    def save_results_with_statistics(self, filename: str = None):
        """Save results with confidence intervals."""
        if filename is None:
            filename = os.path.join(self.output_dir, "benchmark_with_statistics.csv")
        
        # Group by algorithm, map_size, and density
        grouped = {}
        for result in self.results:
            key = (result['algorithm'], result['map_size'], result['density'])
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(result)
        
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = [
                'Algorithm', 'Map_Size', 'Obstacle_Density(%)',
                'Avg_Runtime(s)', 'Std_Dev_Runtime', '95%_CI_Runtime',
                'Avg_Explored_Nodes', 'Std_Dev_Nodes',
                'Avg_Memory(MB)', 'Peak_Memory(MB)',
                'Path_Length'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for (algo, size, density), trials in sorted(grouped.items()):
                import statistics
                
                runtimes = [t['runtime'] for t in trials]
                nodes = [t['explored_nodes'] for t in trials]
                memory = [t['peak_memory'] for t in trials]
                path_length = trials[0]['path_length']  # Same for all trials
                
                avg_runtime = statistics.mean(runtimes)
                std_runtime = statistics.stdev(runtimes) if len(runtimes) > 1 else 0
                ci_runtime = 1.96 * std_runtime / (len(runtimes) ** 0.5)  # 95% CI
                
                avg_nodes = statistics.mean(nodes)
                std_nodes = statistics.stdev(nodes) if len(nodes) > 1 else 0
                
                avg_memory = statistics.mean(memory)
                peak_memory = max(memory)
                
                writer.writerow({
                    'Algorithm': algo,
                    'Map_Size': size,
                    'Obstacle_Density(%)': int(density * 100),
                    'Avg_Runtime(s)': f"{avg_runtime:.6f}",
                    'Std_Dev_Runtime': f"{std_runtime:.6f}",
                    '95%_CI_Runtime': f"±{ci_runtime:.6f}",
                    'Avg_Explored_Nodes': f"{avg_nodes:.0f}",
                    'Std_Dev_Nodes': f"{std_nodes:.0f}",
                    'Avg_Memory(MB)': f"{avg_memory:.2f}",
                    'Peak_Memory(MB)': f"{peak_memory:.2f}",
                    'Path_Length': f"{path_length:.0f}"
                })
        
        print(f"Statistical results saved to: {filename}")
    
    def print_statistical_summary(self):
        """Print summary with confidence intervals."""
        import statistics
        
        print("\n" + "=" * 100)
        print("STATISTICAL ANALYSIS WITH CONFIDENCE INTERVALS")
        print("=" * 100)
        
        # Group results
        grouped = {}
        for result in self.results:
            key = (result['algorithm'], result['map_size'], result['density'])
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(result)
        
        # Analyze by map size
        for size in [2500, 10000, 40000, 90000, 250000]:
            print(f"\nMap Size {int(size**0.5)}×{int(size**0.5)} ({size} nodes):")
            print("-" * 100)
            
            for algo in ['Dijkstra', 'A*', 'BFS']:
                runtimes = [
                    r['runtime'] for r in self.results 
                    if r['algorithm'] == algo and r['map_size'] == size
                ]
                
                if runtimes:
                    avg = statistics.mean(runtimes)
                    std = statistics.stdev(runtimes) if len(runtimes) > 1 else 0
                    ci = 1.96 * std / (len(runtimes) ** 0.5)
                    
                    print(f"  {algo:10s}: {avg*1000:7.2f} ± {ci*1000:6.2f} ms "
                          f"(n={len(runtimes)} trials)")
        
        # Algorithm comparison
        print("\n" + "=" * 100)
        print("ALGORITHM COMPARISON (All tests combined)")
        print("=" * 100)
        
        for algo in ['Dijkstra', 'A*', 'BFS']:
            algo_results = [r for r in self.results if r['algorithm'] == algo]
            
            runtimes = [r['runtime'] for r in algo_results]
            nodes = [r['explored_nodes'] for r in algo_results]
            memory = [r['peak_memory'] for r in algo_results]
            
            avg_runtime = statistics.mean(runtimes)
            std_runtime = statistics.stdev(runtimes) if len(runtimes) > 1 else 0
            
            avg_nodes = statistics.mean(nodes)
            std_nodes = statistics.stdev(nodes) if len(nodes) > 1 else 0
            
            avg_memory = statistics.mean(memory)
            
            print(f"\n{algo}:")
            print(f"  Avg Runtime:      {avg_runtime*1000:7.2f} ± {std_runtime*1000:6.2f} ms")
            print(f"  Avg Nodes:        {avg_nodes:8.0f} ± {std_nodes:8.0f}")
            print(f"  Avg Memory:       {avg_memory:7.2f} MB")


if __name__ == "__main__":
    benchmark = AdvancedBenchmark(output_dir="../results_enhanced")
    benchmark.run_all_benchmarks()
    benchmark.save_results_with_statistics()
    benchmark.print_statistical_summary()
