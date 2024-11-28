import cv2
import numpy as np

from picamera2 import Picamera2

import app.algorithm as algorithm

picam = Picamera2(0)

def start_camera(size):
    picam.configure(picam.create_video_configuration(main = {"format": "XRGB8888", "size": size}))
    picam.start()

def stop_camera():
    picam.stop()

def take_file(output):
    return picam.capture_file(output)

def take_picture():
    return picam.capture_array()

def generate_frames(lower_bound_color, upper_bound_color, crop, threshold = False, reference = False, crop_preview = False):
    while True:
        frame = picam.capture_array()
        frame_copy = frame.copy()

        if threshold:
            frame_copy = algorithm.color_range_threshold(frame_copy, np.array(lower_bound_color), np.array(upper_bound_color))
        
        if reference:
            frame_copy = cv2.line(frame_copy, (0, frame_copy.shape[0] // 2), (frame_copy.shape[1], frame_copy.shape[0] // 2), (0, 0, 255), 2)
            frame_copy = cv2.line(frame_copy, (frame_copy.shape[1] // 2, 0), (frame_copy.shape[1] // 2, frame_copy.shape[0]), (0, 0, 255), 2)

        if crop_preview:
            top_crop, bottom_crop, right_crop = crop

            height, width, _ = frame_copy.shape

            if right_crop <= width and right_crop >= width//2:
                frame_copy = frame_copy[:, width//2:right_crop]
            if top_crop >= 0 and top_crop <= height//2 and bottom_crop <= height and bottom_crop >= height//2:
                frame_copy = frame_copy[top_crop:bottom_crop, :]

        ret, buffer = cv2.imencode(".jpg", frame_copy)

        if not ret:
            break

        frame_copy = buffer.tobytes()

        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame_copy + b'\r\n')