import cv2
import numpy as np
import base64
from io import BytesIO
from PIL import Image
import time


def get_horizontal_distance(bigImage):
    distance = 0
    image = cv2.imdecode(np.fromstring(base64.b64decode(bigImage.split(';base64,')[0]), np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        return

    cv2.namedWindow("Image")
    cv2.imshow("Image", image)

    points = []

    def mouse_callback(event, x, y, flags, param):
        nonlocal distance
        if event == cv2.EVENT_LBUTTONDOWN:
            points.append((x, y))
            cv2.circle(image, (x, y), 3, (0, 0, 255), -1)
            cv2.imshow("Image", image)

            if len(points) == 2:
                distance = abs(points[1][0] - points[0][0])
                cv2.destroyAllWindows()

    cv2.setMouseCallback("Image", mouse_callback)

    cv2.waitKey(0)

    cv2.destroyAllWindows()
    return distance/2