from fpdf import FPDF   # For PDF generation

class Recipe:
    def __init__(self, name: str, ingredients: list, instructions: str, full_recipe: str):
        self.name = name
        self.ingredients = ingredients
        instructions = instructions.split("\n1. ")[-1]
        self.instructions = f'1. {instructions}'.split("\n")
        self.full_recipe = full_recipe

    #TODO: Add any tags that might be useful for filtering in the saved recipes page
    def generate_tags(self) -> None:
        self.num_of_ingredients = len(self.ingredients)
        self.tags = []

    def make_pdf(self) -> bytes:
        # Make the components into strings
        ingredients = "\n- ".join(self.ingredients)
        ingredients = f"- {ingredients}"
        instructions = "\n\n".join(self.instructions)

        # Initialise PDF generator
        pdf = FPDF(format="A4")
        pdf.add_page()

        # Title
        pdf.set_font('Helvetica', size=24, style="BI")
        pdf.multi_cell(text=self.name, w=210/2, padding=5, new_x="LEFT", new_y="NEXT")

        # Main body
        column_width = 190/2
        pdf.set_font('Helvetica', size=18, style="B")
        pdf.multi_cell(text="Ingredients", w=column_width, new_x="RIGHT", new_y="TOP", padding=3)
        pdf.multi_cell(text="Method", w=column_width, new_x="LMARGIN", new_y="NEXT", padding=3)
        pdf.set_font('Helvetica', size=11, style="")
        pdf.multi_cell(w=column_width, h=5, new_x="RIGHT", new_y="TOP", text=ingredients)
        pdf.multi_cell(w=column_width, h=5, new_x="LEFT", new_y="TOP", text=instructions)

        # Output final PDF
        pdf_output = bytes(pdf.output())
        return pdf_output
