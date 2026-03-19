import heapq
import random
import time
import math
from dataclasses import dataclass, field
from typing import Optional

GRID_SIZE = 70
CELL_KM = 1.0

DENSITY_LOW = 0.10
DENSITY_MEDIUM = 0.25
DENSITY_HIGH = 0.40

OBSTACLE = 1
FREE = 0

MOVES_8DIR = [
    (-1, 0, 1.0), (1, 0, 1.0), (0, -1, 1.0), (0, 1, 1.0),
    (-1, -1, math.sqrt(2)), (-1, 1, math.sqrt(2)),
    (1, -1, math.sqrt(2)), (1, 1, math.sqrt(2)),
]


@dataclass(order=True)
class AStarNode:
    f: float
    g: float = field(compare=False)
    row: int = field(compare=False)
    col: int = field(compare=False)
    parent: Optional[object] = field(default=None, compare=False)


def generate_grid(size, density, seed=None):
    if seed is not None:
        random.seed(seed)
    grid = [[FREE] * size for _ in range(size)]
    for r in range(size):
        for c in range(size):
            if random.random() < density:
                grid[r][c] = OBSTACLE
    return grid


def heuristic(r1, c1, r2, c2):
    dr = abs(r1 - r2)
    dc = abs(c1 - c2)
    return (min(dr, dc) * math.sqrt(2)) + abs(dr - dc)


def a_star(grid, start, goal):
    sr, sc = start
    gr, gc = goal

    grid[sr][sc] = FREE
    grid[gr][gc] = FREE

    start_node = AStarNode(f=heuristic(sr, sc, gr, gc), g=0.0, row=sr, col=sc)
    open_list = [start_node]
    open_set = {(sr, sc): start_node}
    closed_set = set()
    nodes_expanded = 0
    nodes_generated = 1

    while open_list:
        current = heapq.heappop(open_list)
        cr, cc = current.row, current.col

        if (cr, cc) in closed_set:
            continue

        closed_set.add((cr, cc))
        nodes_expanded += 1

        if (cr, cc) == (gr, gc):
            path = []
            node = current
            while node is not None:
                path.append((node.row, node.col))
                node = node.parent
            path.reverse()
            return path, nodes_expanded, nodes_generated, len(closed_set)

        for dr, dc, move_cost in MOVES_8DIR:
            nr, nc = cr + dr, cc + dc
            if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]):
                if grid[nr][nc] == OBSTACLE:
                    continue
                if (nr, nc) in closed_set:
                    continue
                new_g = current.g + move_cost
                h = heuristic(nr, nc, gr, gc)
                new_f = new_g + h
                if (nr, nc) in open_set and open_set[(nr, nc)].g <= new_g:
                    continue
                new_node = AStarNode(f=new_f, g=new_g, row=nr, col=nc, parent=current)
                heapq.heappush(open_list, new_node)
                open_set[(nr, nc)] = new_node
                nodes_generated += 1

    return None, nodes_expanded, nodes_generated, len(closed_set)


def compute_moe(path, grid, nodes_expanded, nodes_generated, elapsed_time, grid_size, density):
    if path is None:
        return None

    path_length_cells = len(path) - 1
    path_length_km = sum(
        math.sqrt((path[i+1][0] - path[i][0])**2 + (path[i+1][1] - path[i][1])**2) * CELL_KM
        for i in range(path_length_cells)
    )

    straight_line_km = math.sqrt(
        (path[-1][0] - path[0][0])**2 + (path[-1][1] - path[0][1])**2
    ) * CELL_KM

    path_optimality_ratio = straight_line_km / path_length_km if path_length_km > 0 else 0

    total_cells = grid_size * grid_size
    obstacle_count = sum(grid[r][c] == OBSTACLE for r in range(grid_size) for c in range(grid_size))
    search_efficiency = nodes_expanded / total_cells

    return {
        "path_length_cells": path_length_cells,
        "path_length_km": round(path_length_km, 3),
        "straight_line_distance_km": round(straight_line_km, 3),
        "path_optimality_ratio": round(path_optimality_ratio, 4),
        "nodes_expanded": nodes_expanded,
        "nodes_generated": nodes_generated,
        "search_efficiency": round(search_efficiency, 4),
        "computation_time_ms": round(elapsed_time * 1000, 3),
        "obstacle_density": density,
        "total_obstacles": obstacle_count,
        "grid_size": f"{grid_size}x{grid_size}",
        "path_turns": count_turns(path),
    }


