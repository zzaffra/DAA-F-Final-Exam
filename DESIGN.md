# Design Document: Smart Emergency Evacuation System
## Comparing Dijkstra and A* Algorithms on Large-Scale Building Maps

---

## 1. Design

### 1.1 Problem Statement and Real-World Motivation (D1)

During emergencies such as fires, earthquakes, or building evacuations, occupants must quickly find the safest and shortest route to an emergency exit. In large buildings, manually determining the optimal evacuation path can be difficult, especially when obstacles block certain routes.

**Objective:** Develop a Smart Emergency Evacuation System that automatically computes the shortest evacuation path from a starting location to the nearest exit.

**System Purpose:** The system compares two widely used shortest-path algorithms, Dijkstra's Algorithm and A* Search Algorithm, to evaluate their efficiency and scalability on large-scale building maps.

#### Real-World Importance

This problem is critical because:

1. **Life Safety:** Evacuation speed directly affects human safety during emergencies
2. **Emergency Response:** Helps emergency response teams design and validate evacuation plans
3. **Building Management:** Enables smart building systems to guide occupants efficiently
4. **Urban Planning:** Informs the design of public buildings and transportation hubs
5. **Research:** Validates algorithmic approaches used in modern navigation systems

#### Application Domains

- Building management systems (commercial and residential)
- Emergency response planning and simulation
- Robotics navigation in unknown environments
- Video game pathfinding
- Network routing optimization
- Autonomous vehicle navigation

#### Project Significance

This project serves as a practical case study in graph algorithms, allowing direct comparison of two fundamental pathfinding approaches under realistic conditions. The empirical results validate theoretical complexity analysis and demonstrate the practical impact of heuristic-guided search on algorithm performance.

---

### 1.2 Formal Model (D2)

The building environment is formally represented as a weighted graph:

$$G = (V, E)$$

where:

* **V** is the set of vertices representing walkable cells in the building
* **E** is the set of edges connecting adjacent walkable cells
* **w(u,v)** is the weight function representing movement cost between adjacent cells

#### 1.2.1 Vertices (V)

Each walkable grid cell corresponds to a vertex in the graph.

**Example:**

```
Walkable vertices: {(0,0), (0,1), (0,2), (1,0), (1,1), (1,3), ...}
Excluded vertices: All obstacle cells marked as non-walkable
```

**Vertex Notation:**

Each vertex is represented as an ordered pair (x, y) where:
- x ∈ [0, width-1] (column coordinate)
- y ∈ [0, height-1] (row coordinate)

**Total number of vertices:**

$$|V| = \text{number of walkable cells}$$

For a grid with obstacle density ρ:

$$|V| \approx \text{width} \times \text{height} \times (1 - \rho)$$

#### 1.2.2 Edges (E)

An edge exists between two vertices if they are adjacent horizontally or vertically (4-directional movement).

**Edge Definition:**

$$((x,y), (x',y')) \in E \iff$$
- Both (x,y) and (x',y') are walkable
- |x - x'| + |y - y'| = 1 (adjacent cells)

**Example:**

```
Edges from vertex (x,y):
- ((x,y), (x+1,y))  [right]
- ((x,y), (x-1,y))  [left]
- ((x,y), (x,y+1))  [down]
- ((x,y), (x,y-1))  [up]
```

**Degree:**

Each vertex has at most 4 neighbors (degree ≤ 4).

**Total number of edges:**

$$|E| \approx 4|V| = 4 \times \text{number of walkable cells}$$

#### 1.2.3 Weight Function

All movements between adjacent cells have equal cost:

$$w(u,v) = 1 \quad \forall (u,v) \in E$$

This represents:
- Uniform movement difficulty across walkable areas
- No terrain variation or movement cost differences
- Same evacuation speed regardless of direction

#### 1.2.4 Source and Target Semantics

**Source Vertex (s):**
- Represents the occupant's initial position
- Starting point for evacuation
- Must be a walkable cell
- Specified as input: $s \in V$

