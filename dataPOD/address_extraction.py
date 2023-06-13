import pandas as pd
import re
from datetime import datetime


def address_extraction(text):
    lines = text.splitlines()

    from_address = None
    to_address = None
    a = False
    b = False

    for i, line in enumerate(lines):
        if not a and any(keyword in line.lower() for keyword in ["consignor", "shipper (from)", "from", "shipper", "| sue p er"]):
            from_address = "\n".join(lines[i+1:i+10])
            a = True

        if not b and "receiver" in line.lower():
            to_address = ""
            for j in range(i+1, len(lines)):
                to_address += lines[j] + "\n"
            b = True

        if not a and "sender" in line.lower():
            from_address = ""
            for j in range(i+1, len(lines)):
                if "orig" in lines[j].lower():
                    break
                from_address += lines[j] + "\n"
            a = True

        if not a and any(keyword in line.lower() for keyword in ["origin"]):
            from_address = "\n".join(lines[i:i+1])
            a = True

        if not b and any(keyword in line.lower() for keyword in ["receiver", "consignee", "consignee (to)", "to"]):
            to_address = "\n".join(lines[i+1:])
            b = True

        if not b and any(keyword in line.lower() for keyword in ["destination"]):
            to_address = "\n".join(lines[i:i+1])
            b = True

        if a and b:
            break

    if from_address:
        return ("from", from_address)

    elif to_address:
        return ("to", to_address)

    else:
        return ("", None)
