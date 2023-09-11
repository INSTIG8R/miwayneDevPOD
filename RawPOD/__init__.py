import logging
import base64
import azure.functions as func
import os
import asyncio
import tempfile

from pdf2image import convert_from_path
from PIL import Image

from .UploadTo_rawimage import UploadTo_rawimage
from .UploadTo_rawpdf import UploadTo_rawpdf
from .UploadRawToMiwayne import UploadRawToMiwayne
from .DeleteFolderContents import DeleteFolderContents
from .GetAuth0Token import GetAuth0Token
from .ImageToPdf import ImageToPdf

async def main(myblob: func.InputStream):
    logging.info(f"Python blob trigger function processed blob \n"
                 f"Name: {myblob.name}\n"
                 f"Blob Size: {myblob.length} bytes")

    logging.info("###########################  new function started  ###########################")

    name_with_path = myblob.name
    file_name = name_with_path.split("/")[-1]
    file_name_no_ext = file_name.split(".")[:-1]
    file_name_no_ext = file_name_no_ext[0]

    logging.info("filename: {}".format(file_name))
    logging.info(f"file name without extension : {file_name_no_ext}")

    file_data = myblob.read()
    encoded_string = base64.b64encode(file_data)
    bytes_file = base64.b64decode(encoded_string, validate=True)

    logging.info(f"bytes file prepared")

    with tempfile.TemporaryDirectory() as temp_dir:
        folder_name = os.path.join(temp_dir, file_name_no_ext)

        logging.info(f"Folder Name is : {folder_name}")

        if os.path.exists(folder_name):
            DeleteFolderContents_result = DeleteFolderContents(folder_name)
            logging.info(DeleteFolderContents_result)

        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        file_path = os.path.join(folder_name, file_name)

        logging.info(file_path)

        try:
            with open(file_path, 'wb') as f:
                f.write(bytes_file)

            with open(file_path, 'rb') as f:
                file_contents = f.read()

            # Decode the file contents if necessary (e.g., for text files)
            # decoded_contents = file_contents.decode('utf-8')

            # logging.info(f"File contents: {decoded_contents}")

            # Check if the file was successfully written at file_path
            if os.path.isfile(file_path):
                logging.info(f"File successfully written at {file_path}")
            else:
                logging.error(f"Failed to write the file at {file_path}")

        except Exception as e:
            logging.error(f"Error writing the file: {str(e)}")

        image_folder = os.path.join(folder_name, "image")
        os.makedirs(image_folder, exist_ok=True)
        logging.info(f"image folder created : {image_folder}")

        pdf_folder = os.path.join(folder_name, "pdf")
        os.makedirs(pdf_folder, exist_ok=True)
        logging.info(f"pdf folder created : {pdf_folder}")

        manual_folder = os.path.join(folder_name, "manual")
        os.makedirs(manual_folder, exist_ok=True)
        logging.info(f"manual folder created : {manual_folder}")

        pdf_path = os.path.join(folder_name, 'pdf')

        if not file_name.endswith('.pdf'):
            logging.info("file doesn't end with .pdf")
            converted_pdf_filename = file_name_no_ext + ".pdf"
            file_name = converted_pdf_filename
            file_path = os.path.join(folder_name, file_name)
            logging.info(f"new converted file path is {file_path}")
            ImageToPdf(folder_name,file_path)
            logging.info(f"new converted file name is {file_name}")

            
            # image = Image.open(file_path)
            # file_path = os.path.join(folder_name, file_name_no_ext + '.pdf')
            # image.save(file_path, 'PDF')

        id_token = GetAuth0Token()

        if file_name.endswith('.pdf'):
            for attempt in range(5):
                logging.info(f"Starting Attempt: {attempt+1}")
                try:
                    images = convert_from_path(file_path)

                    if images:
                        # loop through each image and save it as a PNG file
                        for i, image in enumerate(images):
                            try:
                                image_number = i + 1
                                image_number = str(image_number)
                                logging.info(f"{image_number} started")

                                image_save_path = os.path.join(image_folder, file_name_no_ext + "_page_" + image_number + '.png')
                                logging.info(f"image save path : {image_save_path}")

                                image.save(image_save_path, 'PNG')

                                image = Image.open(image_save_path)
                                logging.info("image opened/read")

                                pdf_file_name = file_name_no_ext + "_page_" + image_number + '.pdf'
                                pdf_save_path = os.path.join(pdf_path, pdf_file_name)

                                image.save(pdf_save_path, 'PDF')
                                logging.info(f"pdf saved in : {pdf_save_path}")

                                size_in_bytes = os.path.getsize(pdf_save_path)
                                size_in_kb_float = size_in_bytes / 1024
                                size_in_kb = int(size_in_kb_float)

                                logging.info(f"size_in_kb {size_in_kb} kb")

                                blob_url = UploadTo_rawpdf(pdf_save_path, pdf_file_name)
                                logging.info(f"blobUrl is : {blob_url}")
                                response = await UploadRawToMiwayne(pdf_file_name, blob_url, size_in_kb, id_token)
                                data = response
                                logging.info(f"response from upload raw to miwayne is : {data}")

                                id_value = data['data']['id']

                                image_path_with_id = os.path.join(image_folder, file_name_no_ext + "_page_" + image_number + "_" + id_value + '.png')
                                image_name_with_id = file_name_no_ext + "_page_" + image_number + "_" + id_value + '.png'

                                logging.info(image_path_with_id)

                                image.save(image_path_with_id, 'PNG')

                                log = UploadTo_rawimage(image_path_with_id, image_name_with_id)

                                logging.info(log)
                                logging.info(f"Image number:{i + 1} ended")

                            except Exception as e:
                                logging.error(f"Error processing image {i + 1}: {str(e)}")

                        break  # Break the loop if images are successfully converted and processed
                    else:
                        logging.info(f"No images found in conversion attempt {attempt + 1}")

                except Exception as e:
                    logging.error(f"Error converting images from PDF: {str(e)}")

    logging.info(f"completed working on function {file_name}")

    if os.path.exists(folder_name):
        DeleteFolderContents(folder_name)
