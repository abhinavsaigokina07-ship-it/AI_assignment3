import heapq
from collections import defaultdict

INDIA_ROAD_GRAPH = {
    "Delhi": [("Jaipur", 281), ("Agra", 233), ("Chandigarh", 274), ("Lucknow", 555), ("Amritsar", 452)],
    "Jaipur": [("Delhi", 281), ("Agra", 240), ("Jodhpur", 335), ("Udaipur", 395), ("Ajmer", 135)],
    "Agra": [("Delhi", 233), ("Jaipur", 240), ("Lucknow", 363), ("Gwalior", 119), ("Kanpur", 288)],
    "Mumbai": [("Pune", 149), ("Surat", 284), ("Nashik", 167), ("Aurangabad", 335), ("Goa", 597)],
    "Pune": [("Mumbai", 149), ("Nashik", 211), ("Aurangabad", 235), ("Hyderabad", 559), ("Kolhapur", 228)],
    "Chennai": [("Bangalore", 346), ("Hyderabad", 627), ("Madurai", 462), ("Coimbatore", 497), ("Tirupati", 138)],
    "Kolkata": [("Bhubaneswar", 440), ("Patna", 600), ("Siliguri", 595), ("Asansol", 200), ("Ranchi", 392)],
    "Bangalore": [("Chennai", 346), ("Hyderabad", 570), ("Mysore", 145), ("Coimbatore", 365), ("Pune", 838)],
    "Hyderabad": [("Bangalore", 570), ("Chennai", 627), ("Pune", 559), ("Nagpur", 503), ("Warangal", 148)],
    "Ahmedabad": [("Surat", 266), ("Jaipur", 656), ("Mumbai", 524), ("Vadodara", 113), ("Gandhinagar", 30)],
    "Lucknow": [("Delhi", 555), ("Agra", 363), ("Kanpur", 83), ("Varanasi", 322), ("Allahabad", 208)],
    "Chandigarh": [("Delhi", 274), ("Amritsar", 229), ("Shimla", 116), ("Ludhiana", 95), ("Jalandhar", 146)],
    "Patna": [("Kolkata", 600), ("Varanasi", 294), ("Ranchi", 333), ("Muzaffarpur", 74), ("Gaya", 100)],
    "Bhopal": [("Indore", 197), ("Nagpur", 356), ("Gwalior", 426), ("Jabalpur", 297), ("Ujjain", 189)],
    "Nagpur": [("Bhopal", 356), ("Hyderabad", 503), ("Jabalpur", 307), ("Amravati", 150), ("Wardha", 75)],
    "Indore": [("Bhopal", 197), ("Ujjain", 55), ("Ahmedabad", 395), ("Mumbai", 590), ("Gwalior", 482)],
    "Varanasi": [("Lucknow", 322), ("Patna", 294), ("Allahabad", 128), ("Gorakhpur", 258), ("Gaya", 241)],
    "Amritsar": [("Delhi", 452), ("Chandigarh", 229), ("Jalandhar", 81), ("Ludhiana", 141)],
    "Surat": [("Mumbai", 284), ("Ahmedabad", 266), ("Vadodara", 153), ("Nashik", 229)],
    "Jodhpur": [("Jaipur", 335), ("Udaipur", 250), ("Ajmer", 201), ("Bikaner", 250), ("Barmer", 200)],
    "Kochi": [("Coimbatore", 200), ("Thiruvananthapuram", 219), ("Madurai", 312), ("Kozhikode", 186), ("Thrissur", 74)],
    "Coimbatore": [("Chennai", 497), ("Bangalore", 365), ("Madurai", 213), ("Kochi", 200), ("Salem", 165)],
    "Madurai": [("Chennai", 462), ("Coimbatore", 213), ("Kochi", 312), ("Tirunelveli", 157), ("Trichy", 137)],
    "Thiruvananthapuram": [("Kochi", 219), ("Madurai", 360), ("Nagercoil", 87)],
    "Bhubaneswar": [("Kolkata", 440), ("Cuttack", 27), ("Visakhapatnam", 450), ("Ranchi", 550)],
    "Visakhapatnam": [("Bhubaneswar", 450), ("Vijayawada", 352), ("Hyderabad", 620), ("Rajahmundry", 196)],
    "Vijayawada": [("Visakhapatnam", 352), ("Hyderabad", 278), ("Chennai", 427), ("Tirupati", 291)],
    "Ranchi": [("Kolkata", 392), ("Patna", 333), ("Bhubaneswar", 550), ("Asansol", 210)],
    "Guwahati": [("Siliguri", 320), ("Shillong", 100), ("Dibrugarh", 440), ("Jorhat", 311)],
    "Siliguri": [("Kolkata", 595), ("Guwahati", 320), ("Patna", 651), ("Darjeeling", 77)],
    "Gwalior": [("Agra", 119), ("Bhopal", 426), ("Jhansi", 102), ("Indore", 482)],
    "Jabalpur": [("Nagpur", 307), ("Bhopal", 297), ("Allahabad", 393), ("Raipur", 398)],
    "Raipur": [("Nagpur", 294), ("Jabalpur", 398), ("Bhubaneswar", 630), ("Bilaspur", 113)],
    "Dehradun": [("Delhi", 302), ("Chandigarh", 186), ("Haridwar", 54), ("Rishikesh", 43)],
    "Haridwar": [("Dehradun", 54), ("Delhi", 219), ("Rishikesh", 21), ("Meerut", 175)],
    "Allahabad": [("Lucknow", 208), ("Varanasi", 128), ("Patna", 302), ("Jabalpur", 393)],
    "Kanpur": [("Lucknow", 83), ("Agra", 288), ("Allahabad", 190), ("Delhi", 488)],
    "Nashik": [("Mumbai", 167), ("Pune", 211), ("Surat", 229), ("Aurangabad", 183)],
    "Aurangabad": [("Mumbai", 335), ("Pune", 235), ("Nashik", 183), ("Nagpur", 514), ("Hyderabad", 549)],
    "Mysore": [("Bangalore", 145), ("Coimbatore", 210), ("Ooty", 128)],
    "Shimla": [("Chandigarh", 116), ("Dehradun", 183), ("Manali", 278)],
    "Udaipur": [("Jaipur", 395), ("Jodhpur", 250), ("Ahmedabad", 257), ("Ajmer", 280)],
    "Ajmer": [("Jaipur", 135), ("Jodhpur", 201), ("Udaipur", 280)],
    "Tirupati": [("Chennai", 138), ("Bangalore", 265), ("Vijayawada", 291)],
    "Vadodara": [("Ahmedabad", 113), ("Surat", 153), ("Mumbai", 401)],
    "Gandhinagar": [("Ahmedabad", 30)],
    "Ludhiana": [("Chandigarh", 95), ("Amritsar", 141), ("Jalandhar", 54)],
    "Jalandhar": [("Chandigarh", 146), ("Amritsar", 81), ("Ludhiana", 54)],
    "Muzaffarpur": [("Patna", 74), ("Gaya", 155)],
    "Gaya": [("Patna", 100), ("Varanasi", 241), ("Muzaffarpur", 155)],
    "Gorakhpur": [("Varanasi", 258), ("Lucknow", 273)],
    "Jhansi": [("Gwalior", 102), ("Agra", 235), ("Bhopal", 357)],
    "Ujjain": [("Indore", 55), ("Bhopal", 189)],
    "Amravati": [("Nagpur", 150), ("Aurangabad", 358)],
    "Wardha": [("Nagpur", 75), ("Amravati", 80)],
    "Kolhapur": [("Pune", 228), ("Goa", 367)],
    "Goa": [("Mumbai", 597), ("Pune", 457), ("Kolhapur", 367)],
    "Bikaner": [("Jodhpur", 250), ("Jaipur", 330), ("Delhi", 463)],
    "Barmer": [("Jodhpur", 200)],
    "Nagercoil": [("Thiruvananthapuram", 87), ("Madurai", 254)],
    "Salem": [("Coimbatore", 165), ("Chennai", 333), ("Trichy", 148)],
    "Trichy": [("Madurai", 137), ("Chennai", 326), ("Salem", 148), ("Coimbatore", 218)],
    "Tirunelveli": [("Madurai", 157), ("Thiruvananthapuram", 213)],
    "Kozhikode": [("Kochi", 186), ("Coimbatore", 210)],
    "Thrissur": [("Kochi", 74), ("Kozhikode", 113)],
    "Ooty": [("Mysore", 128), ("Coimbatore", 86)],
    "Cuttack": [("Bhubaneswar", 27), ("Kolkata", 452)],
    "Rajahmundry": [("Visakhapatnam", 196), ("Vijayawada", 177)],
    "Warangal": [("Hyderabad", 148), ("Visakhapatnam", 474)],
    "Asansol": [("Kolkata", 200), ("Ranchi", 210)],
    "Shillong": [("Guwahati", 100)],
    "Dibrugarh": [("Guwahati", 440), ("Jorhat", 130)],
    "Jorhat": [("Guwahati", 311), ("Dibrugarh", 130)],
    "Darjeeling": [("Siliguri", 77)],
    "Bilaspur": [("Raipur", 113), ("Nagpur", 380)],
    "Rishikesh": [("Dehradun", 43), ("Haridwar", 21)],
    "Meerut": [("Delhi", 72), ("Haridwar", 175), ("Agra", 198)],
    "Manali": [("Shimla", 278), ("Chandigarh", 306)],
}


