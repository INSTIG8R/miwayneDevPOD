import shutil
import os
import logging

def DeleteFolderContents(folder_path):
    # Check if the folder exists
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        logging.info("Temp-Folder not found")
        return

    # Delete all the files and subdirectories inside the folder
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)

    logging.info("Temp-Folder contents deleted successfully.")