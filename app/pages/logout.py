import streamlit as st
from functions.ui.auth_page import logout_page
from components.navigation import nav_bar

st.set_page_config(
    page_title="Logout - Currency Exchange",
    page_icon="🔓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Initialize session state for navigation
if "is_logged_in" not in st.session_state:
    st.session_state.is_logged_in = False
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

# Display navigation bar
nav_bar()

# Handle logout
if st.session_state.get("logged_in", False):
    logout_page()
    # Reset navigation state
    st.session_state.is_logged_in = False
    st.session_state.is_admin = False
    # Redirect to main page
    st.rerun()
else:
    st.title("Already Logged Out")
    st.info("You are not currently logged in.")
    if st.button("Go to Login Page"):
        st.switch_page("pages/login.py")