**Target Vertex (t):**
- Represents an emergency exit location
- Destination for evacuation
- Must be a walkable cell
- Specified as input: $t \in V$

**Path Definition:**

A path P from s to t is a sequence of vertices:

$$P = (v_0, v_1, v_2, ..., v_k)$$

where:
- $v_0 = s$ (starts at source)
- $v_k = t$ (ends at target)
- $(v_i, v_{i+1}) \in E$ for all $i \in [0, k-1]$ (consecutive vertices connected by edge)

**Path Cost:**

$$\text{Cost}(P) = \sum_{i=0}^{k-1} w(v_i, v_{i+1}) = k$$

(Since all weights equal 1, path cost equals path length)

#### 1.2.5 Problem Input

The system receives as input:

1. **Grid Dimensions:**
   - Width: w ∈ [50, 500]
   - Height: h ∈ [50, 500]

2. **Obstacle Configuration:**
   - Locations of non-walkable cells
   - Obstacle density: ρ ∈ {0.1, 0.2, 0.3} (10%, 20%, 30%)
   - Generated using fixed random seed for reproducibility

3. **Source Position:**
   - Starting coordinate: s = (x_s, y_s)
   - Automatically placed in open area

4. **Target Position:**
   - Exit coordinate: t = (x_t, y_t)
   - Automatically placed in open area

#### 1.2.6 Problem Output

The system produces:

1. **Shortest Evacuation Path:**
   - Sequence of waypoints from s to t
   - Guaranteed to minimize total cost

2. **Path Cost:**
   - Minimum number of cells to traverse
   - Represents evacuation distance

3. **Runtime Metrics:**
   - Algorithm execution time (microseconds)
   - Measured using high-precision timer

4. **Search Metrics:**
   - Number of nodes explored (popped from priority queue)
   - Number of nodes visited (marked as processed)

#### 1.2.7 Optimization Objective

**Primary Objective:** Find a path P from source s to target t that minimizes:

$$\text{minimize} \quad \text{Cost}(P) = \sum_{(u,v) \in P} w(u,v)$$

**Subject to constraints:**

1. **Walkability:** All vertices in path must be walkable
   $$\forall v_i \in P: v_i \in V$$

2. **Connectivity:** Consecutive vertices must be adjacent
   $$\forall i \in [0, k-1]: (v_i, v_{i+1}) \in E$$

3. **Reachability:** Path must exist from s to t
   $$\exists P: P_0 = s \land P_k = t$$

**Secondary Objectives (for comparison):**

- Minimize runtime (wall-clock execution time)
- Minimize explored nodes (search efficiency)

---

### 1.3 Algorithm Selection and Justification (D3)

This project compares two well-established shortest-path algorithms: Dijkstra's Algorithm and A* Search Algorithm.

#### 1.3.1 Dijkstra's Algorithm

**Overview:**

Dijkstra's Algorithm computes the shortest path from a source vertex to all reachable vertices in a weighted graph with non-negative edge weights.

**Algorithm Details:**

```
1. Initialize distances: distance[s] = 0, distance[v] = ∞ for all v ≠ s
2. Add s to priority queue
3. While priority queue is not empty:
   a. Extract vertex u with minimum distance
   b. Mark u as visited
   c. If u is target, reconstruct and return path
   d. For each unvisited neighbor v of u:
      i.   Calculate tentative distance: new_dist = distance[u] + w(u,v)
      ii.  If new_dist < distance[v]:
           - Update distance[v] = new_dist
           - Update parent[v] = u
           - Add v to priority queue
4. Return path or "no path found"
```

**Why Dijkstra's Algorithm?**

Reasons for selection:

1. **Optimality Guarantee:** Always finds the optimal shortest path
2. **Benchmark Standard:** Classical algorithm for shortest-path problems
3. **Simplicity:** Easy to implement and understand
4. **Applicability:** Works on all non-negative weight graphs
5. **Comparison Baseline:** Provides reference point for evaluating A*

**Advantages:**

