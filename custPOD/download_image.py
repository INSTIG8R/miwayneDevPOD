import requests

def download_image(url, file_path):
    response = requests.get(url)
    response.raise_for_status()  # Check if the request was successful

    with open(file_path, "wb") as file:
        file.write(response.content)