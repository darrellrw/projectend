try:
    import app.picamera as camera
except ImportError:
    import app.unicamera as camera

import header
import app.process as process

import datetime

from flask import Flask, Response, render_template, request

app = Flask(__name__)

# Utility function to fetch configuration values
def get_color_boundaries(section):
    config = header.get_config()
    lower_bound = [int(i) for i in config.get(section, "LOWER_BOUND_COLOR").split(",")]
    upper_bound = [int(i) for i in config.get(section, "UPPER_BOUND_COLOR").split(",")]
    return lower_bound, upper_bound

def update_color_boundaries(section, lower_bound, upper_bound):
    header.set_config(section, "LOWER_BOUND_COLOR", f"{lower_bound[0]},{lower_bound[1]},{lower_bound[2]}")
    header.set_config(section, "UPPER_BOUND_COLOR", f"{upper_bound[0]},{upper_bound[1]},{upper_bound[2]}")

def reset_config():
    config = header.get_config()
    header.set_config("Configure", "LOWER_BOUND_COLOR", config.get("Default", "LOWER_BOUND_COLOR"))
    header.set_config("Configure", "UPPER_BOUND_COLOR", config.get("Default", "UPPER_BOUND_COLOR"))
    header.set_config("Configure", "H_SCORE", config.get("Default", "H_SCORE"))
    header.set_config("Configure", "B_SCORE", config.get("Default", "B_SCORE"))
    header.set_config("Configure", "TOP_CROP", config.get("Default", "TOP_CROP"))
    header.set_config("Configure", "BOTTOM_CROP", config.get("Default", "BOTTOM_CROP"))
    header.set_config("Configure", "RIGHT_CROP", config.get("Default", "RIGHT_CROP"))
    header.set_config("Configure", "RESOLUTION", config.get("Default", "RESOLUTION"))
    header.set_config("Configure", "FLIP", config.get("Default", "FLIP"))
    header.set_config("Configure", "PCM", config.get("Default", "PCM"))

@app.route("/")
def home():
    reset_config()
    config = header.get_config()

    lower_bound_color, upper_bound_color = get_color_boundaries("Default")
    h_score = int(config.get("Default", "H_SCORE"))
    b_score = int(config.get("Default", "B_SCORE"))
    pcm = int(config.get("Default", "PCM"))

    top_crop = int(config.get("Default", "TOP_CROP"))
    bottom_crop = int(config.get("Default", "BOTTOM_CROP"))
    right_crop = int(config.get("Default", "RIGHT_CROP"))

    return render_template("index.html", lower_bound_color = lower_bound_color, upper_bound_color = upper_bound_color, h_score = h_score, b_score = b_score, pcm = pcm, top_crop = top_crop, bottom_crop = bottom_crop, right_crop = right_crop)

@app.route("/video", methods = ["GET"])
def video():
    threshold_status = request.args.get("threshold", "false") == "true"
    flip = request.args.get("flip", "false") == "true"
    reference = request.args.get("reference", "false") == "true"
    camera_status = request.args.get("camera_status", "false") == "true"
    crop_preview = request.args.get("crop_preview", "false") == "true"

    if flip:
        header.set_config("Configure", "FLIP", "True", )
    else:
        header.set_config("Configure", "FLIP", "False", )

    if camera_status:
        camera_data = camera.generate_frames(threshold_status = threshold_status, flip = flip, reference = reference, crop_preview = crop_preview)

        return Response(camera_data, mimetype = "multipart/x-mixed-replace; boundary=frame", status = 200)
    
    return Response("Camera is not started", status = 500)

@app.route("/change_threshold", methods = ["GET"])
def change_threshold():
    config = header.get_config()
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

    update_color_boundaries("Configure", lower_bound_color, upper_bound_color)
    return Response("OK", status = 200)

@app.route("/change_crop", methods = ["GET"])
def change_crop():
    config = header.get_config()
    top_crop = int(request.args.get("top_crop", config.get("Configure", "TOP_CROP")))
    bottom_crop = int(request.args.get("bottom_crop", config.get("Configure", "BOTTOM_CROP")))
    right_crop = int(request.args.get("right_crop", config.get("Configure", "RIGHT_CROP")))

    header.set_config("Configure", "TOP_CROP", str(top_crop), )
    header.set_config("Configure", "BOTTOM_CROP", str(bottom_crop), )
    header.set_config("Configure", "RIGHT_CROP", str(right_crop), )

    return Response("OK", status = 200)

