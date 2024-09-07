import pandas as pd
import pdfkit
from io import StringIO

# converts HTML table to excel
def html_excel(html_content, output):
    html_io = StringIO(html_content)
    tables = pd.read_html(html_io)
    df = tables[0]
    df.to_excel(output, index=False)

# converts HTML table to pdf
def html_pdf(html_content, output):
    pdfkit.to_string(html_content, output)

html_file = "html_to_format.html"
with open(html_file, 'r') as file:
    html_content = file.read()
html_excel(html_content, "html_to_excel.xlsx")
