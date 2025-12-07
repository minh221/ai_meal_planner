import streamlit as st
import sqlite3
import pandas as pd
import requests  # For sending requests to FastAPI

# Define FastAPI server URL
API_URL = "http://localhost:8000"  # Update this to your FastAPI server URL


st.set_page_config("Trending", layout="wide")
st.title("Checkout the latest recipes!")
st.markdown("<h1 style='font-size:50px'>🍕🍔🍟🌮🌯🥗🍣🍜🍝🍱🍩🍪🧁🍰🎂🍿🍇🍉🍊🍌🍎🍒🥝🥑🥥🍍🍓🥞🥐🍞🧀🍳</h1>", unsafe_allow_html=True)

if "user_id" in st.session_state:
    user_id = st.session_state["user_id"]
    
    # Fetch latest recipes from FastAPI
    try:
        latest_recipes_response = requests.get(f"{API_URL}/recipes/latest")
        if latest_recipes_response.status_code == 200:
            recipes = pd.DataFrame(latest_recipes_response.json())
        else:
            st.error("Failed to fetch latest recipes from API")
            recipes = pd.DataFrame()
    except Exception as e:
        st.error(f"Error connecting to FastAPI: {str(e)}")
        recipes = pd.DataFrame()
    
    # Fetch user's favorites to check which recipes are already favorites
    try:
        user_favorites_response = requests.get(f"{API_URL}/favorites/user/{user_id}")
        if user_favorites_response.status_code == 200:
            favorite_recipe_ids = [fav["recipe_id"] for fav in user_favorites_response.json()]
        else:
            st.warning("Failed to fetch favorites status")
            favorite_recipe_ids = []
    except Exception as e:
        st.warning(f"Error fetching favorites: {str(e)}")
        favorite_recipe_ids = []

    # Display latest recipes
    if not recipes.empty:
        for _, r in recipes.iterrows():
            recipe_id = r["id"]
            with st.container():
                st.subheader(r["title"])
                st.markdown(f"**Type:** {r['type']} | **Diet:** {r['diet']}")
                st.markdown(f"**Calories:** {r['calories']} kcal | **Protein:** {r['protein']}g | **Fat:** {r['fat']}g | **Carbs:** {r['carbs']}g")
                st.markdown(f"**Ingredients:** {r['ingredients']}")
                st.markdown(f"[🔗 Instructions]({r['instructions']})")

                # Show appropriate favorite button based on whether recipe is already a favorite
                if recipe_id in favorite_recipe_ids:
                    if st.button("Remove from Favorites", key=f"remove-{recipe_id}"):
                        response = requests.delete(f"{API_URL}/favorites/remove", json={
                            "user_id": user_id,
                            "recipe_id": recipe_id
                        })
                        if response.status_code == 200:
                            st.success("Removed from favorites!")
                            st.rerun()  # Refresh the page
                        else:
                            st.error("Failed to remove from favorites.")
                else:
                    if st.button("Add to Favorites", key=f"fav-{recipe_id}"):
                        response = requests.post(f"{API_URL}/favorites/add", json={
                            "user_id": user_id,
                            "recipe_id": recipe_id
                        })
                        if response.status_code == 200:
                            st.success("Added to favorites!")
                            st.rerun()  # Refresh the page
                        else:
                            st.error("Failed to add to favorites.")
    else:
        st.info("No recipes available.")

    st.markdown("---")
    st.subheader("Your Favorite Recipes")

    # Fetch user's favorite recipes from FastAPI
    try:
        favorites_response = requests.get(f"{API_URL}/favorites/user/{user_id}/recipes")
        if favorites_response.status_code == 200:
            favorite_recipes = pd.DataFrame(favorites_response.json())
            
            if not favorite_recipes.empty:
                for _, fav in favorite_recipes.iterrows():
                    with st.expander(fav["title"], expanded=False):
                        with st.container():
                            st.subheader(fav["title"])
                            st.markdown(f"**Type:** {fav['type']} | **Diet:** {fav['diet']}")
                            st.markdown(f"**Calories:** {fav['calories']} kcal | **Protein:** {fav['protein']}g | **Fat:** {fav['fat']}g | **Carbs:** {fav['carbs']}g")
                            st.markdown(f"**Ingredients:** {fav['ingredients']}")
                            st.markdown(f"[🔗 Instructions]({fav['instructions']})")
                            
                            # Button to remove from favorites
                            if st.button("Remove from Favorites", key=f"remove-fav-{fav['id']}"):
                                response = requests.delete(f"{API_URL}/favorites/remove", json={
                                    "user_id": user_id,
                                    "recipe_id": fav["id"]
                                })
                                if response.status_code == 200:
                                    st.success("Removed from favorites!")
                                    st.rerun()  # Refresh the page to update the favorites list
                                else:
                                    st.error("Failed to remove from favorites.")
            else:
                st.info("No favorites yet.")
        else:
            st.error("Failed to fetch favorite recipes from API")
    except Exception as e:
        st.error(f"Error fetching favorite recipes: {str(e)}")
        st.info("No favorites available.")
else:
    st.info("Log in or create an account to view recipes.")
