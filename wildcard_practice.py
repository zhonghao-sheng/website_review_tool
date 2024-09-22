# from fnmatch import *
# # currently fnmatch only supports * ? [seq] [!seq] in wildcard pattern, so need to write
# # some manually
# pattern = "fr%nka"
# a = fnmatch("franka", pattern)
#
# # translate % and -  to * and ? in wildcard pattern into fnmatch recognizable
# def translate_wildcard(pattern):
#     pattern = pattern.replace('%', '*')
#     pattern = pattern.replace('_', '?')
#     return pattern
# if a is False:
#     pattern = translate_wildcard(pattern)
#     print(fnmatch("franka", pattern))
#     print
# else:
#     print(True)

from reportlab.lib.pagesizes import letter

from reportlab.pdfgen import canvas



# Define the path for the PDF file

pdf_path = "output.pdf"



# Create a PDF canvas

c = canvas.Canvas(pdf_path, pagesize=letter)



# Set the title and write some text

c.setTitle("Sample PDF Document")

c.drawString(100, 750, "Hello, this is a sample PDF document.")

c.drawString(100, 730, "Here is some more text.")



# Add a table-like structure (simple example)

data = [

    ["Name", "Age", "City"],

    ["Aliceeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee", 300000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000, "New York"],

    ["Bob", 25, "Los Angeles"],

    ["Charlie", 35, "Chicago"]

]



# Set starting position for the table

x = 100

y = 700



# Write the data to the PDF

for row in data:

    c.drawString(x, y, f"{row[0]} | {row[1]} | {row[2]}")

    y -= 20  # Move down for the next row
c.save()