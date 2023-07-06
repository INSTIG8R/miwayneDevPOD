import logging
import cv2
import pytesseract
from .removeMarginAndResize import *


def sealink_address(img):

    img = resized_image(img)
    # Define the region of interest
    # Sender
    x1 = 5
    y1 = 290
    w1 = 290
    h1 = 110

    # Receiver
    x2 = 330
    y2 = 290
    w2 = 290
    h2 = 110

    # Crop the region of interest
    roi1 = img[y1:y1+h1, x1:x1+w1]
    roi2 = img[y2:y2+h2, x2:x2+w2]

    # Apply Pytesseract OCR to extract the text
    text1 = pytesseract.image_to_string(roi1, lang='eng')
    text2 = pytesseract.image_to_string(roi2, lang='eng')

    from_address = text1.strip().replace("\\n", "\n")
    to_address = text2.strip().replace("\\n", "\n")

    return from_address, to_address


def bascik(img):

    no_margin_img = remove_margin(img)
    img = resized_image(no_margin_img)
    # Define the region of interest
    # Sender
    x1 = 30
    y1 = 190
    w1 = 360
    h1 = 140

    # Receiver
    x2 = 460
    y2 = 190
    w2 = 360
    h2 = 140

    # Refcode
    x3 = 630
    y3 = 150
    w3 = 160
    h3 = 40

    # Crop the region of interest
    roi1 = img[y1:y1+h1, x1:x1+w1]
    roi2 = img[y2:y2+h2, x2:x2+w2]
    roi3 = img[y3:y3+h3, x3:x3+w3]

    # Apply Pytesseract OCR to extract the text
    text1 = pytesseract.image_to_string(roi1, lang='eng')
    text2 = pytesseract.image_to_string(roi2, lang='eng')
    text3 = pytesseract.image_to_string(roi3, lang='eng')

    from_address = text1.strip().replace("\\n", "\n")
    to_address = text2.strip().replace("\\n", "\n")
    refcode = text3.strip().replace("\\n", "\n")

    # logging.info the extracted text
    logging.info(f"\n{from_address}")
    logging.info(f"\n{to_address}")
    logging.info(f"\n {refcode}" )
    return from_address, to_address, refcode

# info = pd.read_csv('Text.csv')
# text = info['Text'][0].strip()
# a,b=unique_address(text)
# a


def sub60(img):
    img = resized_image(img)
    # Define the region of interest
    # Sender
    x1 = 10
    y1 = 330
    w1 = 360
    h1 = 120

    # Receiver
    x2 = 10
    y2 = 450
    w2 = 360
    h2 = 120

    # Crop the region of interest
    roi1 = img[y1:y1+h1, x1:x1+w1]
    roi2 = img[y2:y2+h2, x2:x2+w2]

    # Apply Pytesseract OCR to extract the text
    text1 = pytesseract.image_to_string(roi1, lang='eng')
    text2 = pytesseract.image_to_string(roi2, lang='eng')

    from_address = text1.strip().replace("\\n", "\n")
    to_address = text2.strip().replace("\\n", "\n")

    # logging.info the extracted text
    logging.info(from_address)
    logging.info(to_address)

    return from_address, to_address
