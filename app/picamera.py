import cv2

import header

from picamera2 import Picamera2

import app.calculation as calculation

picam = Picamera2(0)
picam.configure(picam.create_video_configuration(main = {"format": "XRGB8888", "size": (640, 480)}))
picam.start()

config = header.get_config()

def get_color_boundaries(section):
    lower_bound = [int(i) for i in config.get(section, "LOWER_BOUND_COLOR").split(",")]
    upper_bound = [int(i) for i in config.get(section, "UPPER_BOUND_COLOR").split(",")]
    return lower_bound, upper_bound

def generate_frames(threshold_status = False, flip = False, reference = False):
    while True:
        lower_bound_color, upper_bound_color = get_color_boundaries("Configure")

        frame = picam.capture_array()

        frame_copy = frame.copy()
        
        if flip:
            frame_copy = cv2.flip(frame_copy, 0)
            frame_copy = cv2.flip(frame_copy, 1)
        
        if reference:
            frame_copy = cv2.line(frame_copy, (0, frame_copy.shape[0] // 2), (frame_copy.shape[1], frame_copy.shape[0] // 2), (0, 0, 255), 2)
            frame_copy = cv2.line(frame_copy, (frame_copy.shape[1] // 2, 0), (frame_copy.shape[1] // 2, frame_copy.shape[0]), (0, 0, 255), 2)

        if threshold_status:
            frame_copy = calculation.color_range_threshold(frame_copy, tuple(lower_bound_color), tuple(upper_bound_color))

        ret, buffer = cv2.imencode(".jpg", frame_copy)

        if not ret:
            break

        frame_copy = buffer.tobytes()

        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame_copy + b'\r\n')
    
    picam.close()

def take_picture():
    return picam.capture_array()

def take_file(output):
    return picam.capture_file(output)