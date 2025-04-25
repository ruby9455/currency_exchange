import sys

def _read_toml(file_path: str) -> dict:
    """
    Read a TOML file and return its contents as a dictionary.
    """
    import toml
    try:
        with open(file_path, 'r') as file:
            data = toml.load(file)
        return data
    except Exception as e:
        print(f"Error reading TOML file: {e}")
        return {}
    
def _get_hashed_password(password: str) -> str:
    """
    Hash a password using SHA-256.
    """
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()

def _verify_password(stored_password: str, provided_password: str) -> bool:
    """
    Verify a stored password against a provided password.
    """
    import hashlib
    return stored_password == hashlib.sha256(provided_password.encode()).hexdigest()

def store_password(password: str) -> None:
    """
    Store a hashed password in a TOML file.
    """
    import toml
    hashed_password = _get_hashed_password(password)
    config = _read_toml(".streamlit/secrets.toml")
    
    if "app" not in config:
        config["app"] = {}
    if "password" not in config["app"]:
        config["app"]["password"] = ""
    
    # if the password is already stored, ask for confirmation to overwrite
    if config["app"]["password"] != "":
        confirm = input("Password already exists. Do you want to overwrite it? (y/n): ")
        if confirm.lower() != 'y':
            print("Password not changed.")
            return
        
    config["app"]["password"] = hashed_password
    
    # Write the updated config back to the TOML file
    with open(".streamlit/secrets.toml", 'w') as file:
        toml.dump(config, file)
        
    print("Password stored successfully.")

def store_secondary_password(password: str) -> None:
    """
    Store a secondary hashed password in a TOML file.
    """
    import toml
    hashed_password = _get_hashed_password(password)
    config = _read_toml(".streamlit/secrets.toml")
    
    if "app" not in config:
        config["app"] = {}
    if "secondary_password" not in config["app"]:
        config["app"]["secondary_password"] = ""
    
    # if the password is already stored, ask for confirmation to overwrite
    if config["app"]["secondary_password"] != "":
        confirm = input("Secondary password already exists. Do you want to overwrite it? (y/n): ")
        if confirm.lower() != 'y':
            print("Secondary password not changed.")
            return
        
    config["app"]["secondary_password"] = hashed_password
    
    # Write the updated config back to the TOML file
    with open(".streamlit/secrets.toml", 'w') as file:
        toml.dump(config, file)
        
    print("Secondary password stored successfully.")
    
def authenticate_user(username: str, password: str) -> bool:
    """
    Authenticate a user based on username and password.
    """
    # For demonstration purposes, we will use a hardcoded username and password
    # In a real application, you would check against a database or other secure storage
    config = _read_toml(".streamlit/secrets.toml")
    
    correct_username = config.get("app", {}).get("username", "")
    correct_password = config.get("app", {}).get("password", "")
    
    if username == correct_username and _verify_password(correct_password, password):
        print("User authenticated successfully.")
        return True
    return False

def authenticate_with_secondary(username: str, password: str) -> bool:
    """
    Authenticate a user with their secondary password.
    This should be used for sensitive operations like data deletion.
    """
    config = _read_toml(".streamlit/secrets.toml")
    
    correct_username = config.get("app", {}).get("username", "")
    secondary_password = config.get("app", {}).get("secondary_password", "")
    
    if username == correct_username and _verify_password(secondary_password, password):
        print("User authenticated with secondary password successfully.")
        return True
    print("Secondary password authentication failed.")
    return False

if __name__ == "__main__":    
    if len(sys.argv) < 2:
        print("Usage: python shared_func.py <command>")
        print("Available commands: store_password, list_functions")
        sys.exit(1)
        
    command = sys.argv[1]
    
    if command == "store_password":
        if len(sys.argv) < 3:
            print("Usage: python shared_func.py store_password <password>")
            sys.exit(1)
        password = sys.argv[2]
        store_password(password)
    elif command == "list_functions":
        # Get all functions from locals() that don't start with underscore (non-private)
        functions = [name for name, obj in locals().items() 
                    if callable(obj) and not name.startswith('_')]
        print(f"Available functions: {', '.join(functions)}")
        
        # Include private functions with underscore if needed
        private_functions = [name for name, obj in locals().items() 
                           if callable(obj) and name.startswith('_') and not name.startswith('__')]
        if private_functions:
            print(f"Private helper functions: {', '.join(private_functions)}")
    else:
        print(f"Unknown command: {command}")
        print("Available commands: store_password, list_functions")
        sys.exit(1)