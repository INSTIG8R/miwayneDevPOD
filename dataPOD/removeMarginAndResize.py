import cv2
from .clean_image import clean_image
import numpy as np

# Remove Margin


def remove_margin(image):
    # image = cv2.imread(image_path)
    thresh1 = clean_image(image)
    thresh = cv2.bitwise_not(thresh1)
    # Find the contours of the connected components in the image
    contours, _ = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Find the bounding box that contains all the contours
    bounding_rect = cv2.boundingRect(np.concatenate(contours))

    # Crop the image using the bounding box coordinates
    cropped_image = thresh1[bounding_rect[1]:bounding_rect[1] +
                            bounding_rect[3], bounding_rect[0]:bounding_rect[0]+bounding_rect[2]]

    # Save the cropped image
    cv2.imwrite('noMargin_cropped.png', cropped_image)
    return cropped_image


# Resize Image
def resized_image(image):
    height, width = image.shape[:2]

    # Resize the image to have a maximum width of 900 pixels
    max_width = 900
    ratio = max_width / width
    new_size = (int(width * ratio), int(height * ratio))
    resized_image = cv2.resize(image, new_size)
    return resized_image
