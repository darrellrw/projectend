import cv2
import numpy as np

# def color_range_threshold(image, lower_bound_color, upper_bound_color):
#     hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
#     mask = cv2.inRange(hsv_image, lower_bound_color, upper_bound_color)
#     mask = cv2.GaussianBlur(mask, (3, 3), 0)
#     mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
#     return mask

def color_range_threshold(image, lower_bound_color, upper_bound_color):
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv_image, lower_bound_color, upper_bound_color)
    mask = cv2.GaussianBlur(mask, (3, 3), 0)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    
    edges = cv2.Canny(mask, 100, 200)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    line_mask = np.zeros_like(mask)
    cv2.drawContours(line_mask, contours, -1, (255), thickness=cv2.FILLED)
    
    return line_mask

def centroid_extraction(mask):
    height, width = mask.shape

    centroids = []

    for y in range(height):
        numerator = np.sum(np.arange(width) * mask[y, :])
        denominator = np.sum(mask[y, :])
        centroids.append([(numerator / denominator), y] if denominator > 0 else [0, y])
    
    return centroids

def point_cloud_generation(centroids, h_score, b_score):
    coordinate_values = []

    for centroid in centroids:
        x, y = centroid
        z = (x * h_score) / b_score
        coordinate_values.append([x, y, z])

    return coordinate_values

def rotate_position(coordinate_values, angle):
    rotated_coordinates = []
    rad = np.radians(angle)

    for coordinate in coordinate_values:
        x, y, z = coordinate
        new_x, new_z = np.dot(np.array([[np.cos(rad), -np.sin(rad)], [np.sin(rad), np.cos(rad)]]), np.array([x, z]))
        rotated_coordinates.append([angle, new_x, y, new_z])
    
    return rotated_coordinates