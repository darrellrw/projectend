import cv2

import app.imageprocess as imageprocess

cap = cv2.VideoCapture(0)

def generate_frames(threshold_status = False, lower_bound_color = (255, 150, 210), upper_bound_color = (255, 255, 255)):

    while True:
        ret, frame = cap.read()
        frame_copy = frame.copy()

        if threshold_status:
            frame_copy = imageprocess.color_range_threshold(frame_copy, lower_bound_color, upper_bound_color)

        ret, buffer = cv2.imencode('.jpg', frame_copy)
        frame_copy = buffer.tobytes()

        if not ret:
            break

        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame_copy + b'\r\n')

    cap.release()