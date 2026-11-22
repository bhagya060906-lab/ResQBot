
import pygame


class MissionMetrics:
    """
    Tracks the performance of a ResQBot rescue mission.
    """

    def __init__(self):
        self.start_time = pygame.time.get_ticks()

        self.distance_travelled = 0
        self.obstacles_detected = 0
        self.path_length = 0

        self.mission_status = "NOT STARTED"
        self.navigation_mode = "MANUAL"

    def start_mission(self):
        """Mark the mission as running."""
        self.mission_status = "IN PROGRESS"

    def record_movement(self):
        """Record one successful grid-cell movement."""
        self.distance_travelled += 1

    def update_obstacles(self, count):
        """Update the number of detected static obstacles."""
        self.obstacles_detected = count

    def update_path_length(self, path):
        """Update the currently calculated path length."""
        if path:
            self.path_length = len(path) - 1
        else:
            self.path_length = 0

    def update_navigation_mode(self, autonomous):
        """Record the current navigation mode."""
        if autonomous:
            self.navigation_mode = "AUTONOMOUS"
        else:
            self.navigation_mode = "MANUAL"

    def complete_mission(self):
        """Mark the mission as completed."""
        self.mission_status = "COMPLETED"

    def get_elapsed_time(self):
        """Return elapsed mission time in seconds."""
        current_time = pygame.time.get_ticks()
        elapsed_ms = current_time - self.start_time

        return elapsed_ms / 1000
