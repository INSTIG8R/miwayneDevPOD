import cv2
import json


def create_JSON(filename, date, time, code, fromA, toA, manual):

    # Create a dictionary to store the text
    key_value = {'Filename': filename[:-4], 'Date': date, 'Time': time, 'CONNOTE': code,
                 'Sender Address': fromA, 'Receiver Address': toA, 'Manual Version Created': manual}

    # Save the dictionary as a JSON file
    with open('Output.json', 'a') as f:
        json.dump(key_value, f)