- ✓ Guaranteed to find optimal path
- ✓ No heuristic needed (works generally)
- ✓ Complete exploration provides search insights
- ✓ Well-understood behavior and complexity

**Disadvantages:**

- ✗ Explores many unnecessary nodes
- ✗ No directional guidance toward goal
- ✗ Performance decreases significantly with graph size
- ✗ Inefficient for large sparse graphs

**Complexity Analysis:**

Using a binary min-heap for the priority queue:

- **Time Complexity:** $O((V + E) \log V) = O(n^2 \log n)$ for n×n grid
  - V iterations of outer loop
  - Each vertex can be inserted and extracted from heap once
  - Each edge examined once
  - Heap operations: O(log V)

- **Space Complexity:** $O(V) = O(n^2)$
  - Distance dictionary: O(V)
  - Parent dictionary: O(V)
  - Priority queue: O(V) worst case

**Implementation Details:**

- Priority queue: Python's `heapq` module
- Distance tracking: Dictionary with O(1) lookup
- Parent tracking: Dictionary for path reconstruction

---

#### 1.3.2 A* Search Algorithm

**Overview:**

A* is an informed search algorithm that extends Dijkstra's Algorithm by incorporating a heuristic function estimating remaining distance to the goal. This guides the search toward the target, reducing explored nodes while maintaining optimality.

**Heuristic Function - Manhattan Distance:**

For a grid environment with 4-directional movement, the Manhattan Distance heuristic is used:

$$h(n) = |x_n - x_{goal}| + |y_n - y_{goal}|$$

**Properties of the Heuristic:**

1. **Admissibility:** The heuristic never overestimates actual cost
   $$h(n) \leq d(n, \text{goal}) \quad \forall n$$
   - This guarantees A* finds optimal path

2. **Consistency:** Satisfies the triangle inequality
   $$h(n) \leq w(n, m) + h(m) \quad \forall (n,m) \in E$$
   - This eliminates need for repeated vertex processing

3. **Computational Efficiency:** O(1) to calculate
   - Only requires arithmetic operations
   - No complex calculations needed

**Algorithm Details:**

```
1. Initialize:
   - g[s] = 0  (actual cost from start)
   - h[s] = h(s)  (estimated cost to goal)
   - f[s] = g[s] + h[s]  (total estimated cost)
2. Add s to open set and priority queue
3. While open set is not empty:
   a. Extract vertex u with minimum f-score
   b. Remove from open set, mark as visited
   c. If u is goal:
      i.  Return path with cost g[goal]
   d. For each unvisited neighbor v of u:
      i.   Calculate tentative g: new_g = g[u] + w(u,v)
      ii.  If new_g < g[v]:
           - g[v] = new_g
           - parent[v] = u
           - h[v] = h(v)
           - f[v] = g[v] + h[v]
           - Add v to open set if not already there
4. Return "no path found"
```

**Why A* Algorithm?**

Reasons for selection:

1. **Designed for Pathfinding:** Specifically engineered for goal-directed search
2. **Efficiency:** Dramatically reduces nodes explored vs. Dijkstra
3. **Practical Impact:** Widely used in industry (games, robotics, navigation)
4. **Optimality:** With admissible heuristic, finds optimal path
5. **Comparison Value:** Demonstrates power of informed search

**Advantages:**

- ✓ Finds optimal path (with admissible heuristic)
- ✓ Explores far fewer nodes than Dijkstra
- ✓ Scales better to large problems
- ✓ Heuristic provides directional guidance
- ✓ Commonly used in practice

**Disadvantages:**

- ✗ Heuristic quality affects performance
- ✗ Heuristic calculation overhead (small but non-zero)
- ✗ Less intuitive than Dijkstra
- ✗ Performance depends on problem structure

**Complexity Analysis:**

Worst-case complexity equals Dijkstra's (both examine all nodes):

- **Worst-case Time:** $O((V + E) \log V) = O(n^2 \log n)$
  - When heuristic is uninformative

