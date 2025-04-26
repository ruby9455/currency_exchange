import streamlit as st
from functions.utils import _load_css
from components.nav_bar_settings import get_tabs, get_cols_ratio, PAGE_FILE_NAME_DICT

def nav_bar():
    _load_css()
    general_tabs, auth_tab = get_tabs(is_logged_in=st.session_state.is_logged_in, is_admin=st.session_state.is_admin)
    cols_ratio = get_cols_ratio(is_logged_in=st.session_state.is_logged_in, is_admin=st.session_state.is_admin)
    
    with st.container(key='nav-bar'):
        nav_bar = st.columns(cols_ratio)

        # Display regular navigation tabs
        for idx, tab in enumerate(general_tabs):
            nav_bar[idx + 1].page_link(
                page=PAGE_FILE_NAME_DICT[tab],
                label=tab,
            )
        
        # Display login/logout tab at the right end (after the spacer column)
        # Correct calculation: left margin(1) + all general tabs + spacer column(1)
        right_end_idx = 1 + len(general_tabs) + 2 # + 1 for the left and right margin and spacer respectively
        nav_bar[right_end_idx].page_link(
            page=PAGE_FILE_NAME_DICT[auth_tab],
            label=auth_tab,
        )