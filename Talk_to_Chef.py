import streamlit as st
import replicate
import os
from transformers import AutoTokenizer
import re

# Set assistant icon to Snowflake logo
icons = {"assistant": "./resources/chef-hat.svg", "user": "👨‍🍳"}

DEFAULT_PROMPT = ["You are a helpful chef",
                  "You are a famous, condescending chef defined by his fiery temper, aggressive behaviour, strict demeanour, and frequent usage of profane language, while making blunt, critical, and controversial comments, including insults and sardonic wisecracks about contestants and their cooking abilities." ,
                  "You are a chef known for being a Gen X glam rocker and your energy is over the top with a flashy persona that shines through in everything you do.",
                  "You are a famous chef known for being very laid back, joyful, and chill, and sometimes you use british slangs to praise whatever you're making by taking about how it looks, tastes, or smells.",
                  "You are a middle-aged Asian chef with an exaggerated Cantonese accent who is usually seen aggressively critiquing people's attempts at cooking Asian food. You expertise in east Asian cuisine and prefer to give fried rice related recipes and often say phrases like 'Haiya!' and 'Fuiyo!'. You MUST use those phrases in your response.",
                  "You are a chef obsessed with burgers and you will stop at nothing to create a burger, no matter what the ingredients are. You MUST add multiple burger emojis in your response."]

CHEF_LIST = ["Default","Gordon Ramsay", "Guy Fieri", "Jamie Oliver", "Uncle Roger", "Burger Guy"]

MODE_PROMPT = ["Additionally, the user will give a list of ingredients and you are tasked to provide the user a recipe," +
                  " please restrain the recipe to what the user has listed: do not add any other ingredients than what the user has given. Even if it is just one ingredient, please try to come up with a recipe. You may comment on the recipe beforehand, but the recipe must be in the form of: Ingredients: <list of ingredients separated by a new line> Instructions: <List of instructions for the recipe>",
                "Additionally, the user will provide the name of a meal and you are tasked to provide a recipe for that meal in the form of: Ingredients: <list of ingredients separated by a new line> Instructions: <List of instructions for the recipe>"]

MODE_LIST = ["Create recipe from ingredients", "Create recipe for dish"]

ABOUT_MESSAGES = ['This chat bot is designed to give you recipe suggestions based on ingredients you have. To use it, simply write each of your ingredients separated by commas.',
                  'This chat bot is designed to give you a recipe based on the dish you provide. To use it, simply enter the name of your dish.']

START_MESSAGES = ["Hi, I'm an language model trained to be your personal chef! Ask me about any recipe or anything food related.",
                  "Right, let's get one thing straight - cooking isn't just about throwing ingredients together and hoping for the best. It's an art form, and I expect nothing but perfection from you. Now, let's get started!",
                  "Welcome, my friend! Are you ready to take your taste buds on a wild ride? Let's dive into the world of flavor and create something that'll make your mouth water!",
                  "Hello there! Let's cook up a storm together, using fresh ingredients and simple techniques to create a delicious meal that'll bring smiles to everyone's faces. Ready to get started?",
                  "Hey buddy, my main man! Ready to have some fun in the kitchen? Let's make something so tasty, it'll make your taste buds dance like they've never danced before.",
                  "Welcome to the burger joint, my friend! What can I get started for you today?"]

EXAMPLES = ['Eggs, flour, milk, vanilla extract, baking soda, baking powder, butter, sugar, salt.',
            'Bolognese']

# This is used to check that all the ingredients detected are valid
# https://github.com/schollz/food-identicon/blob/master/ingredients.txt
INGREDIENT_LIST = []
with open("resources/ingredients_list.txt", mode="r") as file:
    lines = file.read().split("\n")
    INGREDIENT_LIST = [i.capitalize() for i in lines]

class Recipe:
    def __init__(self, name, ingredients, full_recipe):
        self.name = name
        self.ingredients = ingredients
        self.full_recipe = full_recipe

        self.instructions = self.generateInstructions(full_recipe)

    #TODO: Generate the instructions by passing it to another ai (because the original recipe could be formatted weirdly)
    def generateInstructions(self, recipe):
        instruction_list = recipe.split("\n")
        return instruction_list

# App title
st.set_page_config(page_title="Home - Chef Chat", page_icon="👨‍🍳")

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": START_MESSAGES[index]}]

