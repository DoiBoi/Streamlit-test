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

def reset_options():
    st.session_state.filters = {
        "veg": True,
        "dairy": True,
        "min time": 0,
        "max time": 120,
        "sort by": 0
        }

def delete_all_recipes():
    st.session_state.recipes = []

def remove_recipe(name: str):
    for index, recipe in enumerate(st.session_state.recipes):
        if recipe.name == name:
            st.session_state.recipes.pop(index)
            break

# Create sidebar
with st.sidebar:
    st.title('CHEF CHAT :cook:')

    st.header("Navigation")
    st.page_link("Talk_to_Chef.py", label="Talk to Chef", icon="🍳")

    st.divider()

    st.header("Filters")
    st.subheader("Categories")

    if "filters" not in st.session_state.keys():
        st.session_state.filters = {
            "veg": True,
            "dairy": True,
            "min time": 0,
            "max time": 120,
            "sort by": 0
            }

    veg = st.checkbox("Non-vegetarian", value=st.session_state.filters["veg"])
    dairy = st.checkbox("Dairy", value=st.session_state.filters["dairy"])
    min_time, max_time = st.select_slider("Total preparation & cook time (minutes)",
                                          options=[i for i in range(0, 121, 5)],
                                          value=[st.session_state.filters["min time"], st.session_state.filters["max time"]]
                                          )

    st.session_state.filters["veg"] = veg
    st.session_state.filters["dairy"] = dairy
    st.session_state.filters["min time"] = min_time
    st.session_state.filters["max time"] = max_time

    st.subheader("Sort by")
    sort = st.radio("Sort by", options=SORT_OPTIONS, index=st.session_state.filters["sort by"], label_visibility="collapsed")

    st.session_state.filters["sort by"] = SORT_OPTIONS.index(sort)

    st.button("Reset filters", type="secondary", on_click=reset_options)

    col1, col2 = st.columns(2)
    clear_all = col1.button("Clear all recipes", type="primary")

    if clear_all:
        clear_all = col2.button("Confirm delete", type="secondary", on_click=delete_all_recipes)

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
                        st.write(f"- {ingredient}")

                # Method section
                with rcol2:
                    st.subheader("Method")
                    for step in recipe.instructions:
                        st.write(step)

                pdf = recipe.make_pdf()

                st.download_button("Download recipe as PDF",
                                   mime="application/pdf",
                                   data=pdf,
                                   key="".join(random.choice(string.ascii_lowercase) for i in range(128)),
                                   file_name=f"{recipe.name} Recipe.pdf")
                st.button("Delete recipe",
                          type="primary",
                          key="".join(random.choice(string.ascii_lowercase) for i in range(128)),
                          on_click=lambda recipe=recipe: remove_recipe(recipe.name))
