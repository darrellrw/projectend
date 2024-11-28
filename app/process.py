import os
import csv
import time
import cv2

from adafruit_servokit import ServoKit
import plotly.express as px
import open3d as o3d
import numpy as np

import app.algorithm as algorithm
import app.calibration as calibration

kit = ServoKit(channels = 16)

def servo_rotate(channel = 0, angle = 0):
    kit.continuous_servo[channel].throttle = angle

def servo_stop(channel = 0):
    kit.continuous_servo[channel].throttle = 0

def rotating_test(channel = 0, angle = 0.1, duration = 5):
    servo_rotate(channel = channel, angle = 0)
    servo_rotate(channel = channel, angle = angle)
    time.sleep(duration)
    servo_rotate(channel = channel, angle = 0)

def take_picture_file(camera, folder_path = "/home/darrell/Documents/tugasakhir/data"):
    image_name = time.strftime("pic_%Y-%m-%d_%H-%M-%S", time.localtime())
    output_image = camera.take_picture()
    output_path = os.path.join(folder_path, image_name + ".jpg")
    cv2.imwrite(output_path, output_image)
    return output_path

def calibrate(camera, data_path = "/home/darrell/Documents/tugasakhir/data"):
    current_time = time.strftime("cal_%Y-%m-%d_%H-%M-%S", time.localtime())
    output_image = calibration.process_image(camera.take_picture())
    output_path = os.path.join(data_path, current_time + ".jpg")
    cv2.imwrite(output_path, output_image)
    return output_path

def scanning(camera, delay = 0.0573, data_path = "/home/darrell/Documents/tugasakhir/data"):
    print("Scanning process started")
    if not os.path.exists(data_path):
        os.makedirs(data_path)
    
    current_time = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
    folder_path = os.path.join(data_path, current_time)
    os.makedirs(folder_path)
    os.makedirs(os.path.join(folder_path, "images"))

    for i in range(360):
        servo_rotate(channel = 0, angle = 0)
        time.sleep(0.1)
        servo_rotate(channel = 0, angle = 0.05)
        time.sleep(delay)
        servo_rotate(channel = 0, angle = 0)
        time.sleep(0.1)
        print(f"\tAngle: {i}")

        camera.take_file(os.path.join(folder_path, "images", f"{i}.jpg"))
    
    print("Scanning process finished\n")
    return folder_path

def generate_cloud_point(folder_path, lower_bound_color, upper_bound_color, h_score, b_score, top_crop = 0, bottom_crop = 480, right_crop = 640):
    print("Generating point cloud")
    image_list = []
    images_path = os.path.join(folder_path, "images")

    if not os.path.exists(images_path):
        print("Images folder not found")
        return None

    print("Scanning image folder")
    for image in os.listdir(images_path):
        print(f"\tFound: {image}")
        if image.endswith(".jpg"):
            image_list.append(os.path.join(images_path, image))
    
    print(f"Total images found: {len(image_list)}")
    
    if len(image_list) == 0 or len(image_list) != 360:
        print("Images not found or not complete")
        return None
    
    image_list = sorted(image_list, key = lambda x: int(os.path.splitext(os.path.basename(x))[0]))

    print("Images sorted")
    print("Processing images")

    coordinates = []

    for image in image_list:
        print(f"\tProcessing: {image}")
        frame = cv2.imread(image)
        
        height, width, _ = frame.shape

        if right_crop <= width and right_crop >= width//2:
                frame = frame[:, width//2:right_crop]
        if top_crop >= 0 and top_crop <= height//2 and bottom_crop <= height and bottom_crop >= height//2:
            frame = frame[top_crop:bottom_crop, :]

        mask = algorithm.color_range_threshold(frame, lower_bound_color, upper_bound_color)
        centroids = algorithm.centroid_extraction(mask)
        point_cloud = algorithm.point_cloud_generation(centroids, h_score, b_score)
        coordinates += algorithm.rotate_position(point_cloud, int(image_list.index(image)))

    coordinates = [coord for coord in coordinates if coord[1] != 0 or coord[3] != 0]

    print("Point cloud generated\n")

    csv_path = os.path.join(folder_path, "point_cloud.csv")
    with open(csv_path, 'w', newline = '') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["X", "Y", "Z"])
        csvwriter.writerows(coordinates)
    
    print(f"Point cloud saved to {csv_path}\n")

    ploty_path = os.path.join(folder_path, "data_plotly.html")
    df = px.data.iris()
    fig = px.scatter_3d(df, x = [position[1] for position in coordinates], y = [position[2] for position in coordinates], z = [position[3] for position in coordinates])
    fig.write_html(ploty_path, auto_open = False)

    print(f"Point cloud plot saved to {ploty_path}\n")

    try:
        generate_mesh(folder_path, [position[1:] for position in coordinates])
    except Exception as e:
        print(f"Error Generating Mesh: {e}")
        return csv_path

    print(f"Mesh generated\n")

    return csv_path

def generate_mesh(folder_path, point_cloud):
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(point_cloud)

    o3d.io.write_point_cloud(os.path.join(folder_path, "point_cloud.ply"), pcd)
    
    pcd.estimate_normals(search_param = o3d.geometry.KDTreeSearchParamHybrid(radius = 0.1, max_nn = 30))

    radius = 1.5 * np.mean(pcd.compute_nearest_neighbor_distance())
    mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(pcd, o3d.utility.DoubleVector([radius, radius * 1.5]))
    mesh.compute_vertex_normals()
    mesh = mesh.simplify_vertex_clustering(voxel_size = 0.002)
    mesh = mesh.filter_smooth_taubin(number_of_iterations = 50)

    mesh.remove_degenerate_triangles()
    mesh.remove_duplicated_triangles()
    mesh.remove_duplicated_vertices()
    mesh.remove_non_manifold_edges()

    o3d.io.write_triangle_mesh(os.path.join(folder_path, "mesh.ply"), mesh)


# def generate_mesh(folder_path, point_cloud):
#     pcd = o3d.geometry.PointCloud()
#     pcd.points = o3d.utility.Vector3dVector(point_cloud)
#     o3d.io.write_point_cloud(os.path.join(folder_path, "point_cloud.ply"), pcd)
#     pcd.estimate_normals(search_param = o3d.geometry.KDTreeSearchParamHybrid(radius = 0.05, max_nn = 30))
#     distances = pcd.compute_nearest_neighbor_distance()
#     avg_dist = np.mean(distances)
#     radius = 2.5 * avg_dist
#     mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(
#         pcd, o3d.utility.DoubleVector([radius, radius * 2])
#     )
#     # mesh = o3d.t.geometry.TriangleMesh.from_legacy(mesh).fill_holes(hole_size = 10000).to_legacy()
#     mesh = mesh.simplify_vertex_clustering(voxel_size = 0.005)
#     mesh = mesh.filter_smooth_taubin(number_of_iterations = 20)
#     mesh.remove_degenerate_triangles()
#     mesh.remove_duplicated_triangles()
#     mesh.remove_duplicated_vertices()
#     mesh.remove_non_manifold_edges()
#     o3d.io.write_triangle_mesh(os.path.join(folder_path, "mesh.ply"), mesh)