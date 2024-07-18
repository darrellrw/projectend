import cv2
import numpy as np

import header

config = header.get_config()

def color_range_threshold(image, lower_bound_color, upper_bound_color):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    mask = cv2.inRange(hsv, lower_bound_color, upper_bound_color)
    return mask

def average_pixel_position(mask):
    height, width = mask.shape[:2]
    pixel_positions = []
    for y in range(height):
        row_sum = 0
        count = 0
        for x in range(width):
            if mask[y, x] > 0:
                row_sum += x
                count += 1
        if count > 0:
            average_position = row_sum / count
            pixel_positions.append((int(average_position), y))
    return pixel_positions

def z_formula(x, h, b):
    return (x * h) / b

def calculate_z(pixel_positions):
    z_values = []
    for position in pixel_positions:
        x = position[0]
        y = position[1]
        z = z_formula(x, config.get("Configure", "H_SCORE"), config.get("Configure", "B_SCORE"))
        z_values.append((x, y, int(z)))
    return z_values

def rotate_transform(x, z, angle):
    new_x_z = np.dot(np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]]), np.array([x, z]))
    return new_x_z[0], new_x_z[1]

def positions_rotate(pixel_positions, angle):
    rotated_positions = []
    for position in pixel_positions:
        x = position[0]
        y = position[1]
        z = position[2]
        new_x, new_z = rotate_transform(x, z, angle)
        rotated_positions.append((new_x, y, new_z))
    return rotated_positions