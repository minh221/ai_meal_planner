import streamlit as st
import requests
import json
import pandas as pd
from typing import List, Dict, Any
import time
from utils import get_base64_image

# API endpoint configuration
API_URL = "http://127.0.0.1:8000"

# Initialize session state for storing generated meal plan
if "meal_plan_data" not in st.session_state:
    st.session_state.meal_plan_data = None


def apply_main_page_styles(image_path="assets/background.jpg", css_file="src/streamlit_app/styles/home_style.css"):
    """Apply main page styles with banner image and CSS file."""
    img_base64 = get_base64_image(image_path)
    
    # Create banner HTML if image exists
    if img_base64:
        banner_html = f"""
            <div style="
                width: 100%;
                height: 250px;
                background: url('data:image/jpeg;base64,{img_base64}');
                background-size: cover;
                background-position: center;
                border-radius: 20px;
                margin-bottom: 2rem;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
            "></div>
        """
    else:
        # Fallback to gradient banner
        banner_html = """
            <div style="
                width: 100%;
                height: 250px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 0 0 20px 20px;
                margin-bottom: 2rem;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
            "></div>
        """
    
    # Load CSS from file
    try:
        with open(css_file) as f:
            css_content = f.read()
    except FileNotFoundError:
        st.error(f"CSS file not found: {css_file}")
        css_content = ""
    
    # Apply CSS
    st.markdown(
        f"""
        <style>
            {css_content}
        </style>
        """,
        unsafe_allow_html=True,
    )
    
    # Display banner
    st.markdown(banner_html, unsafe_allow_html=True)


def display_meal_plan(meal_plan_data):
    """Display the meal plan based on the provided data structure"""
    
    try:
        if not isinstance(meal_plan_data, dict):
            # Try to convert from string if needed
            if isinstance(meal_plan_data, str):
                if meal_plan_data.startswith("```json"):
                    json_string = meal_plan_data[7:-3]
                else:
                    json_string = meal_plan_data
                
                meal_plan_data = json.loads(json_string)
            else:
                st.error("Invalid meal plan data format")
                return
        
        # Display header
        st.markdown('<div class="meal-card">', unsafe_allow_html=True)
        st.subheader("🧑‍🍳 Your Personalized Meal Plan")
        
        # Display general advice if available
        if "general_advice" in meal_plan_data:
            st.info(meal_plan_data["general_advice"])
        
        # Display dietary accommodations if available
        if "dietary_accommodations" in meal_plan_data and meal_plan_data["dietary_accommodations"]:
            st.markdown("<h4>🥗 Dietary Accommodations</h4>", unsafe_allow_html=True)
            with st.expander("View advices", expanded=True):
                for diet_type, description in meal_plan_data["dietary_accommodations"].items():
                    st.markdown(f"**{diet_type}**: {description}")
        
        # Display health considerations if available
        if "health_condition_considerations" in meal_plan_data and meal_plan_data["health_condition_considerations"]:
            st.markdown("<h4>❤️ Health Considerations</h4>", unsafe_allow_html=True)
            with st.expander("View advices", expanded=True):
                for condition, details in meal_plan_data["health_condition_considerations"].items():
                    st.markdown(f"**{condition}**: {details}")
        
        # Display daily meal plans
        daily_plans = meal_plan_data.get("meal_plan", [])
        
        for day_plan in daily_plans:
            day_num = day_plan.get("day", 0)
            meals = day_plan.get("meals", [])
            daily_advice = day_plan.get("daily_advice", "")
            
            st.markdown(f'<div class="day-header">📅 Day {day_num}</div>', unsafe_allow_html=True)
            with st.expander(f"View meals", expanded=day_num == 1):
                
                # Display daily advice if available
                if daily_advice:
                    st.info(daily_advice)
                
                # Display each meal
                for meal in meals:
                    meal_name = meal.get("name", "")
                    foods = meal.get("foods", [])
                    
                    st.markdown(f'<div class="meal-name">{meal_name}</div>', unsafe_allow_html=True)
                    
                    # Process each food item
                    for food in foods:
                        if isinstance(food, dict):
                            food_name = food.get("name", "")
                            portion = food.get("portion_size", "")
                            preparation = food.get("preparation", "")
                            calories = food.get("calories", 0)
                            protein = food.get("protein", 0)
                            fat = food.get("fat", 0)
                            carbs = food.get("carbs", 0)
                            
                            st.markdown('<div class="food-item">', unsafe_allow_html=True)
                            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                            
                            with col1:
                                st.markdown(f"**{food_name}**")
                            
                            with col2:
                                st.markdown(f"*{portion}*")
                            
                            with col3:
                                st.markdown(f"**Cal:** {calories} kcal")
                                st.markdown(f"**P:** {protein}g | **F:** {fat}g | **C:** {carbs}g")
                            
                            with col4:
                                if preparation:
                                    st.markdown(f"*{preparation}*")
                            
                            st.markdown('</div>', unsafe_allow_html=True)
                        else:
                            st.markdown(f"- {food}")
                    
                    st.markdown("---")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Error displaying meal plan: {str(e)}")
        st.write("Raw meal plan data:")
        st.write(meal_plan_data)


