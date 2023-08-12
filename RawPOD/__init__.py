import logging
import base64
import azure.functions as func
import os
from pdf2image import convert_from_path
from PIL import Image


from .UploadTo_rawimage import UploadTo_rawimage
from .UploadTo_rawpdf import UploadTo_rawpdf
from .UploadRawToMiwayne import UploadRawToMiwayne
from .DeleteFolderContents import DeleteFolderContents
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

    logging.info("filename: {}".format(fileName))
    logging.info(f"file name without extension : {fileNameNoExt}")

    fileData = myblob.read()
    encoded_string = base64.b64encode(fileData)
    bytes_file = base64.b64decode(encoded_string, validate=True)

    logging.info(f"given file in bytes is : \n"
                 f"{bytes_file}")
    
    folderName = "./" + fileNameNoExt +"/"

    logging.info(f"Folder Name is : {folderName}")

    # if os.path.exists(f'{folderName}/'):
    #     DeleteFolderContents_result = DeleteFolderContents(f'{folderName}/')
    #     logging.info(DeleteFolderContents_result)

    if not os.path.exists(folderName):
        os.makedirs(folderName)

    filePath = folderName + fileName

    logging.info(filePath)

    try:
        with open(filePath, 'wb') as f:
            f.write(bytes_file)

        with open(filePath, 'rb') as f:
            file_contents = f.read()

        # Decode the file contents if necessary (e.g., for text files)
        # decoded_contents = file_contents.decode('utf-8')

        # logging.info(f"File contents: {decoded_contents}")

        # Check if the file was successfully written at filePath
        if os.path.isfile(filePath):
            logging.info(f"File successfully written at {filePath}")
        else:
            logging.error(f"Failed to write the file at {filePath}")

    except Exception as e:
        logging.error(f"Error writing the file: {str(e)}")

    # with open(filePath, 'wb') as f:
    #     f.write(bytes_file)

    # Check if the file was successfully written at filePath
    # if os.path.isfile(filePath):
    #     logging.info(f"File successfully written at {filePath}")
    # else:
    #     logging.error(f"Failed to write the file at {filePath}")

    imageFolder = folderName + "image" + "/"

    if not os.path.exists(imageFolder):
        os.makedirs(imageFolder)
        logging.info(f"image folder created : {imageFolder}")

    pdfFolder = folderName + "pdf" + "/"

    if not os.path.exists(pdfFolder):
        os.makedirs(pdfFolder)
        logging.info(f"pdf folder created : {pdfFolder}")

    manualFolder = folderName + "manual" + "/"

    if not os.path.exists(manualFolder):
        os.makedirs(manualFolder)
        logging.info(f"manual folder created : {manualFolder}")

    pdfPath = folderName + 'pdf/'

    if not fileName.endswith('.pdf'):
        logging.info("file doesn't end with .pdf")
        image = Image.open(filePath)
        filePath = folderName + fileNameNoExt + '.pdf'
        image.save(filePath, 'PDF')

    id_token = GetAuth0Token()

    if fileName.endswith('.pdf'):
        for attempt in range(5):
            logging.info(f"Starting Attempt: {attempt+1}")
            try:
                images = convert_from_path(filePath)

                if images:
                    # loop through each image and save it as a PNG file
                    for i, image in enumerate(images):
                        try:
                            imageNumber = i+1
                            logging.info(f"{imageNumber} started")

                            imageSavePath = imageFolder + fileNameNoExt + "_page_" + imageNumber + '.png'

                            image.save(imageSavePath, 'PNG')

                            image = Image.open(imageSavePath)
                            
                            pdfFileName = fileNameNoExt + "_page_" + imageNumber + '.pdf'
                            pdfSavePath = pdfPath + pdfFileName

                            image.save(pdfSavePath, 'PDF')

                            size_in_bytes = os.path.getsize(pdfSavePath)
                            size_in_kb_float = size_in_bytes / 1024
                            size_in_kb = int(size_in_kb_float)

                            logging.info(f"size_in_kb {size_in_kb} kb")

                            blobUrl = UploadTo_rawpdf(pdfSavePath, pdfFileName)
                            logging.info(f"blobUrl is : {blobUrl}")
                            response = UploadRawToMiwayne(pdfFileName, blobUrl,size_in_kb, id_token)
                            data = response.json()
                            logging.info(f"response from upload raw to miwayne is : {data}")

                            

                            id_value = data['data']['id']

                            imagePathWithID = imageFolder + fileNameNoExt + "_page_" + imageNumber + "_" + id_value + '.png'
                            imageNameWithID = fileNameNoExt + "_page_" + imageNumber + "_" + id_value + '.png'

                            logging.info(imagePathWithID)

                            image.save(imagePathWithID, 'PNG')


                            log = UploadTo_rawimage(imagePathWithID, imageNameWithID)

                            logging.info(log)
                            logging.info(f"Image number:{i+1} ended")
                            
                        except Exception as e:
                            logging.error(f"Error processing image {i+1}: {str(e)}")
                    
                    break  # Break the loop if images are successfully converted and processed
                else:
                    logging.info(f"No images found in conversion attempt {attempt+1}")
            
            except Exception as e:
                logging.error(f"Error converting images from PDF: {str(e)}")

    logging.info(f"completed working on function {fileName}")

    # if os.path.exists(f'{folderName}/'):
    #     DeleteFolderContents(f'{folderName}/')