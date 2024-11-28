import os
import sys
import signal
import configparser
import shutil

from urllib.parse import unquote
import numpy as np

from flask import Flask, Response, render_template, request
import csv

import app.camera as camera
import app.process as process
import app.argumentation as argumentation

app = Flask(__name__)

config = configparser.ConfigParser()
config.read("config.ini")

@app.route("/")
def home():
    lower_bound_color = [int(i) for i in config.get("Configure", "LOWER_BOUND_COLOR").split(",")]
    upper_bound_color = [int(i) for i in config.get("Configure", "UPPER_BOUND_COLOR").split(",")]
    h_score = float(config.get("Configure", "H_SCORE"))
    b_score = float(config.get("Configure", "B_SCORE"))
    crop = [int(i) for i in config.get("Configure", "CROP").split(",")]
    pcm = float(config.get("Configure", "PCM"))
    delay = float(config.get("Configure", "DELAY"))

    return render_template("index.html", lower_bound_color = lower_bound_color, upper_bound_color = upper_bound_color, h_score = h_score, b_score = b_score, pcm = pcm, crop = crop, delay = delay)

@app.route("/video", methods = ["GET"])
def video():
    threshold = request.args.get("threshold", "false") == "true"
    reference = request.args.get("reference", "false") == "true"
    crop_preview = request.args.get("crop_preview", "false") == "true"

    lower_bound_color = [int(i) for i in config.get("Configure", "LOWER_BOUND_COLOR").split(",")]
    upper_bound_color = [int(i) for i in config.get("Configure", "UPPER_BOUND_COLOR").split(",")]

    crop = [int(i) for i in config.get("Configure", "CROP").split(",")]

    return Response(camera.generate_frames(threshold = threshold, reference = reference, crop_preview = crop_preview, lower_bound_color = lower_bound_color, upper_bound_color = upper_bound_color, crop = crop), mimetype="multipart/x-mixed-replace; boundary=frame", status = 200)

@app.route("/rotating_test", methods = ["GET"])
def rotating_test():
    process.rotating_test(channel = 0, angle = 0.1, duration = 5)
    return Response(str("Rotating Test"), status = 200)

@app.route("/calibrate", methods = ["GET"])
def calibrate():
    output_response = process.calibrate(camera)
    return Response(str(f"File Path: {output_response}"), status = 200)

@app.route("/take_file", methods = ["GET"])
def take_file():
    output_response = process.take_picture_file(camera)
    return Response(str(f"File Path: {output_response}"), status = 200)

@app.route("/scanning", methods = ["GET"])
def scanning():
    delay = float(config.get("Configure", "DELAY"))
    output_response = process.scanning(camera, delay)
    print(f"Delay: {delay}")

    shutil.copy("config.ini", output_response)

    return Response(str(f"Folder Path: {output_response}"), status = 200)

@app.route("/generate", methods = ["GET"])
def generate():
    folder_path = unquote(request.args.get("folder_path", ""))

    if folder_path == "":
        return Response("Folder Path not found", status = 400)

    config_generate = configparser.ConfigParser()
    config_generate.read(os.path.join(folder_path, "config.ini"))

    lower_bound_color = [int(i) for i in config_generate.get("Configure", "LOWER_BOUND_COLOR").split(",")]
    upper_bound_color = [int(i) for i in config_generate.get("Configure", "UPPER_BOUND_COLOR").split(",")]
    h_score = float(config_generate.get("Configure", "H_SCORE"))
    b_score = float(config_generate.get("Configure", "B_SCORE"))
    top_crop = int(config_generate.get("Configure", "CROP").split(",")[0])
    bottom_crop = int(config_generate.get("Configure", "CROP").split(",")[1])
    right_crop = int(config_generate.get("Configure", "CROP").split(",")[2])

    print(f"Top Crop: {top_crop} | Bottom Crop: {bottom_crop} | Right Crop: {right_crop} | H Score: {h_score} | B Score: {b_score} | Lower Bound: {lower_bound_color} | Upper Bound: {upper_bound_color} | Folder Path: {folder_path}")

    output_response = process.generate_cloud_point(folder_path, np.array(lower_bound_color), np.array(upper_bound_color), h_score, b_score, top_crop, bottom_crop, right_crop)
    
    return Response(str(f"File Path: {output_response}"), status = 200)

