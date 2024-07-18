try:
    import app.picamera as camera
except ImportError:
    import app.unicamera as camera

import header

import cv2

from flask import Flask, Response, render_template, request

app = Flask(__name__)

config = header.get_config()

@app.route("/")
def home():
    return render_template("index.html", lower_bound_color = [int(i) for i in config.get("Default", "DEFAULT_LOWER_BOUND_COLOR").split(",")], upper_bound_color = [int(i) for i in config.get("Default", "DEFAULT_UPPER_BOUND_COLOR").split(",")], h_score = int(config.get("Default", "DEFAULT_H_SCORE")), b_score = int(config.get("Default", "DEFAULT_B_SCORE")))

@app.route("/video", methods = ["GET"])
def video():
    threshold_status = request.args.get("threshold", "False")

    lower_r = int(config.get("Configure", "LOWER_BOUND_COLOR").split(",")[0])
    lower_g = int(config.get("Configure", "LOWER_BOUND_COLOR").split(",")[1])
    lower_b = int(config.get("Configure", "LOWER_BOUND_COLOR").split(",")[2])

    upper_r = int(config.get("Configure", "UPPER_BOUND_COLOR").split(",")[0])
    upper_g = int(config.get("Configure", "UPPER_BOUND_COLOR").split(",")[1])
    upper_b = int(config.get("Configure", "UPPER_BOUND_COLOR").split(",")[2])

    if threshold_status == "True":
        return Response(camera.generate_frames(threshold_status = True, lower_bound_color = (lower_r, lower_g, lower_b), upper_bound_color = (upper_r, upper_g, upper_b)), mimetype = "multipart/x-mixed-replace; boundary=frame")

    return Response(camera.generate_frames(threshold_status = False), mimetype = "multipart/x-mixed-replace; boundary=frame")

@app.route("/change_threshold", methods = ["GET"])
def change_threshold():
    lower_r = int(request.args.get("lower_r", config.get("Configure", "LOWER_BOUND_COLOR").split(",")[0]))
    lower_g = int(request.args.get("lower_g", config.get("Configure", "LOWER_BOUND_COLOR").split(",")[1]))
    lower_b = int(request.args.get("lower_b", config.get("Configure", "LOWER_BOUND_COLOR").split(",")[2]))

    upper_r = int(request.args.get("upper_r", config.get("Configure", "UPPER_BOUND_COLOR").split(",")[0]))
    upper_g = int(request.args.get("upper_g", config.get("Configure", "UPPER_BOUND_COLOR").split(",")[1]))
    upper_b = int(request.args.get("upper_b", config.get("Configure", "UPPER_BOUND_COLOR").split(",")[2]))

    header.set_config("Configure", "LOWER_BOUND_COLOR", f"{lower_r},{lower_g},{lower_b}")
    header.set_config("Configure", "UPPER_BOUND_COLOR", f"{upper_r},{upper_g},{upper_b}")

    return "OK"

@app.route("/change_score", methods = ["GET"])
def change_score():
    h_score = int(request.args.get("h_score", config.get("Configure", "H_SCORE")))
    b_score = int(request.args.get("b_score", config.get("Configure", "B_SCORE")))

    header.set_config("Configure", "H_SCORE", str(h_score))
    header.set_config("Configure", "B_SCORE", str(b_score))

    return "OK"

@app.route("/picture", methods = ["GET"])
def picture():
    frame = camera.take_picture()
    cv2.imwrite("data/image.jpg", frame)
    return "OK"

def start():
    app.run(host = "0.0.0.0", port = 5000, threaded = True)