import streamlit as st
from components.navigation import nav_bar
from functions.ui.auth_page import init_auth_state, login_page, auth_header

def transaction_history_page():
    """Render the transaction history page"""
    st.title("Transaction History")

def main():
    init_auth_state()
    nav_bar()
    header_placeholder = st.empty()
    content_placeholder = st.empty()
    if not st.session_state.is_logged_in:
        with content_placeholder:
            login_page()
    else:
        content_placeholder.empty()
        with header_placeholder:
            auth_header(page_title="Transaction History")
        with content_placeholder:
            transaction_history_page()
    
if __name__ == "__main__":
    st.set_page_config(
        page_title="Transaction History",
        page_icon="📜",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    main()