
import pygame
import sys
import numpy as np

from perception.detection import detect_objects
from navigation.path_planner import build_navigation_map
from simulation.dynamic_obstacle import DynamicObstacle
from analytics.metrics import MissionMetrics


# =========================================
# 1. INITIALIZATION
# =========================================

pygame.init()

MAP_WIDTH = 900
MAP_HEIGHT = 650
PANEL_WIDTH = 300
FOOTER_HEIGHT = 50

WIDTH = MAP_WIDTH + PANEL_WIDTH
HEIGHT = MAP_HEIGHT + FOOTER_HEIGHT

CELL_SIZE = 50

ROWS = MAP_HEIGHT // CELL_SIZE
COLS = MAP_WIDTH // CELL_SIZE

screen = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.display.set_caption(
    "ResQBot | Autonomous Search and Rescue"
)

clock = pygame.time.Clock()

MOVE_INTERVAL_MS = 300
last_move_time = 0

# Colour palette
BACKGROUND = (13, 18, 30)
MAP_BACKGROUND = (19, 27, 42)
PANEL_BACKGROUND = (24, 33, 50)
GRID_COLOR = (39, 51, 70)

WHITE = (238, 243, 250)
MUTED = (145, 160, 180)

BLUE = (55, 145, 255)
DARK_BLUE = (20, 75, 145)
CYAN = (80, 220, 245)

RED = (220, 55, 65)
LIGHT_RED = (255, 225, 220)
GREEN = (40, 210, 140)
ORANGE = (255, 160, 65)
DARK_ORANGE = (160, 80, 25)
YELLOW = (255, 210, 75)

font_title = pygame.font.SysFont("Arial", 27, bold=True)
font_heading = pygame.font.SysFont("Arial", 19, bold=True)
font_normal = pygame.font.SysFont("Arial", 16)
font_small = pygame.font.SysFont("Arial", 13)


# =========================================
# 2. ENVIRONMENT
# =========================================

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

# Robot initially faces upward.
robot_heading = (-1, 0)

dynamic_obstacle = DynamicObstacle(
    row=7,
    start_col=5,
    min_col=5,
    max_col=15,
    interval_ms=500
)

autonomous_mode = False

metrics = MissionMetrics()
metrics.start_mission()

previous_path = None
path_recalculations = 0


# =========================================
# 3. HELPER FUNCTIONS
# =========================================

def draw_text(text, x, y, font, color=WHITE):
    rendered = font.render(text, True, color)
    screen.blit(rendered, (x, y))


def draw_panel_card(x, y, width, height):
    rect = pygame.Rect(x, y, width, height)

    pygame.draw.rect(
        screen,
        PANEL_BACKGROUND,
        rect,
        border_radius=10
    )


# =========================================
# 4. ROBOT MOVEMENT
# =========================================

def move_robot(row_change, col_change):
    """Move the rover while preventing obstacle collisions."""

    global robot_heading

    if metrics.mission_status == "COMPLETED":
        return False

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

    robot_heading = (row_change, col_change)

    metrics.record_movement()

    if tuple(robot) == target:
        metrics.complete_mission()

    return True


# =========================================
# 5. DRAW RESCUE ROVER
# =========================================

