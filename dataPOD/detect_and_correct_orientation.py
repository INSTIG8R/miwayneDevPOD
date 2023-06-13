import cv2
import numpy as np


def detect_and_correct_orientation(image):
    # Load the image and convert it to grayscale
    #image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply thresholding to obtain a binary image
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)

    # Find contours in the binary image
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Sort the contours in descending order of their areas
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    # Find the box with the largest area
    largest_box = contours[0]   #max(boxes, key=cv2.contourArea)

    # Determine the angle of the largest box
    rect = cv2.minAreaRect(largest_box)
    angle = rect[-1]

    # If the angle is less than -45 degrees, add 90 degrees to it
    if angle < -45:
        angle += 90
    elif angle > 45:
        angle-=90

    # Rotate the image by the determined angle
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    return rotated
