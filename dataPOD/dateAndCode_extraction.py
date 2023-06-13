import pandas as pd
import re
from datetime import datetime
import csv
from .unique_address import *
# from .segment_OCR_model import OCR_model


def dateAndCode_extraction(df, image):
    # read the CSV file into a pandas DataFrame
    # df = pd.read_csv('TextDetected.csv')

    # define the regex pattern to match dates in the format YYYY-MM-DD
    date_pattern = r'\d{2}/\d{2}/\d{4}|\d{1}/\d{2}/\d{4}|\d{2}-\d{2}-\d{4}|\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{2}'
    code_pattern = r'ECC[A-Z0-9]{7}|ECW[A-Z0-9]{7}|IFL[0-9]{7}|1FL[0-9]{7}|ILF[0-9]{7}|£CC[A-Z0-9]{7}|—CC[A-Z0-9]{7}|€CC[A-Z0-9]{7}|Ecc[A-Z0-9]{7}|Ecco[A-Z0-9]{7}|\(FL[0-9]{7}'
    time_pattern = r'[0-9]{2}:[0-9]{2} a.m|[0-9]{2}:[0-9]{2} p.m|[0-9]{1}:[0-9]{2} a.m|[0-9]{1}:[0-9]{2} p.m|[0-9]{2}:[0-9]{2}'

    sealink_pattern = r'\bSEALINK\b'
    sub60_pattern = r'\bSUB60\b'
    bascik_pattern = r'\bBASCIK\b|\bBASCI\b'
    uniqueCode = ''

    with open('./tmp/Date_Code.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write header row to the CSV file
        writer.writerow(['Filename', 'Extracted Date', 'Time',
                        'Extracted Code', 'From Address', 'To Address', 'uniqueCode'])

    # iterate over each row in the DataFrame and extract any dates from the 'text_column'
    for i, row in df.iterrows():
        text = row['Extracted Text']
        dates = re.findall(date_pattern, text)
        codes = re.findall(code_pattern, text)
        times = re.findall(time_pattern, text)
        from_ad, to_ad = None, None  # address_extraction(text)
        filename = row['Filename']

        # check if sealink company
        is_sealink = bool(re.search(sealink_pattern, text))
        if is_sealink:
            print("sealink:", is_sealink)
            from_ad, to_ad = sealink_address(image)

        # check if sub60 company
        is_sub60 = bool(re.search(sub60_pattern, text))
        if is_sub60:
            print("sub60:", is_sub60)
            from_ad, to_ad = sub60(image)

        # check if bascik company
        is_bascik = bool(re.search(bascik_pattern, text))
        if is_bascik:
            print("bascik:", is_bascik)
            from_ad, to_ad, uniqueCode = bascik(image)

        with open('./tmp/Date_Code.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            if text.strip():
                writer.writerow(
                    [filename, dates, times, codes, from_ad, to_ad, uniqueCode])

    return dates, codes, times, from_ad, to_ad, uniqueCode