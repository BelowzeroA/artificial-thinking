import math


def get_distance_between_coords(x1, y1, x2, y2):
    return math.hypot(x2 - x1, y2 - y1)


def get_angle_in_degrees(val):
    return math.degrees(math.atan(val))


def sign(val):
    return (val > 0) - (val < 0)