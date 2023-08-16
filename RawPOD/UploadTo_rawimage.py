from azure.storage.blob import BlobServiceClient, BlobClient, ContentSettings
import logging
import asyncio
import aiofiles

# storage_account_key = "Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw=="
# storage_account_name = "devstoreaccount1"
# connection_string = "AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;DefaultEndpointsProtocol=http;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;QueueEndpoint=http://127.0.0.1:10001/devstoreaccount1;TableEndpoint=http://127.0.0.1:10002/devstoreaccount1;"
# container_name = "rawimage"

storage_account_key = "X1YcOGXjPoyizvmAXXher38DOlYGsND2a2TxJwZ4+qdAmGBEI5HPV9rbWC4JOXj3qIVvsyIgH3+x+AStB/U8xA=="
storage_account_name = "sakirsapoddev1"
connection_string = "DefaultEndpointsProtocol=https;AccountName=sakirsapoddev1;AccountKey=X1YcOGXjPoyizvmAXXher38DOlYGsND2a2TxJwZ4+qdAmGBEI5HPV9rbWC4JOXj3qIVvsyIgH3+x+AStB/U8xA==;BlobEndpoint=https://sakirsapoddev1.blob.core.windows.net/;QueueEndpoint=https://sakirsapoddev1.queue.core.windows.net/;TableEndpoint=https://sakirsapoddev1.table.core.windows.net/;FileEndpoint=https://sakirsapoddev1.file.core.windows.net/;"
container_name = "rawimage"

def UploadTo_rawimage(file_path,file_name):
    # blob_service_client = BlobServiceClient.from_connection_string(conn_str=connection_string)
    content_settings = ContentSettings(content_type="image/png")
    blob = BlobClient.from_connection_string(conn_str=connection_string, container_name=container_name, blob_name=file_name)
    # blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_name)
    with open(file_path,"rb") as data:
        blob.upload_blob(data,overwrite=True,content_settings=content_settings)
        # blob.upload_blob(data,overwrite=True)
        logging.info(f"Uploaded {file_name}.")
        log = "completed function upload to rawimage"

    logging.info(log)

    return log