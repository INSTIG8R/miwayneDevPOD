import requests
import logging
import json

def UploadRawToMiwayne(fileName,fileUrl):

    ####################### List of API Endpoint #######################
    authUrl = "https://dev-rtgqet4r.au.auth0.com/oauth/token"
    # categoryUrl = "https://dev.test-wayne.com/api/DocumentCategories"
    rawPODUrl = "https://stage.test-wayne.com/api/pod/raw"
    configUrl = "https://stage.test-wayne.com/api/UIConfigurations/data/"
    
    ####################### Auth0 Token #######################
    
    authPayload={"grant_type": "password",
            "username": "SABBIR.SRISTY@BISHUDIGITAL.COM",
            "password": "Iamtheone@36",
            "audience": "https://stage.test-wayne.com/api/",
            "client_id": "gyNB4hFUbB3skeBssVeSdnNUofTo1wS0",
            "client_secret": "PxJ59wcHwdaOkGqMAhj_PX9r4PgdTuJs-cTIpYcfxQhSRe2eeOswxryJ4XSl37sJ",
            "scope": "openid profile email"}
    authHeaders = { 'content-type': "application/x-www-form-urlencoded" }

    authResponse = requests.post(authUrl, data=authPayload,headers=authHeaders)

    print("response is ",authResponse)

    if authResponse.status_code == 200:
        logging.info("Authentication successful")
        id_token = authResponse.json()['access_token']
        logging.info("id token: {}".format(id_token))
    else:
        logging.info("Authentication failed")

    logging.info(type(id_token))


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

    print("\n\nconfig response: {}".format(podConfigListResponse.json()))

    podConfigListResponse = json.loads(podConfigListResponse.text)
    podID = podConfigListResponse[0]['id']

    print("\n\npodID :" + podID )

    try:
        rawPodConfigListResponse = requests.get(rawPodConfigList, headers=categoryHeaders, verify=False) #will return an array 
    except requests.exceptions.HTTPError as e:
        logging.info(e)

    print("\n\nconfig response: {}".format(rawPodConfigListResponse.json()))

    rawPodConfigListResponse = json.loads(rawPodConfigListResponse.text)
    rawPodConfigID = rawPodConfigListResponse[0]['id']

    print("\n\nrawPodConfigID :" + rawPodConfigID )   

    payload={
        "fileName": fileName,
        "documentType": "pdf",
        "categoryId": podID,
        "subCategoryId": rawPodConfigID,
        "fileUrl": fileUrl,
        "docSize": 60739206
        }

    headers = {
        'Authorization' : 'Bearer ' + id_token,
        'Content-Type': 'application/json'
    }


    # with open(file_path, 'rb') as f:
    response = requests.post(rawPODUrl, headers=headers, json=payload, verify=False)
    print(response)
    print("uploaded successfully from function")

    return response