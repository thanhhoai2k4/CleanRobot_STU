class TargetStore:

    def __init__(self):

        self.current_target = None

    def set_target(self, target):

        self.current_target = target

    def get_target(self):

        return self.current_target

    def clear(self):

        self.current_target = None