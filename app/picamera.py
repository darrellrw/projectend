import os

import cv2

import header

from picamera2 import Picamera2

import app.calculation as calculation

picam = Picamera2(0)

def start_camera(size):
    picam.configure(picam.create_video_configuration(main = {"format": "XRGB8888", "size": size}))
    picam.start()

def stop_camera():
    picam.stop()

def generate_frames(threshold_status = False, flip = False, reference = False, crop_preview = False):
    config = header.get_config()
    while True:
        lower_bound_color = [int(i) for i in config.get("Configure", "LOWER_BOUND_COLOR").split(",")]
        upper_bound_color = [int(i) for i in config.get("Configure", "UPPER_BOUND_COLOR").split(",")]

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

        if crop_preview:
            right_crop = int(config.get("Configure", "RIGHT_CROP"))
            top_crop = int(config.get("Configure", "TOP_CROP"))
            bottom_crop = int(config.get("Configure", "BOTTOM_CROP"))

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
    
    picam.close()

def take_picture():
    return picam.capture_array()

def take_file(output):
    return picam.capture_file(output)