def save_meal_plan():
    """Save the meal plan to the database through FastAPI"""
    if not st.session_state.meal_plan_data:
        st.error("No meal plan to save")
        return
    
    with st.spinner("Saving your meal plan..."):
        try:
            payload = {
                "user_id": st.session_state.user_id,
                "meal_plan": str(st.session_state.meal_plan_data)
            }
            
            response = requests.post(f"{API_URL}/save-meal-plan", json=payload)
            
            if response.status_code == 200:
                st.success("✅ Meal plan saved successfully!")
                st.balloons()
            else:
                st.error(f"❌ Error saving meal plan: {response.json().get('detail', 'Unknown error')}")
        
        except Exception as e:
            st.error(f"⚠️ Error connecting to server: {str(e)}")


# Function to fetch user data
def fetch_user_data(user_id):
    response = requests.get(f"{API_URL}/get-user-data/{user_id}")
    if response.status_code == 200:
        return response.json()
    else:
        return None


# Function to toggle edit mode
def toggle_edit_mode():
    st.session_state.editable = not st.session_state.editable


# Main app
st.set_page_config(page_title="Personalized Meal Planner", layout="wide")

# Apply custom styles
apply_main_page_styles()

st.title("🍽️ Personalized Meal Planner")
st.markdown("<h1 style='font-size:30px'>🌮🌯🥗🍣🍜🍝🍱🥝🥑🥥🍳</h1>", unsafe_allow_html=True)

