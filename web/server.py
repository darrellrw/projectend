try:
    import app.picamera as camera
except ImportError:
    import app.unicamera as camera

from flask import Flask, Response, render_template, request

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/video", methods = ["GET"])
def video():
    threshold_status = request.args.get("threshold", "False")

    lower_r = int(request.args.get("lower_r", 255))
    lower_g = int(request.args.get("lower_g", 150))
    lower_b = int(request.args.get("lower_b", 210))

    upper_r = int(request.args.get("upper_r", 255))
    upper_g = int(request.args.get("upper_g", 255))
    upper_b = int(request.args.get("upper_b", 255))


    if threshold_status == "True":
        return Response(camera.generate_frames(threshold_status = True, lower_bound_color = (lower_r, lower_g, lower_b), upper_bound_color = (upper_r, upper_g, upper_b)), mimetype = "multipart/x-mixed-replace; boundary=frame")

    return Response(camera.generate_frames(threshold_status = False), mimetype = "multipart/x-mixed-replace; boundary=frame")

def start():
    app.run(host = "0.0.0.0", port = 5000, threaded = True)