import aiohttp
import logging
import json

async def UploadRawToMiwayne(fileName, fileUrl, size_in_kb, id_token):

    rawPODUrl = "https://dev.test-wayne.com/api/pod/raw"
    configUrl = "https://dev.test-wayne.com/api/UIConfigurations/data/"

    ####################### Obtaining Miwayne Document Type POD Config Data #######################

    configModule = {
        "POD_DOCUMENT_CATEGORY": "POD DOCUMENT CATEGORY",
        "POD_PROCESSED_CONFIGURATION": "POD PROCESS CONFIGURATION",
        "POD_RAW_CONFIGURATION": "POD RAW CONFIGURATION",
        "POD_MANUAL_CONFIGURATION": "POD MANUAL CONFIGURATION",
        "POD_CUSTOMER_VERSION_CONFIGURATION": "POD CUSTOMER VERSION CONFIGURATION"
    }

    configType = {
        "DOCUMENT_CATEGORY": "DOCUMENT CATEGORY"
    }

    podConfigList = configUrl + configModule["POD_DOCUMENT_CATEGORY"] + "/" + configType['DOCUMENT_CATEGORY']
    rawPodConfigList = configUrl + configModule["POD_RAW_CONFIGURATION"] + "/" + configType['DOCUMENT_CATEGORY']

    categoryHeaders = {
        "Authorization": "Bearer " + id_token
    }

    logging.info("categoryHeaders: {}".format(categoryHeaders))

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(podConfigList, headers=categoryHeaders) as response:
                podConfigListResponse = await response.text()
        except aiohttp.ClientError as e:
            logging.info(e)

    logging.info("\n\nconfig response: {}".format(podConfigListResponse))

    podConfigListResponse = json.loads(podConfigListResponse)
    podID = podConfigListResponse[0]['id']

    logging.info("\n\npodID :" + podID)

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(rawPodConfigList, headers=categoryHeaders) as response:
                rawPodConfigListResponse = await response.text()
        except aiohttp.ClientError as e:
            logging.info(e)

    logging.info("\n\nconfig response: {}".format(rawPodConfigListResponse))

    rawPodConfigListResponse = json.loads(rawPodConfigListResponse)
    rawPodConfigID = rawPodConfigListResponse[0]['id']

    logging.info("\n\nrawPodConfigID :" + rawPodConfigID)

    payload = {
        "fileName": fileName,
        "documentType": "pdf",
        "categoryId": podID,
        "subCategoryId": rawPodConfigID,
        "fileUrl": fileUrl,
        "docSize": size_in_kb
    }

    headers = {
        'Authorization': 'Bearer ' + id_token,
        'Content-Type': 'application/json'
    }

    logging.info(f"fileName: {fileName}\n"
                 f"categoryId: {podID} \n"
                 f"subCategoryId: {rawPodConfigID} \n"
                 f"fileUrl: {fileUrl} \n"
                 f"docSize: {size_in_kb}")

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(rawPODUrl, headers=headers, json=payload) as response:
                result = await response.text()
                logging.info(result)
        except aiohttp.ClientError as e:
            logging.info(e)

    logging.info("uploaded successfully from function")