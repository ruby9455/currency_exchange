import bcrypt
from datetime import datetime
import streamlit as st
from functions.ui.auth_ui import get_user_collection_ui
from functions.ui.auth_page import init_auth_state, login_page, auth_header

def init_user_management_state():
    """Initialize user management specific state variables"""
    if "selected_user" not in st.session_state:
        st.session_state.selected_user = None
    if "user_action" not in st.session_state:
        st.session_state.user_action = ""

def hash_password(password):
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed

def verify_password(stored_password, provided_password):
    """Verify password using bcrypt"""
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password)

def register_user_page():
    """User registration form"""
    st.subheader("Register New User")
    
    with st.form("register_form"):
        username = st.text_input("Username")
        left_col, right_col = st.columns(2)
        password = left_col.text_input("Password", type="password")
        confirm_password = left_col.text_input("Confirm Password", type="password")
        secondary_password = right_col.text_input("Secondary Password", type="password")
        confirm_secondary_password = right_col.text_input("Confirm Secondary Password", type="password")
        
        # Set role to "user" by default and hide it from the UI
        role = "user"        
        submit = st.form_submit_button("Register User")
        
        if submit:
            if password != confirm_password:
                st.error("Passwords do not match!")
                return
            
            if secondary_password != confirm_secondary_password:
                st.error("Secondary passwords do not match!")
                return
                
            users_collection = get_user_collection_ui()
            
            # Check if username already exists
            if users_collection.find_one({"username": username}):
                st.error(f"Username '{username}' already exists!")
                return
                
            # Create user document
            user_doc = {
                "username": username,
                "password": hash_password(password),
                "secondary_password": hash_password(secondary_password),
                "role": role,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "active": True
            }
            
            # Insert user
            result = users_collection.insert_one(user_doc)
            if result.inserted_id:
                st.success(f"User '{username}' registered successfully!")
            else:
                st.error("Failed to register user.")

def list_users_page():
    """List all users"""
    st.subheader("User List")
    
    users_collection = get_user_collection_ui()
    users = list(users_collection.find({}, {"password": 0}))  # Exclude passwords
    
    if not users:
        st.info("No users found.")
        return
    
    # Display users in a table
    user_data = []
    for user in users:
        user_data.append({
            "Username": user["username"],
            "Display Name": user.get("display_name", ""),
            "Email": user.get("email", ""),
            "Role": user.get("role", "user"),
            "Active": "Yes" if user.get("active", True) else "No",
            "Created": user.get("created_at", "")
        })
    
    st.dataframe(user_data)
    
    # Select user for editing
    usernames = [user["username"] for user in users]
    selected_user = st.selectbox("Select user to edit or delete:", [""] + usernames)
    
    if selected_user:
        user = users_collection.find_one({"username": selected_user})
        if user:
            st.session_state.selected_user = user
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Edit User"):
                    st.session_state.user_action = "edit"
                    st.rerun()
            with col2:
                if st.button("Delete User", type="primary", use_container_width=True):
                    st.session_state.user_action = "delete"
                    st.rerun()

def edit_user_page():
    """Edit user information"""
    if not st.session_state.selected_user:
        st.error("No user selected.")
        return
    
    user = st.session_state.selected_user
    st.subheader(f"Edit User: {user['username']}")
    
    with st.form("edit_user_form"):
        display_name = st.text_input("Display Name", value=user.get("display_name", ""))
        email = st.text_input("Email", value=user.get("email", ""))
        
        # Get current role
        current_role = user.get("role", "user")
        
        # Show role but don't allow changing to admin
        if current_role == "admin":
            st.info("User has admin role (can only be set via terminal commands)")
            role = "admin"
        else:
            st.info("Regular user role")
            role = "user"
        
        active = st.checkbox("Active", value=user.get("active", True))
        
        change_password = st.checkbox("Change Password")
        new_password = ""
        confirm_password = ""
        
        if change_password:
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm New Password", type="password")
        
        submit = st.form_submit_button("Update User")
        
        if submit:
            users_collection = get_user_collection_ui()
            
            # Prepare update document
            update_doc = {
                "$set": {
                    "display_name": display_name,
                    "email": email,
                    "role": role,
                    "active": active,
                    "updated_at": datetime.now()
                }
            }
            
            # Handle password change
            if change_password:
                if new_password != confirm_password:
                    st.error("Passwords do not match!")
                    return
                
                if new_password:  # Only update if a new password was provided
                    update_doc["$set"]["password"] = hash_password(new_password)
            
            # Update user
            result = users_collection.update_one({"username": user["username"]}, update_doc)
            
            if result.modified_count > 0:
                st.success(f"User '{user['username']}' updated successfully!")
                st.session_state.user_action = ""
                st.session_state.selected_user = None
                st.rerun()
            else:
                st.info("No changes made.")
    
    if st.button("Cancel"):
        st.session_state.user_action = ""
        st.session_state.selected_user = None
        st.rerun()

def delete_user_page():
    """Delete user confirmation"""
    if not st.session_state.selected_user:
        st.error("No user selected.")
        return
    
    user = st.session_state.selected_user
    st.subheader(f"Delete User: {user['username']}")
    
    st.warning("Are you sure you want to delete this user? This action cannot be undone.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Cancel"):
            st.session_state.user_action = ""
            st.session_state.selected_user = None
            st.rerun()
    with col2:
        if st.button("Confirm Delete", type="primary"):
            users_collection = get_user_collection_ui()
            result = users_collection.delete_one({"username": user["username"]})
            
            if result.deleted_count > 0:
                st.success(f"User '{user['username']}' deleted successfully!")
                st.session_state.user_action = ""
                st.session_state.selected_user = None
                st.rerun()
            else:
                st.error("Failed to delete user.")

def user_actions():
    """Display user management actions"""
    left_col, right_col = st.columns([2, 8])
    
    with left_col:
        st.selectbox(
            label="Select an action",
            options=["", "Register User", "List Users"],
            key="user_management_action"
        )
    
    with right_col:
        # Handle specific user edit/delete actions
        if st.session_state.user_action == "edit":
            edit_user_page()
        elif st.session_state.user_action == "delete":
            delete_user_page()
        # Handle main actions
        elif st.session_state.user_management_action == "":
            pass
        elif st.session_state.user_management_action == "Register User":
            register_user_page()
        elif st.session_state.user_management_action == "List Users":
            list_users_page()
        else:
            st.warning("Please select an action from the dropdown.")

def main():
    # Initialize authentication state
    init_auth_state()
    
    # Initialize user management specific state
    init_user_management_state()
    
    header = auth_header()
    
    header[1].title("User Management")
    content = st.container()
    
    if not st.session_state.is_logged_in:
        with content:
            login_page()
    else:
        content.empty()
        
        with content:
            user_actions()

if __name__ == "__main__":
    st.set_page_config(
        page_title="User Management",
        page_icon=":busts_in_silhouette:",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    
    # Make sure bcrypt is installed
    try:
        import bcrypt
    except ImportError:
        st.error("bcrypt package is required. Please install it using `pip install bcrypt`.")
        st.code("pip install bcrypt")
        st.stop()
    
    main()