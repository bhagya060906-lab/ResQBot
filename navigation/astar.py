
import heapq


def heuristic(a, b):
    """Calculate Manhattan distance."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar(start, goal, obstacles, rows, cols):

    if start in obstacles or goal in obstacles:
        return None

    open_set = []

    heapq.heappush(open_set, (heuristic(start, goal), 0, start))

    came_from = {}
    g_score = {start: 0}
    closed_set = set()

    directions = [
        (-1, 0),
        (1, 0),
        (0, -1),
        (0, 1)
    ]

    while open_set:

        f_score, current_g, current = heapq.heappop(open_set)

        if current in closed_set:
            continue

        if current_g != g_score.get(current):
            continue

        if current == goal:

            path = [current]

            while current in came_from:
                current = came_from[current]
                path.append(current)

            path.reverse()
            return path

        closed_set.add(current)

        for dr, dc in directions:

            neighbor = (
                current[0] + dr,
                current[1] + dc
            )

            row, col = neighbor

            if not (0 <= row < rows and 0 <= col < cols):
                continue

            if neighbor in obstacles or neighbor in closed_set:
                continue

            tentative_g = current_g + 1

            if tentative_g < g_score.get(neighbor, float("inf")):

                came_from[neighbor] = current
                g_score[neighbor] = tentative_g

                new_f = tentative_g + heuristic(neighbor, goal)

                heapq.heappush(
                    open_set,
                    (new_f, tentative_g, neighbor)
                )

    return None