@app.route("/generate_debug", methods = ["GET"])
def generate_debug():
    folder_path = unquote(request.args.get("folder_path", ""))

    if folder_path == "":
        return Response("Folder Path not found", status = 400)
    
    for foldered_data in [d for d in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, d))]:
        chosen_folder = os.path.join(folder_path, foldered_data)
        print(f"\n\nDebug Start Generating: {chosen_folder}")

        config_generate = configparser.ConfigParser()
        config_generate.read(os.path.join(chosen_folder, "config.ini"))

        lower_bound_color = [int(i) for i in config_generate.get("Configure", "LOWER_BOUND_COLOR").split(",")]
        upper_bound_color = [int(i) for i in config_generate.get("Configure", "UPPER_BOUND_COLOR").split(",")]
        h_score = float(config_generate.get("Configure", "H_SCORE"))
        b_score = float(config_generate.get("Configure", "B_SCORE"))
        top_crop = int(config_generate.get("Configure", "CROP").split(",")[0])
        bottom_crop = int(config_generate.get("Configure", "CROP").split(",")[1])
        right_crop = int(config_generate.get("Configure", "CROP").split(",")[2])

        output_response = process.generate_cloud_point(chosen_folder, np.array(lower_bound_color), np.array(upper_bound_color), h_score, b_score, top_crop, bottom_crop, right_crop)
    
    return Response(str("Debug Done"), status = 200)

@app.route("/change_threshold", methods = ["GET"])
def change_threshold():
    lower_bound_color = [
        int(request.args.get("lower_h", config.get("Configure", "LOWER_BOUND_COLOR").split(",")[0])),
        int(request.args.get("lower_s", config.get("Configure", "LOWER_BOUND_COLOR").split(",")[1])),
        int(request.args.get("lower_v", config.get("Configure", "LOWER_BOUND_COLOR").split(",")[2]))
    ]
    upper_bound_color = [
        int(request.args.get("upper_h", config.get("Configure", "UPPER_BOUND_COLOR").split(",")[0])),
        int(request.args.get("upper_s", config.get("Configure", "UPPER_BOUND_COLOR").split(",")[1])),
        int(request.args.get("upper_v", config.get("Configure", "UPPER_BOUND_COLOR").split(",")[2]))
    ]

    config.set("Configure", "LOWER_BOUND_COLOR", f"{lower_bound_color[0]},{lower_bound_color[1]},{lower_bound_color[2]}")
    config.set("Configure", "UPPER_BOUND_COLOR", f"{upper_bound_color[0]},{upper_bound_color[1]},{upper_bound_color[2]}")

    with open("config.ini", "w") as configfile:
        config.write(configfile)

    return Response("Threshold Change", status = 200)

@app.route("/change_crop", methods = ["GET"])
def change_crop():
    top_crop = int(request.args.get("top_crop", config.get("Configure", "CROP").split(",")[0]))
    bottom_crop = int(request.args.get("bottom_crop", config.get("Configure", "CROP").split(",")[1]))
    right_crop = int(request.args.get("right_crop", config.get("Configure", "CROP").split(",")[2]))

    config.set("Configure", "CROP", f"{top_crop},{bottom_crop},{right_crop}")

    with open("config.ini", "w") as configfile:
        config.write(configfile)

    return Response("Crop Change", status = 200)