def draw_rover(row, col):
    """
    Draw a miniature top-down rescue rover.

    The rover has four wheels, a blue chassis,
    a front sensor and a camera indicator.
    """

    center_x = col * CELL_SIZE + CELL_SIZE // 2
    center_y = row * CELL_SIZE + CELL_SIZE // 2

    # Draw the rover on a separate transparent surface.
    rover_surface = pygame.Surface(
        (CELL_SIZE, CELL_SIZE),
        pygame.SRCALPHA
    )

    # Four wheels
    wheel_positions = [
        (7, 9),
        (35, 9),
        (7, 31),
        (35, 31)
    ]

    for wheel_x, wheel_y in wheel_positions:

        pygame.draw.rect(
            rover_surface,
            (25, 30, 40),
            (wheel_x, wheel_y, 9, 12),
            border_radius=3
        )

        pygame.draw.line(
            rover_surface,
            (100, 110, 125),
            (wheel_x + 2, wheel_y + 6),
            (wheel_x + 7, wheel_y + 6),
            1
        )

    # Main rover chassis
    pygame.draw.rect(
        rover_surface,
        BLUE,
        (12, 5, 26, 40),
        border_radius=7
    )

    # Inner chassis panel
    pygame.draw.rect(
        rover_surface,
        DARK_BLUE,
        (16, 10, 18, 30),
        border_radius=4
    )

    # Front sensor assembly
    pygame.draw.rect(
        rover_surface,
        CYAN,
        (17, 7, 16, 7),
        border_radius=3
    )

    # Camera lens
    pygame.draw.circle(
        rover_surface,
        WHITE,
        (25, 10),
        3
    )

    pygame.draw.circle(
        rover_surface,
        (20, 40, 60),
        (25, 10),
        1
    )

    # Central equipment module
    pygame.draw.rect(
        rover_surface,
        (80, 175, 255),
        (18, 20, 14, 10),
        border_radius=3
    )

    # Small status indicator
    pygame.draw.circle(
        rover_surface,
        GREEN,
        (25, 35),
        3
    )

    # Rotate according to movement direction.
    heading_angles = {
        (-1, 0): 0,
        (0, 1): -90,
        (1, 0): 180,
        (0, -1): 90
    }

    angle = heading_angles.get(robot_heading, 0)

    rotated_rover = pygame.transform.rotate(
        rover_surface,
        angle
    )

    rover_rect = rotated_rover.get_rect(
        center=(center_x, center_y)
    )

    screen.blit(
        rotated_rover,
        rover_rect
    )


# =========================================
# 6. DRAW HAZARD BARRICADE
# =========================================

def draw_hurdle(row, col):
    """
    Draw a red-and-white striped disaster-zone barricade.
    """

    x = col * CELL_SIZE
    y = row * CELL_SIZE

    # Two support posts
    pygame.draw.rect(
        screen,
        (105, 40, 45),
        (x + 8, y + 13, 7, 29),
        border_radius=2
    )

    pygame.draw.rect(
        screen,
        (105, 40, 45),
        (x + 35, y + 13, 7, 29),
        border_radius=2
    )

    # Main red barrier
    barrier = pygame.Rect(
        x + 5,
        y + 15,
        40,
        17
    )

    pygame.draw.rect(
        screen,
        RED,
        barrier,
        border_radius=3
    )

    # White hazard stripes
    pygame.draw.line(
        screen,
        LIGHT_RED,
        (x + 13, y + 17),
        (x + 20, y + 30),
        4
    )

    pygame.draw.line(
        screen,
        LIGHT_RED,
        (x + 25, y + 17),
        (x + 32, y + 30),
        4
    )

    # Dark outline
    pygame.draw.rect(
        screen,
        (120, 35, 45),
        barrier,
        1,
        border_radius=3
    )


# =========================================
# 7. DRAW MOVING HAZARD
# =========================================

def draw_dynamic_hazard(row, col):

    center_x = col * CELL_SIZE + CELL_SIZE // 2
    center_y = row * CELL_SIZE + CELL_SIZE // 2

    # Shadow
    pygame.draw.ellipse(
        screen,
        (10, 15, 25),
        (center_x - 17, center_y + 10, 34, 9)
    )

    # Barrel body
    pygame.draw.rect(
        screen,
        ORANGE,
        (center_x - 14, center_y - 16, 28, 32),
        border_radius=5
    )

    # Top rim
    pygame.draw.ellipse(
        screen,
        (255, 195, 100),
        (center_x - 14, center_y - 17, 28, 10)
    )

    # Bottom rim
    pygame.draw.arc(
        screen,
        DARK_ORANGE,
        (center_x - 14, center_y + 7, 28, 10),
        0,
        3.14,
        2
    )

    # Hazard marking
    pygame.draw.line(
        screen,
        DARK_ORANGE,
        (center_x - 9, center_y - 3),
        (center_x + 9, center_y - 3),
        3
    )

    pygame.draw.line(
        screen,
        DARK_ORANGE,
        (center_x - 9, center_y + 5),
        (center_x + 9, center_y + 5),
        3
    )