- **Average-case Time:** Often dramatically better
  - Explores approximately $O(n)$ nodes for many problems
  - Effective speedup: 5-10x in practice

- **Space Complexity:** $O(V) = O(n^2)$
  - Same memory usage as Dijkstra

**Implementation Details:**

- Priority queue: Python's `heapq` module
- Heuristic: Manhattan distance (O(1) calculation)
- Open set tracking: Set data structure for O(1) membership

---

#### 1.3.3 Expected Trade-Offs

**Dijkstra's Algorithm:**

- ✓ Guaranteed optimal path
- ✓ No heuristic needed
- ✗ Explores larger portion of graph
- ✗ Slower for large maps
- → Best for: Completeness guarantee, educational baseline

**A* Search Algorithm:**

- ✓ Guaranteed optimal path (with admissible heuristic)
- ✓ Much faster in practice
- ✓ Explores fewer nodes
- ✗ Heuristic-dependent
- → Best for: Practical performance, large-scale problems

**Expected Performance Difference:**

The performance gap is expected to be particularly significant as map size increases:

| Factor | Dijkstra | A* | Impact |
|--------|----------|-----|--------|
| Path Quality | Optimal | Optimal | Same |
| Runtime | Linear with nodes | Sublinear with nodes | **A* faster** |
| Explored Nodes | All reachable | Subset toward goal | **A* fewer** |
| Heuristic Overhead | None | Minimal | Negligible |

**Theoretical Justification for A* Advantage:**

1. **Heuristic Guidance:** Manhattan distance provides tight lower bound on remaining distance
2. **Pruning Effect:** Heuristic eliminates exploration of distant nodes early
3. **Scaling:** Advantage increases with problem size (more nodes to prune)
4. **Consistency:** Manhattan distance is consistent in grid environments

---

### 1.4 Data Structures and System Architecture (D4)

#### 1.4.1 Core Data Structures

**1. Grid Representation**

```python
Grid[row][column] -> Cell Type
```

**Properties:**

- 2D array (list of lists in Python)
- Cell values: EMPTY (0), OBSTACLE (1), START (2), EXIT (3)
- Space: O(width × height)
- Access: O(1) per cell

**Justification:**

- Efficient storage and access
- Natural match for building layouts
- Easy obstacle generation
- Straightforward neighbor computation

**Example:**

```
50 x 50 grid with 20% obstacles:
- Total cells: 2,500
- Walkable cells: ~2,000
- Obstacles: ~500
- Memory: ~10 KB (minimal)
```

---

**2. Graph Representation - Implicit Adjacency**

Rather than storing a complete adjacency list or matrix, the graph is represented implicitly:

```python
Node(pos=(x,y)) -> Neighbors computed from grid
```

**Neighbor Computation:**

```python
def get_neighbors(x, y):
    neighbors = []
    for dx, dy in [(0,-1), (0,1), (-1,0), (1,0)]:
        nx, ny = x + dx, y + dy
        if is_walkable(nx, ny):
            neighbors.append((nx, ny))
    return neighbors
```

**Justification:**

- **Memory Efficiency:** For n×n grid, implicit representation uses O(n²) space vs. O(n⁴) for explicit adjacency matrix
- **Scalability:** Feasible for 500×500 grids (250,000 cells)
- **Flexibility:** Easy to modify obstacles dynamically
- **Natural Fit:** Grid structure already defines adjacency

**Example - Memory Savings:**

```
100×100 grid (10,000 nodes):
- Explicit adjacency list: 10,000 × 4 × pointer size ≈ 160 KB
- Implicit (on-demand): 0 KB (computed as needed)
```

---

**3. Priority Queue**

```python
import heapq

pq = []  # Min-heap
heapq.heappush(pq, (priority, unique_id, data))
priority, unique_id, data = heapq.heappop(pq)
```

**Properties:**

- Implementation: Binary min-heap
- Insert: O(log n)
- Extract-min: O(log n)
- Space: O(V) worst case

**Why Python's heapq:**

