try:
    import app.picamera as camera
except ImportError:
    import app.unicamera as camera

import header
import app.process as process

from flask import Flask, Response, render_template, request

app = Flask(__name__)
config = header.get_config()

# Utility function to fetch configuration values
def get_color_boundaries(section):
    lower_bound = [int(i) for i in config.get(section, "LOWER_BOUND_COLOR").split(",")]
    upper_bound = [int(i) for i in config.get(section, "UPPER_BOUND_COLOR").split(",")]
    return lower_bound, upper_bound

def update_color_boundaries(section, lower_bound, upper_bound):
    header.set_config(section, "LOWER_BOUND_COLOR", ",".join(map(str, lower_bound)))
    header.set_config(section, "UPPER_BOUND_COLOR", ",".join(map(str, upper_bound)))

@app.route("/")
def home():
    lower_bound_color, upper_bound_color = get_color_boundaries("Default")
    h_score = int(config.get("Default", "H_SCORE"))
    b_score = int(config.get("Default", "B_SCORE"))

    return render_template("index.html", lower_bound_color = lower_bound_color, upper_bound_color = upper_bound_color, h_score = h_score, b_score = b_score)

@app.route("/video", methods = ["GET"])
def video():
    threshold_status = request.args.get("threshold", "false") == "true"
    flip = request.args.get("flip", "false") == "true"
    reference = request.args.get("reference", "false") == "true"

    return Response(camera.generate_frames(threshold_status = threshold_status, flip = flip, reference = reference), mimetype = "multipart/x-mixed-replace; boundary=frame", status = 200)

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

    update_color_boundaries("Configure", lower_bound_color, upper_bound_color)
    return Response("OK", status = 200)

@app.route("/change_score", methods = ["GET"])
def change_score():
    if request.args.get("b_score") == "NaN":
        h_score = float(request.args.get("h_score", config.get("Configure", "H_SCORE")))
        b_score = 0
    elif request.args.get("h_score") == "NaN":
        h_score = 0
        b_score = float(request.args.get("b_score", config.get("Configure", "B_SCORE")))
    else:
        h_score = float(request.args.get("h_score", config.get("Configure", "H_SCORE")))
        b_score = float(request.args.get("b_score", config.get("Configure", "B_SCORE")))

    header.set_config("Configure", "H_SCORE", str(h_score))
    header.set_config("Configure", "B_SCORE", str(b_score))

    return Response("OK", status = 200)

@app.route("/rotating_test", methods = ["GET"])
def rotating_test():
    process.rotating_test()
    return Response("OK", status = 200)

@app.route("/scanning", methods = ["GET"])
def scanning():
    folder_path = process.start_scanning()
    return Response(str(folder_path), status = 200)

@app.route("/generate", methods = ["GET"])
def generate():
    folder_path = request.args.get("folder_path", "")
    ploty_path, csv_path = process.generate_point_cloud(f"data/{folder_path}")
    if ploty_path is None or csv_path is None:
        return Response("No Image Found", status = 500)
    return Response(str(f"Plotly: {ploty_path} | CSV: {csv_path}"), status = 200)

@app.route("/scanning_generate", methods = ["GET"])
def scanning_generate():
    folder_path = process.start_scanning()
    ploty_path, csv_path = process.generate_point_cloud(folder_path)
    return Response(str(f"Folder Path: {folder_path} | Plotly: {ploty_path} | CSV: {csv_path}"), status = 200)

def start():
    app.run(host = "0.0.0.0", port = 5000, threaded = True)