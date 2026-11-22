
import unittest
import pygame

from analytics.metrics import MissionMetrics


class TestMissionMetrics(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pygame.init()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        self.metrics = MissionMetrics()

    def test_initial_status(self):
        self.assertEqual(
            self.metrics.mission_status,
            "NOT STARTED"
        )

    def test_start_mission(self):
        self.metrics.start_mission()

        self.assertEqual(
            self.metrics.mission_status,
            "IN PROGRESS"
        )

    def test_record_movement(self):
        self.metrics.record_movement()
        self.metrics.record_movement()

        self.assertEqual(
            self.metrics.distance_travelled,
            2
        )

    def test_update_path_length(self):
        path = [
            (0, 0),
            (0, 1),
            (1, 1),
            (2, 1)
        ]

        self.metrics.update_path_length(path)

        self.assertEqual(
            self.metrics.path_length,
            3
        )

    def test_empty_path(self):
        self.metrics.update_path_length(None)

        self.assertEqual(
            self.metrics.path_length,
            0
        )

    def test_navigation_mode(self):
        self.metrics.update_navigation_mode(True)

        self.assertEqual(
            self.metrics.navigation_mode,
            "AUTONOMOUS"
        )

        self.metrics.update_navigation_mode(False)

        self.assertEqual(
            self.metrics.navigation_mode,
            "MANUAL"
        )

    def test_complete_mission(self):
        self.metrics.complete_mission()

        self.assertEqual(
            self.metrics.mission_status,
            "COMPLETED"
        )


if __name__ == "__main__":
    unittest.main()
