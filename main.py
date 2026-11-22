
import pygame
import sys
import numpy as np

from perception.detection import detect_objects
from navigation.path_planner import build_navigation_map
from simulation.dynamic_obstacle import DynamicObstacle
from analytics.metrics import MissionMetrics


# -----------------------------------------
# 1. INITIALIZATION
# -----------------------------------------

pygame.init()

WIDTH = 900
HEIGHT = 650
CELL_SIZE = 50

ROWS = HEIGHT // CELL_SIZE
COLS = WIDTH // CELL_SIZE

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(
    "ResQBot - Search and Rescue Simulation"
)

clock = pygame.time.Clock()

MOVE_INTERVAL_MS = 300
last_move_time = 0

# Colors
BACKGROUND = (20, 25, 35)
GRID_COLOR = (45, 52, 65)
ROBOT_COLOR = (40, 140, 255)
OBSTACLE_COLOR = (220, 65, 65)
TARGET_COLOR = (40, 200, 120)
TEXT_COLOR = (240, 240, 240)
DYNAMIC_COLOR = (255, 150, 40)

font = pygame.font.SysFont("Arial", 22)
small_font = pygame.font.SysFont("Arial", 18)


# -----------------------------------------
# 2. ENVIRONMENT
# -----------------------------------------

obstacles = {
    (2, 3), (3, 3), (4, 3),
    (5, 3), (6, 3),

    (2, 7), (3, 7), (4, 7),
    (5, 7), (6, 7),

    (8, 5), (8, 6), (8, 7),

    (3, 12), (4, 12), (5, 12),

    (9, 12), (10, 12)
}

robot = [1, 1]
target = (10, 15)

# Moving obstacle with a wider movement range
dynamic_obstacle = DynamicObstacle(
    row=7,
    start_col=5,
    min_col=5,
    max_col=15,
    interval_ms=500
)

autonomous_mode = False

# Mission analytics
metrics = MissionMetrics()
metrics.start_mission()

# Track path changes
previous_path = None
path_recalculations = 0


# -----------------------------------------
# 3. ROBOT MOVEMENT
# -----------------------------------------

def move_robot(row_change, col_change):

    new_row = robot[0] + row_change
    new_col = robot[1] + col_change

    if not (0 <= new_row < ROWS):
        return False

    if not (0 <= new_col < COLS):
        return False

    new_position = (new_row, new_col)

    if new_position in obstacles:
        return False

    if new_position == dynamic_obstacle.position:
        return False

    robot[0] = new_row
    robot[1] = new_col

    metrics.record_movement()

    return True


# -----------------------------------------
# 4. DRAW ENVIRONMENT
# -----------------------------------------

def draw_environment(status):

    screen.fill(BACKGROUND)

    # Draw grid
    for row in range(ROWS):
        for col in range(COLS):

            rect = pygame.Rect(
                col * CELL_SIZE,
                row * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE
            )

            pygame.draw.rect(
                screen,
                GRID_COLOR,
                rect,
                1
            )

    # Draw static obstacles
    for row, col in obstacles:

        rect = pygame.Rect(
            col * CELL_SIZE,
            row * CELL_SIZE,
            CELL_SIZE,
            CELL_SIZE
        )

        pygame.draw.rect(
            screen,
            OBSTACLE_COLOR,
            rect.inflate(-5, -5)
        )

    # Draw dynamic obstacle
    dynamic_row, dynamic_col = dynamic_obstacle.position

    dynamic_rect = pygame.Rect(
        dynamic_col * CELL_SIZE,
        dynamic_row * CELL_SIZE,
        CELL_SIZE,
        CELL_SIZE
    )

    pygame.draw.rect(
        screen,
        DYNAMIC_COLOR,
        dynamic_rect.inflate(-5, -5)
    )

    # Draw target
    target_rect = pygame.Rect(
        target[1] * CELL_SIZE,
        target[0] * CELL_SIZE,
        CELL_SIZE,
        CELL_SIZE
    )

    pygame.draw.circle(
        screen,
        TARGET_COLOR,
        target_rect.center,
        CELL_SIZE // 3
    )

    # Draw robot
    robot_rect = pygame.Rect(
        robot[1] * CELL_SIZE,
        robot[0] * CELL_SIZE,
        CELL_SIZE,
        CELL_SIZE
    )

    pygame.draw.rect(
        screen,
        ROBOT_COLOR,
        robot_rect.inflate(-10, -10),
        border_radius=10
    )

    pygame.draw.circle(
        screen,
        TEXT_COLOR,
        robot_rect.center,
        5
    )

    # Status
    status_text = font.render(
        status,
        True,
        TEXT_COLOR
    )

    screen.blit(
        status_text,
        (15, HEIGHT - 35)
    )

    controls = small_font.render(
        "A: Auto | Arrow Keys: Manual | ESC: Exit",
        True,
        TEXT_COLOR
    )

    screen.blit(
        controls,
        (WIDTH - 390, HEIGHT - 35)
    )


# -----------------------------------------
# 5. ANALYTICS DASHBOARD
# -----------------------------------------

