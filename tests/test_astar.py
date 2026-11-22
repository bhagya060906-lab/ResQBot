
import unittest

from navigation.astar import astar


class TestAStar(unittest.TestCase):

    def test_finds_path_without_obstacles(self):
        path = astar(
            start=(0, 0),
            goal=(4, 4),
            obstacles=set(),
            rows=5,
            cols=5
        )

        self.assertIsNotNone(path)
        self.assertEqual(path[0], (0, 0))
        self.assertEqual(path[-1], (4, 4))

    def test_avoids_obstacles(self):
        obstacles = {
            (1, 0)
        }

        path = astar(
            start=(0, 0),
            goal=(2, 0),
            obstacles=obstacles,
            rows=3,
            cols=3
        )

        self.assertIsNotNone(path)

        for cell in path:
            self.assertNotIn(cell, obstacles)

    def test_returns_none_when_goal_is_blocked(self):
        path = astar(
            start=(0, 0),
            goal=(2, 2),
            obstacles={(2, 2)},
            rows=3,
            cols=3
        )

        self.assertIsNone(path)

    def test_returns_none_when_no_path_exists(self):
        obstacles = {
            (0, 1),
            (1, 0)
        }

        path = astar(
            start=(0, 0),
            goal=(2, 2),
            obstacles=obstacles,
            rows=3,
            cols=3
        )

        self.assertIsNone(path)

    def test_start_equals_goal(self):
        path = astar(
            start=(2, 2),
            goal=(2, 2),
            obstacles=set(),
            rows=5,
            cols=5
        )

        self.assertEqual(path, [(2, 2)])


if __name__ == "__main__":
    unittest.main()
