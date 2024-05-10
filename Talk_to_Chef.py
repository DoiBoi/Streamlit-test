import streamlit as st  # For website generation
import replicate        # For accessing AI model API
import os               # For opening external text files
from transformers import AutoTokenizer
from Recipe import Recipe

# Set assistant icon to Snowflake logo
icons = {"assistant": "./resources/chef-hat.svg", "user": "👨‍🍳"}

DEFAULT_INGREDIENTS_PROMPT = ["You are a chef. Only provide the ingredients to this dish, do NOT under any circumstance provide the methodology or anything else. Do not start with the word ingredients, start immediately by listing the ingredients.",
                  "You are a famous, condescending chef defined by his fiery temper, aggressive behaviour, strict demeanour, and frequent usage of profane language. Only provide the ingredients to this dish, do NOT under any circumstance provide the methodology or anything else. Do not start with the word ingredients, start immediately by listing the ingredients.",
                  "You are a chef known for being a Gen X glam rocker and your energy is over the top with a flashy persona. Only provide the ingredients to this dish, do NOT under any circumstance provide the methodology or anything else. Do not start with the word ingredients, start immediately by listing the ingredients.",
                  "You are a famous chef known for being very laid back, joyful, and chill. Only provide the ingredients to this dish, do NOT under any circumstance provide the methodology or anything else. Do not start with the word ingredients, start immediately by listing the ingredients.",
                  "You are a middle-aged Asian chef who's expertise is in east Asian cuisine and prefer to give fried rice related recipes. Only provide the ingredients to this dish, do NOT under any circumstance provide the methodology or anything else. Do not start with the word ingredients, start immediately by listing the ingredients.",
                  "You are a chef obsessed with burgers and you will stop at nothing to create a burger. Only provide the ingredients to this dish, do NOT under any circumstance provide the methodology or anything else. Do not start with the word ingredients, start immediately by listing the ingredients."]

DEFAULT_METHOD_PROMPT = ["You are a helpful chef. Only provide the instructions to make this dish, do NOT under any circumstance provide the ingredients or anything else. You MUST ONLY use the ingredients provided. Write it as if you were a chef.",
                  "You are a famous, condescending chef defined by his fiery temper, aggressive behaviour, strict demeanour, and frequent usage of profane language, while making blunt, critical, and controversial comments, including insults and sardonic wisecracks about contestants and their cooking abilities. Only provide the instructions to make this dish, do NOT under any circumstance provide the ingredients or anything else. You MUST ONLY use the ingredients provided.",
                  "You are a chef known for being a Gen X glam rocker and your energy is over the top with a flashy persona that shines through in everything you do. Only provide the instructions to make this dish, do NOT under any circumstance provide the ingredients or anything else. You MUST ONLY use the ingredients provided.",
                  "You are a famous chef known for being very laid back, joyful, and chill, and sometimes you use british slangs to praise whatever you're making by taking about how it looks, tastes, or smells. Only provide the instructions to make this dish, do NOT under any circumstance provide the ingredients or anything else. You MUST ONLY use the ingredients provided.",
                  "You are a middle-aged Asian chef with an exaggerated Cantonese accent who is usually seen aggressively critiquing people's attempts at cooking Asian food. You expertise in east Asian cuisine and prefer to give fried rice related recipes and often say phrases like 'Haiya!' and 'Fuiyo!'. You MUST use those phrases in your response. Only provide the instructions to make this dish, do NOT under any circumstance provide the ingredients or anything else. You MUST ONLY use the ingredients provided.",
                  "You are a chef obsessed with burgers and you will stop at nothing to create a burger, no matter what the ingredients are. Only provide the instructions to make this dish, do NOT under any circumstance provide the ingredients or anything else. You MUST ONLY use the ingredients provided."]

DEFAULT_INGREDIENTS_LIST_PROMPT = "The user will give you a recipe, please return all the ingredients listed in the message as a COMMA SEPARATED SENTENCE without any measurements. It doesn't matter whether the recipe is complete or not, just try to find as many as possible."

DEFAULT_NAME_PROMPT = "The user will give you a recipe with instructions, please return a fitting name for this recipe, and ensure that your response ONLY includes this name, and nothing else. It doesn't matter whether the recipe is complete or not, just try to create a name."

CHEF_LIST = ["Default","Gordon Ramsay", "Guy Fieri", "Jamie Oliver", "Uncle Roger", "Burger Guy"]

MODE_PROMPT = ["Additionally, the user will give a list of ingredients and you are tasked to provide the user a recipe," +
                  " please restrain the recipe to what the user has listed: do not add any other ingredients than what the user has given. Even if it is just one ingredient, please try to come up with a recipe. You may comment on the recipe beforehand, but the recipe must be in the form of: Ingredients: <list of ingredients separated by a new line> Instructions: <List of instructions for the recipe>",
                "Additionally, the user will provide the name of a meal and you are tasked to provide a recipe for that meal in the form of: Ingredients: <list of ingredients separated by a new line> Instructions: <List of instructions for the recipe>"]

