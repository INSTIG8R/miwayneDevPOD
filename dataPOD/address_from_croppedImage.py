import csv
import pandas as pd
from .address_extraction import address_extraction
import requests
import logging
import json


def address_from_croppedImageCSV(id_token):
    authUrl = "https://dev-rtgqet4r.au.auth0.com/oauth/token"
    cityUrl = "https://dev.test-wayne.com/api/Postcodes/City"

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

    log = "finised function address_from_croppedImageCSV"

    return log