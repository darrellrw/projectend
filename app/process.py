import app.picamera as camera
from adafruit_servokit import ServoKit

import plotly.express as px

import time
import os
import cv2

import header

import app.calculation as calculation
import numpy as np

import csv

import open3d as o3d

import shutil

kit = ServoKit(channels = 16)

def servo_rotate(channel = 0, angle = 0):
    kit.continuous_servo[channel].throttle = angle

def rotating_test():
    servo_rotate(channel = 0, angle = 0)
    servo_rotate(channel = 0, angle = 0.1)
    time.sleep(5)
    servo_rotate(channel = 0, angle = 0)

def mesh_generation(folder_path, point_cloud):
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(point_cloud)
    pcd.estimate_normals()
    o3d.io.write_point_cloud(f"{folder_path}/point_cloud.ply", pcd)
    
    distances = pcd.compute_nearest_neighbor_distance()
    avg_distance = np.mean(distances)
    radius = 3 * avg_distance

    mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(pcd, o3d.utility.DoubleVector([radius, radius * 2]))
    
    dec_mesh = mesh.simplify_quadric_decimation(100000)

    dec_mesh.remove_degenerate_triangles()
    dec_mesh.remove_duplicated_triangles()
    dec_mesh.remove_duplicated_vertices()
    dec_mesh.remove_non_manifold_edges()
    
    o3d.io.write_triangle_mesh(f"{folder_path}/mesh.ply", dec_mesh)

    return f"{folder_path}/mesh.obj"

def start_scanning():
    if not os.path.exists("/home/darrell/Documents/projectend/data"):
        os.makedirs("/home/darrell/Documents/projectend/data")
    
    current_time = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
    folder_path = f"/home/darrell/Documents/projectend/data/{current_time}"
    os.makedirs(folder_path)
    os.makedirs(f"{folder_path}/images")

    for i in range(360):
        servo_rotate(channel = 0, angle = 0)
        time.sleep(0.1)
        servo_rotate(channel = 0, angle = 0.05)
        time.sleep(0.0573)
        servo_rotate(channel = 0, angle = 0)
        time.sleep(0.1)
        print(f"Angle: {i}")
        camera.take_file(f"{folder_path}/images/image_{i}.jpg")
    
    config_path = "/home/darrell/Documents/projectend/config.ini"
    config_destination = os.path.join(folder_path, "scan_config.ini")
    shutil.copyfile(config_path, config_destination)
    
    return folder_path

def generate_point_cloud(folder_path):
    image_list = []
    images_path = os.path.join(folder_path, "images")

    if not os.path.exists(images_path):
        return None, None

    for filename in os.listdir(images_path):
        print(filename)
        if filename.endswith(".jpg"):
            image_list.append(os.path.join(images_path, filename))
    
    if len(image_list) == 0:
        return None, None

    config = header.read_from_config_file(os.path.join(folder_path, "scan_config.ini"))

    image_list = sorted(image_list, key=lambda x: int(os.path.splitext(os.path.basename(x))[0].split('_')[1]))

    coordinates = []

    for image in image_list:
        print(f"Processing {image}")
        frame = cv2.imread(image)

        # Flip is needed | Must change the values
        if config.get("Configure", "FLIP") == "True":
            frame = cv2.flip(frame, 1)
            frame = cv2.flip(frame, 0)

        # Crop the image | Must change the values
        height, width, _ = frame.shape

        right_crop = int(config.get("Configure", "RIGHT_CROP"))
        top_crop = int(config.get("Configure", "TOP_CROP"))
        bottom_crop = int(config.get("Configure", "BOTTOM_CROP"))

        if right_crop <= width and right_crop >= width//2:
            frame = frame[:, width//2:right_crop]
        if top_crop >= 0 and top_crop <= height//2 and bottom_crop <= height and bottom_crop >= height//2:
            frame = frame[top_crop:bottom_crop, :]

        mask = calculation.color_range_threshold(frame, np.array(config.get("Configure", "LOWER_BOUND_COLOR").split(","), dtype = int), np.array(config.get("Configure", "UPPER_BOUND_COLOR").split(","), dtype = int))
        pixel_position = calculation.centroid_method(mask)
        coordinate_values = calculation.linear_equation_method(pixel_position, float(config.get("Configure", "H_SCORE")), float(config.get("Configure", "B_SCORE")))
        coordinates += calculation.positions_rotate(coordinate_values, int(image_list.index(image)))

    # Remove coordinates where x and z are both 0
    coordinates = [coord for coord in coordinates if coord[1] != 0 or coord[3] != 0]

    # Plotly 3D Scatter Plot
    ploty_path = os.path.join(folder_path, "data_plotly.html")
    df = px.data.iris()
    fig = px.scatter_3d(df, x = [position[1] for position in coordinates], y = [position[2] for position in coordinates], z = [position[3] for position in coordinates])
    fig.write_html(ploty_path, auto_open = False)

    # Save coordinates to CSV
    csv_path = os.path.join(folder_path, "data_coordinates.csv")
    with open(csv_path, mode = 'w', newline = '') as file:
        writer = csv.writer(file)
        writer.writerow(["Angle", "X", "Y", "Z"])
        for coordinate in coordinates:
            writer.writerow(coordinate)

    # Generate Point Cloud
    coordinates_array = np.array(coordinates)
    point_cloud = coordinates_array[:, 1:].astype(int)
    mesh_path = mesh_generation(folder_path, point_cloud)
    
    return ploty_path, csv_path, mesh_path