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

    veg = st.checkbox("Non-vegetarian", value=st.session_state.filters["veg"], key="veg_filter")
    dairy = st.checkbox("Dairy", value=st.session_state.filters["dairy"], key="dairy_filter")
    min_time, max_time = st.select_slider("Total preparation & cook time (minutes)",
                                          options=[i for i in range(0, 121, 5)],
                                          value=[st.session_state.filters["min time"], st.session_state.filters["max time"]],
                                          key="time_filter")

    st.session_state.filters["veg"] = veg
    st.session_state.filters["dairy"] = dairy
    st.session_state.filters["min time"] = min_time
    st.session_state.filters["max time"] = max_time

    st.subheader("Sort by")
    sort = st.radio("Sort by", options=SORT_OPTIONS, index=st.session_state.filters["sort by"], label_visibility="collapsed", key="sort_by")

    st.session_state.filters["sort by"] = SORT_OPTIONS.index(sort)

    st.button("Reset filters", type="secondary", on_click=reset_options, use_container_width=True)

    col1, col2 = st.columns(2)
    clear_all = col1.button("Clear all recipes", type="primary", use_container_width=True)

    if clear_all:
        confirm_clear_all = col2.button("Confirm delete", type="secondary", on_click=delete_all_recipes, use_container_width=True)

    st.divider()

    st.caption(':red[_For any health-related concerns, including allergy information, please consult a qualified medical expert or your personal physician. Never rely solely on the advice of an AI language model for matters concerning your well-being._]')

# This is used to check that all the ingredients detected are valid
# https://github.com/schollz/food-identicon/blob/master/ingredients.txt
INGREDIENT_LIST = []
with open("resources/ingredients_list.txt", mode="r") as file:
    lines = file.read().split("\n")
    INGREDIENT_LIST = [i.capitalize() for i in lines]

# adapted from https://www.geeksforgeeks.org/quick-sort/
# Function to find the partition position
def partition(array, low, high):

    # Choose the rightmost element as pivot
    pivot = array[high]

    # Pointer for greater element
    i = low - 1

    # Traverse through all elements
    # compare each element with pivot
    for j in range(low, high):
        if array[j].num_of_ingredients <= pivot.num_of_ingredients:

            # If element smaller than pivot is found
            # swap it with the greater element pointed by i
            i = i + 1

            # Swapping element at i with element at j
            (array[i], array[j]) = (array[j], array[i])

    # Swap the pivot element with
    # the greater element specified by i
    (array[i + 1], array[high]) = (array[high], array[i + 1])

    # Return the position from where partition is done
    return i + 1

# adapted from https://www.geeksforgeeks.org/quick-sort/
# Function to perform quicksort
def quicksort(array, low, high):
    if low < high:

        # Find pivot element such that
        # element smaller than pivot are on the left
        # element greater than pivot are on the right
        pi = partition(array, low, high)

        # Recursive call on the left of pivot
        quicksort(array, low, pi - 1)

        # Recursive call on the right of pivot
        quicksort(array, pi + 1, high)

# use quicksort to sort recipe list by number of ingredients
def sort_by_ingredients():
    quicksort(st.session_state.recipes, 0, len(st.session_state.recipes) - 1)

# create container for saved recipe viewer section
viewing_container = st.container()
with viewing_container:
    if ("recipes" not in st.session_state) or (st.session_state.recipes == []):
        st.write("There's nothing to show here! Save a recipe to see it here.")
    else:
        if sort == "Number of ingredients":
            sort_by_ingredients()
        for recipe in st.session_state.recipes:
            with st.expander(recipe.name):
                st.header(recipe.name)
                st.subheader("Tags")

                num_cols = 3
                tcols = [i for i in st.columns(num_cols)]
                index = 0
                for tag in recipe.tags:
                    if tag.capitalize() not in INGREDIENT_LIST:
                        tcols[index%num_cols].button(tag, use_container_width=True, type="secondary", key="".join(random.choice(string.ascii_lowercase) for i in range(128)))
                        index += 1

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

                rbcol1, rbcol2 = st.columns(2)
                rbcol1.download_button("Download recipe as PDF",
                                   mime="application/pdf",
                                   data=pdf,
                                   key="".join(random.choice(string.ascii_lowercase) for i in range(128)),
                                   file_name=f"{recipe.name} Recipe.pdf",
                                   use_container_width=True)
                rbcol2.button("Delete recipe",
                          type="primary",
                          key="".join(random.choice(string.ascii_lowercase) for i in range(128)),
                          on_click=lambda recipe=recipe: remove_recipe(recipe.name),
                          use_container_width=True)
