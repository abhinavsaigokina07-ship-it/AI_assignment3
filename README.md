# AI_assignment3
Module 1 — Dijkstra (Indian Road Network)
Finds the shortest road path between any two Indian cities using a priority queue. Covers ~78 cities across all regions with approximate road distances in kilometres.\

Module 2 — UGV Static Obstacles (A*)
Simulates a ground vehicle navigating a 70×70 km grid battlefield. Obstacles are randomly generated at three density levels (10%, 25%, 40%) and are fully known before the search begins. The vehicle moves in 8 directions.
After each run it prints a Measures of Effectiveness table covering path length, optimality ratio, nodes expanded, and computation time, plus an ASCII map of the path.

Module 3 — UGV Dynamic Obstacles (D* Lite)
Same grid setup, but obstacles can appear or disappear during navigation. D* Lite repairs only the affected parts of the path tree after each change rather than replanning from scratch, making it suitable for real-time use.
Prints per-event replan times and a full MOE summary at the end.
