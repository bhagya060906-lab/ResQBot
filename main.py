
import pygame
import sys

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
pygame.display.set_caption("ResQBot - Search and Rescue Simulation")

clock = pygame.time.Clock()

# Colors
BACKGROUND = (20, 25, 35)
GRID_COLOR = (45, 52, 65)
ROBOT_COLOR = (40, 140, 255)
OBSTACLE_COLOR = (220, 65, 65)
TARGET_COLOR = (40, 200, 120)
TEXT_COLOR = (240, 240, 240)

font = pygame.font.SysFont("Arial", 22)

# -----------------------------------------
# 2. ENVIRONMENT
# -----------------------------------------

# Obstacle positions are represented as (row, column)
obstacles = {
    (2, 3), (3, 3), (4, 3),
    (5, 3), (6, 3),
    (2, 7), (3, 7), (4, 7),
    (5, 7), (6, 7),
    (8, 5), (8, 6), (8, 7),
    (3, 12), (4, 12), (5, 12),
    (9, 12), (10, 12)
}

# Robot starting position
robot = [1, 1]

# Rescue target
target = (10, 15)

# -----------------------------------------
# 3. ROBOT MOVEMENT
# -----------------------------------------

def move_robot(row_change, col_change):

    new_row = robot[0] + row_change
    new_col = robot[1] + col_change

    # Check environment boundaries
    if not (0 <= new_row < ROWS):
        return

    if not (0 <= new_col < COLS):
        return

    # Check for obstacles
    if (new_row, new_col) in obstacles:
        return

    # Update robot position
    robot[0] = new_row
    robot[1] = new_col


# -----------------------------------------
# 4. DRAW ENVIRONMENT
# -----------------------------------------

def draw_environment():

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

            pygame.draw.rect(screen, GRID_COLOR, rect, 1)

    # Draw obstacles
    for row, col in obstacles:

        rect = pygame.Rect(
            col * CELL_SIZE,
            row * CELL_SIZE,
            CELL_SIZE,
            CELL_SIZE
        )

        pygame.draw.rect(screen, OBSTACLE_COLOR, rect.inflate(-5, -5))

    # Draw rescue target
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

    # Draw robot direction indicator
    pygame.draw.circle(
        screen,
        TEXT_COLOR,
        robot_rect.center,
        5
    )

    # Display status
    status = "TARGET REACHED!" if tuple(robot) == target else "MANUAL MODE"

    status_text = font.render(status, True, TEXT_COLOR)
    screen.blit(status_text, (15, HEIGHT - 35))

    controls = font.render(
        "Arrow Keys: Move Robot | ESC: Exit",
        True,
        TEXT_COLOR
    )

    screen.blit(controls, (WIDTH - 410, HEIGHT - 35))


# -----------------------------------------
# 5. MAIN GAME LOOP
# -----------------------------------------

running = True

while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                running = False

            elif event.key == pygame.K_UP:
                move_robot(-1, 0)

            elif event.key == pygame.K_DOWN:
                move_robot(1, 0)

            elif event.key == pygame.K_LEFT:
                move_robot(0, -1)

            elif event.key == pygame.K_RIGHT:
                move_robot(0, 1)

    draw_environment()

    pygame.display.flip()

    clock.tick(60)


# -----------------------------------------
# 6. CLEANUP
# -----------------------------------------

pygame.quit()
sys.exit()
