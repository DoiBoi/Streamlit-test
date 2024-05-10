import replicate
from fpdf import FPDF   # For PDF generation

class Recipe:
    def __init__(self, name: str, ingredients: list, instructions: str, full_recipe: str):
        # Fix issue with leading space character
        if name[0] == " ":
            name = name[1:]
        self.name = name

        self.ingredients = ingredients
        self._clean_instructions(instructions)
        self.full_recipe = full_recipe
        self.num_of_ingredients = len(self.ingredients)

        self.generate_tags()

    def generate_tags(self) -> None:
        self.total_time = 0
        tags = self._generate_arctic_response()
        self.tags = "".join(tags)[1:].split("\n\n")[-1].split(", ")
        if "," in self.tags:
            self.tags = self.tags[-1].split(",")

    # This is a private function just to be used inside the class
    def _clean_instructions(self, instructions: str) -> None:
        instructions = instructions.split("\n1. ")[-1].split("\n")
        self.instructions = []
        step_no = 0
        # Fix issue with numbering not correctly showing up
        for step in instructions:
            if step != "":
                self.instructions.append(f'{step_no+1}. {step.split(f"{step_no+1}. ")[-1]}')
                step_no += 1

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

    # This is a private function just to be used inside the class
    def _generate_arctic_response(self):
        prompt = []
        prompt.append("<|im_start|>system\nYou must generate catagory tags (such as dairy, non-vegetarian, spicy, or others) that would apply to the recipe (IT MUST NOT INCLUDE INGREDIENTS OR THE NAME OF THE DISH) that the user will give to you even if it's incomplete. You MUST format it as a COMMA SEPARATED list of tags and not have anything else in your response.<|im_end|>\n")
        prompt.append("<|im_start|>user\n" + self.full_recipe + "<|im_end|>")

        prompt.append("<|im_start|>assistant")
        prompt.append("")
        prompt_str = "\n".join(prompt)

        response = []
        for event in replicate.stream("snowflake/snowflake-arctic-instruct",
                            input={"prompt": prompt_str,
                                    "prompt_template": r"{prompt}",
                                    "temperature": 0.1,
                                    "top_p": 1,
                                    }):
            response.append(str(event))

        return response