def draw_dashboard(detections, navigation_path):

    elapsed_time = metrics.get_elapsed_time()

    obstacle_count = (
        len(detections["obstacle"]) + 1
    )

    metrics.update_obstacles(obstacle_count)
    metrics.update_path_length(navigation_path)
    metrics.update_navigation_mode(autonomous_mode)

    dashboard_data = [
        f"MISSION: {metrics.mission_status}",
        f"TIME: {elapsed_time:.1f} sec",
        f"DISTANCE: {metrics.distance_travelled} cells",
        f"PATH LENGTH: {metrics.path_length} cells",
        f"OBSTACLES: {metrics.obstacles_detected}",
        f"MODE: {metrics.navigation_mode}",
        f"PATH CHANGES: {path_recalculations}"
    ]

    panel = pygame.Surface((300, 195))
    panel.set_alpha(210)
    panel.fill((10, 15, 25))

    screen.blit(panel, (WIDTH - 310, 45))

    for index, item in enumerate(dashboard_data):

        dashboard_text = small_font.render(
            item,
            True,
            TEXT_COLOR
        )

        screen.blit(
            dashboard_text,
            (WIDTH - 300, 53 + index * 25)
        )


# -----------------------------------------
# 6. MAIN GAME LOOP
# -----------------------------------------

running = True

while running:

    # -------------------------------------
    # A. EVENT HANDLING
    # -------------------------------------

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                running = False

            elif event.key == pygame.K_a:

                if tuple(robot) != target:
                    autonomous_mode = not autonomous_mode

            elif event.key == pygame.K_UP:
                autonomous_mode = False
                move_robot(-1, 0)

            elif event.key == pygame.K_DOWN:
                autonomous_mode = False
                move_robot(1, 0)

            elif event.key == pygame.K_LEFT:
                autonomous_mode = False
                move_robot(0, -1)

            elif event.key == pygame.K_RIGHT:
                autonomous_mode = False
                move_robot(0, 1)

    if not running:
        break

    # -------------------------------------
    # B. UPDATE DYNAMIC OBSTACLE
    # -------------------------------------

    dynamic_obstacle.update(
        pygame.time.get_ticks()
    )

    # -------------------------------------
    # C. CHECK MISSION STATUS
    # -------------------------------------

    if tuple(robot) == target:
        autonomous_mode = False
        metrics.complete_mission()

    if metrics.mission_status == "COMPLETED":
        status = "TARGET REACHED!"
    elif autonomous_mode:
        status = "AUTONOMOUS MODE"
    else:
        status = "MANUAL MODE"

    # -------------------------------------
    # D. DRAW ENVIRONMENT
    # -------------------------------------

    draw_environment(status)

    # -------------------------------------
    # E. CAMERA CAPTURE
    # -------------------------------------

    camera_frame = pygame.surfarray.array3d(screen)

    camera_frame = np.transpose(
        camera_frame,
        (1, 0, 2)
    ).copy()

    # -------------------------------------
    # F. COMPUTER VISION
    # -------------------------------------

    detections = detect_objects(camera_frame)

    # -------------------------------------
    # G. A* PATH PLANNING
    # -------------------------------------

    navigation_path, goal, detected_obstacles = (
        build_navigation_map(
            detections,
            CELL_SIZE,
            ROWS,
            COLS,
            extra_obstacles={dynamic_obstacle.position}
        )
    )

    # Count actual changes in the calculated route
    if navigation_path != previous_path:
        if previous_path is not None:
            path_recalculations += 1

        previous_path = (
            list(navigation_path)
            if navigation_path
            else None
        )

    # -------------------------------------
    # H. AUTONOMOUS MOVEMENT
    # -------------------------------------

    current_time = pygame.time.get_ticks()

    if autonomous_mode:

        if navigation_path and len(navigation_path) > 1:

            if current_time - last_move_time >= MOVE_INTERVAL_MS:

                next_row, next_col = navigation_path[1]

                row_change = next_row - robot[0]
                col_change = next_col - robot[1]

                moved = move_robot(
                    row_change,
                    col_change
                )

                if moved:
                    last_move_time = current_time

        elif not navigation_path:
            status = "PATH BLOCKED - WAITING"

    # -------------------------------------
    # I. DRAW A* PATH
    # -------------------------------------

    if navigation_path:

        for row, col in navigation_path:

            center = (
                col * CELL_SIZE + CELL_SIZE // 2,
                row * CELL_SIZE + CELL_SIZE // 2
            )

            pygame.draw.circle(
                screen,
                (255, 215, 0),
                center,
                7
            )

    # -------------------------------------
    # J. DRAW DETECTION BOXES
    # -------------------------------------

    detection_colours = {
        "obstacle": (255, 120, 120),
        "target": (100, 255, 150),
        "robot": (100, 180, 255)
    }

    for label, objects in detections.items():

        for obj in objects:

            x, y, width, height = obj["bbox"]

            pygame.draw.rect(
                screen,
                detection_colours[label],
                (x, y, width, height),
                2
            )

    # -------------------------------------
    # K. DRAW ANALYTICS
    # -------------------------------------

    draw_dashboard(
        detections,
        navigation_path
    )

    # -------------------------------------
    # L. REFRESH DISPLAY
    # -------------------------------------

    pygame.display.flip()

    clock.tick(60)


# -----------------------------------------
# 7. CLEANUP
# -----------------------------------------

pygame.quit()
sys.exit()
