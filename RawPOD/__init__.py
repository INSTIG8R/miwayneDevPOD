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

    logging.info("filename: {}".format(fileName))

    fileData = myblob.read()
    encoded_string = base64.b64encode(fileData)
    bytes_file = base64.b64decode(encoded_string, validate=True)

    logging.info(f"given file in bytes is : \n"
                 f"{bytes_file}")
    
    folderName = f"./{fileNameNoExt}"

    logging.info(f"Folder Name is : {folderName}")

    # if os.path.exists(f'{folderName}/'):
    #     DeleteFolderContents_result = DeleteFolderContents(f'{folderName}/')
    #     logging.info(DeleteFolderContents_result)

    if not os.path.exists(f'{folderName}/'):
        os.makedirs(f'{folderName}/')

    filePath = f'{folderName}/' + fileName

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

    if not os.path.exists(f'{folderName}/image'):
        os.makedirs(f'{folderName}/image')
        logging.info("image folder created")


    if not os.path.exists(f'{folderName}/pdf'):
        os.makedirs(f'{folderName}/pdf')
        logging.info("pdf folder created")

    if not os.path.exists(f'{folderName}/manual'):
        os.makedirs(f'{folderName}/manual')
        logging.info("manual folder created")

    pdfPath = f'{folderName}/pdf/'

    if not fileName.endswith('.pdf'):
        logging.info("file doesn't end with .pdf")
        image = Image.open(filePath)
        filePath = f'{folderName}/' + fileNameNoExt[0] + '.pdf'
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
                            logging.info(f"Image number:{i+1} started")
                            image.save(f'{folderName}/image/{fileNameNoExt[0]}_page_{i+1}.png', 'PNG')

                            image = Image.open(f'{folderName}/image/{fileNameNoExt[0]}_page_{i+1}.png')
                            pdf_path = f'{folderName}/pdf/{fileNameNoExt[0]}_page_{i+1}.pdf'
                            image.save(pdf_path, 'PDF')
                            size_in_bytes = os.path.getsize(pdf_path)
                            size_in_kb_float = size_in_bytes / 1024
                            size_in_kb = int(size_in_kb_float)
                            logging.info(f"size_in_kb {size_in_kb} kb")
                            blobUrl = UploadTo_rawpdf(f'{pdfPath}{fileNameNoExt[0]}_page_{i+1}.pdf', f'{fileNameNoExt[0]}_page_{i+1}.pdf')
                            logging.info(f"blobUrl is : {blobUrl}")
                            response = UploadRawToMiwayne(f'{fileNameNoExt[0]}_page_{i+1}.pdf', blobUrl,size_in_kb, id_token)
                            data = response.json()
                            logging.info(f"response from upload raw to miwayne is : {data}")

                            

                            id_value = data['data']['id']

                            filename_withpath = f'{folderName}/image/{fileNameNoExt[0]}_page_{i+1}_{id_value}.png'

                            logging.info(filename_withpath)

                            image.save(filename_withpath, 'PNG')


                            log = UploadTo_rawimage(filename_withpath, f'{fileNameNoExt[0]}_page_{i+1}_{id_value}.png')

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