# =========================================
# 8. DRAW SIMULATION MAP
# =========================================

def draw_map():

    pygame.draw.rect(
        screen,
        MAP_BACKGROUND,
        (0, 0, MAP_WIDTH, MAP_HEIGHT)
    )

    # Grid
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

    # Static disaster-zone hurdles
    for row, col in obstacles:
        draw_hurdle(row, col)

    # Moving hazard barrel
    dynamic_row, dynamic_col = dynamic_obstacle.position

    draw_dynamic_hazard(
        dynamic_row,
        dynamic_col
    )

    # Rescue target
    target_rect = pygame.Rect(
        target[1] * CELL_SIZE,
        target[0] * CELL_SIZE,
        CELL_SIZE,
        CELL_SIZE
    )

    pygame.draw.circle(
        screen,
        GREEN,
        target_rect.center,
        18
    )

    pygame.draw.circle(
        screen,
        WHITE,
        target_rect.center,
        8
    )

    # Rescue cross
    pygame.draw.line(
        screen,
        GREEN,
        (target_rect.centerx - 5, target_rect.centery),
        (target_rect.centerx + 5, target_rect.centery),
        2
    )

    pygame.draw.line(
        screen,
        GREEN,
        (target_rect.centerx, target_rect.centery - 5),
        (target_rect.centerx, target_rect.centery + 5),
        2
    )

    # Draw miniature rover
    draw_rover(
        robot[0],
        robot[1]
    )


# =========================================
# 9. DRAW NAVIGATION PATH
# =========================================

def draw_navigation_path(path):

    if not path:
        return

    points = []

    for row, col in path:

        center = (
            col * CELL_SIZE + CELL_SIZE // 2,
            row * CELL_SIZE + CELL_SIZE // 2
        )

        points.append(center)

    if len(points) > 1:

        pygame.draw.lines(
            screen,
            YELLOW,
            False,
            points,
            3
        )

    for point in points:

        pygame.draw.circle(
            screen,
            YELLOW,
            point,
            4
        )


# =========================================
# 10. DRAW DETECTION BOXES
# =========================================

def draw_detection_boxes(detections):

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


# =========================================
# 11. DRAW CONTROL PANEL
# =========================================

def draw_dashboard(detections, navigation_path):

    panel_x = MAP_WIDTH

    pygame.draw.rect(
        screen,
        BACKGROUND,
        (panel_x, 0, PANEL_WIDTH, HEIGHT)
    )

    # Header
    draw_text(
        "ResQBot",
        panel_x + 22,
        24,
        font_title,
        BLUE
    )

    draw_text(
        "ROBOTICS RESCUE CONTROL",
        panel_x + 22,
        59,
        font_small,
        MUTED
    )

    pygame.draw.line(
        screen,
        GRID_COLOR,
        (panel_x + 20, 91),
        (WIDTH - 20, 91),
        1
    )

    # Mission status
    draw_panel_card(
        panel_x + 15,
        110,
        270,
        85
    )

    draw_text(
        "MISSION STATUS",
        panel_x + 30,
        123,
        font_small,
        MUTED
    )

    status_color = (
        GREEN
        if metrics.mission_status == "COMPLETED"
        else BLUE
    )

    draw_text(
        metrics.mission_status,
        panel_x + 30,
        151,
        font_heading,
        status_color
    )

    # Analytics
    elapsed_time = metrics.get_elapsed_time()

    metrics.update_obstacles(
        len(obstacles) + 1
    )

    metrics.update_path_length(navigation_path)
    metrics.update_navigation_mode(autonomous_mode)

    draw_text(
        "MISSION ANALYTICS",
        panel_x + 22,
        218,
        font_heading
    )

    statistics = [
        ("ELAPSED TIME", f"{elapsed_time:.1f} sec"),
        ("DISTANCE", f"{metrics.distance_travelled} cells"),
        ("PATH LENGTH", f"{metrics.path_length} cells"),
        ("OBSTACLES", str(metrics.obstacles_detected)),
        ("ROUTE UPDATES", str(path_recalculations))
    ]

    for index, (label, value) in enumerate(statistics):

        y = 258 + index * 48

        draw_panel_card(
            panel_x + 15,
            y,
            270,
            40
        )

        draw_text(
            label,
            panel_x + 28,
            y + 11,
            font_small,
            MUTED
        )

        value_surface = font_normal.render(
            value,
            True,
            WHITE
        )

        screen.blit(
            value_surface,
            (panel_x + 175, y + 10)
        )

    # Navigation mode
    draw_text(
        "NAVIGATION MODE",
        panel_x + 22,
        515,
        font_heading
    )

    mode_text = (
        "AUTONOMOUS"
        if autonomous_mode
        else "MANUAL"
    )

    mode_color = GREEN if autonomous_mode else ORANGE

    draw_panel_card(
        panel_x + 15,
        545,
        270,
        42
    )

    draw_text(
        mode_text,
        panel_x + 30,
        557,
        font_normal,
        mode_color
    )

    draw_text(
        "SYSTEM: ONLINE",
        panel_x + 22,
        615,
        font_small,
        GREEN
    )


