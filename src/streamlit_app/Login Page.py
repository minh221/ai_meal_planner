import streamlit as st
import requests
import time
from utils import get_base64_image


# API endpoint configuration
API_URL = "http://127.0.0.1:8000/check-user-login"

# Check if user credentials are valid using FastAPI
def check_user_login(user_id, password):
    try:
        response = requests.post(API_URL, json={"user_id": user_id, "password": password})
        if response.status_code == 200:
            data = response.json()
            return data.get("exists", False), data.get("message", "")
    except Exception as e:
        st.error(f"Error connecting to the FastAPI backend: {e}")
        return False, str(e)
    

def apply_login_styles(image_path="assets/background.jpg", css_file="src/streamlit_app/styles/login_style.css"):
    """Apply login page styles with background image and CSS file."""
    img_base64 = get_base64_image(image_path)
    
    # Use gradient background if image not found
    background_style = f"url('data:image/jpeg;base64,{img_base64}')" if img_base64 else "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
    
    # Load CSS from file
    with open(css_file) as f:
        css_content = f.read()
    
    # Apply background and CSS
    st.markdown(
        f"""
        <style>
            /* Background styling */
            .stApp {{
                background: {background_style};
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
            }}
            
            {css_content}
        </style>
        """,
        unsafe_allow_html=True,
    )

# Main app
def main():
    apply_login_styles()
    
    # Create centered login container
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        # Title with emojis - these will now be inside the styled column
        st.markdown('<div class="title">Meal Planner</div>', unsafe_allow_html=True)
        st.markdown('<div class="emoji-row">🍣 🥗 🍹</div>', unsafe_allow_html=True)
        st.markdown('<div class="description">Plan your perfect meals with ease</div>', unsafe_allow_html=True)

        # Input fields with better UX
        user_id = st.text_input(
            "Username",
            placeholder="Enter your username",
            key="username",
            help="Your unique user identifier"
        )
        
        password = st.text_input(
            "Password",
            placeholder="Enter your password",
            type="password",
            key="password",
            help="Your secure password"
        )

        # Container for custom messages
        message_placeholder = st.empty()

        # Login button
        if st.button("🚀 Let's Get Started"):
            if user_id and password:
                # Check if the user credentials are valid
                with st.spinner("🔍 Verifying credentials..."):
                    time.sleep(1)
                    is_valid, message = check_user_login(user_id, password)
                    
                    if is_valid:
                        st.session_state.user_id = user_id
                        message_placeholder.markdown(
                            f'<div class="message-text message-success">{message}</div>',
                            unsafe_allow_html=True
                        )
                        with st.spinner("Redirecting to your meal planner..."):
                            time.sleep(1.5)
                        st.switch_page("pages/Home Page.py")
                    else:
                        message_placeholder.markdown(
                            f'<div class="message-text message-error">{message}</div>',
                            unsafe_allow_html=True
                        )
            else:
                message_placeholder.markdown(
                    '<div class="message-text message-error">Please enter both username and password.</div>',
                    unsafe_allow_html=True
                )
        
        # Optional: Add "Forgot Password" link
        st.markdown(
            '<div class="footer-text">Need help? Contact support</div>',
            unsafe_allow_html=True
        )
        
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    if "user_id" not in st.session_state:
        main()
    else:
        # Welcome screen after authentication
        apply_login_styles()
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(f'''<div class="welcome-title">👋 Welcome back, 
                        {st.session_state.user_id}!</div>''', unsafe_allow_html=True)
            st.markdown('<div class="welcome-subtitle">Ready to plan some delicious meals?</div>', unsafe_allow_html=True)
            
            if st.button("🏠 Go to Meal Planner"):
                st.switch_page("pages/Home Page.py")
            
            st.markdown('</div>', unsafe_allow_html=True)