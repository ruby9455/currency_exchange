import streamlit as st
from components.navigation import nav_bar
from functions.ui.auth_page import logout_page, init_auth_state

def main():
    init_auth_state()
    nav_bar()
    
    if st.session_state.is_logged_in:
        logout_page()
        st.rerun()
    else:
        st.switch_page("main.py")
        
if __name__ == "__main__":
    st.set_page_config(
        page_title="Logout - Currency Exchange",
        page_icon="🔓",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    main()