def dijkstra(graph, source):
    distances = {node: float('inf') for node in graph}
    distances[source] = 0
    predecessors = {node: None for node in graph}
    visited = set()
    priority_queue = [(0, source)]
    nodes_expanded = 0

    while priority_queue:
        current_dist, current_node = heapq.heappop(priority_queue)
        if current_node in visited:
            continue
        visited.add(current_node)
        nodes_expanded += 1

        for neighbor, weight in graph.get(current_node, []):
            if neighbor not in visited:
                new_dist = current_dist + weight
                if new_dist < distances.get(neighbor, float('inf')):
                    distances[neighbor] = new_dist
                    predecessors[neighbor] = current_node
                    heapq.heappush(priority_queue, (new_dist, neighbor))

    return distances, predecessors, nodes_expanded


def reconstruct_path(predecessors, source, target):
    path = []
    current = target
    while current is not None:
        path.append(current)
        current = predecessors[current]
    path.reverse()
    if path[0] == source:
        return path
    return []


def find_shortest_path(source, target):
    if source not in INDIA_ROAD_GRAPH:
        raise ValueError(f"City '{source}' not found in graph.")
    if target not in INDIA_ROAD_GRAPH:
        raise ValueError(f"City '{target}' not found in graph.")

    distances, predecessors, nodes_expanded = dijkstra(INDIA_ROAD_GRAPH, source)
    path = reconstruct_path(predecessors, source, target)
    total_distance = distances[target]

    return {
        "source": source,
        "target": target,
        "path": path,
        "total_distance_km": total_distance,
        "nodes_expanded": nodes_expanded,
        "path_length": len(path),
    }