- ✓ Efficient O(log n) operations
- ✓ Standard library (no external dependencies)
- ✓ Well-tested and optimized
- ✓ Supports tuple comparison

**Usage in Algorithms:**

- **Dijkstra:** `(distance, unique_id, position)`
- **A*:** `(f_score, unique_id, position)` where `f = g + h`

---

**4. Distance and Cost Dictionaries**

```python
distances = {}          # pos -> cost from start
f_scores = {}          # pos -> f_score (A* only)
predecessors = {}      # pos -> parent position
visited = set()        # Set of processed nodes
```

**Properties:**

- Type: Python dictionary and set
- Lookup: O(1) average case
- Space: O(V) for each

**Justification:**

- Average O(1) access vs. O(log V) for tree structures
- Natural fit for sparse graph storage
- Easy path reconstruction
- Minimal overhead

---

**5. Node Tracking Structures**

```python
open_set = set()       # Unprocessed nodes in frontier
closed_set = set()     # Processed nodes
```

**Purpose:**

- Track search frontier
- Avoid reprocessing visited nodes
- Detect when goal is reached

**Operations:**

- Add: O(1)
- Remove: O(1)
- Membership: O(1)

---

#### 1.4.2 System Architecture

**Module-Based Design:**

```
┌─────────────────────────────────────────────────────────┐
│          SMART EMERGENCY EVACUATION SYSTEM              │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────────┐  ┌──────────────────┐            │
│  │  Map Generator   │  │   Graph Builder  │            │
│  │ (map_generator)  │  │   (graph.py)     │            │
│  └────────┬─────────┘  └────────┬─────────┘            │
│           │                     │                      │
│           └─────────┬───────────┘                      │
│                     ▼                                  │
│          ┌─────────────────────┐                       │
│          │   Graph Structure   │                       │
│          │   (nodes + edges)   │                       │
│          └─────────┬───────────┘                       │
│                    │                                   │
│        ┌───────────┼───────────┐                       │
│        │           │           │                       │
│        ▼           ▼           ▼                       │
│    ┌────────┐  ┌──────┐  ┌──────────┐                 │
│    │Dijkstra│  │ A*   │  │Benchmark │                 │
│    │Module  │  │Module│  │ Module   │                 │
│    └────┬───┘  └──┬───┘  └────┬─────┘                 │
│         │         │           │                       │
│         └─────────┼───────────┘                       │
│                   ▼                                   │
│        ┌─────────────────────┐                        │
│        │  Results & Metrics  │                        │
│        │  - Path            │                        │
│        │  - Runtime         │                        │
│        │  - Explored Nodes  │                        │
│        └────────┬────────────┘                        │
│                 │                                     │
│                 ▼                                     │
│       ┌──────────────────────┐                        │
│       │  Visualization Module│                        │
│       │  (visualization.py)  │                        │
│       └──────────────────────┘                        │
│                 │                                     │
│                 ▼                                     │
│       ┌──────────────────────┐                        │
│       │  Output Files        │                        │
│       │  - CSV results       │                        │
│       │  - Performance plots │                        │
│       │  - Path maps         │                        │
│       └──────────────────────┘                        │
│                                                       │
└─────────────────────────────────────────────────────────┘
```

**Module Responsibilities:**

**1. map_generator.py**

```python
class BuildingMap:
    def __init__(width, height, obstacle_density, seed)
    def get_walkable_cells() -> Set[Tuple[int,int]]
    def get_neighbors(x, y) -> List[Tuple[int,int]]
    def is_walkable(x, y) -> bool
```

Functions:
- Generate random obstacle patterns
- Track start and exit positions
- Provide neighbor queries
- Ensure connectivity

---

**2. graph.py**

```python
class Graph:
    def __init__(building_map)
    def get_neighbors(pos) -> List[Tuple[int,int]]
    def get_edge_cost(pos1, pos2) -> float
    def manhattan_distance(pos1, pos2) -> float
```

Functions:
- Represent building map as graph
- Store node references
- Compute heuristic values
- Provide graph queries

