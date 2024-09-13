import pandas as pd
import pdfkit
from io import StringIO
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows

# Converts HTML table to excel and keeps formatting
def html_excel(html_content, output):
    # Load HTML content into a DataFrame
    html_io = StringIO(html_content)
    tables = pd.read_html(html_io)
    df = tables[0]

    # Create a new Excel workbook and active sheet
    wb = Workbook()
    ws = wb.active

    # Apply some styling (like borders and alignment)
    thin_border = Border(left=Side(style='thin'), right=Side(style='thin'), 
                         top=Side(style='thin'), bottom=Side(style='thin'))
    header_font = Font(bold=True)
    cell_alignment = Alignment(horizontal='left', vertical='center', wrap_text=True)

    # Write the dataframe to the worksheet row by row
    for r_idx, row in enumerate(dataframe_to_rows(df, index=False, header=True), start=1):
        for c_idx, value in enumerate(row, start=1):
            cell = ws.cell(row=r_idx, column=c_idx, value=value)
            cell.alignment = cell_alignment
            cell.border = thin_border
            if r_idx == 1:  # Apply header styling
                cell.font = header_font

    # Save the workbook
    wb.save(output)

# Converts HTML table to pdf
def html_pdf(html_content, output):
    pdfkit.to_file(html_content, output)

# Load HTML content
html_file = "html_to_format.html"
with open(html_file, 'r') as file:
    html_content = file.read()

# Convert HTML to Excel with formatting
html_excel(html_content, "html_to_excel.xlsx")
html_pdf(html_content, "html_to_pdf.pdf")
