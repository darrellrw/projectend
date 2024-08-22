import cv2

import app.calculation as calculation

cap = cv2.VideoCapture(0)

def generate_frames(threshold_status = False, lower_bound_color = (255, 150, 210), upper_bound_color = (255, 255, 255)):
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_copy = frame.copy()

        if threshold_status:
            frame_copy = calculation.color_range_threshold(frame_copy, lower_bound_color, upper_bound_color)

        ret, buffer = cv2.imencode('.jpg', frame_copy)
        if not ret:
            break

        frame_copy = buffer.tobytes()

        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame_copy + b'\r\n')

    cap.release()

def take_picture():
    ret, frame = cap.read()
    if not ret:
        return None
    
    return frame