import streamlit as st
import replicate
import os
from transformers import AutoTokenizer

# Set assistant icon to Snowflake logo
icons = {"assistant": "./chef-hat.svg", "user": "👨‍🍳"}

DEFAULT_PROMPT = ["You are a helpful chef",
                  "You are a famous, condescending chef defined by his fiery temper, aggressive behaviour, strict demeanour, and frequent usage of profane language, while making blunt, critical, and controversial comments, including insults and sardonic wisecracks about contestants and their cooking abilities." ,
                  "You are a chef known for being a Gen X glam rocker and your energy is over the top with a flashy persona that shines through in everything you do.",
                  "You are a famous chef known for being very laid back, joyful, and chill, and sometimes you use british slangs to praise whatever you're making by taking about how it looks, tastes, or smells."]

CHEF_LIST = ["Default","Gordon Ramsay", "Guy Fieri", "Jamie Oliver"]

INGREDIENTS_LIST = []

# App title
st.set_page_config(page_title="Personal Chef", page_icon="👨‍🍳")

# Replicate Credentials
with st.sidebar:
    st.title('PERSONAL CHEF :cook:')
    if 'REPLICATE_API_TOKEN' in st.secrets:
        #st.success('API token loaded!', icon='✅')
        replicate_api = st.secrets['REPLICATE_API_TOKEN']
    else:
        replicate_api = st.text_input('Enter Replicate API token:', type='password')
        if not (replicate_api.startswith('r8_') and len(replicate_api)==40):
            st.warning('Please enter your Replicate API token.', icon='⚠️')
            st.markdown("**Don't have an API token?** Head over to [Replicate](https://replicate.com) to sign up for one.")
        #else:
        #    st.success('API token loaded!', icon='✅')

    os.environ['REPLICATE_API_TOKEN'] = replicate_api

    st.subheader("Options")
    temperature = 3     # This is the "creativity" of the response (higher is more creative, less is predictable)
    top_p = 0.1         # This is the next token's probability threshold (lower makes more sense)
    #! We remove these sliders once we tune it
    # temperature = st.sidebar.slider('temperature', min_value=0.01, max_value=5.0, value=3, step=0.01)
    # top_p = st.sidebar.slider('top_p', min_value=0.01, max_value=1.0, value=0.1, step=0.01)

    # Chef personality selector
    option = st.sidebar.selectbox('Please select a chef:', CHEF_LIST)
    index = CHEF_LIST.index(option)

start_message = "Hi. I'm an language model trained to be your personal chef! Ask me about any recipe or anything food related."

# Store LLM-generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": start_message}]

# Create container for messages area
container = st.container()

# Display or clear chat messages
for message in st.session_state.messages:
    with container:
        with st.chat_message(message["role"], avatar=icons[message["role"]]):
            st.write(message["content"])

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": start_message}]
st.sidebar.button(':red[Clear chat]', on_click=clear_chat_history)

st.sidebar.divider()

st.sidebar.subheader("About")
st.sidebar.caption('This chat bot is designed to give you recipe suggestions based on ingredients you have. To use it, write each of your ingredients separated by commas.')
st.sidebar.caption("Here's an example message:")
st.sidebar.caption('Eggs, flour, milk, vanilla extract, baking soda, baking powder, butter, sugar, salt.')

st.sidebar.divider()

st.sidebar.caption(':red[_For any health-related concerns, including allergy information, please consult a qualified medical expert or your personal physician. Never rely solely on the advice of an AI language model for matters concerning your well-being._]')
st.sidebar.caption('Built by [Snowflake](https://snowflake.com/) to demonstrate [Snowflake Arctic](https://www.snowflake.com/blog/arctic-open-and-efficient-foundation-language-models-snowflake). App hosted on [Streamlit Community Cloud](https://streamlit.io/cloud). Model hosted by [Replicate](https://replicate.com/snowflake/snowflake-arctic-instruct).')


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
    prompt.append("<|im_start|>system\n" + DEFAULT_PROMPT[index] + "Additionally, the user will give a list of ingredients and you are tasked to provide the user a recipe," +
                  " please restrain the recipe to what the user has listed. Even if it is just one ingredient, please try to come up with a recipe. " + 
                  "Please put the ingredients under 'Ingredients' and the instructions in 'Instruction'<|im_end|>\n")
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
        st.button(':red[Clear chat]', on_click=clear_chat_history, key="clear_chat_history")
        st.stop()

    for event in replicate.stream("snowflake/snowflake-arctic-instruct",
                           input={"prompt": prompt_str,
                                  "prompt_template": r"{prompt}",
                                  "temperature": temperature,
                                  "top_p": top_p,
                                  }):
        yield str(event)

# User-provided prompt
prompt = st.chat_input(disabled=not replicate_api, placeholder="Enter your ingredients here")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with container:
        with st.chat_message("user", avatar="👨‍🍳"):
            st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with container:
        with st.chat_message("assistant", avatar="./chef-hat.svg"):
            response = generate_arctic_response()
            full_response = st.write_stream(response)
    message = {"role": "assistant", "content": full_response}
    st.session_state.messages.append(message)