# Replicate Credentials
with st.sidebar:
    if 'REPLICATE_API_TOKEN' in st.secrets:
        replicate_api = st.secrets['REPLICATE_API_TOKEN']
    else:
        replicate_api = st.text_input('Enter Replicate API token:', type='password')
        if not (replicate_api.startswith('r8_') and len(replicate_api)==40):
            st.warning('Whoops, something went wrong! Please enter your Replicate API token.', icon='⚠️')
            st.markdown("**Don't have an API token?** Head over to [Replicate](https://replicate.com) to sign up for one.")
        else:
            st.success('API token loaded!', icon='✅')

    os.environ['REPLICATE_API_TOKEN'] = replicate_api


    # DESIGN ELEMENTS
    st.title('CHEF CHAT :cook:')

    # Navigation area
    st.header("Navigation")
    st.page_link("pages/saved_recipes.py", label="Saved Recipes", icon="📃")

    st.divider()

    st.header("Options")

    temperature = 3     # This is the "creativity" of the response (higher is more creative, less is predictable)
    top_p = 0.1         # This is the next token's probability threshold (lower makes more sense)

    # Chef personality selector
    option = st.selectbox('Please select a chef:', CHEF_LIST, help="This determines what personality the chat bot has when creating recipes.", on_change=clear_chat_history)
    index = CHEF_LIST.index(option)

    # Mode selection
    mode = st.radio("Select a mode", MODE_LIST, on_change=clear_chat_history)
    mode_index = MODE_LIST.index(mode)

    st.button('Clear chat', on_click=clear_chat_history, type="primary")

    st.divider()

    st.header("About")
    st.markdown(ABOUT_MESSAGES[mode_index])
    st.markdown("Here's an example message:")
    st.markdown(f"*{EXAMPLES[mode_index]}*")

    st.divider()

    st.caption(':red[_For any health-related concerns, including allergy information, please consult a qualified medical expert or your personal physician. Never rely solely on the advice of an AI language model for matters concerning your well-being._]')
    # st.caption('Built by [Snowflake](https://snowflake.com/) to demonstrate [Snowflake Arctic](https://www.snowflake.com/blog/arctic-open-and-efficient-foundation-language-models-snowflake). App hosted on [Streamlit Community Cloud](https://streamlit.io/cloud). Model hosted by [Replicate](https://replicate.com/snowflake/snowflake-arctic-instruct).')

# Store LLM-generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": START_MESSAGES[index]}]
st.session_state.messages[0]["content"] = START_MESSAGES[index]

# Create container for messages area
container = st.container()

# Display or clear chat messages
for message in st.session_state.messages:
    with container:
        with st.chat_message(message["role"], avatar=icons[message["role"]]):
            st.write(message["content"])


@st.cache_resource(show_spinner=False)
def get_tokenizer():
    """Get a tokenizer to make sure we're not sending too much text
    text to the Model. Eventually we will replace this with ArcticTokenizer
    """
    return AutoTokenizer.from_pretrained("huggyllama/llama-7b")

def get_num_tokens(prompt):
    """Get the number of tokens in a given prompt"""
    tokenizer = get_tokenizer()
    tokens = tokenizer.tokenize(prompt)
    return len(tokens)

# Function for generating Snowflake Arctic response
def generate_arctic_response():
    prompt = []
    prompt.append("<|im_start|>system\n" + DEFAULT_PROMPT[index] + MODE_PROMPT[mode_index] + "<|im_end|>\n")
    for dict_message in st.session_state.messages:
        if dict_message["role"] == "user":
            prompt.append("<|im_start|>user\n" + dict_message["content"] + "<|im_end|>")
        else:
            prompt.append("<|im_start|>assistant\n" + dict_message["content"] + "<|im_end|>")

    prompt.append("<|im_start|>assistant")
    prompt.append("")
    prompt_str = "\n".join(prompt)

    if get_num_tokens(prompt_str) >= 3072:
        st.error("Conversation length too long. Please keep it under 3072 tokens.")
        st.button('Clear chat', on_click=clear_chat_history, key="clear_chat_history", type="primary")
        st.stop()

    for event in replicate.stream("snowflake/snowflake-arctic-instruct",
                           input={"prompt": prompt_str,
                                  "prompt_template": r"{prompt}",
                                  "temperature": temperature,
                                  "top_p": top_p,
                                  }):
        yield str(event)

# Function for generating Snowflake Arctic ingredients list
def generate_arctic_ingredients():
    prompt = []
    prompt.append("<|im_start|>system\nThe user will give you a recipe, please return all the ingredients listed in the message as a COMMA SEPARATED SENTENCE without any measurements. It doesn't matter whether the recipe is complete or not, just try to find as many as possible.<|im_end|>\n")
    prompt.append("<|im_start|>user\n" + st.session_state.messages[-1]["content"] + "<|im_end|>")

    prompt.append("<|im_start|>assistant")
    prompt.append("")
    prompt_str = "\n".join(prompt)

    if get_num_tokens(prompt_str) >= 3072:
        st.error("Conversation length too long. Please keep it under 3072 tokens.")
        st.button('Clear chat', on_click=clear_chat_history, key="clear_chat_history", type="primary")
        st.stop()

    for event in replicate.stream("snowflake/snowflake-arctic-instruct",
                           input={"prompt": prompt_str,
                                  "prompt_template": r"{prompt}",
                                  "temperature": 0.1,
                                  "top_p": 1,
                                  }):
        yield str(event)

