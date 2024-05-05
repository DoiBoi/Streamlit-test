import string
import streamlit as st
import replicate
import os
from transformers import AutoTokenizer
import random

st.set_page_config(
    page_title="Saved Recipes - Chef Chat",
    page_icon="📃",
)

st.title("Saved Recipes 📃")

SORT_OPTIONS = ["Number of ingredients", "Preparation time"]

# Create sidebar
with st.sidebar:
    st.title('CHEF CHAT :cook:')

    st.header("Navigation")
    st.page_link("Talk_to_Chef.py", label="Talk to Chef", icon="🍳")

    st.divider()

    st.header("Filters")
    st.subheader("Categories")
    veg = st.checkbox("Non-vegetarian", value=True)
    dairy = st.checkbox("Dairy", value=True)
    min_time, max_time = st.select_slider("Total preparation & cook time (minutes)", options=[i for i in range(0, 121, 5)], value=[0, 120])

    st.subheader("Sort by")
    st.radio("Sort by", options=SORT_OPTIONS, label_visibility="collapsed")

    st.divider()

    st.caption(':red[_For any health-related concerns, including allergy information, please consult a qualified medical expert or your personal physician. Never rely solely on the advice of an AI language model for matters concerning your well-being._]')

# This is used to check that all the ingredients detected are valid
# https://github.com/schollz/food-identicon/blob/master/ingredients.txt
INGREDIENT_LIST = []
with open("resources/ingredients_list.txt", mode="r") as file:
    lines = file.read().split("\n")
    INGREDIENT_LIST = [i.capitalize() for i in lines]


# create container for saved recipe viewer section
viewing_container = st.container()
with viewing_container:
    if "recipes" not in st.session_state:
        st.write("There's nothing to show here! Save a recipe to see it here.")
    elif st.session_state.recipes == []:
        st.write("There's nothing to show here! Save a recipe to see it here.")
    else:
        for recipe in st.session_state.recipes:
            with st.expander(recipe.name):
                st.header(recipe.name)
                rcol1, rcol2 = st.columns(2)

                # Ingredients section
                with rcol1:
                    st.subheader("Ingredients")
                    for ingredient in recipe.ingredients:
                        if ingredient in INGREDIENT_LIST:
                            st.write(f"- {ingredient}")

                # Method section
                with rcol2:
                    st.subheader("Method")
                    for step in recipe.instructions:
                        st.write(step)

                st.button("Download recipe as PDF", key="".join(random.choice(string.lowercase) for i in range(128)))
                st.button("Delete recipe", key="".join(random.choice(string.lowercase) for i in range(128)))
