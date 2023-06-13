import cv2
from PIL import Image
from .detect_and_correct_orientation import detect_and_correct_orientation
# Load the PNG image


def clean_image(img):
    # Prep image, copy, convert to gray scale, blur, and threshold

    newImage = detect_and_correct_orientation(img)
    # newImage = img.copy()

    gray = cv2.cvtColor(newImage, cv2.COLOR_BGR2GRAY)
    # blur = cv2.GaussianBlur(gray, (3, 3), 0)
    thresh = cv2.threshold(
        gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    thresh = cv2.bitwise_not(thresh)  # Invert the image
    return thresh
