from fpdf import FPDF

instructions_list = ""
ingredients_list = ""

# Initialise PDF generator
pdf = FPDF(format="A4")
pdf.add_page()

# Title
pdf.set_font('Helvetica', size=24, style="BI")
pdf.multi_cell(text="Recipe Name", w=210/2, padding=5, new_x="LEFT", new_y="NEXT")

# Main body
column_width = 190/2
pdf.set_font('Helvetica', size=18, style="B")
pdf.multi_cell(text="Ingredients", w=column_width, new_x="RIGHT", new_y="TOP", padding=3)
pdf.multi_cell(text="Method", w=column_width, new_x="LMARGIN", new_y="NEXT", padding=3)
pdf.set_font('Helvetica', size=11, style="")
pdf.multi_cell(w=column_width, h=5, new_x="RIGHT", new_y="TOP", text=ingredients_list)
pdf.multi_cell(w=column_width, h=5, new_x="LEFT", new_y="TOP", text=instructions_list)

pdf_output = pdf.output()
