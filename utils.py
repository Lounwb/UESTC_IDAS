import cv2
import numpy as np
import base64
from io import BytesIO
from PIL import Image
import time

import random
import string

characters = string.ascii_letters + string.digits

def get(session, url, params=None, data=None):
    if params is not None and data is not None:
        response = session.get(url, params=params, data=data)
    elif params is not None:
        response = session.get(url, params=params)
    elif data is not None:
        response = session.get(url, data=data)
    else:
        response = session.get(url)
    return response

def post(session, url, params=None, data=None):
    if params is not None and data is not None:
        response = session.post(url, params=params, data=data)
    elif params is not None:
        response = session.post(url, params=params)
    elif data is not None:
        response = session.post(url, data=data)
    else:
        response = session.post(url)
    return response
def get_horizontal_distance(bigImage):
    distance = 0
    image = cv2.imdecode(np.fromstring(base64.b64decode(bigImage.split(';base64,')[0]), np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        return
    cv2.namedWindow("Slider Capcha")
    cv2.setWindowProperty("Slider Capcha", cv2.WND_PROP_TOPMOST, 1)

    cv2.resizeWindow("Slider Capcha", 295, 280)
    cv2.imshow("Slider Capcha", image)

    def mouse_callback(event, x, y, flags, param):
        nonlocal distance
        if event == cv2.EVENT_LBUTTONDOWN:
            distance = x
            # cv2.circle(image, (x, y), 3, (0, 0, 255), -1)
            cv2.imshow("Slider Capcha", image)
            cv2.destroyAllWindows()

    cv2.setMouseCallback("Slider Capcha", mouse_callback)

    k = cv2.waitKey(0)

    cv2.destroyAllWindows()
    # if k != 27:
    #     file_name = ''.join(random.choice(characters) for _ in range(16))
    #     cv2.imwrite(f"./datasets/images/val/{file_name}.png", image)
    #     # cv2.imwrite(f"./datasets/images/train/{file_name}.png", image)
    #     # with open("./datasets/train_dataset.csv", 'a') as f:
    #     with open("./datasets/val_dataset.csv", 'a') as f:
    #         f.write(f"{file_name}.png,{int((distance / 295 * 280) // 2)}\n")

    return (distance / 295 * 280) // 2, k
    # return distance // 2, k