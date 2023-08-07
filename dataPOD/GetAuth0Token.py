import logging
import requests
from azure.storage.blob import BlobClient

####################### List of API Endpoint #######################

def GetAuth0Token():    
    # Connection string for your Azure Storage account
    connection_string = "DefaultEndpointsProtocol=https;AccountName=sakirsapodstage1;AccountKey=ONVKkSm6zRmOfNr1810y824wRaud90qJ60LsG0rAXj8h+r5I6d9U6fVZs0mTEV3zHN6qIYhMajkR+AStDOoStw==;BlobEndpoint=https://sakirsapodstage1.blob.core.windows.net/;QueueEndpoint=https://sakirsapodstage1.queue.core.windows.net/;TableEndpoint=https://sakirsapodstage1.table.core.windows.net/;FileEndpoint=https://sakirsapodstage1.file.core.windows.net/;"

    # Name of the container and file to download
    container_name = "token"
    file_name = "token_file.txt"

    # Create the BlobClient object
    blob_client = BlobClient.from_connection_string(conn_str=connection_string, container_name=container_name, blob_name=file_name)

    # Download the file as a blob
    downloaded_blob = blob_client.download_blob()

    # Read the contents of the file
    id_token = downloaded_blob.readall().decode('utf-8')

    # Print the contents of the file
    logging.info(f"token is : {id_token}")

    return id_token