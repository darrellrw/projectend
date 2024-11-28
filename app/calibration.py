import cv2
import numpy as np
import imutils
from scipy.spatial import distance as dist
from imutils import perspective
from imutils import contours

def midpoint(ptA, ptB):
    return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)

def process_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (7, 7), 0)

    edged = cv2.Canny(gray, 50, 100)
    edged = cv2.dilate(edged, None, iterations=1)
    edged = cv2.erode(edged, None, iterations=1)

    cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    (cnts, _) = contours.sort_contours(cnts)
    
    # pixelsPerMilimeter = None
    output_image = image.copy()

    for c in cnts:
        if cv2.contourArea(c) < 100:
            continue
        box = cv2.minAreaRect(c)
        box = cv2.cv.BoxPoints(box) if imutils.is_cv2() else cv2.boxPoints(box)
        box = np.array(box, dtype="int")
        box = perspective.order_points(box)
        cv2.drawContours(output_image, [box.astype("int")], -1, (0, 255, 0), 2)

        for (x, y) in box:
            cv2.circle(output_image, (int(x), int(y)), 5, (0, 0, 255), -1)

        (tl, tr, br, bl) = box
        (tltrX, tltrY) = midpoint(tl, tr)
        (blbrX, blbrY) = midpoint(bl, br)
        (tlblX, tlblY) = midpoint(tl, bl)
        (trbrX, trbrY) = midpoint(tr, br)

        cv2.circle(output_image, (int(tltrX), int(tltrY)), 5, (255, 0, 0), -1)
        cv2.circle(output_image, (int(blbrX), int(blbrY)), 5, (255, 0, 0), -1)
        cv2.circle(output_image, (int(tlblX), int(tlblY)), 5, (255, 0, 0), -1)
        cv2.circle(output_image, (int(trbrX), int(trbrY)), 5, (255, 0, 0), -1)

        cv2.line(output_image, (int(tltrX), int(tltrY)), (int(blbrX), int(blbrY)), (255, 0, 255), 2)
        cv2.line(output_image, (int(tlblX), int(tlblY)), (int(trbrX), int(trbrY)), (255, 0, 255), 2)

        dA = dist.euclidean((tltrX, tltrY), (blbrX, blbrY))
        dB = dist.euclidean((tlblX, tlblY), (trbrX, trbrY))

        # if pixelsPerMilimeter is None:
        #     pixelsPerMilimeter = dB / width

        # dimA = dA / pixelsPerMilimeter
        # dimB = dB / pixelsPerMilimeter

        # cv2.putText(output_image, "{:.1f}mm".format(dimA), (int(tltrX - 15), int(tltrY - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
        # cv2.putText(output_image, "{:.1f}mm".format(dimB), (int(trbrX + 10), int(trbrY)), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
        cv2.putText(output_image, "{:.1f}px".format(dA), (int(tltrX - 15), int(tltrY + 20)), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
        cv2.putText(output_image, "{:.1f}px".format(dB), (int(trbrX + 10), int(trbrY + 30)), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
    
    return output_image