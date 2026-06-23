class FakeNav2Client:

    def send_goal(self, pose):

        print(
            f"Fake Nav2: go to "
            f"x={pose.pose.position.x:.2f} "
            f"y={pose.pose.position.y:.2f}"
        )

        return True

    def cancel_goal(self):

        print("Fake Nav2: cancel goal")