# =========================================
# 12. DRAW LEGEND AND FOOTER
# =========================================

def draw_footer():

    pygame.draw.rect(
        screen,
        PANEL_BACKGROUND,
        (0, MAP_HEIGHT, WIDTH, FOOTER_HEIGHT)
    )

    pygame.draw.line(
        screen,
        GRID_COLOR,
        (0, MAP_HEIGHT),
        (WIDTH, MAP_HEIGHT),
        1
    )

    legend = [
        (BLUE, "RESCUE ROVER"),
        (RED, "BARRICADE"),
        (ORANGE, "MOVING HAZARD"),
        (GREEN, "RESCUE TARGET"),
        (YELLOW, "PLANNED ROUTE")
    ]

    x = 20

    for color, label in legend:

        pygame.draw.circle(
            screen,
            color,
            (x + 6, MAP_HEIGHT + 25),
            6
        )

        draw_text(
            label,
            x + 18,
            MAP_HEIGHT + 16,
            font_small,
            MUTED
        )

        x += 175


# =========================================
# 13. MAIN GAME LOOP
# =========================================

running = True

while running:

    # Event handling
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                running = False

            elif event.key == pygame.K_a:

                if metrics.mission_status != "COMPLETED":
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

    # Update moving obstacle
    blocked_positions = obstacles | {
        tuple(robot),
        target
    }

    dynamic_moved = dynamic_obstacle.update(
        pygame.time.get_ticks(),
        blocked_positions
    )

    # Mission status
    if tuple(robot) == target:
        autonomous_mode = False
        metrics.complete_mission()

    # Draw environment before camera capture
    screen.fill(BACKGROUND)
    draw_map()

    # Simulated camera capture
    camera_frame = pygame.surfarray.array3d(screen)

    camera_frame = np.transpose(
        camera_frame,
        (1, 0, 2)
    ).copy()

    # Computer vision
    detections = detect_objects(camera_frame)

    # A* path planning
    navigation_path, goal, detected_obstacles = (
        build_navigation_map(
            detections,
            CELL_SIZE,
            ROWS,
            COLS,
            extra_obstacles={dynamic_obstacle.position}
        )
    )

    # Route change tracking
    if dynamic_moved:

        if (
            navigation_path is not None
            and previous_path is not None
            and navigation_path != previous_path
        ):
            path_recalculations += 1

    previous_path = (
        list(navigation_path)
        if navigation_path
        else None
    )

    # Autonomous movement
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
            autonomous_mode = False

    # Draw navigation and detections
    draw_navigation_path(navigation_path)
    draw_detection_boxes(detections)

    # Draw dashboard and footer
    draw_dashboard(
        detections,
        navigation_path
    )

    draw_footer()

    pygame.display.flip()

    clock.tick(60)


# =========================================
# 14. CLEANUP
# =========================================

pygame.quit()
sys.exit()
