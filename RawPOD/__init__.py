import logging
import base64
import azure.functions as func
import os
from pdf2image import convert_from_path
from PIL import Image

from .UploadTo_rawimage import UploadTo_rawimage
from .UploadTo_rawpdf import UploadTo_rawpdf

def main(myblob: func.InputStream):
    logging.info(f"Python blob trigger function processed blob \n"
                 f"Name: {myblob.name}\n"
                 f"Blob Size: {myblob.length} bytes")
    
    nameWithPath = myblob.name
    fileName = nameWithPath.split("/")[-1]
    fileNameNoExt = fileName.split(".")[:-1]

    # logging.info("file name: {}".format(fileName))
    print("filename : "+fileName)

    fileData = myblob.read()
    encoded_string = base64.b64encode(fileData)
    bytes_file = base64.b64decode(encoded_string, validate=True)

    if not os.path.exists('./tmp'):
        os.makedirs('./tmp')

    filePath = './tmp/' + fileName

    with open(filePath, 'wb') as f:
        f.write(bytes_file)

    if not os.path.exists('./tmp/image'):
        os.makedirs('./tmp/image')

    if not os.path.exists('./tmp/pdf'):
        os.makedirs('./tmp/pdf')

    if not os.path.exists('./tmp/manual'):
        os.makedirs('./tmp/manual')

    imagePath = './tmp/image/'
    pdfPath = './tmp/pdf/'

    if not fileName.endswith('.pdf'):
        image = Image.open(fileName)
        pdf_path = './tmp/' + fileNameNoExt + '.pdf'
        image.save(pdf_path, 'PDF')

    if fileName.endswith('.pdf'):

        images = convert_from_path(filePath)

        # loop through each image and save it as a PNG file
        for i, image in enumerate(images):
            image.save(f'./tmp/image/{fileNameNoExt[0]}_page_{i+1}.png', 'PNG')
            UploadTo_rawimage(f'{imagePath}{fileNameNoExt[0]}_page_{i+1}.png', f'{fileNameNoExt[0]}_page_{i+1}.png')


            image = Image.open(f'./tmp/image/{fileNameNoExt[0]}_page_{i+1}.png')
            pdf_path = f'./tmp/pdf/{fileNameNoExt[0]}_page_{i+1}.pdf'
            image.save(pdf_path, 'PDF')
            UploadTo_rawpdf(f'{pdfPath}{fileNameNoExt[0]}_page_{i+1}.pdf', f'{fileNameNoExt[0]}_page_{i+1}.pdf')
            
