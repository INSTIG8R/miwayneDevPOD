import pandas as pd
import re


def values(dates, Times, Codes, from_ad, to_ad, uniqueCode, df):
    # info = pd.read_csv('Date_Code.csv')
    df = pd.read_csv(df)
    manual = False

    # DATE
    try:
        date = dates[-1]
    except (IndexError, TypeError):
        date = ' '
        manual = True
        print("Date Not Found")

    # CONNOTE
    try:
        if not Codes:
            code = uniqueCode
        else:
            code = Codes[0]
            if code[0] == '—' or code[0] == '£' or code[0] == '€':
                code = 'E' + code[1:]
            elif code[0] == '1' or code[0] == '(':
                code = 'I' + code[1:]
            elif code[:3] == 'Ecc':
                code = 'ECC' + code[3:]
    except (IndexError, TypeError):
        code = ' '
        manual = True
        print("Ref Code Not Found")

    # TIME
    try:
        time = Times[-1]
    except (IndexError, TypeError):
        time = ' '

    # SENDER ADDRESS
    # df = pd.read_csv('Address_found.csv')
    try:
        max_len_from = 0
        fromA = ''

        if from_ad is not None:
            fromA = from_ad.strip()
        else:
            for index, row in df.loc[df['address_type'] == 'from'].iterrows():
                address = row['address'].strip()
                if not address:
                    continue
                lines = [line for line in address.splitlines() if line.strip()]
                if not lines:
                    continue
                if any(s in lines[-1] for s in ["Email", "Emall", "Cmail", "Ermail", "Ermall", "@"]):
                    lines.pop()
                # match email pattern using regular expressions
                if lines and re.match(r"[^@]+@[^@]+\.[^@]+", lines[-1].strip()):
                    lines.pop()
                address = '\n'.join(lines)
                if len(address) > max_len_from:
                    max_len_from = len(address)
                    fromA = address

            if fromA == '':
                manual = True
                print("Sender Address Not Found")
    except (IndexError, TypeError):
        fromA = ' '
        manual = True
        print("Sender Address Not Found")

    # RECEIVER ADDRESS
    try:
        max_len_to = 0
        toA = ''

        if to_ad is not None:
            toA = to_ad.strip()
        else:
            for index, row in df.loc[df['address_type'] == 'to'].iterrows():
                address = row['address'].strip()
                if not address:
                    continue
                lines = [line for line in address.splitlines() if line.strip()]
                if not lines:
                    continue
                if any(s in lines[-1] for s in ["Email", "Emall", "Cmail", "Ermail", "Ermall", "@"]):
                    lines.pop()
                # match email pattern using regular expressions
                if lines and re.match(r"[^@]+@[^@]+\.[^@]+", lines[-1].strip()):
                    lines.pop()
                address = '\n'.join(lines)
                if len(address) > max_len_to:
                    max_len_to = len(address)
                    toA = address

            if toA == '':
                manual = True
                print("Receiver Address Not Found")

    except (IndexError, TypeError):
        toA = ' '
        manual = True
        print("Receiver Address Not Found")

    return date, time, code, fromA, toA, manual