---

**3. dijkstra.py**

```python
class Dijkstra:
    def __init__(graph)
    def find_path(start, goal) -> DijkstraResult
    @staticmethod
    def _reconstruct_path(predecessors, start, goal)
```

Functions:
- Implement Dijkstra algorithm
- Track metrics during search
- Reconstruct optimal path
- Return comprehensive result

---

**4. astar.py**

```python
class AStar:
    def __init__(graph, heuristic=None)
    def find_path(start, goal) -> AStarResult
    @staticmethod
    def _reconstruct_path(predecessors, start, goal)
```

Functions:
- Implement A* algorithm
- Apply Manhattan heuristic
- Track metrics during search
- Return comprehensive result

---

**5. benchmark.py**

```python
class Benchmark:
    def __init__(output_dir)
    def run_all_benchmarks()
    def save_results_csv(filename)
    def generate_visualizations()
    def generate_sample_maps()
    def print_summary()
```

Functions:
- Execute full test suite
- Manage configurations
- Collect results
- Generate outputs

---

**6. visualization.py**

```python
class Visualization:
    @staticmethod
    def plot_map(building_map, path, title, filename)
    @staticmethod
    def plot_runtime_comparison(results, sizes, filename)
    @staticmethod
    def plot_explored_nodes_comparison(results, sizes, filename)
    @staticmethod
    def plot_obstacle_density_impact(results, densities, filename)
```

Functions:
- Create path visualizations
- Generate performance plots
- Produce analysis figures
- Save results as images

---

#### 1.4.3 Data Flow

**Execution Flow:**

```
1. Initialization
   ├─ Load configuration (map sizes, densities)
   ├─ Initialize benchmark tracker
   └─ Create output directories

2. For each map size:
   └─ For each obstacle density:
      ├─ Generate building map
      │  ├─ Create grid with obstacles
      │  ├─ Place start position
      │  └─ Place exit position
      │
      ├─ Build graph
      │  ├─ Create nodes for walkable cells
      │  └─ Identify edges (neighbors)
      │
      ├─ Run Dijkstra
      │  ├─ Start timer
      │  ├─ Execute algorithm
      │  ├─ Stop timer
      │  └─ Record metrics
      │
      ├─ Run A*
      │  ├─ Start timer
      │  ├─ Execute algorithm
      │  ├─ Stop timer
      │  └─ Record metrics
      │
      └─ Store results
         ├─ Path length
         ├─ Runtime
         ├─ Explored nodes
         └─ Visited nodes

3. Post-Processing
   ├─ Save results to CSV
   ├─ Generate visualizations
   │  ├─ Runtime plots
   │  ├─ Efficiency plots
   │  └─ Sample maps
   └─ Print summary statistics
```

---

#### 1.4.4 Memory Layout

**For a 500×500 map with 20% obstacles:**

```
Building Map (Grid):
  - Size: 500 × 500 = 250,000 cells
  - Memory: 250,000 bytes ≈ 244 KB
  - Walkable cells: ~200,000

Graph Structure:
  - Node objects: 200,000 × ~100 bytes = ~20 MB
  - Edge references: 200,000 × 4 pointers = ~6.4 MB

Algorithm Runtime (each):
  - Distances dict: 200,000 entries = ~16 MB
  - Predecessors dict: 200,000 entries = ~16 MB
  - Priority queue: ~200,000 entries = ~16 MB
  - Visited set: ~200,000 entries = ~16 MB
  - Total per algorithm: ~64 MB

Total Peak Memory: ~100 MB
```

---

#### 1.4.5 Algorithmic Integration

**Common Code Path:**

```python
def run_algorithm(algorithm, graph, start, goal):
    """Generic algorithm runner."""
    start_time = time.perf_counter()
    result = algorithm.find_path(start, goal)
    end_time = time.perf_counter()
    
    result.runtime = end_time - start_time
    return result
```

**Result Object (Same interface):**

