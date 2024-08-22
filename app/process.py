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

config = header.get_config()

kit = ServoKit(channels = 16)

def servo_rotate(channel = 0, angle = 0):
    kit.continuous_servo[channel].throttle = angle

def rotating_test():
    servo_rotate(channel = 0, angle = 0)
    servo_rotate(channel = 0, angle = 0.1)
    time.sleep(5)
    servo_rotate(channel = 0, angle = 0)

def start_scanning():
    if not os.path.exists("data"):
        os.makedirs("data")
    
    current_time = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
    folder_path = f"data/{current_time}"
    os.makedirs(folder_path)

    for i in range(360):
        servo_rotate(channel = 0, angle = 0)
        time.sleep(0.1)
        servo_rotate(channel = 0, angle = 0.025)
        time.sleep(0.01557)
        servo_rotate(channel = 0, angle = 0)
        time.sleep(0.1)
        print(f"Angle: {i}")
        camera.take_file(f"{folder_path}/images/image_{i}.jpg")
    
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

    image_list = sorted(image_list, key=lambda x: int(os.path.splitext(os.path.basename(x))[0].split('_')[1]))

    coordinates = []

    for image in image_list:
        print(f"Processing {image}")
        frame = cv2.imread(image)

        # Flip is needed
        frame = cv2.flip(frame, 1)
        frame = cv2.flip(frame, 0)

        # Crop the image
        height, width, _ = frame.shape
        frame = frame[:, width//2:450]
        frame = frame[100:315, :]

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
    
    return ploty_path, csv_path