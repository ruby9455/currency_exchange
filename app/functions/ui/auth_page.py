import streamlit as st
from functions.ui.auth_ui import authenticate_user_ui, check_user_role_ui

def init_auth_state():
    """Initialize authentication state variables in session state"""
    if "is_logged_in" not in st.session_state: 
        st.session_state.is_logged_in = False
    if "login_id" not in st.session_state: 
        st.session_state.login_id = ""
    if "is_admin" not in st.session_state: 
        st.session_state.is_admin = False

def login_page():
    """Render the login page with username and password fields"""
    st.title("Login Page")
    st.text_input("Enter Login ID", key="login_id")
    st.text_input("Enter Password", type="password", key="password")
    
    if st.button("Login"):
        if authenticate_user_ui(st.session_state.login_id, st.session_state.password):
            st.session_state.is_logged_in = True
            st.session_state.logged_in_user = st.session_state.login_id
            st.session_state.is_admin = check_user_role_ui(st.session_state.logged_in_user, required_roles=["admin"])
            del st.session_state.password
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid login credentials. Please try again.")

def logout_page():
    """Handle user logout and clear session state"""
    st.session_state.is_logged_in = False
    st.session_state.is_admin = False
    if "logged_in_user" in st.session_state:
        del st.session_state.logged_in_user
    if "password" in st.session_state: 
        del st.session_state.password
    st.success("Logged out successfully.")

def auth_header():
    """Render the authentication header with welcome message and logout button"""
    header = st.columns([1, 5, 1])
    
    if st.session_state.is_logged_in:
        header[0].write(f"Welcome {st.session_state.logged_in_user}!")
        header[2].button("Logout", key="logout", on_click=logout_page)
    
    return header

def auth_sidebar():
    """Add logout button to sidebar if user is logged in"""
    if st.session_state.is_logged_in and st.sidebar.button("Logout"):
        st.session_state.is_logged_in = False
        st.success("Logged out successfully.")
        st.rerun()