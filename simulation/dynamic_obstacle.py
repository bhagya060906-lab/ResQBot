
class DynamicObstacle:
    """
    Simulates a moving obstacle that travels horizontally
    between two grid boundaries.
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

    def update(self, current_time):

        if current_time - self.last_update < self.interval_ms:
            return

        next_col = self.col + self.direction

        if next_col > self.max_col:
            self.direction = -1

        elif next_col < self.min_col:
            self.direction = 1

        self.col += self.direction
        self.last_update = current_time
