# To enable ssh & remote debugging on app service change the base image to the one below
# FROM mcr.microsoft.com/azure-functions/python:4-python3.10-appservice
FROM mcr.microsoft.com/azure-functions/python:4-python3.10

ENV AzureWebJobsScriptRoot=/home/site/wwwroot \
    AzureFunctionsJobHost__Logging__Console__IsEnabled=true


RUN apt-get install 'ffmpeg'\
    'libsm6'\ 
    'libxext6'  -y && \
	apt-get install -y tesseract-ocr && \
    apt-get install -y libtesseract-dev && \
    apt-get install -y libzbar0 && \
    apt-get install -y poppler-utils    

COPY requirements.txt /
RUN pip install --upgrade pip

RUN pip install -r /requirements.txt

COPY . /home/site/wwwroot