import cv2
import numpy as np

import header

config = header.get_config()

## OpenCV Formula
def color_range_threshold(image, lower_bound_color, upper_bound_color):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_bound_color, upper_bound_color)
    return mask

## Math Formula
def centroid_method(mask):
    height, width = mask.shape
    middle_point = np.zeros(height, dtype = int)

    for y in range(height):
        numerator = np.sum(np.arange(width) * mask[y, :])
        denominator = np.sum(mask[y, :])
        if denominator > 0:
            middle_point[y] = (numerator / denominator)
        else:
            middle_point[y] = 0

    return middle_point

def linear_equation_method(pixel_position, h_score, b_score):
    coordinate_values = np.zeros((len(pixel_position), 3), dtype = int)

    for position in range(len(pixel_position)):
        z_value = (pixel_position[position] * h_score) / b_score
        coordinate_values[position] = [pixel_position[position], position, z_value]
    
    return coordinate_values

def positions_rotate(coordinate_values, angle):
    rotated_positions = []

    rad = (angle * (np.pi / 180))

    for position in coordinate_values:
        x = position[0]
        y = position[1]
        z = position[2]
        new_x, new_z = np.dot(np.array([[np.cos(rad), -np.sin(rad)], [np.sin(rad), np.cos(rad)]]), np.array([x, z]))
        rotated_positions.append((angle, int(new_x), int(y), int(new_z)))
    return rotated_positions