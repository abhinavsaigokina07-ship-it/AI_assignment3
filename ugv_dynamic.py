import heapq
import random
import time
import math
from dataclasses import dataclass, field
from typing import Optional, Dict, Tuple, List, Set

GRID_SIZE = 70
CELL_KM = 1.0
INF = float('inf')

OBSTACLE = 1
FREE = 0

MOVES_8DIR = [
    (-1, 0, 1.0), (1, 0, 1.0), (0, -1, 1.0), (0, 1, 1.0),
    (-1, -1, math.sqrt(2)), (-1, 1, math.sqrt(2)),
    (1, -1, math.sqrt(2)), (1, 1, math.sqrt(2)),
]


def generate_base_grid(size, density, seed=None):
    if seed is not None:
        random.seed(seed)
    grid = [[FREE] * size for _ in range(size)]
    for r in range(size):
        for c in range(size):
            if random.random() < density:
                grid[r][c] = OBSTACLE
    return grid


def heuristic(r1, c1, r2, c2):
    dr, dc = abs(r1 - r2), abs(c1 - c2)
    return min(dr, dc) * math.sqrt(2) + abs(dr - dc)


def successors(grid, r, c):
    result = []
    for dr, dc, cost in MOVES_8DIR:
        nr, nc = r + dr, c + dc
        if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]):
            if grid[nr][nc] == FREE:
                result.append((nr, nc, cost))
    return result


class DStarLite:
    def __init__(self, grid, start, goal):
        self.grid = [row[:] for row in grid]
        self.start = start
        self.goal = goal
        self.size = len(grid)
        self.km = 0.0
        self.g: Dict[Tuple, float] = {}
        self.rhs: Dict[Tuple, float] = {}
        self.open_heap: List = []
        self.open_set: Dict[Tuple, Tuple] = {}
        self.replans = 0
        self.nodes_expanded_total = 0
        self.dynamic_events = []

        for r in range(self.size):
            for c in range(self.size):
                self.g[(r, c)] = INF
                self.rhs[(r, c)] = INF

        self.rhs[self.goal] = 0.0
        k = self._calc_key(self.goal)
        heapq.heappush(self.open_heap, (k, self.goal))
        self.open_set[self.goal] = k

    def _calc_key(self, s):
        g_rhs = min(self.g[s], self.rhs[s])
        k1 = g_rhs + heuristic(self.start[0], self.start[1], s[0], s[1]) + self.km
        k2 = g_rhs
        return (k1, k2)

    def _update_vertex(self, u):
        if u != self.goal:
            min_rhs = INF
            for dr, dc, cost in MOVES_8DIR:
                nr, nc = u[0] + dr, u[1] + dc
                if 0 <= nr < self.size and 0 <= nc < self.size:
                    if self.grid[nr][nc] == FREE:
                        val = cost + self.g[(nr, nc)]
                        if val < min_rhs:
                            min_rhs = val
            self.rhs[u] = min_rhs

        if u in self.open_set:
            del self.open_set[u]

        if self.g[u] != self.rhs[u]:
            k = self._calc_key(u)
            heapq.heappush(self.open_heap, (k, u))
            self.open_set[u] = k

    def _compute_shortest_path(self):
        expanded = 0
        while self.open_heap:
            k_old, u = heapq.heappop(self.open_heap)
            if u not in self.open_set or self.open_set[u] != k_old:
                continue

            k_new = self._calc_key(u)
            s_key = self._calc_key(self.start)

            if k_old < s_key or self.rhs[self.start] != self.g[self.start]:
                if k_old < k_new:
                    heapq.heappush(self.open_heap, (k_new, u))
                    self.open_set[u] = k_new
                elif self.g[u] > self.rhs[u]:
                    self.g[u] = self.rhs[u]
                    del self.open_set[u]
                    for dr, dc, _ in MOVES_8DIR:
                        nr, nc = u[0] + dr, u[1] + dc
                        if 0 <= nr < self.size and 0 <= nc < self.size:
                            self._update_vertex((nr, nc))
                    expanded += 1
                else:
                    self.g[u] = INF
                    self._update_vertex(u)
                    for dr, dc, _ in MOVES_8DIR:
                        nr, nc = u[0] + dr, u[1] + dc
                        if 0 <= nr < self.size and 0 <= nc < self.size:
                            self._update_vertex((nr, nc))
                    expanded += 1
            else:
                break

        self.nodes_expanded_total += expanded
        return expanded

    def initialize(self):
        self.grid[self.start[0]][self.start[1]] = FREE
        self.grid[self.goal[0]][self.goal[1]] = FREE
        self._compute_shortest_path()

    def extract_path(self):
        path = [self.start]
        current = self.start
        visited = set()
        visited.add(current)

        while current != self.goal:
            best_next = None
            best_cost = INF
            for dr, dc, move_cost in MOVES_8DIR:
                nr, nc = current[0] + dr, current[1] + dc
                if 0 <= nr < self.size and 0 <= nc < self.size:
                    if self.grid[nr][nc] == FREE and (nr, nc) not in visited:
                        total = move_cost + self.g[(nr, nc)]
                        if total < best_cost:
                            best_cost = total
                            best_next = (nr, nc)

            if best_next is None or best_cost >= INF:
                return None
            current = best_next
            visited.add(current)
            path.append(current)
            if len(path) > self.size * self.size:
                return None

        return path

    def update_obstacles(self, new_obstacles: List[Tuple[int, int]], removed_obstacles: List[Tuple[int, int]]):
        last_start = self.start
        changed_cells = []

        for (r, c) in new_obstacles:
            if self.grid[r][c] == FREE and (r, c) != self.start and (r, c) != self.goal:
                self.grid[r][c] = OBSTACLE
                changed_cells.append((r, c))

        for (r, c) in removed_obstacles:
            if self.grid[r][c] == OBSTACLE:
                self.grid[r][c] = FREE
                changed_cells.append((r, c))

        if not changed_cells:
            return 0

        self.km += heuristic(last_start[0], last_start[1], self.start[0], self.start[1])

        for cell in changed_cells:
            self._update_vertex(cell)
            for dr, dc, _ in MOVES_8DIR:
                nr, nc = cell[0] + dr, cell[1] + dc
                if 0 <= nr < self.size and 0 <= nc < self.size:
                    self._update_vertex((nr, nc))

        expanded = self._compute_shortest_path()
        self.replans += 1
        return expanded

    def advance_start(self, new_start: Tuple[int, int]):
        self.start = new_start


