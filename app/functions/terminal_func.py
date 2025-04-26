import os
import sys

current_path = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_path))
# Add project root to Python path if not already there
if project_root not in sys.path:
    sys.path.insert(0, project_root)
# Add the parent directory of the current file to sys.path if not already there
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

def create_admin_user_helper():
    """
    Helper function to create an admin user in terminal.
    """
    try:
        # First try absolute imports
        from app.functions.db.mongo_connection import get_mongo_client
        from app.functions.db.mongo_collection_management import get_all_databases
        from app.functions.auth_func import create_admin_user
    except ImportError:
        # If that fails, try relative imports
        import sys
        print("Absolute imports failed. Using direct imports...")
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from db.mongo_connection import get_mongo_client
        from db.mongo_collection_management import get_all_databases
        from auth_func import create_admin_user

    client = get_mongo_client()
    if client is None:
        print("Failed to connect to MongoDB.")
        return
    all_databases = get_all_databases(client)
    print("Available databases:")
    for idx, db in enumerate(all_databases):
        print(f"{idx + 1}: {db}")
    db_index = int(input("Select a database by number: ")) - 1
    if db_index < 0 or db_index >= len(all_databases):
        print("Invalid selection.")
        return
    
    db_name = all_databases[db_index]
    print(f"Selected database: {db_name}")
    username = input("Enter username for admin user: ")
    password = input("Enter password for admin user: ")

    confirm_password = input("Confirm password for admin user: ")
    if password != confirm_password:
        print("Passwords do not match. Admin user not created.")
        return
    
    if create_admin_user(db_name, username, password):
        print("Admin user created successfully.")
    else:
        print("Failed to create admin user.")

# Main code block
if __name__ == "__main__":
    functions = [name for name, obj in locals().items() 
                if callable(obj) and not name.startswith('_')]
    print(f"Available functions: {', '.join(functions)}")
    
    if len(sys.argv) < 2:
        print("Usage: python terminal_func.py <command>")
        print("Available commands")
        for idx, func in enumerate(functions):
            print(f"{idx + 1}: {func}")
        sys.exit(1)

    command = sys.argv[1]

    if command in functions:
        func = locals()[command]
        if func == create_admin_user_helper:
            func()
        else:
            print(f"Function {command} does not require any arguments.")
    else:
        print(f"Unknown command: {command}")
        print("Available commands:")
        for idx, func in enumerate(functions):
            print(f"{idx + 1}: {func}")
        sys.exit(1)
