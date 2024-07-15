import cv2
import numpy as np

from picamera2 import Picamera2

picam = Picamera2(0)
picam.configure(picam.create_preview_configuration(main={"format": "XRGB8888", "size": (640, 480)}))
picam.start()

def generate_frames():
    while True:
        frame = picam.capture_array()

        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        frame_copy = frame.copy()

        ret, buffer = cv2.imencode(".jpg", frame_copy)

        if not ret:
            break

        frame_copy = buffer.tobytes()

        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame_copy + b'\r\n')
    
    picam.close()