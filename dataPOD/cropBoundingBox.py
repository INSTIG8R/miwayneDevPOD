import cv2
import numpy as np
from PIL import Image
import os
# Load the PNG image


def cropBoundingBox(img, filename):

    newImage = img.copy()
    image = img.copy()

    # Find all contours
    contours, hierarchy = cv2.findContours(
        image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    # Set a minimum threshold for the size of the bounding box
    min_box_size = 200
    max_box_size = 600

    if not os.path.exists(f"./tmp/croppedImage/{filename[:-4]}_boxes"):
        os.makedirs(f"./tmp/croppedImage/{filename[:-4]}_boxes")

    for i, contour in enumerate(contours):
        # Get the minimum bounding rectangle
        rect = cv2.minAreaRect(contour)
        box = cv2.boxPoints(rect)
        box = np.int0(box)

        # Check the area of the bounding box
        if rect[1][0] * rect[1][1] < min_box_size * min_box_size:
            # Skip small boxes
            continue

        if rect[1][0] * rect[1][1] > max_box_size * max_box_size:
            # Skip large boxes
            continue

        # Increase the size of the bounding boxes
        rect = (rect[0], (int(rect[1][0] * 1.1),
                int(rect[1][1] * 1.2)), rect[2])

        # Draw the bounding box
        cv2.drawContours(image, [box], 0, (0, 255, 0), 2)

        # Crop the bounding box
        x, y, w, h = cv2.boundingRect(box)
        roi = image[y:y+h, x:x+w]
        cv2.imwrite(
            f"./tmp/croppedImage/{filename[:-4]}_boxes/box_{i+1}.png", roi)

    cv2.imwrite(f"./tmp/{filename[:-4]}_bounding_image.jpg", image)

    log = "finised function cropBoundingBox"

    return log
