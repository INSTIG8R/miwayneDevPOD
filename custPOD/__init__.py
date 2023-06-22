import logging
import json
import azure.functions as func
import os
import datetime

from .generate_pdf import generate_pdf
from .DeleteFolderContents import DeleteFolderContents
from .download_image import download_image
from .UploadCustToBlob import UploadCustToBlob

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        req_body = req.get_json()
        response = json.dumps(req_body)

        print(response)

        req_bodyText = json.loads(response)

        date_string  =  req_bodyText['deliveryDate']
        code  =  req_bodyText['consignmentNote']
        fromA =  req_bodyText['senderAddress']
        toA   =  req_bodyText['receiverAddress']
        image_path = req_bodyText['image_path']

        datetime_obj = datetime.datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%fZ")

        # Extract the date and time components
        date = datetime_obj.date()
        time = datetime_obj.time()

        date_str = date.strftime("%Y-%m-%d")
        time_str = time.strftime("%H:%M:%S")

        print("Date:", date)
        print("Time:", time_str)
        
        if os.path.exists('./tmp'):
            DeleteFolderContents('./tmp')

        if not os.path.exists('./tmp/logo'):
            os.makedirs('./tmp/logo')

        if not os.path.exists('./tmp/screenshot'):
            os.makedirs('./tmp/screenshot')
        
        logo_url = 'https://sakirsapoddev2a280f8.blob.core.windows.net/logo/logo.jpg'
        logo_path = './tmp/logo/logo.jpg'
        download_image(logo_url, logo_path)

        screenshot_url = image_path
        screenshot_filename = os.path.basename(screenshot_url)
        screenshot_path = f"./tmp/{screenshot_filename}"

        download_image(screenshot_url, screenshot_path)

        custPOD_path = f"./tmp/customer_{code}.pdf"
        custPOD_filename = f"customer_{code}.pdf"
        generate_pdf(date_str,time_str,code,fromA,toA,logo_path,screenshot_path,custPOD_path)

        blobUrl = UploadCustToBlob(custPOD_path,custPOD_filename)



        url = {
            "url" : image_path,
            "date"  :  date_str,
            "time"  :  time_str,
            "consignmentNote"  :  code,
            "senderAddress" :  fromA,
            "receiverAddress"   :  toA,
            "image_path" : image_path
        }
        


        return func.HttpResponse(body=json.dumps(url), mimetype='application/json')
    except ValueError:
        return func.HttpResponse(
            "Invalid JSON payload provided.",
            status_code=400
        )