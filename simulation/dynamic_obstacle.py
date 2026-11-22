
class DynamicObstacle:
    """
    Simulates a horizontally moving obstacle.

    The obstacle reverses direction at its boundaries
    and avoids occupied cells.
    """

    def __init__(
        self,
        row,
        start_col,
        min_col,
        max_col,
        interval_ms=1200
    ):
        self.row = row
        self.col = start_col

        self.min_col = min_col
        self.max_col = max_col

        self.direction = 1
        self.interval_ms = interval_ms
        self.last_update = 0

    @property
    def position(self):
        return (self.row, self.col)

    def update(self, current_time, blocked_positions=None):
        """
        Move the obstacle if its movement interval has elapsed.

        blocked_positions contains cells the obstacle must avoid.
        Returns True if the obstacle moved, otherwise False.
        """

        if current_time - self.last_update < self.interval_ms:
            return False

        if blocked_positions is None:
            blocked_positions = set()

        next_col = self.col + self.direction

        # Reverse direction at movement boundaries.
        if next_col > self.max_col or next_col < self.min_col:
            self.direction *= -1
            next_col = self.col + self.direction

        next_position = (self.row, next_col)

        # Reverse direction if the next cell is occupied.
        if next_position in blocked_positions:
            self.direction *= -1
            next_col = self.col + self.direction
            next_position = (self.row, next_col)

        # If both directions are blocked, remain stationary.
        if (
            next_col < self.min_col
            or next_col > self.max_col
            or next_position in blocked_positions
        ):
            self.last_update = current_time
            return False

        self.col = next_col
        self.last_update = current_time

        return True
