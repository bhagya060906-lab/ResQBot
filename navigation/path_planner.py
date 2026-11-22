
from navigation.astar import astar


def get_grid_cells(bbox, cell_size, rows, cols):
    """Convert an object's bounding box into occupied grid cells."""

    x, y, width, height = bbox

    start_col = x // cell_size
    end_col = (x + width - 1) // cell_size

    start_row = y // cell_size
    end_row = (y + height - 1) // cell_size

    occupied_cells = set()

    for row in range(start_row, end_row + 1):
        for col in range(start_col, end_col + 1):
            if 0 <= row < rows and 0 <= col < cols:
                occupied_cells.add((row, col))

    return occupied_cells


def build_navigation_map(
    detections,
    cell_size,
    rows,
    cols,
    extra_obstacles=None
):
    """Build the occupancy grid and calculate an A* route."""

    obstacles = set()

    for obj in detections["obstacle"]:
        obstacles.update(
            get_grid_cells(
                obj["bbox"],
                cell_size,
                rows,
                cols
            )
        )

    # Add simulated or externally supplied obstacles
    if extra_obstacles:
        obstacles.update(extra_obstacles)

    robot_objects = detections["robot"]
    target_objects = detections["target"]

    if not robot_objects or not target_objects:
        return None, None, obstacles

    robot_x, robot_y = robot_objects[0]["center"]
    target_x, target_y = target_objects[0]["center"]

    start = (robot_y // cell_size, robot_x // cell_size)
    goal = (target_y // cell_size, target_x // cell_size)

    if not (
        0 <= start[0] < rows
        and 0 <= start[1] < cols
        and 0 <= goal[0] < rows
        and 0 <= goal[1] < cols
    ):
        return None, goal, obstacles

    # The robot's current cell must not be treated as blocked
    obstacles.discard(start)

    path = astar(
        start,
        goal,
        obstacles,
        rows,
        cols
    )

    return path, goal, obstacles
