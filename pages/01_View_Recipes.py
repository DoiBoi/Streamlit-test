import streamlit as st
import replicate
import os
from transformers import AutoTokenizer
import re
from Talk_to_Chef import INGREDIENT_LIST

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

st.write("Saved Recipes")

# st.markdown(
#     """
#     Streamlit is an open-source app framework built specifically for
#     Machine Learning and Data Science projects.
#     **👈 Select a demo from the sidebar** to see some examples
#     of what Streamlit can do!
#     ### Want to learn more?
#     - Check out [streamlit.io](https://streamlit.io)
#     - Jump into our [documentation](https://docs.streamlit.io)
#     - Ask a question in our [community
#         forums](https://discuss.streamlit.io)
#     ### See more complex demos
#     - Use a neural net to [analyze the Udacity Self-driving Car Image
#         Dataset](https://github.com/streamlit/demo-self-driving)
#     - Explore a [New York City rideshare dataset](https://github.com/streamlit/demo-uber-nyc-pickups)
# """
# )

# create container for saved recipe viewer section
viewing_container = st.container()
with viewing_container: 
    if "recipes" not in st.session_state:
        st.write("There's nothing here!")

    elif st.session_state.recipes == []:
        st.write("There's nothing here!")
        
    else:
        for recipe in st.session_state.recipes:
            st.write(recipe.name)

            with st.expander("Ingredients"):
                for ingredient in recipe.ingredients:
                    if ingredient in INGREDIENT_LIST:
                        st.write(ingredient)