@app.route("/change_score", methods = ["GET"])
def change_score():
    config = header.get_config()
    if request.args.get("b_score") == "NaN":
        h_score = float(request.args.get("h_score", config.get("Configure", "H_SCORE")))
        b_score = 0
        pcm = float(request.args.get("pcm", config.get("Configure", "PCM")))
    elif request.args.get("h_score") == "NaN":
        h_score = 0
        b_score = float(request.args.get("b_score", config.get("Configure", "B_SCORE")))
        pcm = float(request.args.get("pcm", config.get("Configure", "PCM")))
    elif request.args.get("pcm") == "NaN":
        h_score = float(request.args.get("h_score", config.get("Configure", "H_SCORE")))
        b_score = float(request.args.get("b_score", config.get("Configure", "B_SCORE")))
        pcm = 0
    else:
        h_score = float(request.args.get("h_score", config.get("Configure", "H_SCORE")))
        b_score = float(request.args.get("b_score", config.get("Configure", "B_SCORE")))
        pcm = float(request.args.get("pcm", config.get("Configure", "PCM")))

    header.set_config("Configure", "H_SCORE", str(h_score), )
    header.set_config("Configure", "B_SCORE", str(b_score), )
    header.set_config("Configure", "PCM", str(pcm), )

    return Response("OK", status = 200)

@app.route("/rotating_test", methods = ["GET"])
def rotating_test():
    process.rotating_test()
    return Response("OK", status = 200)

@app.route("/scanning", methods = ["GET"])
def scanning():
    config = header.get_config()
    folder_path = process.start_scanning()
    header.save_config(folder_path, dict(config["Configure"]))

    return Response(str(folder_path), status = 200)

@app.route("/generate", methods = ["GET"])
def generate():
    folder_path = request.args.get("folder_path", "")
    ploty_path, csv_path, mesh_path = process.generate_point_cloud(f"data/{folder_path}")
    if ploty_path is None or csv_path is None:
        return Response("No Image Found", status = 500)
    return Response(str(f"Plotly: {ploty_path} | CSV: {csv_path} | Mesh: {mesh_path}"), status = 200)

@app.route("/scanning_generate", methods = ["GET"])
def scanning_generate():
    folder_path = process.start_scanning()
    ploty_path, csv_path, mesh_path = process.generate_point_cloud(folder_path)
    return Response(str(f"Folder Path: {folder_path} | Plotly: {ploty_path} | CSV: {csv_path} | Mesh: {mesh_path}"), status = 200)

@app.route("/enable_camera", methods = ["GET"])
def enable_camera():
    config = header.get_config()
    res_width = int(request.args.get("res_width", config.get("Default", "RESOLUTION").split(",")[0]))
    res_height = int(request.args.get("res_height", config.get("Default", "RESOLUTION").split(",")[1]))

    camera.start_camera((res_width, res_height))
    return Response(f"{res_width}x{res_height}", status = 200)

@app.route("/disable_camera", methods = ["GET"])
def disable_camera():
    camera.stop_camera()
    return Response("OK", status = 200)

@app.route("/change_resolution", methods = ["GET"])
def change_resolution():
    config = header.get_config()
    res_width = int(request.args.get("res_width", config.get("Configure", "RESOLUTION").split(",")[0]))
    res_height = int(request.args.get("res_height", config.get("Configure", "RESOLUTION").split(",")[1]))

    header.set_config("Configure", "RESOLUTION", f"{res_width},{res_height}", )
    return Response("OK", status = 200)

@app.route("/take_file", methods = ["GET"])
def take_file():
    folder_path = "data/" + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".jpg"
    camera.take_file(folder_path)
    return Response(str(folder_path), status = 200)

def start(debug = False):
    app.run(host = "0.0.0.0", port = 5000, threaded = True, debug = debug)