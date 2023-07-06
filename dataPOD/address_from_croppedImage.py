import csv
import pandas as pd
from .address_extraction import address_extraction
import requests
import logging
import json


def address_from_croppedImageCSV():
    authUrl = "https://dev-rtgqet4r.au.auth0.com/oauth/token"
    cityUrl = "https://stage.test-wayne.com/api/Postcodes/City"

    authPayload = {"grant_type": "password",
                   "username": "SABBIR.SRISTY@BISHUDIGITAL.COM",
                   "password": "Iamtheone@36",
                   "audience": "https://stage.test-wayne.com/api/",
                   "client_id": "gyNB4hFUbB3skeBssVeSdnNUofTo1wS0",
                   "client_secret": "PxJ59wcHwdaOkGqMAhj_PX9r4PgdTuJs-cTIpYcfxQhSRe2eeOswxryJ4XSl37sJ",
                   "scope": "openid profile email"}
    authHeaders = {'content-type': "application/x-www-form-urlencoded"}

    authResponse = requests.post(
        authUrl, data=authPayload, headers=authHeaders)

    logging.info(f"response is {authResponse}")

    if authResponse.status_code == 200:
        logging.info("Authentication successful")
        id_token = authResponse.json()['access_token']
        logging.info("id token: {}".format(id_token))
    else:
        logging.info("Authentication failed")

    logging.info(type(id_token))

    cityHeaders = {
        "Authorization": "Bearer " + id_token
    }

    r = requests.get(cityUrl, headers=cityHeaders, verify=False)

    city_list = json.loads(r.text)
    city_list = [keyword.lower().strip() for keyword in city_list]

    my_cities = ['wiri', 'st johns', 'avonhead', 'waltham', 'harewood', 'albany',
                 'manukau', 'henderson', 'wellington', 'christchurch', 'vanessa', 'rakaia', 'tamaki']
    [city_list.append(city) for city in my_cities if city not in city_list]
    # logging.info(city_list)

    # New CSV for storing extracted addresses
    with open('./tmp/Address_found.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['address_type', 'address'])

    df = pd.read_csv('./tmp/Cropped_Text.csv')

    for i, row in df.iterrows():
        text = row['Extracted Text']
        s, ad = address_extraction(text)

        if ad != None:
            if any(keyword in ad.lower() for keyword in city_list):
                # if ad != None:
                with open('./tmp/Address_found.csv', mode='a', newline='') as file:
                    writer = csv.writer(file)
                    if text.strip():
                        writer.writerow([s, ad])
                # logging.info(s)
                # logging.info(ad)
