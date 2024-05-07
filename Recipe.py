from fpdf import FPDF   # For PDF generation

class Recipe:
    def __init__(self, name: str, ingredients: list, instructions: str, full_recipe: str):
        # Fix issue with leading space character
        if name[0] == " ":
            name = name[1:]
        self.name = name

        self.ingredients = ingredients

        instructions = instructions.split("\n1. ")[-1].split("\n")
        self.instructions = []
        # Fix issue with numbering not correctly showing up
        for index, step in enumerate(instructions):
            if step != "":
                self.instructions.append(f'{index+1}. {step.split(f"{index+1}. ")[-1]}')

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
        pdf.multi_cell(text=self.name, w=190, padding=5, new_x="LEFT", new_y="NEXT", markdown=True)

        # Main body
        column_width = 190/2
        pdf.set_font('Helvetica', size=18, style="B")
        pdf.multi_cell(text="Ingredients", w=column_width, new_x="RIGHT", new_y="TOP", padding=3)
        pdf.multi_cell(text="Method", w=column_width, new_x="LMARGIN", new_y="NEXT", padding=3)
        pdf.set_font('Helvetica', size=11, style="")
        pdf.multi_cell(w=column_width, h=5, new_x="RIGHT", new_y="TOP", text=ingredients, markdown=True)
        pdf.multi_cell(w=column_width, h=5, new_x="LEFT", new_y="TOP", text=instructions, markdown=True)

        # Output final PDF
        pdf_output = bytes(pdf.output())
        return pdf_output
