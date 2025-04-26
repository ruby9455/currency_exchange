import streamlit as st
from functions.ui.crud_ui import get_create_table_page, get_insert_data_page, get_fetch_data_page, get_update_data_page, get_delete_data_page
from functions.ui.auth_page import init_auth_state, login_page, logout_page, auth_header, auth_sidebar

def db_actions():
    left_col, right_col = st.columns([2, 8])
    default_action_index = 2
    with left_col:  
        st.selectbox(
            label="Select an action", 
            options=["", "Create Table on Database", "Insert Data", "Fetch Data", "Update Data", "Delete Data"], 
            index=default_action_index,
            key="db_action"
        )
    with right_col:
        if st.session_state.db_action == "":
            pass
        elif st.session_state.db_action == "Create Table on Database":
            get_create_table_page()
        elif st.session_state.db_action == "Insert Data":
            get_insert_data_page()
        elif st.session_state.db_action == "Fetch Data":
            get_fetch_data_page()
        elif st.session_state.db_action == "Update Data":
            get_update_data_page()
        elif st.session_state.db_action == "Delete Data":
            get_delete_data_page()
        else:
            st.warning("Please select an action from the dropdown.")

def main():
    init_auth_state()
    header = auth_header()
    
    header[1].title("Database Operations")
    content = st.container()
    if not st.session_state.logged_in:
        with content:
            login_page()
    else:
        content.empty()
        with content:
            db_actions()

if __name__ == "__main__":
    st.set_page_config(
        page_title="Database Operations",
        page_icon=":guardsman:",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    main()

