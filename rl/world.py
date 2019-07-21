
class World:

    def __init__(self, grid_size=10):
        self.grid_size = grid_size
        self.hive_x = grid_size / 2
        self.hive_y = grid_size - 1
        self.objects = []