MODE_LIST = ["Create recipe from ingredients", "Create recipe for dish"]

ABOUT_MESSAGES = ['This chat bot is designed to give you recipe suggestions based on ingredients you have. To use it, simply write each of your ingredients separated by commas.',
                  'This chat bot is designed to give you a recipe based on the dish you provide. To use it, simply enter the name of your dish.']

START_MESSAGES = [["Hi, I'm an language model trained to be your personal chef! Give me some ingredients and I'll make a recipe or ask me anything food related!",
                   "Hi, I'm an language model trained to be your personal chef! Give me the name of a dish and I'll make a recipe or ask me anything food related!"],
                  ["Right, let's get one thing straight - cooking isn't just about throwing ingredients together and hoping for the best. It's an art form, and I expect nothing but perfection from you. Now, let's get started!",
                  "Right, let's get one thing straight - cooking isn't just about throwing ingredients together and hoping for the best. It's an art form, and I expect nothing but perfection from you. Now, let's get started!"],
                  ["Welcome, my friend! Are you ready to take your taste buds on a wild ride? Let's dive into the world of flavor and create something that'll make your mouth water!",
                  "Welcome, my friend! Are you ready to take your taste buds on a wild ride? Let's dive into the world of flavor and create something that'll make your mouth water!"],
                  ["Hello there! Let's cook up a storm together, using fresh ingredients and simple techniques to create a delicious meal that'll bring smiles to everyone's faces. Ready to get started?",
                  "Hello there! Let's cook up a storm together, using fresh ingredients and simple techniques to create a delicious meal that'll bring smiles to everyone's faces. Ready to get started?"],
                  ["Hey buddy, my main man! Ready to have some fun in the kitchen? Let's make something so tasty, it'll make your taste buds dance like they've never danced before.",
                  "Hey buddy, my main man! Ready to have some fun in the kitchen? Let's make something so tasty, it'll make your taste buds dance like they've never danced before."],
                  ["Welcome to the burger joint, my friend! What can I get started for you today?",
                  "Welcome to the burger joint, my friend! What can I get started for you today?"]]

EXAMPLES = ['Eggs, flour, milk, vanilla extract, baking soda, baking powder, butter, sugar, salt.',
            'Bolognese']

CHAT_INPUT_HINTS = ["Enter your ingredients here",
                    "Enter a dish name here"]

# INDEX = 0

# This is used to check that all the ingredients detected are valid
# https://github.com/schollz/food-identicon/blob/master/ingredients.txt
INGREDIENT_LIST = []
with open("resources/ingredients_list.txt", mode="r") as file:
    lines = file.read().split("\n")
    INGREDIENT_LIST = [i.capitalize() for i in lines]

# App title
st.set_page_config(page_title="Home - Chef Chat", page_icon="👨‍🍳")

def clear_chat_history():
    INDEX = CHEF_LIST.index(st.session_state.personality_index)
    MODE_INDEX = MODE_LIST.index(st.session_state.mode_index)
    st.session_state.messages = [{"role": "assistant", "content": START_MESSAGES[INDEX][MODE_INDEX]}]

def reset_options():
    st.session_state.personality_option = 0
    st.session_state.mode_option = 0

def set_mode_from_key():
    MODE_INDEX = MODE_LIST.index(st.session_state.mode_index)
    st.session_state.mode_option = MODE_INDEX
    clear_chat_history()
def set_person_from_key():
    INDEX = CHEF_LIST.index(st.session_state.personality_index)
    st.session_state.personality_option = INDEX
    clear_chat_history()

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
    st.title('CHEF CHAT 👨‍🍳')

    # Navigation area
    st.header("Navigation")
    st.page_link("pages/saved_recipes.py", label="Saved Recipes", icon="📃")

    st.divider()

    st.header("Options")

    temperature = 3     # This is the "creativity" of the response (higher is more creative, less is predictable)
    top_p = 0.1         # This is the next token's probability threshold (lower makes more sense)

    # Chef personality selector
    if "personality_option" not in st.session_state.keys():
        st.session_state.personality_option = 0

    option = st.selectbox('Please select a chef:', CHEF_LIST, index=st.session_state.personality_option, help="This determines what personality the chat bot has when creating recipes.", on_change=set_person_from_key, key = "personality_index")

    # Mode selection
    if "mode_option" not in st.session_state.keys():
        st.session_state.mode_option = 0

    mode = st.radio("Select a mode", MODE_LIST, index=st.session_state.mode_option, on_change=set_mode_from_key, key="mode_index")

    st.button("Reset options", on_click=reset_options, type="secondary", use_container_width=True)

    col1, col2 = st.columns(2)
    clear_chat = col1.button("Clear chat", type="primary", use_container_width=True)

    if clear_chat:
        confirm_clear_chat = col2.button('Confirm clear', on_click=clear_chat_history, type="secondary", use_container_width=True)

    st.divider()

    st.header("About")
    st.markdown(ABOUT_MESSAGES[st.session_state.mode_option])
    st.markdown("Here's an example message:")
    st.markdown(f"*{EXAMPLES[st.session_state.mode_option]}*")

    st.divider()

    st.caption(':red[_For any health-related concerns, including allergy information, please consult a qualified medical expert or your personal physician. Never rely solely on the advice of an AI language model for matters concerning your well-being._]')
    # st.caption('Built by [Snowflake](https://snowflake.com/) to demonstrate [Snowflake Arctic](https://www.snowflake.com/blog/arctic-open-and-efficient-foundation-language-models-snowflake). App hosted on [Streamlit Community Cloud](https://streamlit.io/cloud). Model hosted by [Replicate](https://replicate.com/snowflake/snowflake-arctic-instruct).')