```python
class Result:
    path: List[Tuple[int,int]]      # Waypoints
    path_length: float               # Total cost
    explored_nodes: int              # Nodes processed
    visited_nodes: int               # Nodes marked visited
    runtime: float                   # Execution time
```

---

### 1.5 Implementation Details

#### Priority Queue Usage

**Dijkstra's Algorithm:**

```python
# Store: (distance, unique_id, position)
heapq.heappush(pq, (cost, id(position), position))
current_cost, _, current_pos = heapq.heappop(pq)
```

**A* Algorithm:**

```python
# Store: (f_score, unique_id, position)
# where f_score = g_score + h_score
heapq.heappush(pq, (f, id(position), position))
f, _, current_pos = heapq.heappop(pq)
```

The `unique_id` ensures consistent ordering when priorities are equal.

---

#### Heuristic Function - Manhattan Distance

**Formula:**

$$h(n) = |x_n - x_{goal}| + |y_n - y_{goal}|$$

**Python Implementation:**

```python
def manhattan_distance(pos1, pos2):
    x1, y1 = pos1
    x2, y2 = pos2
    return abs(x1 - x2) + abs(y1 - y2)
```

**Properties:**

- **Admissible:** Always ≤ actual remaining cost
- **Consistent:** Satisfies triangle inequality
- **Computational:** O(1) - just arithmetic
- **Appropriate:** Designed for grid-based movement

---

#### Path Reconstruction

**Algorithm:**

```python
def reconstruct_path(predecessors, start, goal):
    path = []
    current = goal
    
    while current is not None:
        path.append(current)
        current = predecessors.get(current)
    
    path.reverse()
    return path
```

**Example:**

```
Predecessors: {(1,1): (0,1), (0,1): (0,0), (0,0): None, ...}

Reconstruction from goal=(1,1):
  (1,1) -> (0,1) -> (0,0) -> None
  Reversed: [(0,0), (0,1), (1,1)]
```

---

### 1.6 Summary of Design Decisions

**Grid Representation:**
- ✓ 2D array for natural building layout modeling
- ✓ Implicit graph avoids O(n⁴) adjacency matrix

**Data Structures:**
- ✓ Python `heapq` for efficient priority queue operations
- ✓ Dictionaries for O(1) node tracking
- ✓ Sets for O(1) membership checking

**Algorithm Selection:**
- ✓ Dijkstra: Classical reference point
- ✓ A*: Modern practical approach
- ✓ Manhattan distance: Appropriate grid heuristic

**Architecture:**
- ✓ Modular design: Each component independent
- ✓ Flexible interfaces: Easy to extend
- ✓ Comprehensive metrics: Detailed performance analysis

**Reproducibility:**
- ✓ Fixed random seed: Deterministic results
- ✓ High-precision timing: Accurate measurements
- ✓ CSV export: Raw data availability

---

## 2. Implementation Status

All design elements have been successfully implemented:

### Implemented Components

1. ✅ **Map Generator** (map_generator.py)
   - Grid-based building representation
   - Random obstacle generation with configurable density
   - Start and exit placement
   - Corridor-based generation for connectivity

2. ✅ **Graph Module** (graph.py)
   - Graph representation from building maps
   - Neighbor querying
   - Manhattan distance heuristic

3. ✅ **Dijkstra's Algorithm** (dijkstra.py)
   - Full manual implementation
   - Priority queue-based search
   - Comprehensive result tracking
   - Path reconstruction

4. ✅ **A* Search Algorithm** (astar.py)
   - Full manual implementation
   - Heuristic-guided search
   - Manhattan distance application
   - Identical interface to Dijkstra

5. ✅ **Benchmark Suite** (benchmark.py)
   - 30 test configurations
   - Automated execution
   - CSV result export
   - Comparison analysis

6. ✅ **Visualization** (visualization.py)
   - Runtime comparison plots
   - Search efficiency analysis
   - Path visualization
   - Impact analysis plots

---

**Design Document Version:** 1.0  
**Project Status:** Complete and Benchmarked  
**Last Updated:** June 2026