def find_all_distances(source):
    if source not in INDIA_ROAD_GRAPH:
        raise ValueError(f"City '{source}' not found in graph.")

    distances, predecessors, nodes_expanded = dijkstra(INDIA_ROAD_GRAPH, source)
    reachable = {k: v for k, v in distances.items() if v < float('inf') and k != source}
    sorted_distances = sorted(reachable.items(), key=lambda x: x[1])

    return {
        "source": source,
        "distances": sorted_distances,
        "nodes_expanded": nodes_expanded,
        "reachable_cities": len(reachable),
    }


def print_path_result(result):
    print(f"\n{'='*55}")
    print(f"  SOURCE : {result['source']}")
    print(f"  TARGET : {result['target']}")
    print(f"{'='*55}")
    if result['path']:
        print(f"  SHORTEST PATH   : {' -> '.join(result['path'])}")
        print(f"  TOTAL DISTANCE  : {result['total_distance_km']} km")
        print(f"  CITIES IN PATH  : {result['path_length']}")
    else:
        print("  No path found between these cities.")
    print(f"  NODES EXPANDED  : {result['nodes_expanded']}")
    print(f"{'='*55}\n")


def print_all_distances(result, top_n=15):
    print(f"\n{'='*55}")
    print(f"  ALL SHORTEST DISTANCES FROM: {result['source']}")
    print(f"  Reachable cities: {result['reachable_cities']}")
    print(f"  Nodes expanded  : {result['nodes_expanded']}")
    print(f"{'='*55}")
    print(f"  {'CITY':<25} {'DISTANCE (km)':>15}")
    print(f"  {'-'*40}")
    for city, dist in result['distances'][:top_n]:
        print(f"  {city:<25} {dist:>15}")
    if len(result['distances']) > top_n:
        print(f"  ... and {len(result['distances']) - top_n} more cities")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    result1 = find_shortest_path("Delhi", "Chennai")
    print_path_result(result1)

    result2 = find_shortest_path("Mumbai", "Kolkata")
    print_path_result(result2)

    result3 = find_shortest_path("Amritsar", "Kochi")
    print_path_result(result3)

    result4 = find_all_distances("Bangalore")
    print_all_distances(result4, top_n=20)
