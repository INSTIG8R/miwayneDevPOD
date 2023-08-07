############### NEW FORMAT ################
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from PIL import Image
from io import BytesIO

def generate_pdf(date,time,code,fromA,toA,logo_path,screenshot_path,custPOD_path):
# Create PDF document

  c = canvas.Canvas(custPOD_path, pagesize=letter)
  
  # Load the image
  image = logo_path

  # Get the dimensions of the image
  with open(image, "rb") as f:
      img_width, img_height = canvas.ImageReader(f).getSize()

  #logging.info(letter)

  # Calculate the center position of the page
  center_x = letter[0]/2
  top_y = letter[1] - 0.5*inch

  # Draw the image at the top center of the page
  c.drawImage(image, center_x - 0.5*img_width, top_y - img_height, width=img_width, height=img_height)




  #####################   TABLE-1    #######################

  # Define table dimensions and styling
  table_width, table_height = 6 * inch, 2 * inch
  table_x, table_y = center_x - 0.5 * table_width, top_y - table_height - 0.8 * inch
  row_height = 0.5 * inch
  col_width = table_width / 2
  table_bottom_y = table_y - table_height 

  #logging.info("table_x:",table_x, "\ntable_y:",table_y,"\ntable_height",table_height,"\ntable_bottom_y",table_bottom_y,"\nrow_height:",row_height,"\ncol_width:",col_width)

  # Draw the title
  c.setFont("Helvetica-Bold", 14)
  title_x, title_y =  306.0, 666.0           #table_x + table_width / 2, table_y + table_height + 0.25 * inch
  c.drawCentredString(title_x, title_y, "PROOF OF DELIVERY")
  


  # Add data to table
  datas = [['REF 1', 'REF 2', 'REF 3'], ['JOB CODE', 'SENDERS REF', 'CONTACT NAME', 'CONTACT PHONE']]
  data = [[' ', ' ', ' '], [code, ' ', ' ', ' ']]

  for i in range(len(data)):
      for j in range(len(data[i])):
          cell_x = table_x + j * (table_width / len(data[i]))
          cell_y = table_y + i * row_height
          cell_width = (table_width / len(data[i]))
          cell_height = row_height
          
          # Draw the cell rectangle
          c.rect(cell_x, cell_y, cell_width, cell_height)

          # Calculate the x and y coordinates for the small text
          small_text_x = cell_x + 0.1 * inch
          small_text_y = cell_y + cell_height - 0.1 * inch
          
          # Set the font size for the small text and draw it
          c.setFont("Helvetica", 7)
          c.drawString(small_text_x, small_text_y, datas[i][j])

          # Calculate the x and y coordinates for the text
          text_x = cell_x + cell_width / 2
          text_y = cell_y + cell_height / 3
          
          c.setFont("Helvetica", 10)
          # Draw the cell text
          c.drawCentredString(text_x, text_y, data[i][j])



  #######################  TABLE-2  ######################


  data2 = [[ toA,fromA]]
  data2S = [['TO','FROM']]

  # Define table dimensions and styling

  table_x, table_y =  center_x - 0.5*table_width,  table_bottom_y + 0.25 * inch   #top_y - table_height-table_height-(table_height/2) - 0.5 * inch
  row_height = 1.25 * inch
  col_width = table_width / 2
  text_x, text_y = table_x + col_width / 2, table_y + row_height / 2
  table_bottom_y = table_y - table_height
  #logging.info(table_y)


  # Draw the title
  c.setFont("Helvetica-Bold", 10)  # or 10, or any other desired font size
  title_x, title_y = table_x + table_width / 7.5, table_y +  table_height/3 + 0.75 * inch
  c.drawCentredString(title_x, title_y, "DELIVERY DETAILS")
  #logging.info(title_y)



  for i in range(len(data2)):
      for j in range(len(data2[i])):
          cell_x = table_x + j * (table_width / len(data2[i]))
          cell_y = table_y + i * row_height
          cell_width = (table_width / len(data2[i]))
          cell_height = row_height
          
          # Draw the cell rectangle
          c.rect(cell_x, cell_y, cell_width, cell_height)
          
          # Calculate the x and y coordinates for the small text
          small_text_x = cell_x + 0.1 * inch
          small_text_y = cell_y + cell_height - 0.1 * inch
          
          # Set the font size for the small text and draw it
          c.setFont("Helvetica", 7)
          c.drawString(small_text_x, small_text_y, data2S[i][j])

          # Calculate the x and y coordinates for the text
          text_x = cell_x + cell_width / 8
          text_y = cell_y + cell_height /1.25
          
          #c.translate(inch,inch)
          textobject = c.beginText(text_x, text_y)
          textobject.setFont("Helvetica", 8)
          #c.setFont("Helvetica", 10)
          # Draw the cell text
          #c.drawCentredString(text_x, text_y, data2[i][j])

          lines = data2[i][j].splitlines()
          for line in lines: 
            textobject.textLine(line)
          c.drawText(textobject)




  ########################  TABLE-3  ############################

  data3 = [  [' ',' ',' ',' ',' '] ]
  data3S = [['ITEMS','CUBIC METERS','KILOS','SERVICE','DANGEROUS GOODS']]

  # Define table dimensions and styling

  table_x, table_y =  center_x - 0.5*table_width,  table_bottom_y + 1 * inch     #top_y - table_height-table_height-(table_height/2)-(table_height/2) - 1.1 * inch
  row_height = 0.5 * inch
  col_width = table_width / 2
  text_x, text_y = table_x + col_width / 2, table_y + row_height / 2
  table_bottom_y = table_y - table_height


  # Draw the title
  c.setFont("Helvetica-Bold", 10)
  title_x, title_y = table_x + table_width / 7.4, table_y + table_height/3      #+ 0.25 * inch
  c.drawCentredString(title_x, title_y, "GOODS DESCRIPTION")


  for i in range(len(data3)):
      for j in range(len(data3[i])):
          cell_x = table_x + j * (table_width / len(data3[i]))
          cell_y = table_y + i * row_height
          cell_width = (table_width / len(data3[i]))
          cell_height = row_height
          
          # Draw the cell rectangle
          c.rect(cell_x, cell_y, cell_width, cell_height)
          
          # Calculate the x and y coordinates for the small text
          small_text_x = cell_x + 0.1 * inch
          small_text_y = cell_y + cell_height - 0.1 * inch
          
          # Set the font size for the small text and draw it
          c.setFont("Helvetica", 7)
          c.drawString(small_text_x, small_text_y, data3S[i][j])

          # Calculate the x and y coordinates for the text
          text_x = cell_x + cell_width / 2
          text_y = cell_y + cell_height / 3
          
          c.setFont("Helvetica", 10)
          # Draw the cell text
          c.drawCentredString(text_x, text_y, data3[i][j])




  ##########################  TABLE-4  ############################


  data4 = [    [' ',date+" "+time+".",' '] ]
  data4S = [    ['TICKET','DATE&TIME','RECEIVER NAME'] ]

  # Define table dimensions and styling

  table_x, table_y =  center_x - 0.5*table_width,  table_bottom_y + 1 * inch    #top_y - table_height-table_height-(table_height/2)-(table_height/2)-(table_height/2)- 2 * inch
  row_height = 0.5 * inch
  col_width = table_width / 2
  text_x, text_y = table_x + col_width / 2, table_y + row_height / 2
  table_bottom_y = table_y - table_height


  # Draw the title
  c.setFont("Helvetica-Bold", 10)
  title_x, title_y = table_x + table_width / 4, table_y + table_height/3 #+ 0.15 * inch
  c.drawCentredString(title_x, title_y, "RECEIVED IN GOOD ORDER AND CONDITION")


  for i in range(len(data4)):
      for j in range(len(data4[i])):
          cell_x = table_x + j * (table_width / len(data4[i]))
          cell_y = table_y + i * row_height
          cell_width = (table_width / len(data4[i]))
          cell_height = row_height
          
          # Draw the cell rectangle
          c.rect(cell_x, cell_y, cell_width, cell_height)
          
          # Calculate the x and y coordinates for the small text
          small_text_x = cell_x + 0.1 * inch
          small_text_y = cell_y + cell_height - 0.1 * inch
          
          # Set the font size for the small text and draw it
          c.setFont("Helvetica", 7)
          c.drawString(small_text_x, small_text_y, data4S[i][j])

          # Calculate the x and y coordinates for the text
          text_x = cell_x + cell_width / 2
          text_y = cell_y + cell_height / 3
          
          c.setFont("Helvetica", 10)
          # Draw the cell text
          c.drawCentredString(text_x, text_y, data4[i][j])


  #####################   WHITE BOX For SS  #######################

  c.setFillColorRGB(1, 1, 1)  # Set fill color to white
  x, y, width, height = table_x, table_bottom_y- table_height + 0.5*inch, table_width, table_height + 1*inch
  c.rect(x, y, width, height, fill=True)

  # Load the image
  #image_path = "4.jpg"  # Replace with the path to your image file
  try:
    img = Image.open(screenshot_path)
    img_width, img_height = img.size

    # Calculate the position and size of the image to fit within the box
    box_width = width - 2 * (1.5 * inch)
    box_height = height - 2 * (0.1 * inch)
    scale_factor = min(box_width / img_width, box_height / img_height)
    resized_width = img_width * scale_factor
    resized_height = img_height * scale_factor
    image_x = x + (width - resized_width) / 2
    image_y = y + (height - resized_height) / 2

    # Draw the image inside the box
    c.drawImage(screenshot_path, image_x, image_y, width=resized_width, height=resized_height)

  except FileNotFoundError:
      pass

  c.save()

#generate_pdf(date,time,code,fromA,toA,manual,filename,image_path)