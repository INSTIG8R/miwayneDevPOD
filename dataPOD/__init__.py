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


async def main(myblob: func.InputStream):
    logging.info(f"Python blob trigger function processed blob \n"
                 f"Name: {myblob.name}\n"
                 f"Blob Size: {myblob.length} bytes")
    
    logging.info("###########################  new function started  ###########################")

    nameWithPath = myblob.name
    fileName = nameWithPath.split("/")[-1]
    fileNameNoExt = fileName.split(".")[:-1]
    fileNameNoExt = fileNameNoExt[0]

    # Extract the desired part
    start_index = nameWithPath.rfind('_') + 1
    end_index = nameWithPath.rfind('.')
    id = nameWithPath[start_index:end_index]

    # logging.info("file name: {}".format(fileName))
    logging.info("filename : " + fileName)
    logging.info(f"file name without extension : {fileNameNoExt}")

    fileData = myblob.read()
    encoded_string = base64.b64encode(fileData)
    bytes_file = base64.b64decode(encoded_string, validate=True)

    folderName = "./" + fileNameNoExt +"/"

    logging.info(f"Folder Name is : {folderName}")

    if os.path.exists(folderName):
        DeleteFolderContents_result = DeleteFolderContents(folderName)
        logging.info(DeleteFolderContents_result)

    imageFolder = folderName + "image" + "/"

    if not os.path.exists(imageFolder):
        os.makedirs(imageFolder)
        logging.info(f"image folder created : {imageFolder}")

    filePath = imageFolder + fileName

    with open(filePath, 'wb') as f:
        f.write(bytes_file)

    logging.info(f"file path is : {filePath}")

    

    manualFolder = folderName + "manual" + "/"

    if not os.path.exists(manualFolder):
        os.makedirs(manualFolder)
        logging.info(f"image folder created : {manualFolder}")

    processedFolder = folderName + "processed" + "/"

    if not os.path.exists(processedFolder):
        os.makedirs(processedFolder)
        logging.info(f"image folder created : {processedFolder}")

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

    textDetectedPath = folderName + "TextDetected.csv"

    with open(textDetectedPath, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write header row to the CSV file
        writer.writerow(['Filename', 'Extracted Text'])

    for filename_png in os.listdir(imageFolder):

        logging.info(f"started working on {filename_png}")

        if filename_png.endswith('.png'):

            try:
                filename_png_path = imageFolder + filename_png
                image = cv2.imread(filename_png_path)

                cleaned = clean_image(image)
                text = pytesseract.image_to_string(cleaned, config=confi)

                with open(textDetectedPath, mode='a', newline='') as file:
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
            bounding_box_path = folderName + 'croppedImage/' + filename_png[:-4] + '_boxes'

            logging.info(f"bounding box path is : {bounding_box_path}")
            # bounding_box_path = f'{folderName}/croppedImage/{filename_png[:-4]}_boxes'

            with open(textDetectedPath, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Filename', 'Extracted Text'])

            for filename_box in os.listdir(bounding_box_path):

                if filename_box.endswith('.png'):

                    image_box_path = bounding_box_path + '/' + filename_box
                    image_box = cv2.imread(
                        f'{bounding_box_path}/{filename_box}')

                    text = pytesseract.image_to_string(image_box, config=confi)

                    with open(textDetectedPath, mode='a', newline='') as file:
                        writer = csv.writer(file)
                        if text.strip():
                            writer.writerow([filename_box, text])

        except:
            logging.info("Couldn't create bounding boxes, tile cannot extend outside image")

        try:
            dates, Codes, Times, from_ad, to_ad = '', '', '', None, None
            whole_page = pd.read_csv(textDetectedPath)
            dates, Codes, Times, from_ad, to_ad, uniqueCode = dateAndCode_extraction(
                whole_page, image, folderName)
            # dateAndCode_CSV = pd.read_csv(f'{folderName}/Date_Code.csv')

            address_from_croppedImageCSV_result = address_from_croppedImageCSV(id_token)

            logging.info(address_from_croppedImageCSV_result)

            addressCSVPath = folderName + 'Address_found.csv'

            date, time, code, fromA, toA, manual = values(
                dates, Times, Codes, from_ad, to_ad, uniqueCode, addressCSVPath)

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
                processedPath = "manual_" + filename_png + ".pdf"
                # processedPath = f"manual_{filename_png}.pdf"

                img = Image.open(filename_png_path)
                pdf_filename = manualFolder + "manual_" + filename_png[:-4] + ".pdf"
                Blobfilename = filename_png[:-4] + ".pdf"

                # pdf_filename = f'{folderName}/manual/manual_{filename_png[:-4]}.pdf'
                # Blobfilename = f'{filename_png[:-4]}.pdf'

                img.save(pdf_filename, 'PDF', resolution=100.0)
                logging.info("Manual Version generated")

                log = await UploadManualToBlob(pdf_filename, Blobfilename)
                logging.info(f"from init py log = {log}")
                response = await UploadManualToMiwayne(id,code, fromA,toA,deliveryDate,id_token)
                logging.info(f"miwayne upload from init py = {response}")

                logging.info("Manual Version uploaded successfully from init")

            else:
                # generate_pdf(date, time, code, fromA,
                #              toA, manual, filename_png)
                
                logging.info("All Data stripped successfully")

                processedPath = code + ".pdf"
                img = Image.open(filename_png_path)
                pdf_filename = processedFolder + processedPath
                Blobfilename = processedPath

                img.save(pdf_filename, 'PDF', resolution=100.0)

                log = await UploadProcessedToBlob(pdf_filename, Blobfilename)
                logging.info(f"from init py log = {log}")
                response = await UploadProcessedToMiwayne(id,code, fromA,toA,deliveryDate,id_token)
                logging.info(f"miwayne upload from init py = {response}")
                logging.info(f"{code} Processed Version uploaded successfully from init")

        except:
            logging.info("Error in generating Customer Version PDF.")

            img = Image.open(f'{folderName}/image/{filename_png}')
            pdf_filename = f'{folderName}/manual/manual_{filename_png[:-4]}.pdf'
            Blobfilename = f'{filename_png[:-4]}.pdf'

            img.save(pdf_filename, 'PDF', resolution=100.0)
            logging.info("Manual Version generated from except block")

            log = await UploadManualToBlob(pdf_filename, Blobfilename)
            logging.info(f"from init py log = {log}")
            response = await UploadManualToMiwayne(id,code, fromA,toA,deliveryDate,id_token)
            logging.info(f"miwayne upload from init py = {response}")
            logging.info("Manual Version uploaded successfully from except block in init")

        logging.info(f"finised working on {filename_png}")

    logging.info(f"completed working on function {fileName}")