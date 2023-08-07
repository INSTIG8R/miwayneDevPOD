import requests
import logging
import json

async def UploadRawToMiwayne(fileName,fileUrl,size_in_kb, id_token):

    rawPODUrl = "https://dev.test-wayne.com/api/pod/raw"
    configUrl = "https://dev.test-wayne.com/api/UIConfigurations/data/"


    ####################### Obtaining Miwayne Document Type POD Config Data #######################

    configModule = {
        "POD_DOCUMENT_CATEGORY" : "POD DOCUMENT CATEGORY",
        "POD_PROCESSED_CONFIGURATION" : "POD PROCESS CONFIGURATION",
        "POD_RAW_CONFIGURATION" : "POD RAW CONFIGURATION",
        "POD_MANUAL_CONFIGURATION" : "POD MANUAL CONFIGURATION",
        "POD_CUSTOMER_VERSION_CONFIGURATION" : "POD CUSTOMER VERSION CONFIGURATION"
    }

    configType = {
        "DOCUMENT_CATEGORY" : "DOCUMENT CATEGORY"
    }

    podConfigList = configUrl+configModule["POD_DOCUMENT_CATEGORY"]+"/"+configType['DOCUMENT_CATEGORY']
    rawPodConfigList =configUrl+configModule["POD_RAW_CONFIGURATION"]+"/"+configType['DOCUMENT_CATEGORY']
    
    categoryHeaders = {
        "Authorization": "Bearer " + id_token
    }

    logging.info("categoryHeaders: {}".format(categoryHeaders))

    try:
        podConfigListResponse = requests.get(podConfigList, headers=categoryHeaders, verify=False) #will return an array 
    except requests.exceptions.HTTPError as e:
        logging.info(e)

    logging.info("\n\nconfig response: {}".format(podConfigListResponse.json()))

    podConfigListResponse = json.loads(podConfigListResponse.text)
    podID = podConfigListResponse[0]['id']

    logging.info("\n\npodID :" + podID )

    try:
        rawPodConfigListResponse = requests.get(rawPodConfigList, headers=categoryHeaders, verify=False) #will return an array 
    except requests.exceptions.HTTPError as e:
        logging.info(e)

    logging.info("\n\nconfig response: {}".format(rawPodConfigListResponse.json()))

    rawPodConfigListResponse = json.loads(rawPodConfigListResponse.text)
    rawPodConfigID = rawPodConfigListResponse[0]['id']

    logging.info("\n\nrawPodConfigID :" + rawPodConfigID )   

    payload={
        "fileName": fileName,
        "documentType": "pdf",
        "categoryId": podID,
        "subCategoryId": rawPodConfigID,
        "fileUrl": fileUrl,
        "docSize": size_in_kb
        }

    headers = {
        'Authorization' : 'Bearer ' + id_token,
        'Content-Type': 'application/json'
    }

    logging.info(f"fileName: {fileName}\n"
        f"categoryId: {podID} \n"
        f"subCategoryId: {rawPodConfigID} \n"
        f"fileUrl: {fileUrl} \n"
        f"docSize: {size_in_kb}")

    # with open(file_path, 'rb') as f:
    response = await requests.post(rawPODUrl, headers=headers, json=payload, verify=False)
    logging.info(response)
    logging.info(response.json())
    
    logging.info("uploaded successfully from function")

    return response