def count_turns(path):
    turns = 0
    if len(path) < 3:
        return 0
    for i in range(1, len(path) - 1):
        d1 = (path[i][0] - path[i-1][0], path[i][1] - path[i-1][1])
        d2 = (path[i+1][0] - path[i][0], path[i+1][1] - path[i][1])
        if d1 != d2:
            turns += 1
    return turns


def render_grid_ascii(grid, path, start, goal, max_display=40):
    size = len(grid)
    path_set = set(path) if path else set()
    display_size = min(size, max_display)

    print(f"\n  Grid view (top-left {display_size}x{display_size} of {size}x{size}):")
    print("  " + "+" + "-" * (display_size * 2 - 1) + "+")

    for r in range(display_size):
        row_str = "  |"
        for c in range(display_size):
            if (r, c) == start:
                row_str += "S "
            elif (r, c) == goal:
                row_str += "G "
            elif (r, c) in path_set:
                row_str += ". "
            elif grid[r][c] == OBSTACLE:
                row_str += "# "
            else:
                row_str += "  "
        print(row_str.rstrip() + "|")

    print("  " + "+" + "-" * (display_size * 2 - 1) + "+")
    print("  Legend:  S=Start  G=Goal  .=Path  #=Obstacle")


def print_moe(moe):
    print(f"\n  {'MEASURE OF EFFECTIVENESS':^45}")
    print(f"  {'='*45}")
    metrics = [
        ("Grid Size",               moe["grid_size"]),
        ("Obstacle Density",        f"{moe['obstacle_density']*100:.0f}%"),
        ("Total Obstacles",         moe["total_obstacles"]),
        ("Path Length (cells)",     moe["path_length_cells"]),
        ("Path Length (km)",        f"{moe['path_length_km']} km"),
        ("Straight-line Dist (km)", f"{moe['straight_line_distance_km']} km"),
        ("Path Optimality Ratio",   f"{moe['path_optimality_ratio']:.4f}"),
        ("Path Turns",              moe["path_turns"]),
        ("Nodes Expanded",          moe["nodes_expanded"]),
        ("Nodes Generated",         moe["nodes_generated"]),
        ("Search Efficiency",       f"{moe['search_efficiency']:.4f}"),
        ("Computation Time",        f"{moe['computation_time_ms']} ms"),
    ]
    for key, val in metrics:
        print(f"  {key:<28} {str(val):>15}")
    print(f"  {'='*45}\n")


def run_scenario(density_label, density_value, start, goal, seed=42):
    print(f"\n{'='*55}")
    print(f"  SCENARIO: {density_label} Obstacle Density ({density_value*100:.0f}%)")
    print(f"  Start: {start}   Goal: {goal}")
    print(f"{'='*55}")

    grid = generate_grid(GRID_SIZE, density_value, seed=seed)

    t0 = time.time()
    path, expanded, generated, closed = a_star(grid, start, goal)
    elapsed = time.time() - t0

    if path:
        moe = compute_moe(path, grid, expanded, generated, elapsed, GRID_SIZE, density_value)
        print_moe(moe)
        render_grid_ascii(grid, path, start, goal, max_display=30)
    else:
        print("  No path found — goal is unreachable with current obstacle placement.")
        print(f"  Nodes expanded: {expanded}, Time: {elapsed*1000:.2f} ms\n")


if __name__ == "__main__":
    start = (5, 5)
    goal = (64, 64)

    run_scenario("LOW",    DENSITY_LOW,    start, goal, seed=1)
    run_scenario("MEDIUM", DENSITY_MEDIUM, start, goal, seed=2)
    run_scenario("HIGH",   DENSITY_HIGH,   start, goal, seed=3)
