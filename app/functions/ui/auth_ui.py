import streamlit as st
from functions.ui.db_func_ui import get_cached_mongo_client
from functions.db.mongo_collection_management import get_all_databases

def _get_db():
    """
    Get the database name from the TOML file.
    """
    from functions.utils import _read_toml
    config = _read_toml(".streamlit/secrets.toml")
    db_name = config.get("mongo", {}).get("db_name", "")
    return db_name

def create_admin_user_wrapper():
    """
    Create an admin user in the database.
    """
    from functions.auth_func import create_admin_user
    db_name = _get_db()
    
    # Input fields for username and password
    username = st.text_input("Enter Username")
    password = st.text_input("Enter Password", type="password")
    
    if st.button("Create Admin User"):
        if username and password:
            # Call the function to create the admin user in the database
            # Assuming create_admin_user is a function that handles this
            success = create_admin_user(db_name=db_name, username=username, password=password)
            if success:
                st.success("Admin user created successfully!")
            else:
                st.error("Failed to create admin user.")
        else:
            st.warning("Please fill in both fields.")
            
def authenticate_user_ui(username: str, password: str) -> bool:
    """
    UI for user authentication.
    """
    from functions.auth_func import authenticate_user
    db_name = _get_db()
    
    return authenticate_user(db_name=db_name, username=username, password=password)