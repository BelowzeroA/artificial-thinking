import os
import random

import matplotlib.pyplot as plt
import imageio

from vision.image import Image


def draw_vertical_line(img, x):
    img_height = img.shape[0]
    for y in range(img_height):
        img[y][x] = 0


def draw_horizontal_line(img, y):
    img_width = img.shape[1]
    for x in range(img_width):
        img[y][x] = 0


def _calc_average_weight(sab):
    total_weight = 0
    num_synapses = 0
    for neuron in sab.receptive_neurons:
        for conn in neuron.incoming_connections:
            if conn.source.clump != sab and not conn.inhibitory:
                num_synapses += 1
                total_weight += conn.weight
    return total_weight / num_synapses


def show_receptive_map(receptive_layer, orientation):
    receptive_map = receptive_layer.get_firing_map(orientation=orientation)
    plt.imshow(receptive_map)
    plt.show(block=True)


from PIL import Image
import cv2


class Contour:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.num = 0
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def input_area(self) -> int:
        return self.width * self.height

    def point_within(self, x: int, y: int) -> bool:
        if x < self.x or y < self.y or x > self.x + self.width or y > self.y + self.height:
            return False
        return True

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.width == other.width and self.height == other.height

    @classmethod
    def from_contour(cls, contour) -> 'Contour':
        return cls(*cv2.boundingRect(contour))

    def _repr(self):
        return f'C{self.num}'

    def __repr__(self):
        return self._repr()

    def __str__(self):
        return self._repr()


def contours_intersect(c1: Contour, c2: Contour):
    if c1.point_within(c2.x, c2.y):
        return True
    if c1.point_within(c2.x + c2.width, c2.y):
        return True
    if c1.point_within(c2.x, c2.y + c2.height):
        return True
    if c1.point_within(c2.x + c2.width, c2.y + c2.height):
        return True
    return False


def detectROI(img_filename: str):
    v = cv2.imread(img_filename)
    s = cv2.cvtColor(v, cv2.COLOR_BGR2GRAY)
    s = cv2.Laplacian(s, cv2.CV_16S, ksize=3)
    s = cv2.convertScaleAbs(s)

    ret, binary = cv2.threshold(s, 40, 255, cv2.THRESH_BINARY)
    cv2.imshow('nier', binary)
    raw_contours, hierarchy = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    height = v.shape[0]
    width = v.shape[1]
    min_height = int(height / 20)
    min_width = int(width / 20)
    max_height = int(height / 2)
    max_width = int(width / 2)
    contours = [Contour.from_contour(contour) for contour in raw_contours]
    contours = [c for c in contours if max_width > c.width > min_width and max_height > c.height > min_height]
    for i, c in enumerate(contours):
        c.num = i + 1
    groups = []
    for c in contours:
        for c_attempted in contours:
            if c == c_attempted:
                continue
            if contours_intersect(c, c_attempted):
                group_exists = False
                for group in groups:
                    if c_attempted in group and c not in group:
                        group.append(c)
                        group_exists = True
                    elif c_attempted not in group and c in group:
                        group.append(c_attempted)
                        group_exists = True
                    elif c_attempted in group and c in group:
                        group_exists = True
                if not group_exists:
                    groups.append([c, c_attempted])

    for c in raw_contours:
        x, y, w, h = cv2.boundingRect(c)
        if max_width > w > min_width and max_height > h > min_height:
            cv2.rectangle(v, (x, y), (x + w, y + h), (155, 155, 0), 1)
    cv2.imshow('nier2', v)

    cv2.waitKey()
    cv2.destroyAllWindows()


def _find_size_candidates(self, image):
    binary_image = self._filter_image(image)

    _, contours, _ = cv2.findContours(binary_image,
                                      cv2.RETR_LIST,
                                      cv2.CHAIN_APPROX_SIMPLE)

    size_candidates = []
    for contour in contours:
        bounding_rect = cv2.boundingRect(contour)
        contour_area = cv2.contourArea(contour)
        if self._is_valid_contour(contour_area, bounding_rect):
            candidate = (bounding_rect[2] + bounding_rect[3]) / 2
            size_candidates.append(candidate)

    return size_candidates


def main():

    path = 'data/images'
    img_filename = os.path.join(path, 'room_with_cat.bmp')
    # img_filename = os.path.join(path, 'cat_alone.bmp')
    detectROI(img_filename)

    # img = Image(imageio.imread(img_filename))
    # plt.imshow(img.source)
    # plt.show(block=True)

    target_image_filename = os.path.join(path, 'room_with_cat_resized.bmp')
    basewidth = 100
    img = Image.open(img_filename)
    wpercent = (basewidth / float(img.size[0]))
    hsize = int((float(img.size[1]) * float(wpercent)))
    img = img.resize((basewidth, hsize), Image.ANTIALIAS)
    # img.save(target_image_filename, img.format)
    # network.run(max_ticks=60)

    # raw = misc.imread(os.path.join(path, 'П2.png'), flatten=0)
    # x_right = img.detect_right_boundary(img)
    # draw_vertical_line(img, x_right)

    # plt.imshow(img1.source)
    # plt.colorbar()
    # plt.show()


if __name__ == '__main__':
    main()