if "user_id" in st.session_state:
    user_id = st.session_state.user_id

    # Initialize session state for editable mode if it doesn't exist
    if 'editable' not in st.session_state:
        st.session_state.editable = False

    # Fetch user data from the backend (if available)
    user_data = fetch_user_data(user_id)
    print("User_data............................", user_data)

    # If no user data is returned, display a friendly message and allow the user to fill in their profile
    if not user_data:
        st.session_state.editable = True
        st.warning("It seems like you're using the app for the first time! Please fill out your profile.")
        user_data = {
            "number_of_days": '1',
            "age": 0,
            "gender": "Male",
            "height_cm": 0.0,
            "weight_kg": 0.0,
            "health_conditions": "",
            "dietary_preferences": [],
            "allergies": "",
            "nutritional_goals": [],
            "food_preferences": "",
        }
        
    # Input form
    with st.form("meal_plan_form"):
        st.subheader("🩺 Your Health Profile")
        with st.expander("View details", expanded=st.session_state.editable):

            col1, col2 = st.columns(2)
            
            with col1:
                age = st.number_input(
                    "Age", 
                    min_value=0, 
                    max_value=150, 
                    value=user_data['age'],
                    disabled=not st.session_state.editable
                )
                
                gender = st.selectbox(
                    "Gender",
                    options=["Male", "Female"],
                    index=["Male", "Female"].index(user_data['gender']),
                    disabled=not st.session_state.editable
                )
                
                weight = st.number_input(
                    "Weight (kg)", 
                    min_value=0.0, 
                    value=user_data['weight_kg'],
                    disabled=not st.session_state.editable
                )
                
                height = st.number_input(
                    "Height (cm)", 
                    min_value=0.0, 
                    value=user_data['height_cm'],
                    disabled=not st.session_state.editable
                )

                number_of_days = st.selectbox(
                    "How many days of meals do you want?", 
                    options=["1", "3", "5", "7"], 
                    index=["1", "3", "5", "7"].index(user_data['number_of_days']),
                    disabled=not st.session_state.editable
                )

            with col2:
                health_conditions = st.text_input(
                    "Health conditions (comma-separated)", 
                    placeholder="Do you have any special condition? e.g., diabetes, heart disease", 
                    value=user_data['health_conditions'],
                    disabled=not st.session_state.editable
                )
                
                dietary_preferences = st.multiselect(
                    "Dietary Preferences",
                    options=[
                        "Vegetarian", "Vegan", "Pescatarian", "Keto", "Paleo", 
                        "Mediterranean", "Gluten-Free", "Dairy-Free", "Halal", 
                        "Kosher", "None", ""
                    ],
                    default=user_data['dietary_preferences'],
                    disabled=not st.session_state.editable
                )

                allergies = st.text_input(
                    "Allergies", 
                    placeholder="e.g., shellfish, peanuts", 
                    value=user_data['allergies'],
                    disabled=not st.session_state.editable
                )
                
                nutritional_goals = st.multiselect(
                    "Nutritional Goals",
                    options=[
                        "Weight Loss", "Weight Gain", "Muscle Building", "High Protein", 
                        "High Fiber", "Low Sodium", "Low Sugar", "Low Carb", "Low Fat", 
                        "Heart Health", "Diabetic-Friendly", "Anti-Inflammatory", "Brain Health", 
                        "Improved Digestion", "Balanced Diet", "None", ""
                    ],
                    default=user_data['nutritional_goals'],
                    disabled=not st.session_state.editable
                )

                food_preferences = st.text_area(
                    "Food Preferences", 
                    value=user_data['food_preferences'],
                    disabled=not st.session_state.editable
                )

            # Create a row of buttons at the bottom
            button_col1, button_col2 = st.columns(2)
            
            with button_col1:
                save_button = st.form_submit_button("Save Changes", disabled=not st.session_state.editable)
            
            with button_col2:
                edit_button = st.form_submit_button(
                    "Cancel Edit" if st.session_state.editable else "Edit Profile",
                    type="secondary"
                )
            
            # Handle button clicks
            if save_button and st.session_state.editable:
                data_to_save = {
                    "user_id": user_id,
                    "number_of_days": number_of_days,
                    "age": age,
                    "gender": gender,
                    "height_cm": height,
                    "weight_kg": weight,
                    "health_conditions": health_conditions,
                    "dietary_preferences": ",".join(dietary_preferences),
                    "allergies": allergies,
                    "nutritional_goals": ",".join(nutritional_goals),
                    "food_preferences": food_preferences
                }

                print(data_to_save)
                
                try:
                    save_response = requests.post(f"{API_URL}/save-user-data", json=data_to_save)
                    save_response.raise_for_status()
                    st.success("Your information has been saved!")
                    st.session_state.editable = False
                    st.rerun()
                except requests.exceptions.RequestException as e:
                    st.error(f"Error saving data: {e}")
                    
            if edit_button:
                toggle_edit_mode()
                st.rerun()

    # Action buttons
    col1, col2 = st.columns([1, 1])
    with col1:
        generate_button = st.button("🎨 Generate Meal Plan")
    with col2:
        to_trending_button = st.button("🔥 View Trending Recipes")

    if to_trending_button:
        st.switch_page("pages/Trending.py")
    
    # Process form submission
    if generate_button:
        with st.spinner("Generating your personalized meal plan..."):
            health_conditions_list = [item.strip().lower() for item in health_conditions.split(",") if item.strip()]
            
            payload = {
                "user_id": user_id,
                "number_of_days": number_of_days,
                "age": age,
                "gender": gender,
                "height_cm": height,
                "weight_kg": weight,
                "health_conditions": health_conditions,
                "dietary_preferences": str(dietary_preferences),
                "allergies": allergies,
                "nutritional_goals": str(nutritional_goals),
                "food_preferences": food_preferences
            }
            
            try:
                response = requests.post(f"{API_URL}/generate-meal-plan", json=payload)
                
                if response.status_code == 200:
                    response = response.json()
                    st.session_state.meal_plan_data = response.get("raw", response)
                    st.success("✅ Meal plan generated successfully!")
                else:
                    st.error(f"❌ Error: {response.json().get('detail', 'Unknown error')}")
            except Exception as e:
                st.error(f"⚠️ Could not connect to backend: {str(e)}")

    # Evaluate meal plan button
    if st.session_state.meal_plan_data != None:
        if st.button("📊 Evaluate Meal Plan"):
            with st.spinner("Evaluating the meal plan..."):
                health_conditions_list = [item.strip().lower() for item in health_conditions.split(",") if item.strip()]
                
                payload = {
                    "user_id": user_id,
                    "age": age,
                    "gender": gender,
                    "height_cm": height,
                    "weight_kg": weight,
                    "health_conditions": health_conditions,
                    "dietary_preferences": str(dietary_preferences),
                    "allergies": allergies,
                    "nutritional_goals": str(nutritional_goals),
                    "food_preferences": food_preferences,
                    "meal_plan_json": str(st.session_state.meal_plan_data)
                }
                
                try:
                    response = requests.post(f"{API_URL}/evaluate-meal-plan", json=payload)
                    
                    if response.status_code == 200:
                        response = response.json()
                        st.session_state.evaluation = response.get("raw", response)
                        st.success("✅ Meal plan evaluated successfully!")
                    else:
                        st.error(f"❌ Error: {response.json().get('detail', 'Unknown error')}")
                except Exception as e:
                    st.error(f"⚠️ Could not connect to backend: {str(e)}")

    # Display meal plan section
    if st.session_state.meal_plan_data:
        st.markdown("---")
        display_meal_plan(st.session_state.meal_plan_data)
        
        # Save button and feedback section
        col1, col2 = st.columns([1, 3])
        
        with col1:
            if st.button("💾 Save Meal Plan"):
                save_meal_plan()
        
        with col2:
            st.markdown('<div class="meal-card">', unsafe_allow_html=True)
            st.markdown("#### 💬 Feedback")
            feedback = st.text_input("Not happy with the meal? Give us your feedback!",
                                    placeholder="e.g., 'less carbs', 'no meat', 'more spicy'")

            if st.button("🔄 Generate New Meal Plan"):
                st.info("This feature is not yet implemented. Please check back later!")
            st.markdown('</div>', unsafe_allow_html=True)

else:
    # Not logged in view
    st.markdown('<div class="not-logged-in-card">', unsafe_allow_html=True)
    st.info("👋 Log in or create an account to start your meal planner.")
    if st.button("Go to Login"):
        st.switch_page("Login Page.py")
    st.markdown('</div>', unsafe_allow_html=True)