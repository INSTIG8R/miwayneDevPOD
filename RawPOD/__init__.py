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

def main(myblob: func.InputStream):
    logging.info(f"Python blob trigger function processed blob \n"
                 f"Name: {myblob.name}\n"
                 f"Blob Size: {myblob.length} bytes")
    
    nameWithPath = myblob.name
    fileName = nameWithPath.split("/")[-1]
    fileNameNoExt = fileName.split(".")[:-1]

    logging.info("filename: {}".format(fileName))

    fileData = myblob.read()
    encoded_string = base64.b64encode(fileData)
    bytes_file = base64.b64decode(encoded_string, validate=True)

    logging.info(bytes_file)

    if os.path.exists('./tmp'):
        DeleteFolderContents('./tmp')

    if not os.path.exists('./tmp'):
        os.makedirs('./tmp')

    filePath = './tmp/' + fileName

    logging.info(filePath)

    try:
        with open(filePath, 'wb') as f:
            f.write(bytes_file)

        with open(filePath, 'rb') as f:
            file_contents = f.read()

        # Decode the file contents if necessary (e.g., for text files)
        decoded_contents = file_contents.decode('utf-8')

        logging.info(f"File contents: {decoded_contents}")

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

    if not os.path.exists('./tmp/image'):
        os.makedirs('./tmp/image')

    if not os.path.exists('./tmp/pdf'):
        os.makedirs('./tmp/pdf')

    if not os.path.exists('./tmp/manual'):
        os.makedirs('./tmp/manual')

    pdfPath = './tmp/pdf/'

    if not fileName.endswith('.pdf'):
        image = Image.open(filePath)
        pdf_path = './tmp/' + fileNameNoExt[0] + '.pdf'
        image.save(pdf_path, 'PDF')

    if fileName.endswith('.pdf'):
        for attempt in range(5):
            logging.info(f"Starting Attempt: {attempt+1}")
            try:
                images = convert_from_path(filePath)

                if images:
                    # loop through each image and save it as a PNG file
                    for i, image in enumerate(images):
                        try:
                            logging.info(f"Image number:{i+1} started")
                            image.save(f'./tmp/image/{fileNameNoExt[0]}_page_{i+1}.png', 'PNG')

                            image = Image.open(f'./tmp/image/{fileNameNoExt[0]}_page_{i+1}.png')
                            pdf_path = f'./tmp/pdf/{fileNameNoExt[0]}_page_{i+1}.pdf'
                            image.save(pdf_path, 'PDF')
                            size_in_bytes = os.path.getsize(pdf_path)
                            size_in_kb = size_in_bytes / 1024
                            logging.info(f"size_in_kb {size_in_kb} kb")
                            blobUrl = UploadTo_rawpdf(f'{pdfPath}{fileNameNoExt[0]}_page_{i+1}.pdf', f'{fileNameNoExt[0]}_page_{i+1}.pdf')
                            logging.info(blobUrl)
                            response = UploadRawToMiwayne(f'{fileNameNoExt[0]}_page_{i+1}.pdf', blobUrl)

                            logging.info(response.json())

                            data = response.json()

                            id_value = data['data']['id']

                            filename_withpath = f"./tmp/image/{fileNameNoExt[0]}_page_{i+1}_{id_value}.png"

                            logging.info(filename_withpath)

                            image.save(filename_withpath, 'PNG')
                            UploadTo_rawimage(filename_withpath, f'{fileNameNoExt[0]}_page_{i+1}_{id_value}.png')
                            logging.info(f"Image number:{i+1} ended")
                            
                        except Exception as e:
                            logging.error(f"Error processing image {i+1}: {str(e)}")
                    
                    break  # Break the loop if images are successfully converted and processed
                else:
                    logging.info(f"No images found in conversion attempt {attempt+1}")
            
            except Exception as e:
                logging.error(f"Error converting images from PDF: {str(e)}")

    if os.path.exists('./tmp'):
        DeleteFolderContents('./tmp')