@app.route("/change_score", methods = ["GET"])
def change_score():
    h_score = request.args.get("h_score", config.get("Configure", "H_SCORE"))
    b_score = request.args.get("b_score", config.get("Configure", "B_SCORE"))
    pcm = request.args.get("pcm", config.get("Configure", "PCM"))
    delay = request.args.get("delay", config.get("Configure", "DELAY"))

    if h_score == "NaN":
        h_score = 0
    else:
        h_score = float(h_score)

    if b_score == "NaN":
        b_score = 0
    else:
        b_score = float(b_score)

    if pcm == "NaN":
        pcm = 0
    else:
        pcm = float(pcm)

    if delay == "NaN":
        delay = 0
    else:
        delay = float(delay)

    config.set("Configure", "H_SCORE", str(h_score))
    config.set("Configure", "B_SCORE", str(b_score))
    config.set("Configure", "PCM", str(pcm))
    config.set("Configure", "DELAY", str(delay))

    with open("config.ini", "w") as configfile:
        config.write(configfile)

    return Response("Score Change", status = 200)

@app.route("/reset", methods = ["GET"])
def reset():
    for key, value in config.items("Default"):
        config.set("Configure", key, value)

    with open("config.ini", "w") as configfile:
        config.write(configfile)

    return Response(str("Default Configuration"), status = 200)

@app.route("/data_gen", methods = ["GET"])
def data_gen():
    folder_path = unquote(request.args.get("folder_path_cp", ""))
    x1data = request.args.get("x1data", "")
    x2data = request.args.get("x2data", "")

    config_generate = configparser.ConfigParser()
    config_generate.read(os.path.join(folder_path, "config.ini"))

    if folder_path == "" or x1data == "" or x2data == "":
        return Response("Folder Path or Data not found", status = 400)
    
    pcm = float(config_generate.get("Configure", "PCM"))
    
    augmented_data_x1 = argumentation.compute_x_distance_on_y(folder_path, float(x1data), pcm)
    augmented_data_x2 = argumentation.compute_x_distance_on_y(folder_path, float(x2data), pcm)
    augmented_data_y = argumentation.compute_height_range(folder_path, pcm)

    return Response(str(f"Data X1: {augmented_data_x1} | Data X2: {augmented_data_x2} | Data Y: {augmented_data_y}"), status = 200)

@app.route("/data_gen_debug", methods = ["GET"])
def data_gen_debug():
    folder_path = unquote(request.args.get("folder_path", ""))
    x1data = request.args.get("x1data", "")
    x2data = request.args.get("x2data", "")

    csv_file_path = os.path.join(folder_path, "augmented_data.csv")

    data_final = []

    for foldered_data in [d for d in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, d))]:
        chosen_folder = os.path.join(folder_path, foldered_data)
        print(f"\n\nDebug Data: {chosen_folder}")

        config_generate = configparser.ConfigParser()
        config_generate.read(os.path.join(chosen_folder, "config.ini"))

        if chosen_folder == "" or x1data == "" or x2data == "":
            return Response("Folder Path or Data not found", status = 400)
        
        pcm = float(config_generate.get("Configure", "PCM"))
        
        augmented_data_x1 = argumentation.compute_x_distance_on_y(chosen_folder, float(x1data), pcm)
        augmented_data_x2 = argumentation.compute_x_distance_on_y(chosen_folder, float(x2data), pcm)
        augmented_data_y = argumentation.compute_height_range(chosen_folder, pcm)

        data_final.append([chosen_folder, augmented_data_x1, augmented_data_x2, augmented_data_y])

    with open(csv_file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Folder Path", "Data X1", "Data X2", "Data Y"])
        writer.writerows(data_final)

    return Response(str("Debug Done"), status = 200)

def signal_handler(sig, frame):
    print("\nStopping camera...")
    camera.stop_camera()
    sys.exit(0)

def start(debug = False, port = 5000):
    camera.start_camera((640, 480))
    signal.signal(signal.SIGINT, signal_handler)
    app.run(host = "0.0.0.0", port = port, threaded = True, debug = debug)