def generate_dynamic_events(grid_size, num_steps, num_new_per_step, num_remove_per_step, seed=100):
    random.seed(seed)
    events = []
    for _ in range(num_steps):
        new_obs = [
            (random.randint(1, grid_size - 2), random.randint(1, grid_size - 2))
            for _ in range(num_new_per_step)
        ]
        rem_obs = [
            (random.randint(1, grid_size - 2), random.randint(1, grid_size - 2))
            for _ in range(num_remove_per_step)
        ]
        events.append((new_obs, rem_obs))
    return events


def count_path_turns(path):
    turns = 0
    if len(path) < 3:
        return 0
    for i in range(1, len(path) - 1):
        d1 = (path[i][0] - path[i-1][0], path[i][1] - path[i-1][1])
        d2 = (path[i+1][0] - path[i][0], path[i+1][1] - path[i][1])
        if d1 != d2:
            turns += 1
    return turns


def compute_path_km(path):
    return sum(
        math.sqrt((path[i+1][0] - path[i][0])**2 + (path[i+1][1] - path[i][1])**2) * CELL_KM
        for i in range(len(path) - 1)
    )


def render_dynamic_grid_ascii(grid, path, start, goal, new_obs, max_display=35):
    size = len(grid)
    path_set = set(path) if path else set()
    new_obs_set = set(new_obs)
    display_size = min(size, max_display)

    print(f"\n  Grid view (top-left {display_size}x{display_size} after dynamic event):")
    print("  " + "+" + "-" * (display_size * 2 - 1) + "+")

    for r in range(display_size):
        row_str = "  |"
        for c in range(display_size):
            if (r, c) == start:
                row_str += "S "
            elif (r, c) == goal:
                row_str += "G "
            elif (r, c) in new_obs_set and grid[r][c] == OBSTACLE:
                row_str += "X "
            elif (r, c) in path_set:
                row_str += ". "
            elif grid[r][c] == OBSTACLE:
                row_str += "# "
            else:
                row_str += "  "
        print(row_str.rstrip() + "|")

    print("  " + "+" + "-" * (display_size * 2 - 1) + "+")
    print("  Legend:  S=Start  G=Goal  .=Path  #=Obstacle  X=New Dynamic Obstacle\n")


