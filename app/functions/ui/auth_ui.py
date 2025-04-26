import streamlit as st
from functions.utils import _get_default_db

def create_admin_user_wrapper():
    """
    Create an admin user in the database.
    """
    from functions.auth_func import create_admin_user
    db_name = _get_default_db()
    
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

def get_user_collection_ui():
    """
    Get user collections from the database.
    """
    from functions.auth_func import get_user_collection
    db_name = _get_default_db()
    
    return get_user_collection(db_name=db_name)
            
def authenticate_user_ui(username: str, password: str) -> bool:
    """
    UI for user authentication.
    """
    from functions.auth_func import authenticate_user
    db_name = _get_default_db()
    
    return authenticate_user(db_name=db_name, username=username, password=password)

def check_user_role_ui(username: str, required_roles: list[str]) -> bool:
    """
    Check the user role in the database.
    """
    from functions.auth_func import check_user_role
    db_name = _get_default_db()
    
    return check_user_role(db_name=db_name, username=username, required_roles=required_roles)

def check_secondary_password_ui(username: str, secondary_password: str) -> bool:
    """
    Check the secondary password for the user.
    """
    from functions.auth_func import check_secondary_password
    db_name = _get_default_db()
    
    return check_secondary_password(db_name=db_name, username=username, secondary_password=secondary_password)