def replace_ingredient(ingredient):
    # Make new input and remove old one
    prev_user_input = st.session_state.messages[-2]

    # Add the other ingredients in a way that makes sense
    if "but without using" in prev_user_input["content"]:
        user_input = {"role": "user", "content": f"{prev_user_input['content']}, and {ingredient}"}
    else:
        user_input = {"role": "user", "content": f"{prev_user_input['content']} but without using {ingredient}"}
    st.session_state.messages.append(user_input)

    # Add new user input to history
    with container:
        with st.chat_message("user", avatar=icons["user"]):
            st.write(user_input["content"])

    # Generate new response
    generate_display_info()

# Function for generating Snowflake Arctic name
def generate_arctic_name():
    prompt = []
    prompt.append("<|im_start|>system\nThe user will give you a recipe with instructions, please return a fitting name for this recipe, and ensure that your response ONLY includes this name, and nothing else. It doesn't matter whether the recipe is complete or not, just try to create a name.<|im_end|>\n")
    prompt.append("<|im_start|>user\n" + st.session_state.messages[-1]["content"] + "<|im_end|>")

    prompt.append("<|im_start|>assistant")
    prompt.append("")
    prompt_str = "\n".join(prompt)

    if get_num_tokens(prompt_str) >= 3072:
        st.error("Conversation length too long. Please keep it under 3072 tokens.")
        st.button('Clear chat', on_click=clear_chat_history, key="clear_chat_history", type="primary")
        st.stop()

    for event in replicate.stream("snowflake/snowflake-arctic-instruct",
                           input={"prompt": prompt_str,
                                  "prompt_template": r"{prompt}",
                                  "temperature": 0.1,
                                  "top_p": 1,
                                  }):
        yield str(event)

# saves given recipe into session state
# recipe parameter: recipe object (defined near the top of the file)
def save_recipe(recipe):
    if "recipes" not in st.session_state:
        st.session_state.recipes = []

    st.session_state.recipes.append(recipe)
    for recipe in st.session_state.recipes:
        print(recipe)

# clears all saved recipes, if any are saved
def clear_recipes():
    if "recipes" in st.session_state:
        st.session_state.recipes = []

# Generates the regular response and the ingredients list
def generate_display_info():
    with container:
        with st.chat_message("assistant", avatar=icons["assistant"]):
            response = generate_arctic_response()
            full_response = st.write_stream(response)

            # Add to history
            message = {"role": "assistant", "content": full_response}
            st.session_state.messages.append(message)

            # Get all the ingredients needed and put them into a list
            ingredients_msg = generate_arctic_ingredients()
            ingredients = "".join(list(ingredients_msg)).split("\n\n")[-1]  # This stops any overflow from previous responses
            ingredients_list = ingredientregex.sub("", ingredients).strip(" ").split(", ")

            name_msg = generate_arctic_name()
            name = "".join(list(name_msg)).split("\n\n")[-1] 

            # Make everything capitalized to stop issues and format nicer
            ingredient_list = [i.capitalize() for i in ingredients_list]

            # Check if all the ingredients are actually valid
            ingredients_list = []
            for ingredient in ingredient_list:
                if ingredient in INGREDIENT_LIST:
                    ingredients_list.append(ingredient)

            st.button("Save recipe", type="secondary", key="save", on_click=lambda recipe=Recipe(name, ingredients_list, full_response): save_recipe(recipe))

            if mode_index == 1:
                # Show the replace ingredients list
                num_cols = 3
                with st.expander("Replace ingredient:"):
                    icols = [i for i in st.columns(num_cols)]
                    index = 0
                    for ingredient in ingredients_list:
                        icols[index%num_cols].button(ingredient, type="secondary", key=ingredient, on_click=lambda ingredient=ingredient: replace_ingredient(ingredient))
                        index += 1

# User-provided prompt
prompt = st.chat_input(disabled=not replicate_api, on_submit=generate_arctic_response, placeholder="Enter your ingredients here")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with container:
        with st.chat_message("user", avatar=icons["user"]):
            st.write(prompt)

# Regex for getting just ingredients
ingredientregex = re.compile("[^a-zA-Z, \r\n]")       # https://stackoverflow.com/a/22521156

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    generate_display_info()
