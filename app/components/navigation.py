import streamlit as st
from components.nav_bar_settings import get_tabs, get_cols_ratio, PAGE_FILE_NAME_DICT

def nav_bar():
    tabs = get_tabs(is_logged_in=st.session_state.is_logged_in, is_admin=st.session_state.is_admin)
    with st.container(key='nav-bar'):
        nav_bar = st.columns(get_cols_ratio(is_logged_in=st.session_state.is_logged_in, is_admin=st.session_state.is_admin))
        
        # Separate regular tabs from auth tabs (login/logout)
        auth_tabs = ["Login", "Logout"]
        regular_tabs = [tab for tab in tabs if tab not in auth_tabs]
        auth_tab = next((tab for tab in tabs if tab in auth_tabs), None)
        
        # Display regular navigation tabs
        for idx, tab in enumerate(regular_tabs):
            nav_bar[idx + 1].page_link(
                page=PAGE_FILE_NAME_DICT[tab],
                label=tab,
            )
            
        # Display auth tab (login/logout) at the last position
        if auth_tab:
            # Calculate the last position (excluding the right margin)
            last_pos = len(nav_bar) - 1
            nav_bar[last_pos].page_link(
                page=PAGE_FILE_NAME_DICT[auth_tab],
                label=auth_tab,
            )