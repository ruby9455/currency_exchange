import streamlit as st
from functions.ui.auth_page import login_page, init_auth_state
from components.navigation import nav_bar

st.set_page_config(
    page_title="Login - Currency Exchange",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Initialize session state for navigation
if "is_logged_in" not in st.session_state:
    st.session_state.is_logged_in = False
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

# Initialize auth state
init_auth_state()

# Display navigation bar
nav_bar()

# Main content
login_page()

# Update navigation state when user logs in
if st.session_state.get("logged_in", False):
    # Set is_logged_in for navigation
    st.session_state.is_logged_in = True
    
    # Check if user is admin for navigation permissions
    if "logged_in_user" in st.session_state:
        from functions.ui.auth_ui import get_user_collection_ui
        users_collection = get_user_collection_ui()
        user = users_collection.find_one({"username": st.session_state.logged_in_user})
        if user and user.get("role") == "admin":
            st.session_state.is_admin = True
    
    # Redirect to main page
    st.rerun()