def print_dynamic_moe(stats):
    print(f"\n  {'DYNAMIC UGV - MEASURES OF EFFECTIVENESS':^50}")
    print(f"  {'='*50}")
    rows = [
        ("Grid Size",                    stats["grid_size"]),
        ("Base Obstacle Density",        f"{stats['base_density']*100:.0f}%"),
        ("Dynamic Events Processed",     stats["dynamic_events"]),
        ("Total Replanning Episodes",    stats["replans"]),
        ("Total Nodes Expanded",         stats["nodes_expanded_total"]),
        ("Path Length (cells)",          stats["path_cells"]),
        ("Path Length (km)",             f"{stats['path_km']:.3f} km"),
        ("Straight-line Distance (km)",  f"{stats['straight_km']:.3f} km"),
        ("Path Optimality Ratio",        f"{stats['optimality']:.4f}"),
        ("Path Turns",                   stats["turns"]),
        ("Total Computation Time",       f"{stats['time_ms']:.3f} ms"),
        ("Avg Replan Time",              f"{stats['avg_replan_ms']:.3f} ms"),
    ]
    for key, val in rows:
        print(f"  {key:<35} {str(val):>13}")
    print(f"  {'='*50}\n")


def run_dynamic_ugv(base_density=0.15, num_dynamic_events=5, new_per_event=8, remove_per_event=3, seed=42):
    print(f"\n{'='*60}")
    print(f"  DYNAMIC UGV NAVIGATION — D* Lite Algorithm")
    print(f"  Base density: {base_density*100:.0f}%  |  Dynamic events: {num_dynamic_events}")
    print(f"{'='*60}")

    start = (5, 5)
    goal = (64, 64)

    base_grid = generate_base_grid(GRID_SIZE, base_density, seed=seed)
    planner = DStarLite(base_grid, start, goal)

    t0 = time.time()
    planner.initialize()
    init_time = time.time() - t0

    events = generate_dynamic_events(GRID_SIZE, num_dynamic_events, new_per_event, remove_per_event, seed=seed+1)
    replan_times = []
    all_new_obs = []

    for i, (new_obs, rem_obs) in enumerate(events):
        all_new_obs.extend(new_obs)
        t1 = time.time()
        planner.update_obstacles(new_obs, rem_obs)
        replan_times.append(time.time() - t1)
        print(f"  Event {i+1}: +{len(new_obs)} obstacles, -{len(rem_obs)} obstacles removed. Replan: {replan_times[-1]*1000:.2f} ms")

    total_time = time.time() - t0
    final_path = planner.extract_path()

    if final_path:
        path_km = compute_path_km(final_path)
        straight_km = math.sqrt((goal[0]-start[0])**2 + (goal[1]-start[1])**2) * CELL_KM
        optimality = straight_km / path_km if path_km > 0 else 0

        stats = {
            "grid_size": f"{GRID_SIZE}x{GRID_SIZE}",
            "base_density": base_density,
            "dynamic_events": num_dynamic_events,
            "replans": planner.replans,
            "nodes_expanded_total": planner.nodes_expanded_total,
            "path_cells": len(final_path) - 1,
            "path_km": path_km,
            "straight_km": straight_km,
            "optimality": optimality,
            "turns": count_path_turns(final_path),
            "time_ms": total_time * 1000,
            "avg_replan_ms": (sum(replan_times) / len(replan_times) * 1000) if replan_times else 0,
        }
        print_dynamic_moe(stats)
        render_dynamic_grid_ascii(planner.grid, final_path, start, goal, all_new_obs, max_display=30)
    else:
        print("  Path not found after dynamic updates — goal may be surrounded by obstacles.")
        print(f"  Total replans: {planner.replans}, Nodes expanded: {planner.nodes_expanded_total}\n")


if __name__ == "__main__":
    run_dynamic_ugv(base_density=0.15, num_dynamic_events=5, new_per_event=8, remove_per_event=3, seed=42)
    run_dynamic_ugv(base_density=0.20, num_dynamic_events=10, new_per_event=12, remove_per_event=5, seed=77)
