class SearchBehavior:

    def __init__(self):

        self.waypoints = [

            (0.0, 0.0),

            (1.0, 0.0),

            (1.0, 1.0),

            (0.0, 1.0)

        ]

        self.index = 0

    def get_next_waypoint(self):

        wp = self.waypoints[self.index]

        self.index += 1

        self.index %= len(self.waypoints)

        return wp