import streamlit as st
from functions.ui.crud_ui import get_create_table_page, get_insert_data_page, get_fetch_data_page, get_update_data_page, get_delete_data_page
from functions.auth_func import authenticate_user

def init_page():
    if "logged_in" not in st.session_state: 
        st.session_state.logged_in = False
    if "login_id" not in st.session_state: 
        st.session_state.login_id = ""

def login_page():
    st.title("Login Page")
    st.text_input("Enter Login ID", key="login_id")
    st.text_input("Enter Password", type="password", key="password", value="V5i9akab.")
    
    if st.button("Login"):
        if authenticate_user(st.session_state.login_id, st.session_state.password):
            st.session_state.logged_in = True
            st.session_state.logged_in_user = st.session_state.login_id
            del st.session_state.password
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid login credentials. Please try again.")

def logout_page():
    st.session_state.logged_in = False
    if "logged_in_user" in st.session_state:
        del st.session_state.logged_in_user
    if "password" in st.session_state: 
        del st.session_state.password
    st.success("Logged out successfully.")

def db_actions():
    left_col, right_col = st.columns([2, 8])
    default_action_index = 2
    with left_col:  
        st.selectbox(
            label="Select an action", 
            options=["", "Create Table on Database", "Insert Data", "Fetch Data", "Update Data", "Delete Data"], 
            # index=0, # TODO: switch back to 0 when deploying
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
    init_page()
    header = st.columns([1, 5, 1])
    
    header[1].title("Database Operations")
    content = st.container()
    if not st.session_state.logged_in:
        with content:
            login_page()
    else:
        header[0].write(f"Welcome {st.session_state.logged_in_user}!")
        header[2].button("Logout", key="logout", on_click=logout_page)
        content.empty()
        with content:
            db_actions()
        
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.success("Logged out successfully.")

if __name__ == "__main__":
    st.set_page_config(
        page_title="Database Operations",
        page_icon=":guardsman:",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    main()

