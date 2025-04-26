import bcrypt
from functions.utils import _read_toml
from functions.db.mongo_connection import get_mongo_client

def _get_hashed_password(password: str) -> str:
    """
    Hash a password using SHA-256.
    Deprecated: Use bcrypt_hash_password instead.
    """
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()

def _verify_password(stored_password: str, provided_password: str) -> bool:
    """
    Verify a stored password against a provided password using SHA-256.
    Deprecated: Use bcrypt_verify_password instead.
    """
    import hashlib
    return stored_password == hashlib.sha256(provided_password.encode()).hexdigest()

def bcrypt_hash_password(password: str) -> bytes:
    """
    Hash a password using bcrypt.
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed

def bcrypt_verify_password(stored_password: bytes, provided_password: str) -> bool:
    """
    Verify a stored password against a provided password using bcrypt.
    """
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password)

def get_user_collection(db_name: str):
    """
    Get the users collection from MongoDB.
    """
    client = get_mongo_client()
    if client is None:
        print("Failed to connect to MongoDB.")
        return None
    
    db = client[db_name]
    return db["users"]

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

def create_admin_user(db_name: str, username: str, password: str) -> bool:
    """
    Create an admin user in the MongoDB users collection.
    """
    users = get_user_collection(db_name=db_name)
    if users is None:
        print("Failed to connect to MongoDB.")
        return False
    
    # Check if user already exists
    existing_user = users.find_one({"username": username})
    if existing_user:
        print(f"User '{username}' already exists.")
        return False
    
    # Create admin user
    user_doc = {
        "username": username,
        "display_name": "Administrator",
        "email": "",
        "password": bcrypt_hash_password(password),
        "role": "admin",
        "created_at": _get_current_datetime(),
        "updated_at": _get_current_datetime(),
        "active": True
    }
    
    result = users.insert_one(user_doc)
    if result.inserted_id:
        print(f"Admin user '{username}' created successfully.")
        return True
    else:
        print("Failed to create admin user.")
        return False

def _get_current_datetime():
    """
    Get current datetime for MongoDB documents.
    """
    from datetime import datetime
    return datetime.now()

def authenticate_user(db_name: str, username: str, password: str) -> bool:
    """
    Authenticate a user based on username and password.
    First tries MongoDB, falls back to TOML if MongoDB authentication fails.
    """
    # Try MongoDB authentication first
    try:
        users = get_user_collection(db_name=db_name)
        if users is None:
            print("Failed to connect to MongoDB.")
            return False
        user = users.find_one({"username": username, "active": True})
        
        if user and user.get("password"):
            # Check if password is stored as bytes (bcrypt) or string (old SHA-256)
            stored_password = user["password"]
            
            if isinstance(stored_password, bytes):
                # Bcrypt password
                if bcrypt_verify_password(stored_password, password):
                    print("User authenticated successfully via MongoDB (bcrypt).")
                    return True
            else:
                # Legacy SHA-256 password (string)
                if _verify_password(stored_password, password):
                    print("User authenticated successfully via MongoDB (SHA-256).")
                    # Consider upgrading to bcrypt
                    return True
        
    except Exception as e:
        print(f"MongoDB authentication error: {e}")
    
    # Fall back to TOML authentication for backward compatibility
    try:
        config = _read_toml(".streamlit/secrets.toml")
        
        correct_username = config.get("app", {}).get("username", "")
        correct_password = config.get("app", {}).get("password", "")
        
        if username == correct_username and _verify_password(correct_password, password):
            print("User authenticated successfully via TOML.")
            return True
    except Exception as e:
        print(f"TOML authentication error: {e}")
    
    return False

def authenticate_with_secondary(username: str, password: str) -> bool: # TODO: revise this function to use bcrypt and mongodb
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

def check_user_role(db_name: str, username: str, required_roles: list) -> bool:
    """
    Check if a user has one of the required roles.
    """
    try:
        users = get_user_collection(db_name=db_name)
        if users is None:
            print("Failed to connect to MongoDB.")
            return False
        user = users.find_one({"username": username, "active": True})
        
        if user and user.get("role") in required_roles:
            return True
    except Exception as e:
        print(f"Error checking user role: {e}")
    
    return False

