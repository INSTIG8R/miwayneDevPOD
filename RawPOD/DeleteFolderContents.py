import shutil
import os
import logging

def DeleteFolderContents(folder_path2):
    # Check if the folder exists
    # if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
    #     logging.info("Temp-Folder not found")
    #     return

    # # Delete all the files and subdirectories inside the folder
    # for filename in os.listdir(folder_path):
    #     file_path = os.path.join(folder_path, filename)
    #     if os.path.isfile(file_path):
    #         os.remove(file_path)
    #     elif os.path.isdir(file_path):
    #         shutil.rmtree(file_path)

    if os.path.exists(folder_path2) and os.path.isdir(folder_path2):
        try:
            for item in os.listdir(folder_path2):
                item_path = os.path.join(folder_path2, item)
                if os.path.isfile(item_path):
                    os.remove(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
            os.rmdir(folder_path2)
            logging.info(f"Folder '{folder_path2}' deleted successfully.")
        except OSError as e:
            logging.info(f"Error: {e}")
    else:
        logging.info(f"Folder '{folder_path2}' does not exist or is not a valid directory.")

    logging.info("Temp-Folder contents deleted successfully.")