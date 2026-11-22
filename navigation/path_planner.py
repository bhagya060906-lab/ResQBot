
from navigation.astar import astar


def build_navigation_map(detections, cell_size, rows, cols):

    obstacles = set()

    for obj in detections["obstacle"]:

        x, y = obj["center"]

        col = x // cell_size
        row = y // cell_size

        obstacles.add((row, col))

    robot_objects = detections["robot"]
    target_objects = detections["target"]

    if not robot_objects or not target_objects:
        return None, None, obstacles

    robot_x, robot_y = robot_objects[0]["center"]
    target_x, target_y = target_objects[0]["center"]

    start = (
        robot_y // cell_size,
        robot_x // cell_size
    )

    goal = (
        target_y // cell_size,
        target_x // cell_size
    )

    path = astar(
        start,
        goal,
        obstacles,
        rows,
        cols
    )

    return path, goal, obstacles
