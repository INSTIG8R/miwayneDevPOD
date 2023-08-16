import cv2
import numpy as np
from PIL import Image
import os
import logging
# Load the PNG image


def cropBoundingBox(img, filename, folderName):

    newImage = img.copy()
    image = img.copy()

    # Find all contours
    contours, hierarchy = cv2.findContours(
        image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    # Set a minimum threshold for the size of the bounding box
    min_box_size = 200
    max_box_size = 600

    croppedBoxFolder = folderName + "croppedImage/" + filename[:-4] + "_boxes"
    if not os.path.exists(croppedBoxFolder):
        os.makedirs(croppedBoxFolder)
        logging.info(f"cropped box folder created : {croppedBoxFolder}")

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
        boxPNGPath = croppedBoxFolder + "/box_" + str(i+1) + ".png"
        cv2.imwrite(
            boxPNGPath, roi)


    boundingImagePath = folderName + filename[:-4] + "_bounding_image.jpg"
    cv2.imwrite(boundingImagePath, image)

    log = "finised function cropBoundingBox"

    return log
