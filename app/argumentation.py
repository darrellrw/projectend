import os
import numpy as np
import open3d as o3d

def compute_x_distance_on_y(cloud_point_file, y_axis, point_conversion_multiplier):
    # Check if the file exists
    file_path = os.path.join(cloud_point_file, "point_cloud.ply")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Point cloud file not found at {file_path}")
    
    # Load point cloud data
    pcd = o3d.io.read_point_cloud(file_path)
    points = np.asarray(pcd.points)
    
    # Tolerance for y-axis comparison (floating-point precision)
    tolerance = 1e-5
    
    # Collect x-values for points that are within the tolerance of the specified y-axis
    x_values_on_y = points[np.abs(points[:, 1] - y_axis) < tolerance, 0]
    
    # Check if any x-values were found
    if len(x_values_on_y) == 0:
        return None  # No points found on the specified y-axis
    
    # Calculate minimum and maximum x-values
    min_x = np.min(x_values_on_y) * point_conversion_multiplier
    max_x = np.max(x_values_on_y) * point_conversion_multiplier

    print(f"Min x: {min_x}, Max x: {max_x}")
    
    # Calculate and return the scaled distance along the x-axis
    return np.abs(max_x - min_x)

def compute_height_range(cloud_point_file, point_conversion_multiplier):
    # Check if the file exists
    file_path = os.path.join(cloud_point_file, "point_cloud.ply")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Point cloud file not found at {file_path}")
    
    # Load point cloud data
    pcd = o3d.io.read_point_cloud(file_path)
    points = np.asarray(pcd.points)
    
    # Find the highest and lowest points along the y-axis
    lowest_point_y = points[np.argmin(points[:, 1])]
    highest_point_y = points[np.argmax(points[:, 1])]
    
    # Calculate and return the scaled height difference
    return np.abs((highest_point_y[1] - lowest_point_y[1]) * point_conversion_multiplier)