# Store LLM-generated responses
INDEX = CHEF_LIST.index(st.session_state.personality_index)
MODE_INDEX = st.session_state.mode_option

if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": START_MESSAGES[INDEX][MODE_INDEX]}]
st.session_state.messages[0]["content"] = START_MESSAGES[INDEX][MODE_INDEX]

st.title("Talk to Chef 🍳")

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


# Function for generating Snowflake Arctic responses
# user_input is whether or not this response will depend on what the user has inputted (user_input = True)
#                           or if it just depends on the previous response from the ai (user_input = False)
def generate_arctic_response(given_prompt: str, temp: float, top: float, user_input: bool):
    prompt = []
    prompt.append("<|im_start|>system\n" + given_prompt + "<|im_end|>\n")
    if user_input:
        for dict_message in st.session_state.messages:
            if dict_message["role"] == "user":
                prompt.append("<|im_start|>user\n" + dict_message["content"] + "<|im_end|>")
            else:
                prompt.append("<|im_start|>assistant\n" + dict_message["content"] + "<|im_end|>")
    else:
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
                                  "temperature": temp,
                                  "top_p": top,
                                  }):
        yield str(event)

def replace_ingredient(ingredient: str):
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

# saves given recipe into session state
# recipe parameter: recipe object (defined in the Recipe.py file)
def save_recipe(recipe: Recipe):
    if "recipes" not in st.session_state:
        st.session_state.recipes = []

    st.session_state.recipes.append(recipe)

# clears all saved recipes, if any are saved
def clear_recipes():
    if "recipes" in st.session_state:
        st.session_state.recipes = []

# Generates the regular response and the ingredients list
def generate_display_info():
    global INDEX

    with container:
        with st.chat_message("assistant", avatar=icons["assistant"]):
            ingredients_response = generate_arctic_response(DEFAULT_INGREDIENTS_PROMPT[INDEX], temperature, top_p, True)
            method_response = generate_arctic_response(DEFAULT_METHOD_PROMPT[INDEX], temperature, top_p, False)

            name_msg = generate_arctic_response(DEFAULT_NAME_PROMPT, 0.1, 1, False)
            name = "".join(list(name_msg)).split("\n\n")[-1]

            st.header(name)

            icol, mcol = st.columns(2)
            with icol:
                st.subheader("Ingredients")
                ingredients_response = st.write_stream(ingredients_response)
            with mcol:
                st.subheader("Method")
                method_response = st.write_stream(method_response)

            full_response = "Ingredients:\n" + ingredients_response + "\n\nMethod:\n" + method_response

            # Add to history
            message = {"role": "assistant", "content": full_response}
            st.session_state.messages.append(message)

            # Get all the ingredients needed and put them into a list
            ingredients_msg = generate_arctic_response(DEFAULT_INGREDIENTS_LIST_PROMPT, 0.1, 1, False)
            ingredients_list = "".join(list(ingredients_msg))[1:].split(", ")

            # Make everything capitalized to stop issues and format nicer
            ingredient_list = [i.split(" (")[0].capitalize() for i in ingredients_list]

            # Check if all the ingredients are actually valid
            ingredients_list = []
            for ingredient in ingredient_list:
                if ingredient in INGREDIENT_LIST:
                    ingredients_list.append(ingredient)

            st.button("Save recipe", type="secondary", key="save", on_click=lambda recipe=Recipe(name, ingredients_list, method_response, full_response): save_recipe(recipe))

            if MODE_INDEX == 1:
                # Show the replace ingredients list
                num_cols = 3
                with st.expander("Replace ingredient:"):
                    icols = [i for i in st.columns(num_cols)]
                    index = 0
                    for ingredient in ingredients_list:
                        icols[index%num_cols].button(ingredient, type="secondary", key=ingredient, on_click=lambda ingredient=ingredient: replace_ingredient(ingredient))
                        index += 1

# User-provided prompt
prompt = st.chat_input(disabled=not replicate_api, placeholder=CHAT_INPUT_HINTS[MODE_INDEX])
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with container:
        with st.chat_message("user", avatar=icons["user"]):
            st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    generate_display_info()
