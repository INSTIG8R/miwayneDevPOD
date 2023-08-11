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
import asyncio

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
from .GetAuth0Token import GetAuth0Token


def main(myblob: func.InputStream):
    logging.info(f"Python blob trigger function processed blob \n"
                 f"Name: {myblob.name}\n"
                 f"Blob Size: {myblob.length} bytes")
    
    logging.info("###########################  new function started  ###########################")

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

    folderName = f"./{fileNameNoExt}"

    logging.info(f"Folder Name is : {folderName}")

    # if os.path.exists('./tmp'):
    #     DeleteFolderContents_result = DeleteFolderContents('./tmp')
    #     logging.info(DeleteFolderContents_result)

    if not os.path.exists(f'{folderName}/image'):
        os.makedirs(f'{folderName}/image')

    filePath = f'{folderName}/image' + fileName

    logging.info(f"file path is : {filePath}")

    with open(filePath, 'wb') as f:
        f.write(bytes_file)


    if not os.path.exists(f'{folderName}/manual'):
        os.makedirs(f'{folderName}/manual')

    if not os.path.exists(f'{folderName}/processed'):
        os.makedirs(f'{folderName}/processed')

    confi = r'''
    {
    "OCR": {
        "ImagePreprocessing": {
        "Deskew": true,
        "CorrectOrientation": true,
        "EnhanceContrast": true,
        "Binarize": true
        },
        "Segmentation": {
        "Mode": "Paragraph",
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

    id_token = GetAuth0Token()

    with open(f'{folderName}/TextDetected.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write header row to the CSV file
        writer.writerow(['Filename', 'Extracted Text'])

    for filename_png in os.listdir(f'{folderName}/image/'):

        logging.info(f"started working on {filename_png}")

        if filename_png.endswith('.png'):

            try:
                image = cv2.imread(f'{folderName}/image/{filename_png}')

                cleaned = clean_image(image)
                text = pytesseract.image_to_string(cleaned, config=confi)

                with open(f'{folderName}/TextDetected.csv', mode='a', newline='') as file:
                    writer = csv.writer(file)
                    if text.strip():
                        writer.writerow([filename_png, text])
            except:
                logging.info("Error in Text extraction from whole image.")

        try:
            # bounding boxes are saved in a folder
            cropBoundingBox_result = cropBoundingBox(cleaned, filename_png, folderName)

            logging.info(cropBoundingBox_result)

            # Set cropped image folder path
            bounding_box_path = f'{folderName}/croppedImage/{filename_png[:-4]}_boxes'

            with open(f'{folderName}/Cropped_Text.csv', mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Filename', 'Extracted Text'])

            for filename_box in os.listdir(bounding_box_path):

                if filename_box.endswith('.png'):

                    image_box = cv2.imread(
                        f'{bounding_box_path}/{filename_box}')

                    text = pytesseract.image_to_string(image_box, config=confi)

                    with open(f'{folderName}/Cropped_Text.csv', mode='a', newline='') as file:
                        writer = csv.writer(file)
                        if text.strip():
                            writer.writerow([filename_box, text])

        except:
            logging.info("Couldn't create bounding boxes, tile cannot extend outside image")

        try:
            dates, Codes, Times, from_ad, to_ad = '', '', '', None, None
            whole_page = pd.read_csv(f'{folderName}/TextDetected.csv')
            dates, Codes, Times, from_ad, to_ad, uniqueCode = dateAndCode_extraction(
                whole_page, image, folderName)
            # dateAndCode_CSV = pd.read_csv(f'{folderName}/Date_Code.csv')

            address_from_croppedImageCSV_result = address_from_croppedImageCSV(id_token)

            logging.info(address_from_croppedImageCSV_result)

            date, time, code, fromA, toA, manual = values(
                dates, Times, Codes, from_ad, to_ad, uniqueCode, f'{folderName}/Address_found.csv')

            if not code.strip():
                manual = True
                logging.info("ConNote not found")

            logging.info(f"\n\nDate Time Code:{date},{time},{code}\n"
                         f"\nSender: {fromA}\n"
                         f"\nReceiver: {toA}\n"
                         f"\nManual: {manual}")
            
            create_JSON_result = create_JSON(filename_png, date, time, code, fromA, toA, manual)

            logging.info(create_JSON_result)

            deliveryDate = format_datetime(date,time)

            if manual:
                customerPath = f"manual_{filename_png}.pdf"

                img = Image.open(f'{folderName}/image/{filename_png}')
                pdf_filename = f'{folderName}/manual/manual_{filename_png[:-4]}.pdf'
                Blobfilename = f'{filename_png[:-4]}.pdf'

                img.save(pdf_filename, 'PDF', resolution=100.0)
                logging.info("Manual Version generated")

                log = UploadManualToBlob(pdf_filename, Blobfilename)
                logging.info(f"from init py log = {log}")
                response = UploadManualToMiwayne(id,code, fromA,toA,deliveryDate,id_token)
                logging.info(f"miwayne upload from init py = {response}")

                logging.info("Manual Version uploaded successfully from init")

            else:
                # generate_pdf(date, time, code, fromA,
                #              toA, manual, filename_png)
                
                logging.info("All Data stripped successfully")

                customerPath = f"{code}.pdf"
                img = Image.open(f'{folderName}/image/{filename_png}')
                pdf_filename = f'{folderName}/processed/{customerPath}'
                Blobfilename = f'{customerPath}'

                img.save(pdf_filename, 'PDF', resolution=100.0)

                log = UploadProcessedToBlob(pdf_filename, Blobfilename)
                logging.info(f"from init py log = {log}")
                response = UploadProcessedToMiwayne(id,code, fromA,toA,deliveryDate,id_token)
                logging.info(f"miwayne upload from init py = {response}")
                logging.info(f"{code} Processed Version uploaded successfully from init")

        except:
            logging.info("Error in generating Customer Version PDF.")

            img = Image.open(f'{folderName}/image/{filename_png}')
            pdf_filename = f'{folderName}/manual/manual_{filename_png[:-4]}.pdf'
            Blobfilename = f'{filename_png[:-4]}.pdf'

            img.save(pdf_filename, 'PDF', resolution=100.0)
            logging.info("Manual Version generated from except block")

            log = UploadManualToBlob(pdf_filename, Blobfilename)
            logging.info(f"from init py log = {log}")
            response = UploadManualToMiwayne(id,code, fromA,toA,deliveryDate,id_token)
            logging.info(f"miwayne upload from init py = {response}")
            logging.info("Manual Version uploaded successfully from except block in init")

        logging.info(f"finised working on {filename_png}")

    logging.info(f"completed working on function {fileName}")