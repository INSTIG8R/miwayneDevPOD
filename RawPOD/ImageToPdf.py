import os
import img2pdf

def ImageToPdf(folder_name, file_name):

  images = [os.path.join(folder_name, file) for file in os.listdir(folder_name) if file.endswith(".png") or file.endswith(".jpg") or file.endswith(".jpeg")]

  with open(file_name, "wb") as f:
    f.write(img2pdf.convert(images))