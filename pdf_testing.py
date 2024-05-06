from fpdf import FPDF

instructions_list = "1. Step one, do this\n2. Step two, do that.\n3. Step three, do some more stuff.\n4. Step four.\n5. Step five, you're done."
ingredients_list = "Some ingredients are listed here\n\n- Rice\n- Burger\n- Cheese\n- Beef\n- Some other ingredient"

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

# To save to variable
pdf_output = bytes(pdf.output())
# To save to file
pdf.output("pdf_testing.pdf")
