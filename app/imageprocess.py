import cv2

# Setelah melakukan threshold nanti mencari contour dari cahaya laser dan mencari garis tengah dari laser tersebut

def color_range_threshold(image, lower_bound_color, upper_bound_color):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    mask = cv2.inRange(hsv, lower_bound_color, upper_bound_color)
    return mask