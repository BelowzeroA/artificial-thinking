BOUNDARY_THRESHOLD = 20


class Image:
    """
    Wrapper around simple image
    """
    def __init__(self, source):
        self._rgb_source = source
        self.source = self._rgb2gray(source)
        self.width = self.source.shape[1]
        self.height = self.source.shape[0]

    def _rgb2gray(self, rgb):
        r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
        gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
        return gray

    def detect_right_boundary(self):
        rightmost_x = self.width - 1
        for x_shift in range(rightmost_x):
            accumulated_difference = 0
            current_x = rightmost_x - x_shift
            for y in range(self.height):
                difference = abs(self.source[y][current_x] - self.source[y][current_x - 1])
                accumulated_difference += difference
            if accumulated_difference / self.height > BOUNDARY_THRESHOLD:
                return current_x
        return rightmost_x

    def detect_left_boundary(self):
        leftmost_x = 0
        for x_shift in range(self.width):
            accumulated_difference = 0
            current_x = x_shift
            for y in range(self.height):
                difference = abs(self.source[y][current_x] - self.source[y][current_x + 1])
                accumulated_difference += difference
            if accumulated_difference / self.height > BOUNDARY_THRESHOLD:
                return current_x
        return leftmost_x

    def detect_upper_boundary(self):
        uppermost_y = 0
        for y_shift in range(self.height):
            accumulated_difference = 0
            current_y = y_shift
            for x in range(self.width):
                difference = abs(self.source[current_y][x] - self.source[current_y + 1][x])
                accumulated_difference += difference
            if accumulated_difference / self.width > BOUNDARY_THRESHOLD:
                return current_y
        return uppermost_y
