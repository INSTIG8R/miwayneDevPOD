import logging
import base64
import azure.functions as func
import os
import cv2
import csv
import numpy as np
import pytesseract
from PIL import Image
import pandas as pd

from .clean_image import clean_image
from .cropBoundingBox import cropBoundingBox
from .dateAndCode_extraction import dateAndCode_extraction
from .address_from_croppedImage import address_from_croppedImageCSV
from .values import values
from .create_JSON import create_JSON
from .DeleteFolderContents import DeleteFolderContents
from .UploadManualToBlob import UploadManualToBlob
from .UploadProcessedToBlob import UploadProcessedToBlob
from .UploadManualToMiwayne import UploadManualToMiwayne
from .UploadProcessedToMiwayne import UploadProcessedToMiwayne
from .format_datetime import format_datetime

# from .generate_pdf import generate_pdf

def main(myblob: func.InputStream):
    logging.info(f"Python blob trigger function processed blob \n"
                 f"Name: {myblob.name}\n"
                 f"Blob Size: {myblob.length} bytes")
    
    nameWithPath = myblob.name
    fileName = nameWithPath.split("/")[-1]
    fileNameNoExt = fileName.split(".")[:-1]

    # Extract the desired part
    start_index = nameWithPath.rfind('_') + 1
    end_index = nameWithPath.rfind('.')
    id = nameWithPath[start_index:end_index]

    # logging.info("file name: {}".format(fileName))
    logging.info("filename : " + fileName)

    fileData = myblob.read()
    encoded_string = base64.b64encode(fileData)
    bytes_file = base64.b64decode(encoded_string, validate=True)

    if os.path.exists('./tmp'):
        DeleteFolderContents('./tmp')

    if not os.path.exists('./tmp/image'):
        os.makedirs('./tmp/image')

    filePath = './tmp/image/' + fileName

    with open(filePath, 'wb') as f:
        f.write(bytes_file)


    if not os.path.exists('./tmp/manual'):
        os.makedirs('./tmp/manual')

    if not os.path.exists('./tmp/processed'):
        os.makedirs('./tmp/processed')

    confi = r'''
    {
    "OCR": {
        "ImagePreprocessing": {
        "Deskew": true,
        "CorrectOrientation": true
        },
        "Segmentation": {
        "Mode": "Block",
        "Language": "eng",
        "PageSegMode": "auto"
        },
        "Recognition": {
        "EngineMode": "LSTM_ONLY",
        "CharWhitelist": "",
        "CharBlacklist": "",
        "PSM": "auto",
        "OEM": "DEFAULT"
        }
    }
    }
    '''

    with open('./tmp/TextDetected.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write header row to the CSV file
        writer.writerow(['Filename', 'Extracted Text'])

    for filename_png in os.listdir('./tmp/image/'):

        if filename_png.endswith('.png'):

            try:
                image = cv2.imread(f'./tmp/image/{filename_png}')

                cleaned = clean_image(image)
                text = pytesseract.image_to_string(cleaned, config=confi)

                with open('./tmp/TextDetected.csv', mode='a', newline='') as file:
                    writer = csv.writer(file)
                    if text.strip():
                        writer.writerow([filename_png, text])
            except:
                logging.info("Error in Text extraction from whole image.")

        try:
            # bounding boxes are saved in a folder
            cropBoundingBox(cleaned, filename_png)

            # Set cropped image folder path
            bounding_box_path = f"./tmp/croppedImage/{filename_png[:-4]}_boxes"

            with open('./tmp/Cropped_Text.csv', mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Filename', 'Extracted Text'])

            for filename_box in os.listdir(bounding_box_path):

                if filename_box.endswith('.png'):

                    image_box = cv2.imread(
                        f'{bounding_box_path}/{filename_box}')

                    text = pytesseract.image_to_string(image_box, config=confi)

                    with open('./tmp/Cropped_Text.csv', mode='a', newline='') as file:
                        writer = csv.writer(file)
                        if text.strip():
                            writer.writerow([filename_box, text])

        except:
            logging.info("Couldn't create bounding boxes, tile cannot extend outside image")

        try:
            dates, Codes, Times, from_ad, to_ad = '', '', '', None, None
            whole_page = pd.read_csv('./tmp/TextDetected.csv')
            dates, Codes, Times, from_ad, to_ad, uniqueCode = dateAndCode_extraction(
                whole_page, image)
            # dateAndCode_CSV = pd.read_csv('./tmp/Date_Code.csv')

            address_from_croppedImageCSV()

            date, time, code, fromA, toA, manual = values(
                dates, Times, Codes, from_ad, to_ad, uniqueCode, './tmp/Address_found.csv')

            logging.info(f"\n\nDate Time Code:{date},{time},{code}\n"
                         f"\nSender: {fromA}\n"
                         f"\nReceiver: {toA}\n"
                         f"\nManual: {manual}")
            create_JSON(filename_png, date, time, code, fromA, toA, manual)

            deliveryDate = format_datetime(date,time)

            if manual:
                customerPath = f"manual_{filename_png}.pdf"

                img = Image.open(f"./tmp/image/{filename_png}")
                pdf_filename = f'./tmp/manual/manual_{filename_png[:-4]}.pdf'
                Blobfilename = f'{filename_png[:-4]}.pdf'

                img.save(pdf_filename, 'PDF', resolution=100.0)
                logging.info("Manual Version generated")

                UploadManualToBlob(pdf_filename, Blobfilename)
                UploadManualToMiwayne(id,code, fromA,toA,deliveryDate)

                logging.info("Manual Version uploaded successfully from init")

            else:
                # generate_pdf(date, time, code, fromA,
                #              toA, manual, filename_png)
                
                logging.info("All Data stripped successfully")

                customerPath = f"{code}.pdf"
                img = Image.open(f"./tmp/image/{filename_png}")
                pdf_filename = f'./tmp/processed/{customerPath}'
                Blobfilename = f'{customerPath}'

                img.save(pdf_filename, 'PDF', resolution=100.0)

                UploadProcessedToBlob(pdf_filename, Blobfilename)
                UploadProcessedToMiwayne(id,code, fromA,toA,deliveryDate)

                logging.info(f"{code} Processed Version uploaded successfully from init")

        except:
            logging.info("Error in generating Customer Version PDF.")

            img = Image.open(f"./tmp/image/{filename_png}")
            pdf_filename = f'./tmp/manual/manual_{filename_png[:-4]}.pdf'
            Blobfilename = f'{filename_png[:-4]}.pdf'

            img.save(pdf_filename, 'PDF', resolution=100.0)
            logging.info("Manual Version generated from except block")

            UploadManualToBlob(pdf_filename, Blobfilename)
            UploadManualToMiwayne(id,code, fromA,toA,deliveryDate)
            logging.info("Manual Version uploaded successfully from except block in init")